"""
Complete Workflow Integration Tests

Tests for 'Complete Workflow Integration' story:
- Workflow determines action from current_action (with fallback to completed_actions)
- Guardrails load with number prefixes
- Actions save state when called directly
- Close tool marks complete and transitions
- Jumping to different behavior-action updates state correctly
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.bot import Bot
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, then_completed_actions_include, then_workflow_current_state_is
from conftest import create_bot_config_file, given_bot_name_and_behaviors_setup
from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

# Removed given_bot_config_with_behaviors - use conftest.create_bot_config_file directly

def given_behaviors_exist_with_workflow(bot_directory: Path, behaviors: list):
    """Given step: Behavior folders exist with behavior.json files."""
    for behavior in behaviors:
        create_actions_workflow_json(bot_directory, behavior)

def given_base_actions_exist_with_transitions(bot_directory: Path):
    """Given step: Base actions exist with next_action transitions."""
    from agile_bot.bots.base_bot.src.state.workspace import get_base_actions_directory
    base_actions_dir = get_base_actions_directory(bot_directory=bot_directory)
    base_actions_dir.mkdir(parents=True, exist_ok=True)
    
    actions_config = [
        ('gather_context', 2, 'decide_planning_criteria'),
        ('decide_planning_criteria', 3, 'build_knowledge'),
        ('build_knowledge', 4, 'validate_rules'),
        ('validate_rules', 5, 'render_output')
    ]
    
    for action_name, order, next_action in actions_config:
        action_dir = base_actions_dir / f'{order}_{action_name}'
        action_dir.mkdir(parents=True, exist_ok=True)
        (action_dir / 'instructions.json').write_text(json.dumps({'instructions': [f'Test {action_name}']}), encoding='utf-8')
        (action_dir / 'action_config.json').write_text(json.dumps({
            'name': action_name,
            'workflow': True,
            'order': order,
            'next_action': next_action
        }), encoding='utf-8')
    return base_actions_dir

def when_bot_is_created(bot_name: str, bot_directory: Path, config_path: Path):
    """When step: Bot is instantiated."""
    return Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)

def when_action_is_executed(bot, behavior_name: str, action_name: str):
    """When step: Action is executed."""
    behavior = getattr(bot, behavior_name)
    action_method = getattr(behavior, action_name)
    return action_method()

def when_action_is_closed_and_transitioned(bot, behavior_name: str, action_name: str):
    """When step: Action is closed and workflow transitions."""
    behavior = getattr(bot, behavior_name)
    behavior.workflow.save_completed_action(action_name)
    behavior.workflow.load_state()
    behavior.workflow.transition_to_next()

def then_workflow_state_shows_action(workflow_file: Path, bot_name: str, behavior: str, action: str):
    """Then step: Workflow state shows specified action."""
    state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert state['current_action'] == f'{bot_name}.{behavior}.{action}'

def then_workflow_state_shows_behavior(workflow_file: Path, bot_name: str, behavior: str):
    """Then step: Workflow state shows specified behavior."""
    state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert state['current_behavior'] == f'{bot_name}.{behavior}'

# Removed then_completed_actions_include - use test_helpers.then_completed_actions_include instead


def given_test_environment_setup(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list):
    """Given: Test environment setup with bot config, behaviors, and base actions."""
    bootstrap_env(bot_directory, workspace_directory)
    config_path = create_bot_config_file(bot_directory, bot_name, behaviors)
    given_behaviors_exist_with_workflow(bot_directory, behaviors)
    given_base_actions_exist_with_transitions(bot_directory)
    return config_path


def then_action_result_has_correct_action(result, expected_action: str):
    """Then: Action result has correct action."""
    assert result.action == expected_action


# Removed then_workflow_current_state_is - use test_helpers.then_workflow_current_state_is instead


def then_action_is_completed(workflow, action_name: str):
    """Then: Action is completed."""
    assert workflow.is_action_completed(action_name)


# Import shared helper from conftest
from conftest import given_bot_name_and_behaviors_setup

def given_completed_actions_for_behaviors(bot_name: str, behaviors: list, action: str):
    """Given: Completed actions for multiple behaviors."""
    return [f'{bot_name}.{behavior}.{action}' for behavior in behaviors]

def then_action_result_has_correct_behavior_and_action(result, expected_behavior: str, expected_action: str):
    """Then: Action result has correct behavior and action."""
    assert result.behavior == expected_behavior
    assert result.action == expected_action


# ============================================================================
# STORY: Complete Workflow Integration
# ============================================================================

class TestInvokeBehaviorActionsInWorkflowOrder:
    """Story: Complete Workflow Integration - End-to-end test of the complete workflow with all fixes."""

    def test_complete_workflow_end_to_end(self, bot_directory, workspace_directory, tmp_path):
        """
        Complete end-to-end workflow test demonstrating all fixes working together.

        Flow:
        1. Start at gather_context
        2. Execute gather_context
        3. Close gather_context -> Transitions to decide_planning_criteria
        4. Jump to discovery.gather_context (out of order)
        5. Verify state shows discovery.gather_context
        6. Close and verify proper transition
        """
        # Given: Environment is bootstrapped
        bot_name, behaviors = given_bot_name_and_behaviors_setup('story_bot', ['shape', 'discovery'])
        config_path = given_test_environment_setup(bot_directory, workspace_directory, bot_name, behaviors)
        
        # When: Bot is created
        bot = when_bot_is_created(bot_name, bot_directory, config_path)
        workflow_file = workspace_directory / 'workflow_state.json'
        
        # Step 1: Execute gather_context
        print("\n=== Step 1: Execute gather_context ===")
        result = when_action_is_executed(bot, 'shape', 'gather_context')
        then_action_result_has_correct_action(result, 'gather_context')
        then_workflow_current_state_is(bot.shape.workflow, 'gather_context')
        then_workflow_state_shows_action(workflow_file, bot_name, 'shape', 'gather_context')
        print("[OK] Executed gather_context, state saved")
        
        # Step 2: Close gather_context
        print("\n=== Step 2: Close gather_context ===")
        when_action_is_closed_and_transitioned(bot, 'shape', 'gather_context')
        then_workflow_current_state_is(bot.shape.workflow, 'decide_planning_criteria')
        then_action_is_completed(bot.shape.workflow, 'gather_context')
        print("[OK] gather_context closed, transitioned to decide_planning_criteria")
        
        # Step 3: Jump to discovery.gather_context (out of order)
        print("\n=== Step 3: Jump to discovery.gather_context (out of order) ===")
        result = when_action_is_executed(bot, 'discovery', 'gather_context')
        then_action_result_has_correct_behavior_and_action(result, 'discovery', 'gather_context')
        then_workflow_state_shows_behavior(workflow_file, bot_name, 'discovery')
        then_workflow_state_shows_action(workflow_file, bot_name, 'discovery', 'gather_context')
        print("[OK] Jumped to discovery.gather_context, state correctly shows discovery.gather_context")
        
        # Step 4: Close discovery.gather_context
        print("\n=== Step 4: Close discovery.gather_context ===")
        when_action_is_closed_and_transitioned(bot, 'discovery', 'gather_context')
        then_workflow_current_state_is(bot.discovery.workflow, 'decide_planning_criteria')
        print("[OK] discovery.gather_context closed, transitioned to decide_planning_criteria")
        
        # Then: Completed actions from both behaviors are tracked
        expected_completed_actions = given_completed_actions_for_behaviors('story_bot', ['shape', 'discovery'], 'gather_context')
        then_completed_actions_include(workflow_file, expected_completed_actions)
        print("[OK] All completed actions tracked across both behaviors")
        
        print("\n=== SUCCESS: Complete workflow with all fixes working! ===")
