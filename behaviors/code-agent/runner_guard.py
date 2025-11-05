"""
Runner Guard - Ensures runners are only called via Cursor slash commands

Prevents direct execution of runner scripts and guides users to use
proper Cursor slash commands which trigger full AI workflow and validation.
"""

import sys


def require_command_invocation(command_name: str):
    """
    Guard to prevent direct runner execution.
    
    Checks if runner was invoked with --from-command flag (set by Cursor commands).
    If not, displays helpful message directing user to proper slash command.
    
    Args:
        command_name: The slash command name (e.g., "code-agent-structure")
    """
    # Check if --from-command flag is present
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)

