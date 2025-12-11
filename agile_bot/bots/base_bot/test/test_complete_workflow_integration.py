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
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env


# ============================================================================
# STORY: Complete Workflow Integration
# ============================================================================

class TestCompleteWorkflowIntegration:
    """Story: Complete Workflow Integration - End-to-end test of the complete workflow with all fixes."""

    def test_complete_workflow_end_to_end(self, bot_directory, workspace_directory, tmp_path):
        """
        Complete end-to-end workflow test demonstrating all fixes working together.

        Flow:
        1. Start at gather_context
        2. Execute gather_context
        3. Close gather_context -> Transitions to decide_planning_criteria
        4. Jump to discovery.gather_context (out of order)
        5. Verify state shows discovery.gather_context
        6. Close and verify proper transition
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Setup
        bot_name = 'story_bot'
        
        # Bot config with multiple behaviors
        config = {'name': bot_name, 'behaviors': ['shape', 'discovery']}
        config_path = bot_directory / 'config' / 'bot_config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config), encoding='utf-8')
        
        # Create behavior folders
        for behavior in ['shape', 'discovery']:
            behavior_dir = bot_directory / 'behaviors' / behavior
            behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base_actions with next_action transitions
        # Use actual repo root so load_workflow_states_and_transitions can find them
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        base_actions_dir.mkdir(parents=True, exist_ok=True)
        
        actions_config = [
            ('gather_context', 2, 'decide_planning_criteria'),
            ('decide_planning_criteria', 3, 'build_knowledge'),
            ('build_knowledge', 4, 'validate_rules'),
            ('validate_rules', 5, 'render_output')
        ]
        
        for action_name, order, next_action in actions_config:
            action_dir = base_actions_dir / f'{order}_{action_name}'
            action_dir.mkdir(parents=True, exist_ok=True)
            (action_dir / 'instructions.json').write_text(json.dumps({'instructions': [f'Test {action_name}']}), encoding='utf-8')
            (action_dir / 'action_config.json').write_text(json.dumps({
                'name': action_name,
                'workflow': True,
                'order': order,
                'next_action': next_action
            }), encoding='utf-8')
        
        # Create Bot
        bot = Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)
        workflow_file = workspace_directory / 'workflow_state.json'
        
        # Step 1: Execute gather_context
        print("\n=== Step 1: Execute gather_context ===")
        result = bot.shape.gather_context()
        assert result.action == 'gather_context'
        assert bot.shape.workflow.current_state == 'gather_context'
        
        state = json.loads(workflow_file.read_text(encoding='utf-8'))
        assert state['current_action'] == 'story_bot.shape.gather_context'
        print("[OK] Executed gather_context, state saved")
        
        # Step 2: Close gather_context
        print("\n=== Step 2: Close gather_context ===")
        bot.shape.workflow.save_completed_action('gather_context')
        # Reload state to ensure workflow sees the completed action
        bot.shape.workflow.load_state()
        bot.shape.workflow.transition_to_next()
        assert bot.shape.workflow.current_state == 'decide_planning_criteria'
        assert bot.shape.workflow.is_action_completed('gather_context')
        print("[OK] gather_context closed, transitioned to decide_planning_criteria")
        
        # Step 3: Jump to discovery.gather_context (out of order)
        print("\n=== Step 3: Jump to discovery.gather_context (out of order) ===")
        result = bot.discovery.gather_context()
        assert result.behavior == 'discovery'
        assert result.action == 'gather_context'
        
        state = json.loads(workflow_file.read_text(encoding='utf-8'))
        assert state['current_behavior'] == 'story_bot.discovery'
        assert state['current_action'] == 'story_bot.discovery.gather_context'
        print("[OK] Jumped to discovery.gather_context, state correctly shows discovery.gather_context")
        
        # Step 4: Close discovery.gather_context
        print("\n=== Step 4: Close discovery.gather_context ===")
        bot.discovery.workflow.save_completed_action('gather_context')
        bot.discovery.workflow.transition_to_next()
        assert bot.discovery.workflow.current_state == 'decide_planning_criteria'
        print("[OK] discovery.gather_context closed, transitioned to decide_planning_criteria")
        
        # Verify completed actions from both behaviors
        state = json.loads(workflow_file.read_text(encoding='utf-8'))
        action_states = [a['action_state'] for a in state.get('completed_actions', [])]
        assert 'story_bot.shape.gather_context' in action_states
        assert 'story_bot.discovery.gather_context' in action_states
        print("[OK] All completed actions tracked across both behaviors")
        
        print("\n=== SUCCESS: Complete workflow with all fixes working! ===")
