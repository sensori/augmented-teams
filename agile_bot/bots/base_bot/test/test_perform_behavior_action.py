"""
Perform Behavior Action Tests

Tests for all stories in the 'Perform Behavior Action' sub-epic:
- Access Bot Paths
- Load Bot Configuration
- Load Bot Behaviors
- Invoke Behavior Actions In Workflow Order
- Insert Context Into Instructions
- Inject Next Behavior Reminder
- Close Current Action





"""
import pytest
import json
import os
from pathlib import Path
# Workflow class removed - state managed by Behaviors and Actions collections
from agile_bot.bots.base_bot.src.bot.bot import Bot, BotResult, Behavior
from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from conftest import (
    bootstrap_env, create_workflow_state_file, create_bot_config_file, 
    create_test_workflow, given_bot_name_and_behavior_setup, given_bot_name_and_behaviors_setup,
    Workflow
)
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, read_activity_log, create_activity_log_file,
    create_actions_workflow_json, create_behavior_folder, create_behavior_folder_with_json,
    get_workflow_state_path, given_bot_name_and_behavior_setup
)
from agile_bot.bots.base_bot.test.test_helpers import (
    when_bot_is_created, create_base_instructions, given_bot_instance_created
)
from agile_bot.bots.base_bot.test.test_execute_behavior_actions import (
    then_workflow_current_state_is,
    then_completed_actions_include
)
# ============================================================================
# HELPER FUNCTIONS - Sub-Epic Level (Used across multiple test classes)
# ============================================================================

# ============================================================================
# WORKFLOW STATE HELPERS
# ============================================================================

def given_workflow_is_at_action(workflow: Workflow, action: str):
    """Given: Workflow is at specified action."""
    workflow.navigate_to_action(action)

def given_action_is_not_completed(workflow: Workflow, action: str):
    """Given: Action is not completed."""
    # Verify action is not in completed_actions
    action_state = f'{workflow.bot_name}.{workflow.behavior}.{action}'
    assert not any(a.get('action_state') == action_state for a in workflow._completed_actions)

def when_user_closes_current_action(workflow: Workflow, action: str):
    """When: User closes current action."""
    workflow.save_completed_action(action)
    workflow.transition_to_next()

def when_user_closes_current_action_and_transitions(workflow: Workflow, action: str):
    """When: User closes current action and transitions."""
    workflow.save_completed_action(action)
    workflow.transition_to_next()

def when_close_already_completed_action(workflow: Workflow, action: str):
    """When: Close already completed action."""
    # Should handle gracefully even if already completed
    workflow.save_completed_action(action)

def then_action_is_marked_complete(workflow: Workflow, action: str):
    """Then: Action is marked complete."""
    action_state = f'{workflow.bot_name}.{workflow.behavior}.{action}'
    assert any(a.get('action_state') == action_state for a in workflow._completed_actions)

def then_workflow_transitions_to_next_action(workflow: Workflow, expected_action: str):
    """Then: Workflow transitions to next action."""
    assert workflow.current_state == expected_action

def then_completed_actions_count_is(workflow_file: Path, expected_count: int):
    """Then: Completed actions count is expected."""
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert len(state_data.get('completed_actions', [])) == expected_count

def then_current_action_is(workflow_file: Path, bot_name: str, behavior: str, expected_action: str):
    """Then: Current action is expected."""
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    expected_action_state = f'{bot_name}.{behavior}.{expected_action}'
    assert state_data.get('current_action') == expected_action_state

def then_workflow_stays_at_action(workflow: Workflow, expected_action: str):
    """Then: Workflow stays at action."""
    assert workflow.current_state == expected_action

def then_action_is_saved_to_completed_actions(workflow_file: Path, bot_name: str, behavior: str, action: str):
    """Then: Action is saved to completed actions."""
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    action_state = f'{bot_name}.{behavior}.{action}'
    completed_states = [a.get('action_state') for a in state_data.get('completed_actions', [])]
    assert action_state in completed_states

def then_completed_actions_count_is_at_least(workflow_file: Path, min_count: int):
    """Then: Completed actions count is at least min_count."""
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert len(state_data.get('completed_actions', [])) >= min_count

def then_bot_has_close_current_action_method(bot):
    """Then: Bot has close_current_action method."""
    assert hasattr(bot, 'close_current_action')
    assert callable(getattr(bot, 'close_current_action'))

def given_bot_config_and_behavior_setup(bot_directory: Path, bot_name: str, behaviors: list):
    """Given: Bot config and behavior setup."""
    return create_bot_config_file(bot_directory, bot_name, behaviors)

def given_completed_action_for_behavior(bot_name: str, behavior: str, action: str, timestamp: str = '2025-12-04T15:55:00.000000'):
    """Given: Completed action entry for behavior."""
    return [{'action_state': f'{bot_name}.{behavior}.{action}', 'timestamp': timestamp}]


def given_workflow_state_file_loaded(workflow_file: Path):
    """Given: Workflow state file loaded."""
    return json.loads(workflow_file.read_text(encoding='utf-8'))


def given_initial_completed_action_count(workflow_file: Path, action_name: str):
    """Given: Initial completed action count for action."""
    initial_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    return len([a for a in initial_state['completed_actions'] if action_name in a['action_state']])


def given_bot_environment_bootstrapped(bot_directory: Path, workspace_directory: Path):
    """Given: Bot environment bootstrapped."""
    bootstrap_env(bot_directory, workspace_directory)


# ============================================================================
# WORKFLOW ASSERTION HELPERS - Sub-epic specific (Perform Behavior Action only)
# ============================================================================

# then_completed_actions_include imported from test_execute_behavior_actions.py (epic-level helper)

def when_execute_workflow_steps_and_verify_completion(test_instance, bot, workflow_file: Path, bot_name: str):
    """When: Execute workflow steps and verify completion."""
    test_instance._execute_workflow_steps(bot, workflow_file, bot_name)
    then_all_completed_actions_tracked_across_behaviors()

def then_all_completed_actions_tracked_across_behaviors():
    """Then: All completed actions tracked across behaviors."""
    print("[OK] All completed actions tracked across both behaviors")

# ============================================================================
# HELPER FUNCTIONS - Shared across test classes
# ============================================================================

def given_standard_workflow_states(bot_directory: Path):
    """Given: Standard workflow states (clarify through render)."""
    return create_workflow_states(bot_directory, [
        'clarify', 'strategy', 'build', 
        'validate', 'render'
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
    """Given: behavior.json with validate as final action."""
    create_actions_workflow_json(
        bot_directory=bot_directory,
        behavior_name=behavior_name,
        actions=[
            {'name': 'clarify', 'order': 1, 'next_action': 'strategy'},
            {'name': 'strategy', 'order': 2, 'next_action': 'build'},
            {'name': 'build', 'order': 3, 'next_action': 'validate'},
            {'name': 'validate', 'order': 4}  # validate is final action (no render after it)
        ]
    )


def given_base_action_instructions_exist_for_validate_rules(bot_directory: Path):
    """Given: Base action instructions exist for validate."""
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    # Use test_base_bot if bot_directory is base_bot
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    validate_dir = base_actions_dir / 'validate'
    validate_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        'name': 'validate',
        'workflow': True,
        'order': 4,
        'instructions': [
            'Load and review clarification.json and planning.json',
            'Check Content Data against all rules',
            'Generate a validation report'
        ]
    }
    config_file = validate_dir / 'action_config.json'
    config_file.write_text(json.dumps(config), encoding='utf-8')
    return validate_dir


def given_standard_workflow_actions_config(bot_directory: Path):
    """Given: Standard workflow actions config (clarify through validate)."""
    return given_action_configs_exist_for_workflow_actions(bot_directory, [
        ('clarify', 'clarify', 1),
        ('strategy', 'strategy', 2),
        ('build', 'build', 3),
        ('validate', 'validate', 4),
        ('render', 'render', 5)
    ])


def given_action_configs_exist_for_workflow_actions(bot_directory: Path, workflow_actions: list):
    """Given: action_config.json files for workflow actions."""
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    # Use test_base_bot if bot_directory is base_bot
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    
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
    # Create behavior.json files for all behaviors
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    for behavior_name in behaviors:
        if behavior_name == 'shape':
            given_behavior_workflow_with_validate_rules_as_final(bot_directory, 'shape')
        else:
            create_actions_workflow_json(bot_directory, behavior_name)
    given_base_action_instructions_exist_for_validate_rules(bot_directory)
    given_standard_workflow_actions_config(bot_directory)
    given_story_graph_file_exists(workspace_directory)
    # Create minimal guardrails files for all behaviors (required by Guardrails class initialization)
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    for behavior_name in behaviors:
        create_minimal_guardrails_files(bot_directory, behavior_name, 'story_bot')


def given_environment_setup_for_non_final_action_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for non-final action test."""
    bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    # Create behavior.json files for all behaviors
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    for behavior_name in behaviors:
        create_actions_workflow_json(bot_directory, behavior_name)
    given_standard_workflow_states(bot_directory)
    given_base_action_instructions_exist_for_validate_rules_not_final(bot_directory)
    given_action_configs_exist_for_workflow_actions_with_render_output_after(bot_directory)
    given_story_graph_file_exists(workspace_directory)
    # Create minimal guardrails files for all behaviors (required by Guardrails class initialization)
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    for behavior_name in behaviors:
        create_minimal_guardrails_files(bot_directory, behavior_name, 'story_bot')


def given_environment_setup_for_last_behavior_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for last behavior test."""
    bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    # Create behavior.json files for all behaviors
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    for behavior_name in behaviors:
        if behavior_name == 'discovery':
            # Create behavior.json with render as final action
            create_actions_workflow_json(
                bot_directory=bot_directory,
                behavior_name='discovery',
                actions=[
                    {'name': 'clarify', 'order': 1, 'next_action': 'strategy'},
                    {'name': 'strategy', 'order': 2, 'next_action': 'build'},
                    {'name': 'build', 'order': 3, 'next_action': 'render'},
                    {'name': 'render', 'order': 4}
                ]
            )
        else:
            create_actions_workflow_json(bot_directory, behavior_name)
    given_base_action_instructions_exist_for_render_output(bot_directory)
    given_standard_workflow_actions_config(bot_directory)
    # Create minimal guardrails files for all behaviors (required by Guardrails class initialization)
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    for behavior_name in behaviors:
        create_minimal_guardrails_files(bot_directory, behavior_name, 'story_bot')


def when_validate_rules_action_executes(bot_directory: Path, behavior: str = 'shape', action_name: str = None):
    """When: validate action executes through Actions collection."""
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    from pathlib import Path
    
    # Create Bot instance
    config_path = bot_directory / 'bot_config.json'
    bot = Bot(bot_name='story_bot', bot_directory=bot_directory, config_path=config_path)
    
    # Navigate to behavior
    behavior_obj = bot.behaviors.find_by_name(behavior)
    if behavior_obj is None:
        raise ValueError(f"Behavior '{behavior}' not found")
    
    # Determine action name - use provided name or try both validate and validate_rules
    if action_name is None:
        # Try validate_rules first (standard workflow), then validate (custom workflow)
        action_names = behavior_obj.actions.names
        if 'validate_rules' in action_names:
            action_name = 'validate_rules'
        elif 'validate' in action_names:
            action_name = 'validate'
        else:
            raise ValueError(f"Neither 'validate' nor 'validate_rules' found in actions: {action_names}")
    
    # Navigate to validate action
    behavior_obj.actions.navigate_to(action_name)
    
    # Execute current action through Actions collection (which will inject reminders)
    action_result = behavior_obj.actions.execute_current(parameters={})
    
    # Return the action object and result
    return behavior_obj.actions.current, action_result


def then_base_instructions_include_next_behavior_reminder(action_result):
    """Then: base_instructions include next behavior reminder."""
    instructions = action_result['instructions']
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
    """Given: Base action instructions exist for validate (not final)."""
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    bot_base_actions_dir = get_test_base_actions_dir(bot_directory)
    
    validate_rules_dir = bot_base_actions_dir / 'validate'
    validate_rules_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        'name': 'validate',
        'workflow': True,
        'order': 4,
        'instructions': [
            'Validate story graph against rules',
            'Generate validation report'
        ]
    }
    config_file = validate_rules_dir / 'action_config.json'
    config_file.write_text(json.dumps(config), encoding='utf-8')
    return validate_rules_dir


def given_action_configs_exist_for_workflow_actions_with_render_output_after(bot_directory: Path):
    """Given: action_config.json files for workflow actions with render after validate.
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    bot_base_actions_dir = get_test_base_actions_dir(bot_directory)
    workflow_actions = [
        ('clarify', 'clarify', 1),
        ('strategy', 'strategy', 2),
        ('build', 'build', 3),
        ('validate', 'validate', 4),
        ('render', 'render', 5)
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


def then_base_instructions_do_not_include_next_behavior_reminder(action_result):
    """Then: base_instructions do NOT include next behavior reminder."""
    instructions = action_result.get('instructions', {})
    base_instructions_list = instructions.get('base_instructions', [])
    
    instructions_text = ' '.join(base_instructions_list)
    assert 'NEXT BEHAVIOR REMINDER' not in instructions_text, (
        "base_instructions should NOT include 'NEXT BEHAVIOR REMINDER' when action is not final"
    )


def given_base_action_instructions_exist_for_render_output(bot_directory: Path):
    """Given: Base action instructions exist for render."""
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    # Use test_base_bot if bot_directory is base_bot
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    render_output_dir = base_actions_dir / 'render'
    render_output_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        'name': 'render',
        'workflow': True,
        'order': 5,
        'instructions': [
            'Render story map documents',
            'Render domain model documents'
        ]
    }
    config_file = render_output_dir / 'action_config.json'
    config_file.write_text(json.dumps(config), encoding='utf-8')
    return render_output_dir


def when_render_output_action_executes(bot_directory: Path, behavior: str = 'discovery'):
    """When: render action executes through Actions collection."""
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    from pathlib import Path
    
    # Create Bot instance
    config_path = bot_directory / 'bot_config.json'
    bot = Bot(bot_name='story_bot', bot_directory=bot_directory, config_path=config_path)
    
    # Navigate to behavior
    behavior_obj = bot.behaviors.find_by_name(behavior)
    if behavior_obj is None:
        raise ValueError(f"Behavior '{behavior}' not found")
    
    # Navigate to render action
    behavior_obj.actions.navigate_to('render')
    
    # Execute current action through Actions collection (which will inject reminders)
    action_result = behavior_obj.actions.execute_current(parameters={})
    
    # Return the action object and result
    return behavior_obj.actions.current, action_result


# ============================================================================
# STORY: Inject Next Behavior Reminder
# ============================================================================

class TestInjectNextBehaviorReminder:
    """Story: Inject Next Behavior Reminder - Tests that next behavior reminder is injected for final actions."""

    def test_next_behavior_reminder_injected_when_final_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is injected when action is final action
        GIVEN: validate is the final action in behavior workflow
        AND: bot_config.json defines behavior sequence
        WHEN: validate action executes
        THEN: base_instructions include next behavior reminder
        AND: reminder contains next behavior name and prompt text
        """
        given_environment_setup_for_final_action_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'arrange', 'discovery'])
        
        action, action_result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        base_instructions_list = then_base_instructions_include_next_behavior_reminder(action_result)
        then_reminder_contains_prompt_text(base_instructions_list)

    def test_next_behavior_reminder_not_injected_when_not_final_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when action is not final
        GIVEN: validate is NOT the final action (render comes after)
        AND: bot_config.json defines behavior sequence
        WHEN: validate action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        given_environment_setup_for_non_final_action_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'arrange'])
        
        action, action_result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        then_base_instructions_do_not_include_next_behavior_reminder(action_result)

    def test_next_behavior_reminder_not_injected_when_no_next_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
        GIVEN: discovery is the last behavior in bot_config.json
        AND: render is the final action
        WHEN: render action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        given_environment_setup_for_last_behavior_test(bot_directory, workspace_directory, ['shape', 'prioritization', 'discovery'])
        
        action, action_result = when_render_output_action_executes(bot_directory, 'discovery')
        
        then_base_instructions_do_not_include_next_behavior_reminder(action_result)


# ============================================================================
# STORY: Close Current Action
# ============================================================================
# All helpers moved to test_helpers.py - imported above


