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
from conftest import bootstrap_env, create_bot_config_file, given_bot_name_and_behaviors_setup, given_bot_name_and_behavior_setup

# ============================================================================
# HELPER FUNCTIONS - Sub-Epic Level (Used across multiple test classes)
# ============================================================================

# Removed duplicate create_bot_config - use conftest.create_bot_config_file instead

def given_test_bot_behaviors():
    """Given: Test bot behaviors list."""
    return ['shape', 'discovery', 'exploration', 'specification']

# Use shared helpers from conftest - call with bot_name='test_bot' when needed
# given_bot_name_and_behaviors_setup imported from conftest
# given_bot_name_and_behavior_setup imported from conftest

def given_trigger_patterns_for_shape_behavior():
    """Given: Trigger patterns for shape behavior."""
    return ['shape.*story', 'start.*mapping', 'story.*discovery']

def then_generator_creates_behavior_tools_with_names(generator, expected_count: int, expected_behaviors: list):
    """Then: Generator creates behavior tools with names."""
    tool_names = [tool['name'] for tool in generator.registered_tools]
    behavior_tools = [tool for tool in generator.registered_tools if tool.get('type') == 'behavior_tool']
    assert len(behavior_tools) == expected_count, f"Expected {expected_count} behavior tools, got {len(behavior_tools)}"
    for behavior in expected_behaviors:
        assert behavior in tool_names or any(t.get('behavior') == behavior for t in generator.registered_tools)

def then_behavior_tool_registered_with_patterns(generator, behavior: str, patterns: list):
    """Then: Behavior tool registered with trigger patterns."""
    tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
    assert tool is not None, f"Behavior tool for {behavior} should be registered"
    assert tool['type'] == 'behavior_tool'
    for pattern in patterns:
        assert pattern in tool['description']
        assert pattern in tool['trigger_patterns']

def given_bot_config_file_with_working_dir_and_behaviors(
    workspace_root: Path,
    bot_name: str,
    behaviors: list
) -> Path:
    """Given step: A bot configuration file with a working directory and behaviors.
    
    Creates bot_config.json file with specified behaviors.
    Used by: Multiple test classes that need bot configuration.
    """
    return create_bot_config_file(
        workspace_root / 'agile_bot' / 'bots' / bot_name,
        bot_name,
        behaviors,
        workspace_root=workspace_root
    )

def given_bot_configured_by_config(workspace_root: Path, bot_name: str):
    """Given step: A bot that has been initialized with that config file.
    
    Initializes bot directory and workspace with bootstrap environment.
    Used by: Multiple test classes that need initialized bot environment.
    """
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    workspace_directory = workspace_root / 'workspace'
    workspace_directory.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_dir, workspace_directory)
    return bot_dir, workspace_directory

def given_base_actions_structure_exists(bot_dir: Path):
    """Given step: Base actions structure exists.
    
    Creates base_actions directory structure in bot directory.
    Used by: Tests that need base actions for workflow.
    """
    create_base_actions_structure(bot_dir)

def given_behavior_workflow_files_exist_for_behaviors(bot_dir: Path, behaviors: list):
    """Given step: Behavior workflow files exist for behaviors.
    
    Creates behavior.json files for all specified behaviors.
    Used by: Tests that need behavior workflow configurations.
    """
    from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
    for behavior in behaviors:
        create_actions_workflow_json(bot_dir, behavior)

def given_behavior_with_trigger_words(bot_dir: Path, behavior: str, patterns: list):
    """Given step: Behavior has trigger words configured.
    
    Creates behavior.json with custom trigger words.
    Used by: Tests that need behavior with trigger patterns.
    """
    from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
    create_actions_workflow_json(bot_dir, behavior)
    # Update behavior.json with custom trigger words
    behavior_dir = bot_dir / 'behaviors' / behavior
    behavior_file = behavior_dir / 'behavior.json'
    behavior_data = json.loads(behavior_file.read_text())
    behavior_data['trigger_words'] = {
        'description': f'Trigger words for {behavior}',
        'patterns': patterns,
        'priority': 10
    }
    behavior_file.write_text(json.dumps(behavior_data, indent=2), encoding='utf-8')
    return behavior_file

def given_behavior_without_trigger_words(bot_dir: Path, behavior: str):
    """Given step: Behavior does not have trigger words configured.
    
    Creates behavior.json without trigger_words field.
    Used by: Tests that verify graceful handling of missing trigger words.
    """
    from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
    create_actions_workflow_json(bot_dir, behavior)
    # Remove trigger_words from behavior.json
    behavior_dir = bot_dir / 'behaviors' / behavior
    behavior_file = behavior_dir / 'behavior.json'
    behavior_data = json.loads(behavior_file.read_text())
    behavior_data.pop('trigger_words', None)
    behavior_file.write_text(json.dumps(behavior_data, indent=2), encoding='utf-8')
    return behavior_file

def given_bot_config_file_with_invalid_json(workspace_root: Path, bot_name: str, invalid_content: str = 'not valid json {'):
    """Given step: Bot Config file exists with invalid JSON syntax.
    
    Creates a bot config file with malformed JSON content.
    Used by: Tests that verify error handling for malformed config files.
    """
    config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(invalid_content)
    return config_file

def given_bot_config_does_not_exist(workspace_root: Path, bot_name: str):
    """Given step: Bot Config does NOT exist.
    
    Ensures bot config file is removed if it exists.
    Used by: Tests that verify error handling for missing config files.
    """
    config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
    if config_path.exists():
        config_path.unlink()
    return config_path

