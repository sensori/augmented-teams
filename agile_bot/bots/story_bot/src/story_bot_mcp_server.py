"""
Story Bot MCP Server Entry Point

Runnable MCP server for story_bot using FastMCP and base generator.
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

# 2. Read bot_config.json and set workspace directory (if not already set by mcp.json)
if 'WORKING_AREA' not in os.environ:
    config_path = bot_directory / 'bot_config.json'
    if config_path.exists():
        bot_config = json.loads(config_path.read_text(encoding='utf-8'))
        # Check mcp.env.WORKING_AREA (standard location)
        if 'mcp' in bot_config and 'env' in bot_config['mcp']:
            mcp_env = bot_config['mcp']['env']
            if 'WORKING_AREA' in mcp_env:
                os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']
        # Fallback to top-level WORKING_AREA
        elif 'WORKING_AREA' in bot_config:
            os.environ['WORKING_AREA'] = bot_config['WORKING_AREA']

# ============================================================================
# Now import - everything will read from environment variables
# ============================================================================

from agile_bot.bots.base_bot.src.bot.workspace import (
    get_bot_directory,
    get_workspace_directory
)
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def main():
    """Main entry point for story_bot MCP server.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from bot_config.json (or overridden by mcp.json env)
    
    All subsequent code reads from these environment variables.
    """
    # Get directories (these now just read from env vars we set above)
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()
    
    # Create MCP server
    generator = MCPServerGenerator(
        bot_directory=bot_directory
    )

    mcp_server = generator.create_server_instance()
    generator.register_all_behavior_action_tools(mcp_server)

    mcp_server.run()


if __name__ == '__main__':
    main()
