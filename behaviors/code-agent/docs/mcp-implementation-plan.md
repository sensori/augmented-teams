# MCP Server Implementation Plan

## Goal
Expose each behavior's commands as MCP tools, allowing AI agents to call commands directly without CLI parsing.

## Steps

### 1. Install MCP Python SDK
```bash
pip install mcp
```

### 2. Create MCP Server for Each Behavior

For each behavior (`bdd`, `ddd`, `character`, `code-agent`, `stories`):

1. Create `behaviors/{behavior-name}/mcp_server.py`
2. Import command classes from runner
3. Register one tool per command action
4. Implement tool handlers that call command methods directly

### 3. Tool Naming Pattern

Tools follow: `{registry-key}-{action}`

Examples:
- `bdd-scaffold-generate`
- `bdd-scaffold-validate`
- `bdd-scaffold-correct`
- `code-agent-sync-generate`
- `character-sheet-generate`
- `ddd-structure-generate`

### 4. MCP Config Files

Each behavior needs:
- `behaviors/{behavior-name}/{behavior-name}-mcp.json` (source)
- Synced to `.cursor/mcp/{behavior-name}-mcp.json` (deployed)

Config structure:
```json
{
  "mcpServers": {
    "{behavior-name}-behavior": {
      "command": "python",
      "args": ["behaviors/{behavior-name}/mcp_server.py"],
      "env": {}
    }
  }
}
```

### 5. Register in Main Config

Update main `mcp.json` (or `.cursor/mcp.json`) to include all behavior servers.

### 6. Benefits

- ✅ Direct Python function calls (no CLI parsing)
- ✅ Type-safe with JSON schemas
- ✅ Faster execution
- ✅ Discoverable via `list_tools()`
- ✅ Standard MCP protocol

### 7. Character Behavior Special Case

Character commands use Agent classes, not Command classes:
- Import `CharacterSheetAgent`, `CharacterRollAgent`, etc.
- Call agent methods directly (e.g., `agent.build_prompt()`, `agent.execute_roll()`)

### 8. Testing

Test each MCP server:
```python
from mcp import Client
client = Client(stdio=True)
tools = await client.list_tools()
result = await client.call_tool("bdd-scaffold-generate", {"test_file_path": "..."})
```

