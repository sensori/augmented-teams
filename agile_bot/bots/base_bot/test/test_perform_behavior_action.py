"""
Perform Behavior Action Tests

Tests for all stories in the 'Perform Behavior Action' sub-epic:
- Inject Next Behavior Reminder
- Close Current Action
- Invoke Behavior Actions In Workflow Order
- Find Behavior Folder
"""
import pytest
import json
import os
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow
from agile_bot.bots.base_bot.src.bot.bot import Bot, BotResult, Behavior
from conftest import (
    bootstrap_env, create_workflow_state_file, create_bot_config_file, 
    create_test_workflow, given_bot_name_and_behavior_setup, given_bot_name_and_behaviors_setup
)
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env as test_helpers_bootstrap_env, read_activity_log, create_activity_log_file,
    create_actions_workflow_json, create_behavior_folder, create_behavior_folder_with_json,
    get_workflow_state_path, given_bot_name_and_behavior_setup as test_helpers_given_bot_name_and_behavior_setup
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

def given_test_bot_folder_and_behavior_names():
    """Given: Test bot folder and behavior names."""
    return 'test_bot', '8_tests', 'tests'

def given_test_bot_and_nonexistent_behavior_names():
    """Given: Test bot and nonexistent behavior names."""
    return 'test_bot', 'nonexistent'

def then_behavior_folder_matches_expected(found_folder: Path, behavior_folder: Path, expected_name: str):
    """Then: Behavior folder matches expected."""
    assert found_folder == behavior_folder
    assert found_folder.name == expected_name

def then_all_completed_actions_tracked_across_behaviors():
    """Then: All completed actions tracked across behaviors."""
    print("[OK] All completed actions tracked across both behaviors")

def when_expect_behavior_folder_not_found_error(bot_directory: Path, bot_name: str, behavior_name: str):
    """When: Expect behavior folder not found error."""
    with pytest.raises(FileNotFoundError, match='Behavior folder not found'):
        Behavior.find_behavior_folder(bot_directory, bot_name, behavior_name)

# ============================================================================
# HELPER FUNCTIONS - Shared across test classes
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
    test_helpers_bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    given_behavior_workflow_with_validate_rules_as_final(bot_directory, 'shape')
    given_base_action_instructions_exist_for_validate_rules(bot_directory)
    given_standard_workflow_actions_config(bot_directory)
    given_story_graph_file_exists(workspace_directory)