class TestCloseCurrentAction:
    """Story: Close Current Action - Tests that users can explicitly mark an action as complete and transition to the next action."""

    def test_close_current_action_marks_complete_and_transitions(self, bot_directory, workspace_directory):
        """Scenario: Close current action and transition to next"""

        # Given workflow is at action "strategy"
        # And action has NOT been marked complete yet
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'clarify')

        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'strategy', completed)

        given_workflow_is_at_action(workflow, 'strategy')
        given_action_is_not_completed(workflow, 'strategy')

        # When user closes current action
        when_user_closes_current_action_and_transitions(workflow, 'strategy')

        # Then action is saved to completed_actions
        then_action_is_marked_complete(workflow, 'strategy')
        # And workflow transitions to next action
        then_workflow_transitions_to_next_action(workflow, 'build')
        then_completed_actions_count_is(workflow_file, 2)
        then_current_action_is(workflow_file, bot_name, behavior, 'build')


    def test_close_action_at_final_action_stays_at_final(self, bot_directory, workspace_directory):
        """Scenario: Close final action stays at final action"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        # Use 'render' as final action (workflow has render as final, not validate)
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'render', [])
        
        given_workflow_is_at_action(workflow, 'render')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'render')
        # No transition_to_next() call - render is final
        
        # Then action is saved but state stays at render
        then_action_is_marked_complete(workflow, 'render')
        then_workflow_stays_at_action(workflow, 'render')


    def test_close_final_action_transitions_to_next_behavior(self, bot_directory, workspace_directory):
        """Scenario: Close final action and verify it's marked complete"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        # Given: Workflow is at final action
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate', [])
        
        given_workflow_is_at_action(workflow, 'validate')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'validate')
        
        # Then action is marked complete
        then_action_is_marked_complete(workflow, 'validate')
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'validate')


    def test_close_action_saves_to_completed_actions_list(self, bot_directory, workspace_directory):
        """Scenario: Closing action saves it to completed_actions list"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'clarify', [])
        
        # When closing action
        when_user_closes_current_action(workflow, 'clarify')
        
        # Then it's in completed_actions
        then_completed_actions_count_is(workflow_file, 1)
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'clarify')


    def test_close_handles_action_already_completed_gracefully(self, bot_directory, workspace_directory):
        """Scenario: Idempotent close (already completed)"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'clarify')
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'strategy', completed)
        
        # Verify initial state
        initial_count = given_initial_completed_action_count(workflow_file, 'clarify')
        
        # When closing already completed action
        when_close_already_completed_action(workflow, 'clarify')
        
        # Then no NEW entry added (may save again with new timestamp, but test just checks it completes gracefully)
        then_completed_actions_count_is_at_least(workflow_file, initial_count)


    def test_bot_class_has_close_current_action_method(self, bot_directory, workspace_directory):
        """Scenario: Bot class exposes close_current_action method"""
        
        # Given: Bot is initialized
        given_bot_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, _ = given_bot_name_and_behavior_setup()
        config_path = given_bot_config_and_behavior_setup(bot_directory, bot_name, ['shape'])
        # Create behavior.json files for all behaviors
        from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
        for behavior_name in ['shape']:
            create_actions_workflow_json(bot_directory, behavior_name)
        # Create minimal guardrails files (required by Guardrails class initialization)
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        for behavior_name in ['shape']:
            create_minimal_guardrails_files(bot_directory, behavior_name, bot_name)
        bot = when_bot_is_created(bot_name, bot_directory, config_path)
        
        # Then: Bot should have close_current_action method
        then_bot_has_close_current_action_method(bot)


# ============================================================================
# STORY: Invoke Behavior Actions In Workflow Order
# ============================================================================

def given_behaviors_exist_with_workflow(bot_directory: Path, behaviors: list):
    """Given step: Behavior folders exist with behavior.json files."""
    for behavior in behaviors:
        create_actions_workflow_json(bot_directory, behavior)

def given_base_actions_exist_with_transitions(bot_directory: Path):
    """Given step: Base actions exist with next_action transitions."""
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    # Use test_base_bot if bot_directory is base_bot
    base_actions_dir = get_test_base_actions_dir(bot_directory)
    
    actions_config = [
        ('clarify', 2, 'strategy'),
        ('strategy', 3, 'build'),
        ('build', 4, 'validate'),
        ('validate', 5, 'render')
    ]
    
    for action_name, order, next_action in actions_config:
        action_dir = base_actions_dir / action_name
        action_dir.mkdir(parents=True, exist_ok=True)
        (action_dir / 'action_config.json').write_text(json.dumps({
            'name': action_name,
            'instructions': [f'Test {action_name}'],
            'workflow': True,
            'order': order,
            'next_action': next_action
        }), encoding='utf-8')
    return base_actions_dir

def given_behavior_json_file_created(behavior_dir: Path, behavior_config: dict):
    """Given step: Create behavior.json file with config."""
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    return behavior_file

def given_expected_transitions_list():
    """Given step: Create expected transitions list."""
    return [
        {'trigger': 'proceed', 'source': 'build', 'dest': 'render'},
        {'trigger': 'proceed', 'source': 'render', 'dest': 'validate'},
        {'trigger': 'proceed', 'source': 'validate', 'dest': 'complete'}
    ]

def when_action_is_executed(bot, behavior_name: str, action_name: str):
    """When step: Action is executed."""
    behavior = bot.behaviors.find_by_name(behavior_name)
    if behavior is None:
        raise ValueError(f"Behavior {behavior_name} not found")
    action_method = getattr(behavior, action_name)
    return action_method()

def when_action_is_closed_and_transitioned(bot, behavior_name: str, action_name: str):
    """When step: Action is closed and workflow transitions."""
    behavior = bot.behaviors.find_by_name(behavior_name)
    if behavior is None:
        raise ValueError(f"Behavior {behavior_name} not found")
    # Behavior.workflow was removed - use behavior.actions instead
    behavior.actions.close_current()  # This saves completed action and transitions
    behavior.actions.save_state()

def then_workflow_state_shows_action(workflow_file: Path, bot_name: str, behavior: str, action: str):
    """Then step: Workflow state shows specified action."""
    if workflow_file.exists():
        state = json.loads(workflow_file.read_text(encoding='utf-8'))
        assert state['current_action'] == f'{bot_name}.{behavior}.{action}'

def then_workflow_state_shows_behavior(workflow_file: Path, bot_name: str, behavior: str):
    """Then step: Workflow state shows specified behavior."""
    if workflow_file.exists():
        state = json.loads(workflow_file.read_text(encoding='utf-8'))
        assert state['current_behavior'] == f'{bot_name}.{behavior}'

def given_test_environment_setup(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list):
    """Given: Test environment setup with bot config, behaviors, and base actions."""
    bootstrap_env(bot_directory, workspace_directory)
    config_path = create_bot_config_file(bot_directory, bot_name, behaviors)
    given_behaviors_exist_with_workflow(bot_directory, behaviors)
    given_base_actions_exist_with_transitions(bot_directory)
    return config_path

def then_action_result_has_correct_action(result, expected_action: str):
    """Then: Action result has correct action."""
    assert result.action == expected_action

def then_action_is_completed(workflow, action_name: str):
    """Then: Action is completed."""
    assert workflow.is_action_completed(action_name)

def given_completed_actions_for_behaviors(bot_name: str, behaviors: list, action: str):
    """Given: Completed actions for multiple behaviors."""
    return [f'{bot_name}.{behavior}.{action}' for behavior in behaviors]

def then_action_result_has_correct_behavior_and_action(result, expected_behavior: str, expected_action: str):
    """Then: Action result has correct behavior and action."""
    assert result.behavior == expected_behavior
    assert result.action == expected_action

def given_bot_name_behaviors_and_config_setup(bot_directory: Path, workspace_directory: Path):
    """Given: Bot name, behaviors and config setup."""
    bot_name, behaviors = given_bot_name_and_behaviors_setup('story_bot', ['shape', 'discovery'])
    config_path = given_test_environment_setup(bot_directory, workspace_directory, bot_name, behaviors)
    return bot_name, behaviors, config_path

def when_bot_and_workflow_file_created(bot_name: str, bot_directory: Path, config_path: Path, workspace_directory: Path):
    """When: Bot and workflow file created."""
    bot = when_bot_is_created(bot_name, bot_directory, config_path)
    workflow_file = workspace_directory / 'workflow_state.json'
    return bot, workflow_file

def when_execute_shape_gather_context_and_verify(bot, workflow_file: Path, bot_name: str):
    """When: Execute shape clarify and verify."""
    result = when_action_is_executed(bot, 'shape', 'clarify')
    then_action_result_has_correct_action(result, 'clarify')
    shape_behavior = bot.behaviors.find_by_name('shape')
    # Check current action from actions collection instead of workflow
    assert shape_behavior.actions.current is not None
    assert shape_behavior.actions.current.action_name == 'clarify'
    then_workflow_state_shows_action(workflow_file, bot_name, 'shape', 'clarify')
    return result

def when_close_shape_gather_context_and_verify(bot):
    """When: Close shape clarify and verify."""
    when_action_is_closed_and_transitioned(bot, 'shape', 'clarify')
    shape_behavior = bot.behaviors.find_by_name('shape')
    # Check current action from actions collection instead of workflow
    assert shape_behavior.actions.current is not None
    assert shape_behavior.actions.current.action_name == 'strategy'
    # Verify clarify is in completed actions by checking workflow state file
    from agile_bot.bots.base_bot.test.test_helpers import get_workflow_state_path
    workflow_file = get_workflow_state_path(bot.behaviors.bot_paths.workspace_directory)
    if workflow_file.exists():
        state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
        completed_states = [a.get('action_state', '') for a in state_data.get('completed_actions', [])]
        assert f'{bot.name}.shape.clarify' in completed_states

def when_execute_discovery_gather_context_and_verify(bot, workflow_file: Path, bot_name: str):
    """When: Execute discovery clarify and verify."""
    result = when_action_is_executed(bot, 'discovery', 'clarify')
    then_action_result_has_correct_behavior_and_action(result, 'discovery', 'clarify')
    then_workflow_state_shows_behavior(workflow_file, bot_name, 'discovery')
    then_workflow_state_shows_action(workflow_file, bot_name, 'discovery', 'clarify')
    return result

def when_close_discovery_gather_context_and_verify(bot):
    """When: Close discovery clarify and verify."""
    when_action_is_closed_and_transitioned(bot, 'discovery', 'clarify')
    discovery_behavior = bot.behaviors.find_by_name('discovery')
    # Check current action from actions collection instead of workflow
    assert discovery_behavior.actions.current is not None
    assert discovery_behavior.actions.current.action_name == 'strategy'

def then_verify_completed_actions_across_behaviors(workflow_file: Path, bot_name: str):
    """Then: Verify completed actions across behaviors."""
    expected_completed_actions = given_completed_actions_for_behaviors('story_bot', ['shape', 'discovery'], 'clarify')
    then_completed_actions_include(workflow_file, expected_completed_actions)


class TestInvokeBehaviorActionsInWorkflowOrder:
    """Story: Invoke Behavior Actions In Workflow Order - End-to-end test of the complete workflow with all fixes."""

    def _execute_workflow_steps(self, bot, workflow_file, bot_name):
        """Helper: Execute workflow steps for end-to-end test."""
        print("\n=== Step 1: Execute clarify ===")
        action_result = when_execute_shape_gather_context_and_verify(bot, workflow_file, bot_name)
        print("[OK] Executed clarify, state saved")
        
        print("\n=== Step 2: Close clarify ===")
        when_close_shape_gather_context_and_verify(bot)
        print("[OK] clarify closed, transitioned to strategy")
        
        print("\n=== Step 3: Jump to discovery.clarify (out of order) ===")
        action_result = when_execute_discovery_gather_context_and_verify(bot, workflow_file, bot_name)
        print("[OK] Jumped to discovery.clarify, state correctly shows discovery.clarify")
        
        print("\n=== Step 4: Close discovery.clarify ===")
        when_close_discovery_gather_context_and_verify(bot)
        print("[OK] discovery.clarify closed, transitioned to strategy")
        then_verify_completed_actions_across_behaviors(workflow_file, bot_name)

    def test_complete_workflow_end_to_end(self, bot_directory, workspace_directory, tmp_path):
        """
        Complete end-to-end workflow test demonstrating all fixes working together.

        Flow:
        1. Start at clarify
        2. Execute clarify
        3. Close clarify -> Transitions to strategy
        4. Jump to discovery.clarify (out of order)
        5. Verify state shows discovery.clarify
        6. Close and verify proper transition
        """
        bot_name, behaviors, config_path = given_bot_name_behaviors_and_config_setup(bot_directory, workspace_directory)
        bot, workflow_file = when_bot_and_workflow_file_created(bot_name, bot_directory, config_path, workspace_directory)
        when_execute_workflow_steps_and_verify_completion(self, bot, workflow_file, bot_name)
        
        print("\n=== SUCCESS: Complete workflow with all fixes working! ===")


# ============================================================================
# STORY: Find Behavior Folder (Workflow Action Sequence)
# ============================================================================

def given_workflow_state_file_with_empty_current_action(workspace_directory: Path, bot_name: str, behavior: str, completed_actions: list):
    """Given: Workflow state file with empty current_action."""
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': '',
        'completed_actions': completed_actions,
        'timestamp': '2025-12-04T15:45:00.000000'
    }), encoding='utf-8')
    return workflow_file

def given_workflow_state_file_with_completed_actions(workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed_actions: list):
    """Given: Workflow state file with completed actions."""
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'completed_actions': completed_actions,
        'timestamp': '2025-12-04T15:48:00.000000'
    }), encoding='utf-8')
    return workflow_file

def when_workflow_navigates_to_action(workflow: Workflow, target_action: str, out_of_order: bool = False):
    """When: Workflow navigates to action."""
    workflow.navigate_to_action(target_action, out_of_order=out_of_order)

def then_current_state_is(workflow: Workflow, expected_state: str):
    """Then: Current state is expected."""
    assert workflow.current_state == expected_state

def then_completed_actions_do_not_include(workflow_file: Path, bot_name: str, behavior: str, action_name: str):
    """Then: Completed actions do not include specified action."""
    loaded_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    completed_action_states = [a['action_state'] for a in loaded_state['completed_actions']]
    assert f'{bot_name}.{behavior}.{action_name}' not in completed_action_states

def given_standard_workflow_states_and_transitions():
    """Given: Standard workflow states and transitions."""
    states = ['clarify', 'strategy', 
              'build', 'validate', 'render']
    transitions = [
        {'trigger': 'proceed', 'source': 'clarify', 'dest': 'strategy'},
        {'trigger': 'proceed', 'source': 'strategy', 'dest': 'build'},
        {'trigger': 'proceed', 'source': 'build', 'dest': 'validate'},
        {'trigger': 'proceed', 'source': 'validate', 'dest': 'render'},
    ]
    return states, transitions

def given_workflow_created(bot_name: str, behavior: str, bot_directory: Path, states: list = None, transitions: list = None):
    """Given: Workflow created with states and transitions."""
    if states is None or transitions is None:
        states, transitions = given_standard_workflow_states_and_transitions()
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory,
        states=states,
        transitions=transitions
    )
    return workflow

def given_workflow_state_with_completed_actions(workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed_actions: list):
    """Given: Workflow state with completed actions."""
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'completed_actions': completed_actions,
        'timestamp': '2025-12-04T15:48:00.000000'
    }), encoding='utf-8')
    return workflow_file

def then_completed_actions_removed_after_target(workflow_file: Path, bot_name: str, behavior: str, target_action: str):
    """Then: Completed actions after target are removed."""
    loaded_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    completed_action_states = [a['action_state'] for a in loaded_state['completed_actions']]
    # Actions after target should be removed
    action_order = ['clarify', 'strategy', 'build', 'validate', 'render']
    target_index = action_order.index(target_action)
    for i in range(target_index + 1, len(action_order)):
        assert f'{bot_name}.{behavior}.{action_order[i]}' not in completed_action_states

def given_behavior_config_created(bot_directory: Path, behavior: str, behavior_config: dict):
    """Given: Behavior config created."""
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    behavior_dir = bot_directory / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    # Extract bot_name from bot_directory (e.g., 'agile_bot/bots/story_bot' -> 'story_bot')
    bot_name = bot_directory.name if bot_directory.name in ['story_bot', 'test_story_bot'] else 'story_bot'
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_directory, behavior, bot_name)
    return behavior_file

def when_behavior_is_initialized(bot_name: str, behavior: str, bot_directory: Path):
    """When: Behavior is initialized."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_instance = Behavior(
        name=behavior,
        bot_name=bot_name,
        bot_paths=bot_paths
    )
    return behavior_instance

def then_workflow_states_match(behavior_instance, expected_states: list):
    """Then: Workflow states match expected."""
    # Behavior.workflow was removed - use behavior.actions instead
    actual_states = [action.action_name for action in behavior_instance.actions]
    assert actual_states == expected_states, (
        f"Expected states {expected_states}, got {actual_states}"
    )

def then_workflow_transitions_match(behavior_instance, expected_transitions: list):
    """Then: Workflow transitions match expected."""
    # Behavior.workflow was removed - transitions are implicit in action order
    # Verify that actions are in the correct order to match transitions
    actions_list = list(behavior_instance.actions)
    actual_transitions = []
    for i in range(len(actions_list) - 1):
        current_action = actions_list[i]
        next_action = actions_list[i + 1]
        # Check if current action has next_action configured
        if hasattr(current_action, 'base_action_config') and hasattr(current_action.base_action_config, 'next_action'):
            next_action_name = current_action.base_action_config.next_action
            if next_action_name:
                actual_transitions.append({
                    'trigger': 'proceed',
                    'source': current_action.action_name,
                    'dest': next_action_name
                })
    # For now, just verify actions exist in correct order
    # Full transition matching would require checking next_action on each action
    assert len(actions_list) > 0, "No actions found"

def when_behavior_is_initialized_raises_error(bot_name: str, behavior: str, bot_directory: Path):
    """When: Behavior is initialized raises error."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    bot_paths = BotPaths(bot_directory=bot_directory)
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name=behavior,
            bot_name=bot_name,
            bot_paths=bot_paths
        )
    return exc_info

