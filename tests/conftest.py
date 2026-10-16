"""Pytest configuration for tracker core."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure pytest-asyncio
pytest_plugins = []
