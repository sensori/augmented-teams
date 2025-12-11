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
    
    # Create base_actions structure
    create_base_actions_structure(bot_directory)
    
    # Create bot instance
    bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_file)
    
    # Set up workspace
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    
    # When initializing workflow with invalid behavior
    with pytest.raises(ValueError, match="Behavior 'invalid_behavior' not found"):
        bot.initialize_workflow_state(
            confirmed_behavior='invalid_behavior',
            working_dir=workspace_dir
        )

