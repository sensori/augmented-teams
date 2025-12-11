"""
Tests for CLI exception handling - no fallbacks.

CLI should raise exceptions when:
- Parameter description cannot be inferred
"""
import pytest
from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCLI


def test_cli_raises_exception_when_parameter_description_cannot_be_inferred():
    """CLI should raise ValueError when parameter description cannot be inferred."""
    cli = BaseBotCLI(bot_name='test_bot', bot_directory=Path('/fake/path'))
    
    # When inferring parameter description for unknown command
    with pytest.raises(ValueError, match="Cannot infer parameter description"):
        cli._infer_parameter_description(
            cmd_name='unknown_command_xyz',
            param_num='1',
            cmd_content=''
        )