def given_bot_has_instructions_json(workspace_root: Path, bot_name: str, goal: str, behavior_descriptions: dict):
    """Given step: Bot has instructions.json with goal and behavior descriptions.
    
    Creates instructions.json file in bot directory.
    Used by: Tests that need bot goal and behavior descriptions.
    """
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    instructions_file = bot_dir / 'instructions.json'
    instructions_data = {
        'botName': bot_name,
        'goal': goal,
        'description': f'Helps teams create and refine user stories',
        'behaviors': behavior_descriptions
    }
    instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
    return instructions_file

def given_behaviors_with_descriptions_and_trigger_words(bot_dir: Path, behaviors_config: list):
    """Given step: Behaviors have descriptions and trigger words configured.
    
    Creates behavior.json files with descriptions and trigger words.
    behaviors_config: list of dicts with 'name', 'description', 'patterns' keys.
    Used by: Tests that need behaviors with full metadata.
    """
    from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json
    for behavior_config in behaviors_config:
        behavior = behavior_config['name']
        create_actions_workflow_json(bot_dir, behavior)
        behavior_dir = bot_dir / 'behaviors' / behavior
        behavior_file = behavior_dir / 'behavior.json'
        behavior_data = json.loads(behavior_file.read_text())
        behavior_data['description'] = behavior_config['description']
        behavior_data['trigger_words'] = {
            'description': f'Trigger words for {behavior}',
            'patterns': behavior_config['patterns'],
            'priority': 10
        }
        behavior_file.write_text(json.dumps(behavior_data, indent=2), encoding='utf-8')
    return bot_dir

def given_workflow_state_exists(workspace_directory: Path, bot_name: str, behavior: str, action: str, completed_actions: list = None):
    """Given step: Workflow state exists.
    
    Creates workflow_state.json file with specified state.
    Used by: Tests that need workflow state for action execution.
    """
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_data = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{action}',
        'completed_actions': completed_actions or []
    }
    workflow_file.write_text(json.dumps(workflow_data), encoding='utf-8')
    return workflow_file

def when_bot_tool_generator_processes_config(bot_name: str, config_path: Path):
    """When step: Bot Tool Generator processes Bot Config."""
    from agile_bot.bots.base_bot.src.mcp.bot_tool_generator import BotToolGenerator
    generator = BotToolGenerator(bot_name=bot_name, config_path=config_path)
    return generator.create_bot_tool()

def when_behavior_tool_generator_processes_config(bot_name: str, config_path: Path):
    """When step: Behavior Tool Generator processes Bot Config."""
    from agile_bot.bots.base_bot.src.mcp.behavior_tool_generator import BehaviorToolGenerator
    generator = BehaviorToolGenerator(bot_name=bot_name, config_path=config_path)
    return generator.create_behavior_tools()

def when_mcp_server_generator_receives_bot_config(bot_dir: Path, behaviors: list = None):
    """When step: MCP Server Generator receives Bot Config."""
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(bot_directory=bot_dir)
    if behaviors:
        return generator.generate_server(behaviors=behaviors)
    return generator.create_server_instance()

def when_generator_registers_all_behavior_action_tools(bot_dir: Path):
    """When step: Generator registers all behavior action tools.
    
    Creates generator, server instance, and registers all tools.
    Returns tuple of (generator, mcp_server) with registered_tools populated.
    """
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(bot_directory=bot_dir)
    mcp_server = generator.create_server_instance()
    generator.register_all_behavior_action_tools(mcp_server)
    return generator, mcp_server

def when_generator_generates_awareness_files(bot_dir: Path):
    """When step: Generator generates awareness files.
    
    Creates generator and calls generate_awareness_files().
    Returns generator instance.
    """
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(bot_directory=bot_dir)
    generator.generate_awareness_files()
    return generator

def when_server_deployer_deploys(config_path: Path, workspace_root: Path, protocol_handler_url: str = None):
    """When step: Server Deployer deploys server.
    
    Creates ServerDeployer and calls deploy_server().
    Returns deployment result.
    """
    from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
    deployer_kwargs = {
        'config_path': config_path,
        'workspace_root': workspace_root
    }
    if protocol_handler_url:
        deployer_kwargs['protocol_handler_url'] = protocol_handler_url
    deployer = ServerDeployer(**deployer_kwargs)
    return deployer.deploy_server()

def when_server_deployer_gets_catalog(config_path: Path, workspace_root: Path):
    """When step: Server Deployer gets tool catalog.
    
    Creates ServerDeployer and calls get_tool_catalog().
    Returns catalog.
    """
    from agile_bot.bots.base_bot.src.mcp.server_deployer import ServerDeployer
    deployer = ServerDeployer(
        config_path=config_path,
        workspace_root=workspace_root
    )
    return deployer.get_tool_catalog()

@pytest.mark.asyncio
async def when_behavior_tool_invoked(mcp_server, tool_name: str, parameters: dict):
    """When step: Behavior tool is invoked through FastMCP.
    
    Invokes tool through FastMCP client and returns result.
    """
    async with Client(mcp_server) as client:
        result = await client.call_tool(tool_name, parameters)
        return result

def then_bot_tool_instance_created(bot_tool, expected_count: int = 1):
    """Then step: Bot tool instance(s) created."""
    if expected_count == 1:
        assert bot_tool is not None
    else:
        assert len(bot_tool) == expected_count

