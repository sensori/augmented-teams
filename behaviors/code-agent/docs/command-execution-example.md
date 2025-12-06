# Command Execution Example: Before vs After

## Problem: Current Approach

When you invoke `/code-agent-sync`, the AI agent currently:

1. Reads the command file
2. Manually parses the "Runner" section
3. Extracts CLI command strings
4. Constructs terminal command: `python behaviors/code-agent/code_agent_runner.py sync`
5. Executes via subprocess

**Issues:**
- Must rediscover execution pattern in each chat session
- Error-prone manual parsing
- No type safety
- Slow (subprocess overhead)

---

## Solution: Structured Metadata + Command Executor

### Step 1: Update Command File with Metadata

**Before:**
```markdown
### Command: `/code-agent-sync`

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py sync [feature-name] [--force] [--target-dirs]`
```

**After:**
```markdown
---
execution:
  registry_key: code-agent-sync
  python_import: behaviors.code_agent.code_agent_runner.SyncIndexCommand
  cli_runner: behaviors/code-agent/code_agent_runner.py
  actions:
    generate:
      cli: sync
      method: generate
      params:
        - name: feature_name
          optional: true
          type: str
        - name: force
          optional: true
          type: bool
          flag: --force
        - name: target_directories
          optional: true
          type: list[str]
          flag: --target-dirs
    validate:
      cli: validate-sync
      method: validate
  working_directory: workspace_root
---

### Command: `/code-agent-sync`
...
```

### Step 2: AI Agent Uses Command Executor

**Before (Manual):**
```python
# AI agent must manually:
1. Read command file
2. Parse "Runner" section
3. Extract CLI command
4. Build command string
5. Run subprocess
```

**After (Automatic):**
```python
from behaviors.code_agent.utils.command_executor import execute_command

# One line - handles everything automatically
result = execute_command("code-agent-sync", "generate")
# Or with parameters:
result = execute_command("code-agent-sync", "generate", 
                         feature_name="bdd", force=True)
```

### Step 3: Execution Flow

```
User: /code-agent-sync
  ↓
AI Agent: execute_command("code-agent-sync", "generate")
  ↓
Command Executor:
  1. Finds command file (.cursor/commands/code-agent-sync-cmd.md)
  2. Parses YAML frontmatter
  3. Extracts execution metadata
  4. Tries Python import first:
     - Imports: behaviors.code_agent.code_agent_runner.SyncIndexCommand
     - Instantiates: SyncIndexCommand()
     - Calls: .generate()
  5. If Python import fails, falls back to CLI:
     - Runs: python behaviors/code-agent/code_agent_runner.py sync
  ↓
Returns result with success status and output
```

---

## Benefits

### 1. **Faster Execution**
- Python import: ~10ms (direct function call)
- CLI subprocess: ~100-500ms (process startup overhead)
- **10-50x faster** for Python imports

### 2. **Type Safety**
- Structured metadata enables parameter validation
- IDE support for command classes
- Catch errors at import time, not runtime

### 3. **Discoverability**
- All commands have consistent metadata structure
- Can auto-generate command documentation
- Can build command registry automatically

### 4. **Maintainability**
- Single source of truth (command file metadata)
- Changes to execution logic in one place
- No need to update multiple locations

### 5. **Better UX**
- AI agent doesn't need to rediscover patterns
- Consistent execution across all commands
- Automatic fallback (Python → CLI → MCP)

---

## Migration Plan

### Phase 1: Add Metadata to Existing Commands
1. Update command template (✅ Done)
2. Add metadata to high-priority commands:
   - `/code-agent-sync`
   - `/code-agent-feature`
   - `/code-agent-command`
   - `/code-agent-rule`

### Phase 2: Update AI Agent Execution Logic
1. Import `command_executor` utility
2. Replace manual CLI parsing with `execute_command()` calls
3. Test with existing commands

### Phase 3: Expand to All Commands
1. Add metadata to all command files
2. Update all AI agent execution patterns
3. Remove manual CLI parsing code

---

## Example: Updated `/code-agent-sync` Command

See `behaviors/code-agent/sync/code-agent-sync-cmd.md` for full example with metadata.

**Key Changes:**
- YAML frontmatter with execution metadata
- Python import path specified
- Parameter definitions with types
- Multiple execution methods (Python, CLI, MCP)

---

## Next Steps

1. **Test the executor**: Try executing a command using the new utility
2. **Update one command**: Add metadata to `/code-agent-sync` as proof of concept
3. **Update AI agent**: Modify AI agent to use `execute_command()` instead of manual parsing
4. **Expand**: Add metadata to all commands gradually

---

## Questions?

- How does this handle commands with complex parameters?
  - Metadata supports full parameter definitions with types and flags
  
- What if Python import fails?
  - Automatic fallback to CLI execution
  
- Can this work with MCP tools?
  - Yes, metadata includes `mcp_tool` field for external tool access
  
- How do I add metadata to a new command?
  - Use the updated command template with YAML frontmatter

