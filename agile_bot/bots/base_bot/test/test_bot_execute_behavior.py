"""
Tests for Bot.execute_behavior() method - Production code path tests.

Tests the main entry point for behavior execution that handles:
- Workflow state initialization (entry workflow)
- Behavior order checking and confirmations
- Action order checking
- Routing to behaviors
"""
import pytest
import json
from pathlib import Path
from conftest import create_bot_config_file
from agile_bot.bots.base_bot.src.bot.bot import Bot, BotResult
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_base_instructions, given_bot_name_and_behavior_setup, given_bot_instance_created
from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json


# Removed create_actions_workflow_json - use test_build_agile_bots_helpers.create_actions_workflow_json instead
# Already imported at top of file
    """Helper: Create behavior.json for a behavior (REQUIRED)."""
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_config = {
        "behaviorName": behavior_name.split('_')[-1] if '_' in behavior_name and behavior_name[0].isdigit() else behavior_name,
        "description": f"Test behavior: {behavior_name}",
        "goal": f"Test goal for {behavior_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": [
            f"**BEHAVIOR WORKFLOW INSTRUCTIONS:**",
            "",
            f"Test instructions for {behavior_name}."
        ],
        "actions_workflow": {
            "actions": [
                {"name": "gather_context", "order": 1, "next_action": "decide_planning_criteria"},
                {"name": "decide_planning_criteria", "order": 2, "next_action": "build_knowledge"},
                {"name": "build_knowledge", "order": 3, "next_action": "validate_rules"},
                {"name": "validate_rules", "order": 4, "next_action": "render_output"},
                {"name": "render_output", "order": 5}
            ]
        },
        "trigger_words": {
            "description": f"Trigger words for {behavior_name}",
            "patterns": [f"test.*{behavior_name}"],
            "priority": 10
        }
    }
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    return behavior_file

# Removed create_base_instructions - use test_helpers.create_base_instructions instead


def given_test_environment_setup(bot_directory: Path, workspace_directory: Path):
    """Given: Test environment setup."""
    bootstrap_env(bot_directory, workspace_directory)
    create_base_instructions(bot_directory)  # Imported from test_helpers


def given_bot_config_created(bot_directory: Path, bot_name: str, behaviors: list) -> Path:
    """Given: Bot config created."""
    return create_bot_config_file(bot_directory, bot_name, behaviors)


def given_behavior_workflow_created(bot_directory: Path, behavior_name: str):
    """Given: Behavior workflow created."""
    create_actions_workflow_json(bot_directory, behavior_name)


def given_multiple_behavior_workflows_created(bot_directory: Path, behavior_names: list):
    """Given: Multiple behavior workflows created."""
    for behavior_name in behavior_names:
        given_behavior_workflow_created(bot_directory, behavior_name)


def given_completed_action_entry(bot_name: str, behavior: str, action: str, timestamp: str = None) -> dict:
    """Given: Completed action entry for workflow state."""
    if timestamp is None:
        timestamp = '2025-12-04T15:44:22.812230'
    return {'action_state': f'{bot_name}.{behavior}.{action}', 'timestamp': timestamp}


def given_workflow_state_created(workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed_actions: list = None):
    """Given: Workflow state created."""
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'completed_actions': completed_actions or []
    }), encoding='utf-8')
    return workflow_file


# Removed given_bot_instance_created - use test_helpers.given_bot_instance_created instead


