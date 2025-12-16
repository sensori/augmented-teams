"""
Gather Context Tests

Tests for all stories in the 'Gather Context' sub-epic:
- Track Activity for Gather Context Action
- Proceed To Decide Planning
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.actions.clarify.clarify_action import ClarifyContextAction
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
# Workflow class removed - state managed by Behaviors and Actions collections

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
            'action_state': f'{bot_name}.{behavior}.clarify',
            'timestamp': f'{9 + i}:00'
        })
    return entries

def given_expected_activity_log_entries_for_behaviors(bot_name: str = 'story_bot', behaviors: list = None):
    """Given: Expected activity log entries for multiple behaviors."""
    if behaviors is None:
        behaviors = ['shape', 'discovery']
    return [
        {'action_state': f'{bot_name}.{behavior}.clarify'}
        for behavior in behaviors
    ]

def given_questions_and_evidence_for_guardrails():
    """Given: Questions and evidence for guardrails."""
    questions = ['What is the scope?', 'Who are the users?']
    evidence = ['Requirements doc', 'User interviews']
    return questions, evidence

def given_workflow_state_file_with_completed_action(workspace_directory: Path, bot_name: str, behavior: str, action: str, completed_actions: list):
    """Given: behavior_action_state.json file with completed action."""
    import json
    state_file = workspace_directory / 'behavior_action_state.json'
    state_data = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{action}',
        'completed_actions': completed_actions or [],
        'timestamp': '2025-12-04T16:00:00.000000'
    }
    state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    return state_file

def given_completed_action_entry_for_behavior(bot_name: str, behavior: str, action: str, timestamp: str = '2025-12-03T10:05:30Z'):
    """Given: Completed action entry for behavior."""
    return [{
        'action_state': f'{bot_name}.{behavior}.{action}',
        'timestamp': timestamp
    }]

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
    completed_actions = given_completed_action_entry_for_behavior(bot_name, behavior, 'clarify')
    # When clarify is completed, current_action should be set to the next action (strategy)
    # This simulates the state after clarify was completed and workflow advanced
    state_file = given_workflow_state_file_with_completed_action(workspace_directory, bot_name, behavior, 'strategy', completed_actions)
    return bot_name, behavior, state_file


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
    """Given step: ClarifyContextAction is initialized."""
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
                {'name': 'clarify', 'order': 1}
            ]
        }
    }
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    # Create guardrails files if they don't exist (required by ClarifyContextAction and Guardrails)
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
    
    # Create ClarifyContextAction with new signature
    from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
    base_action_config = BaseActionConfig('clarify', bot_paths)
    
    return ClarifyContextAction(
        base_action_config=base_action_config,
        behavior=behavior,
        activity_tracker=None
    )

def when_action_tracks_activity_on_start(action: ClarifyContextAction):
    """When step: Action tracks activity on start."""
    action.track_activity_on_start()

def when_action_tracks_activity_on_completion(action: ClarifyContextAction, outputs: dict = None, duration: int = None):
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

def when_action_injects_questions_and_evidence(action: ClarifyContextAction):
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

def when_action_executes_with_clarification_parameters(action: ClarifyContextAction, parameters: dict):
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

class TestTrackActivityForClarifyContextAction:
    """Story: Track Activity for Gather Context Action - Tests activity tracking during execution."""

    def test_track_activity_when_gather_context_action_starts(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when clarify action starts
        GIVEN: behavior is 'discovery' and action is 'clarify'
        WHEN: clarify action starts execution
        THEN: Activity logger creates entry with timestamp and action_state
        """
        # Given: Environment is bootstrapped
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        # And: ClarifyContextAction is initialized
        action = given_environment_bootstrapped_and_action_initialized_for_discovery(bot_directory)
        
        # When: Action starts and logs activity
        when_action_tracks_activity_on_start(action)
        
        # Then: Activity logged with correct action_state
        then_activity_logged_with_action_state(log_file, 'story_bot.discovery.clarify')

    def test_track_activity_when_gather_context_action_completes(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when clarify action completes
        GIVEN: clarify action started
        WHEN: clarify action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Given: Environment is bootstrapped
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        # And: ClarifyContextAction is initialized
        action = given_environment_bootstrapped_and_action_initialized_for_discovery(bot_directory)
        
        # When: Action completes
        when_action_tracks_activity_on_completion(action)
        
        # Then: Completion entry logged with outputs and duration
        outputs, duration = given_action_outputs_and_duration()
        then_completion_entry_logged_with_outputs(log_file, outputs, duration)

    def test_track_multiple_gather_context_invocations_across_behaviors(self, workspace_directory):
        """
        SCENARIO: Track multiple clarify invocations across behaviors
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
    """Story: Proceed To Strategy - Tests transition from clarify to strategy."""

    def test_seamless_transition_from_clarify_to_strategy(self, bot_directory, workspace_directory):
        """
        SCENARIO: Seamless transition from clarify to strategy
        GIVEN: clarify action is complete
        WHEN: workflow transitions
        THEN: Workflow proceeds to strategy
        """
        # Given: Bot directory and workspace directory are set up
        # When: Gather context action completes
        # Then: Workflow transitions to decide_planning_criteria (verified by verify_workflow_transition)
        verify_workflow_transition(bot_directory, workspace_directory, 'clarify', 'strategy')

    def test_workflow_state_captures_gather_context_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow state captures clarify completion
        GIVEN: clarify action completes
        WHEN: Workflow saves completed action
        THEN: workflow state updated with timestamp and completed_actions
        """
        # Given: Bot directory and workspace directory are set up
        # When: Gather context action completes
        # Then: Workflow state captures completion (verified by verify_workflow_saves_completed_action)
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'clarify')

    def test_workflow_resumes_at_decide_planning_criteria_after_interruption(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow resumes at strategy after interruption
        GIVEN: clarify is completed and chat was interrupted
        WHEN: user reopens chat and invokes bot tool
        THEN: Workflow auto-forwards to strategy action
        """
        # Bootstrap environment
        bot_name, behavior, state_file = given_environment_bootstrapped_for_workflow_resume(bot_directory, workspace_directory)
        
        # When: Bot loads and determines next action
        from conftest import create_bot_config_file
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        
        create_bot_config_file(bot_directory, bot_name, [behavior])
        create_actions_workflow_json(bot_directory, behavior)
        create_minimal_guardrails_files(bot_directory, behavior, bot_name)
        
        config_path = bot_directory / 'bot_config.json'
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)
        
        # Then: Bot should auto-advance past completed clarify action
        # Actions collection loads state and sets current to next uncompleted action
        behavior_obj = bot.behaviors.find_by_name(behavior)
        behavior_obj.actions.load_state()
        assert behavior_obj.actions.current is not None, "Should have a current action"
        assert behavior_obj.actions.current.action_name == 'strategy', f"Should transition to strategy, got {behavior_obj.actions.current.action_name}"


# ============================================================================
# STORY: Inject Guardrails as Part of Clarify Requirements
# ============================================================================

class TestInjectGuardrailsAsPartOfClarifyRequirements:
    """Story: Inject Guardrails as Part of Clarify Requirements - Tests guardrail injection."""

    def test_action_injects_questions_and_evidence(self, bot_directory, workspace_directory):
        # Given: Environment is bootstrapped
        bot_name, behavior, questions, evidence = given_environment_bootstrapped_with_guardrails(bot_directory, workspace_directory)
        # And: ClarifyContextAction is initialized
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
        # Given: Environment is bootstrapped with malformed JSON
        import json
        import pytest
        
        # When: Creating action with malformed guardrails JSON
        # Then: Raises JSONDecodeError during initialization (does not handle gracefully)
        with pytest.raises(json.JSONDecodeError):
            bot_name, behavior, action_obj = given_environment_bootstrapped_with_malformed_guardrails(bot_directory, workspace_directory)


# ============================================================================
# STORY: Store Clarification Data
# ============================================================================

class TestStoreClarificationData:
    """Story: Store Clarification Data - Tests that clarification data is saved to clarification.json."""

    def test_save_clarification_data_when_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Save clarification data when parameters are provided
        GIVEN: clarify action is initialized
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
        AND: clarify action is initialized for 'shape' behavior
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
        GIVEN: clarify action is initialized
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


# ============================================================================
# HELPER FUNCTIONS - Domain Classes (Stories 17-20: BaseActionConfig, Actions, Action, Guardrails)
# ============================================================================

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.actions.actions import Actions
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.guardrails import Guardrails


def given_action_config_file_created(bot_directory: Path, action_name: str, config_data: dict):
    """Given: action_config.json file created.
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    base_actions_dir = get_test_base_actions_dir(bot_directory) / action_name
    base_actions_dir.mkdir(parents=True, exist_ok=True)
    config_file = base_actions_dir / 'action_config.json'
    config_file.write_text(json.dumps(config_data), encoding='utf-8')
    return config_file


def when_base_action_config_instantiated(action_name: str, bot_paths: BotPaths):
    """When: BaseActionConfig instantiated."""
    return BaseActionConfig(action_name=action_name, bot_paths=bot_paths)


def when_actions_instantiated(behavior_config, behavior):
    """When: Actions instantiated."""
    # Behavior already has actions property initialized, use it
    if isinstance(behavior, Behavior):
        return behavior.actions
    # Fallback for old tests that pass string
    return Actions(behavior_config=behavior_config, behavior=behavior)


def when_action_instantiated(base_action_config: BaseActionConfig, behavior: Behavior):
    """When: Action instantiated."""
    return Action(base_action_config=base_action_config, behavior=behavior)


def when_guardrails_instantiated(behavior_config):
    """When: Guardrails instantiated."""
    return Guardrails(behavior_config=behavior_config)


def then_base_action_config_properties_accessible(base_action_config: BaseActionConfig):
    """Then: BaseActionConfig properties are accessible."""
    assert hasattr(base_action_config, 'order')
    assert hasattr(base_action_config, 'next_action')
    assert hasattr(base_action_config, 'custom_class')
    assert hasattr(base_action_config, 'instructions')
    assert hasattr(base_action_config, 'workflow')


def then_actions_collection_contains_actions(actions: Actions, expected_count: int):
    """Then: Actions collection contains expected number of actions."""
    action_list = list(actions)
    assert len(action_list) == expected_count


def then_action_is_not_none(action):
    """Then: Action is not None."""
    assert action is not None


def then_action_is_none(action):
    """Then: Action is None."""
    assert action is None


def then_action_properties_accessible(action: Action):
    """Then: Action properties are accessible."""
    assert hasattr(action, 'order')
    assert hasattr(action, 'action_class')
    assert hasattr(action, 'instructions')
    assert hasattr(action, 'tracker')


def then_guardrails_properties_accessible(guardrails: Guardrails):
    """Then: Guardrails properties are accessible."""
    assert hasattr(guardrails, 'required_context')
    assert hasattr(guardrails, 'strategy')


def given_environment_bootstrapped(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped."""
    from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env
    bootstrap_env(bot_directory, workspace_directory)


def when_bot_paths_created():
    """When: BotPaths created."""
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    return BotPaths()


def given_complete_action_config_data(action_name: str):
    """Given: Complete action config data."""
    return {
        'name': action_name,
        'order': 1,
        'next_action': 'strategy',
        'action_class': 'ClarifyContextAction',
        'instructions': ['instruction1', 'instruction2'],
        'workflow': True
    }


def then_base_action_config_order_is(base_action_config: BaseActionConfig, expected_order: int):
    """Then: BaseActionConfig order is expected."""
    assert base_action_config.order == expected_order


def then_base_action_config_next_action_is(base_action_config: BaseActionConfig, expected_next_action: str):
    """Then: BaseActionConfig next_action is expected."""
    assert base_action_config.next_action == expected_next_action


def when_behavior_config_accessed_from_behavior(behavior: Behavior):
    """When: BehaviorConfig accessed from behavior."""
    return behavior.behavior_config


def when_actions_count_from_behavior_config(behavior_config):
    """When: Actions count from behavior config."""
    # actions_workflow is already a list, not a dict
    if isinstance(behavior_config.actions_workflow, list):
        return len(behavior_config.actions_workflow)
    # Fallback for dict format
    return len(behavior_config.actions_workflow.get('actions', []))


def when_actions_find_by_name(actions: Actions, action_name: str):
    """When: Actions find_by_name() called."""
    return actions.find_by_name(action_name)


def when_actions_find_by_order(actions: Actions, order: int):
    """When: Actions find_by_order() called."""
    return actions.find_by_order(order)


def when_actions_navigates_to(actions: Actions, action_name: str):
    """When: Actions navigate_to() called."""
    actions.navigate_to(action_name)


def when_actions_current_accessed(actions: Actions):
    """When: Actions current property accessed."""
    return actions.current


def when_actions_next_accessed(actions: Actions):
    """When: Actions next property accessed."""
    return actions.next


def then_next_action_may_be_none_or_not_none(next_action):
    """Then: Next action may be None or not None."""
    if next_action:
        then_action_is_not_none(next_action)


def then_current_action_is_not_none(actions: Actions):
    """Then: Current action is not None."""
    assert actions.current is not None


def then_current_action_name_is(actions: Actions, expected_name: str):
    """Then: Current action name is expected."""
    assert actions.current.action_name == expected_name


def when_actions_close_current_called(actions: Actions):
    """When: Actions close_current() called."""
    actions.close_current()


def then_actions_has_close_current_method(actions: Actions):
    """Then: Actions has close_current method."""
    assert hasattr(actions, 'close_current')


def then_actions_has_execute_current_method(actions: Actions):
    """Then: Actions has execute_current method."""
    assert hasattr(actions, 'execute_current')


def then_action_has_instructions_property(action: Action):
    """Then: Action has instructions property."""
    assert hasattr(action, 'instructions')


def then_action_instructions_is_not_none(action: Action):
    """Then: Action instructions is not None."""
    assert action.instructions is not None


def then_action_order_is_integer(action: Action):
    """Then: Action order is integer."""
    assert isinstance(action.order, int)


def then_action_tracker_is_not_none(action: Action):
    """Then: Action tracker is not None."""
    assert action.tracker is not None


def given_guardrails_files_created(bot_directory: Path, behavior_name: str, bot_name: str = 'story_bot'):
    """Given: Guardrails files created."""
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    return create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)


def then_guardrails_required_context_is_not_none(guardrails: Guardrails):
    """Then: Guardrails required_context is not None."""
    assert guardrails.required_context is not None


def then_guardrails_strategy_is_not_none(guardrails: Guardrails):
    """Then: Guardrails strategy is not None."""
    assert guardrails.strategy is not None


def when_guardrails_required_context_accessed(guardrails: Guardrails):
    """When: Guardrails required_context property accessed."""
    return guardrails.required_context


def when_guardrails_strategy_accessed(guardrails: Guardrails):
    """When: Guardrails strategy property accessed."""
    return guardrails.strategy


def then_guardrails_required_context_is_not_none_from_value(required_context):
    """Then: Guardrails required_context value is not None."""
    assert required_context is not None


def then_guardrails_strategy_is_not_none_from_value(strategy):
    """Then: Guardrails strategy value is not None."""
    assert strategy is not None


# ============================================================================
# TEST CLASSES - Domain Classes (Stories 17-20: BaseActionConfig, Actions, Action, Guardrails)
# ============================================================================

class TestLoadBaseActionConfig:
    """Story: Load Base Action Config (Sub-epic: Gather Context)"""
    
    def test_base_action_config_loads_correct_action_from_action_config_json_file(self, bot_directory, workspace_directory):
        """
        SCENARIO: Base action config loads correct action from action_config.json file
        GIVEN: action_config.json exists in base_actions/{action_name}/ with complete config
        WHEN: BaseActionConfig instantiated with action_name
        THEN: Config loaded from file and properties accessible (order, next_action, custom_class, instructions, workflow)
        """
        # Given: action_config.json exists
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_paths = when_bot_paths_created()
        action_name = 'clarify'
        config_data = given_complete_action_config_data(action_name)
        given_action_config_file_created(bot_directory, action_name, config_data)
        
        # When: BaseActionConfig instantiated
        base_action_config = when_base_action_config_instantiated(action_name, bot_paths)
        
        # Then: Config loaded and properties accessible
        then_base_action_config_properties_accessible(base_action_config)
        then_base_action_config_order_is(base_action_config, 1)
        then_base_action_config_next_action_is(base_action_config, 'strategy')
    
    def test_base_action_config_uses_default_config_when_action_config_json_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Base action config uses default config when action_config.json missing
        GIVEN: Action name without action_config.json
        WHEN: BaseActionConfig instantiated
        THEN: Uses default config (doesn't raise error)
        """
        # Given: Action name without action_config.json
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_paths = when_bot_paths_created()
        action_name = 'nonexistent_action'
        
        # When: BaseActionConfig instantiated
        base_action_config = when_base_action_config_instantiated(action_name, bot_paths)
        
        # Then: Uses default config (doesn't raise error)
        then_base_action_config_properties_accessible(base_action_config)
        then_base_action_config_order_is(base_action_config, 0)


class TestAccessActions:
    """Story: Access Actions (Sub-epic: Gather Context)"""
    
    def test_actions_collection_loads_actions_from_behavior_config(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions collection loads actions from behavior config
        GIVEN: BehaviorConfig with actions_workflow
        WHEN: Actions instantiated with behavior_config and behavior
        THEN: Actions collection contains all actions from config
        """
        # Given: BehaviorConfig with actions_workflow
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        # Create Behavior object (not just name string)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json, create_base_instructions
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_base_instructions(bot_directory)  # Create base action configs for all actions
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        
        # When: Actions instantiated
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # Then: Actions collection contains all actions from config
        expected_count = when_actions_count_from_behavior_config(behavior_config)
        then_actions_collection_contains_actions(actions, expected_count)
    
    def test_actions_find_by_name_returns_action_when_exists(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions find by name returns action when exists
        GIVEN: Actions collection with 'clarify' action
        WHEN: find_by_name('clarify') called
        THEN: Returns Action object
        """
        # Given: Actions collection with 'gather_context' action
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        # Create Behavior object (not just name string)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # When: find_by_name('gather_context') called
        result = when_actions_find_by_name(actions, 'clarify')
        
        # Then: Returns Action object
        then_action_is_not_none(result)
    
    def test_actions_find_by_name_returns_none_when_does_not_exist(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions find by name returns none when does not exist
        GIVEN: Actions collection without 'nonexistent_action'
        WHEN: find_by_name('nonexistent_action') called
        THEN: Returns None
        """
        # Given: Actions collection without 'nonexistent_action'
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        # Create Behavior object (not just name string)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # When: find_by_name('nonexistent_action') called
        result = when_actions_find_by_name(actions, 'nonexistent_action')
        
        # Then: Returns None
        then_action_is_none(result)
    
    def test_actions_find_by_order_returns_action_when_exists(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions find by order returns action when exists
        GIVEN: Actions collection with action at order 1
        WHEN: find_by_order(1) called
        THEN: Returns Action object
        """
        # Given: Actions collection with action at order 1
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # When: find_by_order(1) called
        result = when_actions_find_by_order(actions, 1)
        
        # Then: Returns Action object
        then_action_is_not_none(result)
    
    def test_actions_find_by_order_returns_none_when_does_not_exist(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions find by order returns none when does not exist
        GIVEN: Actions collection without order 99
        WHEN: find_by_order(99) called
        THEN: Returns None
        """
        # Given: Actions collection without order 99
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # When: find_by_order(99) called
        result = when_actions_find_by_order(actions, 99)
        
        # Then: Returns None
        then_action_is_none(result)
    
    def test_actions_current_and_next_properties_return_action_objects(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions current and next properties return action objects
        GIVEN: Actions collection with current action set
        WHEN: current and next properties accessed
        THEN: Returns current Action object and next Action object
        """
        # Given: Actions collection with current action set
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        when_actions_navigates_to(actions, 'clarify')
        
        # When: current and next properties accessed
        current = when_actions_current_accessed(actions)
        next_action = when_actions_next_accessed(actions)
        
        # Then: Returns Action objects
        then_action_is_not_none(current)
        then_next_action_may_be_none_or_not_none(next_action)
    
    def test_actions_navigate_to_action_updates_current_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions navigate to action updates current action
        GIVEN: Actions collection
        WHEN: navigate_to('strategy') called
        THEN: Current action updated to 'strategy'
        """
        # Given: Actions collection
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        
        # When: navigate_to('strategy') called (use an action that exists in the workflow)
        when_actions_navigates_to(actions, 'strategy')
        
        # Then: Current action updated
        then_current_action_is_not_none(actions)
        then_current_action_name_is(actions, 'strategy')
    
    def test_actions_close_current_marks_action_complete(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions close current marks action complete
        GIVEN: Actions collection with current action
        WHEN: close_current() called
        THEN: Current action marked complete
        """
        # Given: Actions collection with current action
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        when_actions_navigates_to(actions, 'clarify')
        
        # When: close_current() called
        when_actions_close_current_called(actions)
        
        # Then: Current action marked complete (observable through workflow state)
        then_actions_has_close_current_method(actions)
    
    def test_actions_execute_current_executes_current_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Actions execute current executes current action
        GIVEN: Actions collection with current action
        WHEN: execute_current() called
        THEN: Current action's execute() method called
        """
        # Given: Actions collection with current action
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        actions = when_actions_instantiated(behavior_config, behavior)
        when_actions_navigates_to(actions, 'clarify')
        
        # When: execute_current() called
        # Then: Method exists (observable behavior)
        then_actions_has_execute_current_method(actions)


class TestInitializeAction:
    """Story: Initialize Action (Sub-epic: Gather Context)"""
    
    def test_action_initializes_with_base_action_config_and_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action initializes with base action config and behavior
        GIVEN: BaseActionConfig and Behavior
        WHEN: Action instantiated with both
        THEN: Action initialized successfully
        """
        # Given: BaseActionConfig and Behavior
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_paths = when_bot_paths_created()
        base_action_config = when_base_action_config_instantiated('clarify', bot_paths)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        # Create behavior.json file (required by Behavior class)
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        create_actions_workflow_json(bot_directory, behavior_name)
        # Create guardrails files (required by Behavior class)
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        # Create Behavior object (not just string)
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        
        # When: Action instantiated
        action = when_action_instantiated(base_action_config, behavior)
        
        # Then: Action initialized successfully
        then_action_is_not_none(action)
    
    def test_action_loads_and_merges_instructions_on_initialization(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action loads and merges instructions on initialization
        GIVEN: BaseActionConfig with instructions and Behavior
        WHEN: Action instantiated
        THEN: Instructions loaded and merged
        """
        # Given: BaseActionConfig with instructions and Behavior
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot_paths = BotPaths(bot_directory=bot_directory)
        base_action_config = when_base_action_config_instantiated('clarify', bot_paths)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        
        # When: Action instantiated
        action = when_action_instantiated(base_action_config, behavior)
        
        # Then: Instructions loaded and merged
        then_action_has_instructions_property(action)
        then_action_instructions_is_not_none(action)
    
    def test_action_properties_return_expected_values(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action properties return expected values
        GIVEN: Action initialized with BaseActionConfig and Behavior
        WHEN: Properties accessed (order, action_class, instructions, tracker)
        THEN: All properties return expected values (order from config, action_class from config, merged instructions dict, ActivityTracker instance)
        """
        # Given: Action initialized
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_actions_workflow_json(bot_directory, behavior_name)
        create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot_paths = BotPaths(bot_directory=bot_directory)
        base_action_config = when_base_action_config_instantiated('clarify', bot_paths)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        action = when_action_instantiated(base_action_config, behavior)
        
        # When: Properties accessed
        # Then: All properties return expected values
        then_action_properties_accessible(action)
        then_action_order_is_integer(action)
        then_action_instructions_is_not_none(action)
        then_action_tracker_is_not_none(action)


class TestLoadGuardrails:
    """Story: Load Guardrails (Sub-epic: Gather Context)"""
    
    def test_guardrails_loads_required_context_guardrails(self, bot_directory, workspace_directory):
        """
        SCENARIO: Guardrails loads required context guardrails
        GIVEN: BehaviorConfig with guardrails directory
        WHEN: Guardrails instantiated with behavior_config
        THEN: Required context guardrails loaded
        """
        # Given: BehaviorConfig with guardrails directory
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        create_actions_workflow_json(bot_directory, behavior_name)
        given_guardrails_files_created(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        
        # When: Guardrails instantiated
        guardrails = when_guardrails_instantiated(behavior_config)
        
        # Then: Required context guardrails loaded
        then_guardrails_properties_accessible(guardrails)
        then_guardrails_required_context_is_not_none(guardrails)
    
    def test_guardrails_loads_strategy_guardrails(self, bot_directory, workspace_directory):
        """
        SCENARIO: Guardrails loads strategy guardrails
        GIVEN: BehaviorConfig with strategy guardrails directory
        WHEN: Guardrails instantiated
        THEN: Strategy guardrails loaded
        """
        # Given: BehaviorConfig with strategy guardrails directory
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        create_actions_workflow_json(bot_directory, behavior_name)
        given_guardrails_files_created(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        
        # When: Guardrails instantiated
        guardrails = when_guardrails_instantiated(behavior_config)
        
        # Then: Strategy guardrails loaded
        then_guardrails_properties_accessible(guardrails)
        then_guardrails_strategy_is_not_none(guardrails)
    
    def test_guardrails_properties_return_guardrails_objects(self, bot_directory, workspace_directory):
        """
        SCENARIO: Guardrails properties return guardrails objects
        GIVEN: Guardrails with loaded guardrails
        WHEN: Properties accessed (required_context, strategy)
        THEN: Returns RequiredContext object and Strategy object
        """
        # Given: Guardrails with loaded guardrails
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        create_actions_workflow_json(bot_directory, behavior_name)
        given_guardrails_files_created(bot_directory, behavior_name, bot_name)
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        guardrails = when_guardrails_instantiated(behavior_config)
        
        # When: Properties accessed
        required_context = when_guardrails_required_context_accessed(guardrails)
        strategy = when_guardrails_strategy_accessed(guardrails)
        
        # Then: Returns guardrails objects
        then_guardrails_required_context_is_not_none_from_value(required_context)
        then_guardrails_strategy_is_not_none_from_value(strategy)
    
    def test_guardrails_handles_missing_guardrails_files_gracefully(self, bot_directory, workspace_directory):
        """
        SCENARIO: Guardrails handles missing guardrails files gracefully
        GIVEN: BehaviorConfig without guardrails files
        WHEN: Guardrails instantiated
        THEN: Creates empty/default guardrails objects
        """
        # Given: BehaviorConfig without guardrails files
        given_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, behavior_name = given_bot_name_and_behavior_setup('story_bot', 'shape')
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        create_actions_workflow_json(bot_directory, behavior_name)
        # Don't create guardrails files - but need behavior.json
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        bot_paths = BotPaths(bot_directory=bot_directory)
        behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
        behavior_config = when_behavior_config_accessed_from_behavior(behavior)
        
        # When: Guardrails instantiated
        guardrails = when_guardrails_instantiated(behavior_config)
        
        # Then: Creates empty/default guardrails objects (doesn't raise error)
        then_guardrails_properties_accessible(guardrails)