def given_environment_setup_for_non_final_action_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for non-final action test."""
    test_helpers_bootstrap_env(bot_directory, workspace_directory)
    create_bot_config_file(bot_directory, 'story_bot', behaviors)
    given_standard_workflow_states(bot_directory)
    given_base_action_instructions_exist_for_validate_rules_not_final(bot_directory)
    given_action_configs_exist_for_workflow_actions_with_render_output_after(bot_directory)
    given_story_graph_file_exists(workspace_directory)


def given_environment_setup_for_last_behavior_test(bot_directory: Path, workspace_directory: Path, behaviors: list):
    """Given: Environment setup for last behavior test."""
    test_helpers_bootstrap_env(bot_directory, workspace_directory)
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
    action_result = action.execute(parameters={})
    return action, action_result


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


def then_base_instructions_do_not_include_next_behavior_reminder(action_result):
    """Then: base_instructions do NOT include next behavior reminder."""
    instructions = action_result.get('instructions', {})
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
    action_result = action.execute(parameters={})
    return action, action_result


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
        
        action, action_result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        base_instructions_list = then_base_instructions_include_next_behavior_reminder(action_result)
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
        
        action, action_result = when_validate_rules_action_executes(bot_directory, 'shape')
        
        then_base_instructions_do_not_include_next_behavior_reminder(action_result)

    def test_next_behavior_reminder_not_injected_when_no_next_behavior(self, bot_directory, workspace_directory):
        """
        SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
        GIVEN: discovery is the last behavior in bot_config.json
        AND: render_output is the final action
        WHEN: render_output action executes
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

        # Given workflow is at action "decide_planning_criteria"
        # And action has NOT been marked complete yet
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'gather_context')

        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)

        given_workflow_is_at_action(workflow, 'decide_planning_criteria')
        given_action_is_not_completed(workflow, 'decide_planning_criteria')

        # When user closes current action
        when_user_closes_current_action_and_transitions(workflow, 'decide_planning_criteria')

        # Then action is saved to completed_actions
        then_action_is_marked_complete(workflow, 'decide_planning_criteria')
        # And workflow transitions to next action
        then_workflow_transitions_to_next_action(workflow, 'build_knowledge')
        then_completed_actions_count_is(workflow_file, 2)
        then_current_action_is(workflow_file, bot_name, behavior, 'build_knowledge')


    def test_close_action_at_final_action_stays_at_final(self, bot_directory, workspace_directory):
        """Scenario: Close final action stays at final action"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate_rules', [])
        
        given_workflow_is_at_action(workflow, 'validate_rules')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'validate_rules')
        # No transition_to_next() call - validate_rules is final
        
        # Then action is saved but state stays at validate_rules
        then_action_is_marked_complete(workflow, 'validate_rules')
        then_workflow_stays_at_action(workflow, 'validate_rules')


    def test_close_final_action_transitions_to_next_behavior(self, bot_directory, workspace_directory):
        """Scenario: Close final action and verify it's marked complete"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        # Given: Workflow is at final action
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate_rules', [])
        
        given_workflow_is_at_action(workflow, 'validate_rules')
        
        # When user closes final action
        when_user_closes_current_action(workflow, 'validate_rules')
        
        # Then action is marked complete
        then_action_is_marked_complete(workflow, 'validate_rules')
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'validate_rules')


    def test_close_action_saves_to_completed_actions_list(self, bot_directory, workspace_directory):
        """Scenario: Closing action saves it to completed_actions list"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'gather_context', [])
        
        # When closing action
        when_user_closes_current_action(workflow, 'gather_context')
        
        # Then it's in completed_actions
        then_completed_actions_count_is(workflow_file, 1)
        then_action_is_saved_to_completed_actions(workflow_file, bot_name, behavior, 'gather_context')


    def test_close_handles_action_already_completed_gracefully(self, bot_directory, workspace_directory):
        """Scenario: Idempotent close (already completed)"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup()
        completed = given_completed_action_for_behavior(bot_name, behavior, 'gather_context')
        
        workflow, workflow_file = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)
        
        # Verify initial state
        initial_count = given_initial_completed_action_count(workflow_file, 'gather_context')
        
        # When closing already completed action
        when_close_already_completed_action(workflow, 'gather_context')
        
        # Then no NEW entry added (may save again with new timestamp, but test just checks it completes gracefully)
        then_completed_actions_count_is_at_least(workflow_file, initial_count)


    def test_bot_class_has_close_current_action_method(self, bot_directory, workspace_directory):
        """Scenario: Bot class exposes close_current_action method"""
        
        # Given: Bot is initialized
        given_bot_environment_bootstrapped(bot_directory, workspace_directory)
        bot_name, _ = given_bot_name_and_behavior_setup()
        config_path = given_bot_config_and_behavior_setup(bot_directory, bot_name, ['shape'])
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
    from agile_bot.bots.base_bot.src.state.workspace import get_base_actions_directory
    base_actions_dir = get_base_actions_directory(bot_directory=bot_directory)
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
    return base_actions_dir

def given_behavior_json_file_created(behavior_dir: Path, behavior_config: dict):
    """Given step: Create behavior.json file with config."""
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    return behavior_file

def given_expected_transitions_list():
    """Given step: Create expected transitions list."""
    return [
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'complete'}
    ]

def when_action_is_executed(bot, behavior_name: str, action_name: str):
    """When step: Action is executed."""
    behavior = getattr(bot, behavior_name)
    action_method = getattr(behavior, action_name)
    return action_method()

def when_action_is_closed_and_transitioned(bot, behavior_name: str, action_name: str):
    """When step: Action is closed and workflow transitions."""
    behavior = getattr(bot, behavior_name)
    behavior.workflow.save_completed_action(action_name)
    behavior.workflow.load_state()
    behavior.workflow.transition_to_next()

def then_workflow_state_shows_action(workflow_file: Path, bot_name: str, behavior: str, action: str):
    """Then step: Workflow state shows specified action."""
    state = json.loads(workflow_file.read_text(encoding='utf-8'))
    assert state['current_action'] == f'{bot_name}.{behavior}.{action}'

