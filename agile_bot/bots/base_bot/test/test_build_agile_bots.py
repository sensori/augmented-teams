"""
Helper functions for "Build Agile Bots" epic tests.

This module contains helper functions used across multiple sub-epics in the Build Agile Bots epic:
- Bot configuration setup
- Behavior configuration
- Bot directory setup

For functions specific to Generate MCP Tools sub-epic, see test_generate_mcp_tools.py (helpers merged into main file).
For functions specific to Generate CLI sub-epic, see test_generate_cli.py (helpers merged into main file).
For functions used across multiple epics, see test_helpers.py.
"""
import json
from pathlib import Path
from conftest import bootstrap_env
from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json


# ============================================================================
# BOT CONFIGURATION HELPERS
# ============================================================================

def given_bot_configured_by_config(workspace_root: Path, bot_name: str):
    """Given: Bot configured by config.
    
    
    """
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    workspace_directory = workspace_root / 'workspace'
    workspace_directory.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_dir, workspace_directory)
    return bot_dir, workspace_directory


def given_bot_config_and_directory_setup(workspace_root: Path, bot_name: str, behaviors: list):
    """Given: Bot config and directory setup.
    
    
    """
    from conftest import create_bot_config_file
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True, exist_ok=True)
    config_file = create_bot_config_file(bot_dir, bot_name, behaviors)
    return config_file, bot_dir


# ============================================================================
# BEHAVIOR CONFIGURATION HELPERS
# ============================================================================

def given_behavior_with_trigger_words(bot_dir: Path, behavior: str, patterns: list):
    """Given: Behavior with trigger words.
    
    
    """
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    import json
    # Create behavior.json if it doesn't exist
    create_actions_workflow_json(bot_dir, behavior)
    behavior_dir = bot_dir / 'behaviors' / behavior
    behavior_file = behavior_dir / 'behavior.json'
    if not behavior_file.exists():
        raise FileNotFoundError(f"behavior.json not found at {behavior_file} after create_actions_workflow_json")
    behavior_data = json.loads(behavior_file.read_text(encoding='utf-8'))
    behavior_data['trigger_words'] = {
        'description': f'Trigger words for {behavior}',
        'patterns': patterns,
        'priority': 10
    }
    behavior_file.write_text(json.dumps(behavior_data, indent=2), encoding='utf-8')
    return behavior_file
