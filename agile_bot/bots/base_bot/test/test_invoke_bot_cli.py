"""
Invoke Bot CLI Tests

Tests for CLI increment stories:
- Invoke Bot CLI
- Invoke Bot Behavior CLI  
- Invoke Bot Behavior Action CLI
- Detect Trigger Words Through Extension

Tests use BaseBotCli pattern from cli_invocation_pattern.md.
CLI routes to bot, bot executes. Tests verify CLI routing and bot execution.
"""
import pytest
from pathlib import Path
import json
from conftest import (
    create_bot_config_file,
    create_workflow_state_file,
    create_base_actions_structure
)
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env

# ============================================================================
# HELPER CLASSES
# ============================================================================

class TriggerTestSetup:
    """Helper class to set up bot with trigger words for testing."""
    
    def __init__(self, bot_directory: Path, workspace_directory: Path, bot_name: str = 'story_bot'):
        self.bot_directory = bot_directory
        self.workspace_directory = workspace_directory
        self.bot_name = bot_name
        self.behaviors = ['shape', 'prioritization', 'arrange', 'discovery', 'exploration', 'scenarios', 'examples', 'tests']
        self.actions = ['initialize_workspace', 'gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
        self.bot_config = None
    
    def setup_bot(self):
        """Set up bot with all behaviors and actions."""
        # workspace_root is bot_directory's parent.parent.parent (tmp_path)
        workspace_root = self.bot_directory.parent.parent.parent
        self.bot_config = setup_bot_for_testing(
            workspace_root, self.bot_name, self.behaviors
        )
        # Ensure behavior folders exist
        behaviors_dir = workspace_root / 'agile_bot' / 'bots' / self.bot_name / 'behaviors'
        for behavior in self.behaviors:
            behavior_dir = behaviors_dir / behavior
            behavior_dir.mkdir(parents=True, exist_ok=True)
            # Create knowledge graph folder for build_knowledge action
            kg_dir = behavior_dir / 'content' / 'knowledge_graph'
            kg_dir.mkdir(parents=True, exist_ok=True)
            # Create a dummy config file with template field pointing to a template file
            template_filename = 'test_template.json'
            kg_config = {'template': template_filename}
            (kg_dir / 'build_story_graph_outline.json').write_text(
                json.dumps(kg_config), encoding='utf-8'
            )
            # Create the actual template file (JSON format)
            template_content = {'instructions': ['Test knowledge graph template']}
            (kg_dir / template_filename).write_text(
                json.dumps(template_content), encoding='utf-8'
            )
        
        # Create story graph file in workspace (required for validate_rules action)
        stories_dir = self.workspace_directory / 'docs' / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        story_graph_file = stories_dir / 'story-graph.json'
        story_graph_file.write_text(json.dumps({
            'epics': [],
            'solution': {'name': 'Test Solution'}
        }), encoding='utf-8')
        
        return self
    
    def add_bot_triggers(self, patterns: list):
        """Add bot-level trigger words."""
        # workspace_root is bot_directory's parent.parent.parent (tmp_path)
        workspace_root = self.bot_directory.parent.parent.parent
        create_bot_trigger_words(workspace_root, self.bot_name, patterns)
        return self
    
    def add_behavior_triggers(self, behavior_patterns: dict):
        """Add behavior-level trigger words.
        
        Args:
            behavior_patterns: Dict mapping behavior -> trigger patterns list
        """
        # workspace_root is bot_directory's parent.parent.parent (tmp_path)
        workspace_root = self.bot_directory.parent.parent.parent
        for behavior, patterns in behavior_patterns.items():
            create_behavior_trigger_words(workspace_root, self.bot_name, behavior, patterns)
        return self
    
    def add_action_triggers(self, behavior: str, action: str, patterns: list):
        """Add action-level trigger words."""
        # workspace_root is bot_directory's parent.parent.parent (tmp_path)
        workspace_root = self.bot_directory.parent.parent.parent
        create_action_trigger_words(workspace_root, self.bot_name, behavior, action, patterns)
        return self
    
    def add_all_action_triggers(self, template: str):
        """Add action triggers for all behavior/action combinations using template.
        
        Args:
            template: Template string with {behavior} and {action} placeholders
        """
        for behavior in self.behaviors:
            for action in self.actions:
                trigger = template.format(behavior=behavior, action=action)
                self.add_action_triggers(behavior, action, [trigger])
        return self
    
    def create_workflow_state(self, current_behavior: str, current_action: str):
        """Create workflow state file."""
        return create_workflow_state_file(
            self.workspace_directory,
            self.bot_name,
            current_behavior,
            current_action,
            completed_actions=[]
        )


class TriggerRouterTestHelper:
    
    """Helper class for testing trigger routing and CLI execution."""
    
    def __init__(self, bot_directory: Path, workspace_directory: Path, bot_name: str, bot_config: Path):
        self.bot_directory = bot_directory
        self.workspace_directory = workspace_directory
        self.bot_name = bot_name
        self.bot_config = bot_config
        self.router = None
        self.cli = None
    
    def match_and_execute(self, trigger_message: str, current_behavior: str = None, current_action: str = None):
        """Match trigger and execute via CLI.
        
        Creates fresh router and CLI instances for each call to avoid state leakage.
        
        Returns:
            Tuple of (route, cli_result)
        """
        from agile_bot.bots.base_bot.src.cli.trigger_router import TriggerRouter
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        
        # Create fresh instances to avoid state leakage between test iterations
        # TriggerRouter needs workspace_root - use workspace_directory's parent (tmp_path)
        workspace_root = self.workspace_directory.parent
        router = TriggerRouter(workspace_root=workspace_root, bot_name=self.bot_name)
        route = router.match_trigger(
            message=trigger_message,
            current_behavior=current_behavior,
            current_action=current_action
        )
        
        if route is None:
            return None, None
        
        # Bootstrap environment before creating CLI (needs BOT_DIRECTORY)
        from agile_bot.bots.base_bot.test.conftest import bootstrap_env
        bootstrap_env(self.bot_directory, self.workspace_directory)
        
        # Create fresh CLI instance for each execution
        cli = BaseBotCli(
            bot_name=self.bot_name,
            bot_config_path=self.bot_config
        )
        
        if route.get('action_name') == 'close_current_action':
            result = cli.close_current_action()
        else:
            result = cli.run(
                behavior_name=route.get('behavior_name'),
                action_name=route.get('action_name'),
                context=trigger_message
            )
        
        return route, result
    
    def assert_route(self, route, expected_bot: str, expected_behavior: str, expected_action: str, expected_type: str):
        """Assert route matches expected values."""
        assert route is not None, "Route should not be None"
        assert route['bot_name'] == expected_bot
        assert route['behavior_name'] == expected_behavior
        assert route['action_name'] == expected_action
        assert route['match_type'] == expected_type
    
    def assert_cli_result(self, result, expected_behavior: str, expected_action: str):
        """Assert CLI result matches expected values."""
        assert result['status'] == 'success'
        assert result['behavior'] == expected_behavior
        assert result['action'] == expected_action


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_behavior_action_instructions(workspace: Path, bot_name: str, behavior: str, action: str) -> Path:
    """Helper: Create behavior action instructions file."""
    instructions_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    instructions_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = instructions_dir / 'instructions.json'
    instructions_data = {
        'action': action,
        'behavior': behavior,
        'instructions': [f'{action} instructions for {behavior}']
    }
    instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
    return instructions_file

def create_base_action_instructions(workspace: Path, action: str) -> Path:
    """Helper: Create base action instructions file with numbered prefix."""
    action_prefixes = {
        'initialize_workspace': '1_initialize_workspace',
        'gather_context': '1_gather_context',
        'decide_planning_criteria': '2_decide_planning_criteria',
        'build_knowledge': '3_build_knowledge',
        'render_output': '4_render_output',
        'validate_rules': '5_validate_rules'
    }
    
    action_folder = action_prefixes.get(action, action)
    base_dir = workspace / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / action_folder
    base_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = base_dir / 'instructions.json'
    instructions_data = {
        'actionName': action,
        'instructions': [f'Base {action} instructions']
    }
    instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
    return instructions_file

def setup_bot_for_testing(workspace_root: Path, bot_name: str, behaviors: list):
    """Helper: Set up complete bot structure for testing.
    
    Args:
        workspace_root: Root workspace directory (tmp_path)
        bot_name: Name of the bot
        behaviors: List of behavior names
    """
    # Construct bot directory path
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    
    # Create bot config
    bot_config = create_bot_config_file(bot_dir, bot_name, behaviors)
    
    # Create base actions structure in bot_directory (no fallback)
    create_base_actions_structure(bot_dir)
    
    # Create base action instructions
    for action in ['initialize_workspace', 'gather_context', 'decide_planning_criteria', 
                   'build_knowledge', 'validate_rules', 'render_output']:
        create_base_action_instructions(workspace_root, action)
    
    return bot_config

def create_bot_trigger_words(workspace: Path, bot_name: str, patterns: list) -> Path:
    """Helper: Create bot-level trigger words file."""
    trigger_dir = workspace / 'agile_bot' / 'bots' / bot_name
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_data = {'patterns': patterns}
    trigger_file.write_text(json.dumps(trigger_data), encoding='utf-8')
    return trigger_file

def create_behavior_trigger_words(workspace: Path, bot_name: str, behavior: str, patterns: list) -> Path:
    """Helper: Create behavior-level trigger words file."""
    behavior_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = behavior_dir / 'trigger_words.json'
    trigger_data = {'patterns': patterns}
    trigger_file.write_text(json.dumps(trigger_data), encoding='utf-8')
    return trigger_file

def create_action_trigger_words(workspace: Path, bot_name: str, behavior: str, action: str, patterns: list) -> Path:
    """Helper: Create action-level trigger words file."""
    action_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    action_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = action_dir / 'trigger_words.json'
    trigger_data = {'patterns': patterns}
    trigger_file.write_text(json.dumps(trigger_data), encoding='utf-8')
    return trigger_file

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path
    return workspace

# ============================================================================
# TEST CLASSES - Detect Trigger Words Through Extension
# ============================================================================

class TestDetectTriggerWordsThroughExtension:
    """Story: Detect Trigger Words Through Extension (Sub-epic: Invoke CLI)"""

    def test_trigger_bot_only_no_behavior_or_action_specified(self, bot_directory, workspace_directory):
        """
        SCENARIO: Trigger bot only (no behavior or action specified)
        GIVEN: user types message containing trigger words
        AND: bot is at specific behavior and action from workflow state
        WHEN: Extension intercepts user message
        THEN: Extension identifies target bot from trigger patterns
        AND: Extension routes to bot using current behavior and action from state
        AND: CLI executes current behavior and action
        """
        # Arrange: Set up bot with bot-level triggers
        setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_bot_triggers([
            'lets work on stories',
            'time to kick off stories',
            'ready to work on stories'
        ])
        
        helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
        trigger_message = 'lets work on stories'
        
        # Act & Assert: Test all behavior/action combinations
        for current_behavior in setup.behaviors:
            for current_action in setup.actions:
                setup.create_workflow_state(current_behavior, current_action)
                
                route, result = helper.match_and_execute(
                    trigger_message,
                    current_behavior=current_behavior,
                    current_action=current_action
                )
                
                # Verify route is correct
                helper.assert_route(route, setup.bot_name, current_behavior, current_action, 'bot_only')
                
                # Verify CLI executed - note initialize_workspace auto-advances to gather_context
                expected_action = 'gather_context' if current_action == 'initialize_workspace' else current_action
                helper.assert_cli_result(result, current_behavior, expected_action)

    def test_trigger_bot_and_behavior_no_action_specified(self, bot_directory, workspace_directory):
        """
        SCENARIO: Trigger bot and behavior (no action specified)
        GIVEN: user types message containing behavior-specific trigger words
        AND: behavior is at specific action from workflow state
        WHEN: Extension intercepts user message
        THEN: Extension identifies bot and behavior from trigger patterns
        AND: Extension routes to behavior using current action from state
        AND: CLI executes behavior with current action
        """
        # Arrange: Set up bot with behavior-level triggers
        behavior_triggers = {
            'shape': 'kick off shaping for a new feature',
            'prioritization': 'rank the backlog for launch',
            'arrange': 'arrange the feature map layout',
            'discovery': 'start discovery for the new product',
            'exploration': 'begin the exploration phase',
            'scenarios': 'draft behavior scenarios',
            'examples': 'prepare usage examples',
            'tests': 'design test coverage'
        }
        
        setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_behavior_triggers(
            {behavior: [trigger] for behavior, trigger in behavior_triggers.items()}
        )
        
        helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
        
        # Act & Assert: Test all behavior/action combinations
        for behavior, trigger_message in behavior_triggers.items():
            for current_action in setup.actions:
                setup.create_workflow_state(behavior, current_action)
                
                route, result = helper.match_and_execute(
                    trigger_message,
                    current_behavior=behavior,
                    current_action=current_action
                )
                
                # Verify route is correct
                helper.assert_route(route, setup.bot_name, behavior, current_action, 'bot_and_behavior')
                
                # Verify CLI executed - note initialize_workspace auto-advances to gather_context
                expected_action = 'gather_context' if current_action == 'initialize_workspace' else current_action
                helper.assert_cli_result(result, behavior, expected_action)

    def test_trigger_bot_behavior_and_action_explicitly(self, bot_directory, workspace_directory):
        """
        SCENARIO: Trigger bot, behavior, and action explicitly
        GIVEN: user types message containing action-specific trigger words
        WHEN: Extension intercepts user message
        THEN: Extension identifies bot, behavior, and action from trigger patterns
        AND: Extension routes directly to specified action
        AND: CLI executes specified action
        """
        # Arrange: Set up bot with action-level triggers for all combinations
        action_trigger_templates = {
            'initialize_workspace': 'set up the workspace area for {behavior}',
            'gather_context': 'gather context for {behavior}',
            'decide_planning_criteria': 'decide planning criteria for {behavior}',
            'build_knowledge': 'build the knowledge base for {behavior}',
            'render_output': 'render outputs for {behavior}',
            'validate_rules': 'validate outputs for {behavior}'
        }
        
        setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot()
        
        for behavior in setup.behaviors:
            for action, template in action_trigger_templates.items():
                trigger = template.format(behavior=behavior)
                setup.add_action_triggers(behavior, action, [trigger])
        
        helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
        
        # Act & Assert: Test all behavior/action combinations
        for behavior in setup.behaviors:
            for action, template in action_trigger_templates.items():
                trigger_message = template.format(behavior=behavior)
                
                route, result = helper.match_and_execute(
                    trigger_message,
                    current_behavior=None,  # Not needed for explicit triggers
                    current_action=None
                )
                
                # Verify route is correct
                helper.assert_route(route, setup.bot_name, behavior, action, 'bot_behavior_action')
                
                # Verify CLI executed - note initialize_workspace auto-advances to gather_context
                expected_action = 'gather_context' if action == 'initialize_workspace' else action
                helper.assert_cli_result(result, behavior, expected_action)
    
    def test_trigger_close_current_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Trigger close current action
        GIVEN: user types message containing close trigger words
        AND: bot is at specific behavior and action from workflow state
        WHEN: Extension intercepts user message
        THEN: Extension identifies close action from trigger patterns
        AND: Extension routes to close_current_action
        AND: CLI closes current action and advances workflow
        """
        # Arrange: Set up bot with close trigger words
        setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_bot_triggers([
            'close current action',
            'done with this step',
            'continue to next action'
        ])
        
        helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
        trigger_message = 'done with this step'
        
        # Act & Assert: Test close for all behavior/action combinations
        for current_behavior in setup.behaviors:
            for current_action in setup.actions:
                setup.create_workflow_state(current_behavior, current_action)
                
                route, result = helper.match_and_execute(
                    trigger_message,
                    current_behavior=current_behavior,
                    current_action=current_action
                )
                
                # Verify close trigger
                assert route is not None, f"Failed for {current_behavior}.{current_action}"
                assert route['bot_name'] == setup.bot_name
                assert route['action_name'] == 'close_current_action'
                assert route['match_type'] == 'close'
                assert result['status'] == 'success'
