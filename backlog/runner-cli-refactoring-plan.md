# Runner CLI Refactoring Plan

**Date:** 2025-01-11
**Status:** Planned
**Priority:** Medium

## Problem Statement

All behavior runners (BDD, DDD, Stories, Code-Agent, Clean-Code) have significant duplicated CLI boilerplate code:
- Windows encoding setup (identical across all runners)
- Dynamic import of common_command_runner (identical across all runners)
- Command dispatching with if/elif chains (similar pattern across all)
- Guard checks (only in BDD, but should be universal)
- Error handling (similar across all)
- Usage message generation (manual in each runner)

**Current State:**
- BDD runner: 259 lines of CLI code
- DDD runner: 70 lines of CLI code  
- Code-Agent runner: 200+ lines of CLI code
- Stories runner: Minimal (incomplete)
- Clean-Code runner: Empty (TODO)

## Solution: CommandRegistry Pattern

Create reusable CLI infrastructure in `common_command_runner.py` and simplify all runners.

---

## Phase 1: Add to common_command_runner.py

### 1.1 Setup Utilities

```python
# ============================================================================
# CLI HELPERS
# ============================================================================

def setup_windows_encoding():
    """Fix Windows console encoding for UTF-8 output"""
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def require_command_invocation(command_name: str):
    """
    Guard to prevent direct runner execution.
    
    Checks if runner was invoked with --from-command flag (set by Cursor commands).
    If not, displays helpful message directing user to proper slash command.
    
    Args:
        command_name: The slash command name (e.g., "bdd-validate")
    """
    import sys
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)
```

### 1.2 CommandRegistry Class

```python
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CommandInfo:
    """Information about a registered command"""
    handler: Callable
    usage: str
    guard: Optional[str] = None
    description: Optional[str] = None

class CommandRegistry:
    """
    Registry for CLI commands with automatic dispatching.
    
    Usage:
        registry = CommandRegistry("my-runner.py")
        registry.register("validate", handle_validate, "validate <file>", guard="my-validate")
        registry.dispatch(sys.argv)
    """
    
    def __init__(self, runner_name: str):
        self.runner_name = runner_name
        self.commands: Dict[str, CommandInfo] = {}
    
    def register(self, name: str, handler: Callable, usage: str, 
                 guard: Optional[str] = None, description: Optional[str] = None):
        """
        Register a command handler.
        
        Args:
            name: Command name (e.g., "validate")
            handler: Function to call with args: handler(args: List[str])
            usage: Usage string for help (e.g., "validate <file-path> [--thorough]")
            guard: Cursor command name for guard check (e.g., "bdd-validate")
            description: Optional description for help text
        """
        self.commands[name] = CommandInfo(handler, usage, guard, description)
    
    def dispatch(self, argv: List[str]):
        """
        Dispatch command from argv.
        
        Args:
            argv: sys.argv (includes script name at argv[0])
        """
        if len(argv) < 2:
            self.print_usage()
            sys.exit(1)
        
        command = argv[1]
        if command not in self.commands:
            print(f"Unknown command: {command}")
            self.print_usage()
            sys.exit(1)
        
        cmd_info = self.commands[command]
        
        # Guard check
        if cmd_info.guard:
            require_command_invocation(cmd_info.guard)
        
        # Call handler with remaining args
        try:
            cmd_info.handler(argv[2:])
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def print_usage(self):
        """Print usage message with all registered commands"""
        print(f"Usage: python {self.runner_name} <command> [args...]")
        print("\nCommands:")
        for name, info in self.commands.items():
            print(f"  {info.usage}")
            if info.description:
                print(f"    {info.description}")
```

### 1.3 Standard Action Handler

```python
def standard_action_handler(command_class, action: str, args: List[str]) -> str:
    """
    Standard handler for generate/validate/execute/correct actions.
    
    Args:
        command_class: Command class to instantiate
        action: Action to perform ("generate", "validate", "execute", "correct")
        args: Command arguments to pass to command_class constructor
    
    Returns:
        Result string from command execution
    """
    command = command_class(*args)
    
    if action == "generate":
        result = command.generate()
    elif action == "validate":
        result = command.validate()
    elif action == "execute":
        result = command.execute()
    elif action == "correct":
        chat_context = args[-1] if args else "User requested correction based on current chat context"
        result = command.correct(chat_context)
    else:
        raise ValueError(f"Unknown action: {action}")
    
    print(result)
    return result
```

---

## Phase 2: Refactor Each Runner

### 2.1 BDD Runner Example

**Before:** 259 lines of CLI code with if/elif chains

