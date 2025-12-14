"""
Invoke Bot Tool Tests

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
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_base_action_instructions
from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_base_instructions(bot_directory: Path):
    """Helper: Create base instructions for all actions in bot_directory (no fallback)."""
    base_actions_dir = bot_directory / 'base_actions'
    action_prefixes = {
        'gather_context': '1_gather_context',
        'decide_planning_criteria': '2_decide_planning_criteria',
        'build_knowledge': '3_build_knowledge',
        'render_output': '4_render_output',
        'validate_rules': '5_validate_rules'
    }
    for action, folder_name in action_prefixes.items():
        action_dir = base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(
            json.dumps({'actionName': action, 'instructions': [f'Instruction for {action}']}),
            encoding='utf-8'
        )

# Removed duplicate create_workflow_state - use conftest.create_workflow_state_file instead

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def bot_directory(tmp_path):
    """Fixture: Bot directory for test bot."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'test_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir

@pytest.fixture
def test_bot_config(bot_directory):
    """Fixture: Test bot configuration."""
    return create_bot_config_file(
        bot_directory,
        'test_bot',
        ['shape', 'discovery', 'exploration', 'specification']
    )

def create_behavior_action_instructions(workspace: Path, bot_name: str, behavior: str, action: str) -> Path:
    """Helper: Create behavior action instructions file."""
    instructions_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    instructions_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = instructions_dir / 'instructions.json'
    instructions_data = {
        'action': action,
        'behavior': behavior,
        'instructions': [f'{action} instructions for {behavior}']
    }
    instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
    return instructions_file

# Use shared helper from test_helpers - imported above


def given_behavior_action_instructions_for_multiple_behaviors(workspace_root: Path, bot_name: str, behaviors: list, action: str):
    """Given: Behavior action instructions for multiple behaviors."""
    for behavior in behaviors:
        create_behavior_action_instructions(workspace_root, bot_name, behavior, action)


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


def given_base_actions_structure_created(bot_directory: Path):
    """Given: Base actions structure created."""
    from agile_bot.bots.base_bot.test.conftest import create_base_actions_structure
    create_base_actions_structure(bot_directory)


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
    from tinydb import TinyDB
    log_file = workspace_directory / 'activity_log.json'
    with TinyDB(log_file) as db:
        entries = db.all()
        assert len(entries) == 1
        assert entries[0]['action_state'] == expected_action_state
        assert entries[0]['status'] == expected_status


class TestInvokeBotTool:
    """Story: Invoke Bot Tool - Tests bot tool invocation behavior."""

    def test_tool_invokes_behavior_action_when_called(self, bot_directory, workspace_directory, test_bot_config):
        """
        SCENARIO: AI Chat invokes test_bot_shape_gather_context tool
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: AI Chat invokes tool with parameters
        THEN: Tool routes to test_bot.Shape.GatherContext() method
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Bot configuration and instructions exist
        workspace_root = workspace_directory.parent
        create_behavior_action_instructions(workspace_root, 'test_bot', 'shape', 'gather_context')
        given_behavior_json_files_for_behaviors(bot_directory, ['shape', 'discovery', 'exploration', 'specification'])
        given_base_action_instructions_created(bot_directory, 'gather_context')
        
        # When: Call REAL Bot API
        bot = given_bot_instance_created('test_bot', bot_directory, test_bot_config)
        result = bot.shape.gather_context()
        
        # Then: Tool executed and returned result
        then_bot_result_has_status_and_behavior_and_action(result, 'completed', 'shape', 'gather_context')

    def test_tool_routes_to_correct_behavior_action_method(self, bot_directory, workspace_directory, test_bot_config):
        """
        SCENARIO: Tool routes to correct behavior action method
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
        bot = given_bot_instance_created('test_bot', bot_directory, test_bot_config)
        result = bot.exploration.build_knowledge()
        
        # Then: Routes to exploration behavior only
        then_bot_result_has_behavior_and_action(result, 'exploration', 'build_knowledge')


class TestLoadAndMergeBehaviorActionInstructions:
    """Story: Load And Merge Behavior Action Instructions - Tests instruction loading and merging."""

    def test_action_loads_and_merges_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action loads and merges instructions for shape gather_context
        GIVEN: Base and behavior-specific instructions exist
        WHEN: Action method is invoked
        THEN: Instructions are loaded from both locations and merged
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Both instruction files exist
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        workspace_root = workspace_directory.parent
        config_file = create_bot_config_file(bot_directory, bot_name, ['shape'])
        behavior_instructions = create_behavior_action_instructions(workspace_root, bot_name, behavior, action)
        base_instructions = given_base_action_instructions_created(bot_directory, action)
        
        # When: Call REAL GatherContextAction API
        action_obj = GatherContextAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        merged_instructions = action_obj.load_and_merge_instructions()
        
        # Then: Instructions merged from both sources
        assert 'base_instructions' in merged_instructions
        assert merged_instructions['action'] == action


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
        result = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        then_bot_result_has_behavior_and_action(result, 'discovery', 'gather_context')

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
        result = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        then_bot_result_has_behavior_and_action(result, 'shape', 'gather_context')


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
        result = bot.discovery.forward_to_current_action()
        
        # Then
        assert result.action == 'gather_context'

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
        result = bot.exploration.forward_to_current_action()
        
        # Then
        assert result.behavior == 'exploration'

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
        result = bot.shape.forward_to_current_action()
        
        # Then
        assert result.action == 'gather_context'
    
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
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given
        bootstrap_env(bot_directory, workspace_directory)
        # Base actions need to be created in actual repo location (where base_actions_dir looks)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        create_base_instructions(bot_directory)
        bot_config = create_bot_config_file(bot_directory, 'test_bot', ['shape'])
        # Create behavior.json file (REQUIRED after refactor)
        create_actions_workflow_json(bot_directory, 'shape')
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='test_bot',
            bot_directory=bot_directory,
            config_path=bot_config
        )
        
        # Verify no workflow state exists yet
        workflow_file = workspace_directory / 'workflow_state.json'
        assert not workflow_file.exists(), "Workflow state should not exist yet"
        
        # Call gather_context DIRECTLY (not via forward_to_current_action)
        result = bot.shape.gather_context()
        
        # Then
        workflow_file = then_workflow_state_file_exists(workspace_directory)
        then_workflow_state_has_correct_values(workflow_file, 'test_bot.shape', 'test_bot.shape.gather_context')
        assert result.action == 'gather_context'


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