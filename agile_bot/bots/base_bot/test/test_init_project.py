"""
Init Project Tests

Tests for all stories in the 'Init Project' epic (in story map order):
- Bootstrap Workspace Configuration
"""
import pytest
from pathlib import Path
import json
import tempfile
import shutil
import os
from conftest import create_bot_config_file
from agile_bot.bots.base_bot.src.bot.bot import Bot
from agile_bot.bots.base_bot.src.bot.workspace import (
    get_bot_directory,
    get_workspace_directory,
    get_behavior_folder
)


# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

# Removed duplicate create_bot_config - use conftest.create_bot_config_file instead


# Removed create_agent_json - use update_bot_config_with_working_area instead
from agile_bot.bots.base_bot.test.test_helpers import update_bot_config_with_working_area


# Removed create_behavior_folder - use test_helpers.create_behavior_folder instead
# Already imported from test_helpers at top of file
def create_behavior_folder_duplicate_removed(bot_directory: Path, behavior_name: str):
    """Helper: Create behavior folder structure with behavior.json."""
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    
    # Create behavior.json file (required)
    behavior_config = {
        "behaviorName": behavior_name.split('_')[-1] if '_' in behavior_name and behavior_name[0].isdigit() else behavior_name,
        "description": f"Test behavior: {behavior_name}",
        "goal": f"Test goal for {behavior_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": [
            f"**BEHAVIOR WORKFLOW INSTRUCTIONS:**",
            "",
            f"Test instructions for {behavior_name}."
        ],
        "actions_workflow": {
            "actions": [
                {"name": "gather_context", "order": 1, "next_action": "decide_planning_criteria"},
                {"name": "decide_planning_criteria", "order": 2, "next_action": "build_knowledge"},
                {"name": "build_knowledge", "order": 3, "next_action": "validate_rules"},
                {"name": "validate_rules", "order": 4, "next_action": "render_output"},
                {"name": "render_output", "order": 5}
            ]
        },
        "trigger_words": {
            "description": f"Trigger words for {behavior_name}",
            "patterns": [f"test.*{behavior_name}"],
            "priority": 10
        }
    }
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    return behavior_dir

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

def given_bot_directory_environment_variable_set(bot_directory: Path):
    """Given step: BOT_DIRECTORY environment variable is set."""
    os.environ['BOT_DIRECTORY'] = str(bot_directory)

def given_workspace_directory_environment_variable_set(workspace_directory: Path):
    """Given step: WORKING_AREA environment variable is set."""
    os.environ['WORKING_AREA'] = str(workspace_directory)

def given_legacy_working_dir_environment_variable_set(workspace_directory: Path):
    """Given step: WORKING_DIR environment variable is set (legacy)."""
    os.environ['WORKING_DIR'] = str(workspace_directory)

def given_workspace_area_and_working_dir_environment_variables_set(workspace_area: Path, working_dir: Path):
    """Given step: Both WORKING_AREA and WORKING_DIR environment variables are set."""
    os.environ['WORKING_AREA'] = str(workspace_area)
    os.environ['WORKING_DIR'] = str(working_dir)

def then_workspace_directory_equals_expected_and_not_different(workspace_directory_path: Path, expected: Path, different: Path):
    """Then step: Workspace directory equals expected value and not different value."""
    assert workspace_directory_path == expected
    assert workspace_directory_path != different

def then_environment_variables_not_set(*variable_names: str):
    """Then step: Environment variables are not set."""
    for var_name in variable_names:
        assert var_name not in os.environ

def then_bot_and_workspace_directories_match_expected(bot_directory_result: Path, workspace_directory_result: Path, expected_bot_directory: Path, expected_workspace_directory: Path):
    """Then step: Bot and workspace directories match expected values."""
    assert bot_directory_result == expected_bot_directory
    assert workspace_directory_result == expected_workspace_directory

def then_bot_has_correct_directories(bot, expected_bot_directory: Path, expected_workspace_directory: Path):
    """Then step: Bot has correct directories."""
    assert bot.bot_directory == expected_bot_directory
    assert bot.workspace_directory == expected_workspace_directory

