"""
Test that workflow correctly determines next action based on current_action.

Workflow loads state from current_action (source of truth), with fallback to completed_actions if current_action is missing or invalid.
"""
import pytest
import json
import os
from pathlib import Path
from agile_bot.bots.base_bot.src.state.workflow import Workflow
from conftest import bootstrap_env, create_workflow_state_file


# ============================================================================
# INLINE HELPERS - Used only by tests in this file
# ============================================================================

def create_test_workflow(
    bot_dir: Path,
    workspace_dir: Path,
    bot_name: str,
    behavior: str,
    current_action: str,
    completed_actions: list = None
) -> Workflow:
    """Helper: Create workflow with specified state for testing."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    # Create workflow state file
    create_workflow_state_file(
        workspace_dir, bot_name, behavior, current_action, completed_actions
    )
    
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    
    return Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=states,
        transitions=transitions
    )


def test_workflow_determines_next_action_from_current_action(bot_directory, workspace_directory):
    """Scenario: Workflow determines next action from current_action (source of truth)"""
    
    # Given workflow_state.json shows:
    #   - current_action: build_knowledge
    #   - completed_actions: [gather_context] (may be behind)
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'}]
    
    # When workflow loads state (current_action is the source of truth)
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'build_knowledge', completed)
    
    # Then current_state should be build_knowledge (uses current_action from file)
    assert workflow.current_state == 'build_knowledge'


def test_workflow_starts_at_first_action_when_no_completed_actions(bot_directory, workspace_directory):
    """Scenario: No completed actions yet"""
    
    # Given workflow loads state with no completed_actions
    bot_name = 'story_bot'
    behavior = 'shape'
    
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'gather_context', [])
    
    # Then current_state should be the first action (gather_context)
    assert workflow.current_state == 'gather_context'


def test_workflow_uses_current_action_when_provided(bot_directory, workspace_directory):
    """Scenario: Workflow uses current_action when provided"""
    
    # Given current_action: decide_planning_criteria
    # And completed_actions: [gather_context]
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'}
    ]
    
    workflow = create_test_workflow(bot_directory, workspace_directory, bot_name, behavior, 'decide_planning_criteria', completed)
    
    # Then current_state should be decide_planning_criteria (uses current_action from file)
    assert workflow.current_state == 'decide_planning_criteria'


def test_workflow_falls_back_to_completed_actions_when_current_action_missing(bot_directory, workspace_directory):
    """Scenario: Workflow falls back to completed_actions when current_action is missing"""
    
    # Given workflow_state.json shows:
    #   - current_action: "" (missing or empty)
    #   - completed_actions: [gather_context, decide_planning_criteria, build_knowledge]
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:47:00.000000'}
    ]
    
    # Bootstrap environment
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create workflow state with empty current_action
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': '',  # Empty - should trigger fallback
        'completed_actions': completed,
        'timestamp': '2025-12-04T15:45:00.000000'
    }), encoding='utf-8')
    
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
    
    # Then current_state should be validate_rules (next after last completed: build_knowledge)
    assert workflow.current_state == 'validate_rules'


def test_workflow_starts_at_first_action_when_no_workflow_state_file_exists(bot_directory, workspace_directory):
    """Scenario: No workflow_state.json file exists (fresh start)"""
    # Given workspace directory exists but workflow_state.json does NOT exist
    bot_name = 'story_bot'
    behavior = 'shape'
    
    # Bootstrap environment
    bootstrap_env(bot_directory, workspace_directory)
    
    workflow_file = workspace_directory / 'workflow_state.json'
    assert not workflow_file.exists()
    
    # When workflow is created
    states = ['gather_context', 'decide_planning_criteria', 
              'build_knowledge', 'validate_rules', 'render_output']
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    
    workflow = Workflow(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory, states=states, transitions=transitions)
    
    # Then current_state should be the FIRST action (gather_context)
    assert workflow.current_state == 'gather_context'


def test_workflow_out_of_order_navigation_removes_completed_actions_after_target(bot_directory, workspace_directory):
    """Scenario: When navigating out of order, completed actions after target are removed"""
    
    # Given workflow_state.json shows:
    #   - current_action: validate_rules (at the end)
    #   - completed_actions: [gather_context, decide_planning_criteria, build_knowledge, validate_rules]
    bot_name = 'story_bot'
    behavior = 'shape'
    completed = [
        {'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'},
        {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:45:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.build_knowledge', 'timestamp': '2025-12-04T15:46:00.000000'},
        {'action_state': f'{bot_name}.{behavior}.render_output', 'timestamp': '2025-12-04T15:47:00.000000'},
    ]
    
    # Bootstrap environment
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create initial workflow state with all actions completed
    workflow_file = workspace_directory / 'workflow_state.json'
    workflow_file.write_text(json.dumps({
        'current_behavior': f'{bot_name}.{behavior}',
        'current_action': f'{bot_name}.{behavior}.validate_rules',
        'completed_actions': completed,
        'timestamp': '2025-12-04T15:48:00.000000'
    }), encoding='utf-8')
    
    # Create workflow with states
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
    
    # Verify initial state
    assert workflow.current_state == 'validate_rules'
    
    # When navigating out of order back to build_knowledge using production method
    target_action = 'build_knowledge'
    workflow.navigate_to_action(target_action, out_of_order=True)
    
    # Then current_state should be build_knowledge
    assert workflow.current_state == target_action
    
    # And render_output should be removed from completed_actions
    loaded_state = json.loads(workflow_file.read_text(encoding='utf-8'))
    completed_action_states = [a['action_state'] for a in loaded_state['completed_actions']]
    assert f'{bot_name}.{behavior}.render_output' not in completed_action_states
    
    # And build_knowledge and earlier actions should still be in completed_actions
    assert f'{bot_name}.{behavior}.gather_context' in completed_action_states
    assert f'{bot_name}.{behavior}.decide_planning_criteria' in completed_action_states
    assert f'{bot_name}.{behavior}.build_knowledge' in completed_action_states


# ============================================================================
# STORY: Behavior-Specific Workflow Order
# ============================================================================

class TestBehaviorSpecificWorkflowOrder:
    """Story: Behavior-Specific Workflow Order - Tests behavior-specific workflow configuration."""
    
    def test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behaviors/{behavior_name}/behavior.json"""
        
        # Given: A behavior with behavior-specific behavior.json file
        bot_name = 'story_bot'
        behavior = '7_write_tests'
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create behavior-specific behavior.json with reversed order
        # (render_output before validate_rules for code generation behaviors)
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
        
        behavior_file = behavior_dir / 'behavior.json'
        behavior_file.write_text(json.dumps(behavior_config), encoding='utf-8')
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Behavior is initialized (will call load_workflow_states_and_transitions with behavior_name)
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        behavior_instance = Behavior(
            name=behavior,
            bot_name=bot_name,
            bot_directory=bot_directory
        )
        
        # Then: Workflow states should be loaded from behavior-specific directory
        # States should be in behavior-specific order: build_knowledge, render_output, validate_rules
        expected_states = ['build_knowledge', 'render_output', 'validate_rules']
        assert behavior_instance.workflow.states == expected_states, (
            f"Expected states {expected_states}, got {behavior_instance.workflow.states}"
        )
        
        # And: Transitions should match behavior-specific order
        expected_transitions = [
            {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
            {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
        ]
        assert behavior_instance.workflow.transitions == expected_transitions, (
            f"Expected transitions {expected_transitions}, got {behavior_instance.workflow.transitions}"
        )
    
    def test_behavior_requires_actions_workflow_json_no_fallback(self, bot_directory, workspace_directory):
        """Scenario: Behavior REQUIRES behavior.json - no fallback exists"""
        
        # Given: Behavior folder exists but behavior.json is missing
        bot_name = 'story_bot'
        behavior = '7_write_tests'
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Behavior is initialized without behavior.json
        # Then: Should raise FileNotFoundError
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        with pytest.raises(FileNotFoundError) as exc_info:
            Behavior(
                name=behavior,
                bot_name=bot_name,
                bot_directory=bot_directory
            )
        
        assert 'behavior.json is REQUIRED' in str(exc_info.value)
        assert behavior in str(exc_info.value)
    
    def test_behavior_loads_from_actions_workflow_json(self, bot_directory, workspace_directory):
        """Scenario: Behavior loads workflow order from behavior.json"""
        
        # Given: Behavior with behavior.json file
        bot_name = 'story_bot'
        behavior = '7_write_tests'
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # Create behavior-specific behavior.json with reversed order
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
        
        bot_name = 'story_bot'
        
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
        bot_name = 'story_bot'
        behavior = '8_code'
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
