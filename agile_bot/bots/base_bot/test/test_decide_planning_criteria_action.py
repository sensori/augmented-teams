"""
Decide Planning Criteria Action Tests

Tests for all stories in the 'Decide Planning Criteria Action' sub-epic:
- Track Activity for Planning Action
- Proceed To Build Knowledge
- Inject Planning Criteria Into Instructions
- Save Final Assumptions and Decisions
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.planning_action import PlanningAction
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_planning_guardrails,
    given_bot_name_and_behavior_setup
)
from agile_bot.bots.base_bot.test.test_execute_behavior_actions import (
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action
)
# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# HELPER FUNCTIONS - Sub-Epic Level (Used across multiple test classes)
# ============================================================================

def when_action_executes_with_parameters(action, parameters: dict):
    """When: Action executes with parameters."""
    return action.do_execute(parameters)

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

def given_planning_assumptions_and_criteria():
    """Given: Planning assumptions and criteria."""
    assumptions = ['Stories follow user story format', 'Acceptance criteria are testable']
    criteria = {'scope': ['Component', 'System', 'Solution']}
    return assumptions, criteria

def given_planning_parameters_with_decisions_and_assumptions():
    """Given: Planning parameters with decisions and assumptions."""
    return {
        'decisions_made': {
            'drill_down': 'Dig deep on system interactions',
            'flow_scope': 'End-to-end user-system behavior'
        },
        'assumptions_made': [
            'Focus on user flow over internal systems',
            'Cover the end-to-end scenario'
        ]
    }

def given_planning_parameters_for_shape_behavior():
    """Given: Planning parameters for shape behavior."""
    return {
        'decisions_made': {'drill_down': 'Dig deep on user workflows'},
        'assumptions_made': ['Focus on user flow']
    }

def given_discovery_planning_decisions_and_assumptions():
    """Given: Discovery planning decisions and assumptions."""
    decisions = {'scope': 'Component level'}
    assumptions = ['Stories follow user story format']
    return decisions, assumptions

def given_expected_planning_decisions_and_assumptions():
    """Given: Expected planning decisions and assumptions."""
    decisions = {'drill_down': 'Dig deep on system interactions'}
    assumptions = ['Focus on user flow over internal systems', 'Cover the end-to-end scenario']
    return decisions, assumptions

def given_planning_action_is_initialized(bot_directory: Path, bot_name: str, behavior: str):
    """Given step: PlanningAction is initialized."""
    return PlanningAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)

def given_planning_guardrails_exist(bot_directory: Path, behavior: str, assumptions: list, criteria: dict):
    """Given step: Planning guardrails exist."""
    create_planning_guardrails(bot_directory, behavior, assumptions, criteria)

def given_planning_json_exists_with_data(workspace_directory: Path, behavior: str, decisions_made: dict, assumptions_made: list):
    """Given step: planning.json exists with data for behavior."""
    stories_folder = workspace_directory / 'docs' / 'stories'
    stories_folder.mkdir(parents=True, exist_ok=True)
    planning_file = stories_folder / 'planning.json'
    existing_data = {
        behavior: {
            'decisions_made': decisions_made,
            'assumptions_made': assumptions_made
        }
    }
    planning_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
    return planning_file

def when_action_injects_decision_criteria_and_assumptions(action: PlanningAction):
    """When step: Action injects decision criteria and assumptions."""
    return action.inject_decision_criteria_and_assumptions()


def then_instructions_contain_decision_criteria_and_assumptions(instructions: dict, expected_assumptions: list):
    """Then step: Instructions contain decision criteria and assumptions."""
    assert 'decision_criteria' in instructions
    assert 'assumptions' in instructions
    assert instructions['assumptions'] == expected_assumptions
    assert instructions['decision_criteria'] is not None

def then_instructions_do_not_contain_planning_data(instructions: dict):
    """Then step: Instructions do not contain planning data."""
    assert 'decision_criteria' not in instructions or instructions['decision_criteria'] == {}
    assert 'assumptions' not in instructions or instructions['assumptions'] == []

def then_planning_json_file_exists(workspace_directory: Path):
    """Then step: planning.json file exists."""
    planning_file = workspace_directory / 'docs' / 'stories' / 'planning.json'
    assert planning_file.exists(), "planning.json should be created"
    return planning_file

def then_planning_json_file_does_not_exist(workspace_directory: Path):
    """Then step: planning.json file does not exist."""
    planning_file = workspace_directory / 'docs' / 'stories' / 'planning.json'
    assert not planning_file.exists(), "planning.json should not be created when no planning data provided"

def then_planning_data_contains_discovery_scope(planning_data: dict, expected_scope: str):
    """Then: Planning data contains discovery scope."""
    assert planning_data['discovery']['decisions_made']['scope'] == expected_scope

def then_planning_data_contains_shape_drill_down(planning_data: dict, expected_drill_down: str):
    """Then: Planning data contains shape drill down."""
    assert planning_data['shape']['decisions_made']['drill_down'] == expected_drill_down

def then_planning_json_contains_behavior_data(planning_file: Path, behavior: str, expected_decisions: dict = None, expected_assumptions: list = None):
    """Then step: planning.json contains behavior data."""
    planning_data = json.loads(planning_file.read_text(encoding='utf-8'))
    assert behavior in planning_data
    if expected_decisions:
        assert 'decisions_made' in planning_data[behavior]
        for key, value in expected_decisions.items():
            assert planning_data[behavior]['decisions_made'][key] == value
    if expected_assumptions:
        assert 'assumptions_made' in planning_data[behavior]
        assert planning_data[behavior]['assumptions_made'] == expected_assumptions
    return planning_data

def then_planning_json_preserves_existing_behaviors(planning_file: Path, existing_behaviors: list):
    """Then step: planning.json preserves existing behavior data."""
    planning_data = json.loads(planning_file.read_text(encoding='utf-8'))
    for behavior in existing_behaviors:
        assert behavior in planning_data, f"Existing {behavior} data should be preserved"
    return planning_data


def given_environment_bootstrapped_with_planning_guardrails(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped with planning guardrails."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    assumptions, criteria = given_planning_assumptions_and_criteria()
    given_planning_guardrails_exist(bot_directory, behavior, assumptions, criteria)
    action_obj = given_planning_action_is_initialized(bot_directory, bot_name, behavior)
    return bot_name, behavior, assumptions, action_obj


def given_environment_bootstrapped_and_planning_action_initialized(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped and planning action initialized."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    action_obj = given_planning_action_is_initialized(bot_directory, bot_name, behavior)
    return bot_name, behavior, action_obj


def given_environment_action_and_planning_parameters(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and planning parameters."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_planning_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_planning_parameters_with_decisions_and_assumptions()
    return action, parameters


def given_environment_with_existing_planning_and_action(bot_directory: Path, workspace_directory: Path):
    """Given: Environment with existing planning and action."""
    bootstrap_env(bot_directory, workspace_directory)
    discovery_decisions, discovery_assumptions = given_discovery_planning_decisions_and_assumptions()
    planning_file = given_planning_json_exists_with_data(workspace_directory, 'discovery', discovery_decisions, discovery_assumptions)
    action = given_planning_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_planning_parameters_for_shape_behavior()
    return planning_file, action, parameters


def given_environment_action_and_empty_planning_parameters(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and empty planning parameters."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_planning_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = {'other_data': 'some value'}
    return action, parameters

# ============================================================================
# STORY: Track Activity for Planning Action
# ============================================================================

class TestTrackActivityForPlanningAction:
    """Story: Track Activity for Planning Action - Tests activity tracking for decide_planning_criteria."""

    def test_track_activity_when_planning_action_starts(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Planning action starts
        # Then: Activity is tracked (verified by verify_action_tracks_start)
        verify_action_tracks_start(bot_directory, workspace_directory, PlanningAction, 'decide_planning_criteria')

    def test_track_activity_when_planning_action_completes(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Planning action completes with outputs and duration
        # Then: Activity is tracked (verified by verify_action_tracks_completion)
        verify_action_tracks_completion(
            bot_directory,
            workspace_directory, 
            PlanningAction, 
            'decide_planning_criteria',
            outputs={'criteria_count': 3, 'assumptions_count': 2},
            duration=240
        )


# ============================================================================
# STORY: Proceed To Build Knowledge
# ============================================================================

class TestProceedToBuildKnowledge:
    """Story: Proceed To Build Knowledge - Tests transition to build_knowledge action."""

    def test_seamless_transition_from_planning_to_build_knowledge(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Planning action completes
        # Then: Workflow transitions to build_knowledge (verified by verify_workflow_transition)
        verify_workflow_transition(bot_directory, workspace_directory, 'decide_planning_criteria', 'build_knowledge')

    def test_workflow_state_captures_planning_completion(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Planning action completes
        # Then: Workflow state captures completion (verified by verify_workflow_saves_completed_action)
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'decide_planning_criteria', behavior='discovery')


# ============================================================================
# STORY: Inject Planning Criteria Into Instructions
# ============================================================================

class TestInjectPlanningCriteriaIntoInstructions:
    """Story: Inject Planning Criteria Into Instructions - Tests planning criteria injection."""

    def test_action_injects_decision_criteria_and_assumptions(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action Injects Decision Criteria And Assumptions
        """
        # Given: Environment is bootstrapped
        bot_name, behavior, assumptions, action_obj = given_environment_bootstrapped_with_planning_guardrails(bot_directory, workspace_directory)
        
        # When: Action injects decision criteria and assumptions
        instructions = when_action_injects_decision_criteria_and_assumptions(action_obj)
        
        # Then: Instructions contain decision criteria and assumptions
        then_instructions_contain_decision_criteria_and_assumptions(instructions, assumptions)

    def test_action_uses_base_planning_when_guardrails_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action Uses Base Planning When Guardrails Missing
        """
        # Given: Environment is bootstrapped
        bot_name, behavior, action_obj = given_environment_bootstrapped_and_planning_action_initialized(bot_directory, workspace_directory)
        
        # When: Action injects decision criteria and assumptions
        instructions = when_action_injects_decision_criteria_and_assumptions(action_obj)
        
        # Then: Instructions do not contain planning data
        then_instructions_do_not_contain_planning_data(instructions)


# ============================================================================
# STORY: Store Planning Data
# ============================================================================

class TestStorePlanningData:
    """Story: Store Planning Data - Tests that planning data is saved to planning.json."""

    def test_save_planning_data_when_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Save planning data when parameters are provided
        GIVEN: decide_planning_criteria action is initialized
        AND: parameters contain decisions_made and assumptions_made
        WHEN: do_execute is called with these parameters
        THEN: planning.json file is created in docs/stories/ folder
        AND: file contains behavior section with decisions_made and assumptions_made
        """
        # Given: Environment is bootstrapped
        action, parameters = given_environment_action_and_planning_parameters(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: planning.json file exists
        planning_file = then_planning_json_file_exists(workspace_directory)
        expected_decisions, expected_assumptions = given_expected_planning_decisions_and_assumptions()
        then_planning_json_contains_behavior_data(planning_file, 'shape', expected_decisions, expected_assumptions)

    def test_preserve_existing_planning_data_when_saving(self, bot_directory, workspace_directory):
        """
        SCENARIO: Preserve existing planning data when saving
        GIVEN: planning.json already exists with data for 'discovery' behavior
        AND: decide_planning_criteria action is initialized for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: planning.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Environment is bootstrapped
        planning_file, action, parameters = given_environment_with_existing_planning_and_action(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: Both behaviors' data are preserved
        planning_data = then_planning_json_preserves_existing_behaviors(planning_file, ['discovery', 'shape'])
        then_planning_data_contains_discovery_scope(planning_data, 'Component level')
        then_planning_data_contains_shape_drill_down(planning_data, 'Dig deep on user workflows')

    def test_skip_saving_when_no_planning_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Skip saving when no planning parameters are provided
        GIVEN: decide_planning_criteria action is initialized
        AND: parameters do not contain decisions_made or assumptions_made
        WHEN: do_execute is called with empty or unrelated parameters
        THEN: planning.json file is not created
        """
        # Given: Environment is bootstrapped
        action, parameters = given_environment_action_and_empty_planning_parameters(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: planning.json file is not created
        then_planning_json_file_does_not_exist(workspace_directory)