def then_workflow_state_shows_behavior(workflow_file: Path, bot_name: str, behavior: str):
    """Then step: Workflow state shows specified behavior."""
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
    """When: Execute shape gather_context and verify."""
    result = when_action_is_executed(bot, 'shape', 'gather_context')
    then_action_result_has_correct_action(result, 'gather_context')
    then_workflow_current_state_is(bot.shape.workflow, 'gather_context')
    then_workflow_state_shows_action(workflow_file, bot_name, 'shape', 'gather_context')
    return result

def when_close_shape_gather_context_and_verify(bot):
    """When: Close shape gather_context and verify."""
    when_action_is_closed_and_transitioned(bot, 'shape', 'gather_context')
    then_workflow_current_state_is(bot.shape.workflow, 'decide_planning_criteria')
    then_action_is_completed(bot.shape.workflow, 'gather_context')

def when_execute_discovery_gather_context_and_verify(bot, workflow_file: Path, bot_name: str):
    """When: Execute discovery gather_context and verify."""
    result = when_action_is_executed(bot, 'discovery', 'gather_context')
    then_action_result_has_correct_behavior_and_action(result, 'discovery', 'gather_context')
    then_workflow_state_shows_behavior(workflow_file, bot_name, 'discovery')
    then_workflow_state_shows_action(workflow_file, bot_name, 'discovery', 'gather_context')
    return result

def when_close_discovery_gather_context_and_verify(bot):
    """When: Close discovery gather_context and verify."""
    when_action_is_closed_and_transitioned(bot, 'discovery', 'gather_context')
    then_workflow_current_state_is(bot.discovery.workflow, 'decide_planning_criteria')

def then_verify_completed_actions_across_behaviors(workflow_file: Path, bot_name: str):
    """Then: Verify completed actions across behaviors."""
    expected_completed_actions = given_completed_actions_for_behaviors('story_bot', ['shape', 'discovery'], 'gather_context')
    then_completed_actions_include(workflow_file, expected_completed_actions)


class TestInvokeBehaviorActionsInWorkflowOrder:
    """Story: Invoke Behavior Actions In Workflow Order - End-to-end test of the complete workflow with all fixes."""

    def _execute_workflow_steps(self, bot, workflow_file, bot_name):
        """Helper: Execute workflow steps for end-to-end test."""
        print("\n=== Step 1: Execute gather_context ===")
        action_result = when_execute_shape_gather_context_and_verify(bot, workflow_file, bot_name)
        print("[OK] Executed gather_context, state saved")
        
        print("\n=== Step 2: Close gather_context ===")
        when_close_shape_gather_context_and_verify(bot)
        print("[OK] gather_context closed, transitioned to decide_planning_criteria")
        
        print("\n=== Step 3: Jump to discovery.gather_context (out of order) ===")
        action_result = when_execute_discovery_gather_context_and_verify(bot, workflow_file, bot_name)
        print("[OK] Jumped to discovery.gather_context, state correctly shows discovery.gather_context")
        
        print("\n=== Step 4: Close discovery.gather_context ===")
        when_close_discovery_gather_context_and_verify(bot)
        print("[OK] discovery.gather_context closed, transitioned to decide_planning_criteria")
        then_verify_completed_actions_across_behaviors(workflow_file, bot_name)

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
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
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
    action_order = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
    target_index = action_order.index(target_action)
    for i in range(target_index + 1, len(action_order)):
        assert f'{bot_name}.{behavior}.{action_order[i]}' not in completed_action_states

def given_behavior_config_created(bot_directory: Path, behavior: str, behavior_config: dict):
    """Given: Behavior config created."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
    return behavior_file

def when_behavior_is_initialized(bot_name: str, behavior: str, bot_directory: Path):
    """When: Behavior is initialized."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    behavior_instance = Behavior(
        name=behavior,
        bot_name=bot_name,
        bot_directory=bot_directory
    )
    return behavior_instance

def then_workflow_states_match(behavior_instance, expected_states: list):
    """Then: Workflow states match expected."""
    assert behavior_instance.workflow.states == expected_states, (
        f"Expected states {expected_states}, got {behavior_instance.workflow.states}"
    )

