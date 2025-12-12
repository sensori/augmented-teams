#!/usr/bin/env python3
"""
Story Bot CLI Entry Point

Command-line interface for story_bot using BaseBotCli.

Usage:
    story_bot [--behavior <name>] [--action <name>] [--options]
    story_bot --help          # Show help/usage documentation
    story_bot --list          # List available behaviors
    story_bot --behavior <name> --list  # List available actions for behavior
    story_bot --close         # Close current action

Examples:
    story_bot                                    # Route to current behavior/action from workflow state
    story_bot --behavior exploration            # Route to exploration behavior, auto-forward to current action
    story_bot --behavior exploration --action gather_context  # Route directly to exploration.gather_context action
    story_bot --behavior exploration --action gather_context --increment_file=increment.txt  # With parameters
"""
from pathlib import Path
import sys
import os
import json

# Setup Python import path for package imports
python_workspace_root = Path(__file__).parent.parent.parent.parent.parent
if str(python_workspace_root) not in sys.path:
    sys.path.insert(0, str(python_workspace_root))

# ============================================================================
# BOOTSTRAP: Set environment variables before importing other modules
# ============================================================================

# 1. Self-detect bot directory from this script's location
bot_directory = Path(__file__).parent.parent  # src/ -> story_bot/
os.environ['BOT_DIRECTORY'] = str(bot_directory)

# 2. Read agent.json and set workspace directory (if not already set)
if 'WORKING_AREA' not in os.environ and 'WORKING_DIR' not in os.environ:
    agent_json_path = bot_directory / 'agent.json'
    if agent_json_path.exists():
        agent_config = json.loads(agent_json_path.read_text(encoding='utf-8'))
        if 'WORKING_AREA' in agent_config:
            os.environ['WORKING_AREA'] = agent_config['WORKING_AREA']

# ============================================================================
# Now import - everything will read from environment variables
# ============================================================================

from agile_bot.bots.base_bot.src.state.workspace import get_bot_directory, get_workspace_directory
from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli


def main():
    """Main CLI entry point.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from agent.json (or pre-set by user)
    
    All subsequent code reads from these environment variables.
    """
    # Get directories (these now just read from env vars we set above)
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()

    bot_name = 'story_bot'
    bot_config_path = bot_directory / 'config' / 'bot_config.json'
    
    cli = BaseBotCli(
        bot_name=bot_name,
        bot_config_path=bot_config_path
    )
    
    cli.main()


if __name__ == '__main__':
    main()
