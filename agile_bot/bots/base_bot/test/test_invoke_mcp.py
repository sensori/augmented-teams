"""
Invoke MCP Tool Tests

Tests for 'Invoke Bot Tool' sub-epic and 'Perform Behavior Action' sub-epic:

Foundational Tests (Increment 1/2):
- Bot Tool Invocation
- Behavior Action Instructions

Increment 3 Tests:
- Forward To Current Behavior and Current Action
- Forward To Current Action
- Activity Logged To Workspace Area Not Bot Area

Uses transitions state machine for workflow state management.
"""
import pytest
from pathlib import Path
import json
from conftest import create_bot_config_file, create_workflow_state_file
from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_behavior_action_instructions, create_actions_workflow_json
from agile_bot.bots.base_bot.test.test_helpers import (
    create_base_action_instructions,
    given_bot_instance_created,
    create_base_instructions
)
# Removed duplicate create_workflow_state - use conftest.create_workflow_state_file instead

# ============================================================================
# HELPER FUNCTIONS - Sub-Epic Level (Used across multiple test classes)
# ============================================================================

def given_base_actions_structure_created(bot_directory):
    """Given: Base actions structure created."""
    return create_bot_config_file(
        bot_directory,
        'test_bot',
        ['shape', 'discovery', 'exploration', 'specification']
    )

# Removed duplicate - imported from test_helpers
from agile_bot.bots.base_bot.test.test_helpers import create_behavior_action_instructions

def create_behavior_action_instructions_from_workspace(workspace: Path, bot_name: str, behavior: str, action: str) -> Path:
    """Helper: Create behavior action instructions file from workspace root.
    
    Wrapper around test_helpers.create_behavior_action_instructions that takes workspace and bot_name.
    """
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    return create_behavior_action_instructions(bot_dir, behavior, action)

# Use shared helper from test_helpers - imported above


def given_behavior_action_instructions_for_multiple_behaviors(workspace_root: Path, bot_name: str, behaviors: list, action: str):
    """Given: Behavior action instructions for multiple behaviors."""
    for behavior in behaviors:
        create_behavior_action_instructions_from_workspace(workspace_root, bot_name, behavior, action)


def given_behavior_json_files_for_behaviors(bot_directory: Path, behaviors: list):
    """Given: Behavior.json files for behaviors."""
    for behavior in behaviors:
        create_actions_workflow_json(bot_directory, behavior)


def given_base_action_instructions_created(bot_directory: Path, action: str):
    """Given: Base action instructions created."""
    from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
    repo_root = get_python_workspace_root()
    return create_base_action_instructions(bot_directory, action)


# Removed given_bot_instance_created - use test_helpers.given_bot_instance_created instead


def then_bot_result_has_status_and_behavior_and_action(result, expected_status: str, expected_behavior: str, expected_action: str):
    """Then: Bot result has correct status, behavior, and action."""
    assert result.status == expected_status
    assert result.behavior == expected_behavior
    assert result.action == expected_action


def then_bot_result_has_behavior_and_action(result, expected_behavior: str, expected_action: str):
    """Then: Bot result has correct behavior and action."""
    assert result.behavior == expected_behavior
    assert result.action == expected_action


def given_knowledge_graph_setup_for_behaviors(workspace_root: Path, bot_name: str, behavior_mapping: dict, action: str):
    """Given: Knowledge graph setup for behaviors."""
    behaviors_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors'
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    for behavior, prefixed_name in behavior_mapping.items():
        behavior_dir = behaviors_dir / prefixed_name
        behavior_dir.mkdir(parents=True, exist_ok=True)
        create_actions_workflow_json(bot_dir, prefixed_name)
        kg_dir = behavior_dir / 'content' / 'knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        template_filename = 'test_template.json'
        kg_config = {'template': template_filename}
        (kg_dir / 'build_story_graph_outline.json').write_text(
            json.dumps(kg_config), encoding='utf-8'
        )
        template_content = {'instructions': ['Test knowledge graph template']}
        (kg_dir / template_filename).write_text(
            json.dumps(template_content), encoding='utf-8'
        )




def given_workflow_state_created(workspace_directory: Path, current_behavior: str, current_action: str):
    """Given: Workflow state created."""
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': current_behavior,
        'current_action': current_action,
        'completed_actions': []
    }), encoding='utf-8')
    return workflow_file


def given_base_instructions_created(bot_directory: Path):
    """Given: Base instructions created."""
    from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
    repo_root = get_python_workspace_root()
    create_base_instructions(bot_directory)


def given_bot_config_and_behavior_workflow(bot_directory: Path, bot_name: str, behaviors: list):
    """Given: Bot config and behavior workflow created."""
    bot_config = create_bot_config_file(bot_directory, bot_name, behaviors)
    given_behavior_json_files_for_behaviors(bot_directory, behaviors)
    return bot_config


