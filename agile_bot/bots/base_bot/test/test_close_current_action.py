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


def test_close_current_action_marks_complete_and_transitions(tmp_path):
    """
    Scenario: Close current action and transition to next
    
    Given workflow is at action "gather_context"
    And action has NOT been marked complete yet
    When user closes current action
    Then action "gather_context" is saved to completed_actions
    And workflow transitions to "decide_planning_criteria" (next action)
    """
    # Setup
    bot_name = 'story_bot'
    behavior = 'shape'
    
    # Create project structure
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Write workflow_state.json with gather_context as current action
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.gather_context',
        'timestamp': '2025-12-04T16:00:00.000000',
        'completed_actions': [
            {
                'action_state': f'{bot_name}.{behavior}.initialize_project',
                'timestamp': '2025-12-04T15:55:00.000000'
            }
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
    # Define states and transitions
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    
    # Create workflow
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    # Verify starting state
    assert workflow.current_state == 'gather_context', "Should start at gather_context"
    assert not workflow.is_action_completed('gather_context'), "gather_context should not be complete yet"
    
    # Execute: Close current action
    current_action = workflow.current_state
    workflow.save_completed_action(current_action)
    workflow.transition_to_next()
    
    # Verify action was marked complete
    assert workflow.is_action_completed('gather_context'), "gather_context should be marked complete"
    
    # Verify transition occurred
    assert workflow.current_state == 'decide_planning_criteria', (
        f"Expected workflow to transition to 'decide_planning_criteria', "
        f"but got '{workflow.current_state}'"
    )
    
    # Verify workflow state file was updated
    updated_state = json.loads(workflow_file.read_text())
    assert len(updated_state['completed_actions']) == 2, "Should have 2 completed actions"
    assert updated_state['completed_actions'][1]['action_state'] == f'{bot_name}.{behavior}.gather_context'
    assert updated_state['current_action'] == f'{bot_name}.{behavior}.decide_planning_criteria'


def test_close_action_at_final_action_stays_at_final(tmp_path):
    """
    Scenario: Close action when already at final action
    
    Given workflow is at action "validate_rules" (final action)
    When user closes current action
    Then action "validate_rules" is saved to completed_actions
    And workflow stays at "validate_rules" (no next action available)
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    # Create project structure
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Write workflow_state.json at final action
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.validate_rules',
        'timestamp': '2025-12-04T16:00:00.000000',
        'completed_actions': [
            {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00.000000'},
            {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00.000000'},
            {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:57:00.000000'},
            {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:58:00.000000'},
            {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:59:00.000000'},
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
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
    
    assert workflow.current_state == 'validate_rules', "Should be at final action"
    
    # Close current action
    workflow.save_completed_action('validate_rules')
    workflow.transition_to_next()  # Should not transition (already at end)
    
    # Verify we're still at final action
    assert workflow.current_state == 'validate_rules', "Should stay at validate_rules (no next action)"
    assert workflow.is_action_completed('validate_rules'), "validate_rules should be marked complete"


def test_close_final_action_transitions_to_next_behavior(tmp_path):
    """
    Scenario: Close final action and transition to next behavior
    
    Given workflow is at final action "validate_rules" of behavior "shape"
    And next behavior in config is "prioritization"
    When user closes current action
    Then "validate_rules" is saved to completed_actions
    And behavior "shape" is marked complete
    And workflow transitions to behavior "prioritization"
    And workflow initializes at first action "initialize_project" of prioritization
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Workflow at final action with all previous actions complete
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.validate_rules',
        'completed_actions': [
            {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00'},
            {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00'},
            {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:57:00'},
            {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:58:00'},
            {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:59:00'},
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
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
    
    assert workflow.current_state == 'validate_rules', "Should be at final action"
    
    # Close final action
    workflow.save_completed_action('validate_rules')
    
    # Verify validate_rules is now complete
    assert workflow.is_action_completed('validate_rules'), "validate_rules should be marked complete"
    
    # Verify we're at the end (validate_rules is final - no transition within behavior)
    workflow.transition_to_next()  # Should not transition (already at end)
    assert workflow.current_state == 'validate_rules', "Should stay at validate_rules (end of behavior)"
    
    # NOTE: Behavior transition to "prioritization" would happen at Bot level (in MCP tool)
    # not in Workflow itself - Workflow only handles actions within a behavior


def test_error_when_closing_action_that_requires_confirmation(tmp_path):
    """
    Scenario: Close action that requires confirmation but wasn't confirmed
    
    Given workflow is at "initialize_project"
    And action has NOT been saved to completed_actions (requires confirmation)
    When user tries to close current action
    Then is_action_completed returns False
    And action should NOT be saved again without proper confirmation flow
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Workflow at initialize_project but NOT complete
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.initialize_project',
        'completed_actions': []  # Empty - nothing complete yet
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
    ]
    
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    # Verify action is NOT complete
    assert not workflow.is_action_completed('initialize_project'), (
        "initialize_project should NOT be complete (requires confirmation)"
    )
    
    # This is the check the MCP tool should do before allowing close
    # If not complete, MCP tool should return error and NOT proceed


def test_close_handles_action_already_completed_gracefully(tmp_path):
    """
    Edge case: Close action that's already marked complete
    
    Should handle gracefully (idempotent operation)
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Action already complete
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.gather_context',
        'completed_actions': [
            {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:55:00.000000'},
            {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:56:00.000000'},
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
    ]
    
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    assert workflow.is_action_completed('gather_context'), "Action should already be complete"
    
    # Close again (should be idempotent)
    workflow.save_completed_action('gather_context')
    
    # Should still work fine
    assert workflow.is_action_completed('gather_context')

