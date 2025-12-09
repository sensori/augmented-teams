# Directory Architecture Refactoring

## Overview

This refactoring clarifies the distinction between two critical directory concepts that were previously conflated.

## The Two Directories

### 1. Bot Directory (where bot code lives)
- **Purpose**: Contains bot source code, configuration, behaviors, and `agent.json`
- **Example**: `C:/dev/augmented-teams/agile_bot/bots/story_bot`
- **Contains**: 
  - `agent.json` - Bot configuration including WORKING_AREA
  - `config/` - Bot configuration files
  - `behaviors/` - Behavior implementations
  - `src/` - Source code
- **Source**: `BOT_DIRECTORY` environment variable (set in mcp.json)
- **Old names**: `workspace_root`, `botspace_root` (CONFUSING!)

### 2. Workspace Directory (where content files go)
- **Purpose**: Where the bot creates content files for a specific project
- **Example**: `C:/dev/augmented-teams/demo/mob_minion`
- **Contains**:
  - `workflow_state.json` - Current workflow state
  - `activity_log.json` - Activity tracking
  - `docs/` - Generated documentation
  - Project-specific content
- **Source**: `WORKING_AREA` field in `agent.json`, or `WORKING_AREA` env var override
- **Old names**: `working_dir`, `WORKING_AREA` (correct but used inconsistently)

## Configuration Flow

### MCP Server Configuration (mcp.json)

```json
{
  "mcpServers": {
    "story-bot": {
      "command": "python",
      "args": ["C:/dev/augmented-teams/agile_bot/bots/story_bot/src/story_bot_mcp_server.py"],
      "cwd": "C:/dev/augmented-teams",
      "env": {
        "PYTHONPATH": "C:/dev/augmented-teams",
        "BOT_DIRECTORY": "C:/dev/augmented-teams/agile_bot/bots/story_bot"
      }
    }
  }
}
```

### Bot Configuration (agent.json)

Located at: `{BOT_DIRECTORY}/agent.json`

```json
{
  "WORKING_AREA": "C:\\dev\\augmented-teams\\demo\\mob_minion"
}
```

## API Changes

### New Utility Functions (workspace.py)

```python
# Get bot directory from BOT_DIRECTORY environment variable
def get_bot_directory() -> Path:
    """Returns: C:/dev/augmented-teams/agile_bot/bots/story_bot"""
    
# Get workspace directory from agent.json WORKING_AREA field
def get_workspace_directory() -> Path:
    """Returns: C:/dev/augmented-teams/demo/mob_minion"""
    
# Read agent.json from bot directory
def read_agent_json(bot_directory: Path) -> dict:
    """Returns: {'WORKING_AREA': '...'}"""
```

### Updated Class Signatures

**Before:**
```python
Bot(bot_name='story_bot', 
    workspace_root=Path('C:/dev/augmented-teams'),  # Confusing!
    config_path=Path(...))
```

**After:**
```python
Bot(bot_name='story_bot',
    bot_directory=Path('C:/dev/augmented-teams/agile_bot/bots/story_bot'),
    workspace_directory=Path('C:/dev/augmented-teams/demo/mob_minion'),
    config_path=Path(...))
```

## Files Updated

### Core Files
1. ✅ `workspace.py` - New directory utility functions
2. ✅ `story_bot_mcp_server.py` - Uses new functions
3. ✅ `mcp.json` - Added BOT_DIRECTORY env vars
4. ✅ `bot.py` - Bot class updated
5. ✅ `bot.py` - Behavior class updated  
6. ✅ `workflow.py` - Workflow class updated

### Still Need Updates
- Action classes (gather_context, build_knowledge, etc.)
- CLI classes and generators
- MCP server generator
- Tool generators
- Activity tracker
- Tests

## Benefits

1. **Clear Separation**: Bot code location vs. content file location
2. **No More Confusion**: `bot_directory` and `workspace_directory` are self-explanatory
3. **Environment-Driven**: Both directories come from environment/config, not hardcoded
4. **Single Source of Truth**: 
   - Bot location: `BOT_DIRECTORY` env var in mcp.json
   - Workspace location: `WORKING_AREA` in agent.json
5. **No Project Initialization**: No need to "initialize project" - just set in agent.json

## Migration Guide

To update a bot to use the new architecture:

1. **Update mcp.json** - Add `BOT_DIRECTORY` to env:
   ```json
   "env": {
     "BOT_DIRECTORY": "C:/path/to/bot/directory"
   }
   ```

2. **Ensure agent.json exists** in bot directory with `WORKING_AREA`:
   ```json
   {
     "WORKING_AREA": "C:/path/to/workspace"
   }
   ```

3. **Update bot MCP server** to use new functions:
   ```python
   from agile_bot.bots.base_bot.src.state.workspace import (
       get_bot_directory,
       get_workspace_directory
   )
   
   bot_directory = get_bot_directory()
   workspace_directory = get_workspace_directory()
   ```

4. **No more passing directories around** - utility functions handle it automatically!