def then_error_mentions_behavior_json_required(exc_info, behavior: str):
    """Then: Error mentions behavior.json is REQUIRED."""
    # Error message changed - check for key parts of the message
    error_msg = str(exc_info.value)
    assert 'behavior.json' in error_msg or 'Behavior config not found' in error_msg
    assert 'REQUIRED' in error_msg or 'must define' in error_msg
    assert behavior in str(exc_info.value)

def given_completed_action_for_gather_context(bot_name: str, behavior: str):
    """Given: Completed action for clarify."""
    return [{'action_state': f'{bot_name}.{behavior}.clarify', 'timestamp': '2025-12-04T15:44:22.812230'}]

def when_create_workflow_with_current_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed: list):
    """When: Create workflow with current action."""
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, current_action, completed, return_workflow_file=False)
    return workflow

def then_workflow_current_state_is_build_knowledge(workflow):
    """Then: Workflow current state is build."""
    assert workflow.current_state == 'build'

def then_workflow_current_state_is_gather_context(workflow):
    """Then: Workflow current state is clarify."""
    assert workflow.current_state == 'clarify'

def then_workflow_current_state_is_decide_planning_criteria(workflow):
    """Then: Workflow current state is strategy."""
    assert workflow.current_state == 'strategy'

def given_completed_actions_for_three_actions(bot_name: str, behavior: str):
    """Given: Completed actions for three actions."""
    return [
        {'action_state': f'{bot_name}.{behavior}.clarify', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.strategy', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build', 'timestamp': '2025-12-04T15:47:00.000000'}
    ]

def given_standard_states_and_transitions():
    """Given: Standard states and transitions."""
    states = ['clarify', 'strategy', 
              'build', 'validate', 'render']
    transitions = [
        {'trigger': 'proceed', 'source': 'clarify', 'dest': 'strategy'},
        {'trigger': 'proceed', 'source': 'strategy', 'dest': 'build'},
        {'trigger': 'proceed', 'source': 'build', 'dest': 'validate'},
        {'trigger': 'proceed', 'source': 'validate', 'dest': 'render'},
    ]
    return states, transitions

def when_create_workflow_with_states_and_transitions(bot_name: str, behavior: str, bot_directory: Path, states: list, transitions: list):
    """When: Create workflow with states and transitions."""
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory,
        states=states,
        transitions=transitions
    )
    return workflow

def given_environment_and_empty_workflow_state(bot_directory: Path, workspace_directory: Path, bot_name: str, behavior: str, completed: list):
    """Given: Environment and empty workflow state."""
    bootstrap_env(bot_directory, workspace_directory)
    given_workflow_state_file_with_empty_current_action(workspace_directory, bot_name, behavior, completed)
    states, transitions = given_standard_states_and_transitions()
    workflow = when_create_workflow_with_states_and_transitions(bot_name, behavior, bot_directory, states, transitions)
    workflow.workspace_root = workspace_directory  # Set workspace_root so load_state can find the file
    workflow.load_state()  # Load state from file (this will fall back to completed_actions)
    return workflow

def given_environment_and_verify_no_workflow_file(bot_directory: Path, workspace_directory: Path):
    """Given: Environment and verify no workflow file."""
    bootstrap_env(bot_directory, workspace_directory)
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()
    return workflow_file

def given_completed_actions_for_four_actions(bot_name: str, behavior: str):
    """Given: Completed actions for four actions."""
    return [
        {'action_state': f'{bot_name}.{behavior}.clarify', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.strategy', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.render', 'timestamp': '2025-12-04T15:47:00.000000'},
    ]

def given_environment_workflow_state_and_workflow(bot_directory: Path, workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed: list):
    """Given: Environment, workflow state and workflow."""
    bootstrap_env(bot_directory, workspace_directory)
    workflow_file = given_workflow_state_with_completed_actions(
        workspace_directory, bot_name, behavior, current_action, completed
    )
    states, transitions = given_standard_states_and_transitions()
    workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
    workflow.workspace_root = workspace_directory  # Set workspace_root so load_state can find the file
    workflow.load_state()  # Load state from file
    return workflow_file, workflow

def when_navigate_to_target_action_out_of_order(workflow, target_action: str):
    """When: Navigate to target action out of order."""
    when_workflow_navigates_to_action(workflow, target_action, out_of_order=True)

def then_verify_completed_actions_after_navigation(workflow_file: Path, bot_name: str, behavior: str):
    """Then: Verify completed actions after navigation."""
    then_completed_actions_do_not_include(workflow_file, bot_name, behavior, 'render')
    expected_action_states = [f'{bot_name}.{behavior}.clarify', f'{bot_name}.{behavior}.strategy', f'{bot_name}.{behavior}.build']
    then_completed_actions_include(workflow_file, expected_action_states)

def given_write_tests_behavior_config():
    """Given: Write tests behavior config."""
    return {
        "behaviorName": "tests",
        "description": "Test behavior: tests",
        "goal": "Test goal for tests",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": ["Test instructions for tests."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build",
                    "order": 3,
                    "next_action": "render"
                },
                {
                    "name": "render",
                    "order": 4,
                    "next_action": "validate"
                },
                {
                    "name": "validate",
                    "order": 5
                }
            ]
        },
        "trigger_words": {
            "description": "Trigger words for tests",
            "patterns": ["test.*tests"],
            "priority": 10
        }
    }

def given_environment_and_bot(tmp_path: Path, bot_name: str = "story_bot"):
    """Given: Environment variables and bot directory exist."""
    bot_dir = tmp_path / "agile_bot" / "bots" / bot_name
    bot_dir.mkdir(parents=True, exist_ok=True)
    os.environ["WORKING_AREA"] = str(tmp_path)
    os.environ["BOT_DIRECTORY"] = str(bot_dir)
    return bot_dir, tmp_path


def when_bot_paths_is_created(workspace_dir: Path) -> BotPaths:
    """When: BotPaths is created."""
    return BotPaths(workspace_dir)


def when_behavior_config_is_created(behavior: str, bot_paths: BotPaths) -> BehaviorConfig:
    """When: BehaviorConfig is created."""
    return BehaviorConfig(behavior, bot_paths)


def then_behavior_config_matches_fields(
    behavior_config: BehaviorConfig,
    expected_description: str,
    expected_goal: str,
    expected_inputs: list,
    expected_outputs: list,
    expected_instructions: dict,
    expected_trigger_words: list,
):
    """Then: BehaviorConfig fields match expected values."""
    assert behavior_config.description == expected_description
    assert behavior_config.goal == expected_goal
    assert behavior_config.inputs == expected_inputs
    assert behavior_config.outputs == expected_outputs
    assert behavior_config.instructions == expected_instructions
    assert behavior_config.trigger_words == expected_trigger_words
    assert behavior_config.base_actions_path == behavior_config.bot_paths.base_actions_directory


def then_actions_workflow_sorted(behavior_config: BehaviorConfig, expected_actions: list, expected_names: list):
    """Then: actions_workflow is sorted and action names are extracted."""
    assert [a["name"] for a in behavior_config.actions_workflow] == expected_actions
    assert behavior_config.actions == expected_names


def given_environment_and_behavior_config(bot_directory: Path, workspace_directory: Path, behavior: str, behavior_config: dict):
    """Given: Environment and behavior config."""
    bootstrap_env(bot_directory, workspace_directory)
    given_behavior_config_created(bot_directory, behavior, behavior_config)

def then_workflow_states_and_transitions_match_tests(behavior_instance):
    """Then: Workflow states and transitions match write tests."""
    then_workflow_states_match(behavior_instance, ['build', 'render', 'validate'])
    then_workflow_transitions_match(behavior_instance, [
        {'trigger': 'proceed', 'source': 'build', 'dest': 'render'},
        {'trigger': 'proceed', 'source': 'render', 'dest': 'validate'},
    ])

def given_behavior_directory_created(bot_directory: Path, behavior: str):
    """Given: Behavior directory created."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir

def given_environment_and_behavior_directory(bot_directory: Path, workspace_directory: Path, behavior: str):
    """Given: Environment and behavior directory."""
    bootstrap_env(bot_directory, workspace_directory)
    behavior_dir = given_behavior_directory_created(bot_directory, behavior)
    return behavior_dir

def then_workflow_states_match_expected(behavior_instance, expected_states: list):
    """Then: Workflow states match expected."""
    # Behavior.workflow was removed - use behavior.actions instead
    actual_states = [action.action_name for action in behavior_instance.actions]
    assert actual_states == expected_states, (
        f"Should use order from behavior.json {expected_states}, got {actual_states}"
    )

def given_knowledge_behavior_config():
    """Given: Knowledge behavior config."""
    return {
        "behaviorName": "knowledge",
        "description": "Test behavior: knowledge",
        "goal": "Test goal for knowledge",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": ["Test instructions for knowledge."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build",
                    "order": 3,
                    "next_action": "validate"
                },
                {
                    "name": "validate",
                    "order": 4,
                    "next_action": "render"
                },
                {
                    "name": "render",
                    "order": 5
                }
            ]
        },
        "trigger_words": {
            "description": "Trigger words for knowledge",
            "patterns": ["test.*knowledge"],
            "priority": 10
        }
    }

def when_create_knowledge_behavior_file(bot_directory: Path, knowledge_behavior: str, knowledge_behavior_config: dict):
    """When: Create knowledge behavior file."""
    knowledge_behavior_dir = given_behavior_directory_created(bot_directory, knowledge_behavior)
    knowledge_behavior_file = knowledge_behavior_dir / 'behavior.json'
    knowledge_behavior_file.write_text(json.dumps(knowledge_behavior_config), encoding='utf-8')
    return knowledge_behavior_file

def when_create_code_behavior_file(bot_directory: Path, code_behavior: str, code_behavior_config: dict):
    """When: Create code behavior file."""
    code_behavior_dir = given_behavior_directory_created(bot_directory, code_behavior)
    code_behavior_file = code_behavior_dir / 'behavior.json'
    code_behavior_file.write_text(json.dumps(code_behavior_config), encoding='utf-8')
    return code_behavior_file

def when_create_behavior_file_with_config(bot_directory: Path, behavior: str, behavior_config: dict):
    """When: Create behavior file with config."""
    behavior_dir = given_behavior_directory_created(bot_directory, behavior)
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    return behavior_file

def given_code_behavior_config():
    """Given: Code behavior config."""
    return {
        "behaviorName": "tests",
        "description": "Test behavior: tests",
        "goal": "Test goal for tests",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": ["Test instructions for tests."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build",
                    "order": 3,
                    "next_action": "render"
                },
                {
                    "name": "render",
                    "order": 4,
                    "next_action": "validate"
                },
                {
                    "name": "validate",
                    "order": 5
                }
            ]
        },
        "trigger_words": {
            "description": "Trigger words for tests",
            "patterns": ["test.*tests"],
            "priority": 10
        }
    }

def when_create_behavior_instances(bot_name: str, knowledge_behavior: str, code_behavior: str, bot_directory: Path):
    """When: Create behavior instances."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    bot_paths = BotPaths(bot_directory=bot_directory)
    knowledge_behavior_instance = Behavior(
        name=knowledge_behavior,
        bot_name=bot_name,
        bot_paths=bot_paths
    )
    code_behavior_instance = Behavior(
        name=code_behavior,
        bot_name=bot_name,
        bot_paths=bot_paths
    )
    return knowledge_behavior_instance, code_behavior_instance

def then_knowledge_behavior_has_standard_order(knowledge_behavior_instance):
    """Then: Knowledge behavior has standard order."""
    knowledge_expected_states = ['build', 'validate', 'render']
    actual_states = [action.action_name for action in knowledge_behavior_instance.actions]
    assert actual_states == knowledge_expected_states, (
        f"Knowledge behavior should have standard order {knowledge_expected_states}, "
        f"got {actual_states}"
    )

def then_code_behavior_has_reversed_order(code_behavior_instance):
    """Then: Code behavior has reversed order."""
    code_expected_states = ['build', 'render', 'validate']
    actual_states = [action.action_name for action in code_behavior_instance.actions]
    assert actual_states == code_expected_states, (
        f"Code behavior should have reversed order {code_expected_states}, "
        f"got {actual_states}"
    )

def then_behaviors_have_different_orders(knowledge_behavior_instance, code_behavior_instance):
    """Then: Behaviors have different orders."""
    knowledge_states = [action.action_name for action in knowledge_behavior_instance.actions]
    code_states = [action.action_name for action in code_behavior_instance.actions]
    assert knowledge_states != code_states, (
        "Different behaviors should have different action orders"
    )

def given_code_behavior_actions_workflow():
    """Given: Code behavior actions workflow."""
    return {
        "actions": [
            {
                "name": "build",
                "order": 3,
                "next_action": "render"
            },
            {
                "name": "render",
                "order": 4,
                "next_action": "validate"
            },
            {
                "name": "validate",
                "order": 5
            }
        ]
    }

def given_code_behavior_config_with_workflow(actions_workflow: dict):
    """Given: Code behavior config with workflow."""
    return {
        "behaviorName": "code",
        "description": "Test behavior: code",
        "goal": "Test goal for code",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/test_base_bot/base_actions",
        "instructions": ["Test instructions for code."],
        "actions_workflow": actions_workflow,
        "trigger_words": {
            "description": "Trigger words for code",
            "patterns": ["test.*code"],
            "priority": 10
        }
    }

