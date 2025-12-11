"""
Base Action Tests

Tests for base action functionality that applies to all actions:
- Inject Next Behavior Reminder
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, read_activity_log, create_activity_log_file, create_workflow_state
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_bot_config(bot_directory: Path, behaviors: list) -> Path:
    """Helper: Create bot_config.json with behavior sequence."""
    config_dir = bot_directory / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    bot_config_file = config_dir / 'bot_config.json'
    bot_config = {
        'name': 'story_bot',
        'behaviors': behaviors
    }
    bot_config_file.write_text(json.dumps(bot_config), encoding='utf-8')
    return bot_config_file


def create_workflow_states(bot_directory: Path, states: list) -> Path:
    """Helper: Create workflow.json with states."""
    workflow_file = bot_directory / 'workflow.json'
    workflow_data = {
        'states': states,
        'transitions': []
    }
    workflow_file.write_text(json.dumps(workflow_data), encoding='utf-8')
    return workflow_file

# ============================================================================
# STORY: Inject Next Behavior Reminder
# ============================================================================

class TestInjectNextBehaviorReminder:
    """Story: Inject Next Behavior Reminder - Tests that next behavior reminder is injected for final actions."""

    def test_next_behavior_reminder_injected_when_final_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is injected when action is final action
        GIVEN: validate_rules is the final action in behavior workflow
        AND: bot_config.json defines behavior sequence
        WHEN: validate_rules action executes
        THEN: base_instructions include next behavior reminder
        AND: reminder contains next behavior name and prompt text
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: bot_config.json with behavior sequence
        create_bot_config(bot_directory, ['shape', 'prioritization', 'arrange', 'discovery'])
        
        # Given: Base action instructions exist
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        validate_rules_dir = base_actions_dir / '5_validate_rules'
        validate_rules_dir.mkdir(parents=True, exist_ok=True)
        
        base_instructions = {
            'instructions': [
                'Load and review clarification.json and planning.json',
                'Check Content Data against all rules',
                'Generate a validation report'
            ]
        }
        instructions_file = validate_rules_dir / 'instructions.json'
        instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
        
        # Given: action_config.json files for workflow actions (so load_workflow_states_and_transitions can find them)
        # Create action configs for all workflow actions
        workflow_actions = [
            ('1_gather_context', 'gather_context', 1),
            ('2_decide_planning_criteria', 'decide_planning_criteria', 2),
            ('3_build_knowledge', 'build_knowledge', 3),
            ('4_render_output', 'render_output', 4),
            ('5_validate_rules', 'validate_rules', 5)
        ]
        for folder_name, action_name, order in workflow_actions:
            action_dir = base_actions_dir / folder_name
            action_dir.mkdir(parents=True, exist_ok=True)
            action_config = {
                'name': action_name,
                'workflow': True,
                'order': order
            }
            action_config_file = action_dir / 'action_config.json'
            action_config_file.write_text(json.dumps(action_config), encoding='utf-8')
        
        # When: Action executes (shape behavior, validate_rules is final)
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        result = action.execute(parameters={})
        
        # Debug: Check if reminder was injected
        instructions = result['instructions']
        base_instructions_list = instructions['base_instructions']
        
        # Debug: Check if this is detected as final action
        is_final = action._is_final_action()
        reminder_text = action._get_next_behavior_reminder()
        
        # Then: base_instructions include next behavior reminder
        # Find reminder section
        reminder_found = False
        next_behavior_found = False
        for i, instruction in enumerate(base_instructions_list):
            if 'NEXT BEHAVIOR REMINDER' in instruction:
                reminder_found = True
                # Check next instruction contains next behavior
                if i + 1 < len(base_instructions_list):
                    next_instruction = base_instructions_list[i + 1]
                    if 'prioritization' in next_instruction.lower():
                        next_behavior_found = True
        
        assert reminder_found, (
            "base_instructions should include 'NEXT BEHAVIOR REMINDER' section"
        )
        assert next_behavior_found, (
            "Reminder should mention 'prioritization' as the next behavior"
        )
        
        # Then: Reminder contains prompt text
        instructions_text = ' '.join(base_instructions_list)
        assert 'next behavior in sequence' in instructions_text.lower(), (
            "Reminder should contain 'next behavior in sequence' text"
        )
        assert 'would you like to continue' in instructions_text.lower() or 'work on a different behavior' in instructions_text.lower(), (
            "Reminder should contain prompt asking user if they want to continue"
        )

    def test_next_behavior_reminder_not_injected_when_not_final_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when action is not final
        GIVEN: validate_rules is NOT the final action (render_output comes after)
        AND: bot_config.json defines behavior sequence
        WHEN: validate_rules action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: bot_config.json with behavior sequence
        create_bot_config(bot_directory, ['shape', 'prioritization', 'arrange'])
        
        # Given: Workflow states file showing validate_rules is NOT final
        create_workflow_states(bot_directory, [
            'gather_context', 'decide_planning_criteria', 'build_knowledge', 
            'validate_rules', 'render_output'
        ])
        
        # Given: Base action instructions exist for validate_rules
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        validate_rules_dir = base_actions_dir / '4_validate_rules'
        validate_rules_dir.mkdir(parents=True, exist_ok=True)
        
        base_instructions = {
            'instructions': [
                'Validate story graph against rules',
                'Generate validation report'
            ]
        }
        instructions_file = validate_rules_dir / 'instructions.json'
        instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
        
        # When: validate_rules action executes (not final action)
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        result = action.execute(parameters={})
        
        # Then: base_instructions do NOT include next behavior reminder
        instructions = result.get('instructions', {})
        base_instructions_list = instructions.get('base_instructions', [])
        
        instructions_text = ' '.join(base_instructions_list)
        assert 'NEXT BEHAVIOR REMINDER' not in instructions_text, (
            "base_instructions should NOT include 'NEXT BEHAVIOR REMINDER' when action is not final"
        )

    def test_next_behavior_reminder_not_injected_when_no_next_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
        GIVEN: discovery is the last behavior in bot_config.json
        AND: render_output is the final action
        WHEN: render_output action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: bot_config.json with discovery as last behavior
        create_bot_config(bot_directory, ['shape', 'prioritization', 'discovery'])
        
        # Given: Base action instructions exist
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        render_output_dir = base_actions_dir / '5_render_output'
        render_output_dir.mkdir(parents=True, exist_ok=True)
        
        base_instructions = {
            'instructions': [
                'Render story map documents',
                'Render domain model documents'
            ]
        }
        instructions_file = render_output_dir / 'instructions.json'
        instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
        
        # Given: Workflow states file showing render_output is final action
        create_workflow_states(bot_directory, [
            'gather_context', 'decide_planning_criteria', 'build_knowledge', 
            'validate_rules', 'render_output'
        ])
        
        # When: Action executes (discovery behavior, last in sequence)
        from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='discovery',
            bot_directory=bot_directory
        )
        result = action.execute(parameters={})
        
        # Then: base_instructions do NOT include next behavior reminder
        instructions = result['instructions']
        base_instructions_list = instructions['base_instructions']
        
        instructions_text = ' '.join(base_instructions_list)
        assert 'NEXT BEHAVIOR REMINDER' not in instructions_text, (
            "base_instructions should NOT include 'NEXT BEHAVIOR REMINDER' when current behavior is last in sequence"
        )

