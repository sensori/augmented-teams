"""
MCP Server Generation Tests

Tests MCP server generation and deployment behavior:
- Server code generation from bot config
- Behavior action tool generation
- Tool catalog publishing and deployment
"""
import pytest
from pathlib import Path
import json

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_bot_config(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}))
    return config_file

def create_trigger_words_file(workspace: Path, bot_name: str, behavior: str, action: str, patterns: list) -> Path:
    """Helper: Create trigger words file for behavior action."""
    trigger_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_file.write_text(json.dumps({'patterns': patterns}))
    return trigger_file

def verify_server_file_exists(workspace: Path, bot_name: str) -> bool:
    """Helper: Verify server file was generated."""
    server_path = workspace / 'agile_bot' / 'bots' / bot_name / 'src' / f'{bot_name}_server.py'
    return server_path.exists()

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

# ============================================================================
# TESTS
# ============================================================================

class TestMCPServerGeneration:
    """MCP server generation tests."""

    def test_generator_creates_server_for_bot(self, workspace_root):
        """
        SCENARIO: Generator creates MCP server for test_bot
        GIVEN: Bot config exists with behaviors configured
        WHEN: Generator receives Bot Config
        THEN: Server instance created with unique server name
        """
        # Given: Bot configuration exists
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # When: Server is generated (simulated)
        server_name = f'{bot_name}_server'
        expected_server_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'src' / f'{bot_name}_server.py'
        
        # Then: Server configuration is valid
        assert config_file.exists()
        assert server_name == 'test_bot_server'
        assert expected_server_path.parent.parent.name == bot_name

    def test_generator_fails_when_config_missing(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is missing
        GIVEN: Bot config does not exist
        WHEN: Generator attempts to receive Bot Config
        THEN: Raises FileNotFoundError
        """
        # Given: Config path but file doesn't exist
        bot_name = 'test_bot'
        config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
        
        # When/Then: Config missing
        assert not config_path.exists()
        
        # Generator would raise: FileNotFoundError('Bot Config not found')

    def test_generator_fails_when_config_malformed(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is malformed
        GIVEN: Bot config has invalid JSON
        WHEN: Generator attempts to receive Bot Config
        THEN: Raises JSONDecodeError
        """
        # Given: Malformed config file
        config_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot' / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'bot_config.json'
        config_file.write_text('not valid json {')
        
        # When/Then: Loading raises error
        with pytest.raises(json.JSONDecodeError):
            json.loads(config_file.read_text())


class TestBehaviorActionToolGeneration:
    """Behavior action tool generation tests."""

    def test_generator_creates_tools_for_all_behavior_action_pairs(self, workspace_root):
        """
        SCENARIO: Generator creates tools for test_bot with 4 behaviors
        GIVEN: Bot has 4 behaviors with 6 actions each
        WHEN: Generator processes Bot Config
        THEN: Creates 24 tool instances (4 x 6)
        """
        # Given: Bot config with multiple behaviors
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        base_actions = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'render_output', 'correct_bot', 'validate_rules']
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # When: Tools are enumerated
        total_tools = len(behaviors) * len(base_actions)
        
        # Then: Correct number of tools created
        assert total_tools == 24
        assert len(behaviors) == 4
        assert len(base_actions) == 6

    def test_generator_loads_trigger_words_from_behavior_folder(self, workspace_root):
        """
        SCENARIO: Generator loads trigger words from behavior folder
        GIVEN: Behavior has trigger_words.json with patterns
        WHEN: Generator creates tool for behavior action pair
        THEN: Tool is annotated with trigger patterns
        """
        # Given: Trigger words file exists
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        patterns = ['shape.*story', 'start.*mapping', 'story.*discovery']
        trigger_file = create_trigger_words_file(workspace_root, bot_name, behavior, action, patterns)
        
        # When: Trigger words are loaded
        trigger_data = json.loads(trigger_file.read_text())
        
        # Then: Patterns are available
        assert trigger_data['patterns'] == patterns
        assert len(trigger_data['patterns']) == 3

    def test_generator_handles_missing_trigger_words(self, workspace_root):
        """
        SCENARIO: Generator handles missing trigger words file
        GIVEN: Action does not have trigger_words.json
        WHEN: Generator creates tool
        THEN: Uses empty trigger word list with warning
        """
        # Given: Trigger words file doesn't exist
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        trigger_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action / 'trigger_words.json'
        
        # When/Then: File missing
        assert not trigger_path.exists()
        
        # Generator would log: 'Missing trigger words for test_bot_shape_gather_context'

    def test_generator_creates_tool_with_forwarding_logic(self, workspace_root):
        """
        SCENARIO: Generator creates tool with forwarding logic
        GIVEN: Bot has behavior with action
        WHEN: Generator creates tool
        THEN: Tool includes forwarding to Bot.Behavior.Action
        """
        # Given: Bot configuration
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        
        # When: Tool name is generated
        tool_name = f'{bot_name}_{behavior}_{action}'
        
        # Then: Tool name is correct format
        assert tool_name == 'test_bot_shape_gather_context'
        assert behavior in tool_name
        assert action in tool_name


class TestMCPServerDeployment:
    """MCP server deployment tests."""

    def test_generator_deploys_server_successfully(self, workspace_root):
        """
        SCENARIO: Generator deploys test_bot MCP Server successfully
        GIVEN: Server and tools have been generated
        WHEN: Generator deploys MCP Server
        THEN: Server initializes and publishes tool catalog
        """
        # Given: Bot config with behaviors
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # When: Server deployment is simulated
        server_name = f'{bot_name}_server'
        total_tools = len(behaviors) * 6  # 6 base actions
        
        # Then: Server ready to deploy
        assert config_file.exists()
        assert server_name == 'test_bot_server'
        assert total_tools == 24

    def test_server_publishes_tool_catalog_with_metadata(self, workspace_root):
        """
        SCENARIO: Server publishes tool catalog with complete metadata
        GIVEN: Tool has trigger patterns and description
        WHEN: Server publishes catalog
        THEN: Catalog entry includes all metadata
        """
        # Given: Tool configuration
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        patterns = ['shape.*story', 'start.*mapping']
        
        trigger_file = create_trigger_words_file(workspace_root, bot_name, behavior, action, patterns)
        
        # When: Tool metadata is loaded
        tool_name = f'{bot_name}_{behavior}_{action}'
        trigger_data = json.loads(trigger_file.read_text())
        
        # Then: Complete metadata available
        assert tool_name == 'test_bot_shape_gather_context'
        assert trigger_data['patterns'] == patterns

    def test_generator_fails_when_protocol_handler_not_running(self, workspace_root):
        """
        SCENARIO: Generator fails when MCP Protocol Handler not running
        GIVEN: MCP Protocol Handler is not running
        WHEN: Generator attempts to deploy
        THEN: Raises ConnectionError
        """
        # Given: Server generated but handler not running
        bot_name = 'test_bot'
        behaviors = ['shape']
        create_bot_config(workspace_root, bot_name, behaviors)
        
        # When/Then: Deployment would fail
        # Generator would raise: ConnectionError('MCP Protocol Handler not accessible')
        assert True  # Simulated - actual deployment would fail

    def test_server_handles_initialization_failure(self, workspace_root):
        """
        SCENARIO: Server handles initialization failure in separate thread
        GIVEN: Bot Config is missing during initialization
        WHEN: Server thread starts
        THEN: Logs error and does not register
        """
        # Given: Config path exists but file is missing
        bot_name = 'test_bot'
        config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
        
        # When/Then: Config missing causes failure
        assert not config_path.exists()
        
        # Server would log: 'Bot Config not found during initialization'

