#!/usr/bin/env python3
"""
Story Bot CLI Entry Point

Command-line interface for story_bot using BaseBotCli.

Usage:
    story_bot [behavior] [action] [--options]
    story_bot --help          # Show help/usage documentation
    story_bot --list          # List available behaviors
    story_bot <behavior> --list  # List available actions for behavior
    story_bot --close         # Close current action

Examples:
    story_bot                          # Route to current behavior/action from workflow state
    story_bot exploration               # Route to exploration behavior, auto-forward to current action
    story_bot exploration gather_context  # Route directly to exploration.gather_context action
    story_bot exploration gather_context --increment_file=increment.txt  # With parameters
"""
from pathlib import Path
import sys

# Add workspace root to path
# From src/{bot_name}_cli.py, go up to workspace root:
# src/ -> {bot_name}/ -> bots/ -> agile_bot/ -> workspace_root (5 levels up)
workspace_root = Path(__file__).parent.parent.parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli


def main():
    """Main CLI entry point."""
    bot_name = 'story_bot'
    bot_config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
    
    cli = BaseBotCli(
        bot_name=bot_name,
        bot_config_path=bot_config_path,
        workspace_root=workspace_root
    )
    
    cli.main()


if __name__ == '__main__':
    main()