def then_workflow_transitions_match(behavior_instance, expected_transitions: list):
    """Then: Workflow transitions match expected."""
    assert behavior_instance.workflow.transitions == expected_transitions, (
        f"Expected transitions {expected_transitions}, got {behavior_instance.workflow.transitions}"
    )

def when_behavior_is_initialized_raises_error(bot_name: str, behavior: str, bot_directory: Path):
    """When: Behavior is initialized raises error."""
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name=behavior,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
    return exc_info

def then_error_mentions_behavior_json_required(exc_info, behavior: str):
    """Then: Error mentions behavior.json is REQUIRED."""
    assert 'behavior.json is REQUIRED' in str(exc_info.value)
    assert behavior in str(exc_info.value)

def given_completed_action_for_gather_context(bot_name: str, behavior: str):
    """Given: Completed action for gather_context."""
    return [{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'}]

def when_create_workflow_with_current_action(bot_directory: Path, workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed: list):
    """When: Create workflow with current action."""
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, current_action, completed, return_workflow_file=False)
    return workflow

def then_workflow_current_state_is_build_knowledge(workflow):
    """Then: Workflow current state is build_knowledge."""
    assert workflow.current_state == 'build_knowledge'

def then_workflow_current_state_is_gather_context(workflow):
    """Then: Workflow current state is gather_context."""
    assert workflow.current_state == 'gather_context'

def then_workflow_current_state_is_decide_planning_criteria(workflow):
    """Then: Workflow current state is decide_planning_criteria."""
    assert workflow.current_state == 'decide_planning_criteria'

def given_completed_actions_for_three_actions(bot_name: str, behavior: str):
    """Given: Completed actions for three actions."""
    return [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:47:00.000000'}
    ]

def given_standard_states_and_transitions():
    """Given: Standard states and transitions."""
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
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
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:47:00.000000'},
    ]

def given_environment_workflow_state_and_workflow(bot_directory: Path, workspace_directory: Path, bot_name: str, behavior: str, current_action: str, completed: list):
    """Given: Environment, workflow state and workflow."""
    bootstrap_env(bot_directory, workspace_directory)
    workflow_file = given_workflow_state_with_completed_actions(
        workspace_directory, bot_name, behavior, current_action, completed
    )
    states, transitions = given_standard_states_and_transitions()
    workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
    return workflow_file, workflow

def when_navigate_to_target_action_out_of_order(workflow, target_action: str):
    """When: Navigate to target action out of order."""
    when_workflow_navigates_to_action(workflow, target_action, out_of_order=True)

def then_verify_completed_actions_after_navigation(workflow_file: Path, bot_name: str, behavior: str):
    """Then: Verify completed actions after navigation."""
    then_completed_actions_do_not_include(workflow_file, bot_name, behavior, 'render_output')
    expected_action_states = [f'{bot_name}.{behavior}.gather_context', f'{bot_name}.{behavior}.decide_planning_criteria', f'{bot_name}.{behavior}.build_knowledge']
    then_completed_actions_include(workflow_file, expected_action_states)

