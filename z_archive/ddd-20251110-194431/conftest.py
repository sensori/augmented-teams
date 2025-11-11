"""Pytest configuration for DDD tests"""
import sys
from pathlib import Path

# Add common_command_runner to Python path for tests
common_runner_path = Path(__file__).parent.parent / "common_command_runner"
if str(common_runner_path) not in sys.path:
    sys.path.insert(0, str(common_runner_path))

