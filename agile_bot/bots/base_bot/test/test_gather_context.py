"""
Gather Context Tests

Tests for all stories in the 'Gather Context' sub-epic:
- Track Activity for Gather Context Action
- Proceed To Decide Planning
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_activity_log_file,
    create_workflow_state,
    read_activity_log,
    create_guardrails_files,
    verify_workflow_transition,
    verify_workflow_saves_completed_action
)

def verify_activity_logged(log_file: Path, action_state: str):
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        entries = db.all()
        assert any(entry['action_state'] == action_state for entry in entries)

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
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action starts and logs activity
        action = GatherContextAction(
            bot_name='story_bot',
            behavior='discovery',
            bot_directory=bot_directory
        )
        action.track_activity_on_start()
        
        # Then: Activity logged with correct action_state
        verify_activity_logged(log_file, 'story_bot.discovery.gather_context')

    def test_track_activity_when_gather_context_action_completes(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when gather_context action completes
        GIVEN: gather_context action started
        WHEN: gather_context action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log with start entry
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action completes
        action = GatherContextAction(
            bot_name='story_bot',
            behavior='discovery',
            bot_directory=bot_directory
        )
        action.track_activity_on_completion(
            outputs={'questions_count': 5, 'evidence_count': 3},
            duration=330
        )
        
        # Then: Completion entry logged
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            log_data = db.all()
            completion_entry = next(e for e in log_data if 'outputs' in e)
            assert completion_entry['outputs']['questions_count'] == 5
            assert completion_entry['duration'] == 330

    def test_track_multiple_gather_context_invocations_across_behaviors(self, workspace_directory):
        """
        SCENARIO: Track multiple gather_context invocations across behaviors
        GIVEN: activity log contains entries for shape and discovery
        WHEN: both entries are present
        THEN: activity log distinguishes same action in different behaviors using full path
        """
        # Given: Activity log with multiple behavior entries (in workspace_directory)
        workspace_directory.mkdir(parents=True, exist_ok=True)
        log_file = workspace_directory / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            db.insert({'action_state': 'story_bot.shape.gather_context', 'timestamp': '09:00'})
            db.insert({'action_state': 'story_bot.discovery.gather_context', 'timestamp': '10:00'})
        
        # When: Read activity log
        with TinyDB(log_file) as db:
            log_data = db.all()
        
        # Then: 2 separate entries with full paths
        assert len(log_data) == 2
        assert log_data[0]['action_state'] == 'story_bot.shape.gather_context'
        assert log_data[1]['action_state'] == 'story_bot.discovery.gather_context'


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
        verify_workflow_transition(bot_directory, workspace_directory, 'gather_context', 'decide_planning_criteria')

    def test_workflow_state_captures_gather_context_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow state captures gather_context completion
        GIVEN: gather_context action completes
        WHEN: Workflow saves completed action
        THEN: workflow state updated with timestamp and completed_actions
        """
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'gather_context')

    def test_workflow_resumes_at_decide_planning_criteria_after_interruption(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow resumes at decide_planning_criteria after interruption
        GIVEN: gather_context is completed and chat was interrupted
        WHEN: user reopens chat and invokes bot tool
        THEN: Workflow auto-forwards to decide_planning_criteria action
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Workflow state with completed gather_context and current_action pointing to it
        from agile_bot.bots.base_bot.src.state.workflow import Workflow
        
        state_file = create_workflow_state(
            workspace_directory,
            'story_bot',
            'discovery',
            'gather_context',
            completed_actions=[{
                'action_state': 'story_bot.discovery.gather_context',
                'timestamp': '2025-12-03T10:05:30Z'
            }]
        )
        
        # When: Workflow loads and determines next action
        states = ['gather_context', 'decide_planning_criteria', 'build_knowledge']
        transitions = [
            {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
            {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        ]
        
        workflow = Workflow(
            bot_name='story_bot',
            behavior='discovery',
            bot_directory=bot_directory,
            states=states,
            transitions=transitions
        )
        
        # Then: Workflow should auto-advance past completed gather_context
        # If current_action is completed, workflow should transition to next
        if workflow.is_action_completed('gather_context'):
            workflow.transition_to_next()
        
        assert workflow.current_state == 'decide_planning_criteria'


# ============================================================================
# STORY: Inject Guardrails as Part of Clarify Requirements
# ============================================================================

class TestInjectGuardrailsAsPartOfClarifyRequirements:
    """Story: Inject Guardrails as Part of Clarify Requirements - Tests guardrail injection."""

    def test_action_injects_questions_and_evidence(self, bot_directory, workspace_directory):
        bot_name = 'test_bot'
        behavior = 'shape'
        questions = ['What is the scope?', 'Who are the users?']
        evidence = ['Requirements doc', 'User interviews']
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        create_guardrails_files(bot_directory, behavior, questions, evidence)
        
        action_obj = GatherContextAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_questions_and_evidence()
        
        assert 'key_questions' in instructions['guardrails']
        assert instructions['guardrails']['key_questions'] == questions
        assert 'evidence' in instructions['guardrails']
        assert instructions['guardrails']['evidence'] == evidence

    def test_action_uses_base_instructions_when_guardrails_missing(self, bot_directory, workspace_directory):
        bot_name = 'test_bot'
        behavior = 'shape'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        action_obj = GatherContextAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_questions_and_evidence()
        
        assert 'guardrails' not in instructions or instructions['guardrails'] == {}

    def test_action_handles_malformed_guardrails_json(self, bot_directory, workspace_directory):
        bot_name = 'test_bot'
        behavior = 'shape'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        guardrails_dir = bot_directory / 'behaviors' / behavior / 'guardrails' / 'required_context'
        guardrails_dir.mkdir(parents=True, exist_ok=True)
        
        questions_file = guardrails_dir / 'key_questions.json'
        questions_file.write_text('invalid json {')
        
        action_obj = GatherContextAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        
        with pytest.raises(json.JSONDecodeError) as exc_info:
            action_obj.inject_questions_and_evidence()
        
        assert 'key_questions.json' in str(exc_info.value) or 'Expecting' in str(exc_info.value)


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
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Action initialized
        action = GatherContextAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters with clarification data
        parameters = {
            'key_questions_answered': {
                'user_types': 'Game Masters',
                'first_action': 'Group tokens into mobs'
            },
            'evidence_provided': {
                'original_input': 'I want to turn minions into mobs',
                'source_file': 'input.txt'
            }
        }
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: clarification.json file exists
        clarification_file = workspace_directory / 'docs' / 'stories' / 'clarification.json'
        assert clarification_file.exists(), "clarification.json should be created"
        
        # Then: File contains correct structure
        clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
        assert 'shape' in clarification_data
        assert 'key_questions' in clarification_data['shape']
        assert 'evidence' in clarification_data['shape']
        assert clarification_data['shape']['key_questions']['user_types'] == 'Game Masters'
        assert clarification_data['shape']['evidence']['original_input'] == 'I want to turn minions into mobs'

    def test_preserve_existing_clarification_data_when_saving(self, bot_directory, workspace_directory):
        """
        SCENARIO: Preserve existing clarification data when saving
        GIVEN: clarification.json already exists with data for 'discovery' behavior
        AND: gather_context action is initialized for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: clarification.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Existing clarification.json with discovery data
        stories_folder = workspace_directory / 'docs' / 'stories'
        stories_folder.mkdir(parents=True, exist_ok=True)
        clarification_file = stories_folder / 'clarification.json'
        existing_data = {
            'discovery': {
                'key_questions': {'scope': 'Component level'},
                'evidence': {'doc': 'requirements.md'}
            }
        }
        clarification_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
        
        # Given: Action initialized for shape behavior
        action = GatherContextAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters with shape clarification data
        parameters = {
            'key_questions_answered': {'user_types': 'Game Masters'},
            'evidence_provided': {'input': 'input.txt'}
        }
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: Both behaviors' data are preserved
        clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
        assert 'discovery' in clarification_data, "Existing discovery data should be preserved"
        assert 'shape' in clarification_data, "New shape data should be added"
        assert clarification_data['discovery']['key_questions']['scope'] == 'Component level'
        assert clarification_data['shape']['key_questions']['user_types'] == 'Game Masters'

    def test_skip_saving_when_no_clarification_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Skip saving when no clarification parameters are provided
        GIVEN: gather_context action is initialized
        AND: parameters do not contain key_questions_answered or evidence_provided
        WHEN: do_execute is called with empty or unrelated parameters
        THEN: clarification.json file is not created
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Action initialized
        action = GatherContextAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters without clarification data
        parameters = {'other_data': 'some value'}
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: clarification.json file is not created
        clarification_file = workspace_directory / 'docs' / 'stories' / 'clarification.json'
        assert not clarification_file.exists(), "clarification.json should not be created when no clarification data provided"
