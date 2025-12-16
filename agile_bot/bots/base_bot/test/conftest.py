"""
Pytest fixtures for base_bot tests.

Fixtures here are used across MULTIPLE test files (cross-epic).
For helpers used by only ONE test file, define them inline in that file.
"""
import json
import pytest
import os
import sys
from pathlib import Path
from typing import Tuple

# Add project root to Python path for imports
_project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# ============================================================================
# BEHAVIOR ACTION STATE HELPERS - State is managed by Behaviors and Actions collections
# ============================================================================

# Workflow class removed - use Bot.behaviors and Behavior.actions directly
# Behaviors know their order and what's current
# Actions know their order and what's current
# State is persisted in behavior_action_state.json

class Workflow:
    """DEPRECATED: Use Bot.behaviors and Behavior.actions directly instead."""
    """Mock Workflow class for testing - Workflow class was removed from production code."""
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path, states: list = None, transitions: list = None, workspace_root: Path = None):
        self.bot_name = bot_name
        self.behavior = behavior
        self.bot_directory = bot_directory
        self.workspace_root = workspace_root
        self.states = states or []
        self.transitions = transitions or []
        self._current_state = states[0] if states else None
        self._completed_actions = []
        
        # Mock machine object for tests that use workflow.machine.set_state()
        class MockMachine:
            def __init__(self, workflow):
                self.workflow = workflow
            def set_state(self, state: str):
                self.workflow._current_state = state
        self.machine = MockMachine(self)
    
    @property
    def current_state(self) -> str:
        """Get current state."""
        return self._current_state
    
    @property
    def state(self) -> str:
        """Get current state (alias)."""
        return self._current_state
    
    @current_state.setter
    def current_state(self, value: str):
        """Set current state."""
        self._current_state = value
    
    @state.setter
    def state(self, value: str):
        """Set current state (alias)."""
        self._current_state = value
    
    def navigate_to_action(self, action: str, out_of_order: bool = False):
        """Navigate to action."""
        if action in self.states:
            self._current_state = action
            if out_of_order:
                # Remove completed actions after the target action
                try:
                    target_index = self.states.index(action)
                    # Remove completed actions that come after target
                    self._completed_actions = [
                        ca for ca in self._completed_actions
                        if self._get_action_name_from_state(ca.get('action_state', '')) not in self.states[target_index + 1:]
                    ]
                    self.save_state()
                except ValueError:
                    pass
    
    def proceed(self):
        """Proceed to next state."""
        if self._current_state and self.transitions:
            for transition in self.transitions:
                if transition.get('source') == self._current_state:
                    self._current_state = transition.get('dest')
                    return
        # If no transition found, stay at current state (final action)
    
    def transition_to_next(self):
        """Transition to next state and save."""
        self.proceed()
        self.save_state()
    
    def save_state(self):
        """Save workflow state to file."""
        if self.workspace_root:
            state_file = self.workspace_root / 'workflow_state.json'
        else:
            # Try to find workspace from environment
            workspace_dir = Path(os.environ.get('WORKING_AREA', self.bot_directory.parent / 'workspace'))
            state_file = workspace_dir / 'workflow_state.json'
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            'current_behavior': f'{self.bot_name}.{self.behavior}',
            'current_action': f'{self.bot_name}.{self.behavior}.{self._current_state}' if self._current_state else '',
            'timestamp': '2025-12-04T16:00:00.000000',
            'completed_actions': self._completed_actions
        }
        state_file.write_text(json.dumps(state_data), encoding='utf-8')
    
    def save_completed_action(self, action: str):
        """Save completed action."""
        action_state = f'{self.bot_name}.{self.behavior}.{action}'
        if not any(a.get('action_state') == action_state for a in self._completed_actions):
            self._completed_actions.append({
                'action_state': action_state,
                'timestamp': '2025-12-04T16:00:00.000000'
            })
        self.save_state()
    
    def load_state(self):
        """Load workflow state from file."""
        if self.workspace_root:
            state_file = self.workspace_root / 'workflow_state.json'
        else:
            workspace_dir = Path(os.environ.get('WORKING_AREA', self.bot_directory.parent / 'workspace'))
            state_file = workspace_dir / 'workflow_state.json'
        
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_action = state_data.get('current_action', '')
            self._completed_actions = state_data.get('completed_actions', [])
            
            if current_action:
                action_name = current_action.split('.')[-1]
                if action_name in self.states:
                    self._current_state = action_name
            else:
                # Fall back to next action after last completed action
                if self._completed_actions:
                    # Find the last completed action for this behavior
                    last_completed = None
                    expected_behavior_prefix = f'{self.bot_name}.{self.behavior}.'
                    for completed in reversed(self._completed_actions):  # Iterate in reverse to get last one first
                        action_state = completed.get('action_state', '')
                        if action_state and action_state.startswith(expected_behavior_prefix):
                            action_name = action_state.split('.')[-1]
                            if action_name in self.states:
                                last_completed = action_name
                                break  # Found the last completed action for this behavior
                    
                    # Find next action after last completed
                    if last_completed and last_completed in self.states:
                        try:
                            current_index = self.states.index(last_completed)
                            if current_index + 1 < len(self.states):
                                self._current_state = self.states[current_index + 1]
                            else:
                                # Already at last action
                                self._current_state = last_completed
                        except ValueError:
                            # Last completed not in states, start at first
                            self._current_state = self.states[0] if self.states else None
                    else:
                        # No completed actions for this behavior, start at first
                        self._current_state = self.states[0] if self.states else None
                else:
                    # No completed actions, start at first
                    self._current_state = self.states[0] if self.states else None
    
    def _get_action_name_from_state(self, action_state: str) -> str:
        """Get action name from action_state string."""
        if action_state:
            parts = action_state.split('.')
            if len(parts) >= 3:
                return parts[-1]
        return ''
    
    def is_action_completed(self, action_name: str) -> bool:
        """Check if action is completed."""
        action_state = f'{self.bot_name}.{self.behavior}.{action_name}'
        return any(a.get('action_state') == action_state for a in self._completed_actions)


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

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

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
def standard_action_order():
    """Fixture: Standard action order (DEPRECATED - use Bot/Behavior/Actions directly)."""
    # Behaviors and Actions manage their own order
    # Actions are ordered by 'order' field in action_config.json
    actions = ['clarify', 'strategy', 'build', 'validate', 'render']
    return actions

