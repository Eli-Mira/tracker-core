"""Tests for tracker core adapters."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from tracker_core.adapters.base import BaseAdapter, ProviderAdapter, NewsAdapter
from tracker_core.adapters.seed import SEED_PROVIDERS, create_seed_providers
from tracker_core.schema import Provider


class TestBaseAdapter:
    """Tests for BaseAdapter."""
    
    def test_base_adapter_is_abstract(self):
        """BaseAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAdapter()
    
    def test_adapter_default_config(self):
        """Adapter initializes with empty config by default."""
        class TestAdapter(ProviderAdapter):
            name = "test"

            def fetch(self):
                return None

            def parse(self, raw):
                return []

            def get_providers(self):
                return []

        adapter = TestAdapter()
        assert adapter.config == {}
        assert adapter.name == "test"

    def test_adapter_get_cache_key(self):
        """Adapter generates cache key from class name."""
        class TestAdapter(ProviderAdapter):
            name = "my-provider"

            def fetch(self):
                return None

            def parse(self, raw):
                return []

            def get_providers(self):
                return []

        adapter = TestAdapter()
        assert adapter.get_cache_key() == "TestAdapter:my-provider"

    def test_adapter_is_rate_limited(self):
        """Adapter detects rate limiting."""
        raw = Mock()
        raw.status_code = 429

        class TestAdapter(ProviderAdapter):
            def fetch(self):
                return raw

            def parse(self, raw):
                return []

            def get_providers(self):
                return []

        adapter = TestAdapter()
        assert adapter.is_rate_limited(raw) is True

    def test_adapter_should_backoff(self):
        """Adapter detects server errors."""
        raw = Mock()
        raw.status_code = 500
        raw.headers = {}

        class TestAdapter(ProviderAdapter):
            def fetch(self):
                return raw

            def parse(self, raw):
                return []

            def get_providers(self):
                return []

        adapter = TestAdapter()
        assert adapter.should_backoff(raw) is True


class TestSeedProviders:
    """Tests for seed provider list."""
    
    def test_seed_providers_count(self):
        """Seed list has expected number of providers."""
        assert len(SEED_PROVIDERS) == 13  # 7 western + 6 chinese
    
    def test_create_seed_providers(self):
        """create_seed_providers adds metadata."""
        providers = create_seed_providers()
        assert len(providers) == 13
        assert providers[0]["needs_review"] is True
        assert providers[0]["last_verified"] is None
    
    def test_seed_providers_have_required_fields(self):
        """All seed providers have required fields."""
        for p in SEED_PROVIDERS:
            assert "name" in p
            assert "base_url" in p
            assert "free_tier_available" in p


class TestAdapterParsing:
    """Test adapter parse methods."""
    
    def test_provider_adapter_parse_empty(self):
        """Provider adapter handles empty response."""
        class TestAdapter(ProviderAdapter):
            name = "test"

            def fetch(self):
                return None

            def parse(self, raw):
                if not raw:
                    return []
                return []

            def get_providers(self):
                return []

        adapter = TestAdapter()
        result = adapter.parse(None)
        assert result == []
