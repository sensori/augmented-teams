"""
Test that workflow correctly determines next action based on completed_actions.

This test demonstrates the bug where workflow reads current_action from file
but doesn't validate it against completed_actions to determine what should be next.
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow


def test_workflow_determines_next_action_from_completed_actions(tmp_path):
    """
    SCENARIO: Workflow state file has incorrect current_action
    
    BUG DESCRIPTION:
    The workflow.load_state() method blindly trusts current_action from the file,
    but it should instead look at completed_actions and determine the NEXT 
    uncompleted action in the sequence.
    
    Given workflow_state.json shows:
      - completed_actions: [initialize_project]
      - current_action: build_knowledge (WRONG - this is 3 steps ahead!)
    
    When workflow loads state
    
    Then current_state should be gather_context (the next uncompleted action after initialize_project)
    Not build_knowledge (which is what the corrupted file says)
    
    EXPECTED LOGIC:
    1. Load completed_actions: [initialize_project]
    2. Find last completed action: initialize_project
    3. Look up what comes next: gather_context
    4. Set current_state to: gather_context
    5. IGNORE current_action from file (it may be corrupted/stale)
    """
    # Setup
    bot_name = 'story_bot'
    behavior = 'shape'
    
    # Create project structure
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    # Write current_project.json
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Write workflow_state.json with INCORRECT current_action
    # This simulates a corrupted state where current_action got out of sync
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.build_knowledge',  # WRONG! Should be gather_context
        'timestamp': '2025-12-04T15:50:13.760028',
        'completed_actions': [
            {
                'action_state': f'{bot_name}.{behavior}.initialize_project',
                'timestamp': '2025-12-04T15:44:22.812230'
            }
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
    # Define workflow states and transitions
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    
    # Execute
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    # Assert - The workflow should detect that initialize_project is complete
    # and the next action should be gather_context, NOT build_knowledge
    assert workflow.current_state == 'gather_context', (
        f"Expected current_state to be 'gather_context' (next after completed initialize_project), "
        f"but got '{workflow.current_state}'. "
        f"Workflow incorrectly trusts current_action from file instead of deriving it from completed_actions."
    )


def test_workflow_starts_at_first_action_when_no_completed_actions(tmp_path):
    """
    SCENARIO: No completed actions yet
    
    When workflow loads state with no completed_actions
    Then current_state should be the first action (initialize_project)
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
    
    # Write workflow_state.json with NO completed actions
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.initialize_project',
        'timestamp': '2025-12-04T15:50:13.760028',
        'completed_actions': []
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
    
    assert workflow.current_state == 'initialize_project'


def test_workflow_determines_action_after_multiple_completed_actions(tmp_path):
    """
    SCENARIO: Multiple actions completed
    
    Given completed_actions: [initialize_project, gather_context]
    Then current_state should be decide_planning_criteria (next uncompleted)
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.decide_planning_criteria',
        'timestamp': '2025-12-04T15:50:13.760028',
        'completed_actions': [
            {
                'action_state': f'{bot_name}.{behavior}.initialize_project',
                'timestamp': '2025-12-04T15:44:22.812230'
            },
            {
                'action_state': f'{bot_name}.{behavior}.gather_context',
                'timestamp': '2025-12-04T15:45:00.000000'
            }
        ]
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state))
    
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
    ]
    
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    assert workflow.current_state == 'decide_planning_criteria'


def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(tmp_path):
    """
    CRITICAL BUG: When NO workflow_state.json file exists at all (fresh start),
    workflow should start at FIRST action (initialize_project).
    
    SCENARIO: No workflow_state.json file exists
    
    Given:
      - current_project.json exists (project is set)
      - workflow_state.json does NOT exist (no state file at all)
    
    When: Workflow is created
    
    Then: current_state should be the FIRST action (initialize_project)
    Not some other action like gather_context
    
    This simulates a fresh start where the MCP tool is called for the first time.
    """
    bot_name = 'story_bot'
    behavior = 'shape'
    
    # Create project structure
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    
    # Write current_project.json so workflow knows where to look
    (bot_dir).mkdir(parents=True, exist_ok=True)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': str(project_dir)}))
    
    # DO NOT create workflow_state.json - simulating fresh start
    workflow_file = project_dir / 'workflow_state.json'
    assert not workflow_file.exists(), "Test setup error: workflow state file should not exist"
    
    # Define states
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    
    # Execute - create workflow when no state file exists
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=tmp_path,
        states=states,
        transitions=transitions
    )
    
    # Assert - should start at FIRST action
    assert workflow.current_state == 'initialize_project', (
        f"Expected workflow to start at 'initialize_project' (first action) when no state file exists, "
        f"but got '{workflow.current_state}'. "
        f"When starting fresh, workflow must begin at the first action in the sequence."
    )


