# Command Execution Improvements: Better AI-to-Code Linking

## Problem Statement

Currently, when a user invokes a command like `/code-agent-sync`, the AI agent must:
1. Read the command file
2. Parse the "Runner" section manually
3. Extract CLI command strings
4. Construct terminal commands
5. Execute via terminal

This is inefficient and error-prone. Each new chat session requires rediscovering how to execute commands.

## Proposed Solutions

### Option 1: Structured Execution Metadata (Recommended)

Add YAML frontmatter or structured JSON section to command files with machine-readable execution metadata.

**Example:**
```markdown
---
execution:
  runner: behaviors/code-agent/code_agent_runner.py
  actions:
    generate:
      cli_action: sync
      class: SyncIndexCommand
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
      cli_action: validate-sync
      class: SyncIndexCommand
      method: validate
  working_directory: workspace_root
  path_format: relative_to_workspace
---

### Command: `/code-agent-sync`
...
```

**Benefits:**
- Machine-readable, structured data
- Easy to parse programmatically
- Supports multiple execution methods (CLI, Python import, MCP)
- Type-safe parameter definitions
- Can be validated

**Implementation:**
- AI agent reads frontmatter, extracts execution metadata
- Constructs command automatically based on action and params
- No manual parsing needed

---

### Option 2: Direct Python Import Path

Reference Python classes/functions directly in command files.

**Example:**
```markdown
**Execution:**
* Python Import: `from behaviors.code_agent.code_agent_runner import SyncIndexCommand`
* Method: `SyncIndexCommand.generate(feature_name=None, force=False, target_directories=None)`
* CLI Fallback: `python behaviors/code-agent/code_agent_runner.py sync [args]`
```

**Benefits:**
- Direct code execution (no subprocess overhead)
- Type checking and IDE support
- Faster execution
- Can pass complex objects, not just strings

**Challenges:**
- Requires Python environment setup
- Import path management
- Error handling more complex

---

### Option 3: MCP Tools for Commands

Create MCP tools that wrap command execution.

**Example:**
```json
{
  "tools": [
    {
      "name": "code_agent_sync",
      "description": "Synchronize commands and rules from behaviors to cursor deployed areas",
      "inputSchema": {
        "type": "object",
        "properties": {
          "feature_name": {"type": "string"},
          "force": {"type": "boolean"},
          "target_directories": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  ]
}
```

**Benefits:**
- Standardized tool interface
- Works across different AI agents
- Can be discovered automatically
- Type-safe schemas

**Implementation:**
- Create MCP server that wraps command runners
- Register tools for each command
- AI agent calls MCP tools instead of terminal commands

---

### Option 4: Command Registry Pattern

Create a centralized command registry that maps command names to executable code.

**Example:**
```python
# behaviors/code-agent/command_registry.py
COMMAND_REGISTRY = {
    "code-agent-sync": {
        "runner": "behaviors/code-agent/code_agent_runner.py",
        "class": "SyncIndexCommand",
        "actions": {
            "generate": {"cli": "sync", "method": "generate"},
            "validate": {"cli": "validate-sync", "method": "validate"}
        }
    }
}
```

**Benefits:**
- Single source of truth
- Easy to discover all commands
- Can generate command documentation automatically
- Supports both CLI and direct execution

**Implementation:**
- AI agent imports registry
- Looks up command by name
- Executes via registry entry

---

### Option 5: Hybrid Approach (Best of All)

Combine structured metadata + Python import + MCP tools.

**Structure:**
1. **Command files** have YAML frontmatter with execution metadata
2. **Command registry** provides Python import paths
3. **MCP tools** wrap commands for external access
4. **AI agent** chooses best execution method:
   - Prefer Python import (fastest, type-safe)
   - Fallback to CLI (more compatible)
   - Use MCP for external tools

**Example Command File:**
```markdown
---
execution:
  registry_key: code-agent-sync
  python_import: behaviors.code_agent.code_agent_runner.SyncIndexCommand
  cli_runner: behaviors/code-agent/code_agent_runner.py
  mcp_tool: code_agent_sync
  actions:
    generate:
      cli: sync
      method: generate
      params: [feature_name?, force?, target_directories?]
---

### Command: `/code-agent-sync`
...
```

**AI Agent Execution Logic:**
```python
def execute_command(command_name: str, action: str, **params):
    # 1. Read command file, extract execution metadata
    metadata = parse_command_metadata(command_name)
    
    # 2. Try Python import first (fastest)
    try:
        command_class = import_class(metadata['python_import'])
        method = getattr(command_class, metadata['actions'][action]['method'])
        return method(**params)
    except:
        # 3. Fallback to CLI
        cli_cmd = build_cli_command(metadata, action, params)
        return run_terminal_command(cli_cmd)
```

---

## Recommended Implementation Plan

### Phase 1: Structured Metadata (Quick Win)
1. Add YAML frontmatter to command template
2. Update existing command files with execution metadata
3. Create parser utility for AI agents
4. Update AI agent execution logic to use metadata

### Phase 2: Command Registry
1. Create centralized command registry
2. Auto-generate registry from command files
3. Add Python import paths to registry
4. Update AI agent to prefer Python imports

### Phase 3: MCP Integration (Optional)
1. Create MCP server for command execution
2. Register commands as MCP tools
3. Add MCP tool discovery
4. Use MCP for external tool access

---

## Example: Updated Command Template

```markdown
---
execution:
  registry_key: [command-name]
  python_import: [module.path.ClassName]
  cli_runner: [runner-path]
  actions:
    generate:
      cli: [cli-action]
      method: generate
      params: [param-list]
    validate:
      cli: [validate-action]
      method: validate
  working_directory: workspace_root
---

### Command: `/[command-name]`

**[Purpose]:** [command-purpose]

**[Rule]:**
* `/[rule-name]` — [Rule description]

**Execution:**
* Python: `[ClassName].generate([params])`
* CLI: `python [runner-path] [cli-action] [args]`

**Runner:**
* CLI: `python [runner-path] [execute-action] [command-parameters]` — Execute full workflow
...
```

---

## Benefits Summary

1. **Faster Execution**: Direct Python imports avoid subprocess overhead
2. **Type Safety**: Structured metadata enables type checking
3. **Discoverability**: Registry and MCP tools make commands discoverable
4. **Maintainability**: Single source of truth for execution metadata
5. **Flexibility**: Multiple execution methods (Python, CLI, MCP)
6. **Better UX**: AI agent doesn't need to rediscover execution patterns

---

## Next Steps

1. **Immediate**: Add structured metadata to command template
2. **Short-term**: Create command registry and parser
3. **Long-term**: Add MCP integration for external access

