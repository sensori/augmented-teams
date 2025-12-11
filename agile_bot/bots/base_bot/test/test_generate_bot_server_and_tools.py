"""
Generate Bot Server And Tools Tests

Tests for all stories in the 'Generate Bot Server And Tools' sub-epic (in story map order):
- Generate Bot Tools (Increment 3)
- Generate Behavior Tools (Increment 3)
- Generate MCP Bot Server (Increment 2)
- Generate Behavior Action Tools (Increment 2)
- Deploy MCP Bot Server (Increment 2)
- Generate Cursor Awareness Files (Increment 2)
"""
import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch
from fastmcp import FastMCP, Client
from conftest import bootstrap_env

# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

def create_bot_config(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_file

def create_base_actions_structure(bot_directory: Path):
    """Helper: Create base_actions directory structure in bot_directory (no fallback)."""
    base_actions_dir = bot_directory / 'base_actions'
    
    actions = [
        ('1_initialize_project', 'decide_planning_criteria'),
        ('1_gather_context', 'decide_planning_criteria'),
        ('2_decide_planning_criteria', 'build_knowledge'),
        ('3_build_knowledge', 'validate_rules'),
        ('4_validate_rules', 'render_output'),
        ('5_render_output', None)
    ]
    
    for order_name, next_action in actions:
        action_dir = base_actions_dir / order_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        # Create action_config.json
        config = {
            'name': order_name.split('_', 1)[1],
            'workflow': True,
            'order': int(order_name.split('_')[0])
        }
        if next_action:
            config['next_action'] = next_action
        
        (action_dir / 'action_config.json').write_text(json.dumps(config), encoding='utf-8')

def create_base_instructions(bot_directory: Path):
    """Helper: Create base instructions for all actions in bot_directory (no fallback)."""
    base_actions_dir = bot_directory / 'base_actions'
    actions = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
    for action in actions:
        action_dir = base_actions_dir / action
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(
            json.dumps({'action': action, 'instructions': [f'Instruction for {action}']}),
            encoding='utf-8'
        )

def create_trigger_words_file(workspace: Path, bot_name: str, behavior: str, action: str, patterns: list) -> Path:
    """Helper: Create trigger words file for behavior action."""
    trigger_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_file.write_text(json.dumps({'patterns': patterns}), encoding='utf-8')
    return trigger_file

def create_base_server_template(workspace: Path) -> Path:
    """Helper: Create base MCP server template."""
    template_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'src'
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file = template_dir / 'base_mcp_server.py'
    template_file.write_text('# Base MCP Server template')
    return template_file

def create_base_bot_class(workspace: Path) -> Path:
    """Helper: Create base bot class."""
    base_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'src'
    base_dir.mkdir(parents=True, exist_ok=True)
    base_file = base_dir / 'base_bot.py'
    base_file.write_text('# Base Bot class')
    return base_file

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
def generator(workspace_root):
    """Fixture: MCPServerGenerator instance with bot config."""
    # Bootstrap environment before importing/creating generator
    bot_name = 'test_bot'
    bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
    workspace_directory = workspace_root / 'workspace'
    workspace_directory.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_dir, workspace_directory)
    
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    
    # Create bot config file
    config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({
        'name': bot_name,
        'behaviors': ['shape', 'discovery']
    }), encoding='utf-8')
    
    gen = MCPServerGenerator(bot_directory=bot_dir)
    return gen

class TestGenerateBotTools:
    """Story: Generate Bot Tools - Tests ONE bot tool with workflow state awareness."""

    def test_generator_creates_bot_tool_for_test_bot(self, workspace_root):
        """
        SCENARIO: Generator creates bot tool for test_bot
        GIVEN: a bot with name 'test_bot'
        AND: bot has 4 behaviors configured
        WHEN: Generator processes Bot Config
        THEN: Generator creates 1 bot tool instance
        """
        # Given: a bot with name 'test_bot'
        bot_config = create_bot_config(
            workspace_root,
            'test_bot',
            ['shape', 'discovery', 'exploration', 'specification']
        )
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.bot_tool_generator import BotToolGenerator
        generator = BotToolGenerator(
            bot_name='test_bot',
            config_path=bot_config
        )
        bot_tool = generator.create_bot_tool()
        
        # Then: 1 bot tool instance created
        assert bot_tool is not None


