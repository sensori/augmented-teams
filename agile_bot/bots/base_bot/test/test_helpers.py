"""
Common Test Helpers - Used Across Multiple Epics

This file contains helper functions that are used across MULTIPLE epics and sub-epics.
These are truly common/shared utilities, not sub-epic-specific helpers.

NOTE: This file does not follow the test_<sub_epic_name>.py naming convention because
it contains common helpers spanning multiple epics. Sub-epic-specific helpers should
be placed in test_<sub_epic_name>_helpers.py files.

For sub-epic-specific helpers, see:
- test_generate_mcp_tools.py (Generate MCP Tools sub-epic - helpers merged into main file)
- test_generate_cli.py (Generate CLI sub-epic - helpers merged into main file)
- test_perform_behavior_action.py (Perform Behavior Action sub-epic - helpers merged into main file)
"""
import json
import os
from pathlib import Path
import pytest
from agile_bot.bots.base_bot.src.bot.bot import Behavior


# ============================================================================
# PATH HELPERS - Centralized path calculations
# ============================================================================

def get_bot_dir(repo_root: Path, bot_name: str) -> Path:
    """Get bot directory path (where bot code lives)."""
    return repo_root / 'agile_bot' / 'bots' / bot_name

def get_activity_log_path(workspace_dir: Path) -> Path:
    """Get activity_log.json path (in workspace directory)."""
    return workspace_dir / 'activity_log.json'

def get_workflow_state_path(workspace_dir: Path) -> Path:
    """Get workflow_state.json path (in workspace directory)."""
    return workspace_dir / 'workflow_state.json'

def get_bot_config_path(bot_dir: Path) -> Path:
    """Get bot config path (in bot directory)."""
    return bot_dir / 'config' / 'bot_config.json'

def get_behavior_dir(bot_dir: Path, behavior: str) -> Path:
    """Get behavior directory path (in bot directory)."""
    return bot_dir / 'behaviors' / behavior

def get_base_bot_dir(repo_root: Path) -> Path:
    """Get test_base_bot directory path for tests (not production base_bot)."""
    return repo_root / 'agile_bot' / 'bots' / 'test_base_bot'

def get_base_actions_dir(repo_root: Path) -> Path:
    """Get base_actions directory path from test_base_bot."""
    return get_base_bot_dir(repo_root) / 'base_actions'

def get_test_base_actions_dir(bot_directory: Path) -> Path:
    """Get base_actions directory, redirecting base_bot to test_base_bot.
    
    If bot_directory is base_bot (production), redirects to test_base_bot/base_actions.
    Otherwise, uses bot_directory/base_actions.
    """
    # If bot_directory is base_bot, redirect to test_base_bot
    if bot_directory.name == 'base_bot':
        # Infer repo_root from bot_directory: agile_bot/bots/base_bot -> repo_root
        repo_root = bot_directory.parent.parent.parent
        return get_base_actions_dir(repo_root)
    # Otherwise use the bot_directory's base_actions
    return bot_directory / 'base_actions'

def get_base_bot_rules_dir(repo_root: Path) -> Path:
    """Get base_bot rules directory path."""
    return get_base_bot_dir(repo_root) / 'rules'

def bootstrap_env(bot_dir: Path, workspace_dir: Path):
    """Bootstrap environment variables for tests."""
    os.environ['BOT_DIRECTORY'] = str(bot_dir)
    os.environ['WORKING_AREA'] = str(workspace_dir)

def update_bot_config_with_working_area(bot_dir: Path, workspace_dir: Path) -> Path:
    """Update bot_config.json with WORKING_AREA field."""
    config_dir = bot_dir / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / 'bot_config.json'
    
    # Load existing config or create new one
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
    else:
        config = {'name': bot_dir.name}
    
    # Add WORKING_AREA
    config['WORKING_AREA'] = str(workspace_dir)
    config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    return config_path

