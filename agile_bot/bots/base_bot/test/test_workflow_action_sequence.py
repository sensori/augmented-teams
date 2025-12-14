"""
Test that workflow correctly determines next action based on current_action.

Workflow loads state from current_action (source of truth), with fallback to completed_actions if current_action is missing or invalid.
"""
import pytest
import json
import os
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow
from conftest import bootstrap_env, create_workflow_state_file, create_test_workflow, given_bot_name_and_behavior_setup
from agile_bot.bots.base_bot.test.test_helpers import then_workflow_current_state_is


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Removed given_bot_and_behavior_setup - use test_helpers.given_bot_name_and_behavior_setup instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import given_bot_name_and_behavior_setup


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


# Removed then_completed_actions_include - use test_helpers.then_completed_actions_include instead
# Note: test_helpers version takes different signature - adapt calls accordingly


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


# Removed then_workflow_current_state_is - use test_helpers.then_workflow_current_state_is instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import then_workflow_current_state_is


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


# ============================================================================
# INLINE HELPERS - Used only by tests in this file
# ============================================================================


def test_workflow_determines_next_action_from_current_action(bot_directory, workspace_directory):
    """Scenario: Workflow determines next action from current_action (source of truth)"""
    
    # Given workflow_state.json shows:
    #   - current_action: build_knowledge
    #   - completed_actions: [gather_context] (may be behind)
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    completed = [{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'}]
    
    # When workflow loads state (current_action is the source of truth)
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'build_knowledge', completed, return_workflow_file=False)
    
    # Then current_state should be build_knowledge (uses current_action from file)
    assert workflow.current_state == 'build_knowledge'


def test_workflow_starts_at_first_action_when_no_completed_actions(bot_directory, workspace_directory):
    """Scenario: No completed actions yet"""
    
    # Given workflow loads state with no completed_actions
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'gather_context', [], return_workflow_file=False)
    
    # Then current_state should be the first action (gather_context)
    assert workflow.current_state == 'gather_context'


def test_workflow_uses_current_action_when_provided(bot_directory, workspace_directory):
    """Scenario: Workflow uses current_action when provided"""
    
    # Given current_action: decide_planning_criteria
    # And completed_actions: [gather_context]
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'}
    ]
    
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed, return_workflow_file=False)
    
    # Then current_state should be decide_planning_criteria (uses current_action from file)
    assert workflow.current_state == 'decide_planning_criteria'


def test_workflow_falls_back_to_completed_actions_when_current_action_missing(bot_directory, workspace_directory):
    """Scenario: Workflow falls back to completed_actions when current_action is missing"""
    
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:47:00.000000'}
    ]
    
    bootstrap_env(bot_directory, workspace_directory)
    given_workflow_state_file_with_empty_current_action(workspace_directory, bot_name, behavior, completed)
    
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
        bot_directory=bot_directory,
        states=states,
        transitions=transitions
    )
    
    then_current_state_is(workflow, 'validate_rules')


def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(bot_directory, workspace_directory):
    """Scenario: No workflow_state.json file exists (fresh start)"""
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    
    bootstrap_env(bot_directory, workspace_directory)
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()
    
    states, transitions = given_standard_workflow_states_and_transitions()
    workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
    
    then_current_state_is(workflow, 'gather_context')


def test_workflow_out_of_order_navigation_removes_completed_actions_after_target(bot_directory, workspace_directory):
    """Scenario: When navigating out of order, completed actions after target are removed"""
    
    # Given workflow_state.json shows:
    #   - current_action: validate_rules (at the end)
    #   - completed_actions: [gather_context, decide_planning_criteria, build_knowledge, validate_rules]
    bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', 'shape')
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:47:00.000000'},
    ]
    
    # Bootstrap environment
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create initial workflow state with all actions completed
    workflow_file = given_workflow_state_with_completed_actions(
        workspace_directory, bot_name, behavior, 'validate_rules', completed
    )
    
    # Create workflow with states
    states, transitions = given_standard_workflow_states_and_transitions()
    workflow = given_workflow_created(bot_name, behavior, bot_directory, states, transitions)
    
    # Verify initial state
    then_workflow_current_state_is(workflow, 'validate_rules')
    
    # When navigating out of order back to build_knowledge using production method
    target_action = 'build_knowledge'
    when_workflow_navigates_to_action(workflow, target_action, out_of_order=True)
    
    # Then current_state should be build_knowledge
    then_workflow_current_state_is(workflow, target_action)
    
    # And render_output should be removed from completed_actions
    then_completed_actions_do_not_include(workflow_file, bot_name, behavior, 'render_output')
    
    # And build_knowledge and earlier actions should still be in completed_actions
    then_completed_actions_include(workflow_file, bot_name, behavior, ['gather_context', 'decide_planning_criteria', 'build_knowledge'])


# ============================================================================
# STORY: Behavior-Specific Workflow Order
# ============================================================================

