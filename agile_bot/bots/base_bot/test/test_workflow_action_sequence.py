"""
Test that workflow correctly determines next action based on current_action.

Workflow loads state from current_action (source of truth), with fallback to completed_actions if current_action is missing or invalid.
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
) -> Workflow:
    """Helper: Create workflow with specified state for testing."""
    create_bot_dir(tmp_path, bot_name)
    project_dir = create_project_dir(tmp_path)
    create_current_project_file(tmp_path, bot_name, str(project_dir))
    
    create_workflow_state_file(
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
    
    return Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )


def test_workflow_determines_next_action_from_current_action(tmp_path):
    """Scenario: Workflow determines next action from current_action (source of truth)"""
    
    # Given workflow_state.json shows:
    #   - current_action: build_knowledge
    #   - completed_actions: [initialize_project] (may be behind)
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [{'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:44:22.812230'}]
    
    # When workflow loads state (current_action is the source of truth)
    workflow = create_test_workflow(tmp_path, bot_name, behavior, 'build_knowledge', completed)
    
    # Then current_state should be build_knowledge (uses current_action from file)
    assert workflow.current_state == 'build_knowledge'


def test_workflow_starts_at_first_action_when_no_completed_actions(tmp_path):
    """Scenario: No completed actions yet"""
    
    # Given workflow loads state with no completed_actions
    bot_name = 'story_bot'
    behavior = 'shape'
    
    workflow = create_test_workflow(tmp_path, bot_name, behavior, 'initialize_project', [])
    
    # Then current_state should be the first action (initialize_project)
    assert workflow.current_state == 'initialize_project'


def test_workflow_uses_current_action_when_provided(tmp_path):
    """Scenario: Workflow uses current_action when provided"""
    
    # Given current_action: decide_planning_criteria
    # And completed_actions: [initialize_project, gather_context]
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'}
    ]
    
    workflow = create_test_workflow(tmp_path, bot_name, behavior, 'decide_planning_criteria', completed)
    
    # Then current_state should be decide_planning_criteria (uses current_action from file)
    assert workflow.current_state == 'decide_planning_criteria'


def test_workflow_falls_back_to_completed_actions_when_current_action_missing(tmp_path):
    """Scenario: Workflow falls back to completed_actions when current_action is missing"""
    
    # Given workflow_state.json shows:
    #   - current_action: "" (missing or empty)
    #   - completed_actions: [initialize_project, gather_context]
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.initialize_project', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'}
    ]
    
    # Create workflow with empty current_action to test fallback
    create_bot_dir(tmp_path, bot_name)
    project_dir = create_project_dir(tmp_path)
    create_current_project_file(tmp_path, bot_name, str(project_dir))
    
    # Create workflow state with empty current_action
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': '',  # Empty - should trigger fallback
        'completed_actions': completed,
        'timestamp': '2025-12-04T15:45:00.000000'
    }), encoding='utf-8')
    
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
    
    # Then current_state should be decide_planning_criteria (next after last completed)
    assert workflow.current_state == 'decide_planning_criteria'


def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(tmp_path):
    """Scenario: No workflow_state.json file exists (fresh start)"""
    # Given current_project.json exists but workflow_state.json does NOT exist
    bot_name = 'story_bot'
    behavior = 'shape'
    
    create_bot_dir(tmp_path, bot_name)
    project_dir = create_project_dir(tmp_path)
    create_current_project_file(tmp_path, bot_name, str(project_dir))
    
    workflow_file = project_dir / 'workflow_state.json'
    assert not workflow_file.exists()
    
    # When workflow is created
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    
    workflow = Workflow(bot_name=bot_name, behavior=behavior, workspace_root=tmp_path, states=states, transitions=transitions)
    
    # Then current_state should be the FIRST action (initialize_project)
    assert workflow.current_state == 'initialize_project'


