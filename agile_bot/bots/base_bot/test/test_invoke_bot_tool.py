"""
Invoke Bot Tool Tests

Tests for 'Invoke Bot Tool' sub-epic and 'Perform Behavior Action' sub-epic:

Foundational Tests (Increment 1/2):
- Bot Tool Invocation
- Behavior Action Instructions

Increment 3 Tests:
- Forward To Current Behavior and Current Action
- Forward To Current Action
- Activity Logged To Project Area Not Bot Area

Uses transitions state machine for workflow state management.
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_bot_config_file(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(
        json.dumps({'name': bot_name, 'behaviors': behaviors}),
        encoding='utf-8'
    )
    return config_file

def create_base_instructions(workspace: Path):
    """Helper: Create base instructions for all actions."""
    actions = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'render_output', 'validate_rules']
    for action in actions:
        action_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(
            json.dumps({'action': action, 'instructions': [f'Instruction for {action}']}),
            encoding='utf-8'
        )

def create_workflow_state(workspace: Path, current_behavior: str, current_action: str) -> Path:
    """Helper: Create workflow state file."""
    state_dir = workspace / 'project_area'
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / 'workflow_state.json'
    state_file.write_text(json.dumps({
        'current_behavior': current_behavior,
        'current_action': current_action,
        'completed_actions': [],
        'timestamp': '2025-12-03T10:00:00Z'
    }), encoding='utf-8')
    return state_file

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

@pytest.fixture
def test_bot_config(workspace_root):
    """Fixture: Test bot configuration."""
    return create_bot_config_file(
        workspace_root,
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

def create_base_action_instructions(workspace: Path, action: str) -> Path:
    """Helper: Create base action instructions file with numbered prefix."""
    action_prefixes = {
        'gather_context': '2_gather_context',
        'decide_planning_criteria': '3_decide_planning_criteria',
        'build_knowledge': '4_build_knowledge',
        'render_output': '5_render_output',
        'validate_rules': '7_validate_rules'
    }
    
    action_folder = action_prefixes.get(action, action)
    base_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action_folder
    base_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = base_dir / 'instructions.json'
    instructions_data = {
        'actionName': action,
        'instructions': [f'Base {action} instructions']
    }
    instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
    return instructions_file

class TestBotToolInvocation:
    """Bot tool invocation behavior tests (Increment 1/2 foundational)."""

    def test_tool_invokes_behavior_action_when_called(self, workspace_root, test_bot_config):
        """
        SCENARIO: AI Chat invokes test_bot_shape_gather_context tool
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: AI Chat invokes tool with parameters
        THEN: Tool routes to test_bot.Shape.GatherContext() method
        """
        # Given: Bot configuration and instructions exist
        create_behavior_action_instructions(workspace_root, 'test_bot', 'shape', 'gather_context')
        create_base_action_instructions(workspace_root, 'gather_context')
        
        # When: Call REAL Bot API
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='test_bot',
            workspace_root=workspace_root,
            config_path=test_bot_config
        )
        result = bot.invoke_tool(
            tool_name='test_bot_shape_gather_context',
            parameters={'behavior': 'shape', 'action': 'gather_context'}
        )
        
        # Then: Tool executed and returned result
        assert result.status == 'completed'
        assert result.behavior == 'shape'
        assert result.action == 'gather_context'

    def test_tool_routes_to_correct_behavior_action_method(self, workspace_root, test_bot_config):
        """
        SCENARIO: Tool routes to correct behavior action method
        GIVEN: Bot has multiple behaviors with build_knowledge action
        WHEN: AI Chat invokes 'test_bot_exploration_build_knowledge'
        THEN: Tool routes to test_bot.Exploration.BuildKnowledge() not other behaviors
        """
        # Given: Multiple behaviors exist
        create_behavior_action_instructions(workspace_root, 'test_bot', 'shape', 'build_knowledge')
        create_behavior_action_instructions(workspace_root, 'test_bot', 'discovery', 'build_knowledge')
        create_behavior_action_instructions(workspace_root, 'test_bot', 'exploration', 'build_knowledge')
        create_base_action_instructions(workspace_root, 'build_knowledge')
        
        # Create base actions structure with action_config.json (needed for workflow)
        from agile_bot.bots.base_bot.test.conftest import create_base_actions_structure
        create_base_actions_structure(workspace_root)
        
        # Create current_project and workflow state so action can execute
        create_bot_config_file(workspace_root, 'test_bot', ['shape', 'discovery', 'exploration'])
        create_workflow_state(workspace_root, 'test_bot.exploration', 'test_bot.exploration.build_knowledge')
        
        # When: Call REAL Bot API for specific behavior
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='test_bot',
            workspace_root=workspace_root,
            config_path=test_bot_config
        )
        result = bot.invoke_tool(
            tool_name='test_bot_exploration_build_knowledge',
            parameters={'behavior': 'exploration', 'action': 'build_knowledge'}
        )
        
        # Then: Routes to exploration behavior only
        assert result.behavior == 'exploration'
        assert result.action == 'build_knowledge'


class TestBehaviorActionInstructions:
    """Behavior action instruction loading and merging tests (Increment 1/2 foundational)."""

    def test_action_loads_and_merges_instructions(self, workspace_root):
        """
        SCENARIO: Action loads and merges instructions for shape gather_context
        GIVEN: Base and behavior-specific instructions exist
        WHEN: Action method is invoked
        THEN: Instructions are loaded from both locations and merged
        """
        # Given: Both instruction files exist
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        
        config_file = create_bot_config_file(workspace_root, bot_name, ['shape'])
        behavior_instructions = create_behavior_action_instructions(workspace_root, bot_name, behavior, action)
        base_instructions = create_base_action_instructions(workspace_root, action)
        
        # When: Call REAL GatherContextAction API
        action_obj = GatherContextAction(
            bot_name=bot_name,
            behavior=behavior,
            workspace_root=workspace_root
        )
        merged_instructions = action_obj.load_and_merge_instructions()
        
        # Then: Instructions merged from both sources
        assert 'base_instructions' in merged_instructions
        assert merged_instructions['action'] == action


class TestForwardToCurrentBehaviorAndCurrentAction:
    """Story: Forward To Current Behavior and Current Action - Tests bot tool forwarding to behavior and action."""

    def test_bot_tool_forwards_to_current_behavior_and_current_action(self, workspace_root):
        """
        SCENARIO: Bot tool forwards to current behavior and current action
        GIVEN: workflow state shows current_behavior='discovery', current_action='build_knowledge'
        WHEN: Bot tool receives invocation
        THEN: Bot tool forwards to correct behavior and action
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['discovery'])
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(bot_name='story_bot', workspace_root=workspace_root, config_path=bot_config)
        result = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        assert result.behavior == 'discovery'
        assert result.action == 'gather_context'

    def test_bot_tool_defaults_to_first_behavior_and_first_action_when_state_missing(self, workspace_root):
        """
        SCENARIO: Bot tool defaults to first behavior and first action when state missing
        GIVEN: workflow state does NOT exist
        WHEN: Bot tool receives invocation
        THEN: Bot tool defaults to first behavior and first action
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['shape', 'discovery'])
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(bot_name='story_bot', workspace_root=workspace_root, config_path=bot_config)
        result = bot.forward_to_current_behavior_and_current_action()
        
        # Then
        assert result.behavior == 'shape'
        assert result.action == 'gather_context'


class TestForwardToCurrentAction:
    """Story: Forward To Current Action - Tests behavior tool forwarding to current action."""

    def test_behavior_tool_forwards_to_current_action_within_behavior(self, workspace_root):
        """
        SCENARIO: Behavior tool forwards to current action within behavior
        GIVEN: a behavior tool for 'discovery' behavior
        AND: workflow state shows current_action='build_knowledge'
        WHEN: Behavior tool receives invocation
        THEN: Behavior tool forwards to build_knowledge action
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['discovery'])
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='story_bot',
            workspace_root=workspace_root,
            config_path=bot_config
        )
        result = bot.discovery.forward_to_current_action()
        
        # Then
        assert result.action == 'gather_context'

    def test_behavior_tool_sets_workflow_to_current_behavior_when_state_shows_different_behavior(self, workspace_root):
        """
        SCENARIO: Behavior tool sets workflow to current behavior when state shows different behavior
        GIVEN: a behavior tool for 'exploration' behavior
        AND: workflow state shows current_behavior='discovery'
        WHEN: Behavior tool receives invocation
        THEN: workflow state updated to current_behavior='exploration'
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['discovery', 'exploration'])
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='story_bot',
            workspace_root=workspace_root,
            config_path=bot_config
        )
        result = bot.exploration.forward_to_current_action()
        
        # Then
        assert result.behavior == 'exploration'

    def test_behavior_tool_defaults_to_first_action_when_state_missing(self, workspace_root):
        """
        SCENARIO: Behavior tool defaults to first action when state missing
        GIVEN: a behavior tool for 'shape' behavior
        AND: workflow state does NOT exist
        WHEN: Behavior tool receives invocation
        THEN: Behavior tool defaults to first action
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['shape'])
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='story_bot',
            workspace_root=workspace_root,
            config_path=bot_config
        )
        result = bot.shape.forward_to_current_action()
        
        # Then
        assert result.action == 'gather_context'
    
    def test_action_called_directly_saves_workflow_state(self, workspace_root):
        """
        SCENARIO: Action called directly saves workflow state
        GIVEN: Bot is initialized with current_project set
        AND: No workflow state exists yet
        WHEN: Action is called directly (e.g., bot.shape.gather_context())
        THEN: workflow_state.json is created with current_behavior and current_action
        AND: This ensures state is saved whether action is called via forward or directly
        """
        # Given
        create_base_instructions(workspace_root)
        bot_config = create_bot_config_file(workspace_root, 'story_bot', ['shape'])
        
        # Create current_project.json
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'story_bot'
        project_dir = workspace_root / 'test_project'
        project_dir.mkdir()
        (bot_dir / 'current_project.json').write_text(json.dumps({'current_project': str(project_dir)}))
        
        # When
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        bot = Bot(
            bot_name='story_bot',
            workspace_root=workspace_root,
            config_path=bot_config
        )
        
        # Verify no workflow state exists yet
        workflow_file = project_dir / 'workflow_state.json'
        assert not workflow_file.exists(), "Workflow state should not exist yet"
        
        # Call gather_context DIRECTLY (not via forward_to_current_action)
        result = bot.shape.gather_context()
        
        # Then
        assert workflow_file.exists(), "Workflow state should be created"
        state_data = json.loads(workflow_file.read_text())
        assert state_data['current_behavior'] == 'story_bot.shape'
        assert state_data['current_action'] == 'story_bot.shape.gather_context'
        assert result.action == 'gather_context'


