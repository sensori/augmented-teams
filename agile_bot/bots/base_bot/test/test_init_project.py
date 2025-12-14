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
from agile_bot.bots.base_bot.src.state.workspace import (
    get_bot_directory,
    get_workspace_directory,
    get_behavior_folder
)


# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

# Removed duplicate create_bot_config - use conftest.create_bot_config_file instead


def create_agent_json(bot_directory: Path, working_area: str) -> Path:
    """Helper: Create agent.json file."""
    agent_json = bot_directory / 'agent.json'
    agent_json.write_text(json.dumps({'WORKING_AREA': working_area}), encoding='utf-8')
    return agent_json


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

def given_bot_config_and_behavior_exist(bot_directory: Path, bot_name: str, behavior_name: str):
    """Given step: Bot configuration and behavior folder exist."""
    config_path = create_bot_config_file(bot_directory, bot_name, [behavior_name])
    create_behavior_folder(bot_directory, behavior_name)
    return config_path

def when_entry_point_bootstraps_from_agent_json(bot_directory: Path):
    """When step: Entry point bootstrap code runs (simulated).
    
    Simulates what entry point does:
    1. Self-detect bot directory
    2. Read agent.json and set WORKING_AREA if not already set
    """
    # 1. Self-detect bot directory
    os.environ['BOT_DIRECTORY'] = str(bot_directory)
    
    # 2. Read agent.json and set WORKING_AREA if not already set
    agent_json_path = bot_directory / 'agent.json'
    if agent_json_path.exists() and 'WORKING_AREA' not in os.environ:
        agent_config = json.loads(agent_json_path.read_text(encoding='utf-8'))
        if 'WORKING_AREA' in agent_config:
            os.environ['WORKING_AREA'] = agent_config['WORKING_AREA']

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
def clean_env():
    """Fixture: Clean environment variables before and after each test."""
    # Store original values
    original_bot_dir = os.environ.get('BOT_DIRECTORY')
    original_working_area = os.environ.get('WORKING_AREA')
    original_working_dir = os.environ.get('WORKING_DIR')
    
    # Clear for test
    if 'BOT_DIRECTORY' in os.environ:
        del os.environ['BOT_DIRECTORY']
    if 'WORKING_AREA' in os.environ:
        del os.environ['WORKING_AREA']
    if 'WORKING_DIR' in os.environ:
        del os.environ['WORKING_DIR']
    
    yield
    
    # Restore original values
    if 'BOT_DIRECTORY' in os.environ:
        del os.environ['BOT_DIRECTORY']
    if 'WORKING_AREA' in os.environ:
        del os.environ['WORKING_AREA']
    if 'WORKING_DIR' in os.environ:
        del os.environ['WORKING_DIR']
        
    if original_bot_dir:
        os.environ['BOT_DIRECTORY'] = original_bot_dir
    if original_working_area:
        os.environ['WORKING_AREA'] = original_working_area
    if original_working_dir:
        os.environ['WORKING_DIR'] = original_working_dir


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
        assert 'WORKING_AREA' not in os.environ
        
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
        different_dir = temp_workspace / 'different'
        os.environ['WORKING_AREA'] = str(workspace_directory)
        os.environ['WORKING_DIR'] = str(different_dir)
        
        # When: get_workspace_directory() is called
        result = get_workspace_directory()
        
        # Then: Returns WORKING_AREA value
        assert result == workspace_directory
        assert result != different_dir
    
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
        assert 'WORKING_AREA' not in os.environ
        assert 'WORKING_DIR' not in os.environ
        
        # When: get_workspace_directory() is called
        # Then: RuntimeError is raised with expected message
        then_runtime_error_raised_with_message(get_workspace_directory, ['WORKING_AREA', 'bootstrap'])
    
    # ========================================================================
    # SCENARIO GROUP 3: Bootstrap from agent.json
    # ========================================================================
    
    def test_entry_point_bootstraps_from_agent_json(self, bot_directory, workspace_directory):
        """
        SCENARIO: Entry point reads agent.json and sets environment
        GIVEN: agent.json exists with WORKING_AREA field
        AND: BOT_DIRECTORY can be self-detected from script location
        WHEN: Entry point bootstrap code runs (simulated)
        THEN: WORKING_AREA environment variable is set from agent.json
        AND: BOT_DIRECTORY environment variable is set from script location
        """
        # Given: agent.json exists with WORKING_AREA field
        create_agent_json(bot_directory, str(workspace_directory))
        
        # When: Entry point bootstrap code runs (simulated)
        when_entry_point_bootstraps_from_agent_json(bot_directory)
        
        # Then: Environment variables are set correctly
        then_environment_variable_is_set('BOT_DIRECTORY', bot_directory)
        then_environment_variable_is_set('WORKING_AREA', workspace_directory)
        
        # And: Functions return correct values
        assert get_bot_directory() == bot_directory
        assert get_workspace_directory() == workspace_directory
    
    def test_environment_variable_takes_precedence_over_agent_json(
        self, bot_directory, workspace_directory, temp_workspace
    ):
        """
        SCENARIO: Pre-set environment variable not overwritten
        GIVEN: WORKING_AREA environment variable is already set (e.g., by mcp.json)
        AND: agent.json also has WORKING_AREA field with different value
        WHEN: Entry point bootstrap code runs (simulated)
        THEN: WORKING_AREA environment variable retains original value
        AND: agent.json value is NOT used (override pattern)
        """
        # Given: Environment variable already set with one value
        override_workspace = temp_workspace / 'override_workspace'
        override_workspace.mkdir(parents=True, exist_ok=True)
        os.environ['WORKING_AREA'] = str(override_workspace)
        
        # And: agent.json has different value
        create_agent_json(bot_directory, str(workspace_directory))
        os.environ['BOT_DIRECTORY'] = str(bot_directory)
        
        # When: Entry point bootstrap code runs (simulated with check)
        # This is what entry point should do - check if already set
        if 'WORKING_AREA' not in os.environ:
            agent_json_path = bot_directory / 'agent.json'
            if agent_json_path.exists():
                agent_config = json.loads(agent_json_path.read_text(encoding='utf-8'))
                if 'WORKING_AREA' in agent_config:
                    os.environ['WORKING_AREA'] = agent_config['WORKING_AREA']
        
        # Then: Environment variable retains override value
        assert os.environ['WORKING_AREA'] == str(override_workspace)
        assert os.environ['WORKING_AREA'] != str(workspace_directory)
        
        # And: Function returns override value
        assert get_workspace_directory() == override_workspace
    
    def test_missing_agent_json_with_preconfig_env_var_works(
        self, bot_directory, workspace_directory
    ):
        """
        SCENARIO: agent.json not required if env vars pre-configured
        GIVEN: WORKING_AREA environment variable is already set
        AND: BOT_DIRECTORY environment variable is already set
        AND: agent.json does NOT exist
        WHEN: Functions are called
        THEN: No error occurs
        AND: Environment variables work correctly
        """
        # Given: Environment variables already set
        os.environ['BOT_DIRECTORY'] = str(bot_directory)
        os.environ['WORKING_AREA'] = str(workspace_directory)
        
        # And: agent.json does NOT exist
        agent_json_path = bot_directory / 'agent.json'
        assert not agent_json_path.exists()
        
        # When/Then: Functions work without error
        assert get_bot_directory() == bot_directory
        assert get_workspace_directory() == workspace_directory
    
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
        assert bot.bot_directory == bot_directory
        assert bot.workspace_directory == workspace_directory
    
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
        workflow_file = bot.shape.workflow.file
        
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
        assert bot.bot_name == 'test_bot'
        assert 'shape' in bot.behaviors
        
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