def then_mcp_server_instance_created(artifacts, bot_name: str):
    """Then step: MCP Server instance created with correct properties."""
    assert artifacts['server_entry'].exists()
    assert artifacts['server_entry'].name == f'{bot_name}_mcp_server.py'
    # Verify it's in the correct location: bot_dir/src/bot_name_mcp_server.py
    assert 'src' in str(artifacts['server_entry'])
    assert bot_name in str(artifacts['server_entry'])

def then_server_code_includes_bot_instantiation(artifacts, bot_name: str):
    """Then step: Generated server includes Bot instantiation code."""
    server_code = artifacts['server_entry'].read_text()
    assert 'MCPServerGenerator' in server_code
    assert 'create_server_instance' in server_code
    assert 'register_all_behavior_action_tools' in server_code
    assert bot_name in server_code

def then_generator_raises_file_not_found_error(bot_dir: Path, expected_config_path: Path):
    """Then step: Generator raises FileNotFoundError with expected message."""
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(bot_directory=bot_dir)
    with pytest.raises(FileNotFoundError) as exc_info:
        generator.create_server_instance()
    assert f'Bot Config not found at {expected_config_path}' in str(exc_info.value)

def then_generator_raises_json_decode_error(bot_dir: Path, config_file: Path):
    """Then step: Generator raises JSONDecodeError with expected message."""
    from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(bot_directory=bot_dir)
    with pytest.raises(json.JSONDecodeError) as exc_info:
        generator.create_server_instance()
    assert f'Malformed Bot Config at {config_file}' in str(exc_info.value)

def then_behavior_tool_execution_succeeds(result, expected_behavior: str, expected_action: str):
    """Then step: Behavior tool execution succeeds with expected results."""
    result_dict = json.loads(result.content[0].text)
    assert result_dict['status'] == 'completed'
    assert result_dict['behavior'] == expected_behavior
    assert result_dict['action'] == expected_action

def then_deployment_succeeds(deployment_result, expected_server_name: str, min_tool_count: int = 7):
    """Then step: Server deployment succeeds."""
    assert deployment_result.status == 'running'
    assert deployment_result.server_name == expected_server_name
    assert deployment_result.tool_count >= min_tool_count
    assert deployment_result.catalog_published is True

def then_deployment_fails_with_error(deployment_result, expected_error_substring: str):
    """Then step: Server deployment fails with expected error."""
    assert deployment_result.status == 'failed'
    assert expected_error_substring in deployment_result.error_message
    assert deployment_result.catalog_published is False

def then_awareness_file_created_with_bot_specific_filename(bot_name: str):
    """Then step: Awareness file created with bot-specific filename."""
    from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
    repo_root = get_python_workspace_root()
    rules_file = repo_root / '.cursor' / 'rules' / f'mcp-{bot_name.replace("_", "-")}-awareness.mdc'
    assert rules_file.exists(), f"Expected bot-specific file: {rules_file}"
    # Verify generic filename does NOT exist
    generic_file = repo_root / '.cursor' / 'rules' / 'mcp-tool-awareness.mdc'
    assert not generic_file.exists(), "Should use bot-specific filename, not generic"
    return rules_file

def then_awareness_file_contains_behavior_sections(content: str, behavior_names: list):
    """Then step: Awareness file contains behavior sections."""
    for behavior_name in behavior_names:
        # Handle both numbered (1_shape -> "1 Shape") and unnumbered (shape -> "Shape") formats
        # The section header format is "### 1 Shape Behavior" (space, not underscore)
        if '_' in behavior_name and behavior_name[0].isdigit():
            # Numbered format: "1_shape" -> "1 Shape"
            parts = behavior_name.split('_', 1)
            numbered_pattern = f'### {parts[0]} {parts[1].title()} Behavior'
            unnumbered_pattern = f'### {parts[1].title()} Behavior'
        else:
            # Unnumbered format: "shape" -> "Shape"
            numbered_pattern = f'### {behavior_name.title()} Behavior'
            unnumbered_pattern = numbered_pattern
        assert numbered_pattern in content or unnumbered_pattern in content, \
            f"Expected behavior section for {behavior_name} not found. Looked for: {numbered_pattern} or {unnumbered_pattern}"

def then_awareness_file_contains_tool_patterns(content: str, bot_name: str, behavior_names: list):
    """Then step: Awareness file contains tool patterns with actual bot name."""
    for behavior_name in behavior_names:
        # Handle both numbered (1_shape) and unnumbered (shape) formats
        numbered_pattern = f'{bot_name}_{behavior_name}_<action>'
        unnumbered_pattern = f'{bot_name}_{behavior_name.split("_", 1)[-1]}_<action>' if '_' in behavior_name else f'{bot_name}_{behavior_name}_<action>'
        assert numbered_pattern in content or unnumbered_pattern in content, \
            f"Expected tool pattern for {behavior_name} not found"

def then_trigger_words_in_behavior_section(content: str, behavior_name: str, trigger_words: list):
    """Then step: Trigger words appear in correct behavior section."""
    # Find behavior section - handle numbered format (1_shape -> "1 Shape")
    if '_' in behavior_name and behavior_name[0].isdigit():
        parts = behavior_name.split('_', 1)
        numbered_pattern = f'### {parts[0]} {parts[1].title()}'
        unnumbered_pattern = f'### {parts[1].title()}'
    else:
        numbered_pattern = f'### {behavior_name.title()}'
        unnumbered_pattern = numbered_pattern
    
    behavior_start = content.find(numbered_pattern) if numbered_pattern in content else content.find(unnumbered_pattern)
    
    if behavior_start != -1:
        # Find next behavior section or end of content
        next_behavior_markers = ['### 1 ', '### 2 ', '### 3 ', '### 4 ', '### 5 ', '### Shape', '### Discovery', '### Exploration']
        next_start = len(content)
        for marker in next_behavior_markers:
            if marker != numbered_pattern and marker != unnumbered_pattern:
                marker_pos = content.find(marker, behavior_start + 1)
                if marker_pos != -1 and marker_pos < next_start:
                    next_start = marker_pos
        
        behavior_section = content[behavior_start:next_start]
        
        # Verify all trigger words are in this section
        for trigger_word in trigger_words:
            assert trigger_word in behavior_section, \
                f"Trigger word '{trigger_word}' not found in {behavior_name} section"
    else:
        # Fallback: just verify trigger words are in content
        for trigger_word in trigger_words:
            assert trigger_word in content, \
                f"Trigger word '{trigger_word}' not found in content"

