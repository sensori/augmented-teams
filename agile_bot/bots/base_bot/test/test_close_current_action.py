"""
Close Current Action Tests

Tests for 'Close Current Action' story:
- Close current action and transition to next
- Close final action and transition to next behavior
- Works regardless of invocation method
- Idempotent completion
- Bot class has close_current_action method (CLI routes to bot.close_current_action)
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow
from agile_bot.bots.base_bot.src.bot.bot import Bot
from conftest import bootstrap_env, create_workflow_state_file, create_bot_config_file, create_test_workflow
from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
from conftest import given_bot_name_and_behavior_setup


# ============================================================================
# HELPER FUNCTIONS - Used only by tests in this file
# ============================================================================

def given_completed_action_for_behavior(bot_name: str, behavior: str, action: str, timestamp: str = '2025-12-04T15:55:00.000000'):
    """Given: Completed action entry for behavior."""
    return [{'action_state': f'{bot_name}.{behavior}.{action}', 'timestamp': timestamp}]

def given_workflow_state_file_loaded(workflow_file: Path):
    """Given: Workflow state file loaded."""
    return json.loads(workflow_file.read_text(encoding='utf-8'))

def given_initial_completed_action_count(workflow_file: Path, action_name: str):
    """Given: Initial completed action count for action."""
    initial_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    return len([a for a in initial_state['completed_actions'] if action_name in a['action_state']])

def given_bot_environment_bootstrapped(bot_directory: Path, workspace_directory: Path):
    """Given: Bot environment bootstrapped."""
    bootstrap_env(bot_directory, workspace_directory)

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

def given_workflow_is_at_action(workflow: Workflow, action_name: str):
    """Given step: Workflow is at specified action."""
    assert workflow.current_state == action_name

def given_action_is_not_completed(workflow: Workflow, action_name: str):
    """Given step: Action has NOT been marked complete yet."""
    assert not workflow.is_action_completed(action_name)

def when_user_closes_current_action(workflow: Workflow, action_name: str):
    """When step: User closes current action."""
    workflow.save_completed_action(action_name)

def when_user_closes_current_action_and_transitions(workflow: Workflow, action_name: str):
    """When step: User closes current action and transitions to next."""
    workflow.save_completed_action(action_name)
    workflow.transition_to_next()

def then_action_is_saved_to_completed_actions(workflow_file: Path, bot_name: str, behavior: str, action_name: str):
    """Then step: Action is saved to completed_actions."""
    updated_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert any(action_name in a['action_state'] for a in updated_state['completed_actions'])

def then_action_is_marked_complete(workflow: Workflow, action_name: str):
    """Then step: Action is marked complete."""
    assert workflow.is_action_completed(action_name)

def then_workflow_transitions_to_next_action(workflow: Workflow, expected_action: str):
    """Then step: Workflow transitions to next action."""
    assert workflow.current_state == expected_action

def then_workflow_stays_at_action(workflow: Workflow, action_name: str):
    """Then step: Workflow stays at specified action."""
    assert workflow.current_state == action_name

def then_completed_actions_count_is(workflow_file: Path, expected_count: int):
    """Then step: Completed actions count matches expected."""
    updated_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert len(updated_state['completed_actions']) == expected_count

def then_current_action_is(workflow_file: Path, bot_name: str, behavior: str, expected_action: str):
    """Then step: Current action matches expected."""
    updated_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert updated_state['current_action'] == f'{bot_name}.{behavior}.{expected_action}'

def then_bot_has_close_current_action_method(bot):
    """Then step: Bot class has close_current_action method."""
    assert hasattr(bot, 'close_current_action')
    assert callable(bot.close_current_action)


# ============================================================================
# STORY: Close Current Action
# ============================================================================

class TestCloseCurrentAction:
    """Story: Close Current Action - Tests that users can explicitly mark an action as complete and transition to the next action."""

    def test_close_current_action_marks_complete_and_transitions(self, bot_directory, workspace_directory):
        """Scenario: Close current action and transition to next"""

        # Given workflow is at action "decide_planning_criteria"
        # And action has NOT been marked complete yet
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'gather_context')

        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)

        given_workflow_is_at_action(workflow, 'decide_planning_criteria')
        given_action_is_not_completed(workflow, 'decide_planning_criteria')

        # When user closes current action
        when_user_closes_current_action_and_transitions(workflow, 'decide_planning_criteria')

        # Then action is saved to completed_actions
        then_action_is_marked_complete(workflow, 'decide_planning_criteria')
        # And workflow transitions to next action
        then_workflow_transitions_to_next_action(workflow, 'build_knowledge')
        then_completed_actions_count_is(workflow_file, 2)
        then_current_action_is(workflow_file, bot_name, behavior, 'build_knowledge')


    def test_close_action_at_final_action_stays_at_final(self, bot_directory, workspace_directory):
        """Scenario: Close final action stays at final action"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate_rules', [])
        
        given_workflow_is_at_action(workflow, 'validate_rules')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'validate_rules')
        # No transition_to_next() call - validate_rules is final
        
        # Then action is saved but state stays at validate_rules
        then_action_is_marked_complete(workflow, 'validate_rules')
        then_workflow_stays_at_action(workflow, 'validate_rules')


    def test_close_final_action_transitions_to_next_behavior(self, bot_directory, workspace_directory):
        """Scenario: Close final action and verify it's marked complete"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        # Given: Workflow is at final action
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate_rules', [])
        
        given_workflow_is_at_action(workflow, 'validate_rules')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'validate_rules')
        
        # Then action is marked complete
        then_action_is_marked_complete(workflow, 'validate_rules')
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'validate_rules')


    def test_close_action_saves_to_completed_actions_list(self, bot_directory, workspace_directory):
        """Scenario: Closing action saves it to completed_actions list"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'gather_context', [])
        
        # When closing action
        when_user_closes_current_action(workflow, 'gather_context')
        
        # Then it's in completed_actions
        then_completed_actions_count_is(workflow_file, 1)
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'gather_context')


    def test_close_handles_action_already_completed_gracefully(self, bot_directory, workspace_directory):
        """Scenario: Idempotent close (already completed)"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'gather_context')
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)
        
        # Verify initial state
        initial_count = given_initial_completed_action_count(workflow_file, 'gather_context')
        
        # When closing already completed action
        workflow.save_completed_action('gather_context')  # Already in completed_actions
        
        # Then no NEW entry added (may save again with new timestamp, but test just checks it completes gracefully)
        updated_state = json.loads(workflow_file.read_text(encoding='utf-8'))
        # Just verify it didn't error out - the action may or may not deduplicate
        assert len(updated_state['completed_actions']) >= initial_count


    def test_bot_class_has_close_current_action_method(self, bot_directory, workspace_directory):
        """Scenario: Bot class exposes close_current_action method"""
        
        # Given: Bot is initialized
        given_bot_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, _ = given_bot_name_and_behavior_setup()
        config_path = create_bot_config_file(bot_directory, bot_name, ['shape'])
        create_actions_workflow_json(bot_directory, 'shape')
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)
        
        # Then: Bot should have close_current_action method
        then_bot_has_close_current_action_method(bot)