def then_workflow_state_file_exists(workspace_directory: Path):
    """Then: Workflow state file exists."""
    workflow_file = workspace_directory / 'workflow_state.json'
    assert workflow_file.exists(), "Workflow state should be created"
    return workflow_file


def then_workflow_state_has_correct_values(workflow_file: Path, expected_behavior: str, expected_action: str):
    """Then: Workflow state has correct values."""
    state_data = json.loads(workflow_file.read_text())
    assert state_data['current_behavior'] == expected_behavior
    assert state_data['current_action'] == expected_action


def given_activity_tracker_created(workspace_directory: Path, bot_name: str):
    """Given: Activity tracker created."""
    from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker
    return ActivityTracker(workspace_directory=workspace_directory, bot_name=bot_name)


def when_activity_tracker_tracks_start(tracker, bot_name: str, behavior: str, action: str):
    """When: Activity tracker tracks start."""
    tracker.track_start(bot_name, behavior, action)


def then_activity_log_exists_at_path(expected_path: Path):
    """Then: Activity log exists at expected path."""
    assert expected_path.exists(), f"Activity log should be at {expected_path}"


def then_activity_log_does_not_exist_at_path(unexpected_path: Path):
    """Then: Activity log does not exist at unexpected path."""
    assert not unexpected_path.exists(), f"Activity log should NOT be at {unexpected_path}"


def then_activity_log_has_entry_with_action_state(workspace_directory: Path, expected_action_state: str, expected_status: str = 'started'):
    """Then: Activity log has entry with expected action_state."""
    then_activity_log_has_single_entry(workspace_directory, expected_action_state, expected_status)


def then_activity_log_has_single_entry(workspace_directory: Path, expected_action_state: str, expected_status: str):
    """Then: Activity log has single entry with expected values."""
    from tinydb import TinyDB
    log_file = workspace_directory / 'activity_log.json'
    with TinyDB(log_file) as db:
        entries = db.all()
        assert len(entries) == 1
        assert entries[0]['action_state'] == expected_action_state
        assert entries[0]['status'] == expected_status


def given_bot_name_behavior_and_action_setup():
    """Given: Bot name, behavior and action setup."""
    bot_name = 'test_bot'
    behavior = 'shape'
    action = 'gather_context'
    return bot_name, behavior, action


def when_create_gather_context_action(bot_name: str, behavior: str, bot_directory: Path):
    """When: Create gather context action."""
    action_obj = GatherContextAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )
    return action_obj


def when_load_and_merge_instructions(action_obj):
    """When: Load and merge instructions."""
    return action_obj.load_and_merge_instructions()


def then_merged_instructions_contain_base_and_action(merged_instructions, action: str):
    """Then: Merged instructions contain base and action."""
    assert 'base_instructions' in merged_instructions
    assert merged_instructions['action'] == action


def given_environment_and_base_instructions(bot_directory: Path, workspace_directory: Path):
    """Given: Environment and base instructions."""
    bootstrap_env(bot_directory, workspace_directory)
    given_base_instructions_created(bot_directory)


def when_create_bot_with_config(bot_name: str, bot_directory: Path, bot_config: Path):
    """When: Create bot with config."""
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    bot = Bot(
        bot_name=bot_name,
        bot_directory=bot_directory,
        config_path=bot_config
    )
    return bot


def then_workflow_state_does_not_exist(workspace_directory: Path):
    """Then: Workflow state does not exist."""
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists(), "Workflow state should not exist yet"
    return workflow_file


def then_result_action_matches_expected(result, expected_action: str):
    """Then: Result action matches expected."""
    assert result.action == expected_action


