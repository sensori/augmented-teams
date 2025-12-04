"""
Story Bot MCP Server Entry Point

Runnable MCP server for story_bot using FastMCP and base generator.
"""
from pathlib import Path
import sys

workspace_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))

from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def main():
    """Main entry point for story_bot MCP server."""
    generator = MCPServerGenerator(
        workspace_root=workspace_root,
        bot_location='agile_bot/bots/story_bot'
    )
    
    mcp_server = generator.create_server_instance()
    generator.register_all_behavior_action_tools(mcp_server)
    
    mcp_server.run()


if __name__ == '__main__':
    main()