@pytest.fixture
def bot_config_file_path(bot_directory):
    """Fixture: Bot config file path."""
    config_dir = bot_directory / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': 'test_bot'}), encoding='utf-8')
    return config_file


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
    behaviors: list = None,  # Deprecated - behaviors are discovered from folders
    workspace_root: Path = None
) -> Path:
    """Factory: Create bot config file in bot directory.
    
    BotConfig expects bot_config.json directly in bot_directory, not in config/ subdirectory.
    Behaviors are discovered from folders, not from config.
    """
    # BotConfig expects bot_config.json directly in bot_directory
    bot_dir.mkdir(parents=True, exist_ok=True)
    config_file = bot_dir / 'bot_config.json'
    # Behaviors are discovered from folders, not stored in config
    config_file.write_text(json.dumps({'name': bot_name}), encoding='utf-8')
    return config_file

def create_behavior_action_state_file(
    workspace_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None,
    action_format: str = "full",
    timestamp: str = None
) -> Path:
    """Factory: Create behavior_action_state.json in workspace directory.
    
    Behaviors know their order. Actions know their order.
    State tracks current behavior and current action.
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
    
    behavior_action_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': current_action_state,
        'timestamp': timestamp,
        'completed_actions': completed_actions or []
    }
    state_file = workspace_dir / 'behavior_action_state.json'
    state_file.write_text(json.dumps(behavior_action_state), encoding='utf-8')
    return state_file

def create_base_actions_structure(bot_directory: Path) -> Path:
    """Factory: Create base_actions directory structure in bot_directory (no fallback).
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    
    # Actions are ordered by 'order' field in action_config.json
    # Behaviors know their order from 'order' field in behavior.json
    action_configs = [
        ('clarify', 'clarify', 1, 'strategy'),
        ('strategy', 'strategy', 2, 'build'),
        ('build', 'build', 3, 'validate'),
        ('validate', 'validate', 4, 'render'),
        ('render', 'render', 5, None)
    ]
    
    for folder_name, action_name, order, next_action in action_configs:
        action_dir = base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        action_config = {
            'name': action_name,
            'workflow': True,
            'order': order
        }
        if next_action:
            action_config['next_action'] = next_action
            
        # Instructions are now in action_config.json
        # For build action, include knowledge graph instructions
        if action_name == 'build':
            action_config['instructions'] = [
                f'Build knowledge graph for {action_name}',
                f'{action_name} base instructions'
            ]
        else:
            action_config['instructions'] = [f'{action_name} base instructions']
        (action_dir / 'action_config.json').write_text(json.dumps(action_config), encoding='utf-8')
    
    return base_actions_dir