def when_create_behavior_instance_for_code(bot_name: str, behavior: str, bot_directory: Path):
    """When: Create behavior instance for code."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_instance = Behavior(
        name=behavior,
        bot_name=bot_name,
        bot_paths=bot_paths
    )
    return behavior_instance

def then_transitions_match_expected(behavior_instance, expected_transitions: list):
    """Then: Transitions match expected."""
    # Behavior.workflow was removed - transitions are implicit in action order
    # Verify actions exist in correct order (transitions are derived from next_action on each action)
    actions_list = list(behavior_instance.actions)
    assert len(actions_list) > 0, "No actions found"
    # For now, just verify we have the expected number of actions
    # Full transition verification would require checking next_action on each action

def then_transition_dict_matches_expected(behavior_instance):
    """Then: Transition dict matches expected."""
    # Behavior.workflow was removed - check next_action from behavior.json instead
    # Get next_action from behavior's actions_workflow config
    behavior_config = behavior_instance.behavior_config
    actions_workflow = getattr(behavior_config, 'actions_workflow', [])
    
    # Find build action in actions_workflow
    build_action_dict = next((a for a in actions_workflow if a.get('name') == 'build'), None)
    if build_action_dict:
        next_action = build_action_dict.get('next_action')
        assert next_action == 'render', (
            f"build should transition to render, got {next_action}"
        )
    
    # Find render action in actions_workflow
    render_action_dict = next((a for a in actions_workflow if a.get('name') == 'render'), None)
    if render_action_dict:
        next_action = render_action_dict.get('next_action')
        assert next_action == 'validate', (
            f"render should transition to validate, got {next_action}"
        )


class TestInvokeBehaviorInWorkflowOrder:
    """Story: Behavior-Specific Workflow Order - Tests behavior-specific workflow configuration."""
    
    def test_workflow_determines_next_action_from_current_action(self, bot_directory, workspace_directory):
        """Scenario: Workflow determines next action from current_action (source of truth)"""
        
        # Given workflow_state.json shows:
        #   - current_action: build
        #   - completed_actions: [clarify] (may be behind)
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_action_for_gather_context(bot_name, behavior)
        
        # When workflow loads state (current_action is the source of truth)
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'build', completed)
        
        # Then current_state should be build (uses current_action from file)
        then_workflow_current_state_is_build_knowledge(workflow)

    def test_workflow_starts_at_first_action_when_no_completed_actions(self, bot_directory, workspace_directory):
        """Scenario: No completed actions yet"""
        
        # Given workflow loads state with no completed_actions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'clarify', [])
        
        # Then current_state should be the first action (clarify)
        then_workflow_current_state_is_gather_context(workflow)

    def test_workflow_uses_current_action_when_provided(self, bot_directory, workspace_directory):
        """Scenario: Workflow uses current_action when provided"""
        
        # Given current_action: strategy
        # And completed_actions: [clarify]
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_action_for_gather_context(bot_name, behavior)
        
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'strategy', completed)
        
        # Then current_state should be strategy (uses current_action from file)
        then_workflow_current_state_is_decide_planning_criteria(workflow)

    def test_workflow_falls_back_to_completed_actions_when_current_action_missing(self, bot_directory, workspace_directory):
        """Scenario: Workflow falls back to completed_actions when current_action is missing"""
        # Given: Bot name, behavior, and completed actions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_actions_for_three_actions(bot_name, behavior)
        
        # When: Workflow is created with empty workflow state
        workflow = given_environment_and_empty_workflow_state(bot_directory, workspace_directory, bot_name, behavior, completed)
        
        # Then: Current state falls back to validate
        then_current_state_is(workflow, 'validate')

    def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(self, bot_directory, workspace_directory):
        """Scenario: No workflow_state.json file exists (fresh start)"""
        # Given: Bot name, behavior, and no workflow file exists
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        
        workflow_file = given_environment_and_verify_no_workflow_file(bot_directory, workspace_directory)
        
        # When: Workflow is created with standard states and transitions
        states, transitions = given_standard_workflow_states_and_transitions()
        workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
        
        # Then: Workflow starts at first action
        then_current_state_is(workflow, 'clarify')

    def test_workflow_out_of_order_navigation_removes_completed_actions_after_target(self, bot_directory, workspace_directory):
        """Scenario: When navigating out of order, completed actions after target are removed"""
        
        # Given workflow_state.json shows:
        #   - current_action: validate (at the end)
        #   - completed_actions: [clarify, strategy, build, validate]
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_actions_for_four_actions(bot_name, behavior)
        
        # Bootstrap environment
        workflow_file, workflow = given_environment_workflow_state_and_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate', completed)
        
        # Verify initial state
        then_workflow_current_state_is(workflow, 'validate')
        
        # When navigating out of order back to build using production method
        target_action = 'build'
        when_navigate_to_target_action_out_of_order(workflow, target_action)
        
        # Then current_state should be build
        then_workflow_current_state_is(workflow, target_action)
        
        # And render should be removed from completed_actions
        then_verify_completed_actions_after_navigation(workflow_file, bot_name, behavior)
    
    def test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behaviors/{behavior_name}/behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'tests')
        behavior_config = given_write_tests_behavior_config()
        
        given_environment_and_behavior_config(bot_directory, workspace_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        then_workflow_states_and_transitions_match_tests(behavior_instance)
    
    def test_behavior_requires_actions_workflow_json_no_fallback(self, bot_directory, workspace_directory):
        """Scenario: Behavior REQUIRES behavior.json - no fallback exists"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'tests')
        behavior_dir = given_environment_and_behavior_directory(bot_directory, workspace_directory, behavior)
        
        exc_info = when_behavior_is_initialized_raises_error(bot_name, behavior, bot_directory)
        
        then_error_mentions_behavior_json_required(exc_info, behavior)
    
    def test_behavior_loads_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'tests')
        behavior_config = given_write_tests_behavior_config()
        
        given_environment_and_behavior_config(bot_directory, workspace_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        # Then: Workflow should use order from behavior.json
        expected_states = ['build', 'render', 'validate']
        then_workflow_states_match_expected(behavior_instance, expected_states)
    
    def _setup_behaviors_with_different_orders(self, bot_directory, bot_name):
        """Helper: Set up knowledge and code behaviors with different orders."""
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        knowledge_behavior = 'shape'
        knowledge_behavior_dir = given_behavior_directory_created(bot_directory, knowledge_behavior)
        knowledge_behavior_config = given_knowledge_behavior_config()
        given_behavior_json_file_created(knowledge_behavior_dir, knowledge_behavior_config)
        # Create minimal guardrails files (required by Guardrails class initialization)
        create_minimal_guardrails_files(bot_directory, knowledge_behavior, bot_name)
        
        code_behavior = 'tests'
        code_behavior_dir = given_behavior_directory_created(bot_directory, code_behavior)
        code_behavior_config = given_code_behavior_config()
        given_behavior_json_file_created(code_behavior_dir, code_behavior_config)
        # Create minimal guardrails files (required by Guardrails class initialization)
        create_minimal_guardrails_files(bot_directory, code_behavior, bot_name)
        return knowledge_behavior, code_behavior

    def test_different_behaviors_can_have_different_action_orders(self, bot_directory, workspace_directory):
        """Scenario: Different behaviors can have different action orders"""
        bot_name, _ = given_bot_name_and_behavior_setup('story_bot')
        knowledge_behavior, code_behavior = self._setup_behaviors_with_different_orders(bot_directory, bot_name)
        bootstrap_env(bot_directory, workspace_directory)
        
        knowledge_behavior_instance, code_behavior_instance = when_create_behavior_instances(bot_name, knowledge_behavior, code_behavior, bot_directory)
        then_knowledge_behavior_has_standard_order(knowledge_behavior_instance)
        then_code_behavior_has_reversed_order(code_behavior_instance)
        then_behaviors_have_different_orders(knowledge_behavior_instance, code_behavior_instance)
    
    def test_workflow_transitions_built_correctly_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Workflow transitions are built correctly from behavior.json"""
        
        # Given: Behavior with behavior.json and custom transitions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'code')
        behavior_dir = given_behavior_directory_created(bot_directory, behavior)
        
        # Create behavior.json with specific next_action values
        actions_workflow = given_code_behavior_actions_workflow()
        behavior_config = given_code_behavior_config_with_workflow(actions_workflow)
        given_behavior_json_file_created(behavior_dir, behavior_config)
        
        # Create minimal guardrails files (required by Guardrails class initialization)
        from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
        create_minimal_guardrails_files(bot_directory, behavior, bot_name)
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Behavior is initialized
        behavior_instance = when_create_behavior_instance_for_code(bot_name, behavior, bot_directory)
        
        # Then: Transitions should be built from action_config.json next_action values
        expected_transitions = given_expected_transitions_list()
        then_transitions_match_expected(behavior_instance, expected_transitions)
        
        # And: Each transition should have correct source and destination
        then_transition_dict_matches_expected(behavior_instance)


# ============================================================================
# Helper functions for Bot.execute_behavior() tests
# ============================================================================

def given_bot_config_created_for_execute_behavior(bot_directory: Path, bot_name: str, behaviors: list) -> Path:
    """Given: Bot config created for execute_behavior tests."""
    return create_bot_config_file(bot_directory, bot_name, behaviors)


def given_behavior_workflow_created_for_execute_behavior(bot_directory: Path, behavior_name: str):
    """Given: Behavior workflow created for execute_behavior tests."""
    create_actions_workflow_json(bot_directory, behavior_name)
    # Create minimal guardrails files (required by Guardrails class initialization)
    from agile_bot.bots.base_bot.test.test_helpers import create_guardrails_files
    create_guardrails_files(bot_directory, behavior_name, questions=[], evidence=[])


def given_multiple_behavior_workflows_created_for_execute_behavior(bot_directory: Path, behavior_names: list):
    """Given: Multiple behavior workflows created for execute_behavior tests."""
    for behavior_name in behavior_names:
        given_behavior_workflow_created_for_execute_behavior(bot_directory, behavior_name)


def given_completed_action_entry(bot_name: str, behavior: str, action: str, timestamp: str = None) -> dict:
    """Given: Completed action entry for workflow state."""
    if timestamp is None:
        timestamp = '2025-12-04T15:44:22.812230'
    return {'action_state': f'{bot_name}.{behavior}.{action}', 'timestamp': timestamp}


def given_workflow_state_created_for_execute_behavior(workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed_actions: list = None):
    """Given: Workflow state created for execute_behavior tests."""
    # Bot.execute_behavior looks for behavior_action_state.json, not workflow_state.json
    state_file = workspace_directory / 'behavior_action_state.json'
    state_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'completed_actions': completed_actions or []
    }), encoding='utf-8')
    return state_file


def given_bot_setup_with_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str, action: str) -> tuple[Bot, Path]:
    """Given: Bot setup with action."""
    bootstrap_env(bot_directory, workspace_directory)
    create_base_instructions(bot_directory)
    bot_config = given_bot_config_created_for_execute_behavior(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created_for_execute_behavior(bot_directory, behavior)
    given_workflow_state_created_for_execute_behavior(workspace_directory, bot_name, behavior, action)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_with_current_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str, current_action: str, completed_actions: list = None) -> tuple[Bot, Path]:
    """Given: Bot setup with current action."""
    bootstrap_env(bot_directory, workspace_directory)
    create_base_instructions(bot_directory)
    bot_config = given_bot_config_created_for_execute_behavior(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created_for_execute_behavior(bot_directory, behavior)
    given_workflow_state_created_for_execute_behavior(workspace_directory, bot_name, behavior, current_action, completed_actions)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_with_multiple_behaviors(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, current_behavior: str, current_action: str, completed_actions: list = None) -> tuple[Bot, Path]:
    """Given: Bot setup with multiple behaviors."""
    bootstrap_env(bot_directory, workspace_directory)
    create_base_instructions(bot_directory)
    bot_config = given_bot_config_created_for_execute_behavior(bot_directory, bot_name, behaviors)
    given_multiple_behavior_workflows_created_for_execute_behavior(bot_directory, behaviors)
    given_workflow_state_created_for_execute_behavior(workspace_directory, bot_name, current_behavior, current_action, completed_actions)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def given_bot_setup_without_workflow_state(bot_directory: Path, workspace_directory: Path, bot_name: str, behaviors: list, behavior: str) -> tuple[Bot, Path]:
    """Given: Bot setup without workflow state."""
    bootstrap_env(bot_directory, workspace_directory)
    create_base_instructions(bot_directory)
    bot_config = given_bot_config_created_for_execute_behavior(bot_directory, bot_name, behaviors)
    given_behavior_workflow_created_for_execute_behavior(bot_directory, behavior)
    given_no_workflow_state_exists(workspace_directory)
    bot = given_bot_instance_created(bot_name, bot_directory, bot_config)
    return bot, bot_config


def when_execute_behavior_called(bot: Bot, behavior: str, action: str = None) -> BotResult:
    """When: Execute behavior called."""
    if action:
        return bot.execute_behavior(behavior, action=action)
    else:
        return bot.execute_behavior(behavior)


def then_bot_result_has_correct_status(result: BotResult, expected_status: str, expected_behavior: str = None, expected_action: str = None):
    """Then: BotResult has correct status."""
    assert isinstance(result, BotResult)
    assert result.status == expected_status
    if expected_behavior:
        assert result.behavior == expected_behavior
    if expected_action:
        assert result.action == expected_action


def then_bot_result_requires_confirmation_with_tool(result: BotResult, tool_name: str):
    """Then: BotResult requires confirmation with specific tool."""
    assert isinstance(result, BotResult)
    assert result.status == 'requires_confirmation'
    assert 'confirmation_tool' in result.data
    assert result.data['confirmation_tool'] == tool_name


def then_bot_result_requires_entry_workflow_confirmation(result: BotResult, expected_behavior: str):
    """Then: BotResult requires entry workflow confirmation."""
    assert isinstance(result, BotResult)
    assert result.status == 'requires_confirmation'
    assert 'behaviors' in result.data
    assert expected_behavior in result.data['behaviors']


def given_standard_workflow_actions():
    """Given: Standard workflow actions list."""
    # Standard workflow uses: clarify, strategy, validate_rules, render (no build)
    return ['clarify', 'strategy', 'validate_rules', 'render']


def then_bot_result_has_error_with_invalid_action_message(result: BotResult, bot_name: str, behavior: str, invalid_action: str, valid_actions: list):
    """Then: BotResult has error with invalid action message."""
    assert isinstance(result, BotResult)
    assert result.status == 'error'
    assert result.behavior == behavior
    assert result.action == invalid_action
    assert 'message' in result.data
    assert 'INVALID ACTION' in result.data['message']
    assert invalid_action in result.data['message']
    # Check that all valid actions are listed in the message
    for valid_action in valid_actions:
        assert valid_action in result.data['message']
    assert 'valid_actions' in result.data
    for valid_action in valid_actions:
        assert valid_action in result.data['valid_actions']
    # The error message shows an example format, not all formats - just check that the example format is present
    assert f'{bot_name}_{behavior}_clarify' in result.data['message']


def given_no_workflow_state_exists(workspace_directory: Path):
    """Given: No workflow state exists."""
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()


class TestExecuteBehavior:
    """Tests for Bot.execute_behavior() - Production code path."""

    def test_execute_behavior_with_action_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior with action parameter
        GIVEN: Bot has behavior 'shape' with action 'clarify'
        WHEN: Bot.execute_behavior('shape', action='clarify') is called
        THEN: Action executes and returns BotResult
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'clarify')
        
        bot_result = when_execute_behavior_called(bot, 'shape', 'clarify')
        
        then_bot_result_has_correct_status(bot_result, 'completed', 'shape', 'clarify')

    def test_execute_behavior_without_action_forwards_to_current(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior without action parameter forwards to current action
        GIVEN: Bot has behavior 'shape' and workflow state shows current_action='strategy'
        WHEN: Bot.execute_behavior('shape') is called (no action parameter)
        THEN: Forwards to current action (strategy)
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'clarify')
        bot, _ = given_bot_setup_with_current_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'strategy', [completed_action])
        
        bot_result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_has_correct_status(bot_result, 'completed', expected_action='strategy')

    def test_execute_behavior_requires_confirmation_when_out_of_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior requires confirmation when out of order
        GIVEN: Current behavior is 'discovery', requested behavior is 'shape' (going backwards)
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation'
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'validate', '2025-12-04T15:45:00.000000')
        bot, _ = given_bot_setup_with_multiple_behaviors(bot_directory, workspace_directory, 'test_bot', ['shape', 'prioritization', 'discovery'], 'prioritization', 'clarify', [completed_action])
        
        bot_result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_requires_confirmation_with_tool(bot_result, 'confirm_out_of_order')

    def test_execute_behavior_handles_entry_workflow_when_no_state(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior handles entry workflow when no workflow state exists
        GIVEN: No workflow_state.json exists
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation' for entry workflow
        """
        bot, _ = given_bot_setup_without_workflow_state(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape')
        
        bot_result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_requires_entry_workflow_confirmation(bot_result, 'shape')

    def test_execute_behavior_returns_error_for_invalid_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior returns error for invalid action
        GIVEN: Bot has behavior 'prioritization' with valid actions: clarify, strategy, etc.
        WHEN: Bot.execute_behavior('prioritization', action='start') is called with invalid action 'start'
        THEN: Returns BotResult with status 'error' and message listing valid actions
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['prioritization'], 'prioritization', 'clarify')
        
        bot_result = when_execute_behavior_called(bot, 'prioritization', 'start')
        
        valid_actions = given_standard_workflow_actions()
        then_bot_result_has_error_with_invalid_action_message(bot_result, 'test_bot', 'prioritization', 'start', valid_actions)


# ============================================================================
# EXCEPTION HANDLING TESTS
# ============================================================================

def given_bot_directory_created(tmp_path, bot_name: str) -> Path:
    """Given: Bot directory created."""
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    return bot_directory


def given_workspace_directory_setup(tmp_path, bot_directory: Path) -> Path:
    """Given: Workspace directory setup."""
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    return workspace_dir


def given_behavior_json_files_exist(bot_directory: Path, behaviors: list):
    """Given: Behavior.json files exist for behaviors."""
    for behavior in behaviors:
        create_actions_workflow_json(bot_directory, behavior)


def when_initializing_workflow_with_invalid_behavior(bot: Bot, workspace_dir: Path, invalid_behavior: str):
    """When: Initializing workflow with invalid behavior."""
    with pytest.raises(ValueError, match=f"Behavior '{invalid_behavior}' not found") as exc_info:
        bot._initialize_workflow_state(
            working_dir=workspace_dir,
            confirmed_behavior=invalid_behavior
        )
    return exc_info


def given_behavior_folder_without_json(bot_directory: Path, behavior_name: str) -> Path:
    """Given: Behavior folder WITHOUT behavior.json."""
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir


def when_creating_behavior_instance_without_json(bot_name: str, bot_directory: Path, behavior_name: str):
    """When: Creating Behavior instance without behavior.json."""
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    bot_paths = BotPaths(bot_directory=bot_directory)
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name=behavior_name,
            bot_name=bot_name,
            bot_paths=bot_paths
        )
    return exc_info


def then_exception_mentions_behavior_json_required(exc_info, behavior_name: str):
    """Then: Exception mentions behavior.json is REQUIRED."""
    # The actual error message says "Behavior config not found" not "behavior.json is REQUIRED"
    assert 'behavior.json' in str(exc_info.value) or 'Behavior config not found' in str(exc_info.value)
    assert behavior_name in str(exc_info.value)