class TestInvokeBehaviorInWorkflowOrder:
    """Story: Behavior-Specific Workflow Order - Tests behavior-specific workflow configuration."""
    
    def test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behaviors/{behavior_name}/behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_config = {
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
        
        bootstrap_env(bot_directory, workspace_directory)
        given_behavior_config_created(bot_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        then_workflow_states_match(behavior_instance, ['build_knowledge', 'render_output', 'validate_rules'])
        then_workflow_transitions_match(behavior_instance, [
            {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
            {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
        ])
    
    def test_behavior_requires_actions_workflow_json_no_fallback(self, bot_directory, workspace_directory):
        """Scenario: Behavior REQUIRES behavior.json - no fallback exists"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        bootstrap_env(bot_directory, workspace_directory)
        
        exc_info = when_behavior_is_initialized_raises_error(bot_name, behavior, bot_directory)
        
        then_error_mentions_behavior_json_required(exc_info, behavior)
    
    def test_behavior_loads_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behavior.json"""
        
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        behavior_config = {
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
        
        bootstrap_env(bot_directory, workspace_directory)
        given_behavior_config_created(bot_directory, behavior, behavior_config)
        
        behavior_instance = when_behavior_is_initialized(bot_name, behavior, bot_directory)
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Behavior is initialized
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        behavior_instance = Behavior(
            name=behavior,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
        
        # Then: Workflow should use order from behavior.json
        expected_states = ['build_knowledge', 'render_output', 'validate_rules']
        assert behavior_instance.workflow.states == expected_states, (
            f"Should use order from behavior.json {expected_states}, got {behavior_instance.workflow.states}"
        )
    
    def test_different_behaviors_can_have_different_action_orders(self, bot_directory, workspace_directory):
        """Scenario: Different behaviors can have different action orders"""
        
        bot_name, _ = given_bot_name_and_behavior_setup('story_bot')
        
        # Given: Knowledge graph behavior (1_shape) with standard order
        knowledge_behavior = '1_shape'
        knowledge_behavior_dir = bot_directory / 'behaviors' / knowledge_behavior
        knowledge_behavior_dir.mkdir(parents=True, exist_ok=True)
        knowledge_actions_workflow = {
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
        }
        knowledge_behavior_config = {
            "behaviorName": "knowledge",
            "description": "Test behavior: knowledge",
            "goal": "Test goal for knowledge",
            "inputs": "Test inputs",
            "outputs": "Test outputs",
            "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
            "instructions": ["Test instructions for knowledge."],
            "actions_workflow": knowledge_actions_workflow,
            "trigger_words": {
                "description": "Trigger words for knowledge",
                "patterns": ["test.*knowledge"],
                "priority": 10
            }
        }
        knowledge_behavior_file = knowledge_behavior_dir / 'behavior.json'
        knowledge_behavior_file.write_text(json.dumps(knowledge_behavior_config), encoding='utf-8')
        
        # And: Code generation behavior (7_write_tests) with reversed order
        code_behavior = '7_write_tests'
        code_behavior_dir = bot_directory / 'behaviors' / code_behavior
        code_behavior_dir.mkdir(parents=True, exist_ok=True)
        code_actions_workflow = {
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
        code_behavior_config = {
            "behaviorName": "write_tests",
            "description": "Test behavior: tests",
            "goal": "Test goal for tests",
            "inputs": "Test inputs",
            "outputs": "Test outputs",
            "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
            "instructions": ["Test instructions for tests."],
            "actions_workflow": code_actions_workflow,
            "trigger_words": {
                "description": "Trigger words for tests",
                "patterns": ["test.*tests"],
                "priority": 10
            }
        }
        code_behavior_file = code_behavior_dir / 'behavior.json'
        code_behavior_file.write_text(json.dumps(code_behavior_config), encoding='utf-8')
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Both behaviors are initialized
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
        
        # Then: Knowledge graph behavior should have standard order
        knowledge_expected_states = ['build_knowledge', 'validate_rules', 'render_output']
        assert knowledge_behavior_instance.workflow.states == knowledge_expected_states, (
            f"Knowledge behavior should have standard order {knowledge_expected_states}, "
            f"got {knowledge_behavior_instance.workflow.states}"
        )
        
        # And: Code generation behavior should have reversed order
        code_expected_states = ['build_knowledge', 'render_output', 'validate_rules']
        assert code_behavior_instance.workflow.states == code_expected_states, (
            f"Code behavior should have reversed order {code_expected_states}, "
            f"got {code_behavior_instance.workflow.states}"
        )
        
        # And: Orders should be different
        assert knowledge_behavior_instance.workflow.states != code_behavior_instance.workflow.states, (
            "Different behaviors should have different action orders"
        )
    
    def test_workflow_transitions_built_correctly_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Workflow transitions are built correctly from behavior.json"""
        
        # Given: Behavior with behavior.json and custom transitions
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '8_code')
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create behavior.json with specific next_action values
        actions_workflow = {
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
        
        behavior_config = {
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
        behavior_file = behavior_dir / 'behavior.json'
        behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Behavior is initialized
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        behavior_instance = Behavior(
            name=behavior,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
        
        # Then: Transitions should be built from action_config.json next_action values
        expected_transitions = [
            {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
            {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
        ]
        assert behavior_instance.workflow.transitions == expected_transitions, (
            f"Expected transitions {expected_transitions}, got {behavior_instance.workflow.transitions}"
        )
        
        # And: Each transition should have correct source and destination
        transition_dict = {t['source']: t['dest'] for t in behavior_instance.workflow.transitions}
        assert transition_dict['build_knowledge'] == 'render_output', (
            "build_knowledge should transition to render_output"
        )
        assert transition_dict['render_output'] == 'validate_rules', (
            "render_output should transition to validate_rules"
        )