# Removed duplicate create_bot_config - use conftest.create_bot_config_file instead
# Import conftest functions when needed: from conftest import create_bot_config_file

def create_activity_log_file(workspace_dir: Path) -> Path:
    """Create activity log file in workspace directory."""
    log_file = get_activity_log_path(workspace_dir)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
    return log_file

# Removed duplicate create_workflow_state - use conftest.create_workflow_state_file instead
# Import conftest functions when needed: from conftest import create_workflow_state_file

def create_guardrails_files(bot_dir: Path, behavior: str, questions: list, evidence: list) -> tuple:
    """Create guardrails files in behavior folder with specific content."""
    guardrails_dir = get_behavior_dir(bot_dir, behavior) / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text(json.dumps({'questions': questions}), encoding='utf-8')
    
    evidence_file = guardrails_dir / 'evidence.json'
    evidence_file.write_text(json.dumps({'evidence': evidence}), encoding='utf-8')
    
    return questions_file, evidence_file

def create_planning_guardrails(bot_dir: Path, behavior: str, assumptions: list, criteria: dict) -> tuple:
    """Create planning guardrails (alias for create_strategy_guardrails for backward compatibility)."""
    return create_strategy_guardrails(bot_dir, behavior, assumptions, criteria)

def create_strategy_guardrails(bot_dir: Path, behavior: str, assumptions: list, criteria: dict) -> tuple:
    """Create strategy guardrails in behavior folder."""
    # Strategy class expects guardrails/strategy/ directory (not planning/)
    guardrails_dir = get_behavior_dir(bot_dir, behavior) / 'guardrails' / 'strategy'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    assumptions_file = guardrails_dir / 'typical_assumptions.json'
    assumptions_file.write_text(json.dumps({'assumptions': assumptions}), encoding='utf-8')
    
    criteria_dir = guardrails_dir / 'strategy_criteria'
    criteria_dir.mkdir(exist_ok=True)
    criteria_file = criteria_dir / 'test_criteria.json'
    criteria_file.write_text(json.dumps(criteria), encoding='utf-8')
    
    return assumptions_file, criteria_file

def create_knowledge_graph_template(bot_dir: Path, behavior: str, template_name: str) -> Path:
    """Create knowledge graph template in behavior folder."""
    kg_dir = get_behavior_dir(bot_dir, behavior) / 'content' / 'knowledge_graph'
    kg_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = kg_dir / f'{template_name}.json'
    template_file.write_text(json.dumps({'template': 'knowledge_graph'}), encoding='utf-8')
    return template_file

def create_validation_rules(bot_dir: Path, behavior: str, rules: list) -> Path:
    """Create validation rules in behavior folder."""
    rules_dir = get_behavior_dir(bot_dir, behavior) / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

def create_common_rules(repo_root: Path, rules: list) -> Path:
    """Create common rules in base_bot directory."""
    rules_dir = get_base_bot_rules_dir(repo_root)
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'common_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

# ============================================================================
# BASE INSTRUCTIONS HELPERS - Epic-level helpers for Invoke Bot epic
# ============================================================================

def create_base_instructions(bot_directory: Path):
    """Create base action configs in bot_directory (no fallback to repo root).
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    base_actions = get_test_base_actions_dir(bot_directory)
    # Action folders no longer have number prefixes
    actions = ['clarify', 'strategy', 'build', 'validate', 'render']
    orders = [1, 2, 3, 4, 5]
    next_actions = ['strategy', 'build', 'validate', 'render', None]
    
    for action, order, next_action in zip(actions, orders, next_actions):
        action_dir = base_actions / action
        action_dir.mkdir(parents=True, exist_ok=True)
        config = {
            'name': action,
            'workflow': True,
            'order': order,
            'instructions': [f'{action} base instructions']
        }
        if next_action:
            config['next_action'] = next_action
        config_file = action_dir / 'action_config.json'
        config_file.write_text(json.dumps(config), encoding='utf-8')


def create_base_action_instructions(bot_directory: Path, action: str) -> Path:
    """Create base action config for specific action in bot_directory (no fallback).
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    
    # Action folders no longer have number prefixes
    action_dir = base_actions_dir / action
    action_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        'name': action,
        'workflow': True,
        'order': 1,
        'instructions': [f'{action} base instructions']
    }
    config_file = action_dir / 'action_config.json'
    config_file.write_text(json.dumps(config), encoding='utf-8')
    return config_file


