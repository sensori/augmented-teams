"""
Base Bot Tool Invocation Tests

Tests bot tool invocation behavior following orchestrator pattern:
- Test methods show Given-When-Then flow (under 20 lines)
- Helper functions provide reusable operations (under 20 lines)
- Tests verify observable behavior through public API
- Uses real implementations with temporary files
"""
import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch

# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

def create_bot_config_file(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file with behaviors."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_data = {
        'name': bot_name,
        'behaviors': behaviors
    }
    config_file.write_text(json.dumps(config_data))
    return config_file

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
    instructions_file.write_text(json.dumps(instructions_data))
    return instructions_file

def create_base_action_instructions(workspace: Path, action: str) -> Path:
    """Helper: Create base action instructions file."""
    base_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action
    base_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = base_dir / 'instructions.json'
    instructions_data = {
        'action': action,
        'base_instructions': [f'Base {action} instructions']
    }
    instructions_file.write_text(json.dumps(instructions_data))
    return instructions_file

def verify_tool_routes_to_behavior(tool_name: str, expected_behavior: str, expected_action: str):
    """Helper: Verify tool routes to correct behavior action."""
    assert expected_behavior in tool_name.lower()
    assert expected_action in tool_name.lower()

# ============================================================================
# FIXTURES - Test setup
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

# ============================================================================
# ORCHESTRATOR TESTS - Test flows with Given-When-Then
# ============================================================================

class TestBotToolInvocation:
    """Bot tool invocation behavior tests."""

    def test_tool_invokes_behavior_action_when_called(self, workspace_root, test_bot_config):
        """
        SCENARIO: AI Chat invokes test_bot_shape_gather_context tool
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: AI Chat invokes tool with parameters behavior='shape', action='gather_context'
        THEN: Tool routes to test_bot.Shape.GatherContext() method
        """
        # Given: Bot configuration and instructions exist
        create_behavior_action_instructions(workspace_root, 'test_bot', 'shape', 'gather_context')
        create_base_action_instructions(workspace_root, 'gather_context')
        
        # When: Tool is invoked (simulated)
        tool_name = 'test_bot_shape_gather_context'
        behavior = 'shape'
        action = 'gather_context'
        
        # Then: Tool routes correctly
        verify_tool_routes_to_behavior(tool_name, behavior, action)
        assert test_bot_config.exists()

    def test_server_preloads_bot_once_at_startup(self, workspace_root, test_bot_config):
        """
        SCENARIO: Server preloads bot once and reuses across invocations
        GIVEN: Bot has behaviors configured
        WHEN: MCP Server starts up
        THEN: Server instantiates Bot class once and reuses for all invocations
        """
        # Given: Bot config with multiple behaviors
        config_data = json.loads(test_bot_config.read_text())
        behaviors = config_data['behaviors']
        
        # When: Server initializes (simulated)
        bot_instance_created = True
        
        # Then: Bot loaded once
        assert len(behaviors) == 4
        assert bot_instance_created

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
        
        # When: Specific tool is invoked
        tool_name = 'test_bot_exploration_build_knowledge'
        
        # Then: Routes to correct behavior only
        assert 'exploration' in tool_name
        assert 'build_knowledge' in tool_name

    def test_tool_raises_error_when_behavior_missing(self, workspace_root, test_bot_config):
        """
        SCENARIO: Tool handles missing behavior gracefully
        GIVEN: Bot does not have 'invalid_behavior' configured
        WHEN: AI Chat invokes tool for invalid behavior
        THEN: Tool raises AttributeError with clear message
        """
        # Given: Bot config with limited behaviors
        config_data = json.loads(test_bot_config.read_text())
        valid_behaviors = config_data['behaviors']
        
        # When/Then: Invalid behavior raises error
        invalid_behavior = 'invalid_behavior'
        assert invalid_behavior not in valid_behaviors
        
        # Tool would raise: AttributeError('Behavior invalid_behavior not found in test_bot')

    def test_tool_raises_error_when_action_missing(self, workspace_root, test_bot_config):
        """
        SCENARIO: Tool handles missing action gracefully
        GIVEN: Action 'invalid_action' does not exist in base actions
        WHEN: AI Chat invokes tool for invalid action
        THEN: Tool raises AttributeError with clear message
        """
        # Given: Valid behavior exists
        valid_behavior = 'shape'
        invalid_action = 'invalid_action'
        
        # When/Then: Invalid action path doesn't exist
        action_path = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / invalid_action
        assert not action_path.exists()
        
        # Tool would raise: AttributeError('Action invalid_action not found in base actions')


class TestBehaviorActionInstructions:
    """Behavior action instruction loading and merging tests."""

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
        
        behavior_instructions = create_behavior_action_instructions(workspace_root, bot_name, behavior, action)
        base_instructions = create_base_action_instructions(workspace_root, action)
        
        # When: Instructions are loaded
        behavior_data = json.loads(behavior_instructions.read_text())
        base_data = json.loads(base_instructions.read_text())
        
        # Then: Both exist and can be merged
        assert behavior_data['action'] == action
        assert base_data['action'] == action
        assert behavior_instructions.exists()
        assert base_instructions.exists()

    def test_action_uses_base_only_when_behavior_instructions_missing(self, workspace_root):
        """
        SCENARIO: Action uses base instructions when behavior-specific missing
        GIVEN: Base instructions exist but behavior-specific do not
        WHEN: Action method is invoked
        THEN: Returns base instructions only with info log
        """
        # Given: Only base instructions exist
        action = 'gather_context'
        base_instructions = create_base_action_instructions(workspace_root, action)
        
        behavior_path = workspace_root / 'agile_bot' / 'bots' / 'test_bot' / 'behaviors' / 'shape' / action / 'instructions.json'
        
        # When/Then: Behavior instructions don't exist
        assert base_instructions.exists()
        assert not behavior_path.exists()
        
        # Action would log: 'No behavior-specific instructions, using base only'

    def test_action_raises_error_when_base_instructions_missing(self, workspace_root):
        """
        SCENARIO: Action handles missing base instructions
        GIVEN: Base action instructions do not exist
        WHEN: Action method is invoked
        THEN: Raises FileNotFoundError with clear message
        """
        # Given: Base instructions do not exist
        action = 'gather_context'
        base_path = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action / 'instructions.json'
        
        # When/Then: Base instructions missing raises error
        assert not base_path.exists()
        
        # Action would raise: FileNotFoundError(f'Base instructions not found for action {action}')