class TestInvokeBotTool:
    """Story: Invoke Bot Tool - Tests bot tool invocation behavior."""

    def test_tool_invokes_behavior_action_when_called(self, bot_directory, workspace_directory, bot_config_file_path):
        """
        SCENARIO: Tool Invokes Behavior Action When Called
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: AI Chat invokes tool with parameters
        THEN: Tool routes to test_bot.Shape.GatherContext() method
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Bot configuration and instructions exist
        workspace_root = workspace_directory.parent
        create_behavior_action_instructions_from_workspace(workspace_root, 'test_bot', 'shape', 'gather_context')
        given_behavior_json_files_for_behaviors(bot_directory, ['shape', 'discovery', 'exploration', 'specification'])
        given_base_action_instructions_created(bot_directory, 'gather_context')
        
        # When: Call REAL Bot API
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config_file_path)
        action_result = bot.shape.gather_context()
        
        # Then: Tool executed and returned result
        then_bot_result_has_status_and_behavior_and_action(action_result, 'completed', 'shape', 'gather_context')

    def test_tool_routes_to_correct_behavior_action_method(self, bot_directory, workspace_directory, bot_config_file_path):
        """
        SCENARIO: Tool Routes To Correct Behavior Action Method
        GIVEN: Bot has multiple behaviors with build_knowledge action
        WHEN: AI Chat invokes 'test_bot_exploration_build_knowledge'
        THEN: Tool routes to test_bot.Exploration.BuildKnowledge() not other behaviors
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Multiple behaviors exist
        workspace_root = workspace_directory.parent
        given_behavior_action_instructions_for_multiple_behaviors(
            workspace_root, 'test_bot', ['shape', 'discovery', 'exploration'], 'build_knowledge'
        )
        behavior_mapping = {'shape': '1_shape', 'discovery': '4_discovery', 'exploration': '5_exploration'}
        given_knowledge_graph_setup_for_behaviors(workspace_root, 'test_bot', behavior_mapping, 'build_knowledge')
        given_base_action_instructions_created(bot_directory, 'build_knowledge')
        given_base_actions_structure_created(bot_directory)
        create_bot_config_file(bot_directory, 'test_bot', ['shape', 'discovery', 'exploration'])
        given_workflow_state_created(workspace_directory, 'test_bot.exploration', 'test_bot.exploration.build_knowledge')
        
        # When: Call REAL Bot API for specific behavior
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config_file_path)
        action_result = bot.exploration.build_knowledge()
        
        # Then: Routes to exploration behavior only
        then_bot_result_has_behavior_and_action(action_result, 'exploration', 'build_knowledge')


class TestLoadAndMergeBehaviorActionInstructions:
    """Story: Load And Merge Behavior Action Instructions - Tests instruction loading and merging."""

    def test_action_loads_and_merges_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action Loads And Merges Instructions
        GIVEN: Base and behavior-specific instructions exist
        WHEN: Action method is invoked
        THEN: Instructions are loaded from both locations and merged
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Both instruction files exist
        bot_name, behavior, action = given_bot_name_behavior_and_action_setup()
        workspace_root = workspace_directory.parent
        config_file = create_bot_config_file(bot_directory, bot_name, ['shape'])
        behavior_instructions = create_behavior_action_instructions_from_workspace(workspace_root, bot_name, behavior, action)
        base_instructions = given_base_action_instructions_created(bot_directory, action)
        
        # When: Call REAL GatherContextAction API
        action_obj = when_create_gather_context_action(bot_name, behavior, bot_directory)
        merged_instructions = when_load_and_merge_instructions(action_obj)
        
        # Then: Instructions merged from both sources
        then_merged_instructions_contain_base_and_action(merged_instructions, action)


class TestForwardToCurrentBehaviorAndCurrentAction:
    """Story: Forward To Current Behavior and Current Action - Tests bot tool forwarding to behavior and action."""

    def test_bot_tool_forwards_to_current_behavior_and_current_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Bot tool forwards to current behavior and current action
        GIVEN: workflow state shows current_behavior='discovery', current_action='build_knowledge'
        WHEN: Bot tool receives invocation
        THEN: Bot tool forwards to correct behavior and action
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given
        given_base_instructions_created(bot_directory)
        bot_config = given_bot_config_and_behavior_workflow(bot_directory, 'test_bot', ['discovery'])
        
        # When
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
        bot_response = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        then_bot_result_has_behavior_and_action(bot_response, 'discovery', 'gather_context')

    def test_bot_tool_defaults_to_first_behavior_and_first_action_when_state_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Bot tool defaults to first behavior and first action when state missing
        GIVEN: workflow state does NOT exist
        WHEN: Bot tool receives invocation
        THEN: Bot tool defaults to first behavior and first action
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given
        given_base_instructions_created(bot_directory)
        bot_config = given_bot_config_and_behavior_workflow(bot_directory, 'test_bot', ['shape', 'discovery'])
        
        # When
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
        bot_response = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        then_bot_result_has_behavior_and_action(bot_response, 'shape', 'gather_context')