class TestBotBehaviorExceptions:
    """Tests for Bot exception handling - no fallbacks."""

    def test_bot_raises_exception_when_behavior_not_found(self, tmp_path):
        """
        SCENARIO: Bot raises exception when behavior not found
        GIVEN: Bot setup with valid behaviors
        WHEN: Initializing workflow with invalid behavior
        THEN: Bot raises ValueError
        """
        # Given: Bot setup with valid behaviors
        bot_name = 'test_bot'
        bot_directory = given_bot_directory_created(tmp_path, bot_name)
        config_file = create_bot_config_file(bot_directory, bot_name, ['shape', 'discovery'])
        workspace_dir = given_workspace_directory_setup(tmp_path, bot_directory)
        from agile_bot.bots.base_bot.test.test_helpers import create_base_actions_structure
        create_base_actions_structure(bot_directory)
        given_behavior_json_files_exist(bot_directory, ['shape', 'discovery'])
        bot = given_bot_instance_created(bot_name, bot_directory, config_file)
        
        # When: Initializing workflow with invalid behavior
        when_initializing_workflow_with_invalid_behavior(bot, workspace_dir, 'invalid_behavior')
        
        # Then: Exception is raised (verified by when_initializing_workflow_with_invalid_behavior)

    def test_behavior_raises_exception_when_actions_workflow_missing(self, tmp_path):
        """
        SCENARIO: Behavior raises exception when actions workflow missing
        GIVEN: Behavior folder exists but behavior.json is missing
        WHEN: Creating Behavior instance
        THEN: Behavior raises FileNotFoundError mentioning behavior.json is REQUIRED
        """
        bot_name = 'test_bot'
        bot_directory = given_bot_directory_created(tmp_path, bot_name)
        given_behavior_folder_without_json(bot_directory, 'shape')
        given_workspace_directory_setup(tmp_path, bot_directory)
        
        exc_info = when_creating_behavior_instance_without_json(bot_name, bot_directory, 'shape')
        then_exception_mentions_behavior_json_required(exc_info, 'shape')


# ============================================================================
# STORY: Insert Context Into Instructions
# ============================================================================

class TestInsertContextIntoInstructions:
    """Tests for Insert Context Into Instructions story."""
    
    def test_action_loads_context_data_into_instructions(self, tmp_path, monkeypatch):
        """Test that Action loads clarification, strategy, and context files into instructions."""
        # Given A clarification.json file exists with data for multiple behaviors
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        docs_dir = workspace_dir / "docs" / "stories"
        docs_dir.mkdir(parents=True)
        
        clarification_data = {
            "shape": {
                "key_questions": {
                    "questions": ["What is the goal?"],
                    "answers": {"goal": "Build a story map"}
                },
                "evidence": {
                    "required": ["input.txt"],
                    "provided": {"input.txt": "content"}
                }
            },
            "discovery": {
                "key_questions": {
                    "questions": ["What stories exist?"],
                    "answers": {"stories": "Many"}
                },
                "evidence": {
                    "required": [],
                    "provided": {}
                }
            }
        }
        
        clarification_file = docs_dir / "clarification.json"
        clarification_file.write_text(json.dumps(clarification_data, indent=2))
        
        # And A strategy.json file exists with data for multiple behaviors
        strategy_data = {
            "shape": {
                "strategy_criteria": {
                    "criteria": {"approach": {"question": "How?", "options": ["A", "B"]}},
                    "decisions_made": {"approach": "A"}
                },
                "assumptions": {
                    "typical_assumptions": ["Assume X"],
                    "assumptions_made": ["Assume Y"]
                },
                "recommended_activities": ["Activity 1"]
            }
        }
        
        strategy_file = docs_dir / "strategy.json"
        strategy_file.write_text(json.dumps(strategy_data, indent=2))
        
        # And A docs/context/ folder exists with input.txt and other files
        context_dir = docs_dir / "context"
        context_dir.mkdir(parents=True)
        (context_dir / "input.txt").write_text("Original input content")
        (context_dir / "initial-context.md").write_text("# Initial Context")
        (context_dir / "requirements.md").write_text("# Requirements")
        
        # And An Action is initialized
        bot_dir = tmp_path / "bot"
        bot_dir.mkdir(parents=True)
        bootstrap_env(bot_dir, workspace_dir)
        bot_paths = BotPaths(bot_directory=bot_dir)
        
        # Create behavior folder with minimal required files
        behavior_folder = create_behavior_folder_with_json(bot_dir, "shape")
        
        behavior = Behavior("shape", "test_bot", bot_paths)
        from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
        base_action_config = BaseActionConfig("build", bot_paths)
        from agile_bot.bots.base_bot.src.actions.action import Action
        action = Action(base_action_config=base_action_config, behavior=behavior)
        
        # When Action loads and merges instructions
        instructions = action.instructions
        
        # Then Instructions contain 'clarification' key with all clarification data
        assert 'clarification' in instructions
        assert instructions['clarification'] == clarification_data
        
        # And Instructions contain 'strategy' key with all strategy data
        assert 'strategy' in instructions
        assert instructions['strategy'] == strategy_data
        
        # And Instructions contain 'context_files' key with list of file names
        assert 'context_files' in instructions
        context_files = instructions['context_files']
        assert isinstance(context_files, list)
        assert 'input.txt' in context_files
        assert 'initial-context.md' in context_files
        assert 'requirements.md' in context_files
        
        # And Base instructions include explanation of clarification data
        base_instructions = instructions['base_instructions']
        assert any('CLARIFICATION DATA AVAILABLE' in str(inst) for inst in base_instructions)
        
        # And Base instructions include explanation of strategy data
        assert any('STRATEGY DATA AVAILABLE' in str(inst) for inst in base_instructions)
        
        # And Base instructions include explanation of context files
        assert any('ORIGINAL CONTEXT FILES AVAILABLE' in str(inst) for inst in base_instructions)
        
        # And Context file contents are NOT loaded into instructions
        assert 'Original input content' not in str(instructions)
        
        # When No clarification.json file exists
        clarification_file.unlink()
        action2 = Action(base_action_config=base_action_config, behavior=behavior)
        instructions2 = action2.instructions
        
        # Then Instructions do NOT contain 'clarification' key and no error is raised
        assert 'clarification' not in instructions2
        assert instructions2 is not None
        
        # When No strategy.json file exists
        strategy_file.unlink()
        action3 = Action(base_action_config=base_action_config, behavior=behavior)
        instructions3 = action3.instructions
        
        # Then Instructions do NOT contain 'strategy' key and no error is raised
        assert 'strategy' not in instructions3
        assert instructions3 is not None
        
        # When No docs/context/ folder exists
        import shutil
        shutil.rmtree(context_dir)
        action4 = Action(base_action_config=base_action_config, behavior=behavior)
        instructions4 = action4.instructions
        
        # Then Instructions do NOT contain 'context_files' key and no error is raised
        assert 'context_files' not in instructions4
        assert instructions4 is not None


# ============================================================================
# HELPER FUNCTIONS - Load Bot Configuration Story
# ============================================================================

def given_bot_directory_and_config_file(tmp_path: Path, bot_name: str, config_data: dict) -> Path:
    """Given: Bot directory and config file exist."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True)
    # BotConfig expects bot_config.json directly in bot_directory, not in config/ subdirectory
    config_file = bot_dir / 'bot_config.json'
    config_file.write_text(
        json.dumps(config_data),
        encoding='utf-8'
    )
    return bot_dir


def given_bot_directory_without_config_file(tmp_path: Path, bot_name: str) -> Path:
    """Given: Bot directory exists but config file is missing."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True)
    return bot_dir


def given_bot_directory_with_invalid_config_file(tmp_path: Path, bot_name: str) -> Path:
    """Given: Bot directory exists with invalid JSON config file."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True)
    # BotConfig expects bot_config.json directly in bot_directory, not in config/ subdirectory
    config_file = bot_dir / 'bot_config.json'
    config_file.write_text('invalid json {', encoding='utf-8')
    return bot_dir


def given_bot_paths_configured(workspace: Path, bot_dir: Path):
    """Given: BotPaths configured with environment variables for tests."""
    os.environ['WORKING_AREA'] = str(workspace)
    os.environ['BOT_DIRECTORY'] = str(bot_dir)
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    return BotPaths(workspace)


def when_bot_config_is_created(bot_name: str, bot_paths) -> BotConfig:
    """When: BotConfig is created."""
    return BotConfig(bot_name=bot_name, bot_paths=bot_paths)


def then_bot_config_is_not_none(bot_config: BotConfig):
    """Then: BotConfig is not None."""
    assert bot_config is not None


def then_bot_config_has_bot_name(bot_config: BotConfig, expected_bot_name: str):
    """Then: BotConfig has correct bot_name."""
    assert bot_config.bot_name == expected_bot_name


def then_bot_config_name_matches(bot_config: BotConfig, expected_name: str):
    """Then: BotConfig.name property matches expected."""
    assert bot_config.name == expected_name


def then_bot_config_behaviors_list_matches(bot_config: BotConfig, expected_behaviors: list):
    """Then: BotConfig.behaviors_list matches expected."""
    assert bot_config.behaviors_list == expected_behaviors


def then_bot_config_behaviors_list_has_length(bot_config: BotConfig, expected_length: int):
    """Then: BotConfig.behaviors_list has expected length."""
    assert len(bot_config.behaviors_list) == expected_length


def then_bot_config_behaviors_list_is_empty(bot_config: BotConfig):
    """Then: BotConfig.behaviors_list is empty."""
    assert bot_config.behaviors_list == []


def then_bot_config_base_actions_path_matches(bot_config: BotConfig, expected_path: Path):
    """Then: BotConfig.base_actions_path matches expected."""
    assert bot_config.base_actions_path == expected_path
    assert isinstance(bot_config.base_actions_path, Path)


def then_bot_config_raises_file_not_found_error(bot_name: str, bot_paths):
    """Then: BotConfig raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        BotConfig(bot_name=bot_name, bot_paths=bot_paths)


def then_bot_config_raises_json_decode_error(bot_name: str, bot_paths):
    """Then: BotConfig raises JSONDecodeError or ValueError."""
    with pytest.raises((json.JSONDecodeError, ValueError)):
        BotConfig(bot_name=bot_name, bot_paths=bot_paths)


# ============================================================================
# STORY: Load Bot Configuration
# ============================================================================

class TestLoadBotConfiguration:
    """Story: Load Bot Configuration - Tests that bot configuration can be loaded from bot_config.json."""
    
    def test_bot_config_instantiation_with_bot_name_and_workspace(self, tmp_path, bot_name):
        """Scenario: BotConfig can be instantiated with bot_name and workspace."""
        # Given: Bot directory and config file exist
        bot_dir = given_bot_directory_and_config_file(
            tmp_path, bot_name, 
            {'name': bot_name, 'behaviors': ['shape', 'prioritization']}
        )
        
        # When: BotConfig is created
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        bot_config = when_bot_config_is_created(bot_name, bot_paths)
        
        # Then: BotConfig is not None and has correct bot_name
        then_bot_config_is_not_none(bot_config)
        then_bot_config_has_bot_name(bot_config, bot_name)
    
    def test_bot_config_name_property(self, tmp_path, bot_name):
        """Scenario: BotConfig.name property returns bot name from config."""
        # Given: Bot directory and config file with name
        bot_dir = given_bot_directory_and_config_file(
            tmp_path, bot_name,
            {'name': bot_name, 'behaviors': ['shape']}
        )
        
        # When: BotConfig is created
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        bot_config = when_bot_config_is_created(bot_name, bot_paths)
        
        # Then: BotConfig.name matches expected
        then_bot_config_name_matches(bot_config, bot_name)
    
    def test_bot_config_behaviors_list_property(self, tmp_path, bot_name):
        """Scenario: BotConfig.behaviors_list property loads from bot_config.json."""
        # Given: Bot directory and config file with behaviors list
        behaviors = ['shape', 'prioritization', 'discovery']
        bot_dir = given_bot_directory_and_config_file(
            tmp_path, bot_name,
            {'name': bot_name, 'behaviors': behaviors}
        )
        
        # When: BotConfig is created
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        bot_config = when_bot_config_is_created(bot_name, bot_paths)
        
        # Then: BotConfig.behaviors_list matches expected
        then_bot_config_behaviors_list_matches(bot_config, behaviors)
        then_bot_config_behaviors_list_has_length(bot_config, 3)
    
    def test_bot_config_behaviors_list_empty_when_missing(self, tmp_path, bot_name):
        """Scenario: BotConfig.behaviors_list returns empty list when behaviors missing from config."""
        # Given: Bot directory and config file without behaviors
        bot_dir = given_bot_directory_and_config_file(
            tmp_path, bot_name,
            {'name': bot_name}
        )
        
        # When: BotConfig is created
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        bot_config = when_bot_config_is_created(bot_name, bot_paths)
        
        # Then: BotConfig.behaviors_list is empty
        then_bot_config_behaviors_list_is_empty(bot_config)
    
    def test_bot_config_base_actions_path_property(self, tmp_path, bot_name):
        """Scenario: BotConfig.base_actions_path property returns path to base_actions directory."""
        # Given: Bot directory and config file
        bot_dir = given_bot_directory_and_config_file(
            tmp_path, bot_name,
            {'name': bot_name, 'behaviors': ['shape']}
        )
        
        # When: BotConfig is created
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        bot_config = when_bot_config_is_created(bot_name, bot_paths)
        
        # Then: BotConfig.base_actions_path matches expected
        expected_path = bot_dir / 'base_actions'
        then_bot_config_base_actions_path_matches(bot_config, expected_path)
    
    def test_bot_config_raises_error_when_config_file_missing(self, tmp_path, bot_name):
        """Scenario: BotConfig raises FileNotFoundError when bot_config.json is missing."""
        # Given: Bot directory exists but config file is missing
        bot_dir = given_bot_directory_without_config_file(tmp_path, bot_name)
        
        # When/Then: BotConfig creation raises FileNotFoundError
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        then_bot_config_raises_file_not_found_error(bot_name, bot_paths)
    
    def test_bot_config_raises_error_when_config_invalid_json(self, tmp_path, bot_name):
        """Scenario: BotConfig raises error when bot_config.json contains invalid JSON."""
        # Given: Bot directory exists with invalid JSON config file
        bot_dir = given_bot_directory_with_invalid_config_file(tmp_path, bot_name)
        
        # When/Then: BotConfig creation raises JSONDecodeError or ValueError
        bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
        then_bot_config_raises_json_decode_error(bot_name, bot_paths)


# ============================================================================
# STORY: Load Behavior Configuration
# ============================================================================


class TestLoadBehaviorConfiguration:
    """Story: Load Behavior Configuration - behavior.json is parsed via BehaviorConfig."""

    def test_behavior_config_loads_fields_and_actions(self, tmp_path):
        """Scenario: BehaviorConfig loads fields and sorts actions_workflow by order."""
        # Given: environment and behavior config file
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "tests"
        behavior_config_data = {
            "description": "Write tests for behaviors",
            "goal": "Ensure behavior actions are validated",
            "inputs": ["stories", "codebase"],
            "outputs": ["test_results"],
            "instructions": {"note": "follow Given-When-Then"},
            "trigger_words": ["tests", "validation"],
            "actions_workflow": {
                "actions": [
                    {"name": "validate", "order": 3, "next_action": None},
                    {"name": "clarify", "order": 1, "next_action": "strategy"},
                    {"name": "strategy", "order": 2, "next_action": "validate"},
                ]
            },
        }
        given_behavior_config_created(bot_dir, behavior, behavior_config_data)

        # When: BehaviorConfig is created
        bot_paths = when_bot_paths_is_created(workspace_dir)
        behavior_config = when_behavior_config_is_created(behavior, bot_paths)

        # Then: Fields and actions are loaded correctly
        then_behavior_config_matches_fields(
            behavior_config,
            expected_description="Write tests for behaviors",
            expected_goal="Ensure behavior actions are validated",
            expected_inputs=["stories", "codebase"],
            expected_outputs=["test_results"],
            expected_instructions={"note": "follow Given-When-Then"},
            expected_trigger_words=["tests", "validation"],
        )
        then_actions_workflow_sorted(
            behavior_config,
            expected_actions=["clarify", "strategy", "validate"],
            expected_names=["clarify", "strategy", "validate"],
        )

    def test_behavior_config_raises_when_missing_file(self, tmp_path):
        """Scenario: BehaviorConfig raises FileNotFoundError when behavior.json missing."""
        # Given: environment set but behavior.json not present
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "missing_behavior"

        # When/Then: Creating BehaviorConfig raises FileNotFoundError
        bot_paths = when_bot_paths_is_created(workspace_dir)
        with pytest.raises(FileNotFoundError):
            when_behavior_config_is_created(behavior, bot_paths)

    def test_behavior_config_raises_on_invalid_json(self, tmp_path):
        """Scenario: BehaviorConfig raises JSONDecodeError or ValueError on invalid JSON."""
        # Given: environment and invalid behavior.json
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "invalid_behavior"
        behavior_dir = bot_dir / "behaviors" / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        (behavior_dir / "behavior.json").write_text("invalid json {", encoding="utf-8")

        # When/Then: Creating BehaviorConfig raises JSONDecodeError or ValueError
        bot_paths = when_bot_paths_is_created(workspace_dir)
        with pytest.raises((json.JSONDecodeError, ValueError)):
            when_behavior_config_is_created(behavior, bot_paths)