def then_workflow_file_location_is_correct(workflow_file: Path, expected_parent: Path, expected_name: str):
    """Then step: Workflow file location is correct."""
    assert workflow_file.parent == expected_parent
    assert workflow_file.name == expected_name

def then_bot_config_loaded_correctly(bot, expected_bot_name: str, expected_behaviors: list):
    """Then step: Bot config loaded correctly."""
    assert bot.bot_name == expected_bot_name
    for behavior in expected_behaviors:
        assert behavior in bot.behaviors

def then_behavior_folder_resolved_correctly(behavior_folder: Path, expected_path: Path):
    """Then step: Behavior folder resolved correctly."""
    assert behavior_folder == expected_path

def then_multiple_calls_return_same_value(function, expected_value: Path, call_count: int = 3):
    """Then step: Multiple calls to function return same value."""
    results = [function() for _ in range(call_count)]
    for result in results:
        assert result == expected_value
    return results

def given_override_workspace_directory_created_and_set(temp_workspace: Path, workspace_name: str):
    """Given step: Override workspace directory created and WORKING_AREA set."""
    override_workspace = temp_workspace / workspace_name
    override_workspace.mkdir(parents=True, exist_ok=True)
    os.environ['WORKING_AREA'] = str(override_workspace)
    return override_workspace

def given_different_directory_created(temp_workspace: Path, directory_name: str):
    """Given step: Create a different directory."""
    return temp_workspace / directory_name

def given_bot_directory_and_workspace_area_environment_variables_set(bot_directory: Path, workspace_directory: Path):
    """Given step: Both BOT_DIRECTORY and WORKING_AREA environment variables are set."""
    os.environ['BOT_DIRECTORY'] = str(bot_directory)
    os.environ['WORKING_AREA'] = str(workspace_directory)

def then_bot_config_does_not_have_working_area(bot_directory: Path):
    """Then step: Bot config does not have WORKING_AREA field."""
    config_path = bot_directory / 'config' / 'bot_config.json'
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        assert 'WORKING_AREA' not in config

def when_entry_point_bootstrap_logic_runs_if_working_area_not_set(bot_directory: Path):
    """When step: Entry point bootstrap logic runs if WORKING_AREA not set."""
    if 'WORKING_AREA' not in os.environ:
        config_path = bot_directory / 'config' / 'bot_config.json'
        if config_path.exists():
            bot_config = json.loads(config_path.read_text(encoding='utf-8'))
            # Check for WORKING_AREA in bot_config.json (legacy field)
            if 'WORKING_AREA' in bot_config:
                os.environ['WORKING_AREA'] = bot_config['WORKING_AREA']
            # Also check mcp.env.WORKING_AREA (new location)
            elif 'mcp' in bot_config and 'env' in bot_config['mcp']:
                mcp_env = bot_config['mcp']['env']
                if 'WORKING_AREA' in mcp_env:
                    os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']

def then_workspace_area_environment_variable_equals_expected_and_not_different(expected_value: Path, different_value: Path):
    """Then step: WORKING_AREA environment variable equals expected and not different."""
    assert os.environ['WORKING_AREA'] == str(expected_value)
    assert os.environ['WORKING_AREA'] != str(different_value)

def given_bot_config_and_behavior_exist(bot_directory: Path, bot_name: str, behavior_name: str):
    """Given step: Bot configuration and behavior folder exist."""
    config_path = create_bot_config_file(bot_directory, bot_name, [behavior_name])
    create_behavior_folder(bot_directory, behavior_name)
    return config_path

def when_entry_point_bootstraps_from_bot_config(bot_directory: Path):
    """When step: Entry point bootstrap code runs (simulated).
    
    Simulates what entry point does:
    1. Self-detect bot directory
    2. Read bot_config.json and set WORKING_AREA if not already set
    """
    # 1. Self-detect bot directory
    os.environ['BOT_DIRECTORY'] = str(bot_directory)
    
    # 2. Read bot_config.json and set WORKING_AREA if not already set
    config_path = bot_directory / 'config' / 'bot_config.json'
    if config_path.exists() and 'WORKING_AREA' not in os.environ:
        bot_config = json.loads(config_path.read_text(encoding='utf-8'))
        # Check for WORKING_AREA in bot_config.json (legacy field)
        if 'WORKING_AREA' in bot_config:
            os.environ['WORKING_AREA'] = bot_config['WORKING_AREA']
        # Also check mcp.env.WORKING_AREA (new location)
        elif 'mcp' in bot_config and 'env' in bot_config['mcp']:
            mcp_env = bot_config['mcp']['env']
            if 'WORKING_AREA' in mcp_env:
                os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']

