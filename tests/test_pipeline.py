"""Tests for tracker core pipeline."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from tracker_core.pipeline.fetcher import HTTPFetcher, FetchResult
from tracker_core.pipeline.stages import (
    FetchStage,
    ParseStage,
    DedupeStage,
    FilterStage,
    StoreStage,
    ReporterStage,
    NotifierStage,
)
from tracker_core.schema import NewsItem, SourceType


class TestHTTPFetcher:
    """Tests for HTTPFetcher."""
    
    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Fetcher returns success on 200."""
        fetcher = HTTPFetcher(timeout=5.0)
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"test": true}'
            mock_response.headers = {"content-type": "application/json"}
            mock_response.url.toString.return_value = "https://example.com"
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await fetcher.fetch("https://example.com")
            
            assert result.success is True
            assert result.status_code == 200
            assert result.content == '{"test": true}'
    
    @pytest.mark.asyncio
    async def test_fetch_error(self):
        """Fetcher handles HTTP errors."""
        fetcher = HTTPFetcher(timeout=5.0)

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")

            # Should raise or return error result
            with pytest.raises(Exception):
                await fetcher.fetch("https://example.com")


class TestPipelineStages:
    """Tests for pipeline stages."""
    
    def test_fetch_stage(self):
        """Fetch stage collects results from adapters."""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch = AsyncMock()

        adapter1 = Mock()
        adapter1.name = "adapter1"
        adapter1.get_fetch_url.return_value = "https://example.com/1"
        adapter1.parse.return_value = [{"id": 1}]

        adapter2 = Mock()
        adapter2.name = "adapter2"
        adapter2.get_fetch_url.return_value = "https://example.com/2"
        adapter2.parse.return_value = [{"id": 2}]

        stage = FetchStage(mock_fetcher, [adapter1, adapter2])

        async def run():
            return await stage.process(None, {})

        data, context = asyncio.run(run())

        assert len(data) == 2
        # errors key only exists if there were errors
        assert context.get("errors") is None or context.get("errors") == []
    
    def test_dedupe_stage(self):
        """Dedupe stage removes duplicates."""
        items = [
            NewsItem(source=SourceType.GITHUB, title="Same", url="https://example.com/1"),
            NewsItem(source=SourceType.REDDIT, title="Same", url="https://example.com/1"),
            NewsItem(source=SourceType.HACKERNEWS, title="Different", url="https://example.com/2"),
        ]
        
        stage = DedupeStage(strategy="url")
        
        async def run():
            return await stage.process(items, {})
        
        data, context = asyncio.run(run())
        
        assert len(data) == 2
        assert context.get("duplicate_count") == 1
    
    def test_filter_stage(self):
        """Filter stage selects relevant items."""
        items = [
            NewsItem(source=SourceType.GITHUB, title="AI model release", url="https://example.com/1"),
            NewsItem(source=SourceType.GITHUB, title="Random update", url="https://example.com/2"),
        ]
        
        stage = FilterStage(keywords=["AI", "model"])
        
        async def run():
            return await stage.process(items, {})
        
        data, context = asyncio.run(run())
        
        assert len(data) == 1
        assert context.get("relevant_count") == 1


class TestReporterStage:
    """Tests for reporter stage."""
    
    def test_reporter_generation(self):
        """Reporter generates text output."""
        from tracker_core.reporter import ProviderReport
        from tracker_core.schema import Provider, VerificationStatus

        providers = [
            Provider(name="Provider 1", base_url="https://p1.com", status=VerificationStatus.VERIFIED),
            Provider(name="Provider 2", base_url="https://p2.com", status=VerificationStatus.UNVERIFIED),
        ]

        reporter = ProviderReport()
        report = reporter.generate(providers, {})

        assert "Provider 1" in report
        assert "Provider 2" in report


class TestNotifierStage:
    """Tests for notifier stage."""
    
    def test_notifier_sends(self):
        """Notifier sends message."""
        from tracker_core.notifier import NullNotifier
        
        notifier = NullNotifier()
        
        async def run():
            return await notifier.send("Test message")
        
        result = asyncio.run(run())
        
        assert result is True