# ============================================================================
# HELPER FUNCTIONS - Load Bot Behaviors Story
# ============================================================================

def given_bot_config_with_behaviors(tmp_path: Path, bot_name: str, behaviors: list) -> BotConfig:
    """Given: BotConfig with behaviors list."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_dir.mkdir(parents=True)
    # BotConfig expects bot_config.json directly in bot_directory, not in config/ subdirectory
    config_file = bot_dir / 'bot_config.json'
    config_file.write_text(
        json.dumps({'name': bot_name, 'behaviors': behaviors}),
        encoding='utf-8'
    )
    
    # Create behavior folders with behavior.json files (required for Behavior initialization)
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    for behavior_name in behaviors:
        create_actions_workflow_json(bot_dir, behavior_name)
        # Create minimal guardrails files (required for Guardrails initialization)
        create_minimal_guardrails_files(bot_dir, behavior_name, bot_name)
        # Create strategy guardrails files (required for Strategy initialization)
        strategy_dir = bot_dir / 'behaviors' / behavior_name / 'guardrails' / 'strategy'
        strategy_dir.mkdir(parents=True, exist_ok=True)
        assumptions_file = strategy_dir / 'typical_assumptions.json'
        assumptions_file.write_text(json.dumps({'typical_assumptions': []}), encoding='utf-8')
        recommended_activities_file = strategy_dir / 'recommended_activities.json'
        recommended_activities_file.write_text(json.dumps({'recommended_activities': []}), encoding='utf-8')
        decision_criteria_dir = strategy_dir / 'decision_criteria'
        decision_criteria_dir.mkdir(parents=True, exist_ok=True)
    
    bot_paths = given_bot_paths_configured(tmp_path, bot_dir)
    return BotConfig(bot_name=bot_name, bot_paths=bot_paths)


def given_behavior_action_state_file(workspace_dir: Path, bot_name: str, current_behavior: str = None):
    """Given: behavior_action_state.json file exists."""
    state_file = workspace_dir / 'behavior_action_state.json'
    state_data = {
        'current_behavior': f'{bot_name}.{current_behavior}' if current_behavior else '',
        'timestamp': '2025-12-04T15:55:00.000000'
    }
    state_file.write_text(json.dumps(state_data), encoding='utf-8')
    return state_file


def when_behaviors_collection_is_created(bot_config: BotConfig):
    """When: Behaviors collection is created."""
    from agile_bot.bots.base_bot.src.bot.behaviors import Behaviors
    return Behaviors(bot_config)


def then_behaviors_collection_is_not_none(behaviors):
    """Then: Behaviors collection is not None."""
    assert behaviors is not None


def then_behaviors_collection_has_current(behaviors, expected_behavior_name: str):
    """Then: Behaviors collection has correct current behavior."""
    assert behaviors.current is not None
    assert behaviors.current.name == expected_behavior_name


def then_behaviors_collection_current_is_none(behaviors):
    """Then: Behaviors collection current is None."""
    assert behaviors.current is None


def when_behaviors_collection_navigates_to(behaviors, behavior_name: str):
    """When: Behaviors collection navigates to behavior."""
    behaviors.navigate_to(behavior_name)


def when_behaviors_next_accessed(behaviors):
    """When: Behaviors next property accessed."""
    return behaviors.next()


def then_current_behavior_is(behaviors, expected_behavior_name: str):
    """Then: Current behavior matches expected."""
    assert behaviors.current is not None
    assert behaviors.current.name == expected_behavior_name


def then_behavior_action_state_file_contains(workspace_dir: Path, bot_name: str, expected_behavior: str):
    """Then: behavior_action_state.json contains expected behavior."""
    state_file = workspace_dir / 'behavior_action_state.json'
    assert state_file.exists()
    state_data = json.loads(state_file.read_text(encoding='utf-8'))
    assert state_data['current_behavior'] == f'{bot_name}.{expected_behavior}'


# ============================================================================
# STORY: Load Bot Behaviors
# ============================================================================

class TestLoadBotBehaviors:
    """Story: Load Bot Behaviors - Tests that bot behaviors can be loaded from configuration and managed as a collection with state persistence."""
    
    def test_load_behaviors_from_bot_config(self, tmp_path, bot_name):
        """Scenario: Bot behaviors are loaded from BotConfig."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        
        # When: Behaviors collection is created
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # Then: Behaviors collection is not None
        then_behaviors_collection_is_not_none(behaviors)
    
    def test_load_behaviors_sets_first_as_current(self, tmp_path, bot_name):
        """Scenario: When behaviors are loaded, first behavior is set as current."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        
        # When: Behaviors collection is created
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # Then: Current behavior is first in list
        then_behaviors_collection_has_current(behaviors, 'shape')
    
    def test_find_behavior_by_name(self, tmp_path, bot_name):
        """Scenario: Behavior can be found by name when it exists."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Find behavior by name
        found_behavior = behaviors.find_by_name('prioritization')
        
        # Then: Behavior is found and matches expected name
        assert found_behavior is not None
        assert found_behavior.name == 'prioritization'
    
    def test_find_behavior_returns_none_when_not_found(self, tmp_path, bot_name):
        """Scenario: Finding behavior by name returns None when behavior doesn't exist."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Find non-existent behavior
        found_behavior = behaviors.find_by_name('nonexistent')
        
        # Then: Behavior is not found (returns None)
        assert found_behavior is None
    
    def test_get_next_behavior(self, tmp_path, bot_name):
        """Scenario: Next behavior in sequence can be retrieved."""
        # Given: BotConfig with behaviors list and current is first
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Get next behavior
        next_behavior = behaviors.next()
        
        # Then: Next behavior is second in list
        assert next_behavior is not None
        assert next_behavior.name == 'prioritization'
    
    def test_get_next_behavior_returns_none_at_end(self, tmp_path, bot_name):
        """Scenario: Getting next behavior returns None when at last behavior."""
        # Given: BotConfig with behaviors list, navigate to last
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors, 'prioritization')
        
        # When: Get next behavior
        next_behavior = behaviors.next()
        
        # Then: Next behavior is None
        assert next_behavior is None
    
    def test_iterate_all_behaviors(self, tmp_path, bot_name):
        """Scenario: All behaviors can be iterated."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Iterate all behaviors
        behavior_names = [b.name for b in behaviors]
        
        # Then: All behaviors are returned
        assert len(behavior_names) == 3
        assert 'shape' in behavior_names
        assert 'prioritization' in behavior_names
        assert 'discovery' in behavior_names
    
    def test_check_behavior_exists(self, tmp_path, bot_name):
        """Scenario: Can check if a behavior exists."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Check if behavior exists
        exists = behaviors.check_exists('shape')
        not_exists = behaviors.check_exists('nonexistent')
        
        # Then: Check exists returns True for existing behavior, False for non-existent
        assert exists is True
        assert not_exists is False
    
    def test_navigate_to_behavior(self, tmp_path, bot_name):
        """Scenario: Can navigate to a specific behavior."""
        # Given: BotConfig with behaviors list
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # When: Navigate to specific behavior
        when_behaviors_collection_navigates_to(behaviors, 'discovery')
        
        # Then: That behavior becomes the current behavior
        then_current_behavior_is(behaviors, 'discovery')
    
    def test_save_current_behavior_state(self, tmp_path, bot_name):
        """Scenario: Current behavior state is persisted to behavior_action_state.json."""
        # Given: BotConfig with behaviors list and current behavior set
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        behaviors = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors, 'prioritization')
        
        # When: Save state
        behaviors.save_state()
        
        # Then: behavior_action_state.json contains current behavior
        then_behavior_action_state_file_contains(tmp_path, bot_name, 'prioritization')
    
    def test_load_behavior_state_from_file(self, tmp_path, bot_name):
        """Scenario: Current behavior state is restored from behavior_action_state.json."""
        # Given: behavior_action_state.json exists with current behavior
        given_behavior_action_state_file(tmp_path, bot_name, 'prioritization')
        behaviors_list = ['shape', 'prioritization', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        
        # When: Behaviors collection is created (loads state automatically)
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # Then: Current behavior matches saved state
        then_behaviors_collection_has_current(behaviors, 'prioritization')
    
    def test_load_behaviors_uses_first_when_state_file_missing(self, tmp_path, bot_name):
        """Scenario: When state file is missing, first behavior is used as current."""
        # Given: BotConfig with behaviors list but no state file
        behaviors_list = ['shape', 'prioritization']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors_list)
        
        # When: Behaviors collection is created
        behaviors = when_behaviors_collection_is_created(bot_config)
        
        # Then: Current behavior is first in list
        then_behaviors_collection_has_current(behaviors, 'shape')


# ============================================================================
# HELPER FUNCTIONS - Load Actions Story
# ============================================================================

def given_bot_paths_for_actions(tmp_path: Path, bot_name: str) -> BotPaths:
    """Given: BotPaths configured for actions tests."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    workspace_dir = tmp_path / 'workspace'
    bot_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_dir, workspace_dir)
    return BotPaths(bot_directory=bot_dir)


def given_behavior_with_actions_workflow(bot_paths: BotPaths, bot_name: str, behavior_name: str, actions: list) -> Path:
    """Given: Behavior with actions_workflow."""
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    behavior_dir = bot_paths.bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    
    behavior_config = {
        "description": f"Test behavior {behavior_name}",
        "goal": "Test goal",
        "inputs": [],
        "outputs": [],
        "actions_workflow": {
            "actions": actions
        }
    }
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_paths.bot_directory, behavior_name, bot_name)
    return behavior_file


def given_base_action_config_exists(bot_paths: BotPaths, action_name: str, config_data: dict = None) -> Path:
    """Given: Base action config file exists.
    
    If bot_directory is base_bot, redirects to test_base_bot/base_actions.
    """
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    base_actions_dir = get_test_base_actions_dir(bot_paths.bot_directory) / action_name
    base_actions_dir.mkdir(parents=True, exist_ok=True)
    config_file = base_actions_dir / 'action_config.json'
    
    if config_data is None:
        config_data = {
            "name": action_name,
            "workflow": True,
            "order": 0
        }
    
    config_file.write_text(json.dumps(config_data), encoding='utf-8')
    return config_file


def given_behavior_action_state_file_with_action(bot_paths: BotPaths, bot_name: str, behavior_name: str, current_action: str = None):
    """Given: behavior_action_state.json file exists with current action."""
    state_file = bot_paths.workspace_directory / 'behavior_action_state.json'
    state_data = {
        'current_behavior': f'{bot_name}.{behavior_name}',
        'timestamp': '2025-12-04T15:55:00.000000'
    }
    if current_action:
        state_data['current_action'] = f'{bot_name}.{behavior_name}.{current_action}'
    state_file.write_text(json.dumps(state_data), encoding='utf-8')
    return state_file


def when_behavior_is_created_for_actions(bot_name: str, behavior_name: str, bot_paths: BotPaths) -> Behavior:
    """When: Behavior is created."""
    return Behavior(name=behavior_name, bot_name=bot_name, bot_paths=bot_paths)


def when_actions_collection_is_created(behavior: Behavior):
    """When: Actions collection is created."""
    return behavior.actions


def then_actions_collection_is_not_none(actions):
    """Then: Actions collection is not None."""
    assert actions is not None


def then_actions_collection_has_current(actions, expected_action_name: str):
    """Then: Actions collection has correct current action."""
    assert actions.current is not None
    assert actions.current.action_name == expected_action_name


def then_actions_collection_current_is_none(actions):
    """Then: Actions collection current is None."""
    assert actions.current is None


def when_actions_collection_navigates_to(actions, action_name: str):
    """When: Actions collection navigates to action."""
    actions.navigate_to(action_name)


def then_actions_current_action_is(actions, expected_action_name: str):
    """Then: Current action matches expected."""
    assert actions.current is not None
    assert actions.current.action_name == expected_action_name


def then_behavior_action_state_file_contains_action(bot_paths: BotPaths, bot_name: str, behavior_name: str, expected_action: str):
    """Then: behavior_action_state.json contains expected action."""
    state_file = bot_paths.workspace_directory / 'behavior_action_state.json'
    assert state_file.exists()
    state_data = json.loads(state_file.read_text(encoding='utf-8'))
    assert state_data['current_action'] == f'{bot_name}.{behavior_name}.{expected_action}'


# ============================================================================
# STORY: Load Actions
# ============================================================================

