"""
Tests for MCPServerGenerator exception handling - no fallbacks.

MCPServerGenerator should raise exceptions when:
- Base actions directory doesn't exist
"""
import pytest
from pathlib import Path
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def test_mcp_generator_raises_exception_when_base_actions_not_found(tmp_path):
    """MCPServerGenerator should raise FileNotFoundError when base_actions doesn't exist."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # NO base_actions directory created
    
    # Create generator
    generator = MCPServerGenerator(bot_directory=bot_directory)
    
    # When discovering workflow actions
    with pytest.raises(FileNotFoundError, match="Base actions directory not found"):
        generator._discover_workflow_actions()
    
    # When discovering independent actions
    with pytest.raises(FileNotFoundError, match="Base actions directory not found"):
        generator._discover_independent_actions()

