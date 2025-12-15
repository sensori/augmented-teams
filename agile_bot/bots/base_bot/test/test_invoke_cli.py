"""
Invoke CLI Tests

Tests for all stories in the 'Invoke CLI' sub-epic:
- Invoke Bot CLI
- Invoke Bot Behavior CLI  
- Invoke Bot Behavior Action CLI
- Get Help for Command Line Functions
- Detect Trigger Words Through Extension
- Save Through CLI

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
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, create_behavior_action_instructions,
    then_route_matches_expected, then_cli_result_matches_expected
)
from agile_bot.bots.base_bot.test.test_helpers import (
    create_base_action_instructions
)
from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json

# ============================================================================
# HELPER CLASSES
# ============================================================================

class TriggerTestSetup:
    """Helper class to set up bot with trigger words for testing."""
    
    def __init__(self, bot_directory: Path, workspace_directory: Path, bot_name: str = 'story_bot'):
        self.bot_directory = bot_directory
        self.workspace_directory = workspace_directory
        self.bot_name = bot_name
        self.behaviors = ['shape', 'prioritization', 'arrange', 'discovery', 'exploration', 'scenarios', 'examples', 'write_tests']
        self.actions = ['initialize_workspace', 'gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
        self.bot_config = None
    
    def setup_bot(self):
        """Set up bot with all behaviors and actions."""
        workspace_root = self.bot_directory.parent.parent.parent
        self.bot_config = setup_bot_for_testing(workspace_root, self.bot_name, self.behaviors)
        self._setup_behavior_folders_and_knowledge_graphs(workspace_root)
        self._create_story_graph_file()
        return self
    
    def _setup_behavior_folders_and_knowledge_graphs(self, workspace_root: Path):
        """Set up behavior folders with behavior.json files and knowledge graph configs."""
        behaviors_dir = workspace_root / 'agile_bot' / 'bots' / self.bot_name / 'behaviors'
        bot_dir = workspace_root / 'agile_bot' / 'bots' / self.bot_name
        for behavior in self.behaviors:
            behavior_dir = behaviors_dir / behavior
            behavior_dir.mkdir(parents=True, exist_ok=True)
            create_actions_workflow_json(bot_dir, behavior)
            self._create_knowledge_graph_config(behavior_dir)
    
    def _create_knowledge_graph_config(self, behavior_dir: Path):
        """Create knowledge graph folder and config files for a behavior."""
        kg_dir = behavior_dir / 'content' / 'knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        template_filename = 'test_template.json'
        kg_config = {'template': template_filename}
        (kg_dir / 'build_story_graph_outline.json').write_text(
            json.dumps(kg_config), encoding='utf-8'
        )
        template_content = {'instructions': ['Test knowledge graph template']}
        (kg_dir / template_filename).write_text(
            json.dumps(template_content), encoding='utf-8'
        )
    
    def _create_story_graph_file(self):
        """Create story graph file in workspace for validate_rules action."""
        stories_dir = self.workspace_directory / 'docs' / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        story_graph_file = stories_dir / 'story-graph.json'
        story_graph_file.write_text(json.dumps({
            'epics': [],
            'solution': {'name': 'Test Solution'}
        }), encoding='utf-8')
    
    def add_bot_triggers(self, patterns: list):
        """Add bot-level trigger words."""
        # workspace_root is bot_directory's parent.parent.parent (tmp_path)
        workspace_root = self.bot_directory.parent.parent.parent
        create_bot_trigger_words(workspace_root, self.bot_name, patterns)
        return self
    
    def add_behavior_triggers(self, behavior_patterns: dict):
        """Add behavior-level trigger words.
        
        
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
    
    def _create_router_and_match(self, trigger_message: str, current_behavior: str = None, current_action: str = None):
        """Helper: Create router and match trigger."""
        from agile_bot.bots.base_bot.src.cli.trigger_router import TriggerRouter
        workspace_root = self.workspace_directory.parent
        router = TriggerRouter(workspace_root=workspace_root, bot_name=self.bot_name)
        return router.match_trigger(
            message=trigger_message,
            current_behavior=current_behavior,
            current_action=current_action
        )
    
    def _create_cli_and_execute(self, route: dict, trigger_message: str):
        """Helper: Create CLI instance and execute route."""
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        from agile_bot.bots.base_bot.test.conftest import bootstrap_env
        
        bootstrap_env(self.bot_directory, self.workspace_directory)
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
        
        return result
    
    def match_and_execute(self, trigger_message: str, current_behavior: str = None, current_action: str = None):
        """Match trigger and execute via CLI.
        
        Creates fresh router and CLI instances for each call to avoid state leakage.
        
        
        """
        route = self._create_router_and_match(trigger_message, current_behavior, current_action)
        if route is None:
            return None, None
        
        result = self._create_cli_and_execute(route, trigger_message)
        return route, result
    
    def assert_route(self, route, expected_bot: str, expected_behavior: str, expected_action: str, expected_type: str):
        """Assert route matches expected values."""
        then_route_matches_expected(route, expected_bot, expected_behavior, expected_action, expected_type)
    
    def assert_cli_result(self, result, expected_behavior: str, expected_action: str):
        """Assert CLI result matches expected values."""
        then_cli_result_matches_expected(result, expected_behavior, expected_action)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Removed create_behavior_action_instructions - use test_helpers.create_behavior_action_instructions instead