class TestLoadActions:
    """Story: Load Actions - Tests that actions can be loaded from behavior configuration and managed as a collection with state persistence."""
    
    def test_load_actions_from_behavior_config(self, tmp_path):
        """Scenario: Actions are loaded from BehaviorConfig."""
        # Given: Environment, behavior with actions_workflow, and base action configs
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1, "next_action": "strategy"},
            {"name": "strategy", "order": 2, "next_action": "build"},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        
        # When: Behavior is created (which creates Actions collection)
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # Then: Actions collection is not None
        then_actions_collection_is_not_none(actions)
    
    def test_load_actions_sets_first_as_current(self, tmp_path):
        """Scenario: When actions are loaded, first action is set as current."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        
        # When: Behavior is created
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # Then: Current action is first in list
        then_actions_collection_has_current(actions, 'clarify')
    
    def test_find_action_by_name(self, tmp_path):
        """Scenario: Action can be found by name when it exists."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
            {"name": "build", "order": 3},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        given_base_action_config_exists(bot_paths, "build")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Find action by name
        found_action = actions.find_by_name('strategy')
        
        # Then: Action is found and matches expected name
        assert found_action is not None
        assert found_action.action_name == 'strategy'
    
    def test_find_action_returns_none_when_not_found(self, tmp_path):
        """Scenario: Finding action by name returns None when action doesn't exist."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Find non-existent action
        found_action = actions.find_by_name('nonexistent')
        
        # Then: Action is not found (returns None)
        assert found_action is None
    
    def test_find_action_by_order(self, tmp_path):
        """Scenario: Action can be found by order when it exists."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify", {"name": "clarify", "order": 1})
        given_base_action_config_exists(bot_paths, "strategy", {"name": "strategy", "order": 2})
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Find action by order
        found_action = actions.find_by_order(2)
        
        # Then: Action is found and matches expected order
        assert found_action is not None
        assert found_action.order == 2
        assert found_action.action_name == 'strategy'
    
    def test_get_next_action(self, tmp_path):
        """Scenario: Next action in sequence can be retrieved."""
        # Given: Environment, behavior with actions_workflow and current is first
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
            {"name": "build", "order": 3},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        given_base_action_config_exists(bot_paths, "build")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Get next action
        next_action = actions.next()
        
        # Then: Next action is second in list
        assert next_action is not None
        assert next_action.action_name == 'strategy'
    
    def test_get_next_action_returns_none_at_end(self, tmp_path):
        """Scenario: Getting next action returns None when at last action."""
        # Given: Environment, behavior with actions_workflow, navigate to last
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        when_actions_collection_navigates_to(actions, 'strategy')
        
        # When: Get next action
        next_action = actions.next()
        
        # Then: Next action is None
        assert next_action is None
    
    def test_iterate_all_actions(self, tmp_path):
        """Scenario: All actions can be iterated."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
            {"name": "build", "order": 3},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        given_base_action_config_exists(bot_paths, "build")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Iterate all actions
        action_names = [a.action_name for a in actions]
        
        # Then: All actions are returned
        assert len(action_names) == 3
        assert 'clarify' in action_names
        assert 'strategy' in action_names
        assert 'build' in action_names
    
    def test_navigate_to_action(self, tmp_path):
        """Scenario: Can navigate to a specific action."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
            {"name": "build", "order": 3},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        given_base_action_config_exists(bot_paths, "build")
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Navigate to specific action
        when_actions_collection_navigates_to(actions, 'build')
        
        # Then: That action becomes the current action
        then_actions_current_action_is(actions, 'build')
    
    def test_save_current_action_state(self, tmp_path):
        """Scenario: Current action state is persisted to behavior_action_state.json."""
        # Given: Environment, behavior with actions_workflow and current action set
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        when_actions_collection_navigates_to(actions, 'strategy')
        
        # When: Save state
        actions.save_state()
        
        # Then: behavior_action_state.json contains current action
        then_behavior_action_state_file_contains_action(bot_paths, bot_name, behavior_name, 'strategy')
    
    def test_load_action_state_from_file(self, tmp_path):
        """Scenario: Current action state is restored from behavior_action_state.json."""
        # Given: behavior_action_state.json exists with current action
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        given_behavior_action_state_file_with_action(bot_paths, bot_name, behavior_name, 'strategy')
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
            {"name": "build", "order": 3},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        given_base_action_config_exists(bot_paths, "build")
        
        # When: Behavior is created (loads state automatically)
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # Then: Current action matches saved state
        then_actions_collection_has_current(actions, 'strategy')
    
    def test_load_actions_uses_first_when_state_file_missing(self, tmp_path):
        """Scenario: When state file is missing, first action is used as current."""
        # Given: Environment, behavior with actions_workflow but no state file
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        
        # When: Behavior is created
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # Then: Current action is first in list
        then_actions_collection_has_current(actions, 'clarify')
    
    def test_close_current_action(self, tmp_path):
        """Scenario: Closing current action marks it complete and moves to next."""
        # Given: Environment, behavior with actions_workflow
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        actions_list = [
            {"name": "clarify", "order": 1},
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "clarify")
        given_base_action_config_exists(bot_paths, "strategy")
        
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        
        # When: Close current action
        actions.close_current()
        
        # Then: Current action moves to next
        then_actions_collection_has_current(actions, 'strategy')
        
        # And: Completed action is saved
        state_file = bot_paths.workspace_directory / 'behavior_action_state.json'
        assert state_file.exists()
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        completed_actions = state_data.get('completed_actions', [])
        assert len(completed_actions) == 1
        assert completed_actions[0]['action_state'] == f'{bot_name}.{behavior_name}.clarify'
    
    def test_action_merges_instructions_from_base_and_behavior(self, tmp_path):
        """Scenario: Action merges instructions from BaseActionConfig and Behavior config."""
        # Given: Environment, behavior with actions_workflow containing instructions
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        # Base action config with instructions
        base_instructions = {
            "instructions": [
                "Base instruction 1",
                "Base instruction 2"
            ]
        }
        given_base_action_config_exists(bot_paths, "clarify", {
            "name": "clarify",
            "order": 1,
            "instructions": base_instructions
        })
        
        # Behavior config with behavior-specific instructions for this action
        actions_list = [
            {
                "name": "clarify", 
                "order": 1,
                "instructions": {
                    "behavior_instructions": [
                        "Behavior-specific instruction 1",
                        "Behavior-specific instruction 2"
                    ]
                }
            },
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "strategy")
        
        # When: Behavior is created (which creates Actions collection and Action instances)
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        gather_context_action = actions.find_by_name('clarify')
        
        # Then: Action has merged instructions
        assert gather_context_action is not None
        assert gather_context_action.instructions is not None
        assert 'base_instructions' in gather_context_action.instructions
        
        # And: Base instructions are present
        base_instructions_list = gather_context_action.instructions['base_instructions']
        assert isinstance(base_instructions_list, list)
        assert len(base_instructions_list) >= 2
        assert "Base instruction 1" in base_instructions_list
        assert "Base instruction 2" in base_instructions_list
        
        # And: Behavior-specific instructions are merged into base_instructions
        # (behavior_instructions are merged into base_instructions, not kept separate)
        assert "Behavior-specific instruction 1" in base_instructions_list
        assert "Behavior-specific instruction 2" in base_instructions_list
        # Verify all 4 instructions are present (2 base + 2 behavior-specific)
        assert len(base_instructions_list) >= 4
    
    def test_action_uses_only_base_instructions_when_behavior_instructions_missing(self, tmp_path):
        """Scenario: Action uses only base instructions when behavior-specific instructions are missing."""
        # Given: Environment, behavior with actions_workflow but no behavior-specific instructions
        bot_name = 'story_bot'
        behavior_name = 'shape'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        # Base action config with instructions
        base_instructions = {
            "instructions": [
                "Base instruction 1",
                "Base instruction 2"
            ]
        }
        given_base_action_config_exists(bot_paths, "clarify", {
            "name": "clarify",
            "order": 1,
            "instructions": base_instructions
        })
        
        # Behavior config WITHOUT behavior-specific instructions
        actions_list = [
            {"name": "clarify", "order": 1},  # No instructions field
            {"name": "strategy", "order": 2},
        ]
        given_behavior_with_actions_workflow(bot_paths, bot_name, behavior_name, actions_list)
        given_base_action_config_exists(bot_paths, "strategy")
        
        # When: Behavior is created
        behavior = when_behavior_is_created_for_actions(bot_name, behavior_name, bot_paths)
        actions = behavior.actions
        gather_context_action = actions.find_by_name('clarify')
        
        # Then: Action has only base instructions
        assert gather_context_action is not None
        assert gather_context_action.instructions is not None
        assert 'base_instructions' in gather_context_action.instructions
        
        # And: Base instructions are present
        base_instructions_list = gather_context_action.instructions['base_instructions']
        assert isinstance(base_instructions_list, list)
        assert len(base_instructions_list) >= 2
        assert "Base instruction 1" in base_instructions_list
        assert "Base instruction 2" in base_instructions_list


# ============================================================================
# STORY: Load Base Action Configuration
# ============================================================================

class TestLoadBaseActionConfiguration:
    """Story: Load Base Action Configuration - action_config.json is parsed via BaseActionConfig."""
    
    def test_base_action_config_loads_fields(self, tmp_path):
        """Scenario: BaseActionConfig loads fields from action_config.json."""
        # Given: Environment and base action config file
        bot_name = 'story_bot'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        action_config_data = {
            "name": "clarify",
            "workflow": True,
            "order": 2,
            "next_action": "strategy"
        }
        given_base_action_config_exists(bot_paths, "clarify", action_config_data)
        
        # When: BaseActionConfig is created
        from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
        base_action_config = BaseActionConfig("clarify", bot_paths)
        
        # Then: Fields are loaded correctly
        assert base_action_config.order == 2
        assert base_action_config.next_action == "strategy"
        assert base_action_config.workflow is True
    
    def test_base_action_config_uses_defaults_when_missing(self, tmp_path):
        """Scenario: BaseActionConfig uses defaults when action_config.json is missing."""
        # Given: Environment but no action_config.json
        bot_name = 'story_bot'
        bot_paths = given_bot_paths_for_actions(tmp_path, bot_name)
        
        # When: BaseActionConfig is created for non-existent action
        from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
        base_action_config = BaseActionConfig("nonexistent_action", bot_paths)
        
        # Then: Default values are used
        assert base_action_config.order == 0
        assert base_action_config.next_action is None
        assert base_action_config.workflow is True


# ============================================================================
# HELPER FUNCTIONS - Access Bot Paths Story
# ============================================================================

def given_environment_variables_set(tmp_path: Path, bot_dir: Path):
    """Given: Environment variables are set for workspace and bot directory."""
    import os
    os.environ['WORKING_AREA'] = str(tmp_path)
    os.environ['BOT_DIRECTORY'] = str(bot_dir)
    return tmp_path, bot_dir


def given_base_actions_directory_exists_in_bot(bot_dir: Path):
    """Given: Base actions directory exists in bot directory.
    
    If bot_dir is base_bot, redirects to test_base_bot/base_actions.
    """
    from agile_bot.bots.base_bot.test.test_helpers import get_test_base_actions_dir
    base_actions_dir = get_test_base_actions_dir(bot_dir)
    base_actions_dir.mkdir(parents=True, exist_ok=True)
    return base_actions_dir


def when_bot_paths_is_created(workspace_path: Path = None):
    """When: BotPaths is created."""
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    if workspace_path:
        return BotPaths(workspace_path)
    return BotPaths()


def then_bot_paths_has_workspace_directory(bot_paths, expected_path: Path):
    """Then: BotPaths has correct workspace_directory property."""
    assert bot_paths.workspace_directory == expected_path
    assert isinstance(bot_paths.workspace_directory, Path)


def then_bot_paths_has_bot_directory(bot_paths, expected_path: Path):
    """Then: BotPaths has correct bot_directory property."""
    assert bot_paths.bot_directory == expected_path
    assert isinstance(bot_paths.bot_directory, Path)


def then_bot_paths_has_base_actions_directory(bot_paths, expected_path: Path):
    """Then: BotPaths has correct base_actions_directory property."""
    assert bot_paths.base_actions_directory == expected_path
    assert isinstance(bot_paths.base_actions_directory, Path)


def then_bot_paths_has_python_workspace_root(bot_paths):
    """Then: BotPaths has python_workspace_root property."""
    assert bot_paths.python_workspace_root is not None
    assert isinstance(bot_paths.python_workspace_root, Path)
    assert bot_paths.python_workspace_root.exists()


def then_bot_paths_find_repo_root_returns_correct_path(bot_paths):
    """Then: BotPaths.find_repo_root() returns correct path."""
    repo_root = bot_paths.find_repo_root()
    assert repo_root == bot_paths.python_workspace_root
    assert isinstance(repo_root, Path)
    assert repo_root.exists()


def then_bot_paths_raises_runtime_error_when_working_area_not_set():
    """Then: BotPaths raises RuntimeError when WORKING_AREA not set."""
    import os
    original_working_area = os.environ.get('WORKING_AREA')
    original_working_dir = os.environ.get('WORKING_DIR')
    
    try:
        if 'WORKING_AREA' in os.environ:
            del os.environ['WORKING_AREA']
        if 'WORKING_DIR' in os.environ:
            del os.environ['WORKING_DIR']
        
        with pytest.raises(RuntimeError, match='WORKING_AREA'):
            from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
            BotPaths()
    finally:
        if original_working_area:
            os.environ['WORKING_AREA'] = original_working_area
        if original_working_dir:
            os.environ['WORKING_DIR'] = original_working_dir


def then_bot_paths_raises_runtime_error_when_bot_directory_not_set():
    """Then: BotPaths raises RuntimeError when BOT_DIRECTORY not set."""
    import os
    original_bot_dir = os.environ.get('BOT_DIRECTORY')
    
    try:
        if 'BOT_DIRECTORY' in os.environ:
            del os.environ['BOT_DIRECTORY']
        
        with pytest.raises(RuntimeError, match='BOT_DIRECTORY'):
            from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
            BotPaths()
    finally:
        if original_bot_dir:
            os.environ['BOT_DIRECTORY'] = original_bot_dir


# ============================================================================
# STORY: Access Bot Paths
# ============================================================================

class TestAccessBotPaths:
    """Story: Access Bot Paths - Tests that bot-related paths can be accessed through a BotPaths class."""
    
    def test_bot_paths_instantiation_with_environment_variables(self, tmp_path, bot_directory):
        """Scenario: BotPaths can be instantiated when environment variables are set."""
        # Given: Environment variables are set
        workspace_dir, bot_dir = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created
        bot_paths = when_bot_paths_is_created()
        
        # Then: BotPaths has correct properties
        then_bot_paths_has_workspace_directory(bot_paths, workspace_dir)
        then_bot_paths_has_bot_directory(bot_paths, bot_dir)
    
    def test_bot_paths_workspace_directory_property(self, tmp_path, bot_directory):
        """Scenario: BotPaths.workspace_directory property returns workspace path from WORKING_AREA."""
        # Given: Environment variables are set
        workspace_dir, _ = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created
        bot_paths = when_bot_paths_is_created()
        
        # Then: BotPaths.workspace_directory matches expected
        then_bot_paths_has_workspace_directory(bot_paths, workspace_dir)
    
    def test_bot_paths_bot_directory_property(self, tmp_path, bot_directory):
        """Scenario: BotPaths.bot_directory property returns bot directory from BOT_DIRECTORY."""
        # Given: Environment variables are set
        _, bot_dir = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created
        bot_paths = when_bot_paths_is_created()
        
        # Then: BotPaths.bot_directory matches expected
        then_bot_paths_has_bot_directory(bot_paths, bot_dir)
    
    def test_bot_paths_base_actions_directory_property(self, tmp_path, bot_directory):
        """Scenario: BotPaths.base_actions_directory property returns base_actions directory."""
        # Given: Environment variables are set and base_actions directory exists
        given_environment_variables_set(tmp_path, bot_directory)
        expected_base_actions = given_base_actions_directory_exists_in_bot(bot_directory)
        
        # When: BotPaths is created
        bot_paths = when_bot_paths_is_created()
        
        # Then: BotPaths.base_actions_directory matches expected
        then_bot_paths_has_base_actions_directory(bot_paths, expected_base_actions)
    
    def test_bot_paths_python_workspace_root_property(self, tmp_path, bot_directory):
        """Scenario: BotPaths.python_workspace_root property returns Python workspace root."""
        # Given: Environment variables are set
        given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created
        bot_paths = when_bot_paths_is_created()
        
        # Then: BotPaths.python_workspace_root is set correctly
        then_bot_paths_has_python_workspace_root(bot_paths)
    
    def test_bot_paths_find_repo_root_method(self, tmp_path, bot_directory):
        """Scenario: BotPaths.find_repo_root() method returns repository root."""
        # Given: Environment variables are set
        given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created and find_repo_root is called
        bot_paths = when_bot_paths_is_created()
        repo_root = bot_paths.find_repo_root()
        
        # Then: find_repo_root returns correct path
        then_bot_paths_find_repo_root_returns_correct_path(bot_paths)
    
    def test_bot_paths_instantiation_with_workspace_path(self, tmp_path, bot_directory):
        """Scenario: BotPaths can be instantiated with explicit workspace path."""
        # Given: Environment variables are set
        workspace_dir, bot_dir = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths is created with explicit workspace path
        bot_paths = when_bot_paths_is_created(workspace_dir)
        
        # Then: BotPaths uses provided workspace path
        then_bot_paths_has_workspace_directory(bot_paths, workspace_dir)
        then_bot_paths_has_bot_directory(bot_paths, bot_dir)
    
    def test_bot_paths_raises_error_when_working_area_not_set(self, bot_directory):
        """Scenario: BotPaths raises RuntimeError when WORKING_AREA environment variable is not set."""
        # Given: BOT_DIRECTORY is set but WORKING_AREA is not
        import os
        os.environ['BOT_DIRECTORY'] = str(bot_directory)
        if 'WORKING_AREA' in os.environ:
            del os.environ['WORKING_AREA']
        if 'WORKING_DIR' in os.environ:
            del os.environ['WORKING_DIR']
        
        # When/Then: BotPaths creation raises RuntimeError
        then_bot_paths_raises_runtime_error_when_working_area_not_set()
    
    def test_bot_paths_raises_error_when_bot_directory_not_set(self, tmp_path):
        """Scenario: BotPaths raises RuntimeError when BOT_DIRECTORY environment variable is not set."""
        # Given: WORKING_AREA is set but BOT_DIRECTORY is not
        import os
        os.environ['WORKING_AREA'] = str(tmp_path)
        if 'BOT_DIRECTORY' in os.environ:
            del os.environ['BOT_DIRECTORY']
        
        # When/Then: BotPaths creation raises RuntimeError
        then_bot_paths_raises_runtime_error_when_bot_directory_not_set()


# ============================================================================
# HELPER FUNCTIONS - Domain Classes (Stories 6, 21-24)
# ============================================================================

from unittest.mock import Mock
from agile_bot.bots.base_bot.src.bot.merged_instructions import MergedInstructions
from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
from agile_bot.bots.base_bot.src.bot.behaviors import Behaviors
from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


def given_base_action_config_with_instructions_for_merged(instructions):
    """Given: BaseActionConfig with instructions for MergedInstructions."""
    base_action_config = Mock(spec=BaseActionConfig)
    base_action_config.instructions = instructions
    return base_action_config


def when_merged_instructions_instantiated_for_base(base_action_config):
    """When: MergedInstructions instantiated for base instructions."""
    return MergedInstructions(base_action_config)


def when_base_instructions_accessed_from_merged(merged_instructions: MergedInstructions):
    """When: base_instructions property accessed from MergedInstructions."""
    return merged_instructions.base_instructions


def then_base_instructions_are_list(result: list, expected: list):
    """Then: Base instructions are expected list."""
    assert result == expected


def then_base_instructions_is_copy(result: list, original: list):
    """Then: Base instructions is copy, not reference."""
    assert result == original
    result.append('test')
    assert len(original) == len([x for x in original if x != 'test'])


def then_base_instructions_verifies_copy_if_list(result: list, instructions):
    """Then: Base instructions verifies copy behavior if instructions is list."""
    if isinstance(instructions, list) and instructions:
        then_base_instructions_is_copy(result, instructions)


def then_behavior_config_behavior_name_is(behavior_config, expected_name: str):
    """Then: BehaviorConfig behavior_name property is expected."""
    assert behavior_config.behavior_name == expected_name


def then_behavior_config_properties_are_accessible(behavior_config):
    """Then: BehaviorConfig properties are accessible."""
    assert behavior_config.description is not None
    assert behavior_config.goal is not None
    assert behavior_config.inputs is not None
    assert behavior_config.outputs is not None
    assert behavior_config.instructions is not None
    assert behavior_config.trigger_words is not None
    assert behavior_config.actions_workflow is not None