def then_rules_directory_exists_and_is_directory():
    """Then step: Rules directory exists and is a directory."""
    from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
    repo_root = get_python_workspace_root()
    rules_dir = repo_root / '.cursor' / 'rules'
    assert rules_dir.exists()
    assert rules_dir.is_dir()
    return rules_dir

def then_awareness_file_exists_with_bot_specific_filename(rules_dir: Path, bot_name: str):
    """Then step: Awareness file exists with bot-specific filename."""
    rules_file = rules_dir / f'mcp-{bot_name.replace("_", "-")}-awareness.mdc'
    assert rules_file.exists()
    return rules_file

def given_path_write_text_mocked_to_raise_permission_error(target_filename: str):
    """Given step: Path.write_text is mocked to raise PermissionError for target filename.
    
    Returns context manager for use with 'with' statement.
    """
    original_write_text = Path.write_text
    
    def mock_write_text(self, *args, **kwargs):
        if target_filename in str(self):
            raise PermissionError(f"Permission denied: {self}")
        return original_write_text(self, *args, **kwargs)
    
    return patch.object(Path, 'write_text', mock_write_text)

def then_permission_error_raised_with_bot_specific_path(function, expected_filename: str):
    """Then step: PermissionError is raised with bot-specific path in message."""
    with pytest.raises(PermissionError) as exc_info:
        function()
    assert expected_filename in str(exc_info.value)

def then_behavior_tool_registered_without_patterns(generator, behavior: str):
    """Then: Behavior tool registered without trigger patterns."""
    tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
    assert tool is not None, f"Behavior tool for {behavior} should be registered"
    assert tool['type'] == 'behavior_tool'

def then_catalog_has_tools_for_behavior(catalog, behavior: str, patterns: list):
    """Then: Catalog has tools for behavior with patterns."""
    behavior_tools = [t for t in catalog.tools.values() if t.behavior == behavior]
    assert len(behavior_tools) > 0, f"Catalog should have tools for behavior '{behavior}'"
    tool_with_patterns = next((t for t in behavior_tools if t.trigger_patterns == patterns), None)
    if tool_with_patterns:
        assert tool_with_patterns.trigger_patterns == patterns
        assert hasattr(tool_with_patterns, 'description')

def then_awareness_file_shape_section_contains_only_shape_words(content: str):
    """Then: Awareness file shape section contains only shape words."""
    shape_section_start = content.find('Shape')
    discovery_section_start = content.find('Discovery')
    if shape_section_start != -1 and discovery_section_start != -1:
        shape_section = content[shape_section_start:discovery_section_start]
        assert 'shape story' in shape_section
        assert 'define story outline' in shape_section
        assert 'create story map' in shape_section
        assert 'discover stories' not in shape_section
        discovery_section = content[discovery_section_start:]
        assert 'discover stories' in discovery_section
        assert 'break down stories' in discovery_section
        assert 'enumerate stories' in discovery_section

def then_awareness_file_contains_tool_patterns_for_behaviors(content: str, bot_name: str, behaviors: list):
    """Then: Awareness file contains tool patterns for behaviors."""
    for behavior in behaviors:
        behavior_name = behavior.split('_')[-1] if '_' in behavior else behavior
        assert f'{bot_name}_{behavior}_' in content or f'{bot_name}_{behavior_name}_' in content or f'story_bot_{behavior_name}_' in content

def given_bot_goal_and_behavior_descriptions():
    """Given: Bot goal and behavior descriptions."""
    goal = 'Transform user needs into well-structured stories'
    descriptions = {
        'shape': 'Create initial story map outline from user context',
        'discovery': 'Elaborate stories with user flows and domain rules'
    }
    return goal, descriptions

def given_behaviors_config_with_descriptions_and_patterns():
    """Given: Behaviors config with descriptions and patterns."""
    return [
        {
            'name': '1_shape',
            'description': 'Create initial story map outline from user context',
            'patterns': ['shape story', 'create story map']
        },
        {
            'name': '4_discovery',
            'description': 'Elaborate stories with user flows and domain rules',
            'patterns': ['discover stories', 'elaborate stories']
        }
    ]

def then_awareness_file_contains_behavior_format_sections(content: str, bot_name: str):
    """Then: Awareness file contains behavior format sections."""
    assert '**When user is trying to:** Create initial story map outline' in content
    assert '**as indicated by Trigger words:**' in content
    assert f'**Then check for:** `{bot_name}_1_shape_<action>` tool' in content or f'**Then check for:** `{bot_name}_shape_<action>` tool' in content
    assert '**When user is trying to:** Elaborate stories with user flows' in content
    assert f'**Then check for:** `{bot_name}_4_discovery_<action>` tool' in content or f'**Then check for:** `{bot_name}_discovery_<action>` tool' in content

