"""
Base Action Tests

Tests for base action functionality that applies to all actions:
- Inject Next Behavior Reminder
"""
import pytest
from pathlib import Path
import json
from conftest import create_bot_config_file
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, read_activity_log, create_activity_log_file
)
from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def given_standard_workflow_states(bot_directory: Path):
    """Given: Standard workflow states (gather_context through render_output)."""
    return create_workflow_states(bot_directory, [
        'gather_context', 'decide_planning_criteria', 'build_knowledge', 
        'validate_rules', 'render_output'
    ])


def create_workflow_states(bot_directory: Path, states: list) -> Path:
    """Helper: Create workflow.json with states."""
    workflow_file = bot_directory / 'workflow.json'
    workflow_data = {
        'states': states,
        'transitions': []
    }
    workflow_file.write_text(json.dumps(workflow_data), encoding='utf-8')
    return workflow_file


def given_behavior_workflow_with_validate_rules_as_final(bot_directory: Path, behavior_name: str):
    """Given: behavior.json with validate_rules as final action."""
    create_actions_workflow_json(
        bot_directory=bot_directory,
        behavior_name=behavior_name,
        actions=[
            {'name': 'gather_context', 'order': 1, 'next_action': 'decide_planning_criteria'},
            {'name': 'decide_planning_criteria', 'order': 2, 'next_action': 'build_knowledge'},
            {'name': 'build_knowledge', 'order': 3, 'next_action': 'render_output'},
            {'name': 'render_output', 'order': 4, 'next_action': 'validate_rules'},
            {'name': 'validate_rules', 'order': 5}
        ]
    )


def given_base_action_instructions_exist_for_validate_rules(bot_directory: Path):
    """Given: Base action instructions exist for validate_rules."""
    from agile_bot.bots.base_bot.src.state.workspace import get_base_actions_directory
    base_actions_dir = get_base_actions_directory(bot_directory=bot_directory)
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
    return validate_rules_dir


def given_standard_workflow_actions_config(bot_directory: Path):
    """Given: Standard workflow actions config (gather_context through validate_rules)."""
    return given_action_configs_exist_for_workflow_actions(bot_directory, [
        ('1_gather_context', 'gather_context', 1),
        ('2_decide_planning_criteria', 'decide_planning_criteria', 2),
        ('3_build_knowledge', 'build_knowledge', 3),
        ('4_render_output', 'render_output', 4),
        ('5_validate_rules', 'validate_rules', 5)
    ])


def given_action_configs_exist_for_workflow_actions(bot_directory: Path, workflow_actions: list):
    """Given: action_config.json files for workflow actions."""
    from agile_bot.bots.base_bot.src.state.workspace import get_base_actions_directory
    base_actions_dir = get_base_actions_directory(bot_directory=bot_directory)
    
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


def given_story_graph_file_exists(workspace_directory: Path):
    """Given: Story graph file exists."""
    rendered_dir = workspace_directory / 'docs' / 'stories'
    rendered_dir.mkdir(parents=True, exist_ok=True)
    story_graph_file = rendered_dir / 'story-graph.json'
    story_graph_file.write_text(json.dumps({
        'epics': [],
        'solution': {'name': 'Test Solution'}
    }), encoding='utf-8')
    return story_graph_file


def given_environment_setup_for_final_action_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for final action test."""
    bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    given_behavior_workflow_with_validate_rules_as_final(bot_directory, 'shape')
    given_base_action_instructions_exist_for_validate_rules(bot_directory)
    given_standard_workflow_actions_config(bot_directory)
    given_story_graph_file_exists(workspace_directory)


def given_environment_setup_for_non_final_action_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for non-final action test."""
    bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    given_standard_workflow_states(bot_directory)
    given_base_action_instructions_exist_for_validate_rules_not_final(bot_directory)
    given_action_configs_exist_for_workflow_actions_with_render_output_after(bot_directory)
    given_story_graph_file_exists(workspace_directory)