def given_bot_setup_with_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str, action: str) -> tuple[Bot, Path]:
    """Given: Bot setup with action."""
    given_test_environment_setup(bot_directory, workspace_directory)
    bot_config = given_bot_config_created(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created(bot_directory, behavior)
    given_workflow_state_created(workspace_directory, bot_name, behavior, action)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_with_current_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str, current_action: str, completed_actions: list = None) -> tuple[Bot, Path]:
    """Given: Bot setup with current action."""
    given_test_environment_setup(bot_directory, workspace_directory)
    bot_config = given_bot_config_created(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created(bot_directory, behavior)
    given_workflow_state_created(workspace_directory, bot_name, behavior, current_action, completed_actions)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_with_multiple_behaviors(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, current_behavior: str, current_action: str, completed_actions: list = None) -> tuple[Bot, Path]:
    """Given: Bot setup with multiple behaviors."""
    given_test_environment_setup(bot_directory, workspace_directory)
    bot_config = given_bot_config_created(bot_directory, bot_name, behaviors)
    given_multiple_behavior_workflows_created(bot_directory, behaviors)
    given_workflow_state_created(workspace_directory, bot_name, current_behavior, current_action, completed_actions)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_without_workflow_state(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str) -> tuple[Bot, Path]:
    """Given: Bot setup without workflow state."""
    given_test_environment_setup(bot_directory, workspace_directory)
    bot_config = given_bot_config_created(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created(bot_directory, behavior)
    given_no_workflow_state_exists(workspace_directory)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def when_execute_behavior_called(bot: Bot, behavior: str, action: str = None) -> BotResult:
    """When: Execute behavior called."""
    if action:
        return bot.execute_behavior(behavior, action=action)
    else:
        return bot.execute_behavior(behavior)


def then_bot_result_has_correct_status(result: BotResult, expected_status: str, expected_behavior: str = None, expected_action: str = None):
    """Then: BotResult has correct status."""
    assert isinstance(result, BotResult)
    assert result.status == expected_status
    if expected_behavior:
        assert result.behavior == expected_behavior
    if expected_action:
        assert result.action == expected_action


def then_bot_result_requires_confirmation_with_tool(result: BotResult, tool_name: str):
    """Then: BotResult requires confirmation with specific tool."""
    assert isinstance(result, BotResult)
    assert result.status == 'requires_confirmation'
    assert 'confirmation_tool' in result.data
    assert result.data['confirmation_tool'] == tool_name


def then_bot_result_requires_entry_workflow_confirmation(result: BotResult, expected_behavior: str):
    """Then: BotResult requires entry workflow confirmation."""
    assert isinstance(result, BotResult)
    assert result.status == 'requires_confirmation'
    assert 'behaviors' in result.data
    assert expected_behavior in result.data['behaviors']


def given_standard_workflow_actions():
    """Given: Standard workflow actions list."""
    return ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']

def then_bot_result_has_error_with_invalid_action_message(result: BotResult, bot_name: str, behavior: str, invalid_action: str, valid_actions: list):
    """Then: BotResult has error with invalid action message."""
    assert isinstance(result, BotResult)
    assert result.status == 'error'
    assert result.behavior == behavior
    assert result.action == invalid_action
    assert 'message' in result.data
    assert 'INVALID ACTION' in result.data['message']
    assert invalid_action in result.data['message']
    for valid_action in valid_actions:
        assert valid_action in result.data['message']
    assert 'valid_actions' in result.data
    for valid_action in valid_actions:
        assert valid_action in result.data['valid_actions']
        assert f'{bot_name}_{behavior}_{valid_action}' in result.data['message']


def given_no_workflow_state_exists(workspace_directory: Path):
    """Given: No workflow state exists."""
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()


class TestExecuteBehavior:
    """Tests for Bot.execute_behavior() - Production code path."""

    def test_execute_behavior_with_action_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior with action parameter
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: Bot.execute_behavior('shape', action='gather_context') is called
        THEN: Action executes and returns BotResult
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'gather_context')
        
        result = when_execute_behavior_called(bot, 'shape', 'gather_context')
        
        then_bot_result_has_correct_status(result, 'completed', 'shape', 'gather_context')

    def test_execute_behavior_without_action_forwards_to_current(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior without action parameter forwards to current action
        GIVEN: Bot has behavior 'shape' and workflow state shows current_action='decide_planning_criteria'
        WHEN: Bot.execute_behavior('shape') is called (no action parameter)
        THEN: Forwards to current action (decide_planning_criteria)
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'gather_context')
        bot, _ = given_bot_setup_with_current_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'decide_planning_criteria', [completed_action])
        
        result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_has_correct_status(result, 'completed', expected_action='decide_planning_criteria')

    def test_execute_behavior_requires_confirmation_when_out_of_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior requires confirmation when out of order
        GIVEN: Current behavior is 'discovery', requested behavior is 'shape' (going backwards)
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation'
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'validate_rules', '2025-12-04T15:45:00.000000')
        bot, _ = given_bot_setup_with_multiple_behaviors(bot_directory, workspace_directory, 'test_bot', ['shape', 'prioritization', 'discovery'], 'prioritization', 'gather_context', [completed_action])
        
        result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_requires_confirmation_with_tool(result, 'confirm_out_of_order')

    def test_execute_behavior_handles_entry_workflow_when_no_state(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior handles entry workflow when no workflow state exists
        GIVEN: No workflow_state.json exists
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation' for entry workflow
        """
        bot, _ = given_bot_setup_without_workflow_state(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape')
        
        result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_requires_entry_workflow_confirmation(result, 'shape')

    def test_execute_behavior_returns_error_for_invalid_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior returns error for invalid action
        GIVEN: Bot has behavior 'prioritization' with valid actions: gather_context, decide_planning_criteria, etc.
        WHEN: Bot.execute_behavior('prioritization', action='start') is called with invalid action 'start'
        THEN: Returns BotResult with status 'error' and message listing valid actions
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['prioritization'], 'prioritization', 'gather_context')
        
        result = when_execute_behavior_called(bot, 'prioritization', 'start')
        
        valid_actions = given_standard_workflow_actions()
        then_bot_result_has_error_with_invalid_action_message(result, 'test_bot', 'prioritization', 'start', valid_actions)

