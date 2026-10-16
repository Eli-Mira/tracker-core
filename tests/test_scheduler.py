"""Tests for tracker core scheduler."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from tracker_core.scheduler import TrackerScheduler


class TestTrackerScheduler:
    """Tests for TrackerScheduler."""
    
    @pytest.fixture
    def scheduler(self, tmp_path):
        """Create scheduler with temp config."""
        config = tmp_path / "schedule.yaml"
        config.write_text("""
api_tracker:
  mode: cron
  cron:
    hour: 2
    minute: 0
    day_of_week: "*"
news_tracker:
  mode: cron
  cron:
    hour: 7
    minute: 0
    day_of_week: "*"
alerts:
  consecutive_failures: 3
  check_interval_minutes: 10
""")
        return TrackerScheduler(str(config))
    
    def test_create_scheduler(self, scheduler):
        """Scheduler can be created."""
        assert scheduler is not None
        assert scheduler._jobs == {}
    
    def test_add_job(self, scheduler):
        """Jobs can be added to scheduler."""
        async def dummy_job():
            pass
        
        scheduler.add_job("test_job", dummy_job)
        assert "test_job" in scheduler._jobs
    
    def test_remove_job(self, scheduler):
        """Jobs can be removed."""
        async def dummy_job():
            pass
        
        scheduler.add_job("test_job", dummy_job)
        scheduler.remove_job("test_job")
        assert "test_job" not in scheduler._jobs
    
    def test_record_success(self, scheduler):
        """Success recording increments counter."""
        async def dummy_job():
            pass

        scheduler.add_job("test_job", dummy_job)
        scheduler.record_success("test_job")

        assert scheduler._run_count.get("test_job") == 1
        assert scheduler._consecutive_failures.get("test_job") == 0

    def test_record_failure(self, scheduler):
        """Failure recording increments counter."""
        async def dummy_job():
            pass

        scheduler.add_job("test_job", dummy_job)
        scheduler.record_failure("test_job")

        assert scheduler._run_count.get("test_job") == 0
        assert scheduler._consecutive_failures.get("test_job") == 1
    
    def test_get_status(self, scheduler):
        """Scheduler returns status dict."""
        status = scheduler.get_status()
        assert "running" in status
        assert "jobs" in status
