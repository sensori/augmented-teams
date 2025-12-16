"""Entry point wrapper for TriggerRouter for external callers (e.g., VS Code extension)."""

import json
import sys
from pathlib import Path

# Ensure workspace root is on sys.path (similar to bot CLIs)
_here = Path(__file__).resolve()
_workspace_root = None
for anc in _here.parents:
    if anc.name == "agile_bot":
        _workspace_root = anc.parent
        break
if _workspace_root and str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

from agile_bot.bots.base_bot.src.cli.trigger_router import TriggerRouter
from agile_bot.bots.base_bot.src.bot.workspace import get_bot_directory, get_workspace_directory


def main() -> None:
    """Resolve a trigger message to a routing decision and print JSON to stdout."""
    message = sys.argv[1] if len(sys.argv) > 1 else ""
    current_behavior = sys.argv[2] if len(sys.argv) > 2 else None
    current_action = sys.argv[3] if len(sys.argv) > 3 else None

    # Get bot directory and workspace directory (router will use BotPaths internally)
    try:
        bot_directory = get_bot_directory()
        workspace_directory = get_workspace_directory()
    except RuntimeError:
        # Fallback: infer from workspace root
        if _workspace_root:
            bot_directory = _workspace_root / 'agile_bot' / 'bots' / 'story_bot'
            workspace_directory = _workspace_root / 'workspace'
        else:
            bot_directory = Path.cwd()
            workspace_directory = Path.cwd() / 'workspace'
    
    router = TriggerRouter(bot_directory=bot_directory, workspace_path=workspace_directory)
    route = router.match_trigger(
        message=message.lower(),
        current_behavior=current_behavior,
        current_action=current_action,
    )
    print(json.dumps(route or {}))


if __name__ == "__main__":
    main()