def create_behavior_folder(bot_dir: Path, folder_name: str) -> Path:
    """Create behavior folder in bot directory."""
    behavior_dir = get_behavior_dir(bot_dir, folder_name)
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir

def create_behavior_action_instructions(bot_dir: Path, behavior: str, action: str) -> Path:
    """Create behavior-specific action instructions."""
    instructions_dir = get_behavior_dir(bot_dir, behavior) / action
    instructions_dir.mkdir(parents=True, exist_ok=True)
    
    instructions_file = instructions_dir / 'instructions.json'
    instructions_file.write_text(json.dumps({
        'instructions': [f'{behavior}.{action} specific instructions']
    }), encoding='utf-8')
    return instructions_file

# Removed duplicate create_trigger_words_file - use test_generate_mcp_tools.create_trigger_words_file instead

def create_actions_workflow_json(bot_directory: Path, behavior_name: str, actions: list = None, order: int = None) -> Path:
    """Given step: Behavior exists with actions workflow.
    
    Creates behavior.json file for a behavior (new format).
    
    Used across multiple epics:
    - Generate MCP Tools (Build Agile Bots epic)
    - Generate CLI (Build Agile Bots epic)
    - Invoke Bot (Invoke Bot epic)
    - Execute Behavior Actions (Execute Behavior Actions epic)
    - Validate Rules (Execute Behavior Actions epic)
    
    Args:
        bot_directory: Path to bot directory
        behavior_name: Name of the behavior
        actions: Optional list of action configs. If None, creates default actions.
        order: Optional order number for behavior. If None, behavior.json will not have order field.
    
    """
    import json
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    
    if actions is None:
        # Standard workflow order - using actual action names: clarify, strategy, build, validate, render
        # Note: 'build' action class doesn't exist yet, so it's excluded until BuildAction is implemented
        actions = [
            {
                "name": "clarify",
                "order": 1,
                "next_action": "strategy",
                "instructions": [
                    f"Follow agile_bot/bots/test_base_bot/base_actions/clarify/action_config.json",
                    f"Test instructions for clarify in {behavior_name}"
                ]
            },
            {
                "name": "strategy",
                "order": 2,
                "next_action": "validate",
                "instructions": [
                    f"Follow agile_bot/bots/test_base_bot/base_actions/strategy/action_config.json",
                    f"Test instructions for strategy in {behavior_name}"
                ]
            },
            {
                "name": "validate",
                "order": 3,
                "next_action": "render",
                "instructions": [
                    f"Follow agile_bot/bots/test_base_bot/base_actions/validate/action_config.json",
                    f"Test instructions for validate in {behavior_name}"
                ]
            },
            {
                "name": "render",
                "order": 4,
                "instructions": [
                    f"Follow agile_bot/bots/test_base_bot/base_actions/render/action_config.json",
                    f"Test instructions for render in {behavior_name}"
                ]
            }
        ]
    
    # Create behavior.json with all sections matching production structure
    behavior_config = {
        "behaviorName": behavior_name.split('_')[-1] if '_' in behavior_name and behavior_name[0].isdigit() else behavior_name,
        "description": f"Test behavior: {behavior_name}",
        "goal": f"Test goal for {behavior_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": [
            f"**BEHAVIOR WORKFLOW INSTRUCTIONS:**",
            "",
            f"Test instructions for {behavior_name}."
        ],
        "actions_workflow": {
            "actions": actions
        },
        "trigger_words": {
            "description": f"Trigger words for {behavior_name}",
            "patterns": [f"test.*{behavior_name}"]
        }
    }
    
    # Add order field if provided (matches production structure)
    if order is not None:
        behavior_config["order"] = order
    
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    return behavior_file

