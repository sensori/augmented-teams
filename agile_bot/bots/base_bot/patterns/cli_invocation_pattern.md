# CLI Invocation Pattern

## Overview

CLI (Command Line Interface) provides a terminal-based alternative to MCP protocol for invoking bot tools and behaviors. CLI commands mirror MCP tool hierarchy and use the same routing logic.

**Key Principle:** CLI routes to bot, bot executes. CLI parses arguments, routes to bot, and returns/prints result (same as MCP tools).

## Implementation Structure

### Base CLI Class (90% of Functionality)

**Base CLI class in base_bot contains all common functionality:**

```python
# agile_bot/bots/base_bot/src/cli/base_bot_cli.py

#!/usr/bin/env python3
"""Base Bot CLI - 90% of functionality inherited by bot-specific CLIs"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.bot import Bot

class BaseBotCli:
    """Base CLI class - bot-specific CLIs inherit 90% of functionality from this"""
    
    def __init__(self, bot_name: str, bot_config_path: Path, workspace_root: Path = None):
        self.bot_name = bot_name
        self.workspace_root = workspace_root or Path.cwd()
        self.bot_config_path = bot_config_path
        
        # Instantiate bot with config
        self.bot = Bot(
            bot_name=self.bot_name,
            workspace_root=self.workspace_root,
            config_path=self.bot_config_path
        )
    
    def run(self, behavior_name: str = None, action_name: str = None, close: bool = False, **kwargs):
        """Single function with optional parameters to route to bot
        
        Args:
            behavior_name: Optional behavior name
            action_name: Optional action name
            close: If True, close current action
            **kwargs: Additional parameters to pass to action
        """
        if close:
            # Close current action
            result = self.bot.close_current_action()
        elif action_name:
            # Route directly to specific action
            behavior_obj = getattr(self.bot, behavior_name)
            action_method = getattr(behavior_obj, action_name)
            result = action_method(parameters=kwargs)
        elif behavior_name:
            # Route to behavior, auto-forward to current action
            behavior_obj = getattr(self.bot, behavior_name)
            result = behavior_obj.forward_to_current_action()
        else:
            # Route to current behavior/action from workflow state
            result = self.bot.forward_to_current_behavior_and_current_action()
        
        # Return serializable dict (same as MCP tools)
        return {
            "status": result.status,
            "behavior": result.behavior,
            "action": result.action,
            "data": result.data
        }
    
    def list_behaviors(self):
        """List available behaviors"""
        print(f"Available behaviors for {self.bot_name}:")
        for behavior in self.bot.behaviors:
            print(f"  - {behavior}")
    
    def list_actions(self, behavior_name: str):
        """List available actions for behavior"""
        # Implementation to list actions
        print(f"Available actions for {behavior_name}:")
        # ... list actions logic ...
    
    @staticmethod
    def parse_arguments(description: str = "Bot CLI"):
        """Parse CLI arguments - generic for all bots"""
        import argparse
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('behavior', nargs='?', help='Behavior name (optional)')
        parser.add_argument('action', nargs='?', help='Action name (optional)')
        parser.add_argument('--close', action='store_true', help='Close current action')
        parser.add_argument('--list', action='store_true', help='List available options')
        
        args, unknown = parser.parse_known_args()
        
        # Parse remaining arguments as action parameters
        params = {}
        for arg in unknown:
            if '=' in arg:
                key, value = arg.split('=', 1)
                params[key.lstrip('--')] = value
        
        return args, params
    
    def main(self):
        """Main CLI entry point - generic for all bots"""
        args, params = BaseBotCli.parse_arguments(description=f"{self.bot_name} CLI")
        
        try:
            if args.list:
                if args.behavior:
                    self.list_actions(args.behavior)
                else:
                    self.list_behaviors()
            else:
                # Single function with optional parameters
                result = self.run(
                    behavior_name=args.behavior,
                    action_name=args.action,
                    close=args.close,
                    **params
                )
                # Print result (same approach as MCP tools)
                print(json.dumps(result, indent=2))
        except Exception as e:
            import sys
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
```

### Bot-Specific CLI (Minimal - Inherits from Base)

**Bot-specific CLI that inherits from base:**

```python
# agile_bot/bots/{bot_name}/src/{bot_name}_cli.py

#!/usr/bin/env python3
"""{BotName} CLI"""

import sys
from pathlib import Path
from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli

class {BotName}Cli(BaseBotCli):
    """CLI for {bot_name} - inherits 90% of functionality from BaseBotCli"""
    
    def __init__(self, workspace_root: Path = None):
        # Bot-specific values
        bot_name = '{bot_name}'
        bot_config_path = (
            (workspace_root or Path.cwd()) / 
            'agile_bot' / 
            'bots' / 
            '{bot_name}' / 
            'config' / 
            'bot_config.json'
        )
        # Call base class with bot-specific values
        super().__init__(
            bot_name=bot_name,
            bot_config_path=bot_config_path,
            workspace_root=workspace_root
        )

def main():
    """Main CLI entry point - calls base class main()"""
    cli = {BotName}Cli()
    cli.main()

if __name__ == '__main__':
    main()
```

### Shell Script Entry Point (Unix/Linux/Mac)

**Shell script entry point for bot CLI:**

```bash
#!/bin/bash
# {bot_name}_cli - Shell script entry point for {BotName} CLI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Run Python CLI script
python3 "$SCRIPT_DIR/src/{bot_name}_cli.py" "$@"
```

