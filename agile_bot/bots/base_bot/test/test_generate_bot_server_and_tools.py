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

def create_base_actions_structure(workspace: Path):
    """Helper: Create base_actions directory structure with 6 workflow actions."""
    base_actions_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    actions = [
        ('1_initialize_project', 'decide_planning_criteria'),
        ('2_gather_context', 'decide_planning_criteria'),
        ('3_decide_planning_criteria', 'build_knowledge'),
        ('4_build_knowledge', 'render_output'),
        ('5_render_output', 'validate_rules'),
        ('7_validate_rules', None)
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

def create_base_instructions(workspace: Path):
    """Helper: Create base instructions for all actions."""
    actions = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'render_output', 'validate_rules', 'correct_bot']
    for action in actions:
        action_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action
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
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    
    # Create bot config file
    bot_name = 'test_bot'
    config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({
        'name': bot_name,
        'behaviors': ['shape', 'discovery']
    }), encoding='utf-8')
    
    gen = MCPServerGenerator(
        workspace_root=workspace_root,
        bot_location='agile_bot/bots/test_bot'
    )
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
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.bot_tool_generator import BotToolGenerator
        generator = BotToolGenerator(
            bot_name='test_bot',
            config_path=bot_config,
            workspace_root=workspace_root
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
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.behavior_tool_generator import BehaviorToolGenerator
        generator = BehaviorToolGenerator(
            bot_name='test_bot',
            config_path=bot_config,
            workspace_root=workspace_root
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
        
        # When: MCP Server Generator receives Bot Config (generates files)
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
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
        
        # When: MCP Server Generator attempts to receive Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        
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
        
        # When: MCP Server Generator attempts to receive Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        
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
        GIVEN: Bot with 4 behaviors, each behavior has 6 base actions configured
        WHEN: Generator processes Bot Config
        THEN: Generator creates 24 tool instances with unique names
        """
        # Given: Bot with 4 behaviors configured, each has 6 base actions
        bot_name = 'test_bot'
        behaviors = ['shape', 'discovery', 'exploration', 'specification']
        create_base_actions_structure(workspace_root)
        config_file = create_bot_config(workspace_root, bot_name, behaviors)
        
        # When: Generator processes Bot Config
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        mcp_server = generator.create_server_instance()
        generator.register_all_behavior_action_tools(mcp_server)
        
        # Then: Generator enumerates 24 (behavior, action) pairs
        assert len(generator.registered_tools) == 29  # 1 bot_tool + 4 behavior_tools + (4 behaviors × 6 actions)
        
        # And Generator creates 24 tool instances with unique names
        tool_names = [tool['name'] for tool in generator.registered_tools]
        assert 'test_bot_shape_gather_context' in tool_names
        assert 'test_bot_discovery_build_knowledge' in tool_names
        
        # And each tool includes forwarding logic to invoke Bot.Behavior.Action
        # (verified by tool registration)

    def test_generator_loads_trigger_words_from_behavior_folder(self, workspace_root):
        """
        SCENARIO: Generator loads trigger words from behavior folder
        GIVEN: Behavior has trigger_words.json with patterns
        WHEN: Generator creates tool for behavior action pair
        THEN: Tool is registered with trigger patterns in description
        """
        # Given: Trigger words file exists
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        patterns = ['shape.*story', 'start.*mapping', 'story.*discovery']
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        trigger_file = create_trigger_words_file(workspace_root, bot_name, behavior, action, patterns)
        
        # When: Call REAL MCPServerGenerator to register tool with trigger words
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        mcp_server = generator.create_server_instance()
        generator.register_behavior_action_tool(
            mcp_server=mcp_server,
            behavior=behavior,
            action=action
        )
        
        # Then: Tool registered with trigger patterns
        tool_name = f'{bot_name}_{behavior}_{action}'
        tool = next(t for t in generator.registered_tools if t['name'] == tool_name)
        assert tool['name'] == 'test_bot_shape_gather_context'
        assert 'shape.*story' in tool['description']
        assert 'shape.*story' in tool['trigger_patterns']

    def test_generator_handles_missing_trigger_words(self, workspace_root):
        """
        SCENARIO: Generator handles missing trigger words file
        GIVEN: Action does not have trigger_words.json
        WHEN: Generator creates tool
        THEN: Tool registered without trigger patterns
        """
        # Given: No trigger words file exists
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        
        # When: Call REAL MCPServerGenerator (trigger words missing)
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        mcp_server = generator.create_server_instance()
        generator.register_behavior_action_tool(
            mcp_server=mcp_server,
            behavior=behavior,
            action=action
        )
        
        # Then: Tool registered without trigger patterns (graceful handling)
        tool_name = f'{bot_name}_{behavior}_{action}'
        tool = next(t for t in generator.registered_tools if t['name'] == tool_name)
        assert tool['name'] == 'test_bot_shape_gather_context'
        assert tool['trigger_patterns'] == []

    @pytest.mark.asyncio
    async def test_generator_registers_tool_with_forwarding_to_bot_behavior_action(self, workspace_root):
        """
        SCENARIO: Generator registers tool with forwarding logic
        GIVEN: Bot has behavior with action
        WHEN: Generator registers tool with FastMCP
        THEN: Tool forwards invocation to Bot.Behavior.Action
        """
        # Given: Bot configuration
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        
        # When: Call REAL MCPServerGenerator to register tool
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        generator = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location=f'agile_bot/bots/{bot_name}'
        )
        mcp_server = generator.create_server_instance()
        
        # Mock the bot to verify forwarding
        from agile_bot.bots.base_bot.src.bot.bot import BotResult
        mock_bot = Mock()
        mock_bot.shape.gather_context = Mock(return_value=BotResult('completed', 'shape', 'gather_context', {'result': 'success'}))
        generator.bot = mock_bot
        
        generator.register_behavior_action_tool(
            mcp_server=mcp_server,
            behavior=behavior,
            action=action
        )
        
        # Then: Tool registered and callable through FastMCP
        assert any(t['name'] == 'test_bot_shape_gather_context' for t in generator.registered_tools)
        
        # Test tool invocation through FastMCP client
        create_base_instructions(workspace_root)
        async with Client(mcp_server) as client:
            result = await client.call_tool('test_bot_shape_gather_context', {})
            
            # Verify result contains BotResult structure
            result_dict = json.loads(result.content[0].text)
            assert result_dict['status'] == 'completed'
            assert result_dict['behavior'] == 'shape'
            assert result_dict['action'] == 'gather_context'


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
        assert deployment_result.tool_count == 24  # 4 behaviors x 6 actions
        assert deployment_result.catalog_published is True

    def test_server_publishes_tool_catalog_with_metadata(self, workspace_root):
        """
        SCENARIO: Server publishes tool catalog with complete metadata
        GIVEN: Tool has trigger patterns and description
        WHEN: Server publishes catalog
        THEN: Catalog entry includes all metadata
        """
        # Given: Tool with complete metadata
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'gather_context'
        patterns = ['shape.*story', 'start.*mapping']
        
        config_file = create_bot_config(workspace_root, bot_name, [behavior])
        create_trigger_words_file(workspace_root, bot_name, behavior, action, patterns)
        
        # When: Call REAL ServerDeployer API to get catalog
        from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
        deployer = ServerDeployer(
            config_path=config_file,
            workspace_root=workspace_root
        )
        catalog = deployer.get_tool_catalog()
        
        # Then: Catalog includes tool with complete metadata
        tool_entry = catalog.get_tool('test_bot_shape_gather_context')
        assert tool_entry.name == 'test_bot_shape_gather_context'
        assert tool_entry.trigger_patterns == patterns
        assert tool_entry.behavior == 'shape'
        assert tool_entry.action == 'gather_context'
        assert hasattr(tool_entry, 'description')

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
        
        # When: Generate awareness files
        from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
        gen = MCPServerGenerator(
            workspace_root=workspace_root,
            bot_location='agile_bot/bots/test_bot'
        )
        gen.generate_awareness_files()
        
        # Then: Rules file created with BOT-SPECIFIC filename
        rules_file = workspace_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        assert rules_file.exists(), f"Expected bot-specific file: {rules_file}"
        
        # And: Generic filename should NOT exist
        generic_file = workspace_root / '.cursor' / 'rules' / 'mcp-tool-awareness.mdc'
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
        gen = MCPServerGenerator(workspace_root=workspace_root, bot_location='agile_bot/bots/test_bot')
        gen.generate_awareness_files()
        
        # Then: Critical rule mentions SPECIFIC bot name
        rules_file = workspace_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
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
        gen = MCPServerGenerator(workspace_root=workspace_root, bot_location='agile_bot/bots/test_bot')
        gen.generate_awareness_files()
        
        # Then: File has behavior sections with tool patterns
        rules_file = workspace_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
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
        # Given: .cursor/rules/ directory does not exist
        rules_dir = workspace_root / '.cursor' / 'rules'
        assert not rules_dir.exists()
        
        # When: Generate awareness files
        generator.generate_awareness_files()
        
        # Then: Directory created
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
        # Given: Create directory but make it read-only
        rules_dir = workspace_root / '.cursor' / 'rules'
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
        
        # Then: Rules file created with bot-specific filename
        rules_file = workspace_root / '.cursor' / 'rules' / 'mcp-test-bot-awareness.mdc'
        assert rules_file.exists()
        
        content = rules_file.read_text(encoding='utf-8')
        # Test bot specific content
        assert 'test_bot' in content.lower()
        assert 'Priority: Check MCP Tools First' in content
        assert 'Bot: test_bot' in content