# Removed create_base_action_instructions - use test_helpers.create_base_action_instructions instead
# Consolidated helper functions from test_invoke_bot_cli.py

def create_base_action_instructions_duplicate_removed(workspace: Path, action: str) -> Path:
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

def create_bot_trigger_words(workspace: Path, bot_name: str, patterns: list) -> Path:
    """Helper: Create bot-level trigger words file."""
    trigger_dir = workspace / 'agile_bot' / 'bots' / bot_name
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_data = {'patterns': patterns}
    trigger_file.write_text(json.dumps(trigger_data), encoding='utf-8')
    return trigger_file

def create_behavior_trigger_words(workspace: Path, bot_name: str, behavior: str, patterns: list) -> Path:
    """Helper: Create behavior-level trigger words in behavior.json (new format)."""
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    # Create or update behavior.json file with trigger words (REQUIRED after refactor)
    behavior_dir = bot_dir / 'behaviors' / behavior
    behavior_dir.mkdir(parents=True, exist_ok=True)
    behavior_file = behavior_dir / 'behavior.json'
    
    # Load existing behavior.json or create new one
    if behavior_file.exists():
        behavior_data = json.loads(behavior_file.read_text())
    else:
        create_actions_workflow_json(bot_dir, behavior)
        behavior_data = json.loads(behavior_file.read_text())
    
    # Update trigger_words in behavior.json (router reads from behavior.json now)
    behavior_data['trigger_words'] = {
        'description': f'Trigger words for {behavior}',
        'patterns': patterns,
        'priority': 10
    }
    behavior_file.write_text(json.dumps(behavior_data, indent=2), encoding='utf-8')
    return behavior_file

def create_action_trigger_words(workspace: Path, bot_name: str, behavior: str, action: str, patterns: list) -> Path:
    """Helper: Create action-level trigger words file."""
    action_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    action_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = action_dir / 'trigger_words.json'
    trigger_data = {'patterns': patterns}
    trigger_file.write_text(json.dumps(trigger_data), encoding='utf-8')
    return trigger_file

def when_execute_trigger_for_all_behaviors_and_actions(setup, helper, trigger_message, current_behavior=None, current_action=None):
    """When: Execute trigger for all behaviors and actions."""
    for behavior in setup.behaviors:
        for action in setup.actions:
            if current_behavior is None:
                test_behavior = behavior
            else:
                test_behavior = current_behavior
            if current_action is None:
                test_action = action
            else:
                test_action = current_action
            setup.create_workflow_state(test_behavior, test_action)
            
            route, result = helper.match_and_execute(
                trigger_message,
                current_behavior=test_behavior,
                current_action=test_action
            )
            
            yield behavior, action, route, result

def then_verify_route_and_result_for_bot_only(setup, helper, behavior, action, route, result, trigger_message):
    """Then: Verify route and result for bot-only trigger."""
    helper.assert_route(route, setup.bot_name, behavior, action, 'bot_only')
    expected_action = 'gather_context' if action == 'initialize_workspace' else action
    helper.assert_cli_result(result, behavior, expected_action)

def then_verify_route_and_result_for_bot_and_behavior(setup, helper, behavior, action, route, result, trigger_message):
    """Then: Verify route and result for bot and behavior trigger."""
    helper.assert_route(route, setup.bot_name, behavior, action, 'bot_and_behavior')
    expected_action = 'gather_context' if action == 'initialize_workspace' else action
    helper.assert_cli_result(result, behavior, expected_action)

def then_verify_route_and_result_for_explicit_action(setup, helper, behavior, action, route, result):
    """Then: Verify route and result for explicit action trigger."""
    helper.assert_route(route, setup.bot_name, behavior, action, 'bot_behavior_action')
    expected_action = 'gather_context' if action == 'initialize_workspace' else action
    helper.assert_cli_result(result, behavior, expected_action)