def create_base_actions_structure(bot_directory: Path):
    """Create base actions directory structure in bot_directory (no fallback).
    
    Creates base_actions directory with action_config.json files.
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    
    NOTE: This is kept for backward compatibility. New tests should use actions-workflow.json instead.
    """
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    
    # Actions no longer have number prefixes - use clean names
    actions = [
        ('clarify', 1, 'strategy'),
        ('strategy', 2, 'build'),
        ('build', 3, 'validate'),
        ('validate', 4, 'render'),
        ('render', 5, None)
    ]
    
    for action_name, order, next_action in actions:
        action_dir = base_actions_dir / action_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        # Create action_config.json
        config = {
            'name': action_name,
            'workflow': True,
            'order': order
        }
        if next_action:
            config['next_action'] = next_action
        
        (action_dir / 'action_config.json').write_text(json.dumps(config), encoding='utf-8')
    

def read_activity_log(workspace_dir: Path) -> list:
    """Read activity log from workspace directory."""
    log_file = get_activity_log_path(workspace_dir)
    if not log_file.exists():
        return []
    
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        return db.all()

# Removed verify_action_tracks_start, verify_action_tracks_completion, verify_workflow_transition, 
# verify_workflow_saves_completed_action, then_workflow_current_state_is, then_completed_actions_include,
# _create_validate_action, _create_gather_context_action, _create_action_with_provided_class,
# _create_action_with_default_class, given_environment_bootstrapped_and_action_initialized
# - These are epic-level helpers for "Execute Behavior Actions" epic, moved to test_execute_behavior_actions.py
# Import from: from agile_bot.bots.base_bot.test.test_execute_behavior_actions import ...

# ============================================================================
# COMMON GIVEN/WHEN/THEN HELPERS - Used across multiple test files
# ============================================================================

def given_bot_name_and_behavior_setup(bot_name: str = 'story_bot', behavior: str = 'shape'):
    """Given: Bot name and behavior setup.
    
    """
    return bot_name, behavior

# ============================================================================
# BOT INSTANCE HELPERS - Epic-level helpers for Invoke Bot epic
# ============================================================================

def given_bot_instance_created(bot_name: str, bot_directory: Path, config_path: Path):
    """Given: Bot instance created."""
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    return Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)


def when_bot_is_created(bot_name: str, bot_directory: Path, config_path: Path):
    """When: Bot is created."""
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    return Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)


# Removed then_completed_actions_include, then_workflow_current_state_is - moved to test_execute_behavior_actions.py

def then_activity_logged_with_action_state(log_file_or_workspace: Path, expected_action_state: str):
    """Then: Activity logged with expected action_state.
    
    Accepts either log_file Path or workspace_directory Path.
    """
    from tinydb import TinyDB
    if (log_file_or_workspace / 'activity_log.json').exists():
        # It's a workspace directory
        log_file = log_file_or_workspace / 'activity_log.json'
    else:
        # It's already a log file
        log_file = log_file_or_workspace
    
    with TinyDB(log_file) as db:
        entries = db.all()
        # Debug: print all entries if assertion fails
        if not any(entry.get('action_state') == expected_action_state for entry in entries):
            actual_states = [entry.get('action_state') for entry in entries]
            raise AssertionError(
                f"Expected action_state '{expected_action_state}' not found in activity log. "
                f"Actual entries: {actual_states}"
            )

