"""
Tests for CLI exception handling - no fallbacks.

CLI should raise exceptions when:
- Parameter description cannot be inferred
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def given_mock_bot_created(tmp_path: Path, bot_name: str = 'test_bot'):
    """Given: Mock bot created."""
    mock_bot = Mock()
    mock_bot.name = bot_name
    mock_bot.bot_directory = tmp_path / bot_name
    return mock_bot

def when_cli_infers_parameter_description_for_unknown_command(cli: BaseBotCli):
    """When: CLI infers parameter description for unknown command."""
    return cli._infer_parameter_description(
        cmd_name='unknown_command_xyz',
        param_num='1',
        cmd_content=''
    )


def test_cli_raises_exception_when_parameter_description_cannot_be_inferred(tmp_path):
    """CLI should raise ValueError when parameter description cannot be inferred."""
    # Create a mock bot
    mock_bot = given_mock_bot_created(tmp_path)
    
    # Create CLI with mock bot
    cli = BaseBotCli(bot=mock_bot)
    
    # When inferring parameter description for unknown command
    with pytest.raises(ValueError, match="Cannot infer parameter description"):
        when_cli_infers_parameter_description_for_unknown_command(cli)