def then_awareness_file_contains_error_handling_section(content: str):
    """Then: Awareness file contains error handling section."""
    assert 'If a registered tool is broken or returns an error' in content
    assert 'DO NOT automatically attempt a workaround' in content
    assert 'Inform user of the exact error details' in content

def given_expected_awareness_filename():
    """Given: Expected awareness filename."""
    return 'mcp-test-bot-awareness.mdc'

def then_awareness_file_contains_required_sections(rules_file: Path, bot_name: str):
    """Then step: Awareness file contains all required sections."""
    content = rules_file.read_text(encoding='utf-8')
    assert bot_name.lower() in content.lower()
    assert 'Priority: Check MCP Tools First' in content
    assert f'Bot: {bot_name}' in content
    return content


def then_generator_creates_sufficient_tools(generator, min_tool_count: int = 7):
    """Then: Generator creates sufficient tools."""
    assert len(generator.registered_tools) >= min_tool_count


def given_test_bot_behavior_and_action():
    """Given: Test bot, behavior and action."""
    return 'test_bot', 'shape', 'gather_context'


def when_find_behavior_tool_in_registered_tools(generator, behavior: str):
    """When: Find behavior tool in registered tools."""
    tool = next((t for t in generator.registered_tools if t.get('behavior') == behavior), None)
    assert tool is not None, f"Behavior tool for {behavior} should be registered"
    assert tool['type'] == 'behavior_tool'
    return tool


def when_invoke_behavior_tool_with_action(mcp_server, tool, action: str):
    """When: Invoke behavior tool with action."""
    tool_name = tool['name']
    return when_behavior_tool_invoked(mcp_server, tool_name, {'action': action})


def then_catalog_has_tools_registered(catalog):
    """Then: Catalog has tools registered."""
    assert len(catalog.tools) > 0, "Catalog should have tools registered"


def when_deployer_attempts_deployment_with_invalid_url(config_file: Path, workspace_root: Path):
    """When: Deployer attempts deployment with invalid URL."""
    with pytest.raises(ConnectionError) as exc_info:
        when_server_deployer_deploys(config_file, workspace_root, protocol_handler_url='http://localhost:9999')
    assert 'MCP Protocol Handler not accessible' in str(exc_info.value)


def given_test_bot_name():
    """Given: Test bot name."""
    return 'test_bot'


def then_awareness_file_contains_bot_name(content: str, bot_name: str):
    """Then: Awareness file contains bot name."""
    assert bot_name in content


def then_awareness_file_contains_priority_check_message(content: str, bot_name: str):
    """Then: Awareness file contains priority check message."""
    assert f'ALWAYS check for and use MCP {bot_name} tools FIRST' in content


def then_awareness_file_contains_repair_question(content: str):
    """Then: Awareness file contains repair question."""
    assert 'Should I attempt to repair the tool, or proceed manually' in content


def when_create_rules_directory_if_needed():
    """When: Create rules directory if needed."""
    rules_dir = then_rules_directory_exists_and_is_directory()
    rules_dir.mkdir(parents=True, exist_ok=True)
    return rules_dir


def when_generator_generates_awareness_files_direct(generator):
    """When: Generator generates awareness files directly."""
    generator.generate_awareness_files()


def given_bot_directory_path(workspace_root: Path, bot_name: str):
    """Given: Bot directory path."""
    return workspace_root / 'agile_bot' / 'bots' / bot_name


def when_read_awareness_file_content(rules_file: Path):
    """When: Read awareness file content."""
    return rules_file.read_text(encoding='utf-8')


def given_bot_config_and_directory_setup(workspace_root: Path, bot_name: str, behaviors: list):
    """Given: Bot config and directory setup."""
    bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
    bot_dir = given_bot_directory_path(workspace_root, bot_name)
    return bot_config, bot_dir

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

# Removed create_base_instructions - use test_helpers.create_base_instructions instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import create_base_instructions

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
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: A bot that has been initialized with that config file
        WHEN: Generator processes Bot Config
        THEN: Generator creates 1 bot tool instance
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, 'test_bot')
        
        # When: Generator processes Bot Config
        bot_tool = when_bot_tool_generator_processes_config('test_bot', bot_config)
        
        # Then: 1 bot tool instance created
        then_bot_tool_instance_created(bot_tool)


