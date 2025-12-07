"""
Complete Workflow Integration Tests

Tests for 'Complete Workflow Integration' story:
- Workflow determines action from current_action (with fallback to completed_actions)
- Guardrails load with number prefixes
- Actions save state when called directly
- Close tool marks complete and transitions
- Jumping to different behavior-action updates state correctly
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.bot import Bot


# ============================================================================
# STORY: Complete Workflow Integration
# ============================================================================

class TestCompleteWorkflowIntegration:
    """Story: Complete Workflow Integration - End-to-end test of the complete workflow with all fixes."""

    def test_complete_workflow_end_to_end(self, tmp_path):
    """
    Complete end-to-end workflow test demonstrating all fixes working together.
    
    Flow:
    1. Start at initialize_project
    2. Confirm → Saves to completed_actions
    3. Forward to gather_context
    4. Close gather_context → Transitions to decide_planning_criteria
    5. Jump to discovery.gather_context (out of order)
    6. Verify state shows discovery.gather_context (not initialize_project)
    7. Close and verify proper transition
    """
    # Setup
    bot_name = 'story_bot'
    
    # Create bot structure
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    config_dir = bot_dir / 'config'
    config_dir.mkdir(parents=True)
    
    # Bot config with multiple behaviors
    config = {'name': bot_name, 'behaviors': ['shape', 'discovery']}
    (config_dir / 'bot_config.json').write_text(json.dumps(config))
    
    # Create project
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir()
    (bot_dir / 'current_project.json').write_text(json.dumps({'current_project': str(project_dir)}))
    
    # Create base_actions with next_action transitions
    base_actions_dir = tmp_path / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    actions_config = [
        ('initialize_project', 1, 'gather_context'),
        ('gather_context', 2, 'decide_planning_criteria'),
        ('decide_planning_criteria', 3, 'build_knowledge'),
        ('build_knowledge', 4, 'render_output')
    ]
    
    for action_name, order, next_action in actions_config:
        action_dir = base_actions_dir / f'{order}_{action_name}'
        action_dir.mkdir(parents=True)
        (action_dir / 'instructions.json').write_text(json.dumps({'instructions': [f'Test {action_name}']}))
        (action_dir / 'action_config.json').write_text(json.dumps({
            'name': action_name,
            'workflow': True,
            'order': order,
            'next_action': next_action
        }))
    
    # Create Bot
    bot = Bot(bot_name=bot_name, workspace_root=tmp_path, config_path=config_dir / 'bot_config.json')
    workflow_file = project_dir / 'workflow_state.json'
    
    # Step 1: Initialize project
    print("\n=== Step 1: Initialize Project ===")
    result = bot.shape.initialize_project({'confirm': True, 'project_area': str(project_dir)})
    assert result.action == 'initialize_project'
    assert bot.shape.workflow.is_action_completed('initialize_project')
    print("✓ initialize_project completed and saved")
    
    # Step 2: Forward (will execute initialize_project again, see it's complete, and transition)
    print("\n=== Step 2: Forward (transition from initialize_project) ===")
    result = bot.shape.forward_to_current_action()
    assert result.action == 'initialize_project'  # Still returns initialize_project
    assert bot.shape.workflow.current_state == 'gather_context'  # But transitioned to gather_context
    print("✓ forward_to_current_action checked completion and transitioned to gather_context")
    
    # Step 3: Call forward again to execute gather_context
    print("\n=== Step 3: Execute gather_context ===")
    result = bot.shape.forward_to_current_action()
    assert result.action == 'gather_context'
    assert bot.shape.workflow.current_state == 'gather_context'
    
    state = json.loads(workflow_file.read_text())
    assert state['current_action'] == 'story_bot.shape.gather_context'
    print("✓ Executed gather_context, state saved")
    
    # Step 4: Close gather_context
    print("\n=== Step 4: Close gather_context ===")
    bot.shape.workflow.save_completed_action('gather_context')
    bot.shape.workflow.transition_to_next()
    assert bot.shape.workflow.current_state == 'decide_planning_criteria'
    assert bot.shape.workflow.is_action_completed('gather_context')
    print("✓ gather_context closed, transitioned to decide_planning_criteria")
    
    # Step 5: Jump to discovery.gather_context (out of order)
    print("\n=== Step 5: Jump to discovery.gather_context (out of order) ===")
    result = bot.discovery.gather_context()
    assert result.behavior == 'discovery'
    assert result.action == 'gather_context'
    
    state = json.loads(workflow_file.read_text())
    assert state['current_behavior'] == 'story_bot.discovery'
    assert state['current_action'] == 'story_bot.discovery.gather_context'
    print("✓ Jumped to discovery.gather_context, state correctly shows discovery.gather_context")
    
    # Step 6: Close discovery.gather_context
    print("\n=== Step 6: Close discovery.gather_context ===")
    bot.discovery.workflow.save_completed_action('gather_context')
    bot.discovery.workflow.transition_to_next()
    assert bot.discovery.workflow.current_state == 'decide_planning_criteria'
    print("✓ discovery.gather_context closed, transitioned to decide_planning_criteria")
    
    # Verify completed actions from both behaviors
    state = json.loads(workflow_file.read_text())
    action_states = [a['action_state'] for a in state.get('completed_actions', [])]
    assert 'story_bot.shape.initialize_project' in action_states
    assert 'story_bot.shape.gather_context' in action_states
    assert 'story_bot.discovery.gather_context' in action_states
    print("✓ All completed actions tracked across both behaviors")
    
    print("\n=== SUCCESS: Complete workflow with all fixes working! ===")

