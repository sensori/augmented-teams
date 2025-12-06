"""
Pytest configuration for Story IO Mamba tests.

This imports the mamba test discovery plugin from behaviors/conftest.py
to ensure pytest can discover mamba tests without trying to import them.
"""
import sys
from pathlib import Path

# Add behaviors directory to path so we can import the mamba plugin
workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
behaviors_path = workspace_root / "behaviors"
if str(behaviors_path) not in sys.path:
    sys.path.insert(0, str(behaviors_path))

# Import the mamba plugin hooks (this registers them with pytest)
try:
    from conftest import pytest_collect_file, MambaFile, MambaTestItem, MambaTestError
except ImportError:
    # If import fails, pytest will try to discover conftest.py in parent dirs
    pass