def given_environment_setup_for_last_behavior_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for last behavior test."""
    bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    given_base_action_instructions_exist_for_render_output(bot_directory)
    given_standard_workflow_states(bot_directory)


def when_validate_rules_action_executes(bot_directory: Path, behavior: str = 'shape'):
    """When: validate_rules action executes."""
    from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
    action = ValidateRulesAction(
        bot_name='story_bot',
        behavior=behavior,
        bot_directory=bot_directory
    )
    result = action.execute(parameters={})
    return action, result


def then_base_instructions_include_next_behavior_reminder(result):
    """Then: base_instructions include next behavior reminder."""
    instructions = result['instructions']
    base_instructions_list = instructions['base_instructions']
    
    reminder_found = False
    next_behavior_found = False
    for i, instruction in enumerate(base_instructions_list):
        if 'NEXT BEHAVIOR REMINDER' in instruction:
            reminder_found = True
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
    return base_instructions_list


def then_reminder_contains_prompt_text(base_instructions_list):
    """Then: Reminder contains prompt text."""
    instructions_text = ' '.join(base_instructions_list)
    assert 'next behavior in sequence' in instructions_text.lower(), (
        "Reminder should contain 'next behavior in sequence' text"
    )
    assert 'would you like to continue' in instructions_text.lower() or 'work on a different behavior' in instructions_text.lower(), (
        "Reminder should contain prompt asking user if they want to continue"
    )


def given_base_action_instructions_exist_for_validate_rules_not_final(bot_directory: Path):
    """Given: Base action instructions exist for validate_rules (not final)."""
    bot_base_actions_dir = bot_directory / 'base_actions'
    bot_base_actions_dir.mkdir(parents=True, exist_ok=True)
    
    validate_rules_dir = bot_base_actions_dir / '4_validate_rules'
    validate_rules_dir.mkdir(parents=True, exist_ok=True)
    
    base_instructions = {
        'instructions': [
            'Validate story graph against rules',
            'Generate validation report'
        ]
    }
    instructions_file = validate_rules_dir / 'instructions.json'
    instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
    return validate_rules_dir


def given_action_configs_exist_for_workflow_actions_with_render_output_after(bot_directory: Path):
    """Given: action_config.json files for workflow actions with render_output after validate_rules."""
    bot_base_actions_dir = bot_directory / 'base_actions'
    workflow_actions = [
        ('1_gather_context', 'gather_context', 1),
        ('2_decide_planning_criteria', 'decide_planning_criteria', 2),
        ('3_build_knowledge', 'build_knowledge', 3),
        ('4_validate_rules', 'validate_rules', 4),
        ('5_render_output', 'render_output', 5)
    ]
    for folder_name, action_name, order in workflow_actions:
        action_dir = bot_base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        action_config = {
            'name': action_name,
            'workflow': True,
            'order': order
        }
        action_config_file = action_dir / 'action_config.json'
        action_config_file.write_text(json.dumps(action_config), encoding='utf-8')


def then_base_instructions_do_not_include_next_behavior_reminder(result):
    """Then: base_instructions do NOT include next behavior reminder."""
    instructions = result.get('instructions', {})
    base_instructions_list = instructions.get('base_instructions', [])
    
    instructions_text = ' '.join(base_instructions_list)
    assert 'NEXT BEHAVIOR REMINDER' not in instructions_text, (
        "base_instructions should NOT include 'NEXT BEHAVIOR REMINDER' when action is not final"
    )


def given_base_action_instructions_exist_for_render_output(bot_directory: Path):
    """Given: Base action instructions exist for render_output."""
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
    return render_output_dir


def when_render_output_action_executes(bot_directory: Path, behavior: str = 'discovery'):
    """When: render_output action executes."""
    from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
    action = RenderOutputAction(
        bot_name='story_bot',
        behavior=behavior,
        bot_directory=bot_directory
    )
    result = action.execute(parameters={})
    return action, result

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
        given_environment_setup_for_final_action_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'arrange', 'discovery'])
        
        action, result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        base_instructions_list = then_base_instructions_include_next_behavior_reminder(result)
        then_reminder_contains_prompt_text(base_instructions_list)

    def test_next_behavior_reminder_not_injected_when_not_final_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when action is not final
        GIVEN: validate_rules is NOT the final action (render_output comes after)
        AND: bot_config.json defines behavior sequence
        WHEN: validate_rules action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        given_environment_setup_for_non_final_action_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'arrange'])
        
        action, result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        then_base_instructions_do_not_include_next_behavior_reminder(result)

    def test_next_behavior_reminder_not_injected_when_no_next_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
        GIVEN: discovery is the last behavior in bot_config.json
        AND: render_output is the final action
        WHEN: render_output action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        given_environment_setup_for_last_behavior_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'discovery'])
        
        action, result = when_render_output_action_executes(bot_directory, 'discovery')
        
        then_base_instructions_do_not_include_next_behavior_reminder(result)

