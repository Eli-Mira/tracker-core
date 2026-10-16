"""Tests for tracker core schema."""

import pytest
from datetime import datetime

from tracker_core.schema import (
    Provider,
    ProviderList,
    NewsItem,
    NewsBatch,
    SourceType,
    Category,
    VerificationStatus,
    validate_provider,
    validate_news_item,
)


class TestProviderSchema:
    """Tests for Provider schema."""
    
    def test_create_minimal_provider(self):
        """Provider can be created with minimal fields."""
        provider = Provider(
            name="Test Provider",
            base_url="https://example.com"
        )
        assert provider.name == "Test Provider"
        assert provider.free_tier_available is True
        assert provider.status == VerificationStatus.UNVERIFIED
    
    def test_create_full_provider(self):
        """Provider can be created with all fields."""
        provider = Provider(
            name="Full Provider",
            base_url="https://full.example.com",
            docs_url="https://docs.example.com",
            free_tier_details={"rate_limit": "100 RPM"},
            status=VerificationStatus.VERIFIED,
            last_verified=datetime.utcnow(),
            region="western",
            tags=["test", "example"]
        )
        assert provider.status == VerificationStatus.VERIFIED
        assert provider.region == "western"
        assert "test" in provider.tags
    
    def test_validate_provider_dict(self):
        """validate_provider works with dict input."""
        data = {
            "name": "Dict Provider",
            "base_url": "https://dict.example.com"
        }
        provider = validate_provider(data)
        assert provider.name == "Dict Provider"
    
    def test_provider_list(self):
        """ProviderList can hold multiple providers."""
        providers = [
            Provider(name="P1", base_url="https://p1.com"),
            Provider(name="P2", base_url="https://p2.com"),
        ]
        provider_list = ProviderList(providers=providers)
        assert len(provider_list.providers) == 2


class TestNewsItemSchema:
    """Tests for NewsItem schema."""
    
    def test_create_minimal_news_item(self):
        """NewsItem can be created with minimal fields."""
        item = NewsItem(
            source=SourceType.GITHUB,
            title="Test Item",
            url="https://github.com/test/repo"
        )
        assert item.source == SourceType.GITHUB
        assert item.is_relevant is False
        assert item.relevance_score == 0.0
    
    def test_create_full_news_item(self):
        """NewsItem can be created with all fields."""
        item = NewsItem(
            source=SourceType.HACKERNEWS,
            title="HN Story",
            url="https://news.ycombinator.com/item?id=123",
            published_date=datetime.utcnow(),
            category=Category.TOOL_LAUNCH,
            relevance_score=0.85,
            is_relevant=True,
            summary="A new tool released"
        )
        assert item.category == Category.TOOL_LAUNCH
        assert item.relevance_score == 0.85
    
    def test_validate_news_item_dict(self):
        """validate_news_item works with dict input."""
        data = {
            "source": "reddit",
            "title": "Reddit Post",
            "url": "https://reddit.com/r/test"
        }
        item = validate_news_item(data)
        assert item.title == "Reddit Post"


class TestNewsBatchSchema:
    """Tests for NewsBatch schema."""
    
    def test_create_empty_batch(self):
        """Empty batch can be created."""
        batch = NewsBatch(date=datetime.utcnow())
        assert batch.total_count == 0
        assert batch.relevant_count == 0
    
    def test_create_batch_with_items(self):
        """Batch can be created with items."""
        items = [
            NewsItem(source=SourceType.GITHUB, title="Item 1", url="https://github.com/1"),
            NewsItem(source=SourceType.REDDIT, title="Item 2", url="https://reddit.com/1"),
        ]
        batch = NewsBatch(date=datetime.utcnow(), items=items)
        # Items are stored, verify they're accessible
        assert len(batch.items) == 2
        assert batch.items[0].title == "Item 1"
        assert batch.items[1].title == "Item 2"
