"""
Helper functions for "Execute Behavior Actions" epic tests.

This module contains helper functions specific to testing behavior action execution:
- Action activity tracking verification
- Workflow transition verification
- Workflow state management
- Action initialization

For functions used across multiple epics, see test_helpers.py.
"""
import json
from pathlib import Path
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_activity_log_file,
    get_workflow_state_path,
    read_activity_log,
    given_bot_name_and_behavior_setup
)


# ============================================================================
# ACTION TRACKING VERIFICATION HELPERS
# ============================================================================

def verify_action_tracks_start(bot_dir: Path, workspace_dir: Path, action_class, action_name: str, 
                               bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify that action tracks start in activity log."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    create_activity_log_file(workspace_dir)
    
    # Create action (no workspace_root parameter)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir
    )
    action.track_activity_on_start()
    
    log_data = read_activity_log(workspace_dir)
    assert any(
        e['action_state'] == f'{bot_name}.{behavior}.{action_name}'
        for e in log_data
    )


def verify_action_tracks_completion(bot_dir: Path, workspace_dir: Path, action_class, action_name: str, 
                                   bot_name: str = 'story_bot', behavior: str = 'exploration', 
                                   outputs: dict = None, duration: int = None):
    """Helper: Verify that action tracks completion in activity log."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    create_activity_log_file(workspace_dir)
    
    # Create action (no workspace_root parameter)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir
    )
    action.track_activity_on_completion(
        outputs=outputs or {},
        duration=duration
    )
    
    log_data = read_activity_log(workspace_dir)
    completion_entry = next((e for e in log_data if 'outputs' in e or 'duration' in e), None)
    assert completion_entry is not None
    if outputs:
        assert completion_entry.get('outputs') == outputs
    if duration:
        assert completion_entry.get('duration') == duration


# ============================================================================
# WORKFLOW VERIFICATION HELPERS
# ============================================================================

def verify_workflow_transition(bot_dir: Path, workspace_dir: Path, source_action: str, dest_action: str, 
                              bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow transitions from source to dest action."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    states = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
    # Create all transitions, not just the one we're testing
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    # No workspace_root parameter
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=states,
        transitions=transitions
    )
    # Set state and save it so load_state() doesn't reset it
    workflow.machine.set_state(source_action)
    workflow.save_state()
    # Mark action as completed
    workflow.save_completed_action(source_action)
    # Now transition
    workflow.transition_to_next()
    assert workflow.state == dest_action


def verify_workflow_saves_completed_action(bot_dir: Path, workspace_dir: Path, action_name: str, 
                                          bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow saves completed action to state file."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    # No workspace_root parameter
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output'],
        transitions=[]
    )
    workflow.save_completed_action(action_name)
    
    # Workflow state is in workspace directory
    state_file = get_workflow_state_path(workspace_dir)
    state_data = json.loads(state_file.read_text(encoding='utf-8'))
    assert any(
        action_name in entry.get('action_state', '')
        for entry in state_data.get('completed_actions', [])
    )


# ============================================================================
# WORKFLOW ASSERTION HELPERS - Used across Execute Behavior Actions epic
# ============================================================================

def then_workflow_current_state_is(workflow, expected_state: str):
    """Then: Workflow current state is expected."""
    assert workflow.current_state == expected_state or workflow.state == expected_state


def then_completed_actions_include(workflow_file: Path, expected_action_states: list):
    """Then: Completed actions include expected action states."""
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    completed_states = [entry.get('action_state') for entry in state_data.get('completed_actions', [])]
    for expected_state in expected_action_states:
        assert expected_state in completed_states, f"Expected {expected_state} in completed_actions"


# ============================================================================
# ACTION INITIALIZATION HELPERS
# ============================================================================

def _create_validate_rules_action(bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create ValidateRulesAction instance."""
    from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
    return ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )


def _create_gather_context_action(bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create GatherContextAction instance."""
    from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
    return GatherContextAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )


def _create_action_with_provided_class(action_class, bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create action instance with provided class."""
    if action_class.__name__ == 'ValidateRulesAction':
        behavior = behavior or 'exploration'
        return _create_validate_rules_action(bot_name, behavior, bot_directory)
    else:
        behavior = behavior or 'shape'
        action_obj = action_class(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        return bot_name, behavior, action_obj


def _create_action_with_default_class(bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create action instance with default class detection."""
    if behavior == 'exploration':
        return _create_validate_rules_action(bot_name, behavior, bot_directory)
    else:
        if bot_name == 'story_bot' and behavior is None:
            bot_name, behavior = given_bot_name_and_behavior_setup()
        else:
            behavior = behavior or 'shape'
        action_obj = _create_gather_context_action(bot_name, behavior, bot_directory)
        return bot_name, behavior, action_obj


def given_environment_bootstrapped_and_action_initialized(bot_directory: Path, workspace_directory: Path, 
                                                          bot_name: str = None, behavior: str = None, 
                                                          action_class=None):
    """Given: Environment bootstrapped and action initialized."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name = bot_name or 'story_bot'
    
    if action_class:
        return _create_action_with_provided_class(action_class, bot_name, behavior, bot_directory)
    else:
        return _create_action_with_default_class(bot_name, behavior, bot_directory)