def then_completion_entry_logged_with_outputs(log_file_or_workspace: Path, expected_outputs: dict = None, expected_duration: int = None):
    """Then: Completion entry logged with outputs and duration.
    
    Accepts either log_file Path or workspace_directory Path.
    """
    from tinydb import TinyDB
    if (log_file_or_workspace / 'activity_log.json').exists():
        # It's a workspace directory
        log_file = log_file_or_workspace / 'activity_log.json'
    else:
        # It's already a log file
        log_file = log_file_or_workspace
    
    with TinyDB(log_file) as db:
        entries = db.all()
        completion_entry = next((e for e in entries if 'outputs' in e), None)
        assert completion_entry is not None
        if expected_outputs is not None:
            assert completion_entry['outputs'] == expected_outputs
        if expected_duration is not None:
            assert completion_entry['duration'] == expected_duration

# ============================================================================
# CONSOLIDATED GIVEN/WHEN/THEN HELPERS - Previously duplicated across files
# ============================================================================

# Removed given_test_bot_directory_created, given_story_graph_file_created - moved to test_build_knowledge.py (helpers merged into main file)
# Removed when_action_executes_with_parameters - merged into test_decide_planning_criteria_action.py


def given_environment_bootstrapped_and_activity_log_initialized(bot_directory: Path, workspace_directory: Path):
    """Given: Environment bootstrapped and activity log initialized."""
    bootstrap_env(bot_directory, workspace_directory)
    log_file = create_activity_log_file(workspace_directory)
    return log_file


# Removed _create_validate_action, _create_gather_context_action, _create_action_with_provided_class,
# _create_action_with_default_class, given_environment_bootstrapped_and_action_initialized
# - moved to test_execute_behavior_actions.py


# Removed given_base_actions_structure_created - merged into test_invoke_mcp.py

# Removed all workflow helpers (lines 412-695) - merged into test_perform_behavior_action.py
# These are specific to Perform Behavior Action sub-epic

# ============================================================================
# CLI/ROUTER HELPERS - Consolidates duplicates from test_invoke_bot_cli.py
# and test_invoke_cli.py
# ============================================================================

def then_route_matches_expected(route, expected_bot: str, expected_behavior: str, expected_action: str, expected_type: str):
    """Then: Route matches expected values."""
    assert route is not None, "Route should not be None"
    assert route['bot_name'] == expected_bot
    assert route['behavior_name'] == expected_behavior
    assert route['action_name'] == expected_action
    assert route['match_type'] == expected_type


def then_cli_result_matches_expected(result, expected_behavior: str, expected_action: str):
    """Then: CLI result matches expected values."""
    assert result['status'] == 'success'
    assert result['behavior'] == expected_behavior
    assert result['action'] == expected_action


# ============================================================================
# TEST CLASSES - Tests for utility functions (merged from test_utils.py)
# ============================================================================