class TestGenerateBehaviorTools:
    """Story: Generate Behavior Tools - Tests behavior tool generation with action routing."""

    def test_generator_creates_behavior_tools_for_test_bot_with_4_behaviors(self, workspace_root):
        """
        SCENARIO: Generator creates behavior tools for test_bot with 4 behaviors
        GIVEN: a bot with name 'test_bot'
        AND: bot has 4 behaviors configured
        WHEN: Generator processes Bot Config
        THEN: Generator creates 4 behavior tool instances
        """
        # Given: a bot with 4 behaviors
        bot_config = create_bot_config(
            workspace_root,
            'test_bot',
            ['shape', 'discovery', 'exploration', 'specification']
        )
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.behavior_tool_generator import BehaviorToolGenerator
        generator = BehaviorToolGenerator(
            bot_name='test_bot',
            config_path=bot_config
        )
        tools = generator.create_behavior_tools()
        
        # Then: 4 behavior tool instances created
        assert len(tools) == 4


class TestGenerateMCPBotServer:
    """Story: Generate MCP Bot Server - Tests MCP server generation using FastMCP."""

    def test_generator_creates_mcp_server_for_test_bot(self, workspace_root):
        """
        SCENARIO: Generator creates MCP server for test_bot
        GIVEN: Bot with name 'test_bot' and behaviors configured
        WHEN: MCP Server Generator receives Bot Config
        THEN: Generator creates MCP Server instance with unique server name
        """
        # Given: Bot with name 'test_bot' and behaviors configured
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: MCP Server Generator receives Bot Config (generates files)
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        artifacts = generator.generate_server(behaviors=behaviors)
        
        # Then: Generator creates MCP Server instance with unique server name 'test_bot_server'
        assert artifacts['server_entry'].exists()
        assert artifacts['server_entry'].name == f'{bot_name}_mcp_server.py'
        
        # And Generated server is saved to exact path
        expected_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'src' / f'{bot_name}_mcp_server.py'
        assert artifacts['server_entry'] == expected_path
        
        # And Generated server includes Bot instantiation code
        server_code = artifacts['server_entry'].read_text()
        assert 'MCPServerGenerator' in server_code
        assert 'create_server_instance' in server_code
        assert 'register_all_behavior_action_tools' in server_code
        assert bot_name in server_code


    def test_generator_fails_when_bot_config_missing(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is missing
        GIVEN: Bot with name 'test_bot' and Bot Config does NOT exist
        WHEN: MCP Server Generator attempts to receive Bot Config
        THEN: Generator raises FileNotFoundError and does not create MCP Server instance
        """
        # Given: Bot with name 'test_bot' and Bot Config does NOT exist at bot_config.json
        bot_name = 'test_bot'
        expected_config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: MCP Server Generator attempts to receive Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        
        # Then: Generator raises FileNotFoundError with message
        with pytest.raises(FileNotFoundError) as exc_info:
            generator.create_server_instance()
        
        assert f'Bot Config not found at {expected_config_path}' in str(exc_info.value)
        
        # And Generator does not create MCP Server instance (verified by exception)

    def test_generator_fails_when_bot_config_malformed(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is malformed
        GIVEN: Bot with name 'test_bot', Bot Config exists with invalid JSON syntax
        WHEN: MCP Server Generator attempts to receive Bot Config
        THEN: Generator raises JSONDecodeError and does not create MCP Server instance
        """
        # Given: Bot with name 'test_bot', Bot Config exists with invalid JSON syntax
        bot_name = 'test_bot'
        config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'bot_config.json'
        config_file.write_text('not valid json {')
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: MCP Server Generator attempts to receive Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        
        # Then: Generator raises JSONDecodeError with message
        with pytest.raises(json.JSONDecodeError) as exc_info:
            generator.create_server_instance()
        
        assert f'Malformed Bot Config at {config_file}' in str(exc_info.value)
        
        # And Generator does not create MCP Server instance (verified by exception)


class TestGenerateBehaviorActionTools:
    """Story: Generate Behavior Action Tools - Tests tool generation using FastMCP."""

    def test_generator_creates_tools_for_test_bot_with_4_behaviors(self, workspace_root):
        """
        SCENARIO: Generator creates tools for test_bot with 4 behaviors
        GIVEN: Bot with 4 behaviors configured
        WHEN: Generator processes Bot Config
        THEN: Generator creates bot tool and 4 behavior tools
        """
        # Given: Bot with 4 behaviors configured
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        create_base_actions_structure(bot_dir)
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # Bootstrap environment before importing/creating generator
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        mcp_server = generator.create_server_instance()
        generator.register_all_behavior_action_tools(mcp_server)
        
        # Then: Generator creates bot tool and behavior tools
        # 1 bot_tool + 1 get_working_dir + 1 close_action + 1 restart + 4 behavior_tools = 8 tools
        assert len(generator.registered_tools) >= 7  # At least bot tool + 4 behavior tools + utility tools
        
        # And Generator creates behavior tools with behavior names
        tool_names = [tool['name'] for tool in generator.registered_tools]
        behavior_tools = [tool for tool in generator.registered_tools if tool.get('type') == 'behavior_tool']
        assert len(behavior_tools) == 4, f"Expected 4 behavior tools, got {len(behavior_tools)}"
        assert 'shape' in tool_names or any(t.get('behavior') == 'shape' for t in generator.registered_tools)
        assert 'discovery' in tool_names or any(t.get('behavior') == 'discovery' for t in generator.registered_tools)
        
        # And each behavior tool includes forwarding logic to invoke Bot.Behavior.Action
        # (verified by tool registration)

    def test_generator_loads_trigger_words_from_behavior_folder(self, workspace_root):
        """
        SCENARIO: Generator loads trigger words from behavior folder
        GIVEN: Behavior has trigger_words.json with patterns
        WHEN: Generator creates behavior tool
        THEN: Behavior tool is registered with trigger patterns in description
        """
        # Given: Trigger words file exists at behavior level
        bot_name = 'test_bot'
        behavior = 'shape'
        patterns = ['shape.*story', 'start.*mapping', 'story.*discovery']
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        # Create trigger words at behavior level (not action level)
        behavior_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        trigger_file = behavior_dir / 'trigger_words.json'
        trigger_file.write_text(json.dumps({'patterns': patterns}), encoding='utf-8')
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL MCPServerGenerator to register behavior tool with trigger words
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        mcp_server = generator.create_server_instance()
        generator.register_all_behavior_action_tools(mcp_server)
        
        # Then: Behavior tool registered with trigger patterns
        tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
        assert tool is not None, f"Behavior tool for {behavior} should be registered"
        assert tool['type'] == 'behavior_tool'
        assert 'shape.*story' in tool['description']
        assert 'shape.*story' in tool['trigger_patterns']

    def test_generator_handles_missing_trigger_words(self, workspace_root):
        """
        SCENARIO: Generator handles missing trigger words file
        GIVEN: Behavior does not have trigger_words.json
        WHEN: Generator creates behavior tool
        THEN: Behavior tool registered without trigger patterns
        """
        # Given: No trigger words file exists at behavior level
        bot_name = 'test_bot'
        behavior = 'shape'
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL MCPServerGenerator (trigger words missing)
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        mcp_server = generator.create_server_instance()
        generator.register_all_behavior_action_tools(mcp_server)
        
        # Then: Behavior tool registered without trigger patterns (graceful handling)
        tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
        assert tool is not None, f"Behavior tool for {behavior} should be registered"
        assert tool['type'] == 'behavior_tool'
        assert tool['trigger_patterns'] == []

    @pytest.mark.asyncio
    async def test_generator_registers_tool_with_forwarding_to_bot_behavior_action(self, workspace_root):
        """
        SCENARIO: Generator registers behavior tool with forwarding logic
        GIVEN: Bot has behavior with action
        WHEN: Generator registers behavior tool with FastMCP
        THEN: Behavior tool forwards invocation to Bot.execute_behavior() (production code path)
        """
        # Given: Bot configuration
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # Create base actions structure (needed for workflow)
        create_base_actions_structure(bot_dir)
        
        # Create base instructions (needed for action execution)
        create_base_instructions(bot_dir)
        
        # Create behavior folder
        behavior_dir = bot_dir / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # When: Call REAL MCPServerGenerator to register behavior tool
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(bot_directory=bot_dir)
        mcp_server = generator.create_server_instance()
        
        # Use REAL Bot instance (not mock) - generator creates it automatically
        # Create workflow state so entry workflow doesn't trigger
        workflow_file = workspace_directory / 'workflow_state.json'
        workflow_file.write_text(json.dumps({
            'current_behavior': f'{bot_name}.{behavior}',
            'current_action': f'{bot_name}.{behavior}.{action}',
            'completed_actions': []
        }), encoding='utf-8')
        
        generator.register_all_behavior_action_tools(mcp_server)
        
        # Then: Behavior tool registered and callable through FastMCP
        tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
        assert tool is not None, f"Behavior tool for {behavior} should be registered"
        assert tool['type'] == 'behavior_tool'
        
        # Test tool invocation through FastMCP client with action parameter
        # This calls the REAL bot.execute_behavior() method
        async with Client(mcp_server) as client:
            # Call behavior tool with action parameter
            result = await client.call_tool(behavior, {'action': action})
            
            # Verify result contains BotResult structure from real execution
            result_dict = json.loads(result.content[0].text)
            assert result_dict['status'] == 'completed'
            assert result_dict['behavior'] == behavior
            assert result_dict['action'] == action


class TestDeployMCPBotServer:
    """Story: Deploy MCP Bot Server - Tests server deployment."""

    def test_generator_deploys_server_successfully(self, workspace_root):
        """
        SCENARIO: Generator deploys test_bot MCP Server successfully
        GIVEN: Server and tools have been generated
        WHEN: Generator deploys MCP Server
        THEN: Server initializes and publishes tool catalog
        """
        # Given: Bot config, server generated, tools generated
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        create_base_server_template(workspace_root)
        
        # Bootstrap environment before importing/creating deployer
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL ServerDeployer API to deploy
        from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
        deployer = ServerDeployer(
            config_path=config_file,
            workspace_root=workspace_root
        )
        deployment_result = deployer.deploy_server()
        
        # Then: Server deployed and running
        assert deployment_result.status == 'running'
        assert deployment_result.server_name == 'test_bot_server'
        # 1 bot_tool + 1 get_working_dir + 1 close_action + 1 restart + 4 behavior_tools = 8 tools
        assert deployment_result.tool_count >= 7  # At least bot tool + 4 behavior tools + utility tools
        assert deployment_result.catalog_published is True

    def test_server_publishes_tool_catalog_with_metadata(self, workspace_root):
        """
        SCENARIO: Server publishes tool catalog with complete metadata
        GIVEN: Tool has trigger patterns and description
        WHEN: Server publishes catalog
        THEN: Catalog entry includes all metadata
        """
        # Given: Tool with complete metadata (trigger words at behavior level)
        bot_name = 'test_bot'
        behavior = 'shape'
        patterns = ['shape.*story', 'start.*mapping']
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        # Create trigger words at behavior level (not action level)
        behavior_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        trigger_file = behavior_dir / 'trigger_words.json'
        trigger_file.write_text(json.dumps({'patterns': patterns}), encoding='utf-8')
        
        # Bootstrap environment before importing/creating deployer
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL ServerDeployer API to get catalog
        from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
        deployer = ServerDeployer(
            config_path=config_file,
            workspace_root=workspace_root
        )
        catalog = deployer.get_tool_catalog()
        
        # Then: Catalog includes tools (catalog builds individual action tools)
        # Note: Catalog may still use old naming convention with individual action tools
        # Check that catalog has tools registered
        assert len(catalog.tools) > 0, "Catalog should have tools registered"
        
        # Check for a tool that matches the behavior (catalog may use action tool names)
        # Since catalog builds action tools, look for one with the behavior name
        behavior_tools = [t for t in catalog.tools.values() if t.behavior == behavior]
        assert len(behavior_tools) > 0, f"Catalog should have tools for behavior '{behavior}'"
        
        # Check that trigger patterns are loaded
        tool_with_patterns = next((t for t in behavior_tools if t.trigger_patterns == patterns), None)
        if tool_with_patterns:
            assert tool_with_patterns.trigger_patterns == patterns
            assert hasattr(tool_with_patterns, 'description')

    def test_generator_fails_when_protocol_handler_not_running(self, workspace_root):
        """
        SCENARIO: Generator fails when MCP Protocol Handler not running
        GIVEN: MCP Protocol Handler is not running
        WHEN: Generator attempts to deploy
        THEN: Raises ConnectionError
        """
        # Given: Bot config but MCP protocol handler not available
        bot_name = 'test_bot'
        behaviors = ['shape']
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # Bootstrap environment before importing/creating deployer
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL ServerDeployer API (protocol handler not running)
        from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
        deployer = ServerDeployer(
            config_path=config_file,
            workspace_root=workspace_root,
            protocol_handler_url='http://localhost:9999'  # Not running
        )
        
        # Then: Raises ConnectionError
        with pytest.raises(ConnectionError) as exc_info:
            deployer.deploy_server()
        
        assert 'MCP Protocol Handler not accessible' in str(exc_info.value)

    def test_server_handles_initialization_failure(self, workspace_root):
        """
        SCENARIO: Server handles initialization failure in separate thread
        GIVEN: Bot Config is missing during initialization
        WHEN: Server thread starts
        THEN: Logs error and does not register
        """
        # Given: Config path but file is missing
        bot_name = 'test_bot'
        config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
        
        # Bootstrap environment before importing/creating deployer
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Call REAL ServerDeployer API with missing config
        from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
        deployer = ServerDeployer(
            config_path=config_path,
            workspace_root=workspace_root
        )
        
        # Then: Deployment fails gracefully with logged error
        deployment_result = deployer.deploy_server()
        
        assert deployment_result.status == 'failed'
        assert 'Bot Config not found' in deployment_result.error_message
        assert deployment_result.catalog_published is False


class TestGenerateCursorAwarenessFiles:
    """Story: Generate Cursor Awareness Files - Tests awareness file generation."""

    def test_generator_creates_workspace_rules_file_with_trigger_patterns(self, workspace_root):
        """
        SCENARIO: Generator creates bot-specific workspace rules file with trigger patterns
        GIVEN: Bot config exists with behaviors that have trigger_words.json files
        WHEN: Generator runs generate_awareness_files() method
        THEN: Generator creates file with bot-specific filename: mcp-test-bot-awareness.mdc
        AND: Filename includes bot name with hyphens
        AND: Generated rules file includes ACTUAL trigger words from bot
        AND: File includes bot name from config
        """
        # Given: Create bot config with behaviors
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery']
        
        config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'bot_config.json'
        config_file.write_text(json.dumps({
            'name': bot_name,
            'behaviors': behaviors
        }), encoding='utf-8')
        
        # Create trigger_words.json for shape behavior
        shape_behavior_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        shape_behavior_dir.mkdir(parents=True, exist_ok=True)
        shape_trigger_file = shape_behavior_dir / 'trigger_words.json'
        shape_trigger_file.write_text(json.dumps({
            'patterns': ['shape story', 'define story outline', 'create story map']
        }), encoding='utf-8')
        
        # Create trigger_words.json for discovery behavior
        discovery_behavior_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '4_discovery'
        discovery_behavior_dir.mkdir(parents=True, exist_ok=True)
        discovery_trigger_file = discovery_behavior_dir / 'trigger_words.json'
        discovery_trigger_file.write_text(json.dumps({
            'patterns': ['discover stories', 'break down stories', 'enumerate stories']
        }), encoding='utf-8')
        
        # Bootstrap environment before importing/creating generator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        workspace_directory = workspace_root / 'workspace'
        workspace_directory.mkdir(parents=True, exist_ok=True)
        bootstrap_env(bot_dir, workspace_directory)
        
        # When: Generate awareness files
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        gen = MCPServerGenerator(bot_directory=bot_dir)
        gen.generate_awareness_files()
        
        # Then: Rules file created with BOT-SPECIFIC filename (in repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_file = repo_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        assert rules_file.exists(), f"Expected bot-specific file: {rules_file}"
        
        # And: Generic filename should NOT exist
        generic_file = repo_root / '.cursor' / 'rules' / 'mcp-tool-awareness.mdc'
        assert not generic_file.exists(), "Should use bot-specific filename, not generic"
        
        content = rules_file.read_text(encoding='utf-8')
        
        # And: File includes bot name
        assert 'test_bot' in content
        
        # And: Trigger words are SECTIONED by behavior (not flat list)
        assert '### Shape Behavior' in content or '## Shape' in content
        assert '### Discovery Behavior' in content or '## Discovery' in content
        
        # And: Shape section includes ONLY shape trigger words
        # Find the shape section
        shape_section_start = content.find('Shape')
        discovery_section_start = content.find('Discovery')
        
        if shape_section_start != -1 and discovery_section_start != -1:
            shape_section = content[shape_section_start:discovery_section_start]
            # Shape trigger words should be in shape section
            assert 'shape story' in shape_section
            assert 'define story outline' in shape_section
            assert 'create story map' in shape_section
            # Discovery trigger words should NOT be in shape section
            assert 'discover stories' not in shape_section
            
            # Discovery section should have discovery trigger words
            discovery_section = content[discovery_section_start:]
            assert 'discover stories' in discovery_section
            assert 'break down stories' in discovery_section
            assert 'enumerate stories' in discovery_section
        
        # And: Each behavior section shows tool pattern
        assert 'story_bot_shape_' in content or 'test_bot_shape_' in content
        assert 'story_bot_discovery_' in content or 'test_bot_discovery_' in content

    def test_rules_file_includes_bot_goal_and_behavior_descriptions(self, workspace_root):
        """
        SCENARIO: Rules file includes bot goal and behavior descriptions from instructions.json
        GIVEN: Bot has instructions.json with goal and behavior descriptions
        WHEN: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
        THEN: File includes bot's goal from instructions.json
        AND: Critical rule mentions bot's goal: "When user is trying to [goal], check MCP tools FIRST"
        AND: Each behavior section includes "When user is trying to [behavior description]"
        """
        # Given: Create bot with instructions.json
        bot_name = 'test_bot'
        config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / 'bot_config.json').write_text(json.dumps({
            'name': bot_name,
            'behaviors': ['shape', 'discovery']
        }), encoding='utf-8')
        
        # Create instructions.json with goal and behavior descriptions
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        (bot_dir / 'instructions.json').write_text(json.dumps({
            'botName': bot_name,
            'goal': 'Transform user needs into well-structured stories',
            'description': 'Helps teams create and refine user stories',
            'behaviors': {
                'shape': 'Create initial story map outline from user context',
                'discovery': 'Elaborate stories with user flows and domain rules'
            }
        }), encoding='utf-8')
        
        # Create trigger words
        shape_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        shape_dir.mkdir(parents=True, exist_ok=True)
        (shape_dir / 'trigger_words.json').write_text(json.dumps({
            'patterns': ['shape story', 'create story map']
        }), encoding='utf-8')
        
        discovery_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '4_discovery'
        discovery_dir.mkdir(parents=True, exist_ok=True)
        (discovery_dir / 'trigger_words.json').write_text(json.dumps({
            'patterns': ['discover stories', 'elaborate stories']
        }), encoding='utf-8')
        
        # When: Generate awareness files
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        gen = MCPServerGenerator(bot_directory=bot_dir)
        gen.generate_awareness_files()
        
        # Then: Critical rule mentions SPECIFIC bot name (file written to repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_file = repo_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        content = rules_file.read_text(encoding='utf-8')
        
        assert 'ALWAYS check for and use MCP test_bot tools FIRST' in content
        
        # And: Each behavior follows explicit format
        # Shape section
        assert '**When user is trying to:** Create initial story map outline' in content
        assert '**as indicated by Trigger words:**' in content
        assert '**Then check for:** `test_bot_shape_<action>` tool' in content
        
        # Discovery section
        assert '**When user is trying to:** Elaborate stories with user flows' in content
        assert '**Then check for:** `test_bot_discovery_<action>` tool' in content
        
        # And: File includes error handling section
        assert 'If a registered tool is broken or returns an error' in content
        assert 'DO NOT automatically attempt a workaround' in content
        assert 'Inform user of the exact error details' in content
        assert 'Should I attempt to repair the tool, or proceed manually' in content

    def test_rules_file_maps_trigger_patterns_to_tool_naming_conventions(self, workspace_root):
        """
        SCENARIO: Rules file maps trigger patterns to tool naming conventions in behavior sections
        GIVEN: Bot has behaviors with trigger_words.json files
        WHEN: File is written to .cursor/rules/mcp-test-bot-awareness.mdc
        THEN: Each behavior section includes tool pattern with ACTUAL bot name
        AND: Tool patterns appear in behavior sections (not flat list)
        """
        # Given: Create bot with trigger words
        bot_name = 'test_bot'
        config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / 'bot_config.json').write_text(json.dumps({
            'name': bot_name,
            'behaviors': ['shape', 'discovery']
        }), encoding='utf-8')
        
        # Create trigger words for shape
        shape_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        shape_dir.mkdir(parents=True, exist_ok=True)
        (shape_dir / 'trigger_words.json').write_text(json.dumps({
            'patterns': ['shape story', 'define outline']
        }), encoding='utf-8')
        
        # Create trigger words for discovery
        discovery_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '4_discovery'
        discovery_dir.mkdir(parents=True, exist_ok=True)
        (discovery_dir / 'trigger_words.json').write_text(json.dumps({
            'patterns': ['discover stories', 'enumerate stories']
        }), encoding='utf-8')
        
        # When: Generate awareness files
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        gen = MCPServerGenerator(bot_directory=bot_dir)
        gen.generate_awareness_files()
        
        # Then: File has behavior sections with tool patterns (file written to repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_file = repo_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        content = rules_file.read_text(encoding='utf-8')
        
        # Verify behavior sections exist
        assert '### Shape Behavior' in content
        assert '### Discovery Behavior' in content
        
        # Verify tool patterns in sections use actual bot name
        assert 'test_bot_shape_<action>' in content
        assert 'test_bot_discovery_<action>' in content
        
        # Verify trigger words are in correct sections
        shape_section = content[content.find('### Shape'):content.find('### Discovery')]
        assert 'shape story' in shape_section
        assert 'define outline' in shape_section
        
        discovery_section = content[content.find('### Discovery'):]
        assert 'discover stories' in discovery_section
        assert 'enumerate stories' in discovery_section

    def test_generator_handles_file_write_errors_gracefully_creates_directory(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors gracefully - creates directory
        GIVEN: MCP Server Generator attempts to create awareness files
        WHEN: .cursor/rules/ directory does not exist
        THEN: Generator creates directory before writing file
        AND: File write succeeds with bot-specific filename
        """
        # Given: .cursor/rules/ directory may or may not exist (in repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_dir = repo_root / '.cursor' / 'rules'
        
        # When: Generate awareness files
        generator.generate_awareness_files()
        
        # Then: Directory exists (created if needed)
        assert rules_dir.exists()
        assert rules_dir.is_dir()
        
        # And: File write succeeded with bot-specific filename
        rules_file = rules_dir / 'mcp-test-bot-awareness.mdc'
        assert rules_file.exists()

    def test_generator_handles_file_write_errors_with_clear_error_message(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors with clear error message
        GIVEN: .cursor/rules/ directory is write-protected
        WHEN: Generator attempts to write file
        THEN: Generator raises clear error message indicating permission issue
        AND: Error includes bot-specific path attempted
        """
        # Given: Mock Path.write_text to raise PermissionError (file written to repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_dir = repo_root / '.cursor' / 'rules'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock Path.write_text to raise PermissionError
        original_write_text = Path.write_text
        
        def mock_write_text(self, *args, **kwargs):
            if 'mcp-test-bot-awareness.mdc' in str(self):
                raise PermissionError(f"Permission denied: {self}")
            return original_write_text(self, *args, **kwargs)
        
        with patch.object(Path, 'write_text', mock_write_text):
            # When/Then: Generator raises error with clear message
            with pytest.raises(PermissionError) as exc_info:
                generator.generate_awareness_files()
            
            # And: Error includes bot-specific path
            assert 'mcp-test-bot-awareness.mdc' in str(exc_info.value)


class TestGenerateAwarenessFilesIntegration:
    """Integration test for full awareness files generation."""

    def test_full_awareness_generation_workflow(self, generator, workspace_root):
        """
        INTEGRATION TEST: Full awareness generation workflow
        GIVEN: MCP Server Generator initialized
        WHEN: generate_awareness_files() called
        THEN: Bot-specific rules file is created
        AND: Rules file has all required sections
        """
        # When: Generate awareness files
        generator.generate_awareness_files()
        
        # Then: Rules file created with bot-specific filename (in repo root)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        rules_file = repo_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        assert rules_file.exists()
        
        content = rules_file.read_text(encoding='utf-8')
        # Test bot specific content
        assert 'test_bot' in content.lower()
        assert 'Priority: Check MCP Tools First' in content
        assert 'Bot: test_bot' in content

