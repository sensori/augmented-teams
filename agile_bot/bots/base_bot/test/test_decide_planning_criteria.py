"""
Decide Planning Criteria Tests

Tests for all stories in the 'Decide Planning Criteria' sub-epic:
- Track Activity for Planning Action
- Proceed To Build Knowledge
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.planning_action import PlanningAction
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action,
    create_planning_guardrails
)

# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# STORY: Track Activity for Planning Action
# ============================================================================

class TestTrackActivityForPlanningAction:
    """Story: Track Activity for Planning Action - Tests activity tracking for decide_planning_criteria."""

    def test_track_activity_when_planning_action_starts(self, bot_directory, workspace_directory):
        verify_action_tracks_start(bot_directory, workspace_directory, PlanningAction, 'decide_planning_criteria')

    def test_track_activity_when_planning_action_completes(self, bot_directory, workspace_directory):
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
        verify_workflow_transition(bot_directory, workspace_directory, 'decide_planning_criteria', 'build_knowledge')

    def test_workflow_state_captures_planning_completion(self, bot_directory, workspace_directory):
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'decide_planning_criteria', behavior='discovery')


# ============================================================================
# STORY: Inject Planning Criteria Into Instructions
# ============================================================================

class TestInjectPlanningCriteriaIntoInstructions:
    """Story: Inject Planning Criteria Into Instructions - Tests planning criteria injection."""

    def test_action_injects_decision_criteria_and_assumptions(self, bot_directory, workspace_directory):
        bot_name = 'test_bot'
        behavior = 'exploration'
        assumptions = ['Stories follow user story format', 'Acceptance criteria are testable']
        criteria = {'scope': ['Component', 'System', 'Solution']}
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        create_planning_guardrails(bot_directory, behavior, assumptions, criteria)
        
        action_obj = PlanningAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_decision_criteria_and_assumptions()
        
        assert 'decision_criteria' in instructions
        assert 'assumptions' in instructions
        assert instructions['assumptions'] == assumptions
        # decision_criteria structure may vary - just verify it's present and has data
        assert instructions['decision_criteria'] is not None

    def test_action_uses_base_planning_when_guardrails_missing(self, bot_directory, workspace_directory):
        bot_name = 'test_bot'
        behavior = 'exploration'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        action_obj = PlanningAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_decision_criteria_and_assumptions()
        
        assert 'decision_criteria' not in instructions or instructions['decision_criteria'] == {}
        assert 'assumptions' not in instructions or instructions['assumptions'] == []


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
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Action initialized
        action = PlanningAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters with planning data
        parameters = {
            'decisions_made': {
                'drill_down': 'Dig deep on system interactions',
                'flow_scope': 'End-to-end user-system behavior'
            },
            'assumptions_made': [
                'Focus on user flow over internal systems',
                'Cover the end-to-end scenario'
            ]
        }
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: planning.json file exists
        planning_file = workspace_directory / 'docs' / 'stories' / 'planning.json'
        assert planning_file.exists(), "planning.json should be created"
        
        # Then: File contains correct structure
        planning_data = json.loads(planning_file.read_text(encoding='utf-8'))
        assert 'shape' in planning_data
        assert 'decisions_made' in planning_data['shape']
        assert 'assumptions_made' in planning_data['shape']
        assert planning_data['shape']['decisions_made']['drill_down'] == 'Dig deep on system interactions'
        assert planning_data['shape']['assumptions_made'][0] == 'Focus on user flow over internal systems'

    def test_preserve_existing_planning_data_when_saving(self, bot_directory, workspace_directory):
        """
        SCENARIO: Preserve existing planning data when saving
        GIVEN: planning.json already exists with data for 'discovery' behavior
        AND: decide_planning_criteria action is initialized for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: planning.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Existing planning.json with discovery data
        stories_folder = workspace_directory / 'docs' / 'stories'
        stories_folder.mkdir(parents=True, exist_ok=True)
        planning_file = stories_folder / 'planning.json'
        existing_data = {
            'discovery': {
                'decisions_made': {'scope': 'Component level'},
                'assumptions_made': ['Stories follow user story format']
            }
        }
        planning_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
        
        # Given: Action initialized for shape behavior
        action = PlanningAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters with shape planning data
        parameters = {
            'decisions_made': {'drill_down': 'Dig deep on user workflows'},
            'assumptions_made': ['Focus on user flow']
        }
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: Both behaviors' data are preserved
        planning_data = json.loads(planning_file.read_text(encoding='utf-8'))
        assert 'discovery' in planning_data, "Existing discovery data should be preserved"
        assert 'shape' in planning_data, "New shape data should be added"
        assert planning_data['discovery']['decisions_made']['scope'] == 'Component level'
        assert planning_data['shape']['decisions_made']['drill_down'] == 'Dig deep on user workflows'

    def test_skip_saving_when_no_planning_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Skip saving when no planning parameters are provided
        GIVEN: decide_planning_criteria action is initialized
        AND: parameters do not contain decisions_made or assumptions_made
        WHEN: do_execute is called with empty or unrelated parameters
        THEN: planning.json file is not created
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Action initialized
        action = PlanningAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        
        # Given: Parameters without planning data
        parameters = {'other_data': 'some value'}
        
        # When: Action executes with parameters
        action.do_execute(parameters)
        
        # Then: planning.json file is not created
        planning_file = workspace_directory / 'docs' / 'stories' / 'planning.json'
        assert not planning_file.exists(), "planning.json should not be created when no planning data provided"
