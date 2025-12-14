"""
Pytest fixtures for base_bot tests.

Fixtures here are used across MULTIPLE test files (cross-epic).
For helpers used by only ONE test file, define them inline in that file.
"""
import json
import pytest
import os
from pathlib import Path
from typing import Tuple


# ============================================================================
# FIXTURES - Cross-file reusable setup
# ============================================================================

@pytest.fixture
def repo_root(tmp_path):
    """Fixture: Repository root directory."""
    return tmp_path

@pytest.fixture
def bot_directory(tmp_path):
    """Fixture: Bot directory for test bot."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'story_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir

@pytest.fixture
def workspace_directory(tmp_path):
    """Fixture: Workspace directory for content files."""
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True)
    return workspace_dir

@pytest.fixture(autouse=True)
def clean_env():
    """Fixture: Clean environment variables before and after each test."""
    # Store original values
    original_bot_dir = os.environ.get('BOT_DIRECTORY')
    original_working_area = os.environ.get('WORKING_AREA')
    original_working_dir = os.environ.get('WORKING_DIR')
    
    # Clear for test
    for key in ['BOT_DIRECTORY', 'WORKING_AREA', 'WORKING_DIR']:
        if key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original values
    for key in ['BOT_DIRECTORY', 'WORKING_AREA', 'WORKING_DIR']:
        if key in os.environ:
            del os.environ[key]
        
    if original_bot_dir:
        os.environ['BOT_DIRECTORY'] = original_bot_dir
    if original_working_area:
        os.environ['WORKING_AREA'] = original_working_area
    if original_working_dir:
        os.environ['WORKING_DIR'] = original_working_dir

@pytest.fixture
def bot_name():
    """Fixture: Default bot name for tests."""
    return 'story_bot'

@pytest.fixture
def standard_workflow_config():
    """Fixture: Standard workflow states and transitions."""
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    return states, transitions


# ============================================================================
# FACTORY FUNCTIONS - Build test objects
# ============================================================================

def bootstrap_env(bot_dir: Path, workspace_dir: Path):
    """Bootstrap environment variables for tests."""
    os.environ['BOT_DIRECTORY'] = str(bot_dir)
    os.environ['WORKING_AREA'] = str(workspace_dir)

def create_bot_config_file(
    bot_dir: Path,
    bot_name: str,
    behaviors: list,
    workspace_root: Path = None
) -> Path:
    """Factory: Create bot config file in bot directory.
    
    Args:
        bot_dir: Bot directory path. If workspace_root is provided and bot_dir is relative,
                 bot_dir will be resolved relative to workspace_root/agile_bot/bots/bot_name.
                 Otherwise, bot_dir should be absolute or relative to current working directory.
        bot_name: Bot name
        behaviors: List of behavior names
        workspace_root: Optional workspace root. If provided and bot_dir doesn't contain 'agile_bot',
                       constructs path as workspace_root/agile_bot/bots/bot_name/config
    
    Returns:
        Path to created bot_config.json file
    """
    # Handle workspace_root pattern: workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
    if workspace_root and 'agile_bot' not in str(bot_dir):
        # Construct full path from workspace_root
        config_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config'
    else:
        # Use bot_dir directly: bot_dir / 'config'
        config_dir = bot_dir / 'config'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_file

def create_workflow_state_file(
    workspace_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None,
    action_format: str = "full",
    timestamp: str = None
) -> Path:
    """Factory: Create workflow_state.json in workspace directory.
    
    Args:
        workspace_dir: Workspace directory where workflow_state.json will be created
        bot_name: Bot name
        behavior: Behavior name
        current_action: Current action name
        completed_actions: Optional list of completed actions
        action_format: Format for current_action field:
            - "full": bot_name.behavior.action (default)
            - "short": action only (no prefix)
            - "behavior_action": behavior.action (no bot_name prefix)
        timestamp: Optional timestamp string. If None, uses default timestamp.
    
    Returns:
        Path to created workflow_state.json file
    """
    # Format current_action based on action_format
    if action_format == "full":
        current_action_state = f'{bot_name}.{behavior}.{current_action}'
    elif action_format == "short":
        current_action_state = current_action
    elif action_format == "behavior_action":
        current_action_state = f'{behavior}.{current_action}'
    else:
        current_action_state = f'{bot_name}.{behavior}.{current_action}'
    
    # Use provided timestamp or default
    if timestamp is None:
        timestamp = '2025-12-04T16:00:00.000000'
    
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': current_action_state,
        'timestamp': timestamp,
        'completed_actions': completed_actions or []
    }
    workflow_file = workspace_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state), encoding='utf-8')
    return workflow_file

def create_base_actions_structure(bot_directory: Path) -> Path:
    """Factory: Create base_actions directory structure in bot_directory (no fallback)."""
    base_actions_dir = bot_directory / 'base_actions'
    
    workflow_actions = [
        ('1_gather_context', 'gather_context', 1, 'decide_planning_criteria'),
        ('2_decide_planning_criteria', 'decide_planning_criteria', 2, 'build_knowledge'),
        ('3_build_knowledge', 'build_knowledge', 3, 'validate_rules'),
        ('4_validate_rules', 'validate_rules', 4, 'render_output'),
        ('5_render_output', 'render_output', 5, None)
    ]
    
    for folder_name, action_name, order, next_action in workflow_actions:
        action_dir = base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        action_config = {
            'name': action_name,
            'workflow': True,
            'order': order
        }
        if next_action:
            action_config['next_action'] = next_action
            
        (action_dir / 'action_config.json').write_text(json.dumps(action_config), encoding='utf-8')
        (action_dir / 'instructions.json').write_text(json.dumps({'instructions': [f'{action_name} base instructions']}), encoding='utf-8')
    
    return base_actions_dir


# ============================================================================
# SHARED GIVEN/WHEN/THEN HELPERS - Used across multiple test files
# ============================================================================

def given_bot_name_and_behaviors_setup(bot_name: str = 'story_bot', behaviors: list = None):
    """Given: Bot name and behaviors setup.
    
    Args:
        bot_name: Bot name (default: 'story_bot')
        behaviors: List of behavior names (default: ['shape', 'discovery'])
    
    Returns:
        Tuple of (bot_name, behaviors)
    """
    if behaviors is None:
        behaviors = ['shape', 'discovery']
    return bot_name, behaviors

def given_bot_name_and_behavior_setup(bot_name: str = 'story_bot', behavior: str = 'shape'):
    """Given: Bot name and behavior setup.
    
    Args:
        bot_name: Bot name (default: 'story_bot')
        behavior: Behavior name (default: 'shape')
    
    Returns:
        Tuple of (bot_name, behavior)
    """
    return bot_name, behavior

def create_test_workflow(
    bot_dir: Path,
    workspace_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None,
    return_workflow_file: bool = True
) -> Tuple:
    """Factory: Create workflow with specified state for testing.
    
    Args:
        bot_dir: Bot directory path
        workspace_dir: Workspace directory path
        bot_name: Bot name
        behavior: Behavior name
        current_action: Current action name
        completed_actions: Optional list of completed actions
        return_workflow_file: If True, returns (Workflow, Path). If False, returns Workflow only.
    
    Returns:
        If return_workflow_file is True: Tuple of (Workflow, Path to workflow_state.json)
        If return_workflow_file is False: Workflow instance
    """
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    # Create workflow state file
    workflow_file = create_workflow_state_file(
        workspace_dir, bot_name, behavior, current_action, completed_actions
    )
    
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=states,
        transitions=transitions
    )
    
    if return_workflow_file:
        return workflow, workflow_file
    else:
        return workflow

def create_base_action_instructions(action_name: str, instructions: list = None) -> dict:
    """Factory: Create base action instructions dictionary.
    
    Args:
        action_name: Action name
        instructions: Optional list of instruction strings. If None, uses default.
    
    Returns:
        Dictionary with 'instructions' key containing list of instruction strings
    """
    if instructions is None:
        instructions = [f'{action_name} base instructions']
    return {'instructions': instructions}