**After:**
```python
"""BDD Runner - Simplified with CommandRegistry"""

from pathlib import Path
import sys

# Import common CLI helpers
from common_command_runner import (
    setup_windows_encoding, CommandRegistry, require_command_invocation,
    Content, BaseRule, Command, CodeAugmentedCommand
)

# Setup encoding
setup_windows_encoding()

# ... BDD-specific classes (BDDCommand, BDDWorkflow, etc.) ...

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

def handle_workflow(args):
    """Handle workflow command"""
    if len(args) < 1:
        print("Error: file_path required for workflow command")
        sys.exit(1)
    
    file_path = args[0]
    scope = args[1] if len(args) > 1 else "describe"
    phase = args[2] if len(args) > 2 else None
    # ... rest of workflow logic

def handle_validate(args):
    """Handle validate command"""
    if len(args) < 1:
        print("Usage: python bdd-runner.py validate <test-file-path> [options]")
        sys.exit(1)
    
    file_path = args[0]
    # ... rest of validate logic

def handle_run(args):
    """Handle run command"""
    if len(args) < 1:
        print("Usage: python bdd-runner.py run [test-file] [framework]")
        sys.exit(1)
    
    test_file = args[0]
    framework = args[1] if len(args) > 1 else None
    # ... rest of run logic

def handle_validate_scaffold(args):
    """Handle validate-scaffold command"""
    if len(args) < 1:
        print("Usage: python bdd-runner.py validate-scaffold <scaffold-file-path>")
        sys.exit(1)
    
    scaffold_file = args[0]
    # ... rest of validate-scaffold logic

def handle_correct_scaffold(args):
    """Handle correct-scaffold command"""
    if len(args) < 1:
        print("Usage: python bdd-runner.py correct-scaffold <scaffold-file-path> [chat-context]")
        sys.exit(1)
    
    scaffold_file = args[0]
    chat_context = args[1] if len(args) > 1 else "User requested scaffold correction"
    # ... rest of correct-scaffold logic

# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    registry = CommandRegistry("bdd-runner.py")
    
    # Register commands
    registry.register(
        "workflow",
        handle_workflow,
        "workflow <file_path> [scope] [phase] [cursor_line] [--auto]",
        guard="bdd-workflow"
    )
    
    registry.register(
        "validate",
        handle_validate,
        "validate <file_path> [--thorough] [--phase=<phase>]",
        guard="bdd-validate"
    )
    
    registry.register(
        "validate-scaffold",
        handle_validate_scaffold,
        "validate-scaffold <test_file_path>",
        guard="bdd-scaffold-validate"
    )
    
    registry.register(
        "correct-scaffold",
        handle_correct_scaffold,
        "correct-scaffold <scaffold-file-path> [chat-context]",
        guard="bdd-scaffold-correct"
    )
    
    registry.register(
        "run",
        handle_run,
        "run [test-file] [framework]",
        guard="bdd-run"
    )
    
    # Dispatch command
    registry.dispatch(sys.argv)
```

**Result:** ~80-100 lines (down from 259)

### 2.2 DDD Runner Example

```python
"""DDD Runner - Simplified with CommandRegistry"""

from pathlib import Path
import sys
from common_command_runner import (
    setup_windows_encoding, CommandRegistry,
    Content, BaseRule, Command, CodeAugmentedCommand
)

setup_windows_encoding()

# ... DDD-specific classes ...

def handle_structure(args):
    """Handle structure analysis"""
    action = args[0] if args else "execute"
    file_path = args[1] if len(args) > 1 else None
    # ... logic

def handle_interaction(args):
    """Handle interaction analysis"""
    action = args[0] if args else "execute"
    file_path = args[1] if len(args) > 1 else None
    # ... logic

if __name__ == "__main__":
    registry = CommandRegistry("ddd_runner.py")
    
    registry.register(
        "structure",
        handle_structure,
        "structure <action> <file-path>",
        guard="ddd-structure"
    )
    
    registry.register(
        "interaction",
        handle_interaction,
        "interaction <action> <file-path>",
        guard="ddd-interaction"
    )
    
    registry.dispatch(sys.argv)
```

**Result:** ~40-50 lines (down from 70)

---

## Phase 3: Benefits Summary

### Code Reduction
- **BDD:** 259 → 100 lines (61% reduction)
- **DDD:** 70 → 50 lines (29% reduction)
- **Code-Agent:** 200+ → 80 lines (60% reduction)
- **Stories:** Minimal → Clean structure
- **Clean-Code:** Empty → Clean foundation