class TestForwardToCurrentAction:
    """Story: Forward To Current Action - Tests behavior tool forwarding to current action."""

    def test_behavior_tool_forwards_to_current_action_within_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Behavior tool forwards to current action within behavior
        GIVEN: a behavior tool for 'discovery' behavior
        AND: workflow state shows current_action='build_knowledge'
        WHEN: Behavior tool receives invocation
        THEN: Behavior tool forwards to build_knowledge action
        """
        # Given
        bootstrap_env(bot_directory, workspace_directory)
        given_base_instructions_created(bot_directory)
        bot_config = given_bot_config_and_behavior_workflow(bot_directory, 'test_bot', ['discovery'])
        
        # When
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
        action_result = bot.discovery.forward_to_current_action()
        
        # Then
        then_result_action_matches_expected(action_result, 'gather_context')

    def test_behavior_tool_sets_workflow_to_current_behavior_when_state_shows_different_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Behavior tool sets workflow to current behavior when state shows different behavior
        GIVEN: a behavior tool for 'exploration' behavior
        AND: workflow state shows current_behavior='discovery'
        WHEN: Behavior tool receives invocation
        THEN: workflow state updated to current_behavior='exploration'
        """
        # Given
        bootstrap_env(bot_directory, workspace_directory)
        given_base_instructions_created(bot_directory)
        bot_config = given_bot_config_and_behavior_workflow(bot_directory, 'test_bot', ['discovery', 'exploration'])
        
        # When
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
        action_result = bot.exploration.forward_to_current_action()
        
        # Then
        assert action_result.behavior == 'exploration'

    def test_behavior_tool_defaults_to_first_action_when_state_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Behavior tool defaults to first action when state missing
        GIVEN: a behavior tool for 'shape' behavior
        AND: workflow state does NOT exist
        WHEN: Behavior tool receives invocation
        THEN: Behavior tool defaults to first action
        """
        # Given
        bootstrap_env(bot_directory, workspace_directory)
        given_base_instructions_created(bot_directory)
        bot_config = given_bot_config_and_behavior_workflow(bot_directory, 'test_bot', ['shape'])
        
        # When
        bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
        action_result = bot.shape.forward_to_current_action()
        
        # Then
        then_result_action_matches_expected(action_result, 'gather_context')
    
    def test_action_called_directly_saves_workflow_state(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action called directly saves workflow state
        GIVEN: Bot is initialized with WORKING_AREA set
        AND: No workflow state exists yet
        WHEN: Action is called directly (e.g., bot.shape.gather_context())
        THEN: workflow_state.json is created with current_behavior and current_action
        AND: This ensures state is saved whether action is called via forward or directly
        """
        # Bootstrap environment
        given_environment_and_base_instructions(bot_directory, workspace_directory)
        
        # Given
        bot_config = create_bot_config_file(bot_directory, 'test_bot', ['shape'])
        # Create behavior.json file (REQUIRED after refactor)
        create_actions_workflow_json(bot_directory, 'shape')
        
        # When
        bot = when_create_bot_with_config('test_bot', bot_directory, bot_config)
        
        # Verify no workflow state exists yet
        workflow_file = then_workflow_state_does_not_exist(workspace_directory)
        
        # Call gather_context DIRECTLY (not via forward_to_current_action)
        action_result = bot.shape.gather_context()
        
        # Then
        workflow_file = then_workflow_state_file_exists(workspace_directory)
        then_workflow_state_has_correct_values(workflow_file, 'test_bot.shape', 'test_bot.shape.gather_context')
        then_result_action_matches_expected(action_result, 'gather_context')


class TestTrackActivityForWorkspace:
    """Story: Activity Logged To Workspace Area Not Bot Area - Tests that activity is tracked in the correct workspace_area location."""

    def test_activity_logged_to_workspace_area_not_bot_area(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity logged to workspace_area not bot area
        GIVEN: WORKING_AREA environment variable specifies workspace_area
        AND: action 'gather_context' executes
        WHEN: Activity logger creates entry
        THEN: Activity log file is at: workspace_area/activity_log.json
        AND: Activity log is NOT at: agile_bot/bots/story_bot/activity_log.json
        AND: Activity log location matches workspace_area from WORKING_AREA environment variable
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Activity tracker tracks activity
        tracker = given_activity_tracker_created(workspace_directory, 'story_bot')
        when_activity_tracker_tracks_start(tracker, 'story_bot', 'shape', 'gather_context')
        
        # Then: Activity log exists in workspace area (no workspace_area subdirectory)
        expected_log = workspace_directory / 'activity_log.json'
        then_activity_log_exists_at_path(expected_log)
        
        # And: Activity log does NOT exist in bot's area
        bot_area_log = bot_directory / 'activity_log.json'
        then_activity_log_does_not_exist_at_path(bot_area_log)

    def test_activity_log_contains_correct_entry(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity log contains correct entry
        GIVEN: action 'gather_context' executes in behavior 'discovery'
        WHEN: Activity logger creates entry
        THEN: Activity log entry includes:
          - action_state='test_bot.discovery.gather_context'
          - timestamp
          - Full path includes bot_name.behavior.action
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Activity tracker tracks activity
        tracker = given_activity_tracker_created(workspace_directory, 'test_bot')
        when_activity_tracker_tracks_start(tracker, 'test_bot', 'shape', 'gather_context')
        
        # Then: Activity log has entry
        then_activity_log_has_entry_with_action_state(workspace_directory, 'test_bot.shape.gather_context', 'started')

