"""
Gather Context Tests

Tests for all stories in the 'Gather Context' sub-epic:
- Track Activity for Gather Context Action
- Proceed To Decide Planning
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.actions.gather_context.gather_context_action import GatherContextAction
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from conftest import create_workflow_state_file
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_activity_log_file,
    read_activity_log,
    create_guardrails_files,
    given_bot_name_and_behavior_setup,
    then_activity_logged_with_action_state,
    then_completion_entry_logged_with_outputs,
    given_environment_bootstrapped_and_activity_log_initialized,
    create_actions_workflow_json
)
from agile_bot.bots.base_bot.test.test_execute_behavior_actions import (
    verify_workflow_transition,
    verify_workflow_saves_completed_action,
    given_environment_bootstrapped_and_action_initialized,
    then_workflow_current_state_is
)

def verify_activity_logged(log_file: Path, action_state: str):
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        entries = db.all()
        assert any(entry['action_state'] == action_state for entry in entries)

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

def given_action_outputs_with_counts(questions_count: int = 5, evidence_count: int = 3):
    """Given: Action outputs with counts."""
    return {'questions_count': questions_count, 'evidence_count': evidence_count}

def given_action_duration(duration: int = 330):
    """Given: Action duration."""
    return duration

def given_activity_log_entries_for_behaviors(bot_name: str = 'story_bot', behaviors: list = None):
    """Given: Activity log entries for multiple behaviors."""
    if behaviors is None:
        behaviors = ['shape', 'discovery']
    entries = []
    for i, behavior in enumerate(behaviors):
        entries.append({
            'action_state': f'{bot_name}.{behavior}.gather_context',
            'timestamp': f'{9 + i}:00'
        })
    return entries

def given_expected_activity_log_entries_for_behaviors(bot_name: str = 'story_bot', behaviors: list = None):
    """Given: Expected activity log entries for multiple behaviors."""
    if behaviors is None:
        behaviors = ['shape', 'discovery']
    return [
        {'action_state': f'{bot_name}.{behavior}.gather_context'}
        for behavior in behaviors
    ]

def given_questions_and_evidence_for_guardrails():
    """Given: Questions and evidence for guardrails."""
    questions = ['What is the scope?', 'Who are the users?']
    evidence = ['Requirements doc', 'User interviews']
    return questions, evidence

def given_json_decode_error_expected_message():
    """Given: JSON decode error expected message."""
    return ['key_questions.json', 'Expecting']

def given_workflow_states_and_transitions():
    """Given: Standard workflow states and transitions."""
    states = ['gather_context', 'decide_planning_criteria', 'build_knowledge']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
    ]
    return states, transitions

def given_workflow_state_file_with_completed_action(workspace_directory: Path, bot_name: str, behavior: str, action: str, completed_actions: list):
    """Given: Workflow state file with completed action."""
    from conftest import create_workflow_state_file
    return create_workflow_state_file(workspace_directory, bot_name, behavior, action, completed_actions=completed_actions)

def given_workflow_with_states_and_transitions(bot_directory: Path, bot_name: str, behavior: str):
    """Given: Workflow with states and transitions."""
    # Workflow class removed - state managed by Behaviors and Actions collections
    states, transitions = given_workflow_states_and_transitions()
    return Workflow(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory, states=states, transitions=transitions)

def given_completed_action_entry_for_behavior(bot_name: str, behavior: str, action: str, timestamp: str = '2025-12-03T10:05:30Z'):
    """Given: Completed action entry for behavior."""
    return [{
        'action_state': f'{bot_name}.{behavior}.{action}',
        'timestamp': timestamp
    }]

def when_action_tracks_activity_with_outputs(action, outputs: dict, duration: int):
    """When: Action tracks activity with outputs."""
    return when_action_tracks_activity_on_completion(action, outputs=outputs, duration=duration)

def when_workflow_transitions_if_action_completed(workflow, action_name: str):
    """When: Workflow transitions if action is completed."""
    if workflow.is_action_completed(action_name):
        workflow.transition_to_next()

def given_clarification_parameters_with_questions_and_evidence():
    """Given: Clarification parameters with questions and evidence."""
    return {
        'key_questions_answered': {
            'user_types': 'Game Masters',
            'first_action': 'Group tokens into mobs'
        },
        'evidence_provided': {
            'original_input': 'I want to turn minions into mobs',
            'source_file': 'input.txt'
        }
    }

def given_clarification_parameters_for_shape_behavior():
    """Given: Clarification parameters for shape behavior."""
    return {
        'key_questions_answered': {'user_types': 'Game Masters'},
        'evidence_provided': {'input': 'input.txt'}
    }

def given_expected_key_questions_for_shape():
    """Given: Expected key questions for shape behavior."""
    return {'user_types': 'Game Masters'}

def given_expected_evidence_for_shape():
    """Given: Expected evidence for shape behavior."""
    return {'original_input': 'I want to turn minions into mobs'}

def given_discovery_key_questions_and_evidence():
    """Given: Discovery key questions and evidence."""
    key_questions = {'scope': 'Component level'}
    evidence = {'doc': 'requirements.md'}
    return key_questions, evidence

def then_clarification_json_contains_shape_data(clarification_file: Path):
    """Then: Clarification JSON contains shape data."""
    expected_key_questions = given_expected_key_questions_for_shape()
    expected_evidence = given_expected_evidence_for_shape()
    then_clarification_json_contains_behavior_data(clarification_file, 'shape', expected_key_questions, expected_evidence)

def then_clarification_data_contains_discovery_scope(clarification_data: dict, expected_scope: str):
    """Then: Clarification data contains discovery scope."""
    assert clarification_data['discovery']['key_questions']['answers']['scope'] == expected_scope

def then_clarification_data_contains_shape_user_types(clarification_data: dict, expected_user_types: str):
    """Then: Clarification data contains shape user types."""
    assert clarification_data['shape']['key_questions']['answers']['user_types'] == expected_user_types




def given_environment_bootstrapped_and_action_initialized_for_discovery(bot_directory: Path):
    """Given: Environment bootstrapped and action initialized for discovery."""
    action = given_gather_context_action_is_initialized(bot_directory, 'story_bot', 'discovery')
    return action


def given_action_outputs_and_duration():
    """Given: Action outputs and duration."""
    outputs = given_action_outputs_with_counts()
    duration = given_action_duration()
    return outputs, duration


def given_environment_bootstrapped_for_workflow_resume(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped for workflow resume."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'discovery')
    completed_actions = given_completed_action_entry_for_behavior(bot_name, behavior, 'gather_context')
    state_file = given_workflow_state_file_with_completed_action(workspace_directory, bot_name, behavior, 'gather_context', completed_actions)
    return bot_name, behavior, state_file


def then_workflow_current_state_is_decide_planning(workflow):
    """Then: Workflow current state is decide_planning_criteria."""
    assert workflow.current_state == 'decide_planning_criteria'


def given_environment_bootstrapped_with_guardrails(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped with guardrails."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    questions, evidence = given_questions_and_evidence_for_guardrails()
    create_guardrails_files(bot_directory, behavior, questions, evidence)
    return bot_name, behavior, questions, evidence




def given_environment_bootstrapped_with_malformed_guardrails(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped with malformed guardrails."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    given_malformed_guardrails_json_exists(bot_directory, behavior)
    action_obj = given_gather_context_action_is_initialized(bot_directory, bot_name, behavior)
    return bot_name, behavior, action_obj


def given_environment_action_and_parameters_for_clarification(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and parameters for clarification."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_gather_context_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_clarification_parameters_with_questions_and_evidence()
    bot_paths = BotPaths(bot_directory=bot_directory)
    return action, parameters, bot_paths


def given_environment_with_existing_clarification_and_action(bot_directory: Path, workspace_directory: Path):
    """Given: Environment with existing clarification and action."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_paths = BotPaths(bot_directory=bot_directory)
    discovery_key_questions, discovery_evidence = given_discovery_key_questions_and_evidence()
    clarification_file = given_clarification_json_exists_with_data(workspace_directory, 'discovery', discovery_key_questions, discovery_evidence, bot_paths)
    action = given_gather_context_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_clarification_parameters_for_shape_behavior()
    return clarification_file, action, parameters, bot_paths