@pytest.fixture
def bot_directory(tmp_path):
    """Fixture: Temporary bot directory."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'test_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir


def create_behavior_folder_with_json(bot_dir: Path, folder_name: str) -> Path:
    """Helper: Create behavior folder in bot directory with behavior.json.
    
    Uses create_behavior_folder from test_helpers and adds behavior.json creation.
    """
    behavior_folder = create_behavior_folder(bot_dir, folder_name)
    
    # Create behavior.json file (required for TestFindBehaviorFolder tests)
    behavior_config = {
        "behaviorName": folder_name.split('_')[-1] if '_' in folder_name and folder_name[0].isdigit() else folder_name,
        "description": f"Test behavior: {folder_name}",
        "goal": f"Test goal for {folder_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": [
            f"**BEHAVIOR WORKFLOW INSTRUCTIONS:**",
            "",
            f"Test instructions for {folder_name}."
        ],
        "actions_workflow": {
            "actions": [
                {"name": "clarify", "order": 1, "next_action": "strategy"},
                {"name": "strategy", "order": 2, "next_action": "build"},
                {"name": "build", "order": 3, "next_action": "validate"},
                {"name": "validate", "order": 4, "next_action": "render"},
                {"name": "render", "order": 5}
            ]
        },
        "trigger_words": {
            "description": f"Trigger words for {folder_name}",
            "patterns": [f"test.*{folder_name}"],
            "priority": 10
        }
    }
    behavior_file = behavior_folder / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    
    return behavior_folder


class TestFindBehaviorFolder:
    """Tests for find_behavior_folder utility function."""

    def test_finds_behavior_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find behavior folder with number prefix
        GIVEN: Behavior folder exists with name 'tests'
        WHEN: find_behavior_folder is called with behavior name (tests)
        THEN: Returns path to folder 'tests'
        """
        # Given: Create numbered behavior folder
        bot_name = 'test_bot'
        folder_name = 'tests'
        behavior_name = 'tests'
        
        behavior_folder = create_behavior_folder_with_json(bot_directory, folder_name)
        
        # When: Behavior folders are directly named (no numbered prefixes)
        found_folder = bot_directory / 'behaviors' / behavior_name
        
        # Then: Returns numbered folder
        assert found_folder == behavior_folder
        assert found_folder.name == 'tests'

    def test_finds_shape_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find shape folder with number prefix
        GIVEN: Behavior folder exists with name 'shape'
        WHEN: find_behavior_folder is called with behavior name (shape)
        THEN: Returns path to folder 'shape'
        """
        # Given: Create numbered behavior folder
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, 'shape')
        
        # When: Behavior folders are directly named
        found_folder = bot_directory / 'behaviors' / 'shape'
        
        # Then: Returns numbered folder
        assert found_folder == behavior_folder
        assert found_folder.name == 'shape'

    def test_finds_exploration_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find exploration folder with number prefix
        GIVEN: Behavior folder exists with name 'exploration'
        WHEN: find_behavior_folder is called with behavior name (exploration)
        THEN: Returns path to folder 'exploration'
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, 'exploration')
        
        # When: Behavior folders are directly named
        found_folder = bot_directory / 'behaviors' / 'exploration'
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == 'exploration'

    def test_raises_error_when_behavior_folder_not_found(self, bot_directory, workspace_directory):
        """
        SCENARIO: Raises error when behavior folder doesn't exist
        GIVEN: Behavior folder does not exist
        WHEN: BehaviorConfig tries to load behavior.json
        THEN: Raises FileNotFoundError with clear message
        """
        # Given: No behavior folder exists and environment is bootstrapped
        bootstrap_env(bot_directory, workspace_directory)
        bot_name = 'test_bot'
        behavior_name = 'nonexistent'
        
        # When: Creating BehaviorConfig for nonexistent behavior
        # Then: FileNotFoundError is raised
        from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
        from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
        
        bot_paths = BotPaths(bot_directory=bot_directory)
        with pytest.raises(FileNotFoundError, match="Behavior config not found"):
            BehaviorConfig(behavior_name, bot_paths, bot_name)

    def test_handles_prioritization_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Prioritization Folder With Prefix
        GIVEN: Behavior folder exists as 'prioritization'
        WHEN: find_behavior_folder is called with behavior name (prioritization)
        THEN: Returns path to 'prioritization'
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, 'prioritization')
        
        # When: Behavior folders are directly named
        found_folder = bot_directory / 'behaviors' / 'prioritization'
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == 'prioritization'

    def test_handles_scenarios_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Scenarios Folder With Prefix
        GIVEN: Behavior folder exists as 'scenarios'
        WHEN: find_behavior_folder is called with behavior name (scenarios)
        THEN: Returns path to 'scenarios'
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, 'scenarios')
        
        # When: Behavior folders are directly named
        found_folder = bot_directory / 'behaviors' / 'scenarios'
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == 'scenarios'

    def test_handles_examples_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Examples Folder With Prefix
        GIVEN: Behavior folder exists as 'examples'
        WHEN: find_behavior_folder is called with behavior name (examples)
        THEN: Returns path to 'examples'
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, 'examples')
        
        # When: Behavior folders are directly named
        found_folder = bot_directory / 'behaviors' / 'examples'
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == 'examples'