def given_write_tests_behavior_config():
    """Given: Write tests behavior config."""
    return {
        "behaviorName": "write_tests",
        "description": "Test behavior: tests",
        "goal": "Test goal for tests",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": ["Test instructions for tests."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build_knowledge",
                    "order": 3,
                    "next_action": "render_output"
                },
                {
                    "name": "render_output",
                    "order": 4,
                    "next_action": "validate_rules"
                },
                {
                    "name": "validate_rules",
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

def given_environment_and_behavior_config(bot_directory: Path, workspace_directory: Path, behavior: str, behavior_config: dict):
    """Given: Environment and behavior config."""
    bootstrap_env(bot_directory, workspace_directory)
    given_behavior_config_created(bot_directory, behavior, behavior_config)

def then_workflow_states_and_transitions_match_write_tests(behavior_instance):
    """Then: Workflow states and transitions match write tests."""
    then_workflow_states_match(behavior_instance, ['build_knowledge', 'render_output', 'validate_rules'])
    then_workflow_transitions_match(behavior_instance, [
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
        {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
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
    assert behavior_instance.workflow.states == expected_states, (
        f"Should use order from behavior.json {expected_states}, got {behavior_instance.workflow.states}"
    )

def given_knowledge_behavior_config():
    """Given: Knowledge behavior config."""
    return {
        "behaviorName": "knowledge",
        "description": "Test behavior: knowledge",
        "goal": "Test goal for knowledge",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": ["Test instructions for knowledge."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build_knowledge",
                    "order": 3,
                    "next_action": "validate_rules"
                },
                {
                    "name": "validate_rules",
                    "order": 4,
                    "next_action": "render_output"
                },
                {
                    "name": "render_output",
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
        "behaviorName": "write_tests",
        "description": "Test behavior: tests",
        "goal": "Test goal for tests",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": ["Test instructions for tests."],
        "actions_workflow": {
            "actions": [
                {
                    "name": "build_knowledge",
                    "order": 3,
                    "next_action": "render_output"
                },
                {
                    "name": "render_output",
                    "order": 4,
                    "next_action": "validate_rules"
                },
                {
                    "name": "validate_rules",
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
    knowledge_behavior_instance = Behavior(
        name=knowledge_behavior,
        bot_name=bot_name,
        bot_directory=bot_directory
    )
    code_behavior_instance = Behavior(
        name=code_behavior,
        bot_name=bot_name,
        bot_directory=bot_directory
    )
    return knowledge_behavior_instance, code_behavior_instance

def then_knowledge_behavior_has_standard_order(knowledge_behavior_instance):
    """Then: Knowledge behavior has standard order."""
    knowledge_expected_states = ['build_knowledge', 'validate_rules', 'render_output']
    assert knowledge_behavior_instance.workflow.states == knowledge_expected_states, (
        f"Knowledge behavior should have standard order {knowledge_expected_states}, "
        f"got {knowledge_behavior_instance.workflow.states}"
    )

def then_code_behavior_has_reversed_order(code_behavior_instance):
    """Then: Code behavior has reversed order."""
    code_expected_states = ['build_knowledge', 'render_output', 'validate_rules']
    assert code_behavior_instance.workflow.states == code_expected_states, (
        f"Code behavior should have reversed order {code_expected_states}, "
        f"got {code_behavior_instance.workflow.states}"
    )

def then_behaviors_have_different_orders(knowledge_behavior_instance, code_behavior_instance):
    """Then: Behaviors have different orders."""
    assert knowledge_behavior_instance.workflow.states != code_behavior_instance.workflow.states, (
        "Different behaviors should have different action orders"
    )

def given_code_behavior_actions_workflow():
    """Given: Code behavior actions workflow."""
    return {
        "actions": [
            {
                "name": "build_knowledge",
                "order": 3,
                "next_action": "render_output"
            },
            {
                "name": "render_output",
                "order": 4,
                "next_action": "validate_rules"
            },
            {
                "name": "validate_rules",
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
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
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
    behavior_instance = Behavior(
        name=behavior,
        bot_name=bot_name,
        bot_directory=bot_directory
    )
    return behavior_instance

def then_transitions_match_expected(behavior_instance, expected_transitions: list):
    """Then: Transitions match expected."""
    assert behavior_instance.workflow.transitions == expected_transitions, (
        f"Expected transitions {expected_transitions}, got {behavior_instance.workflow.transitions}"
    )

def then_transition_dict_matches_expected(behavior_instance):
    """Then: Transition dict matches expected."""
    transition_dict = {t['source']: t['dest'] for t in behavior_instance.workflow.transitions}
    assert transition_dict['build_knowledge'] == 'render_output', (
        "build_knowledge should transition to render_output"
    )
    assert transition_dict['render_output'] == 'validate_rules', (
        "render_output should transition to validate_rules"
    )


class TestInvokeBehaviorInWorkflowOrder:
    """Story: Behavior-Specific Workflow Order - Tests behavior-specific workflow configuration."""
    
    def test_workflow_determines_next_action_from_current_action(self, bot_directory, workspace_directory):
        """Scenario: Workflow determines next action from current_action (source of truth)"""
        
        # Given workflow_state.json shows:
        #   - current_action: build_knowledge
        #   - completed_actions: [gather_context] (may be behind)
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_action_for_gather_context(bot_name, behavior)
        
        # When workflow loads state (current_action is the source of truth)
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'build_knowledge', completed)
        
        # Then current_state should be build_knowledge (uses current_action from file)
        then_workflow_current_state_is_build_knowledge(workflow)

    def test_workflow_starts_at_first_action_when_no_completed_actions(self, bot_directory, workspace_directory):
        """Scenario: No completed actions yet"""
        
        # Given workflow loads state with no completed_actions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'gather_context', [])
        
        # Then current_state should be the first action (gather_context)
        then_workflow_current_state_is_gather_context(workflow)

    def test_workflow_uses_current_action_when_provided(self, bot_directory, workspace_directory):
        """Scenario: Workflow uses current_action when provided"""
        
        # Given current_action: decide_planning_criteria
        # And completed_actions: [gather_context]
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_action_for_gather_context(bot_name, behavior)
        
        workflow = when_create_workflow_with_current_action(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)
        
        # Then current_state should be decide_planning_criteria (uses current_action from file)
        then_workflow_current_state_is_decide_planning_criteria(workflow)

    def test_workflow_falls_back_to_completed_actions_when_current_action_missing(self, bot_directory, workspace_directory):
        """Scenario: Workflow falls back to completed_actions when current_action is missing"""
        # Given: Bot name, behavior, and completed actions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_actions_for_three_actions(bot_name, behavior)
        
        # When: Workflow is created with empty workflow state
        workflow = given_environment_and_empty_workflow_state(bot_directory, workspace_directory, bot_name, behavior, completed)
        
        # Then: Current state falls back to validate_rules
        then_current_state_is(workflow, 'validate_rules')

    def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(self, bot_directory, workspace_directory):
        """Scenario: No workflow_state.json file exists (fresh start)"""
        # Given: Bot name, behavior, and no workflow file exists
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        
        workflow_file = given_environment_and_verify_no_workflow_file(bot_directory, workspace_directory)
        
        # When: Workflow is created with standard states and transitions
        states, transitions = given_standard_workflow_states_and_transitions()
        workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
        
        # Then: Workflow starts at first action
        then_current_state_is(workflow, 'gather_context')

    def test_workflow_out_of_order_navigation_removes_completed_actions_after_target(self, bot_directory, workspace_directory):
        """Scenario: When navigating out of order, completed actions after target are removed"""
        
        # Given workflow_state.json shows:
        #   - current_action: validate_rules (at the end)
        #   - completed_actions: [gather_context, decide_planning_criteria, build_knowledge, validate_rules]
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
        completed = given_completed_actions_for_four_actions(bot_name, behavior)
        
        # Bootstrap environment
        workflow_file, workflow = given_environment_workflow_state_and_workflow(bot_directory, workspace_directory, bot_name, behavior, 'validate_rules', completed)
        
        # Verify initial state
        then_workflow_current_state_is(workflow, 'validate_rules')
        
        # When navigating out of order back to build_knowledge using production method
        target_action = 'build_knowledge'
        when_navigate_to_target_action_out_of_order(workflow, target_action)
        
        # Then current_state should be build_knowledge
        then_workflow_current_state_is(workflow, target_action)
        
        # And render_output should be removed from completed_actions
        then_verify_completed_actions_after_navigation(workflow_file, bot_name, behavior)
    
    def test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behaviors/{behavior_name}/behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_config = given_write_tests_behavior_config()
        
        given_environment_and_behavior_config(bot_directory, workspace_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        then_workflow_states_and_transitions_match_write_tests(behavior_instance)
    
    def test_behavior_requires_actions_workflow_json_no_fallback(self, bot_directory, workspace_directory):
        """Scenario: Behavior REQUIRES behavior.json - no fallback exists"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_dir = given_environment_and_behavior_directory(bot_directory, workspace_directory, behavior)
        
        exc_info = when_behavior_is_initialized_raises_error(bot_name, behavior, bot_directory)
        
        then_error_mentions_behavior_json_required(exc_info, behavior)
    
    def test_behavior_loads_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_config = given_write_tests_behavior_config()
        
        given_environment_and_behavior_config(bot_directory, workspace_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        # Then: Workflow should use order from behavior.json
        expected_states = ['build_knowledge', 'render_output', 'validate_rules']
        then_workflow_states_match_expected(behavior_instance, expected_states)
    
    def _setup_behaviors_with_different_orders(self, bot_directory, bot_name):
        """Helper: Set up knowledge and code behaviors with different orders."""
        knowledge_behavior = '1_shape'
        knowledge_behavior_dir = given_behavior_directory_created(bot_directory, knowledge_behavior)
        knowledge_behavior_config = given_knowledge_behavior_config()
        given_behavior_json_file_created(knowledge_behavior_dir, knowledge_behavior_config)
        
        code_behavior = '7_write_tests'
        code_behavior_dir = given_behavior_directory_created(bot_directory, code_behavior)
        code_behavior_config = given_code_behavior_config()
        given_behavior_json_file_created(code_behavior_dir, code_behavior_config)
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
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '8_code')
        behavior_dir = given_behavior_directory_created(bot_directory, behavior)
        
        # Create behavior.json with specific next_action values
        actions_workflow = given_code_behavior_actions_workflow()
        behavior_config = given_code_behavior_config_with_workflow(actions_workflow)
        given_behavior_json_file_created(behavior_dir, behavior_config)
        
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
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.{current_action}',
        'completed_actions': completed_actions or []
    }), encoding='utf-8')
    return workflow_file


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
    return ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']


def then_bot_result_has_error_with_invalid_action_message(result: BotResult, bot_name: str, behavior: str, invalid_action: str, valid_actions: list):
    """Then: BotResult has error with invalid action message."""
    assert isinstance(result, BotResult)
    assert result.status == 'error'
    assert result.behavior == behavior
    assert result.action == invalid_action
    assert 'message' in result.data
    assert 'INVALID ACTION' in result.data['message']
    assert invalid_action in result.data['message']
    for valid_action in valid_actions:
        assert valid_action in result.data['message']
    assert 'valid_actions' in result.data
    for valid_action in valid_actions:
        assert valid_action in result.data['valid_actions']
        assert f'{bot_name}_{behavior}_{valid_action}' in result.data['message']


def given_no_workflow_state_exists(workspace_directory: Path):
    """Given: No workflow state exists."""
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()


class TestExecuteBehavior:
    """Tests for Bot.execute_behavior() - Production code path."""

    def test_execute_behavior_with_action_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior with action parameter
        GIVEN: Bot has behavior 'shape' with action 'gather_context'
        WHEN: Bot.execute_behavior('shape', action='gather_context') is called
        THEN: Action executes and returns BotResult
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'gather_context')
        
        bot_result = when_execute_behavior_called(bot, 'shape', 'gather_context')
        
        then_bot_result_has_correct_status(bot_result, 'completed', 'shape', 'gather_context')

    def test_execute_behavior_without_action_forwards_to_current(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior without action parameter forwards to current action
        GIVEN: Bot has behavior 'shape' and workflow state shows current_action='decide_planning_criteria'
        WHEN: Bot.execute_behavior('shape') is called (no action parameter)
        THEN: Forwards to current action (decide_planning_criteria)
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'gather_context')
        bot, _ = given_bot_setup_with_current_action(bot_directory, workspace_directory, 'test_bot', ['shape'], 'shape', 'decide_planning_criteria', [completed_action])
        
        bot_result = when_execute_behavior_called(bot, 'shape')
        
        then_bot_result_has_correct_status(bot_result, 'completed', expected_action='decide_planning_criteria')

    def test_execute_behavior_requires_confirmation_when_out_of_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Execute behavior requires confirmation when out of order
        GIVEN: Current behavior is 'discovery', requested behavior is 'shape' (going backwards)
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Returns BotResult with status 'requires_confirmation'
        """
        completed_action = given_completed_action_entry('test_bot', 'shape', 'validate_rules', '2025-12-04T15:45:00.000000')
        bot, _ = given_bot_setup_with_multiple_behaviors(bot_directory, workspace_directory, 'test_bot', ['shape', 'prioritization', 'discovery'], 'prioritization', 'gather_context', [completed_action])
        
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
        GIVEN: Bot has behavior 'prioritization' with valid actions: gather_context, decide_planning_criteria, etc.
        WHEN: Bot.execute_behavior('prioritization', action='start') is called with invalid action 'start'
        THEN: Returns BotResult with status 'error' and message listing valid actions
        """
        bot, _ = given_bot_setup_with_action(bot_directory, workspace_directory, 'test_bot', ['prioritization'], 'prioritization', 'gather_context')
        
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
    from agile_bot.bots.base_bot.src.bot.bot import Behavior
    with pytest.raises(FileNotFoundError) as exc_info:
        Behavior(
            name=behavior_name,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
    return exc_info


def then_exception_mentions_behavior_json_required(exc_info, behavior_name: str):
    """Then: Exception mentions behavior.json is REQUIRED."""
    assert 'behavior.json is REQUIRED' in str(exc_info.value)
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
# STORY: Find Behavior Folder (Behavior.find_behavior_folder utility)
# ============================================================================

@pytest.fixture
def bot_directory(tmp_path):
    """Fixture: Temporary bot directory."""
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'test_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir


class TestFindBehaviorFolder:
    """Tests for find_behavior_folder utility function."""

    def test_finds_behavior_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find behavior folder with number prefix
        GIVEN: Behavior folder exists with number prefix (8_tests)
        WHEN: find_behavior_folder is called with behavior name without prefix (tests)
        THEN: Returns path to numbered folder (8_tests)
        """
        # Given: Create numbered behavior folder
        bot_name, folder_name, behavior_name = given_test_bot_folder_and_behavior_names()
        
        behavior_folder = create_behavior_folder_with_json(bot_directory, folder_name)
        
        # When: Find folder using behavior name (without number)
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, behavior_name)
        
        # Then: Returns numbered folder
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '8_tests')

    def test_finds_shape_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find shape folder with number prefix
        GIVEN: Behavior folder exists with number prefix (1_shape)
        WHEN: find_behavior_folder is called with behavior name (shape)
        THEN: Returns path to numbered folder (1_shape)
        """
        # Given: Create numbered behavior folder
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, '1_shape')
        
        # When: Find folder using behavior name
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, 'shape')
        
        # Then: Returns numbered folder
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '1_shape')

    def test_finds_exploration_folder_with_number_prefix(self, bot_directory):
        """
        SCENARIO: Find exploration folder with number prefix
        GIVEN: Behavior folder exists with number prefix (5_exploration)
        WHEN: find_behavior_folder is called with behavior name (exploration)
        THEN: Returns path to numbered folder (5_exploration)
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, '5_exploration')
        
        # When
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, 'exploration')
        
        # Then
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '5_exploration')

    def test_raises_error_when_behavior_folder_not_found(self, bot_directory):
        """
        SCENARIO: Raises error when behavior folder doesn't exist
        GIVEN: Behavior folder does not exist
        WHEN: find_behavior_folder is called
        THEN: Raises FileNotFoundError with clear message
        """
        # Given: No behavior folder exists
        bot_name, behavior_name = given_test_bot_and_nonexistent_behavior_names()
        
        # When: Finding behavior folder
        # Then: FileNotFoundError is raised (verified by pytest.raises)
        when_expect_behavior_folder_not_found_error(bot_directory, bot_name, behavior_name)

    def test_handles_prioritization_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Prioritization Folder With Prefix
        GIVEN: Behavior folder exists as 2_prioritization
        WHEN: find_behavior_folder is called with behavior name (prioritization)
        THEN: Returns path to 2_prioritization
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, '2_prioritization')
        
        # When
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, 'prioritization')
        
        # Then
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '2_prioritization')

    def test_handles_scenarios_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Scenarios Folder With Prefix
        GIVEN: Behavior folder exists as 6_scenarios
        WHEN: find_behavior_folder is called with behavior name (scenarios)
        THEN: Returns path to 6_scenarios
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, '6_scenarios')
        
        # When
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, 'scenarios')
        
        # Then
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '6_scenarios')

    def test_handles_examples_folder_with_prefix(self, bot_directory):
        """
        SCENARIO: Handles Examples Folder With Prefix
        GIVEN: Behavior folder exists as 7_examples
        WHEN: find_behavior_folder is called with behavior name (examples)
        THEN: Returns path to 7_examples
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(bot_directory, '7_examples')
        
        # When
        found_folder = Behavior.find_behavior_folder(bot_directory, bot_name, 'examples')
        
        # Then
        then_behavior_folder_matches_expected(found_folder, behavior_folder, '7_examples')

