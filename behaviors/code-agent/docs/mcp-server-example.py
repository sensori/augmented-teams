"""
Example MCP Server for Code-Agent Behavior

This shows how to expose code-agent commands as MCP tools.
Each behavior should have a similar mcp_server.py file.
"""

import sys
from pathlib import Path
from typing import Any

# Add workspace root to path
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))

try:
    from mcp import Server, types
    from behaviors.code_agent.code_agent_runner import (
        SyncIndexCommand,
        FeatureCommand,
        CommandCommand,
        RuleCommand
    )
except ImportError:
    # Fallback if MCP SDK not installed
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

server = Server("code-agent-behavior")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all code-agent command tools"""
    return [
        types.Tool(
            name="code-agent-sync-generate",
            description="Synchronize commands and rules from behaviors to cursor deployed areas",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {
                        "type": "string",
                        "description": "Optional feature name to sync (if not provided, syncs all)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force sync even if destination is newer",
                        "default": False
                    },
                    "target_directories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of directories to sync (defaults to behaviors/)"
                    }
                }
            }
        ),
        types.Tool(
            name="code-agent-sync-validate",
            description="Validate synchronized files follow code-agent principles",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string"},
                    "force": {"type": "boolean", "default": False},
                    "target_directories": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        ),
        types.Tool(
            name="code-agent-sync-correct",
            description="Correct sync operations based on validation errors and chat context",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string"},
                    "chat_context": {
                        "type": "string",
                        "description": "Chat context describing what needs to be corrected"
                    }
                },
                "required": ["chat_context"]
            }
        ),
        types.Tool(
            name="code-agent-feature-generate",
            description="Generate a new code-agent feature",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Name of feature to create"},
                    "location": {"type": "string", "description": "Location for feature directory"},
                    "feature_purpose": {"type": "string", "description": "Purpose of the feature"}
                },
                "required": ["feature_name"]
            }
        ),
        # Add more tools for each command...
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute code-agent command tools"""
    try:
        if name == "code-agent-sync-generate":
            command = SyncIndexCommand(
                feature_name=arguments.get("feature_name"),
                force=arguments.get("force", False),
                target_directories=arguments.get("target_directories")
            )
            result = command.generate()
            return [types.TextContent(
                type="text",
                text=f"Sync completed: {result}"
            )]
        
        elif name == "code-agent-sync-validate":
            command = SyncIndexCommand(
                feature_name=arguments.get("feature_name"),
                force=arguments.get("force", False),
                target_directories=arguments.get("target_directories")
            )
            result = command.validate()
            return [types.TextContent(
                type="text",
                text=f"Validation result: {result}"
            )]
        
        elif name == "code-agent-sync-correct":
            command = SyncIndexCommand(
                feature_name=arguments.get("feature_name")
            )
            result = command.correct(arguments.get("chat_context", ""))
            return [types.TextContent(
                type="text",
                text=f"Correction completed: {result}"
            )]
        
        elif name == "code-agent-feature-generate":
            command = FeatureCommand(
                feature_name=arguments.get("feature_name"),
                location=arguments.get("location"),
                feature_purpose=arguments.get("feature_purpose")
            )
            result = command.generate()
            return [types.TextContent(
                type="text",
                text=f"Feature generated: {result}"
            )]
        
        # Add handlers for other commands...
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

if __name__ == "__main__":
    # Run MCP server over stdio (Cursor's preferred method)
    server.run(stdio=True)