### Quality Improvements
1. **Consistency:** All runners follow same pattern
2. **Maintainability:** Fix once in common code, applies everywhere
3. **Readability:** Clear command registration vs. if/elif chains
4. **Extensibility:** Add new commands with one `register()` call
5. **Testing:** CommandRegistry can be unit tested
6. **Documentation:** Auto-generated usage messages

### Developer Experience
1. **Faster development:** Copy pattern, register commands
2. **Less boilerplate:** No more copy-pasting CLI setup
3. **Fewer bugs:** Centralized error handling
4. **Better onboarding:** New developers see clear pattern

---

## Implementation Steps

1. **Step 1:** Add `setup_windows_encoding()`, `require_command_invocation()`, `CommandRegistry` to `common_command_runner.py`

2. **Step 2:** Refactor BDD runner (most complex, good test case)
   - Move handler logic into functions
   - Register all commands
   - Test thoroughly

3. **Step 3:** Refactor DDD runner (simpler, verify pattern works)

4. **Step 4:** Refactor Code-Agent runner

5. **Step 5:** Complete Stories runner

6. **Step 6:** Implement Clean-Code runner

7. **Step 7:** Update documentation

---

## Testing Strategy

1. **Unit Tests:** Test CommandRegistry directly
   - Test registration
   - Test dispatching
   - Test error handling
   - Test guard checks

2. **Integration Tests:** Test each runner
   - Run each command with --no-guard
   - Verify output matches expected
   - Verify error messages

3. **Manual Testing:** Cursor command integration
   - Test each /command invokes runner correctly
   - Verify guard checks work
   - Verify error messages are helpful

---

## Risks & Mitigation

### Risk 1: Breaking existing CLI callers
**Mitigation:** Maintain backward compatibility during transition. Both patterns can coexist.

### Risk 2: Command-specific logic is complex
**Mitigation:** Keep handler functions as flexible containers. Complex logic stays in command classes.

### Risk 3: Different runners need different patterns
**Mitigation:** CommandRegistry is flexible. Special cases can be handled in individual handlers.

---

## Future Enhancements

1. **Sub-commands:** `registry.register_subcommand("bdd", "run", ...)`
2. **Auto-help:** `--help` flag auto-generates from registry
3. **Validation:** Validate args match usage string
4. **Async support:** For long-running commands
5. **Progress bars:** Standard progress reporting
6. **Configuration:** Load command config from JSON

---

## Decision Log

**Decision:** Use function-based handlers instead of class-based
**Rationale:** Simpler, more flexible, easier to test

**Decision:** Keep command logic in BDD classes, not handlers
**Rationale:** Separation of concerns - handlers are thin wrappers

**Decision:** Make guards optional
**Rationale:** Some commands (testing, internal) don't need guards

---

## Current Run Command Architecture

### How `/bdd-code-run` Works (Verified Working):

1. **Delegate Command:** `/bdd-code-run` (`.cursor/commands/bdd-code-run-cmd.md`)
   - Simple delegate: "Execute the run action in `/bdd-code`"
   - No direct runner invocation

2. **Main Phase Command:** `/bdd-code` (`.cursor/commands/bdd-code-cmd.md`)
   - Has **ACTION 6: RUN** (lines 103-127)
   - Specifies runner CLI: `python behaviors/bdd/bdd-runner.py run [test-file] [framework]`

3. **Runner Handler:** `bdd-runner.py` command dispatcher
   - Has `elif command == "run":` handler (line 2572)
   - Calls `BDDWorkflow.run_tests()` static method
   - Returns test results

4. **BDDCommand Class:** Has `run()` method (line 846)
   - Provides command-level run support
   - Can be called directly by command instances

**This architecture is correct and working.** The refactoring should preserve this flow while simplifying the CLI dispatcher code.

---

## References

- Current runners:
  - `behaviors/bdd/bdd-runner.py` (lines 2376-2634)
  - `behaviors/ddd/ddd_runner.py`
  - `behaviors/code-agent/code_agent_runner.py`
  - `behaviors/stories/stories_runner.py`
  - `behaviors/clean-code/clean-code_runner.py`

- Common code:
  - `behaviors/common_command_runner/common_command_runner.py`

- Run command files:
  - `behaviors/bdd/run/bdd-run-cmd.md` - Generic run command
  - `behaviors/bdd/code/bdd-code-run-cmd.md` - Code phase run delegate
  - `behaviors/bdd/test/bdd-test-run-cmd.md` - Test phase run delegate
  - `behaviors/bdd/signature/bdd-signature-run-cmd.md` - Signature phase run delegate

