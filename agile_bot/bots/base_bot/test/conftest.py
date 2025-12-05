"""
Pytest fixtures for base_bot tests.

Fixtures here are used across MULTIPLE test files (cross-epic).
For helpers used by only ONE test file, define them inline in that file.
"""
import json
import pytest
from pathlib import Path


# ============================================================================
# FIXTURES - Cross-file reusable setup
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Workspace directory structure."""
    workspace = tmp_path
    return workspace

@pytest.fixture
def bot_name():
    """Fixture: Default bot name for tests."""
    return 'story_bot'

@pytest.fixture
def standard_workflow_config():
    """Fixture: Standard workflow states and transitions."""
    states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    ]
    return states, transitions


# ============================================================================
# FACTORY FUNCTIONS - Build test objects
# ============================================================================

def create_bot_dir(workspace: Path, bot_name: str) -> Path:
    """Factory: Create bot directory structure."""
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True, exist_ok=True)
    return bot_dir

def create_project_dir(workspace: Path, project_name: str = 'test_project') -> Path:
    """Factory: Create project directory."""
    project_dir = workspace / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

def create_current_project_file(workspace: Path, bot_name: str, project_path: str) -> Path:
    """Factory: Create current_project.json file."""
    bot_dir = create_bot_dir(workspace, bot_name)
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.write_text(json.dumps({'current_project': project_path}), encoding='utf-8')
    return current_project_file

def create_workflow_state_file(
    project_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None
) -> Path:
    """Factory: Create workflow_state.json with specified state."""
    workflow_state = {
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'timestamp': '2025-12-04T16:00:00.000000',
        'completed_actions': completed_actions or []
    }
    workflow_file = project_dir / 'workflow_state.json'
    workflow_file.write_text(json.dumps(workflow_state), encoding='utf-8')
    return workflow_file

def create_bot_config_file(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Factory: Create bot config file."""
    config_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_file

def create_base_actions_structure(workspace: Path) -> Path:
    """Factory: Create base_actions directory structure with action configs."""
    base_actions_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    workflow_actions = [
        ('1_initialize_project', 'initialize_project', 1, 'gather_context'),
        ('2_gather_context', 'gather_context', 2, 'decide_planning_criteria'),
        ('3_decide_planning_criteria', 'decide_planning_criteria', 3, 'build_knowledge'),
        ('4_build_knowledge', 'build_knowledge', 4, 'render_output'),
        ('5_render_output', 'render_output', 5, 'validate_rules'),
        ('7_validate_rules', 'validate_rules', 7, None)
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