def then_verify_close_trigger_route_and_result(setup, route, result):
    """Then: Verify close trigger route and result."""
    assert route is not None, f"Failed for {setup.bot_name}"
    assert route['bot_name'] == setup.bot_name
    assert route['action_name'] == 'close_current_action'
    assert route['match_type'] == 'close'
    assert result['status'] == 'success'

def when_setup_action_triggers_for_all_behaviors(setup, action_trigger_templates: dict):
    """When: Setup action triggers for all behaviors."""
    for behavior in setup.behaviors:
        for action, template in action_trigger_templates.items():
            trigger = template.format(behavior=behavior)
            setup.add_action_triggers(behavior, action, [trigger])

def given_trigger_router_helper_and_message(setup, trigger_message: str):
    """Given step: Create trigger router helper and set trigger message."""
    helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
    return helper, trigger_message

def when_test_all_behavior_action_combinations(setup, helper, trigger_message, verify_func, current_behavior=None, current_action=None):
    """When step: Test all behavior/action combinations."""
    for behavior in (setup.behaviors if current_behavior is None else [current_behavior]):
        for action in (setup.actions if current_action is None else [current_action]):
            setup.create_workflow_state(behavior, action)
            route, result = helper.match_and_execute(
                trigger_message,
                current_behavior=behavior,
                current_action=action
            )
            verify_func(setup, helper, behavior, action, route, result, trigger_message)

def given_standard_behavior_triggers_dict():
    """Given: Standard behavior triggers dictionary."""
    return {
        'shape': 'kick off shaping for a new feature',
        'prioritization': 'rank the backlog for launch',
        'arrange': 'arrange the feature map layout',
        'discovery': 'start discovery for the new product',
        'exploration': 'begin the exploration phase',
        'scenarios': 'draft behavior scenarios',
        'examples': 'prepare usage examples',
        'write_tests': 'design test coverage'
    }

def given_bot_setup_with_behavior_triggers(bot_directory: Path, workspace_directory: Path, behavior_triggers: dict):
    """Given: Bot setup with behavior triggers."""
    return TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_behavior_triggers(
        {behavior: [trigger] for behavior, trigger in behavior_triggers.items()}
    )

def given_action_trigger_templates_dict():
    """Given: Action trigger templates dictionary."""
    return {
        'initialize_workspace': 'set up the workspace area for {behavior}',
        'gather_context': 'gather context for {behavior}',
        'decide_planning_criteria': 'decide planning criteria for {behavior}',
        'build_knowledge': 'build the knowledge base for {behavior}',
        'render_output': 'render outputs for {behavior}',
        'validate_rules': 'validate outputs for {behavior}'
    }

def given_bot_setup_with_action_triggers(bot_directory: Path, workspace_directory: Path, action_trigger_templates: dict):
    """Given: Bot setup with action triggers."""
    return TriggerTestSetup(bot_directory, workspace_directory).setup_bot()

def when_cli_created_with_mock_bot(mock_bot):
    """When: CLI created with mock bot."""
    from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
    return BaseBotCli(bot=mock_bot)

def given_behavior_triggers_dictionary():
    """Given step: Create behavior triggers dictionary."""
    return {
        'shape': 'kick off shaping for a new feature',
        'prioritization': 'rank the backlog for launch',
        'arrange': 'organize the stories',
        'discovery': 'discover the user flows',
        'exploration': 'explore the domain',
        'scenarios': 'write the scenarios',
        'examples': 'create examples',
        'write_tests': 'write the tests'
    }

def when_test_all_behaviors_with_triggers(setup, helper, behavior_triggers: dict, verify_func):
    """When step: Test all behaviors with their triggers."""
    for behavior, trigger_message in behavior_triggers.items():
        for current_action in setup.actions:
            setup.create_workflow_state(behavior, current_action)
            route, result = helper.match_and_execute(
                trigger_message,
                current_behavior=behavior,
                current_action=current_action
            )
            verify_func(setup, helper, behavior, current_action, route, result, trigger_message)

def given_action_trigger_templates_dictionary():
    """Given step: Create action trigger templates dictionary."""
    return {
        'initialize_workspace': 'set up the workspace area for {behavior}',
        'gather_context': 'gather context for {behavior}',
        'decide_planning_criteria': 'decide planning criteria for {behavior}',
        'build_knowledge': 'build knowledge for {behavior}',
        'validate_rules': 'validate rules for {behavior}',
        'render_output': 'render output for {behavior}'
    }

