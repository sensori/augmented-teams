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
from agile_bot.bots.base_bot.src.bot.bot import Bot, BotResult
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env


def create_bot_config_file(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(
        json.dumps({'name': bot_name, 'behaviors': behaviors}),
        encoding='utf-8'
    )
    return config_file


def create_base_instructions(bot_directory: Path):
    """Helper: Create base instructions for all actions in bot_directory."""
    base_actions_dir = bot_directory / 'base_actions'
    
    actions = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
    for action in actions:
        action_dir = base_actions_dir / f'{actions.index(action) + 2}_{action}'
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(
            json.dumps({'actionName': action, 'instructions': [f'Instruction for {action}']}),
            encoding='utf-8'
        )
        # Create action_config.json for workflow
        config_file = action_dir / 'action_config.json'
        order = actions.index(action) + 2
        next_action = actions[order - 1] if order < len(actions) + 1 else None
        config_file.write_text(
            json.dumps({
                'name': action,
                'workflow': True,
                'order': order,
                'next_action': next_action
            }),
            encoding='utf-8'
        )


class TestBotExecuteBehavior:
    """Tests for Bot.execute_behavior() - Production code path."""

    def test_execute_behavior_with_action_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior with action parameter
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: Bot.execute_behavior('shape', action='gather_context') is called
        THEN: Action executes and returns BotResult
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create base actions structure in bot_directory (no fallback)
        create_base_instructions(bot_directory)
        
        # Create bot config
        bot_name = 'test_bot'
        bot_config = create_bot_config_file(bot_directory, bot_name, ['shape'])
        
        # Create behavior folder
        behavior_dir = bot_directory / 'behaviors' / 'shape'
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow state
        workflow_file = workspace_directory / 'workflow_state.json'
        workflow_file.write_text(json.dumps({
            'current_behavior': f'{bot_name}.shape',
            'current_action': f'{bot_name}.shape.gather_context',
            'completed_actions': []
        }), encoding='utf-8')
        
        # Create bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=bot_config)
        
        # When: Execute behavior with action
        result = bot.execute_behavior('shape', action='gather_context')
        
        # Then: Returns BotResult with correct status
        assert isinstance(result, BotResult)
        assert result.status == 'completed'
        assert result.behavior == 'shape'
        assert result.action == 'gather_context'

    def test_execute_behavior_without_action_forwards_to_current(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior without action parameter forwards to current action
        GIVEN: Bot has behavior 'shape' and workflow state shows current_action='decide_planning_criteria'
        WHEN: Bot.execute_behavior('shape') is called (no action parameter)
        THEN: Forwards to current action (decide_planning_criteria)
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create base actions structure in bot_directory (no fallback)
        create_base_instructions(bot_directory)
        
        # Create bot config
        bot_name = 'test_bot'
        bot_config = create_bot_config_file(bot_directory, bot_name, ['shape'])
        
        # Create behavior folder
        behavior_dir = bot_directory / 'behaviors' / 'shape'
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow state with current_action
        workflow_file = workspace_directory / 'workflow_state.json'
        workflow_file.write_text(json.dumps({
            'current_behavior': f'{bot_name}.shape',
            'current_action': f'{bot_name}.shape.decide_planning_criteria',
            'completed_actions': [
                {'action_state': f'{bot_name}.shape.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'}
            ]
        }), encoding='utf-8')
        
        # Create bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=bot_config)
        
        # When: Execute behavior without action parameter
        result = bot.execute_behavior('shape')
        
        # Then: Forwards to current action
        assert isinstance(result, BotResult)
        assert result.action == 'decide_planning_criteria'

    def test_execute_behavior_requires_confirmation_when_out_of_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior requires confirmation when out of order
        GIVEN: Current behavior is 'discovery', requested behavior is 'shape' (going backwards)
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation'
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create base actions structure in bot_directory (no fallback)
        create_base_instructions(bot_directory)
        
        # Create bot config with multiple behaviors (need 3+ to test going backwards)
        bot_name = 'test_bot'
        bot_config = create_bot_config_file(bot_directory, bot_name, ['shape', 'prioritization', 'discovery'])
        
        # Create behavior folders
        for behavior in ['shape', 'prioritization', 'discovery']:
            behavior_dir = bot_directory / 'behaviors' / behavior
            behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow state showing current behavior is 'prioritization' (middle of sequence)
        # Shape is before prioritization, so going back to shape should require confirmation
        workflow_file = workspace_directory / 'workflow_state.json'
        workflow_file.write_text(json.dumps({
            'current_behavior': f'{bot_name}.prioritization',
            'current_action': f'{bot_name}.prioritization.gather_context',
            'completed_actions': [
                {'action_state': f'{bot_name}.shape.validate_rules', 'timestamp': '2025-12-04T15:45:00.000000'}
            ]
        }), encoding='utf-8')
        
        # Create bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=bot_config)
        
        # When: Execute behavior out of order (shape when prioritization is current - going backwards)
        result = bot.execute_behavior('shape')
        
        # Then: Returns confirmation requirement
        assert isinstance(result, BotResult)
        assert result.status == 'requires_confirmation'
        assert 'confirmation_tool' in result.data
        assert result.data['confirmation_tool'] == 'confirm_out_of_order'

    def test_execute_behavior_handles_entry_workflow_when_no_state(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior handles entry workflow when no workflow state exists
        GIVEN: No workflow_state.json exists
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation' for entry workflow
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create base actions structure in bot_directory (no fallback)
        create_base_instructions(bot_directory)
        
        # Create bot config
        bot_name = 'test_bot'
        bot_config = create_bot_config_file(bot_directory, bot_name, ['shape'])
        
        # Create behavior folder
        behavior_dir = bot_directory / 'behaviors' / 'shape'
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify no workflow state exists
        workflow_file = workspace_directory / 'workflow_state.json'
        assert not workflow_file.exists()
        
        # Create bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=bot_config)
        
        # When: Execute behavior without workflow state
        result = bot.execute_behavior('shape')
        
        # Then: Returns entry workflow requirement
        assert isinstance(result, BotResult)
        assert result.status == 'requires_confirmation'
        assert 'behaviors' in result.data
        assert 'shape' in result.data['behaviors']

    def test_execute_behavior_returns_error_for_invalid_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior returns error for invalid action
        GIVEN: Bot has behavior 'prioritization' with valid actions: gather_context, decide_planning_criteria, etc.
        WHEN: Bot.execute_behavior('prioritization', action='start') is called with invalid action 'start'
        THEN: Returns BotResult with status 'error' and message listing valid actions
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create base actions structure in bot_directory (no fallback)
        create_base_instructions(bot_directory)
        
        # Create bot config
        bot_name = 'test_bot'
        bot_config = create_bot_config_file(bot_directory, bot_name, ['prioritization'])
        
        # Create behavior folder
        behavior_dir = bot_directory / 'behaviors' / 'prioritization'
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow state
        workflow_file = workspace_directory / 'workflow_state.json'
        workflow_file.write_text(json.dumps({
            'current_behavior': f'{bot_name}.prioritization',
            'current_action': f'{bot_name}.prioritization.gather_context',
            'completed_actions': []
        }), encoding='utf-8')
        
        # Create bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=bot_config)
        
        # When: Execute behavior with invalid action
        result = bot.execute_behavior('prioritization', action='start')
        
        # Then: Returns error with valid actions listed
        assert isinstance(result, BotResult)
        assert result.status == 'error'
        assert result.behavior == 'prioritization'
        assert result.action == 'start'
        assert 'message' in result.data
        assert 'INVALID ACTION' in result.data['message']
        assert 'start' in result.data['message']
        assert 'gather_context' in result.data['message']  # Should list valid actions
        assert 'valid_actions' in result.data
        assert 'gather_context' in result.data['valid_actions']
        assert f'{bot_name}_prioritization_gather_context' in result.data['message']  # Should suggest correct format

