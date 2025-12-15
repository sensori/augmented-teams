"""
Decide Strategy Criteria Action Tests

Tests for all stories in the 'Decide Strategy Criteria Action' sub-epic:
- Track Activity for Strategy Action
- Proceed To Build Knowledge
- Inject Strategy Criteria Into Instructions
- Save Final Assumptions and Decisions
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.actions.decide_strategy.decide_strategy_action import DecideStrategyAction
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_strategy_guardrails,
    given_bot_name_and_behavior_setup,
    create_actions_workflow_json
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

def given_strategy_assumptions_and_criteria():
    """Given: Strategy assumptions and criteria."""
    assumptions = ['Stories follow user story format', 'Acceptance criteria are testable']
    criteria = {'scope': ['Component', 'System', 'Solution']}
    return assumptions, criteria

def given_strategy_parameters_with_decisions_and_assumptions():
    """Given: Strategy parameters with decisions and assumptions."""
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

def given_strategy_parameters_for_shape_behavior():
    """Given: Strategy parameters for shape behavior."""
    return {
        'decisions_made': {'drill_down': 'Dig deep on user workflows'},
        'assumptions_made': ['Focus on user flow']
    }

def given_discovery_strategy_decisions_and_assumptions():
    """Given: Discovery strategy decisions and assumptions."""
    decisions = {'scope': 'Component level'}
    assumptions = ['Stories follow user story format']
    return decisions, assumptions

def given_expected_strategy_decisions_and_assumptions():
    """Given: Expected strategy decisions and assumptions."""
    decisions = {'drill_down': 'Dig deep on system interactions'}
    assumptions = ['Focus on user flow over internal systems', 'Cover the end-to-end scenario']
    return decisions, assumptions

def given_strategy_action_is_initialized(bot_directory: Path, bot_name: str, behavior_name: str):
    """Given step: DecideStrategyAction is initialized."""
    # Create bot_paths
    bot_paths = BotPaths(bot_directory=bot_directory)
    
    # Ensure behavior.json exists
    import json
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    if not behavior_file.exists():
        behavior_config = {
            "behaviorName": behavior_name,
            "description": f"Test behavior: {behavior_name}",
            "goal": f"Test goal for {behavior_name}",
            "inputs": "Test inputs",
            "outputs": "Test outputs",
            "instructions": {},
            "actions_workflow": {
                "actions": [
                    {'name': 'decide_strategy', 'order': 1}
                ]
            }
        }
        behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    # Create Behavior object
    behavior = Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)
    
    # Create StrategyAction with new signature
    from agile_bot.bots.base_bot.src.bot.base_action_config import BaseActionConfig
    base_action_config = BaseActionConfig('decide_strategy', bot_paths)
    
    return DecideStrategyAction(
        base_action_config=base_action_config,
        behavior=behavior,
        activity_tracker=None
    )

def given_strategy_guardrails_exist(bot_directory: Path, behavior: str, assumptions: list, criteria: dict):
    """Given step: Strategy guardrails exist."""
    create_strategy_guardrails(bot_directory, behavior, assumptions, criteria)

def given_strategy_json_exists_with_data(workspace_directory: Path, behavior: str, decisions_made: dict, assumptions_made: list, bot_paths: BotPaths = None):
    """Given step: strategy.json exists with data for behavior."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        stories_folder = workspace_directory / 'docs' / 'stories'
    else:
        documentation_path = bot_paths.documentation_path
        stories_folder = workspace_directory / documentation_path
    stories_folder.mkdir(parents=True, exist_ok=True)
    strategy_file = stories_folder / 'strategy.json'
    # New structure: strategy_criteria has 'criteria' and 'decisions_made', assumptions has 'typical_assumptions' and 'assumptions_made'
    existing_data = {
        behavior: {
            'strategy_criteria': {
                'criteria': {},
                'decisions_made': decisions_made
            },
            'assumptions': {
                'typical_assumptions': [],
                'assumptions_made': assumptions_made
            },
            'recommended_activities': []
        }
    }
    strategy_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
    return strategy_file