def when_test_all_behaviors_with_action_templates(setup, helper, action_trigger_templates: dict, verify_func):
    """When step: Test all behaviors with action trigger templates."""
    for behavior in setup.behaviors:
        for action, template in action_trigger_templates.items():
            trigger_message = template.format(behavior=behavior)
            route, result = helper.match_and_execute(
                trigger_message,
                current_behavior=None,  # Not needed for explicit triggers
                current_action=None
            )
            verify_func(setup, helper, behavior, action, route, result)

def _create_base_action_instructions(workspace_root: Path):
    """Helper: Create base action instructions."""
    actions = ['initialize_workspace', 'gather_context', 'decide_planning_criteria', 
               'build_knowledge', 'validate_rules', 'render_output']
    for action in actions:
        create_base_action_instructions(workspace_root, action)

def setup_bot_for_testing(workspace_root: Path, bot_name: str, behaviors: list):
    """Helper: Set up complete bot structure for testing.
    
    
    """
    bot_dir = workspace_root / 'agile_bot' / 'bots' / bot_name
    bot_config = create_bot_config_file(bot_dir, bot_name, behaviors)
    create_base_actions_structure(bot_dir)
    _create_base_action_instructions(workspace_root)
    return bot_config

# Removed then_route_matches_expected and then_cli_result_matches_expected - imported from test_helpers
# Removed duplicate helper functions - imported from test_invoke_bot_cli.py above

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
        
        # Given: Trigger router helper and message
        helper, trigger_message = given_trigger_router_helper_and_message(setup, 'lets work on stories')
        
        # When: Test all behavior/action combinations
        when_test_all_behavior_action_combinations(setup, helper, trigger_message, then_verify_route_and_result_for_bot_only)

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
        behavior_triggers = given_standard_behavior_triggers_dict()
        setup = given_bot_setup_with_behavior_triggers(bot_directory, workspace_directory, behavior_triggers)
        
        # Given: Trigger router helper
        helper, _ = given_trigger_router_helper_and_message(setup, '')
        
        # When: Test all behaviors with triggers
        when_test_all_behaviors_with_triggers(setup, helper, behavior_triggers, then_verify_route_and_result_for_bot_and_behavior)

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
        action_trigger_templates = given_action_trigger_templates_dict()
        setup = given_bot_setup_with_action_triggers(bot_directory, workspace_directory, action_trigger_templates)
        
        when_setup_action_triggers_for_all_behaviors(setup, action_trigger_templates)
        
        # Given: Trigger router helper
        helper, _ = given_trigger_router_helper_and_message(setup, '')
        
        # When: Test all behaviors with action templates
        when_test_all_behaviors_with_action_templates(setup, helper, action_trigger_templates, then_verify_route_and_result_for_explicit_action)
    
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
        
        # Given: Trigger router helper and message
        helper, trigger_message = given_trigger_router_helper_and_message(setup, 'done with this step')
        
        # When: Test all behavior/action combinations for close trigger
        def verify_close(setup, helper, behavior, action, route, result, trigger_message):
            then_verify_close_trigger_route_and_result(setup, route, result)
        when_test_all_behavior_action_combinations(setup, helper, trigger_message, verify_close)


# ============================================================================
# EXCEPTION HANDLING TESTS
# ============================================================================

def given_mock_bot_created(tmp_path: Path, bot_name: str = 'test_bot'):
    """Given: Mock bot created."""
    from unittest.mock import Mock
    mock_bot = Mock()
    mock_bot.name = bot_name
    mock_bot.bot_directory = tmp_path / bot_name
    return mock_bot


def when_cli_infers_parameter_description_for_unknown_command(cli):
    """When: CLI infers parameter description for unknown command."""
    from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
    return cli._infer_parameter_description(
        cmd_name='unknown_command_xyz',
        param_num='1',
        cmd_content=''
    )


class TestCLIExceptions:
    """Tests for CLI exception handling - no fallbacks."""

    def test_cli_raises_exception_when_parameter_description_cannot_be_inferred(self, tmp_path):
        """
        SCENARIO: CLI raises exception when parameter description cannot be inferred
        GIVEN: Mock bot is created
        WHEN: CLI is created with mock bot
        AND: Inferring parameter description for unknown command
        THEN: ValueError is raised
        """
        # Given: Mock bot is created
        mock_bot = given_mock_bot_created(tmp_path)
        
        # When: CLI is created with mock bot
        cli = when_cli_created_with_mock_bot(mock_bot)
        
        # When: Inferring parameter description for unknown command
        # Then: ValueError is raised (verified by pytest.raises)
        with pytest.raises(ValueError, match="Cannot infer parameter description"):
            when_cli_infers_parameter_description_for_unknown_command(cli)
