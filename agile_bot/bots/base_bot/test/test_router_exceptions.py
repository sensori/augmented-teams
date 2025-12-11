"""
Tests for Router exception handling - no fallbacks.

Router should raise exceptions when:
- Workflow state file doesn't exist
- Workflow state has no completed actions
- Unknown action in workflow state
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.state.router import Router


def test_router_raises_exception_when_state_file_does_not_exist(tmp_path):
    """Router should raise FileNotFoundError when workflow state file doesn't exist."""
    router = Router(workspace_root=tmp_path)
    state_file = tmp_path / 'workflow_state.json'
    
    # State file doesn't exist
    assert not state_file.exists()
    
    # When determining next action
    with pytest.raises(FileNotFoundError, match="Workflow state file not found"):
        router.determine_next_action_from_state(state_file)


def test_router_raises_exception_when_no_completed_actions(tmp_path):
    """Router should raise ValueError when state file has no completed actions."""
    router = Router(workspace_root=tmp_path)
    state_file = tmp_path / 'workflow_state.json'
    
    # Create state file with no completed actions
    state_file.write_text(json.dumps({
        'current_behavior': 'story_bot.shape',
        'current_action': 'story_bot.shape.gather_context',
        'completed_actions': [],
        'timestamp': '2025-12-04T16:00:00.000000'
    }), encoding='utf-8')
    
    # When determining next action
    with pytest.raises(ValueError, match="no completed actions"):
        router.determine_next_action_from_state(state_file)


def test_router_raises_exception_when_unknown_action(tmp_path):
    """Router should raise ValueError when last action is unknown."""
    router = Router(workspace_root=tmp_path)
    state_file = tmp_path / 'workflow_state.json'
    
    # Create state file with unknown action
    state_file.write_text(json.dumps({
        'current_behavior': 'story_bot.shape',
        'current_action': 'story_bot.shape.unknown_action',
        'completed_actions': [
            {'action_state': 'story_bot.shape.unknown_action', 'timestamp': '2025-12-04T16:00:00.000000'}
        ],
        'timestamp': '2025-12-04T16:00:00.000000'
    }), encoding='utf-8')
    
    # When determining next action
    with pytest.raises(ValueError, match="Unknown last action"):
        router.determine_next_action_from_state(state_file)












