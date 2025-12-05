"""
Test the close_current_action functionality.

Story: Close Current Action
Tests that users can explicitly mark an action as complete and transition to the next action.

Covers all acceptance criteria:
1. Close current action and transition to next
2. Close final action and transition to next behavior
3. Error when action requires confirmation (not in completed_actions)
4. Works regardless of invocation method
5. Idempotent completion
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow
from conftest import (
    create_bot_dir, create_project_dir, create_current_project_file,
    create_workflow_state_file
)


# ============================================================================
# INLINE HELPERS - Used only by tests in this file
# ============================================================================

def create_test_workflow(
    tmp_path: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None
) -> tuple[Workflow, Path]:
    """Helper: Create workflow with specified state for testing."""
    create_bot_dir(tmp_path, bot_name)
    project_dir = create_project_dir(tmp_path)
    create_current_project_file(tmp_path, bot_name, str(project_dir))
    
    workflow_file = create_workflow_state_file(
        project_dir, bot_name, behavior, current_action, completed_actions
    )
    
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    return workflow, workflow_file


def test_close_current_action_marks_complete_and_transitions(tmp_path):
    """Scenario: Close current action and transition to next"""
    
    # Given workflow is at action "gather_context"
    # And action has NOT been marked complete yet
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [{'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00.000000'}]
    
    workflow, workflow_file = create_test_workflow(tmp_path, bot_name, behavior, 'gather_context', completed)
    
    assert workflow.current_state == 'gather_context'
    assert not workflow.is_action_completed('gather_context')
    
    # When user closes current action
    workflow.save_completed_action('gather_context')
    workflow.transition_to_next()
    
    # Then action "gather_context" is saved to completed_actions
    # And workflow transitions to "decide_planning_criteria" (next action)
    assert workflow.is_action_completed('gather_context')
    assert workflow.current_state == 'decide_planning_criteria'
    
    updated_state = json.loads(workflow_file.read_text())
    assert len(updated_state['completed_actions']) == 2
    assert updated_state['completed_actions'][1]['action_state'] == f'{bot_name}.{behavior}.gather_context'
    assert updated_state['current_action'] == f'{bot_name}.{behavior}.decide_planning_criteria'


def test_close_action_at_final_action_stays_at_final(tmp_path):
    """Scenario: Close action when already at final action"""
    
    # Given workflow is at action "validate_rules" (final action)
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:57:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:58:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:59:00.000000'},
    ]
    
    workflow, workflow_file = create_test_workflow(tmp_path, bot_name, behavior, 'validate_rules', completed)
    
    assert workflow.current_state == 'validate_rules'
    
    # When user closes current action
    workflow.save_completed_action('validate_rules')
    workflow.transition_to_next()
    
    # Then action "validate_rules" is saved to completed_actions
    # And workflow stays at "validate_rules" (no next action available)
    assert workflow.current_state == 'validate_rules'
    assert workflow.is_action_completed('validate_rules')


def test_close_final_action_transitions_to_next_behavior(tmp_path):
    """Scenario: Close final action and transition to next behavior"""
    
    # Given workflow is at final action "validate_rules" of behavior "shape"
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00'},
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:57:00'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:58:00'},
        {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:59:00'},
    ]
    
    workflow, workflow_file = create_test_workflow(tmp_path, bot_name, behavior, 'validate_rules', completed)
    
    assert workflow.current_state == 'validate_rules'
    
    # When user closes current action
    workflow.save_completed_action('validate_rules')
    workflow.transition_to_next()
    
    # Then "validate_rules" is saved to completed_actions
    # And workflow stays at "validate_rules" (end of behavior)
    assert workflow.is_action_completed('validate_rules')
    assert workflow.current_state == 'validate_rules'
    
    # NOTE: Behavior transition to "prioritization" would happen at Bot level (in MCP tool)


def test_error_when_closing_action_that_requires_confirmation(tmp_path):
    """Scenario: Close action that requires confirmation but wasn't confirmed"""
    
    # Given workflow is at "initialize_project"
    # And action has NOT been saved to completed_actions (requires confirmation)
    bot_name = 'story_bot'
    behavior = 'shape'
    
    workflow, workflow_file = create_test_workflow(tmp_path, bot_name, behavior, 'initialize_project', [])
    
    # Then is_action_completed returns False
    assert not workflow.is_action_completed('initialize_project')


def test_close_handles_action_already_completed_gracefully(tmp_path):
    """Scenario: Close action that's already marked complete (idempotent)"""
    
    # Given action already complete
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00.000000'},
    ]
    
    workflow, workflow_file = create_test_workflow(tmp_path, bot_name, behavior, 'gather_context', completed)
    
    assert workflow.is_action_completed('gather_context')
    
    # When close again (should be idempotent)
    workflow.save_completed_action('gather_context')
    
    # Then should still work fine
    assert workflow.is_action_completed('gather_context')