def when_action_injects_strategy_criteria_and_assumptions(action: DecideStrategyAction):
    """When step: Action injects decision criteria and assumptions."""
    # Call do_execute to get instructions with planning criteria injected
    result = action.do_execute({})
    instructions = result.get('instructions', {})
    # Return just the strategy criteria portion for testing
    return {
        'strategy_criteria': instructions.get('strategy_criteria', {}),
        'assumptions': instructions.get('assumptions', []),
        'recommended_activities': instructions.get('recommended_activities', [])
    }


def then_instructions_contain_strategy_criteria_and_assumptions(instructions: dict, expected_assumptions: list):
    """Then step: Instructions contain strategy criteria and assumptions."""
    assert 'strategy_criteria' in instructions
    assert 'assumptions' in instructions
    assert instructions['assumptions'] == expected_assumptions
    assert instructions['strategy_criteria'] is not None

def then_instructions_do_not_contain_strategy_data(instructions: dict):
    """Then step: Instructions do not contain strategy data."""
    assert 'strategy_criteria' not in instructions or instructions['strategy_criteria'] == {}
    assert 'assumptions' not in instructions or instructions['assumptions'] == []

def then_strategy_json_file_exists(workspace_directory: Path, bot_paths: BotPaths = None):
    """Then step: strategy.json file exists."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        strategy_file = workspace_directory / 'docs' / 'stories' / 'strategy.json'
    else:
        documentation_path = bot_paths.documentation_path
        strategy_file = workspace_directory / documentation_path / 'strategy.json'
    assert strategy_file.exists(), f"strategy.json should be created at {strategy_file}"
    return strategy_file

def then_strategy_json_file_does_not_exist(workspace_directory: Path, bot_paths: BotPaths = None):
    """Then step: strategy.json file does not exist."""
    if bot_paths is None:
        # Fallback to default path for backward compatibility
        strategy_file = workspace_directory / 'docs' / 'stories' / 'strategy.json'
    else:
        documentation_path = bot_paths.documentation_path
        strategy_file = workspace_directory / documentation_path / 'strategy.json'
    assert not strategy_file.exists(), f"strategy.json should not be created at {strategy_file} when no strategy data provided"

def then_strategy_data_contains_discovery_scope(strategy_data: dict, expected_scope: str):
    """Then: Strategy data contains discovery scope."""
    assert strategy_data['discovery']['strategy_criteria']['decisions_made']['scope'] == expected_scope

def then_strategy_data_contains_shape_drill_down(strategy_data: dict, expected_drill_down: str):
    """Then: Strategy data contains shape drill down."""
    assert strategy_data['shape']['strategy_criteria']['decisions_made']['drill_down'] == expected_drill_down

def then_strategy_json_contains_behavior_data(strategy_file: Path, behavior: str, expected_decisions: dict = None, expected_assumptions: list = None):
    """Then step: strategy.json contains behavior data."""
    strategy_data = json.loads(strategy_file.read_text(encoding='utf-8'))
    assert behavior in strategy_data
    if expected_decisions:
        # New structure: strategy_criteria has 'criteria' and 'decisions_made'
        assert 'strategy_criteria' in strategy_data[behavior]
        assert 'decisions_made' in strategy_data[behavior]['strategy_criteria']
        for key, value in expected_decisions.items():
            assert strategy_data[behavior]['strategy_criteria']['decisions_made'][key] == value
    if expected_assumptions:
        # New structure: assumptions has 'typical_assumptions' and 'assumptions_made'
        assert 'assumptions' in strategy_data[behavior]
        assert 'assumptions_made' in strategy_data[behavior]['assumptions']
        assert strategy_data[behavior]['assumptions']['assumptions_made'] == expected_assumptions
    return strategy_data

def then_strategy_json_preserves_existing_behaviors(strategy_file: Path, existing_behaviors: list):
    """Then step: strategy.json preserves existing behavior data."""
    strategy_data = json.loads(strategy_file.read_text(encoding='utf-8'))
    for behavior in existing_behaviors:
        assert behavior in strategy_data, f"Existing {behavior} data should be preserved"
    return strategy_data


def given_environment_bootstrapped_with_strategy_guardrails(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped with strategy guardrails."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    assumptions, criteria = given_strategy_assumptions_and_criteria()
    given_strategy_guardrails_exist(bot_directory, behavior, assumptions, criteria)
    action_obj = given_strategy_action_is_initialized(bot_directory, bot_name, behavior)
    return bot_name, behavior, assumptions, action_obj


def given_environment_bootstrapped_and_strategy_action_initialized(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped and strategy action initialized."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_name, behavior = given_bot_name_and_behavior_setup()
    action_obj = given_strategy_action_is_initialized(bot_directory, bot_name, behavior)
    return bot_name, behavior, action_obj


def given_environment_action_and_strategy_parameters(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and strategy parameters."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_strategy_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_strategy_parameters_with_decisions_and_assumptions()
    bot_paths = BotPaths(bot_directory=bot_directory)
    return action, parameters, bot_paths


def given_environment_with_existing_strategy_and_action(bot_directory: Path, workspace_directory: Path):
    """Given: Environment with existing strategy and action."""
    bootstrap_env(bot_directory, workspace_directory)
    bot_paths = BotPaths(bot_directory=bot_directory)
    discovery_decisions, discovery_assumptions = given_discovery_strategy_decisions_and_assumptions()
    strategy_file = given_strategy_json_exists_with_data(workspace_directory, 'discovery', discovery_decisions, discovery_assumptions, bot_paths)
    action = given_strategy_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = given_strategy_parameters_for_shape_behavior()
    return strategy_file, action, parameters, bot_paths


def given_environment_action_and_empty_strategy_parameters(bot_directory: Path, workspace_directory: Path):
    """Given: Environment, action and empty strategy parameters."""
    bootstrap_env(bot_directory, workspace_directory)
    action = given_strategy_action_is_initialized(bot_directory, 'story_bot', 'shape')
    parameters = {'other_data': 'some value'}
    bot_paths = BotPaths(bot_directory=bot_directory)
    return action, parameters, bot_paths

# ============================================================================
# STORY: Track Activity for Strategy Action
# ============================================================================

class TestTrackActivityForStrategyAction:
    """Story: Track Activity for Strategy Action - Tests activity tracking for decide_strategy."""

    def test_track_activity_when_strategy_action_starts(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Strategy action starts
        # Then: Activity is tracked (verified by verify_action_tracks_start)
        verify_action_tracks_start(bot_directory, workspace_directory, DecideStrategyAction, 'decide_strategy')

    def test_track_activity_when_strategy_action_completes(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Strategy action completes with outputs and duration
        # Then: Activity is tracked (verified by verify_action_tracks_completion)
        verify_action_tracks_completion(
            bot_directory,
            workspace_directory, 
            DecideStrategyAction, 
            'decide_strategy',
            outputs={'criteria_count': 3, 'assumptions_count': 2},
            duration=240
        )


# ============================================================================
# STORY: Proceed To Build Knowledge
# ============================================================================

class TestProceedToBuildKnowledge:
    """Story: Proceed To Build Knowledge - Tests transition to build_knowledge action."""

    def test_seamless_transition_from_strategy_to_build_knowledge(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Strategy action completes
        # Then: Workflow transitions to build_knowledge (verified by verify_workflow_transition)
        verify_workflow_transition(bot_directory, workspace_directory, 'decide_strategy', 'build_knowledge')

    def test_workflow_state_captures_strategy_completion(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Strategy action completes
        # Then: Workflow state captures completion (verified by verify_workflow_saves_completed_action)
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'decide_strategy', behavior='discovery')


# ============================================================================
# STORY: Inject Strategy Criteria Into Instructions
# ============================================================================

class TestInjectStrategyIntoInstructions:
    """Story: Inject Strategy Into Instructions - Tests strategy injection."""

    def test_action_injects_decision_criteria_and_assumptions(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action Injects Decision Criteria And Assumptions
        """
        # Given: Environment is bootstrapped
        bot_name, behavior, assumptions, action_obj = given_environment_bootstrapped_with_strategy_guardrails(bot_directory, workspace_directory)
        
        # When: Action injects strategy criteria and assumptions
        instructions = when_action_injects_strategy_criteria_and_assumptions(action_obj)
        
        # Then: Instructions contain strategy criteria and assumptions
        then_instructions_contain_strategy_criteria_and_assumptions(instructions, assumptions)

    def test_action_uses_base_strategy_when_guardrails_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action Uses Base Strategy When Guardrails Missing
        """
        # Given: Environment is bootstrapped
        bot_name, behavior, action_obj = given_environment_bootstrapped_and_strategy_action_initialized(bot_directory, workspace_directory)
        
        # When: Action injects strategy criteria and assumptions
        instructions = when_action_injects_strategy_criteria_and_assumptions(action_obj)
        
        # Then: Instructions do not contain strategy data
        then_instructions_do_not_contain_strategy_data(instructions)


# ============================================================================
# STORY: Store Planning Data
# ============================================================================

class TestStoreStrategyData:
    """Story: Store Strategy Data - Tests that strategy data is saved to strategy.json."""

    def test_save_strategy_data_when_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Save strategy data when parameters are provided
        GIVEN: decide_strategy action is initialized
        AND: parameters contain decisions_made and assumptions_made
        WHEN: do_execute is called with these parameters
        THEN: strategy.json file is created in docs/stories/ folder
        AND: file contains behavior section with decisions_made and assumptions_made
        """
        # Given: Environment is bootstrapped
        action, parameters, bot_paths = given_environment_action_and_strategy_parameters(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: strategy.json file exists
        strategy_file = then_strategy_json_file_exists(workspace_directory, bot_paths)
        expected_decisions, expected_assumptions = given_expected_strategy_decisions_and_assumptions()
        then_strategy_json_contains_behavior_data(strategy_file, 'shape', expected_decisions, expected_assumptions)

    def test_preserve_existing_strategy_data_when_saving(self, bot_directory, workspace_directory):
        """
        SCENARIO: Preserve existing strategy data when saving
        GIVEN: strategy.json already exists with data for 'discovery' behavior
        AND: decide_strategy action is initialized for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: strategy.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Environment is bootstrapped
        strategy_file, action, parameters, bot_paths = given_environment_with_existing_strategy_and_action(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: Both behaviors' data are preserved
        strategy_data = then_strategy_json_preserves_existing_behaviors(strategy_file, ['discovery', 'shape'])
        then_strategy_data_contains_discovery_scope(strategy_data, 'Component level')
        then_strategy_data_contains_shape_drill_down(strategy_data, 'Dig deep on user workflows')

    def test_skip_saving_when_no_strategy_parameters_provided(self, bot_directory, workspace_directory):
        """
        SCENARIO: Skip saving when no strategy parameters are provided
        GIVEN: decide_strategy action is initialized
        AND: parameters do not contain decisions_made or assumptions_made
        WHEN: do_execute is called with empty or unrelated parameters
        THEN: strategy.json file is not created
        """
        # Given: Environment is bootstrapped
        action, parameters, bot_paths = given_environment_action_and_empty_strategy_parameters(bot_directory, workspace_directory)
        
        # When: Action executes with parameters
        when_action_executes_with_parameters(action, parameters)
        
        # Then: strategy.json file is not created
        then_strategy_json_file_does_not_exist(workspace_directory, bot_paths)