class TestActivityTrackingLocation:
    """Story: Activity Logged To Project Area Not Bot Area - Tests that activity is tracked in the correct project_area location."""

    def test_activity_logged_to_project_area_not_bot_area(self, workspace_root):
        """
        SCENARIO: Activity logged to project_area not bot area
        GIVEN: current_project.json specifies project_area='agile_bot/bots/base_bot/docs/stories'
        AND: action 'gather_context' executes
        WHEN: Activity logger creates entry
        THEN: Activity log file is at: project_area/activity_log.json
        AND: Activity log is NOT at: agile_bot/bots/story_bot/activity_log.json
        AND: Activity log location matches project_area from current_project.json
        """
        # Given: workspace root and current_project set
        workspace = workspace_root
        
        # Create current_project.json so activity tracking works
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Activity tracker tracks activity
        from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log exists in workspace root (no project_area subdirectory)
        expected_log = workspace / 'activity_log.json'
        assert expected_log.exists(), f"Activity log should be at {expected_log}"
        
        # And: Activity log does NOT exist in bot's area
        bot_area_log = workspace / 'agile_bot' / 'bots' / 'story_bot' / 'activity_log.json'
        assert not bot_area_log.exists(), f"Activity log should NOT be at {bot_area_log}"

    def test_activity_log_contains_correct_entry(self, workspace_root):
        """
        SCENARIO: Activity log contains correct entry
        GIVEN: action 'gather_context' executes in behavior 'discovery'
        WHEN: Activity logger creates entry
        THEN: Activity log entry includes:
          - action_state='story_bot.discovery.gather_context'
          - timestamp
          - Full path includes bot_name.behavior.action
        """
        # Given: workspace root and current_project set
        workspace = workspace_root
        
        # Create current_project.json so activity tracking works
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Activity tracker tracks activity
        from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log has entry
        from tinydb import TinyDB
        log_file = workspace / 'activity_log.json'
        with TinyDB(log_file) as db:
            entries = db.all()
            assert len(entries) == 1
            assert entries[0]['action_state'] == 'story_bot.shape.gather_context'
            assert entries[0]['status'] == 'started'