def when_bot_is_instantiated(bot_name: str, bot_directory: Path, config_path: Path):
    """When step: Bot is instantiated."""
    return Bot(bot_name, bot_directory, config_path)

def then_environment_variable_is_set(variable_name: str, expected_value: Path):
    """Then step: Environment variable is set to expected value."""
    assert os.environ[variable_name] == str(expected_value)

def then_function_returns_path(function, expected_path: Path):
    """Then step: Function returns expected path."""
    result = function()
    assert result == expected_path
    assert isinstance(result, Path)
    return result

def then_runtime_error_raised_with_message(function, expected_keywords: list):
    """Then step: RuntimeError is raised with expected keywords in message."""
    with pytest.raises(RuntimeError) as exc_info:
        function()
    error_message = str(exc_info.value).lower()
    for keyword in expected_keywords:
        assert keyword.lower() in error_message


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_workspace():
    """Fixture: Temporary workspace directory."""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def bot_directory(temp_workspace):
    """Fixture: Bot directory structure."""
    bot_dir = temp_workspace / 'agile_bot' / 'bots' / 'test_bot'
    bot_dir.mkdir(parents=True, exist_ok=True)
    return bot_dir


@pytest.fixture
def workspace_directory(temp_workspace):
    """Fixture: Workspace directory for content files."""
    workspace_dir = temp_workspace / 'demo' / 'test_workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    return workspace_dir


@pytest.fixture(autouse=True)
def _clear_environment_variables():
    """Helper: Clear environment variables for testing."""
    env_vars = ['BOT_DIRECTORY', 'WORKING_AREA', 'WORKING_DIR']
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

def _restore_environment_variables(original_values: dict):
    """Helper: Restore original environment variable values."""
    _clear_environment_variables()
    for var, value in original_values.items():
        if value:
            os.environ[var] = value

def clean_env():
    """Fixture: Clean environment variables before and after each test."""
    # Store original values
    original_values = {
        'BOT_DIRECTORY': os.environ.get('BOT_DIRECTORY'),
        'WORKING_AREA': os.environ.get('WORKING_AREA'),
        'WORKING_DIR': os.environ.get('WORKING_DIR')
    }
    
    # Clear for test
    _clear_environment_variables()
    
    yield
    
    # Restore original values
    _restore_environment_variables(original_values)


# ============================================================================
# STORY: Bootstrap Workspace Configuration
# ============================================================================

