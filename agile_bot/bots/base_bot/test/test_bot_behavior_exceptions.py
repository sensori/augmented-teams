"""
Tests for Bot exception handling - no fallbacks.

Bot should raise exceptions when:
- Behavior not found during workflow initialization
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.bot import Bot
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_base_actions_structure, given_bot_instance_created
from conftest import create_bot_config_file


def given_bot_directory_created(tmp_path, bot_name: str) -> Path:
    """Given: Bot directory created."""
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    return bot_directory


# Removed given_bot_config_with_behaviors - use conftest.create_bot_config_file instead
# Import when needed: from conftest import create_bot_config_file


def given_workspace_directory_setup(tmp_path, bot_directory: Path) -> Path:
    """Given: Workspace directory setup."""
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    return workspace_dir


def given_behavior_json_files_exist(bot_directory: Path, behaviors: list):
    """Given: Behavior.json files exist for behaviors."""
    from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
    for behavior in behaviors:
        create_actions_workflow_json(bot_directory, behavior)


# Removed given_bot_instance_created - use test_helpers.given_bot_instance_created instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import given_bot_instance_created


def when_initializing_workflow_with_invalid_behavior(bot: Bot, workspace_dir: Path, invalid_behavior: str):
    """When: Initializing workflow with invalid behavior."""
    with pytest.raises(ValueError, match=f"Behavior '{invalid_behavior}' not found") as exc_info:
        bot._initialize_workflow_state(
            working_dir=workspace_dir,
            confirmed_behavior=invalid_behavior
        )
    return exc_info


def given_behavior_folder_without_json(bot_directory: Path, behavior_name: str) -> Path:
    """Given: Behavior folder WITHOUT behavior.json."""
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir


def when_creating_behavior_instance_without_json(bot_name: str, bot_directory: Path, behavior_name: str):
    """When: Creating Behavior instance without behavior.json."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name=behavior_name,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
    return exc_info


def then_exception_mentions_behavior_json_required(exc_info, behavior_name: str):
    """Then: Exception mentions behavior.json is REQUIRED."""
    assert 'behavior.json is REQUIRED' in str(exc_info.value)
    assert behavior_name in str(exc_info.value)


def test_bot_raises_exception_when_behavior_not_found(tmp_path):
    """Bot should raise ValueError when behavior not found during workflow initialization."""
    bot_name = 'test_bot'
    bot_directory = given_bot_directory_created(tmp_path, bot_name)
    config_file = create_bot_config_file(bot_directory, bot_name, ['shape', 'discovery'])
    workspace_dir = given_workspace_directory_setup(tmp_path, bot_directory)
    create_base_actions_structure(bot_directory)
    given_behavior_json_files_exist(bot_directory, ['shape', 'discovery'])
    bot = given_bot_instance_created(bot_name, bot_directory, config_file)
    
    when_initializing_workflow_with_invalid_behavior(bot, workspace_dir, 'invalid_behavior')


def test_behavior_raises_exception_when_actions_workflow_missing(tmp_path):
    """Behavior should raise FileNotFoundError when behavior.json is missing."""
    bot_name = 'test_bot'
    bot_directory = given_bot_directory_created(tmp_path, bot_name)
    given_behavior_folder_without_json(bot_directory, 'shape')
    given_workspace_directory_setup(tmp_path, bot_directory)
    
    exc_info = when_creating_behavior_instance_without_json(bot_name, bot_directory, 'shape')
    then_exception_mentions_behavior_json_required(exc_info, 'shape')