def given_environment_action_and_empty_parameters(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and empty parameters."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_gather_context_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = {'other_data': 'some value'}
    bot_paths = BotPaths(bot_directory=bot_directory)
    return action, parameters, bot_paths

def given_gather_context_action_is_initialized(bot_directory: Path, bot_name: str, behavior_name: str):
    """Given step: GatherContextAction is initialized."""
    # Create bot_paths
    bot_paths = BotPaths(bot_directory=bot_directory)
    
    # Ensure behavior.json exists with proper structure
    import json
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    behavior_config = {
        "behaviorName": behavior_name,
        "description": f"Test behavior: {behavior_name}",
        "goal": f"Test goal for {behavior_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "instructions": {},  # Content expects a dict
        "actions_workflow": {
            "actions": [
                {'name': 'gather_context', 'order': 1}
            ]
        }
    }
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    # Create guardrails files if they don't exist (required by GatherContextAction and Guardrails)
    # Required context files
    guardrails_dir = behavior_dir / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    questions_file = guardrails_dir / 'key_questions.json'
    if not questions_file.exists():
        questions_file.write_text(json.dumps({'questions': []}), encoding='utf-8')
    evidence_file = guardrails_dir / 'evidence.json'
    if not evidence_file.exists():
        evidence_file.write_text(json.dumps({'evidence': []}), encoding='utf-8')
    
    # Strategy guardrails files (required by Guardrails.Strategy)
    strategy_dir = behavior_dir / 'guardrails' / 'strategy'
    strategy_dir.mkdir(parents=True, exist_ok=True)
    assumptions_file = strategy_dir / 'typical_assumptions.json'
    if not assumptions_file.exists():
        assumptions_file.write_text(json.dumps({'typical_assumptions': []}), encoding='utf-8')
    recommended_activities_file = strategy_dir / 'recommended_activities.json'
    if not recommended_activities_file.exists():
        recommended_activities_file.write_text(json.dumps({'recommended_activities': []}), encoding='utf-8')
    # StrategyCriterias loads from decision_criteria folder, create empty folder
    decision_criteria_dir = strategy_dir / 'decision_criteria'
    decision_criteria_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Behavior object
    behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
    
    # Create GatherContextAction with new signature
    from agile_bot.bots.base_bot.src.bot.base_action_config import BaseActionConfig
    base_action_config = BaseActionConfig('gather_context', bot_paths)
    
    return GatherContextAction(
        base_action_config=base_action_config,
        behavior=behavior,
        activity_tracker=None
    )

def when_action_tracks_activity_on_start(action: GatherContextAction):
    """When step: Action tracks activity on start."""
    action.track_activity_on_start()

def when_action_tracks_activity_on_completion(action: GatherContextAction, outputs: dict = None, duration: int = None):
    """When step: Action tracks activity on completion."""
    if outputs is None:
        outputs = given_action_outputs_with_counts()
    if duration is None:
        duration = given_action_duration()
    action.track_activity_on_completion(outputs=outputs, duration=duration)

# Removed then_activity_logged_with_action_state - use test_helpers.then_activity_logged_with_action_state instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import then_activity_logged_with_action_state


# Removed then_completion_entry_logged_with_outputs - use test_helpers.then_completion_entry_logged_with_outputs instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import then_completion_entry_logged_with_outputs


def given_activity_log_contains_entries(workspace_directory: Path, entries: list):
    """Given step: Activity log contains entries."""
    workspace_directory.mkdir(parents=True, exist_ok=True)
    log_file = workspace_directory / 'activity_log.json'
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        for entry in entries:
            db.insert(entry)
    return log_file


def then_activity_log_contains_entries(log_file: Path, expected_entries: list):
    """Then step: Activity log contains expected entries."""
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        entries = db.all()
        assert len(entries) == len(expected_entries)
        for expected_entry in expected_entries:
            assert any(
                entry.get('action_state') == expected_entry.get('action_state')
                for entry in entries
            )

# Removed duplicate then_completion_entry_logged_with_outputs - use test_helpers version instead
# Removed duplicate given_activity_log_contains_entries - already defined above
# Removed duplicate then_activity_log_contains_entries - already defined above (line 197)

def when_action_injects_questions_and_evidence(action: GatherContextAction):
    """When step: Action injects questions and evidence."""
    # Call do_execute to get instructions with guardrails injected
    result = action.do_execute({})
    instructions = result.get('instructions', {})
    # Return just the guardrails portion for testing
    return {'guardrails': instructions.get('guardrails', {})}

def then_instructions_contain_guardrails(instructions: dict, expected_questions: list, expected_evidence: list):
    """Then step: Instructions contain guardrails with questions and evidence."""
    assert 'guardrails' in instructions
    assert 'required_context' in instructions['guardrails']
    assert 'key_questions' in instructions['guardrails']['required_context']
    assert instructions['guardrails']['required_context']['key_questions'] == expected_questions
    assert 'evidence' in instructions['guardrails']['required_context']
    assert instructions['guardrails']['required_context']['evidence'] == expected_evidence

def then_instructions_do_not_contain_guardrails(instructions: dict):
    """Then step: Instructions do not contain guardrails."""
    assert 'guardrails' not in instructions or instructions['guardrails'] == {}

def given_malformed_guardrails_json_exists(bot_directory: Path, behavior: str):
    """Given step: Malformed guardrails JSON exists."""
    guardrails_dir = bot_directory / 'behaviors' / behavior / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text('invalid json {')
    return questions_file

def then_json_decode_error_raised_with_message(function, expected_keywords: list):
    """Then step: JSONDecodeError is raised with expected keywords.
    
    Checks that at least one of the expected keywords appears in the error message.
    """
    with pytest.raises(json.JSONDecodeError) as exc_info:
        function()
    error_message = str(exc_info.value)
    assert any(keyword in error_message for keyword in expected_keywords), \
        f"Expected at least one of {expected_keywords} in error message: {error_message}"

def when_action_executes_with_clarification_parameters(action: GatherContextAction, parameters: dict):
    """When step: Action executes with clarification parameters."""
    action.do_execute(parameters)

def then_clarification_json_file_exists(workspace_directory: Path, bot_paths: BotPaths = None):
    """Then step: clarification.json file exists."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        clarification_file = workspace_directory / 'docs' / 'stories' / 'clarification.json'
    else:
        documentation_path = bot_paths.documentation_path
        clarification_file = workspace_directory / documentation_path / 'clarification.json'
    assert clarification_file.exists(), f"clarification.json should be created at {clarification_file}"
    return clarification_file

def then_clarification_json_file_does_not_exist(workspace_directory: Path, bot_paths: BotPaths = None):
    """Then step: clarification.json file does not exist."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        clarification_file = workspace_directory / 'docs' / 'stories' / 'clarification.json'
    else:
        documentation_path = bot_paths.documentation_path
        clarification_file = workspace_directory / documentation_path / 'clarification.json'
    assert not clarification_file.exists(), f"clarification.json should not be created at {clarification_file} when no clarification data provided"

def then_clarification_json_contains_behavior_data(clarification_file: Path, behavior: str, expected_key_questions: dict = None, expected_evidence: dict = None):
    """Then step: clarification.json contains behavior data."""
    clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
    assert behavior in clarification_data
    if expected_key_questions:
        assert 'key_questions' in clarification_data[behavior]
        # New structure: key_questions has 'questions' and 'answers'
        assert 'answers' in clarification_data[behavior]['key_questions']
        for key, value in expected_key_questions.items():
            assert clarification_data[behavior]['key_questions']['answers'][key] == value
    if expected_evidence:
        assert 'evidence' in clarification_data[behavior]
        # New structure: evidence has 'required' and 'provided'
        assert 'provided' in clarification_data[behavior]['evidence']
        for key, value in expected_evidence.items():
            assert clarification_data[behavior]['evidence']['provided'][key] == value
    return clarification_data

def given_clarification_json_exists_with_data(workspace_directory: Path, behavior: str, key_questions: dict, evidence: dict, bot_paths: BotPaths = None):
    """Given step: clarification.json exists with data for behavior."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        stories_folder = workspace_directory / 'docs' / 'stories'
    else:
        documentation_path = bot_paths.documentation_path
        stories_folder = workspace_directory / documentation_path
    stories_folder.mkdir(parents=True, exist_ok=True)
    clarification_file = stories_folder / 'clarification.json'
    # New structure: key_questions has 'questions' and 'answers', evidence has 'required' and 'provided'
    existing_data = {
        behavior: {
            'key_questions': {
                'questions': [],
                'answers': key_questions
            },
            'evidence': {
                'required': [],
                'provided': evidence
            }
        }
    }
    clarification_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
    return clarification_file

def then_clarification_json_preserves_existing_behaviors(clarification_file: Path, existing_behaviors: list):
    """Then step: clarification.json preserves existing behavior data."""
    clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
    for behavior in existing_behaviors:
        assert behavior in clarification_data, f"Existing {behavior} data should be preserved"
    return clarification_data

# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# STORY: Track Activity for Gather Context Action
# ============================================================================

class TestTrackActivityForGatherContextAction:
    """Story: Track Activity for Gather Context Action - Tests activity tracking during execution."""

    def test_track_activity_when_gather_context_action_starts(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when gather_context action starts
        GIVEN: behavior is 'discovery' and action is 'gather_context'
        WHEN: gather_context action starts execution
        THEN: Activity logger creates entry with timestamp and action_state
        """
        # Given: Environment is bootstrapped
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        # And: GatherContextAction is initialized
        action = given_environment_bootstrapped_and_action_initialized_for_discovery(bot_directory)
        
        # When: Action starts and logs activity
        when_action_tracks_activity_on_start(action)
        
        # Then: Activity logged with correct action_state
        then_activity_logged_with_action_state(log_file, 'story_bot.discovery.gather_context')

    def test_track_activity_when_gather_context_action_completes(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when gather_context action completes
        GIVEN: gather_context action started
        WHEN: gather_context action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Given: Environment is bootstrapped
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        # And: GatherContextAction is initialized
        action = given_environment_bootstrapped_and_action_initialized_for_discovery(bot_directory)
        
        # When: Action completes
        when_action_tracks_activity_on_completion(action)
        
        # Then: Completion entry logged with outputs and duration
        outputs, duration = given_action_outputs_and_duration()
        then_completion_entry_logged_with_outputs(log_file, outputs, duration)

    def test_track_multiple_gather_context_invocations_across_behaviors(self, workspace_directory):
        """
        SCENARIO: Track multiple gather_context invocations across behaviors
        GIVEN: activity log contains entries for shape and discovery
        WHEN: both entries are present
        THEN: activity log distinguishes same action in different behaviors using full path
        """
        # Given: Activity log contains entries for shape and discovery
        entries = given_activity_log_entries_for_behaviors()
        log_file = given_activity_log_contains_entries(workspace_directory, entries)
        
        # When: Both entries are present
        # (log file already created above)
        
        # Then: Activity log distinguishes same action in different behaviors using full path
        expected_entries = given_expected_activity_log_entries_for_behaviors()
        then_activity_log_contains_entries(log_file, expected_entries)


# ============================================================================
# STORY: Proceed To Decide Planning
# ============================================================================

class TestProceedToDecidePlanning:
    """Story: Proceed To Decide Planning - Tests transition from gather_context to decide_planning_criteria."""

    def test_seamless_transition_from_gather_context_to_decide_planning_criteria(self, bot_directory, workspace_directory):
        """
        SCENARIO: Seamless transition from gather_context to decide_planning_criteria
        GIVEN: gather_context action is complete
        WHEN: workflow transitions
        THEN: Workflow proceeds to decide_planning_criteria
        """
        # Given: Bot directory and workspace directory are set up
        # When: Gather context action completes
        # Then: Workflow transitions to decide_planning_criteria (verified by verify_workflow_transition)
        verify_workflow_transition(bot_directory, workspace_directory, 'gather_context', 'decide_planning_criteria')

    def test_workflow_state_captures_gather_context_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow state captures gather_context completion
        GIVEN: gather_context action completes
        WHEN: Workflow saves completed action
        THEN: workflow state updated with timestamp and completed_actions
        """
        # Given: Bot directory and workspace directory are set up
        # When: Gather context action completes
        # Then: Workflow state captures completion (verified by verify_workflow_saves_completed_action)
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'gather_context')

    def test_workflow_resumes_at_decide_planning_criteria_after_interruption(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow resumes at decide_planning_criteria after interruption
        GIVEN: gather_context is completed and chat was interrupted
        WHEN: user reopens chat and invokes bot tool
        THEN: Workflow auto-forwards to decide_planning_criteria action
        """
        # Bootstrap environment
        bot_name, behavior, state_file = given_environment_bootstrapped_for_workflow_resume(bot_directory, workspace_directory)
        
        # When: Workflow loads and determines next action
        workflow = given_workflow_with_states_and_transitions(bot_directory, bot_name, behavior)
        
        # Then: Workflow should auto-advance past completed gather_context
        # If current_action is completed, workflow should transition to next
        when_workflow_transitions_if_action_completed(workflow, 'gather_context')
        
        then_workflow_current_state_is_decide_planning(workflow)


# ============================================================================
# STORY: Inject Guardrails as Part of Clarify Requirements
# ============================================================================

class TestInjectGuardrailsAsPartOfClarifyRequirements:
    """Story: Inject Guardrails as Part of Clarify Requirements - Tests guardrail injection."""

    def test_action_injects_questions_and_evidence(self, bot_directory, workspace_directory):
        # Given: Environment is bootstrapped
        bot_name, behavior, questions, evidence = given_environment_bootstrapped_with_guardrails(bot_directory, workspace_directory)
        # And: GatherContextAction is initialized
        action_obj = given_gather_context_action_is_initialized(bot_directory, bot_name, behavior)
        
        # When: Action injects questions and evidence
        instructions = when_action_injects_questions_and_evidence(action_obj)
        
        # Then: Instructions contain guardrails with questions and evidence
        then_instructions_contain_guardrails(instructions, questions, evidence)

    def test_action_uses_base_instructions_when_guardrails_missing(self, bot_directory, workspace_directory):
        # Given: Environment is bootstrapped
        bot_name, behavior, action_obj = given_environment_bootstrapped_and_action_initialized(bot_directory, workspace_directory)
        
        # When: Action injects questions and evidence
        instructions = when_action_injects_questions_and_evidence(action_obj)
        
        # Then: Instructions do not contain guardrails
        then_instructions_do_not_contain_guardrails(instructions)

    def test_action_handles_malformed_guardrails_json(self, bot_directory, workspace_directory):
        # Given: Environment is bootstrapped
        bot_name, behavior, action_obj = given_environment_bootstrapped_with_malformed_guardrails(bot_directory, workspace_directory)
        
        # When: Action injects questions and evidence
        # Then: Action handles malformed JSON gracefully (returns empty guardrails)
        instructions = when_action_injects_questions_and_evidence(action_obj)
        then_instructions_do_not_contain_guardrails(instructions)


# ============================================================================
# STORY: Store Clarification Data
# ============================================================================

class TestStoreClarificationData:
    """Story: Store Clarification Data - Tests that clarification data is saved to clarification.json."""

    def test_save_clarification_data_when_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Save clarification data when parameters are provided
        GIVEN: gather_context action is initialized
        AND: parameters contain key_questions_answered and evidence_provided
        WHEN: do_execute is called with these parameters
        THEN: clarification.json file is created in docs/stories/ folder
        AND: file contains behavior section with key_questions and evidence
        """
        # Given: Environment is bootstrapped
        action, parameters, bot_paths = given_environment_action_and_parameters_for_clarification(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_clarification_parameters(action, parameters)
        
        # Then: clarification.json file exists
        clarification_file = then_clarification_json_file_exists(workspace_directory, bot_paths)
        # And: File contains correct structure
        then_clarification_json_contains_behavior_data(
            clarification_file,
            'shape',
            expected_key_questions={'user_types': 'Game Masters'},
            expected_evidence={'original_input': 'I want to turn minions into mobs'}
        )

    def test_preserve_existing_clarification_data_when_saving(self, bot_directory, workspace_directory):
        """
        SCENARIO: Preserve existing clarification data when saving
        GIVEN: clarification.json already exists with data for 'discovery' behavior
        AND: gather_context action is initialized for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: clarification.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Environment is bootstrapped
        clarification_file, action, parameters, bot_paths = given_environment_with_existing_clarification_and_action(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_clarification_parameters(action, parameters)
        
        # Then: Both behaviors' data are preserved
        clarification_data = then_clarification_json_preserves_existing_behaviors(clarification_file, ['discovery', 'shape'])
        then_clarification_data_contains_discovery_scope(clarification_data, 'Component level')
        then_clarification_data_contains_shape_user_types(clarification_data, 'Game Masters')

    def test_skip_saving_when_no_clarification_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Skip saving when no clarification parameters are provided
        GIVEN: gather_context action is initialized
        AND: parameters do not contain key_questions_answered or evidence_provided
        WHEN: do_execute is called with empty or unrelated parameters
        THEN: clarification.json file is not created
        """
        # Given: Environment is bootstrapped
        action, parameters, bot_paths = given_environment_action_and_empty_parameters(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_clarification_parameters(action, parameters)
        
        # Then: clarification.json file is not created
        then_clarification_json_file_does_not_exist(workspace_directory, bot_paths)