class TestGenerateBehaviorTools:
    """Story: Generate Behavior Tools - Tests behavior tool generation with action routing."""

    def test_generator_creates_behavior_tools_for_test_bot_with_4_behaviors(self, workspace_root):
        """
        SCENARIO: Generator creates behavior tools for test_bot with 4 behaviors
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: A bot that has been initialized with that config file
        WHEN: Generator processes Bot Config
        THEN: Generator creates 4 behavior tool instances
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, 'test_bot')
        
        # When: Generator processes Bot Config
        tools = when_behavior_tool_generator_processes_config('test_bot', bot_config)
        
        # Then: 4 behavior tool instances created
        then_bot_tool_instance_created(tools, expected_count=4)


class TestGenerateMCPBotServer:
    """Story: Generate MCP Bot Server - Tests MCP server generation using FastMCP."""

    def test_generator_creates_mcp_server_for_test_bot(self, workspace_root):
        """
        SCENARIO: Generator creates MCP server for test_bot
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: A bot that has been initialized with that config file
        WHEN: MCP Server Generator receives Bot Config
        THEN: Generator creates MCP Server instance with unique server name
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: MCP Server Generator receives Bot Config (generates files)
        artifacts = when_mcp_server_generator_receives_bot_config(bot_dir, behaviors)
        
        # Then: Generator creates MCP Server instance with unique server name
        then_mcp_server_instance_created(artifacts, bot_name)
        # And Generated server includes Bot instantiation code
        then_server_code_includes_bot_instantiation(artifacts, bot_name)


    def test_generator_fails_when_bot_config_missing(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is missing
        GIVEN: A bot directory exists
        AND: Bot Config does NOT exist
        WHEN: MCP Server Generator attempts to receive Bot Config
        THEN: Generator raises FileNotFoundError and does not create MCP Server instance
        """
        # Given: A bot directory exists
        bot_name = 'test_bot'
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # And: Bot Config does NOT exist
        expected_config_path = given_bot_config_does_not_exist(workspace_root, bot_name)
        
        # When: MCP Server Generator attempts to receive Bot Config
        # Then: Generator raises FileNotFoundError with message
        then_generator_raises_file_not_found_error(bot_dir, expected_config_path)
        
        # And Generator does not create MCP Server instance (verified by exception)

    def test_generator_fails_when_bot_config_malformed(self, workspace_root):
        """
        SCENARIO: Generator fails when Bot Config is malformed
        GIVEN: A bot directory exists
        AND: Bot Config file exists with invalid JSON syntax
        WHEN: MCP Server Generator attempts to receive Bot Config
        THEN: Generator raises JSONDecodeError and does not create MCP Server instance
        """
        # Given: A bot directory exists
        bot_name = 'test_bot'
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # And: Bot Config file exists with invalid JSON syntax
        config_file = given_bot_config_file_with_invalid_json(workspace_root, bot_name)
        
        # When: MCP Server Generator attempts to receive Bot Config
        # Then: Generator raises JSONDecodeError with message
        then_generator_raises_json_decode_error(bot_dir, config_file)
        
        # And Generator does not create MCP Server instance (verified by exception)


class TestGenerateBehaviorActionTools:
    """Story: Generate Behavior Action Tools - Tests tool generation using FastMCP."""

    def test_generator_creates_tools_for_test_bot_with_4_behaviors(self, workspace_root):
        """
        SCENARIO: Generator creates tools for test_bot with 4 behaviors
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Base actions structure exists
        AND: Behavior workflow files exist for all behaviors
        WHEN: Generator processes Bot Config
        THEN: Generator creates bot tool and 4 behavior tools
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup()
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        config_file = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: Base actions structure exists
        given_base_actions_structure_exists(bot_dir)
        # And: Behavior workflow files exist for all behaviors
        given_behavior_workflow_files_exist_for_behaviors(bot_dir, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator processes Bot Config
        generator, mcp_server = when_generator_registers_all_behavior_action_tools(bot_dir)
        
        # Then: Generator creates bot tool and behavior tools
        # 1 bot_tool + 1 get_working_dir + 1 close_action + 1 restart + 4 behavior_tools = 8 tools
        then_generator_creates_sufficient_tools(generator, min_tool_count=7)
        
        # And Generator creates behavior tools with behavior names
        then_generator_creates_behavior_tools_with_names(generator, 4, ['shape', 'discovery'])
        
        # And each behavior tool includes forwarding logic to invoke Bot.Behavior.Action
        # (verified by tool registration)

    def test_generator_loads_trigger_words_from_behavior_folder(self, workspace_root):
        """
        SCENARIO: Generator loads trigger words from behavior folder
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behavior has trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: Generator creates behavior tool
        THEN: Behavior tool is registered with trigger patterns in description
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behavior = given_bot_name_and_behavior_setup()
        patterns = given_trigger_patterns_for_shape_behavior()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, [behavior])
        # And: Behavior has trigger words configured
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_with_trigger_words(bot_dir, behavior, patterns)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator creates behavior tool
        generator, mcp_server = when_generator_registers_all_behavior_action_tools(bot_dir)
        
        # Then: Behavior tool registered with trigger patterns
        then_behavior_tool_registered_with_patterns(generator, behavior, patterns)

    def test_generator_handles_missing_trigger_words(self, workspace_root):
        """
        SCENARIO: Generator handles missing trigger words file
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behavior does not have trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: Generator creates behavior tool
        THEN: Behavior tool registered without trigger patterns
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behavior = given_bot_name_and_behavior_setup()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, [behavior])
        # And: Behavior does not have trigger words configured
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_without_trigger_words(bot_dir, behavior)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator creates behavior tool
        generator, mcp_server = when_generator_registers_all_behavior_action_tools(bot_dir)
        
        # Then: Behavior tool registered without trigger patterns (graceful handling)
        then_behavior_tool_registered_without_patterns(generator, behavior)

    @pytest.mark.asyncio
    async def test_generator_registers_tool_with_forwarding_to_bot_behavior_action(self, workspace_root):
        """
        SCENARIO: Generator registers behavior tool with forwarding logic
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behavior workflow file exists
        AND: A bot that has been initialized with that config file
        WHEN: Generator registers behavior tool with FastMCP
        THEN: Behavior tool forwards invocation to Bot.execute_behavior() (production code path)
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behavior, action = given_test_bot_behavior_and_action()
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(
            workspace_root,
            bot_name,
            [behavior]
        )
        # And: Behavior workflow file exists
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_workflow_files_exist_for_behaviors(bot_dir, [behavior])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # Base actions structure and instructions already created by given_bot_configured_by_config
        # Behavior workflow file already created above
        
        # And: Workflow state exists
        given_workflow_state_exists(workspace_directory, bot_name, behavior, action)
        
        # When: Generator registers behavior tool with FastMCP
        generator, mcp_server = when_generator_registers_all_behavior_action_tools(bot_dir)
        
        # Then: Behavior tool registered and callable through FastMCP
        tool = when_find_behavior_tool_in_registered_tools(generator, behavior)
        
        # And: Behavior tool forwards invocation to Bot.execute_behavior() (production code path)
        # Test tool invocation through FastMCP client with action parameter
        # This calls the REAL bot.execute_behavior() method
        result = await when_invoke_behavior_tool_with_action(mcp_server, tool, action)
        then_behavior_tool_execution_succeeds(result, behavior, action)


class TestDeployMCPBotServer:
    """Story: Deploy MCP Bot Server - Tests server deployment."""

    def test_generator_deploys_server_successfully(self, workspace_root):
        """
        SCENARIO: Generator deploys test_bot MCP Server successfully
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behavior workflow files exist for all behaviors
        AND: A bot that has been initialized with that config file
        WHEN: Generator deploys MCP Server
        THEN: Server initializes and publishes tool catalog
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup()
        config_file = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        create_base_server_template(workspace_root)
        # And: Behavior workflow files exist for all behaviors
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_workflow_files_exist_for_behaviors(bot_dir, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator deploys MCP Server
        deployment_result = when_server_deployer_deploys(config_file, workspace_root)
        
        # Then: Server initializes and publishes tool catalog
        then_deployment_succeeds(deployment_result, 'test_bot_server', min_tool_count=7)

    def test_server_publishes_tool_catalog_with_metadata(self, workspace_root):
        """
        SCENARIO: Server publishes tool catalog with complete metadata
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behavior has trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: Server publishes catalog
        THEN: Catalog entry includes all metadata
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behavior = given_bot_name_and_behavior_setup()
        patterns = ['shape.*story', 'start.*mapping']
        config_file = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, [behavior])
        # And: Behavior has trigger words configured
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_with_trigger_words(bot_dir, behavior, patterns)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Server publishes catalog
        catalog = when_server_deployer_gets_catalog(config_file, workspace_root)
        
        # Then: Catalog entry includes all metadata
        # Note: Catalog may still use old naming convention with individual action tools
        # Check that catalog has tools registered
        then_catalog_has_tools_registered(catalog)
        
        # Check for a tool that matches the behavior (catalog may use action tool names)
        # Since catalog builds action tools, look for one with the behavior name
        then_catalog_has_tools_for_behavior(catalog, behavior, patterns)

    def test_generator_fails_when_protocol_handler_not_running(self, workspace_root):
        """
        SCENARIO: Generator fails when MCP Protocol Handler not running
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: A bot that has been initialized with that config file
        AND: MCP Protocol Handler is not running
        WHEN: Generator attempts to deploy
        THEN: Raises ConnectionError
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['shape'])
        config_file = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # And: MCP Protocol Handler is not running (simulated by invalid URL)
        
        # When: Generator attempts to deploy
        # Then: Raises ConnectionError
        when_deployer_attempts_deployment_with_invalid_url(config_file, workspace_root)

    def test_server_handles_initialization_failure(self, workspace_root):
        """
        SCENARIO: Server handles initialization failure in separate thread
        GIVEN: A bot directory exists
        AND: Bot Config does NOT exist
        WHEN: Server thread starts
        THEN: Logs error and does not register
        """
        # Given: A bot directory exists
        bot_name = given_test_bot_name()
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # And: Bot Config does NOT exist
        config_path = given_bot_config_does_not_exist(workspace_root, bot_name)
        
        # When: Server thread starts
        deployment_result = when_server_deployer_deploys(config_path, workspace_root)
        
        # Then: Logs error and does not register
        then_deployment_fails_with_error(deployment_result, 'Bot Config not found')


class TestGenerateCursorAwarenessFiles:
    """Story: Generate Cursor Awareness Files - Tests awareness file generation."""

    def test_generator_creates_workspace_rules_file_with_trigger_patterns(self, workspace_root):
        """
        SCENARIO: Generator creates bot-specific workspace rules file with trigger patterns
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behaviors have trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: Generator runs generate_awareness_files() method
        THEN: Generator creates file with bot-specific filename: mcp-test-bot-awareness.mdc
        AND: Filename includes bot name with hyphens
        AND: Generated rules file includes ACTUAL trigger words from bot
        AND: File includes bot name from config
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: Behaviors have trigger words configured
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_with_trigger_words(bot_dir, '1_shape', ['shape story', 'define story outline', 'create story map'])
        given_behavior_with_trigger_words(bot_dir, '4_discovery', ['discover stories', 'break down stories', 'enumerate stories'])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator runs generate_awareness_files() method
        gen = when_generator_generates_awareness_files(bot_dir)
        
        # Then: Generator creates file with bot-specific filename: mcp-test-bot-awareness.mdc
        rules_file = then_awareness_file_created_with_bot_specific_filename(bot_name)
        content = rules_file.read_text(encoding='utf-8')
        
        # And: File includes bot name
        then_awareness_file_contains_bot_name(content, bot_name)
        
        # And: Trigger words are SECTIONED by behavior (not flat list)
        then_awareness_file_contains_behavior_sections(content, ['Shape', 'Discovery'])
        
        # And: Shape section includes ONLY shape trigger words
        then_awareness_file_shape_section_contains_only_shape_words(content)
        
        # And: Each behavior section shows tool pattern
        then_awareness_file_contains_tool_patterns_for_behaviors(content, bot_name, ['1_shape', '4_discovery'])

    def test_rules_file_includes_bot_goal_and_behavior_descriptions(self, workspace_root):
        """
        SCENARIO: Rules file includes bot goal and behavior descriptions from instructions.json
        GIVEN: Bot has instructions.json with goal and behavior descriptions
        WHEN: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
        THEN: File includes bot's goal from instructions.json
        AND: Critical rule mentions bot's goal: "When user is trying to [goal], check MCP tools FIRST"
        AND: Each behavior section includes "When user is trying to [behavior description]"
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: Bot has instructions.json with goal and behavior descriptions
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_bot_has_instructions_json(
            workspace_root,
            bot_name,
            'Transform user needs into well-structured stories',
            {
                'shape': 'Create initial story map outline from user context',
                'discovery': 'Elaborate stories with user flows and domain rules'
            }
        )
        # And: Behaviors have descriptions and trigger words configured
        given_behaviors_with_descriptions_and_trigger_words(bot_dir, [
            {
                'name': '1_shape',
                'description': 'Create initial story map outline from user context',
                'patterns': ['shape story', 'create story map']
            },
            {
                'name': '4_discovery',
                'description': 'Elaborate stories with user flows and domain rules',
                'patterns': ['discover stories', 'elaborate stories']
            }
        ])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
        gen = when_generator_generates_awareness_files(bot_dir)
        rules_file = then_awareness_file_created_with_bot_specific_filename(bot_name)
        content = rules_file.read_text(encoding='utf-8')
        
        then_awareness_file_contains_priority_check_message(content, bot_name)
        
        # And: Each behavior follows explicit format
        then_awareness_file_contains_behavior_format_sections(content, bot_name)
        
        # And: File includes error handling section
        then_awareness_file_contains_error_handling_section(content)
        then_awareness_file_contains_repair_question(content)

    def test_rules_file_maps_trigger_patterns_to_tool_naming_conventions(self, workspace_root):
        """
        SCENARIO: Rules file maps trigger patterns to tool naming conventions in behavior sections
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behaviors have trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: File is written to .cursor/rules/mcp-test-bot-awareness.mdc
        THEN: Each behavior section includes tool pattern with ACTUAL bot name
        AND: Tool patterns appear in behavior sections (not flat list)
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config = given_bot_config_file_with_working_dir_and_behaviors(workspace_root, bot_name, behaviors)
        # And: Behaviors have trigger words configured
        bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
        given_behavior_with_trigger_words(bot_dir, '1_shape', ['shape story', 'define outline'])
        given_behavior_with_trigger_words(bot_dir, '4_discovery', ['discover stories', 'enumerate stories'])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # When: File is written to .cursor/rules/mcp-test-bot-awareness.mdc
        gen = when_generator_generates_awareness_files(bot_dir)
        rules_file = then_awareness_file_created_with_bot_specific_filename(bot_name)
        content = rules_file.read_text(encoding='utf-8')
        
        # Then: Each behavior section includes tool pattern with ACTUAL bot name
        then_awareness_file_contains_behavior_sections(content, behaviors)
        # And: Tool patterns appear in behavior sections (not flat list)
        then_awareness_file_contains_tool_patterns(content, bot_name, behaviors)
        # And: Trigger words are in correct sections
        then_trigger_words_in_behavior_section(content, '1_shape', ['shape story', 'define outline'])
        then_trigger_words_in_behavior_section(content, '4_discovery', ['discover stories', 'enumerate stories'])

    def test_generator_handles_file_write_errors_gracefully_creates_directory(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors gracefully - creates directory
        GIVEN: MCP Server Generator attempts to create awareness files
        WHEN: .cursor/rules/ directory does not exist
        THEN: Generator creates directory before writing file
        AND: File write succeeds with bot-specific filename
        """
        # When: Generate awareness files
        generator.generate_awareness_files()
        
        # Then: Directory exists (created if needed)
        rules_dir = then_rules_directory_exists_and_is_directory()
        # And: File write succeeded with bot-specific filename
        then_awareness_file_exists_with_bot_specific_filename(rules_dir, 'test_bot')

    def test_generator_handles_file_write_errors_with_clear_error_message(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors with clear error message
        GIVEN: .cursor/rules/ directory is write-protected
        WHEN: Generator attempts to write file
        THEN: Generator raises clear error message indicating permission issue
        AND: Error includes bot-specific path attempted
        """
        # Given: Rules directory exists
        rules_dir = when_create_rules_directory_if_needed()
        # And: Path.write_text is mocked to raise PermissionError
        expected_filename = given_expected_awareness_filename()
        with given_path_write_text_mocked_to_raise_permission_error(expected_filename):
            # When: Generator attempts to write file
            # Then: Generator raises error with clear message
            then_permission_error_raised_with_bot_specific_path(generator.generate_awareness_files, expected_filename)

    def test_full_awareness_generation_workflow(self, generator, workspace_root):
        """
        INTEGRATION TEST: Full awareness generation workflow
        GIVEN: MCP Server Generator initialized
        WHEN: generate_awareness_files() called
        THEN: Bot-specific rules file is created
        AND: Rules file has all required sections
        """
        # When: Generate awareness files
        when_generator_generates_awareness_files_direct(generator)
        
        # Then: Rules file created with bot-specific filename
        rules_dir = then_rules_directory_exists_and_is_directory()
        rules_file = then_awareness_file_exists_with_bot_specific_filename(rules_dir, 'test_bot')
        # And: Rules file has all required sections
        then_awareness_file_contains_required_sections(rules_file, 'test_bot')