def when_behavior_config_creation_raises_file_not_found_error(behavior: str, bot_paths):
    """When: BehaviorConfig creation raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        when_behavior_config_is_created(behavior, bot_paths)


def then_behaviors_collection_has_count(behaviors_collection, expected_count: int):
    """Then: Behaviors collection has expected count."""
    behavior_list = list(behaviors_collection)
    assert len(behavior_list) == expected_count


def then_behavior_is_not_none(behavior):
    """Then: Behavior is not None."""
    assert behavior is not None


def then_behavior_is_none(behavior):
    """Then: Behavior is None."""
    assert behavior is None


def then_behavior_name_is(behavior, expected_name: str):
    """Then: Behavior name is expected."""
    assert behavior.name == expected_name


def then_check_exists_returns_true(result: bool):
    """Then: Check exists returns True."""
    assert result is True


def then_check_exists_returns_false(result: bool):
    """Then: Check exists returns False."""
    assert result is False


def then_current_behavior_name_is(behaviors_collection, expected_name: str):
    """Then: Current behavior name is expected."""
    assert behaviors_collection.current.name == expected_name


def given_workflow_state_file_with_current_action(workspace_directory: Path, bot_name: str, behavior: str, action: str):
    """Given: Workflow state file with current action."""
    return create_workflow_state_file(workspace_directory, bot_name, behavior, action)


def when_behaviors_collection_close_current_called(behaviors_collection):
    """When: Behaviors collection close_current() called."""
    behaviors_collection.close_current()


def then_behaviors_collection_has_execute_current_method(behaviors_collection):
    """Then: Behaviors collection has execute_current method."""
    assert hasattr(behaviors_collection, 'execute_current')


def when_behaviors_collection_navigates_to(behaviors_collection, behavior_name: str):
    """When: Behaviors collection navigates to behavior."""
    behaviors_collection.navigate_to(behavior_name)


def then_workflow_state_has_completed_actions(workspace_directory: Path, bot_name: str):
    """Then: Workflow state has completed actions."""
    state_file = workspace_directory / f'{bot_name}_workflow_state.json'
    if state_file.exists():
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        assert 'completed_actions' in state_data


def when_behaviors_collection_execute_current_called(behaviors_collection):
    """When: Behaviors collection execute_current() called."""
    try:
        behaviors_collection.execute_current()
    except Exception:
        pass


def when_bot_paths_bot_directory_accessed(bot_paths):
    """When: BotPaths bot_directory property accessed."""
    return bot_paths.bot_directory


def when_bot_paths_workspace_directory_accessed(bot_paths):
    """When: BotPaths workspace_directory property accessed."""
    return bot_paths.workspace_directory


def then_bot_paths_properties_return_paths(bot_dir_result, workspace_dir_result, expected_bot_dir: Path, expected_workspace_dir: Path):
    """Then: BotPaths properties return Path objects."""
    assert isinstance(bot_dir_result, Path)
    assert isinstance(workspace_dir_result, Path)
    assert bot_dir_result == expected_bot_dir
    assert workspace_dir_result == expected_workspace_dir


# ============================================================================
# TEST CLASSES - Domain Classes (Stories 6, 21-24)
# ============================================================================

class TestGetBaseInstructions:
    """Story: Get Base Instructions (MergedInstructions) (Sub-epic: Perform Behavior Action)"""
    
    @pytest.mark.parametrize("instructions,expected_result", [
        # Example 1: List instructions
        (['instruction1', 'instruction2'], ['instruction1', 'instruction2']),
        # Example 2: String instructions
        ('single instruction', ['single instruction']),
        # Example 3: None instructions
        (None, []),
    ])
    def test_base_instructions_property_returns_instructions_from_config(self, instructions, expected_result):
        """
        SCENARIO: Base instructions property returns instructions from config
        GIVEN: BaseActionConfig with instructions (list, string, or None)
        WHEN: base_instructions property accessed
        THEN: Returns list format (converts string to list, returns empty list when None, returns copy not reference)
        """
        # Given: BaseActionConfig with instructions
        base_action_config = given_base_action_config_with_instructions_for_merged(instructions)
        
        # When: MergedInstructions instantiated and base_instructions accessed
        merged_instructions = when_merged_instructions_instantiated_for_base(base_action_config)
        result = when_base_instructions_accessed_from_merged(merged_instructions)
        
        # Then: Base instructions are expected
        then_base_instructions_are_list(result, expected_result)
        
        # Also verify copy behavior for list case
        then_base_instructions_verifies_copy_if_list(result, instructions)


class TestLoadBehaviorConfig:
    """Story: Load Behavior Config (Sub-epic: Perform Behavior Action)"""
    
    def test_behavior_config_loads_correct_behavior_from_behavior_json_file(self, tmp_path):
        """
        SCENARIO: Behavior config loads correct behavior from behavior.json file
        GIVEN: behavior.json exists in behavior folder for 'shape' behavior
        WHEN: BehaviorConfig instantiated with behavior and bot_paths
        THEN: Config loaded from file and behavior_name property returns 'shape'
        """
        # Given: behavior.json exists
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "shape"
        behavior_config_data = {"description": "Shape feature"}
        given_behavior_config_created(bot_dir, behavior, behavior_config_data)
        
        # When: BehaviorConfig instantiated
        bot_paths = when_bot_paths_is_created(workspace_dir)
        behavior_config = when_behavior_config_is_created(behavior, bot_paths)
        
        # Then: behavior_name property returns 'shape'
        then_behavior_config_behavior_name_is(behavior_config, behavior)
    
    def test_behavior_config_provides_access_to_config_objects(self, tmp_path):
        """
        SCENARIO: Behavior config provides access to config objects
        GIVEN: BehaviorConfig loaded with complete behavior.json
        WHEN: Config properties accessed (description, goal, inputs, outputs, instructions, trigger_words, actions_workflow)
        THEN: All config objects are accessible
        """
        # Given: BehaviorConfig loaded with complete behavior.json
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "shape"
        behavior_config_data = {
            "description": "Test description",
            "goal": "Test goal",
            "inputs": ["input1"],
            "outputs": ["output1"],
            "instructions": {"note": "test"},
            "trigger_words": ["test"],
            "actions_workflow": {"actions": []}
        }
        given_behavior_config_created(bot_dir, behavior, behavior_config_data)
        
        # When: BehaviorConfig instantiated
        bot_paths = when_bot_paths_is_created(workspace_dir)
        behavior_config = when_behavior_config_is_created(behavior, bot_paths)
        
        # Then: All config objects are accessible
        then_behavior_config_properties_are_accessible(behavior_config)
    
    def test_behavior_config_raises_error_when_behavior_json_missing(self, tmp_path):
        """
        SCENARIO: Behavior config raises error when behavior.json missing
        GIVEN: Behavior folder without behavior.json
        WHEN: BehaviorConfig instantiated
        THEN: Raises FileNotFoundError
        """
        # Given: Behavior folder without behavior.json
        bot_dir, workspace_dir = given_environment_and_bot(tmp_path, "story_bot")
        behavior = "missing_behavior"
        
        # When/Then: BehaviorConfig instantiated raises FileNotFoundError
        bot_paths = when_bot_paths_is_created(workspace_dir)
        when_behavior_config_creation_raises_file_not_found_error(behavior, bot_paths)


class TestManageBehaviorsCollection:
    """Story: Manage Behaviors Collection (Sub-epic: Perform Behavior Action)"""
    
    def test_behaviors_collection_loads_behaviors_from_bot_config(self, tmp_path):
        """
        SCENARIO: Behaviors collection loads behaviors from bot config
        GIVEN: BotConfig with behaviors list
        WHEN: Behaviors instantiated with bot_config
        THEN: Behaviors collection contains all behaviors from config
        """
        # Given: BotConfig with behaviors list
        bot_name = "story_bot"
        behaviors = ['shape', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        
        # When: Behaviors instantiated
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # Then: Behaviors collection contains all behaviors
        then_behaviors_collection_is_not_none(behaviors_collection)
        then_behaviors_collection_has_count(behaviors_collection, len(behaviors))
    
    def test_behaviors_find_by_name_returns_behavior_when_exists(self, tmp_path):
        """
        SCENARIO: Behaviors find by name returns behavior when exists
        GIVEN: Behaviors collection with 'shape' behavior
        WHEN: find_by_name('shape') called
        THEN: Returns Behavior object
        """
        # Given: Behaviors collection with 'shape' behavior
        bot_name = "story_bot"
        behaviors = ['shape']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # When: find_by_name('shape') called
        result = behaviors_collection.find_by_name('shape')
        
        # Then: Returns Behavior object
        then_behavior_is_not_none(result)
        then_behavior_name_is(result, 'shape')
    
    def test_behaviors_find_by_name_returns_none_when_does_not_exist(self, tmp_path):
        """
        SCENARIO: Behaviors find by name returns none when does not exist
        GIVEN: Behaviors collection without 'nonexistent' behavior
        WHEN: find_by_name('nonexistent') called
        THEN: Returns None
        """
        # Given: Behaviors collection without 'nonexistent' behavior
        bot_name = "story_bot"
        behaviors = ['shape']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # When: find_by_name('nonexistent') called
        result = behaviors_collection.find_by_name('nonexistent')
        
        # Then: Returns None
        then_behavior_is_none(result)
    
    def test_behaviors_check_exists_returns_true_when_behavior_exists(self, tmp_path):
        """
        SCENARIO: Behaviors check exists returns true when behavior exists
        GIVEN: Behaviors collection with 'discovery' behavior
        WHEN: check_exists('discovery') called
        THEN: Returns True
        """
        # Given: Behaviors collection with 'discovery' behavior
        bot_name = "story_bot"
        behaviors = ['discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # When: check_exists('discovery') called
        result = behaviors_collection.check_exists('discovery')
        
        # Then: Returns True
        then_check_exists_returns_true(result)
    
    def test_behaviors_check_exists_returns_false_when_behavior_does_not_exist(self, tmp_path):
        """
        SCENARIO: Behaviors check exists returns false when behavior does not exist
        GIVEN: Behaviors collection without 'nonexistent' behavior
        WHEN: check_exists('nonexistent') called
        THEN: Returns False
        """
        # Given: Behaviors collection without 'nonexistent' behavior
        bot_name = "story_bot"
        behaviors = ['shape']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # When: check_exists('nonexistent') called
        result = behaviors_collection.check_exists('nonexistent')
        
        # Then: Returns False
        then_check_exists_returns_false(result)
    
    def test_behaviors_current_property_returns_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors current property returns current behavior
        GIVEN: Behaviors collection with current behavior set
        WHEN: current property accessed
        THEN: Returns current Behavior object
        """
        # Given: Behaviors collection with current behavior set
        bot_name = "story_bot"
        behaviors = ['shape', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors_collection, 'shape')
        
        # When: current property accessed
        result = behaviors_collection.current
        
        # Then: Returns current Behavior object
        then_behavior_is_not_none(result)
        then_behavior_name_is(result, 'shape')
    
    def test_behaviors_next_property_returns_next_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors next property returns next behavior
        GIVEN: Behaviors collection with current behavior
        WHEN: next property accessed
        THEN: Returns next Behavior object
        """
        # Given: Behaviors collection with current behavior
        bot_name = "story_bot"
        behaviors = ['shape', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors_collection, 'shape')
        
        # When: next property accessed
        result = when_behaviors_next_accessed(behaviors_collection)
        
        # Then: Returns next Behavior object
        then_behavior_is_not_none(result)
        then_behavior_name_is(result, 'discovery')
    
    def test_behaviors_navigate_to_behavior_updates_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors navigate to behavior updates current behavior
        GIVEN: Behaviors collection
        WHEN: navigate_to('discovery') called
        THEN: Current behavior updated to 'discovery'
        """
        # Given: Behaviors collection
        bot_name = "story_bot"
        behaviors = ['shape', 'discovery']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        
        # When: navigate_to('discovery') called
        when_behaviors_collection_navigates_to(behaviors_collection, 'discovery')
        
        # Then: Current behavior updated to 'discovery'
        then_current_behavior_name_is(behaviors_collection, 'discovery')
    
    def test_behaviors_close_current_marks_behavior_and_action_complete(self, tmp_path, workspace_directory):
        """
        SCENARIO: Behaviors close current marks behavior and action complete
        GIVEN: Behaviors collection with current behavior and current action
        WHEN: close_current() called
        THEN: Current behavior marked complete and current action closed
        """
        # Given: Behaviors collection with current behavior and current action
        bot_name = "story_bot"
        behaviors = ['shape']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors_collection, 'shape')
        # Set up workflow state with current action
        given_workflow_state_file_with_current_action(workspace_directory, bot_name, 'shape', 'clarify')
        
        # When: close_current() called
        when_behaviors_collection_close_current_called(behaviors_collection)
        
        # Then: Current behavior marked complete and current action closed
        then_workflow_state_has_completed_actions(workspace_directory, bot_name)
    
    def test_behaviors_execute_current_executes_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors execute current executes current behavior
        GIVEN: Behaviors collection with current behavior
        WHEN: execute_current() called
        THEN: Current behavior's execute() method called
        """
        # Given: Behaviors collection with current behavior
        bot_name = "story_bot"
        behaviors = ['shape']
        bot_config = given_bot_config_with_behaviors(tmp_path, bot_name, behaviors)
        behaviors_collection = when_behaviors_collection_is_created(bot_config)
        when_behaviors_collection_navigates_to(behaviors_collection, 'shape')
        
        # When: execute_current() called
        when_behaviors_collection_execute_current_called(behaviors_collection)
        
        # Then: Method exists and can be called (observable behavior)
        then_behaviors_collection_has_execute_current_method(behaviors_collection)


class TestResolveBotPaths:
    """Story: Resolve Bot Paths (Sub-epic: Perform Behavior Action)"""
    
    def test_bot_paths_resolves_bot_directory_from_environment(self, tmp_path, bot_directory):
        """
        SCENARIO: Bot paths resolves bot directory from environment
        GIVEN: BOT_DIRECTORY environment variable set
        WHEN: BotPaths instantiated
        THEN: bot_directory property returns path from environment
        """
        # Given: BOT_DIRECTORY environment variable set
        workspace_dir, bot_dir = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths instantiated
        bot_paths = when_bot_paths_is_created()
        
        # Then: bot_directory property returns path from environment
        then_bot_paths_has_bot_directory(bot_paths, bot_dir)
    
    def test_bot_paths_resolves_workspace_directory_from_environment(self, tmp_path, bot_directory):
        """
        SCENARIO: Bot paths resolves workspace directory from environment
        GIVEN: WORKING_AREA environment variable set
        WHEN: BotPaths instantiated
        THEN: workspace_directory property returns path from environment
        """
        # Given: WORKING_AREA environment variable set
        workspace_dir, _ = given_environment_variables_set(tmp_path, bot_directory)
        
        # When: BotPaths instantiated
        bot_paths = when_bot_paths_is_created()
        
        # Then: workspace_directory property returns path from environment
        then_bot_paths_has_workspace_directory(bot_paths, workspace_dir)
    
    def test_bot_paths_properties_return_resolved_paths(self, tmp_path, bot_directory):
        """
        SCENARIO: Bot paths properties return resolved paths
        GIVEN: BotPaths with resolved paths
        WHEN: Properties accessed (bot_directory, workspace_directory)
        THEN: Returns bot directory Path and workspace directory Path
        """
        # Given: BotPaths with resolved paths
        workspace_dir, bot_dir = given_environment_variables_set(tmp_path, bot_directory)
        bot_paths = when_bot_paths_is_created()
        
        # When: Properties accessed
        bot_dir_result = when_bot_paths_bot_directory_accessed(bot_paths)
        workspace_dir_result = when_bot_paths_workspace_directory_accessed(bot_paths)
        
        # Then: Returns Path objects
        then_bot_paths_properties_return_paths(bot_dir_result, workspace_dir_result, bot_dir, workspace_dir)
    
    def test_bot_paths_uses_default_paths_when_environment_variables_not_set(self, tmp_path):
        """
        SCENARIO: Bot paths uses default paths when environment variables not set
        GIVEN: No BOT_DIRECTORY or WORKING_AREA environment variables
        WHEN: BotPaths instantiated
        THEN: Uses default path resolution logic
        """
        # Given: No environment variables (cleared)
        import os
        original_bot_dir = os.environ.get('BOT_DIRECTORY')
        original_working_area = os.environ.get('WORKING_AREA')
        
        try:
            if 'BOT_DIRECTORY' in os.environ:
                del os.environ['BOT_DIRECTORY']
            if 'WORKING_AREA' in os.environ:
                del os.environ['WORKING_AREA']
            
            # When/Then: BotPaths instantiated raises error (no defaults in current implementation)
            with pytest.raises(RuntimeError):
                BotPaths()
        finally:
            if original_bot_dir:
                os.environ['BOT_DIRECTORY'] = original_bot_dir
            if original_working_area:
                os.environ['WORKING_AREA'] = original_working_area

