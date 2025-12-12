"""
Tests for Bot exception handling - no fallbacks.

Bot should raise exceptions when:
- Behavior not found during workflow initialization
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.bot import Bot
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_base_actions_structure


def test_bot_raises_exception_when_behavior_not_found(tmp_path):
    """Bot should raise ValueError when behavior not found during workflow initialization."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # Create bot config with behaviors
    config_dir = bot_directory / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({
        'name': bot_name,
        'behaviors': ['shape', 'discovery']
    }), encoding='utf-8')
    
    # Set up workspace FIRST (before creating bot)
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    
    # Create base_actions structure
    create_base_actions_structure(bot_directory)
    
    # Create behavior.json files for behaviors listed in config (REQUIRED after refactor)
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    for behavior in ['shape', 'discovery']:
        create_actions_workflow_json(bot_directory, behavior)
    
    # Create bot instance (after environment is bootstrapped)
    bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_file)
    
    # When initializing workflow with invalid behavior
    with pytest.raises(ValueError, match="Behavior 'invalid_behavior' not found"):
        bot._initialize_workflow_state(
            working_dir=workspace_dir,
            confirmed_behavior='invalid_behavior'
        )


def test_behavior_raises_exception_when_actions_workflow_missing(tmp_path):
    """Behavior should raise FileNotFoundError when behavior.json is missing."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # Create behavior folder WITHOUT behavior.json
    behavior_dir = bot_directory / 'behaviors' / 'shape'
    behavior_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up workspace
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    
    # When creating Behavior instance without behavior.json
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name='shape',
            bot_name=bot_name,
            bot_directory=bot_directory
        )
    
    assert 'behavior.json is REQUIRED' in str(exc_info.value)
    assert 'shape' in str(exc_info.value)


