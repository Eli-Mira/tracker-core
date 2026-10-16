"""Tests for discovery engine."""

import asyncio
import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from tracker_core.schema import Provider, VerificationStatus
from tracker_core.discovery import DiscoveryEngine


class TestDiscoveryEngine:
    """Tests for discovery engine."""

    @pytest.fixture
    def engine(self):
        """Create discovery engine with mock fetcher."""
        providers = [
            Provider(name="Google AI Studio", base_url="https://ai.google.dev/"),
            Provider(name="OpenRouter", base_url="https://openrouter.ai/"),
        ]
        return DiscoveryEngine(existing_providers=providers)

    def test_get_existing_names(self, engine):
        """Engine knows existing provider names."""
        existing = engine.get_existing_names()
        assert "google ai studio" in existing
        assert "openrouter" in existing

    @pytest.mark.asyncio
    async def test_discover_from_openrouter(self, engine):
        """Test OpenRouter discovery."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''{
            "data": [
                {"id": "deepseek/deepseek-chat"},
                {"id": "qwen/qwen-plus"}
            ]
        }'''
        mock_response.success = True

        with patch.object(engine.fetcher, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            await engine._discover_from_openrouter()

        # Should have discovered new providers
        assert len(engine._discovered) >= 2
        names = [d["name"].lower() for d in engine._discovered]
        assert "deepseek" in names
        assert "qwen" in names

    @pytest.mark.asyncio
    async def test_discover_from_github(self, engine):
        """Test GitHub discovery."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''{
            "items": [
                {"owner": {"login": "newprovider"}, "html_url": "https://github.com/newprovider/api"}
            ]
        }'''
        mock_response.success = True

        with patch.object(engine.fetcher, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            await engine._discover_from_github()

        assert len(engine._discovered) >= 1

    @pytest.mark.asyncio
    async def test_filter_existing(self, engine):
        """Existing providers are filtered out."""
        engine._discovered = [
            {"name": "Google AI Studio", "source": "test"},
            {"name": "NewProvider", "source": "test"},
        ]

        existing = engine.get_existing_names()
        new_candidates = [
            c for c in engine._discovered
            if c.get("name", "").lower() not in existing
        ]

        assert len(new_candidates) == 1
        assert new_candidates[0]["name"] == "NewProvider"

    def test_save_candidates(self, engine, tmp_path):
        """Test saving candidates to file."""
        engine._discovered = [
            {"name": "TestProvider", "source": "test"}
        ]

        output = tmp_path / "candidates.json"
        engine.save_candidates(output)

        assert output.exists()
        data = json.loads(output.read_text())
        assert len(data) == 1
        assert data[0]["name"] == "TestProvider"


class TestRunDiscovery:
    """Tests for run_discovery function."""

    @pytest.mark.asyncio
    async def test_run_discovery(self):
        """Test full discovery run."""
        from tracker_core.discovery import run_discovery

        providers = [
            Provider(name="Google AI Studio", base_url="https://ai.google.dev/")
        ]

        # Mock the fetcher to return known data
        with patch('tracker_core.discovery.HTTPFetcher.fetch') as mock_fetch:
            mock_result = Mock()
            mock_result.success = False
            mock_fetch.return_value = mock_result

            # Use the engine directly to avoid nested asyncio.run
            engine = DiscoveryEngine(existing_providers=providers)
            candidates = await engine.discover_all()
            assert isinstance(candidates, list)