**Shell Script Location:**
- **Path:** `agile_bot/bots/{bot_name}/{bot_name}_cli`
- **Example:** `agile_bot/bots/story_bot/story_bot_cli`
- **Location:** Root directory of bot package (same level as `src/` and `config/` folders)
- **Purpose:** Executable entry point for Unix/Linux/Mac that can be invoked with parameters

**Usage on Unix/Linux/Mac:**
```bash
# From bot directory:
cd agile_bot/bots/story_bot
./story_bot_cli                                    # Run current action
./story_bot_cli exploration                        # Run behavior
./story_bot_cli exploration gather_context         # Run specific action
./story_bot_cli --close                            # Close current action
./story_bot_cli --list                             # List behaviors
./story_bot_cli exploration --list                 # List actions for behavior
./story_bot_cli exploration gather_context --param1=value1  # Pass parameters

# From workspace root with full path:
./agile_bot/bots/story_bot/story_bot_cli exploration gather_context
```

### PowerShell Script Entry Point (Windows)

**PowerShell script entry point for bot CLI (Windows):**

```powershell
# {bot_name}_cli.ps1
# {bot_name} - PowerShell script entry point for {BotName} CLI

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$WORKSPACE_ROOT = (Resolve-Path "$SCRIPT_DIR\..\..\..").Path

# Run Python CLI script with all arguments passed through
python "$SCRIPT_DIR\src\{bot_name}_cli.py" $args
```

**PowerShell Script Location:**
- **Path:** `agile_bot/bots/{bot_name}/{bot_name}_cli.ps1`
- **Example:** `agile_bot/bots/story_bot/story_bot_cli.ps1`
- **Location:** Root directory of bot package (same level as `src/` and `config/` folders)
- **Purpose:** Executable entry point for Windows PowerShell that can be invoked with parameters

**Usage on Windows:**
```powershell
# From bot directory:
cd agile_bot\bots\story_bot
.\story_bot_cli.ps1                                    # Run current action
.\story_bot_cli.ps1 exploration                        # Run behavior
.\story_bot_cli.ps1 exploration gather_context         # Run specific action
.\story_bot_cli.ps1 --close                            # Close current action
.\story_bot_cli.ps1 --list                             # List behaviors
.\story_bot_cli.ps1 exploration --list                   # List actions for behavior
.\story_bot_cli.ps1 exploration gather_context --param1=value1  # Pass parameters

# From workspace root with full path:
.\agile_bot\bots\story_bot\story_bot_cli.ps1 exploration gather_context
```

### File Location

**Pattern:** Base CLI in base_bot, bot-specific CLIs inherit from it, shell script entry point

**Structure:**
```
agile_bot/bots/
├── base_bot/
│   ├── src/
│   │   ├── bot/
│   │   │   └── bot.py              ← Bot and Behavior classes (existing)
│   │   ├── cli/
│   │   │   └── base_bot_cli.py    ← Base CLI class (90% of functionality)
│   │   └── base_actions/              ← Actions (configured, not extended)
└── {bot_name}/
    ├── src/
    │   └── {bot_name}_cli.py      ← Python CLI script (cross-platform)
    ├── {bot_name}_cli             ← Bash shell script entry point (Unix/Linux/Mac)
    ├── {bot_name}_cli.ps1         ← PowerShell script entry point (Windows)
    ├── src/
    │   └── {bot_name}_mcp_server.py  ← MCP server (existing)
    └── config/
        └── bot_config.json         ← Bot config
```

### Cursor Command Files

**CLI generates cursor command files for convenient IDE integration:**

```python
# Generate cursor command files
commands = cli.generate_cursor_commands(
    commands_dir=Path('.cursor/commands'),
    cli_script_path=Path('agile_bot/bots/story_bot/story_bot')
)

# Returns:
# {
#     'bot': Path('.cursor/commands/bot'),
#     'bot-behavior': Path('.cursor/commands/bot-behavior'),
#     'bot-behavior-action': Path('.cursor/commands/bot-behavior-action'),
#     'bot-close': Path('.cursor/commands/bot-close')
# }
```

**Generated Command Files:**

For each bot, generates command files with bot name in filename:

1. **`.cursor/commands/<bot-name>.md`** - Invoke bot (routes to current behavior/action)
   ```
   agile_bot/bots/story_bot/story_bot story_bot
   ```

2. **`.cursor/commands/<bot-name>-<behavior>.md`** - Invoke behavior (one file per behavior)
   ```
   agile_bot/bots/story_bot/story_bot story_bot exploration
   ```

3. **`.cursor/commands/<bot-name>-<behavior>-<action>.md`** - Invoke specific action (one file per action)
   ```
   agile_bot/bots/story_bot/story_bot story_bot exploration gather_context
   ```

4. **`.cursor/commands/<bot-name>-close.md`** - Close current action
   ```
   agile_bot/bots/story_bot/story_bot story_bot --close
   ```

**Example for story_bot with exploration behavior:**
- `story_bot.md` - invoke bot
- `story_bot-exploration.md` - invoke exploration behavior
- `story_bot-exploration-gather_context.md` - invoke gather_context action
- `story_bot-exploration-build_knowledge.md` - invoke build_knowledge action
- `story_bot-close.md` - close current action

**Usage in Cursor:**
- Commands appear in Cursor command palette
- Each bot gets its own set of command files
- Bot name, behavior, and action are hardcoded in filenames and command content
- User selects specific command (no parameters needed)
