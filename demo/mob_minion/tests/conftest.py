"""
Shared test fixtures for mob minion tests.

Only truly reusable fixtures that are used across multiple test files should be here.
Most fixtures should be defined inline in test files.
"""
import pytest
from unittest.mock import Mock


@pytest.fixture
def foundry_vtt_core():
    """Fixture: Core Foundry VTT system mock."""
    core = Mock()
    core.session = Mock()
    core.session.is_active = True
    return core














