# MCP Server Setup Guide

## Overview

Each behavior should expose its commands as MCP tools via a dedicated MCP server. This allows AI agents to call commands directly as MCP tools, which is faster and more reliable than CLI parsing.

## Architecture

For each behavior (e.g., `bdd`, `ddd`, `character`, `code-agent`):

1. **MCP Server**: Python script that implements the MCP protocol
2. **MCP Tools**: One tool per command action (e.g., `bdd-scaffold-generate`, `bdd-scaffold-validate`)
3. **MCP Config**: JSON file in `.cursor/mcp/` that registers the server

## Structure

```
behaviors/
  {behavior-name}/
    code/
      mcp_server.py       # MCP server implementation (in code/ folder)
    {behavior-name}-mcp.json  # MCP config (synced to .cursor/mcp/)
```

**Note**: For character behavior, the MCP server is in `behaviors/character/code/mcp_server.py` to keep all character-specific code together.

## MCP Server Implementation Pattern

Each behavior's MCP server should:

1. Use the `mcp` Python SDK (or implement stdio protocol)
2. Register one tool per command action
3. Call the command class methods directly

### Example: Character MCP Server (Agent-based)

Character commands use Agent classes directly, not Command classes. Here's the pattern:

```python
# behaviors/character/code/mcp_server.py
import sys
from pathlib import Path
from mcp import Server, types
from behaviors.bdd.bdd_runner import BDDScaffoldCommand, BDDTestCommand, etc.

server = Server("bdd-behavior")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all BDD command tools"""
    return [
        types.Tool(
            name="bdd-scaffold-generate",
            description="Generate BDD scaffold hierarchy from domain map",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_file_path": {"type": "string", "description": "Path to test file"}
                },
                "required": ["test_file_path"]
            }
        ),
        types.Tool(
            name="bdd-scaffold-validate",
            description="Validate BDD scaffold hierarchy",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_file_path": {"type": "string", "description": "Path to test file"}
                },
                "required": ["test_file_path"]
            }
        ),
        # ... more tools for each command/action
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute BDD command tools"""
    if name == "bdd-scaffold-generate":
        test_file_path = arguments.get("test_file_path")
        command = BDDScaffoldCommand(...)
        result = command.generate()
        return [types.TextContent(type="text", text=str(result))]
    
    elif name == "bdd-scaffold-validate":
        test_file_path = arguments.get("test_file_path")
        command = BDDScaffoldCommand(...)
        result = command.validate()
        return [types.TextContent(type="text", text=str(result))]
    
    # ... handle other tools
    
    raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    server.run(stdio=True)
```

## MCP Config File

Each behavior needs a config file in `.cursor/mcp/{behavior-name}-mcp.json`:

```json
{
  "mcpServers": {
    "character-behavior": {
      "command": "python",
      "args": [
        "behaviors/character/code/mcp_server.py"
      ],
      "cwd": "behaviors/character/code",
      "env": {}
    }
  }
}
```

## Registration in Main MCP Config

**MCP servers start automatically when Cursor loads the project** - no manual initiation needed!

The main `mcp.json` at the project root should register all behavior servers:

```json
{
  "mcpServers": {
    "bdd-behavior": {
      "command": "python",
      "args": ["behaviors/bdd/mcp_server.py"]
    },
    "ddd-behavior": {
      "command": "python",
      "args": ["behaviors/ddd/mcp_server.py"]
    },
    "character-behavior": {
      "command": "python",
      "args": ["behaviors/character/code/mcp_server.py"],
      "cwd": "behaviors/character/code"
    },
    "code-agent-behavior": {
      "command": "python",
      "args": ["behaviors/code-agent/mcp_server.py"]
    }
  }
}
```

## Tool Naming Convention

### For Command-based Behaviors (BDD, DDD, Code-Agent)
Tools follow: `{registry-key}-{action}`

- `bdd-scaffold-generate`
- `bdd-scaffold-validate`
- `bdd-scaffold-correct`
- `code-agent-sync-generate`
- etc.

### For Agent-based Behaviors (Character)
Character commands don't have generate/validate/correct actions - they have agent methods with parameters. Tools follow: `{registry-key}-{method-name}`

- `character-sheet-load` (loads sheet and queries by category)
- `character-tactics-recommend` (tactical recommendations - separate from sheet tools)
- `character-roll-execute` (executes roll mechanics)
- `character-chat-build-prompt` (builds chat prompt)
- `character-episode-manage` (episode management)
- `character-generate-profile` (generates character profile)

## Benefits

1. **Direct Function Calls**: No CLI parsing needed
2. **Type Safety**: MCP tools have schemas
3. **Faster**: Direct Python imports
4. **Discoverable**: AI agents can list available tools
5. **Standardized**: Uses MCP protocol that Cursor supports

## Implementation Steps

1. Install MCP Python SDK: `pip install mcp`
2. Create `mcp_server.py` for each behavior
3. Register all command tools
4. Create MCP config JSON
5. Test with MCP client