class TestBootstrapWorkspace:
    """
    Story: Bootstrap Workspace Configuration
    
    As a bot developer, I want the workspace and bot directories to be 
    automatically configured at startup from environment variables and 
    configuration files, so that I don't need to pass directory paths 
    as parameters throughout the codebase.
    
    Acceptance Criteria:
    1. Entry points (MCP/CLI) bootstrap environment before importing modules
    2. All directory resolution reads from environment variables only
    3. agent.json provides default workspace location
    4. Environment variables can override agent.json
    """
    
    # ========================================================================
    # SCENARIO GROUP 1: Environment Variable Resolution
    # ========================================================================
    
    def test_bot_directory_from_environment_variable(self, bot_directory):
        """
        SCENARIO: Bot directory resolved from environment variable
        GIVEN: BOT_DIRECTORY environment variable is set
        WHEN: get_bot_directory() is called
        THEN: Returns the path from environment variable
        """
        # Given: BOT_DIRECTORY environment variable is set
        given_bot_directory_environment_variable_set(bot_directory)
        
        # When: get_bot_directory() is called
        # Then: Returns the path from environment variable
        then_function_returns_path(get_bot_directory, bot_directory)
    
    def test_workspace_directory_from_environment_variable(self, workspace_directory):
        """
        SCENARIO: Workspace directory resolved from environment variable
        GIVEN: WORKING_AREA environment variable is set
        WHEN: get_workspace_directory() is called
        THEN: Returns the path from environment variable
        """
        # Given: WORKING_AREA environment variable is set
        given_workspace_directory_environment_variable_set(workspace_directory)
        
        # When: get_workspace_directory() is called
        # Then: Returns the path from environment variable
        then_function_returns_path(get_workspace_directory, workspace_directory)
    
    def test_workspace_directory_supports_legacy_working_dir_variable(self, workspace_directory):
        """
        SCENARIO: Backward compatibility with WORKING_DIR variable
        GIVEN: WORKING_DIR environment variable is set (legacy name)
        AND: WORKING_AREA is not set
        WHEN: get_workspace_directory() is called
        THEN: Returns the path from WORKING_DIR variable
        """
        # Given: WORKING_DIR environment variable is set (legacy)
        # AND: WORKING_AREA is not set
        given_legacy_working_dir_environment_variable_set(workspace_directory)
        then_environment_variables_not_set('WORKING_AREA')
        
        # When: get_workspace_directory() is called
        # Then: Returns the path from WORKING_DIR variable
        then_function_returns_path(get_workspace_directory, workspace_directory)
    
    def test_working_area_takes_precedence_over_working_dir(self, workspace_directory, temp_workspace):
        """
        SCENARIO: WORKING_AREA takes precedence over legacy WORKING_DIR
        GIVEN: Both WORKING_AREA and WORKING_DIR are set
        AND: They have different values
        WHEN: get_workspace_directory() is called
        THEN: Returns WORKING_AREA value (preferred)
        """
        # Given: Both variables set with different values
        different_dir = given_different_directory_created(temp_workspace, 'different')
        given_workspace_area_and_working_dir_environment_variables_set(workspace_directory, different_dir)
        
        # When: get_workspace_directory() is called
        workspace_directory_path = get_workspace_directory()
        
        # Then: Returns WORKING_AREA value
        then_workspace_directory_equals_expected_and_not_different(workspace_directory_path, workspace_directory, different_dir)
    
    # ========================================================================
    # SCENARIO GROUP 2: Error Handling
    # ========================================================================
    
    def test_missing_bot_directory_raises_clear_error(self):
        """
        SCENARIO: Missing BOT_DIRECTORY raises helpful error
        GIVEN: BOT_DIRECTORY environment variable is NOT set
        WHEN: get_bot_directory() is called
        THEN: RuntimeError is raised
        AND: Error message explains entry points must bootstrap
        """
        # Given: BOT_DIRECTORY environment variable is NOT set
        assert 'BOT_DIRECTORY' not in os.environ
        
        # When: get_bot_directory() is called
        # Then: RuntimeError is raised with expected message
        then_runtime_error_raised_with_message(get_bot_directory, ['BOT_DIRECTORY', 'bootstrap'])
    
    def test_missing_workspace_directory_raises_clear_error(self):
        """
        SCENARIO: Missing WORKING_AREA raises helpful error
        GIVEN: WORKING_AREA and WORKING_DIR environment variables are NOT set
        WHEN: get_workspace_directory() is called
        THEN: RuntimeError is raised
        AND: Error message explains entry points must bootstrap
        """
        # Given: Neither WORKING_AREA nor WORKING_DIR is set
        then_environment_variables_not_set('WORKING_AREA', 'WORKING_DIR')
        
        # When: get_workspace_directory() is called
        # Then: RuntimeError is raised with expected message
        then_runtime_error_raised_with_message(get_workspace_directory, ['WORKING_AREA', 'bootstrap'])
    
    # ========================================================================
    # SCENARIO GROUP 3: Bootstrap from bot_config.json
    # ========================================================================
    
    def test_entry_point_bootstraps_from_bot_config(self, bot_directory, workspace_directory):
        """
        SCENARIO: Entry point reads bot_config.json and sets environment
        GIVEN: bot_config.json exists with WORKING_AREA field
        AND: BOT_DIRECTORY can be self-detected from script location
        WHEN: Entry point bootstrap code runs (simulated)
        THEN: WORKING_AREA environment variable is set from bot_config.json
        AND: BOT_DIRECTORY environment variable is set from script location
        """
        # Given: bot_config.json exists with WORKING_AREA field
        update_bot_config_with_working_area(bot_directory, workspace_directory)
        
        # When: Entry point bootstrap code runs (simulated)
        when_entry_point_bootstraps_from_bot_config(bot_directory)
        
        # Then: Environment variables are set correctly
        then_environment_variable_is_set('BOT_DIRECTORY', bot_directory)
        then_environment_variable_is_set('WORKING_AREA', workspace_directory)
        
        # And: Functions return correct values
        then_bot_and_workspace_directories_match_expected(get_bot_directory(), get_workspace_directory(), bot_directory, workspace_directory)
    
    def test_environment_variable_takes_precedence_over_bot_config(
        self, bot_directory, workspace_directory, temp_workspace
    ):
        """
        SCENARIO: Pre-set environment variable not overwritten
        GIVEN: WORKING_AREA environment variable is already set (e.g., by mcp.json env)
        AND: bot_config.json also has WORKING_AREA field with different value
        WHEN: Entry point bootstrap code runs (simulated)
        THEN: WORKING_AREA environment variable retains original value
        AND: bot_config.json value is NOT used (override pattern)
        """
        # Given: Environment variable already set with one value
        override_workspace = given_override_workspace_directory_created_and_set(temp_workspace, 'override_workspace')
        
        # And: bot_config.json has different value
        update_bot_config_with_working_area(bot_directory, workspace_directory)
        given_bot_directory_environment_variable_set(bot_directory)
        
        # When: Entry point bootstrap code runs (simulated with check)
        when_entry_point_bootstrap_logic_runs_if_working_area_not_set(bot_directory)
        
        # Then: Environment variable retains override value
        assert os.environ['WORKING_AREA'] == str(override_workspace)
        assert os.environ['WORKING_AREA'] != str(workspace_directory)
        
        # And: Function returns override value
        assert get_workspace_directory() == override_workspace
    
    def test_missing_bot_config_with_preconfig_env_var_works(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: bot_config.json not required if env vars pre-configured
        GIVEN: WORKING_AREA environment variable is already set
        AND: BOT_DIRECTORY environment variable is already set
        AND: bot_config.json does NOT exist or does NOT have WORKING_AREA
        WHEN: Functions are called
        THEN: No error occurs
        AND: Environment variables work correctly
        """
        # Given: Environment variables already set
        given_bot_directory_and_workspace_area_environment_variables_set(bot_directory, workspace_directory)
        
        # And: agent.json does NOT exist
        then_bot_config_does_not_have_working_area(bot_directory)
        
        # When: Functions are called
        # Then: Functions work without error
        then_bot_and_workspace_directories_match_expected(get_bot_directory(), get_workspace_directory(), bot_directory, workspace_directory)
    
    # ========================================================================
    # SCENARIO GROUP 4: Bot Initialization with Bootstrap
    # ========================================================================
    
    def test_bot_initializes_with_bootstrapped_directories(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: Bot successfully initializes with bootstrapped environment
        GIVEN: BOT_DIRECTORY environment variable is set
        AND: WORKING_AREA environment variable is set
        AND: Bot configuration exists
        WHEN: Bot is instantiated
        THEN: Bot uses bot_directory from environment
        AND: Bot.workspace_directory property returns workspace from environment
        """
        # Given: Environment is bootstrapped
        given_bot_directory_environment_variable_set(bot_directory)
        given_workspace_directory_environment_variable_set(workspace_directory)
        # And: Bot configuration exists
        config_path = given_bot_config_and_behavior_exist(bot_directory, 'test_bot', 'shape')
        
        # When: Bot is instantiated
        bot = when_bot_is_instantiated('test_bot', bot_directory, config_path)
        
        # Then: Bot uses correct directories
        then_bot_has_correct_directories(bot, bot_directory, workspace_directory)
    
    def test_workflow_state_created_in_workspace_directory(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: Workflow state file created in correct workspace
        GIVEN: Environment is properly bootstrapped
        AND: Bot is initialized with a behavior
        WHEN: Bot behavior's workflow accesses its file property
        THEN: workflow_state.json path points to workspace directory
        AND: NOT to bot directory
        """
        # Given: Environment is bootstrapped
        given_bot_directory_environment_variable_set(bot_directory)
        given_workspace_directory_environment_variable_set(workspace_directory)
        # And: Bot is initialized
        config_path = given_bot_config_and_behavior_exist(bot_directory, 'test_bot', 'shape')
        bot = when_bot_is_instantiated('test_bot', bot_directory, config_path)
        
        # When: Workflow file path is accessed
        shape_behavior = bot.behaviors.find_by_name('shape')
        workflow_file = shape_behavior.workflow.file
        
        # Then: Path is in workspace directory
        assert workflow_file.parent == workspace_directory
        assert workflow_file.name == 'workflow_state.json'
        
        # And: NOT in bot directory
        assert not str(workflow_file).startswith(str(bot_directory))
    
    # ========================================================================
    # SCENARIO GROUP 5: Path Resolution Consistency
    # ========================================================================
    
    def test_bot_config_loaded_from_bot_directory(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: Bot configuration loaded from bot directory (not workspace)
        GIVEN: BOT_DIRECTORY is set to bot code location
        AND: WORKING_AREA is set to workspace location
        AND: bot_config.json exists in bot directory
        WHEN: Bot loads its configuration
        THEN: bot_config.json is read from BOT_DIRECTORY/config/
        AND: NOT from WORKING_AREA
        """
        # Given: Directories are set
        given_bot_directory_environment_variable_set(bot_directory)
        given_workspace_directory_environment_variable_set(workspace_directory)
        # And: Config exists in bot directory
        config_path = given_bot_config_and_behavior_exist(bot_directory, 'test_bot', 'shape')
        
        # When: Bot loads configuration
        bot = when_bot_is_instantiated('test_bot', bot_directory, config_path)
        
        # Then: Config was loaded from bot directory
        then_bot_config_loaded_correctly(bot, 'test_bot', ['shape'])
        
        # Verify config path is in bot directory
        assert config_path.parent.parent == bot_directory
    
    def test_behavior_folders_resolved_from_bot_directory(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: Behavior folders resolved from bot directory
        GIVEN: BOT_DIRECTORY is set
        AND: WORKING_AREA is set to different location
        WHEN: get_behavior_folder() is called
        THEN: Behavior path is BOT_DIRECTORY/behaviors/{behavior_name}/
        AND: NOT from workspace directory
        """
        # Given: Directories are set
        given_bot_directory_environment_variable_set(bot_directory)
        given_workspace_directory_environment_variable_set(workspace_directory)
        
        # When: get_behavior_folder() is called
        behavior_folder = get_behavior_folder('test_bot', 'shape')
        
        # Then: Path is in bot directory
        expected_path = bot_directory / 'behaviors' / 'shape'
        assert behavior_folder == expected_path
        
        # And: NOT in workspace directory
        assert not str(behavior_folder).startswith(str(workspace_directory))
    
    def test_multiple_calls_use_cached_env_vars(self, bot_directory, workspace_directory):
        """
        SCENARIO: Multiple calls read from cached environment (fast)
        GIVEN: Environment variables are set
        WHEN: get_workspace_directory() is called multiple times
        THEN: Each call returns same value from environment
        AND: No file I/O occurs (just env var reads)
        """
        # Given: Environment variables are set
        given_bot_directory_environment_variable_set(bot_directory)
        given_workspace_directory_environment_variable_set(workspace_directory)
        
        # When: Called multiple times
        result1 = get_workspace_directory()
        result2 = get_workspace_directory()
        result3 = get_workspace_directory()
        
        # Then: Same value each time
        assert result1 == result2 == result3 == workspace_directory
        
        # And: All are Path objects
        assert all(isinstance(r, Path) for r in [result1, result2, result3])
