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
from conftest import Workflow
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
    
    # Create mock behavior object
    from types import SimpleNamespace
    from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
    
    class MockBotPaths:
        def __init__(self, bot_dir, workspace_dir):
            self.bot_directory = bot_dir
            self.workspace_directory = workspace_dir
    
    behavior_folder = bot_dir / 'behaviors' / behavior
    behavior_obj = SimpleNamespace()
    behavior_obj.folder = behavior_folder
    behavior_obj.name = behavior
    behavior_obj.bot_name = bot_name
    behavior_obj.bot_paths = MockBotPaths(bot_dir, workspace_dir)
    behavior_obj.bot = None
    
    # Create activity tracker
    activity_tracker = ActivityTracker(workspace_dir, bot_name)
    
    # Create action using old signature (bot_name, behavior, action_name)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name=action_name,
        activity_tracker=activity_tracker
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
    
    # Create mock behavior object
    from types import SimpleNamespace
    from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
    
    class MockBotPaths:
        def __init__(self, bot_dir, workspace_dir):
            self.bot_directory = bot_dir
            self.workspace_directory = workspace_dir
    
    behavior_folder = bot_dir / 'behaviors' / behavior
    behavior_obj = SimpleNamespace()
    behavior_obj.folder = behavior_folder
    behavior_obj.name = behavior
    behavior_obj.bot_name = bot_name
    behavior_obj.bot_paths = MockBotPaths(bot_dir, workspace_dir)
    behavior_obj.bot = None
    
    # Create activity tracker
    activity_tracker = ActivityTracker(workspace_dir, bot_name)
    
    # Create action using old signature (bot_name, behavior, action_name)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name=action_name,
        activity_tracker=activity_tracker
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
    
    # Workflow class removed - state managed by Behaviors and Actions collections
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
    
    # Workflow class removed - state managed by Behaviors and Actions collections
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

def create_minimal_guardrails_files(bot_dir: Path, behavior_name: str, bot_name: str = 'test_bot'):
    """Create minimal guardrails files structure for tests.
    
    Creates empty guardrails files required by Guardrails class initialization.
    This helper is used by test helpers that need to create Behavior objects.
    
    Args:
        bot_dir: Bot directory path
        behavior_name: Behavior name - can be prefixed (e.g., '1_exploration') or unprefixed (e.g., 'exploration').
                      If prefixed, extracts the unprefixed name and uses Behavior.find_behavior_folder
                      to find the correct folder. This ensures files are created in the same folder
                      that Behavior will use when initialized with the unprefixed name.
        bot_name: Bot name (default: 'test_bot')
    """
    import json
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    
    # Extract unprefixed behavior name (e.g., '1_exploration' -> 'exploration')
    # This matches how Behavior is initialized (with unprefixed name)
    unprefixed_name = behavior_name
    if '_' in behavior_name and behavior_name[0].isdigit():
        # Extract name after the prefix (e.g., '1_exploration' -> 'exploration')
        unprefixed_name = behavior_name.split('_', 1)[1]
    
    # Use Behavior.find_behavior_folder to find the correct behavior folder
    # This ensures we create files in the same folder that Behavior will use
    behavior_dir = Behavior.find_behavior_folder(bot_dir, bot_name, unprefixed_name)
    
    # Required context files
    required_context_dir = behavior_dir / 'guardrails' / 'required_context'
    required_context_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = required_context_dir / 'key_questions.json'
    if not questions_file.exists():
        questions_file.write_text(json.dumps({'questions': []}), encoding='utf-8')
    
    evidence_file = required_context_dir / 'evidence.json'
    if not evidence_file.exists():
        evidence_file.write_text(json.dumps({'evidence': []}), encoding='utf-8')
    
    instructions_file = required_context_dir / 'instructions.json'
    if not instructions_file.exists():
        instructions_file.write_text(json.dumps({'instructions': []}), encoding='utf-8')
    
    # Strategy/planning guardrails files (check both 'strategy' and 'planning' folder names)
    for folder_name in ['strategy', 'planning']:
        strategy_dir = behavior_dir / 'guardrails' / folder_name
        if strategy_dir.exists() or folder_name == 'strategy':  # Create strategy if it doesn't exist, or if planning exists
            strategy_dir.mkdir(parents=True, exist_ok=True)
            
            assumptions_file = strategy_dir / 'typical_assumptions.json'
            if not assumptions_file.exists():
                assumptions_file.write_text(json.dumps({'typical_assumptions': []}), encoding='utf-8')
            
            # Check for both naming conventions
            for activity_file_name in ['recommended_activities.json', 'recommended_human_activity.json']:
                activity_file = strategy_dir / activity_file_name
                if not activity_file.exists():
                    activity_file.write_text(json.dumps({'recommended_activities': []}), encoding='utf-8')
            
            # Decision criteria folder
            decision_criteria_dir = strategy_dir / 'decision_criteria'
            decision_criteria_dir.mkdir(parents=True, exist_ok=True)
            
            # Only create one set of files
            if folder_name == 'strategy':
                break

def _create_validate_rules_action(bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create ValidateRulesAction instance."""
    from agile_bot.bots.base_bot.src.actions.validate_rules.validate_rules_action import ValidateRulesAction
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    
    # Ensure behavior.json exists
    behavior_name_with_prefix = f'1_{behavior}'
    create_actions_workflow_json(bot_directory, behavior_name_with_prefix)
    
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_directory, behavior_name_with_prefix, bot_name)
    
    # Create Behavior object
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_obj = Behavior(behavior, bot_name, bot_paths)
    
    return ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name='validate_rules'
    )


def _create_gather_context_action(bot_name: str, behavior: str, bot_directory: Path):
    """Helper: Create GatherContextAction instance."""
    from agile_bot.bots.base_bot.src.actions.gather_context.gather_context_action import GatherContextAction
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.src.bot.base_action_config import BaseActionConfig
    import json
    
    # Ensure behavior.json exists
    behavior_dir = bot_directory / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    if not behavior_file.exists():
        behavior_config = {
            "behaviorName": behavior,
            "description": f"Test behavior: {behavior}",
            "goal": f"Test goal for {behavior}",
            "inputs": "Test inputs",
            "outputs": "Test outputs",
            "instructions": {},
            "actions_workflow": {
                "actions": [
                    {'name': 'gather_context', 'order': 1}
                ]
            }
        }
        behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    # Create guardrails files if they don't exist (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_directory, behavior, bot_name)
    
    # Create proper Behavior object
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_obj = Behavior(name=behavior, bot_name=bot_name, bot_paths=bot_paths)
    base_action_config = BaseActionConfig('gather_context', bot_paths)
    
    return GatherContextAction(
        base_action_config=base_action_config,
        behavior=behavior_obj,
        activity_tracker=None
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