# ============================================================================
# SHARED GIVEN/WHEN/THEN HELPERS - Used across multiple test files
# ============================================================================

def given_bot_name_and_behaviors_setup(bot_name: str = 'story_bot', behaviors: list = None):
    """Given: Bot name and behaviors setup.
    
    
    """
    if behaviors is None:
        behaviors = ['shape', 'discovery']
    return bot_name, behaviors

def given_bot_name_and_behavior_setup(bot_name: str = 'story_bot', behavior: str = 'shape'):
    """Given: Bot name and behavior setup.
    
    
    """
    return bot_name, behavior

def create_test_behavior_action_state(
    bot_dir: Path,
    workspace_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None,
    return_state_file: bool = True
) -> Tuple:
    """Factory: Create behavior_action_state.json with specified state for testing.
    
    Behaviors know their order. Actions know their order.
    State tracks current behavior and current action.
    """
    # Behaviors and Actions manage their own order and current state
    
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    # Create bot config
    create_bot_config_file(bot_dir, bot_name, [behavior])
    
    # Create behavior.json with actions_workflow.json containing standard actions
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    create_actions_workflow_json(
        bot_directory=bot_dir,
        behavior_name=behavior,
        actions=[
            {'name': 'clarify', 'order': 1, 'next_action': 'strategy'},
            {'name': 'strategy', 'order': 2, 'next_action': 'build'},
            {'name': 'build', 'order': 3, 'next_action': 'validate'},
            {'name': 'validate', 'order': 4, 'next_action': 'render'},
            {'name': 'render', 'order': 5}
        ]
    )
    
    # Create base action configs
    from agile_bot.bots.base_bot.test.test_perform_behavior_action import given_standard_workflow_actions_config
    given_standard_workflow_actions_config(bot_dir)
    
    # Create minimal guardrails files (required for Guardrails initialization)
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    create_minimal_guardrails_files(bot_dir, behavior, bot_name)
    
    # Create behavior_action_state.json file
    state_file = create_behavior_action_state_file(
        workspace_dir, bot_name, behavior, current_action, completed_actions
    )
    
    # Create Bot instance - behaviors and actions manage their own order
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    
    bot_paths = BotPaths(bot_directory=bot_dir)
    bot = Bot(bot_name=bot_name, bot_directory=bot_dir, config_path=bot_dir / 'bot_config.json')
    
    if return_state_file:
        return bot, state_file
    else:
        return bot

def create_base_action_instructions(action_name: str, instructions: list = None) -> dict:
    """Factory: Create base action instructions dictionary.
    
    
    """
    if instructions is None:
        instructions = [f'{action_name} base instructions']
    return {'instructions': instructions}
