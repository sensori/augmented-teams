"""
Tests for MCPServerGenerator exception handling - no fallbacks.

MCPServerGenerator should raise exceptions when:
- Base actions directory doesn't exist
"""
import pytest
from pathlib import Path
from unittest.mock import patch
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def test_mcp_generator_raises_exception_when_base_actions_not_found(tmp_path):
    """MCPServerGenerator should raise FileNotFoundError when base_actions doesn't exist."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # NO base_actions directory created
    
    # Mock get_python_workspace_root to return a path without base_actions
    fake_repo_root = tmp_path / 'agile_bot'
    fake_repo_root.mkdir(parents=True, exist_ok=True)
    # Don't create base_bot/base_actions so it will fail
    
    # Patch before creating generator (since __init__ calls the methods)
    with patch('agile_bot.bots.base_bot.src.state.workspace.get_python_workspace_root', return_value=fake_repo_root):
        # Create generator - this should raise during initialization
        with pytest.raises(FileNotFoundError, match="Base actions directory not found"):
            MCPServerGenerator(bot_directory=bot_directory)


