# AI Agent Execution Context Guide

## Purpose
This document provides critical execution context information for AI agents running command runners to prevent common path and execution issues.

## Critical Rules

### 1. Working Directory
**ALWAYS run commands from workspace root**
- Workspace root: `C:\dev\augmented-teams` (or equivalent)
- **NEVER** assume current directory
- **ALWAYS** navigate to workspace root first: `cd C:\dev\augmented-teams`

### 2. PowerShell Syntax
- **Use semicolon `;` to chain commands**, NOT `&&`
- **Correct**: `cd C:\dev\augmented-teams; python behaviors\code-agent\code_agent_runner.py sync`
- **Wrong**: `cd C:\dev\augmented-teams && python behaviors\code-agent\code_agent_runner.py sync`

### 3. Path Format
- **Runner paths in command files are relative to workspace root**
- Example: `behaviors/bdd/bdd-runner.py` means `C:\dev\augmented-teams\behaviors\bdd\bdd-runner.py`
- **For PowerShell**: Use backslashes `\` in paths
- **For Python code**: Use forward slashes `/` or escaped backslashes `\\`

### 4. Command Execution Pattern
**Standard pattern to follow:**
```powershell
cd C:\dev\augmented-teams; python behaviors\[feature]\[runner].py [action] [args]
```

**Examples:**
- `cd C:\dev\augmented-teams; python behaviors\code-agent\code_agent_runner.py sync`
- `cd C:\dev\augmented-teams; python behaviors\bdd\bdd-runner.py workflow test_file.py mamba`
- `cd C:\dev\augmented-teams; python behaviors\stories\stories_runner.py story-shape generate`

### 5. Test Execution Context
Some commands require specific working directories:
- **Python/Mamba tests**: Run from test file's parent directory (for proper imports)
- **JavaScript/Jest tests**: Run from project root (where package.json is located)
- **Command runners**: Always run from workspace root

### 6. Before Running Any Command
1. Check if you're in workspace root (if unsure, navigate there first)
2. Use PowerShell syntax (`;` not `&&`)
3. Use correct path format (backslashes for PowerShell)
4. Verify the runner file exists at the specified path

## Common Mistakes to Avoid

1. ❌ **Running from subdirectory**: `cd behaviors/stories; python code_agent_runner.py sync`
   ✅ **Correct**: `cd C:\dev\augmented-teams; python behaviors\code-agent\code_agent_runner.py sync`

2. ❌ **Using bash syntax in PowerShell**: `cd C:\dev\augmented-teams && python ...`
   ✅ **Correct**: `cd C:\dev\augmented-teams; python ...`

3. ❌ **Assuming current directory**: Running commands without checking/navigating
   ✅ **Correct**: Always `cd C:\dev\augmented-teams` first

4. ❌ **Wrong path format**: `python behaviors/code-agent/code_agent_runner.py` (forward slashes in PowerShell)
   ✅ **Correct**: `python behaviors\code-agent\code_agent_runner.py` (backslashes in PowerShell)

## Memory Suggestion for User

**Create a memory with this content:**
```
**CRITICAL: Command Runner Execution Context**

When running Python command runners:
1. ALWAYS run from workspace root (C:\dev\augmented-teams)
2. Use PowerShell syntax: semicolon `;` to chain commands, NOT `&&`
3. Runner paths are relative to workspace root
4. Pattern: `cd C:\dev\augmented-teams; python behaviors\[feature]\[runner].py [action] [args]`
5. Never assume current directory - always navigate to workspace root first
```

