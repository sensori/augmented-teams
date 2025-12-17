from pathlib import Path
import os


def get_python_workspace_root() -> Path:
    # workspace.py is at: agile_bot/bots/base_bot/src/bot/workspace.py
    # Need to go up 6 levels to reach workspace root (C:\dev\augmented-teams)
    return Path(__file__).parent.parent.parent.parent.parent.parent


def get_bot_directory() -> Path:
    bot_dir = os.environ.get('BOT_DIRECTORY')
    if not bot_dir:
        raise RuntimeError(
            "BOT_DIRECTORY environment variable is not set. "
            "Entry points must bootstrap this before importing other modules."
        )
    return Path(bot_dir)


def get_workspace_directory() -> Path:
    workspace = os.environ.get('WORKING_AREA') or os.environ.get('WORKING_DIR')
    if not workspace:
        raise RuntimeError(
            "WORKING_AREA environment variable is not set. "
            "Entry points must bootstrap this before importing other modules."
        )
    return Path(workspace)


def get_base_actions_directory(bot_directory: Path = None) -> Path:
    if bot_directory:
        bot_base_actions_dir = Path(bot_directory) / 'base_actions'
        if bot_base_actions_dir.exists():
            return bot_base_actions_dir
        # For test scenarios, fall back to test_base_bot/base_actions
        # This handles both base_bot and other bots (like story_bot) in test environments
        repo_root = get_python_workspace_root()
        test_base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'test_base_bot' / 'base_actions'
        if test_base_actions_dir.exists():
            return test_base_actions_dir
    
    repo_root = get_python_workspace_root()
    base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    if not base_actions_dir.exists():
        raise FileNotFoundError(
            f"Base actions directory not found at {base_actions_dir}. "
            f"This indicates a configuration error - base_actions directory is required."
        )
    
    return base_actions_dir


def get_behavior_folder(bot_name: str, behavior: str) -> Path:
    bot_directory = get_bot_directory()
    return bot_directory / 'behaviors' / behavior
