"""
Invoke Bot CLI Tests

Tests for CLI increment stories:
- Invoke Bot CLI
- Invoke Bot Behavior CLI  
- Invoke Bot Behavior Action CLI

Tests use BaseBotCli pattern from cli_invocation_pattern.md.
CLI routes to bot, bot executes. Tests verify CLI routing and bot execution.
"""
import pytest
from pathlib import Path
import json
from conftest import (
    create_bot_config_file,
    create_workflow_state_file,
    create_base_actions_structure,
    create_bot_dir,
    create_project_dir,
    create_current_project_file
)

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
        'initialize_project': '1_initialize_project',
        'gather_context': '2_gather_context',
        'decide_planning_criteria': '3_decide_planning_criteria',
        'build_knowledge': '4_build_knowledge',
        'render_output': '5_render_output',
        'validate_rules': '7_validate_rules'
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

def setup_bot_for_testing(workspace: Path, bot_name: str, behaviors: list, project_dir: Path = None):
    """Helper: Set up complete bot structure for testing."""
    # Create bot config
    bot_config = create_bot_config_file(workspace, bot_name, behaviors)
    
    # Create base actions structure
    create_base_actions_structure(workspace)
    
    # Create project directory and current_project.json
    if project_dir is None:
        project_dir = create_project_dir(workspace)
    create_current_project_file(workspace, bot_name, str(project_dir))
    
    # Create base action instructions
    for action in ['initialize_project', 'gather_context', 'decide_planning_criteria', 
                   'build_knowledge', 'render_output', 'validate_rules']:
        create_base_action_instructions(workspace, action)
    
    return bot_config, project_dir

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path
    return workspace

# ============================================================================
# TEST CLASSES - Following CLI Invocation Pattern
# ============================================================================

class TestInvokeBotCli:
    """Story: Invoke Bot CLI - Tests CLI routing to current behavior/action from workflow state."""
    
    def test_invoke_bot_cli_with_workflow_state(self, workspace_root):
        """
        SCENARIO: Invoke bot CLI with workflow state (happy_path)
        GIVEN: workflow state contains current_behavior="story_bot.exploration"
        AND: workflow state contains current_action="story_bot.exploration.gather_context"
        AND: workflow_state.json exists
        WHEN: Human executes CLI command "./story_bot"
        THEN: CLI loads bot configuration
        AND: CLI loads workflow state
        AND: CLI routes to bot and invokes current behavior and current action
        AND: Bot executes action
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot with workflow state
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create workflow state
        workflow_file = create_workflow_state_file(
            project_dir,
            bot_name,
            'exploration',
            'gather_context',
            completed_actions=[]
        )
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Invoke CLI using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run()  # No args = route to current behavior/action
        
        # Then: Verify CLI routing and bot execution
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'gather_context'
        
        # Verify action is NOT marked as completed
        state_data = json.loads(workflow_file.read_text())
        assert len(state_data['completed_actions']) == 0
    
    def test_invoke_bot_cli_without_workflow_state(self, workspace_root):
        """
        SCENARIO: Invoke bot CLI without workflow state (edge_case)
        GIVEN: workflow_state.json does NOT exist
        WHEN: Human executes CLI command "./story_bot"
        THEN: CLI loads bot configuration
        AND: CLI detects workflow_state.json does not exist
        AND: CLI defaults to first behavior "story_bot.exploration"
        AND: CLI defaults to first action "story_bot.exploration.initialize_project"
        AND: CLI routes to bot and invokes first behavior and first action
        AND: Bot executes action
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot WITHOUT workflow state
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Verify workflow state does not exist
        workflow_file = project_dir / 'workflow_state.json'
        assert not workflow_file.exists()
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'initialize_project')
        
        # When: Invoke CLI using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run()  # No args = route to current behavior/action (defaults to first)
        
        # Then: Verify CLI defaults to first behavior/action
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'initialize_project'
    
    def test_invoke_bot_cli_with_invalid_bot_name(self, workspace_root):
        """
        SCENARIO: Invoke bot CLI with invalid bot name (error_case)
        GIVEN: bot configuration does NOT exist at specified path
        WHEN: Human executes CLI command "./invalid_bot"
        THEN: CLI attempts to load bot configuration
        AND: CLI detects bot configuration does not exist
        AND: CLI returns error message
        AND: CLI exits with exit code 1
        """
        # Given: Invalid bot config path
        bot_name = 'invalid_bot'
        invalid_config_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'config' / 'bot_config.json'
        
        # When: Attempt to create CLI with invalid config
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        with pytest.raises(Exception):  # Bot initialization should fail
            cli = BaseBotCli(
                bot_name=bot_name,
                bot_config_path=invalid_config_path,
                workspace_root=workspace_root
            )


class TestInvokeBotBehaviorCli:
    """Story: Invoke Bot Behavior CLI - Tests CLI routing to behavior with auto-forward to current action."""
    
    def test_invoke_bot_behavior_cli_with_workflow_state(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior CLI with workflow state (happy_path)
        GIVEN: workflow state contains current_action="story_bot.exploration.gather_context" for behavior "exploration"
        AND: workflow_state.json exists
        WHEN: Human executes CLI command "./story_bot exploration"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "exploration" exists
        AND: CLI loads workflow state
        AND: CLI routes to bot and specified behavior "exploration"
        AND: CLI extracts current_action from workflow state
        AND: CLI routes to current action in behavior
        AND: Bot executes action
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot with workflow state
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create workflow state
        workflow_file = create_workflow_state_file(
            project_dir,
            bot_name,
            'exploration',
            'gather_context',
            completed_actions=[]
        )
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Invoke CLI with behavior name using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run(behavior_name='exploration')  # Route to behavior, auto-forward to current action
        
        # Then: Verify CLI routing and bot execution
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'gather_context'
        
        # Verify action is NOT marked as completed
        state_data = json.loads(workflow_file.read_text())
        assert len(state_data['completed_actions']) == 0
    
    def test_invoke_bot_behavior_cli_without_workflow_state(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior CLI without workflow state (edge_case)
        GIVEN: workflow_state.json does NOT exist
        WHEN: Human executes CLI command "./story_bot exploration"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "exploration" exists
        AND: CLI detects workflow_state.json does not exist
        AND: CLI defaults to first action "story_bot.exploration.initialize_project" of behavior "exploration"
        AND: CLI routes to bot and behavior "exploration"
        AND: CLI routes to first action
        AND: Bot executes action
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot WITHOUT workflow state
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Verify workflow state does not exist
        workflow_file = project_dir / 'workflow_state.json'
        assert not workflow_file.exists()
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'initialize_project')
        
        # When: Invoke CLI with behavior name using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run(behavior_name='exploration')  # Route to behavior, defaults to first action
        
        # Then: Verify CLI defaults to first action
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'initialize_project'
    
    def test_invoke_bot_behavior_cli_with_invalid_behavior(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior CLI with invalid behavior (error_case)
        GIVEN: behavior "invalid_behavior" does NOT exist in bot configuration
        WHEN: Human executes CLI command "./story_bot invalid_behavior"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "invalid_behavior" does not exist
        AND: CLI returns error message
        AND: CLI exits with exit code 1
        """
        # Given: Set up bot with valid behaviors only
        bot_name = 'story_bot'
        behaviors = ['exploration', 'shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # When: Attempt to invoke CLI with invalid behavior using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        # Then: Should raise AttributeError when trying to access invalid behavior
        with pytest.raises(AttributeError):
            cli.run(behavior_name='invalid_behavior')


class TestInvokeBotBehaviorActionCli:
    """Story: Invoke Bot Behavior Action CLI - Tests CLI routing directly to specific behavior action."""
    
    def test_invoke_bot_behavior_action_cli_with_parameters(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior action CLI with parameters (happy_path)
        WHEN: Human executes CLI command "./story_bot exploration gather_context --increment_file=increment-cli-exploration.txt"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "exploration" exists
        AND: CLI validates action "gather_context" exists
        AND: CLI loads workflow state if it exists
        AND: CLI routes to bot and specified behavior "exploration" and action "gather_context"
        AND: CLI passes parameter "increment_file"="increment-cli-exploration.txt" to action
        AND: Bot executes action "gather_context" with parameters
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Invoke CLI with behavior, action, and parameters using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run(
            behavior_name='exploration',
            action_name='gather_context',
            increment_file='increment-cli-exploration.txt'
        )
        
        # Then: Verify CLI routing and bot execution with parameters
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'gather_context'
    
    def test_invoke_bot_behavior_action_cli_without_parameters(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior action CLI without parameters (happy_path)
        WHEN: Human executes CLI command "./story_bot exploration gather_context"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "exploration" exists
        AND: CLI validates action "gather_context" exists
        AND: CLI loads workflow state if it exists
        AND: CLI routes to bot and specified behavior "exploration" and action "gather_context"
        AND: Bot executes action "gather_context" without parameters
        AND: CLI returns result with status="success"
        AND: Action is NOT marked as completed (human must close action separately)
        """
        # Given: Set up bot
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Invoke CLI with behavior and action (no parameters) using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        result = cli.run(
            behavior_name='exploration',
            action_name='gather_context'
        )
        
        # Then: Verify CLI routing and bot execution
        assert result['status'] == 'success'
        assert result['behavior'] == 'exploration'
        assert result['action'] == 'gather_context'
    
    def test_invoke_bot_behavior_action_cli_with_invalid_action(self, workspace_root):
        """
        SCENARIO: Invoke bot behavior action CLI with invalid action (error_case)
        GIVEN: action "invalid_action" does NOT exist in behavior "exploration"
        WHEN: Human executes CLI command "./story_bot exploration invalid_action"
        THEN: CLI loads bot configuration
        AND: CLI validates behavior "exploration" exists
        AND: CLI validates action "invalid_action" does not exist
        AND: CLI returns error message
        AND: CLI exits with exit code 1
        """
        # Given: Set up bot with valid behavior
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create behavior action instructions (but NOT for invalid_action)
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Attempt to invoke CLI with invalid action using BaseBotCli pattern
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        # Then: Should raise AttributeError when trying to access invalid action
        with pytest.raises(AttributeError):
            cli.run(behavior_name='exploration', action_name='invalid_action')


class TestGenerateCursorCommands:
    """Story: Generate Cursor Commands - Tests cursor command file generation."""
    
    def test_generate_cursor_commands_creates_all_files(self, workspace_root):
        """
        SCENARIO: Generate cursor command files (happy_path)
        GIVEN: CLI instance is initialized
        AND: commands directory path is provided
        AND: CLI script path is provided
        WHEN: Human calls generate_cursor_commands()
        THEN: CLI creates .cursor/commands directory
        AND: CLI creates bot command file
        AND: CLI creates bot-behavior command file
        AND: CLI creates bot-behavior-action command file
        AND: CLI creates bot-close command file
        AND: Each command file contains correct CLI invocation
        """
        # Given: Set up bot
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        commands_dir = workspace_root / '.cursor' / 'commands'
        cli_script_path = Path('agile_bot/bots/story_bot/story_bot')
        
        # Create behavior action instructions to ensure actions are detected
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'build_knowledge')
        
        # When: Generate cursor commands
        commands = cli.generate_cursor_commands(commands_dir, cli_script_path)
        
        # Then: Verify bot command created
        assert f'{bot_name}' in commands
        bot_cmd = commands[f'{bot_name}']
        assert bot_cmd.exists()
        assert bot_cmd.name == f'{bot_name}.md'
        assert bot_cmd.read_text(encoding='utf-8') == f"{cli_script_path} {bot_name}"
        
        # Verify behavior command created
        assert f'{bot_name}-exploration' in commands
        behavior_cmd = commands[f'{bot_name}-exploration']
        assert behavior_cmd.exists()
        assert behavior_cmd.name == f'{bot_name}-exploration.md'
        assert behavior_cmd.read_text(encoding='utf-8') == f"{cli_script_path} {bot_name} exploration"
        
        # Verify action commands created (at least gather_context and build_knowledge)
        assert f'{bot_name}-exploration-gather_context' in commands
        action_cmd = commands[f'{bot_name}-exploration-gather_context']
        assert action_cmd.exists()
        assert action_cmd.name == f'{bot_name}-exploration-gather_context.md'
        assert action_cmd.read_text(encoding='utf-8') == f"{cli_script_path} {bot_name} exploration gather_context"
        
        # Verify close command created
        assert f'{bot_name}-close' in commands
        close_cmd = commands[f'{bot_name}-close']
        assert close_cmd.exists()
        assert close_cmd.name == f'{bot_name}-close.md'
        assert close_cmd.read_text(encoding='utf-8') == f"{cli_script_path} {bot_name} --close"
    
    def test_generate_cursor_commands_creates_directory(self, workspace_root):
        """
        SCENARIO: Generate cursor commands creates directory if missing (edge_case)
        GIVEN: CLI instance is initialized
        AND: commands directory does NOT exist
        WHEN: Human calls generate_cursor_commands()
        THEN: CLI creates .cursor/commands directory
        AND: CLI creates all command files
        """
        # Given: Set up bot
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        commands_dir = workspace_root / '.cursor' / 'commands'
        cli_script_path = Path('agile_bot/bots/story_bot/story_bot')
        
        # Verify directory doesn't exist
        assert not commands_dir.exists()
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # When: Generate cursor commands
        commands = cli.generate_cursor_commands(commands_dir, cli_script_path)
        
        # Then: Verify directory created
        assert commands_dir.exists()
        assert commands_dir.is_dir()
        
        # Verify files created (bot, behavior, actions, close)
        assert len(commands) >= 4
        assert f'{bot_name}' in commands
        assert f'{bot_name}-exploration' in commands
        assert f'{bot_name}-exploration-gather_context' in commands
        assert f'{bot_name}-close' in commands
    
    def test_generate_cursor_commands_removes_obsolete_files(self, workspace_root):
        """
        SCENARIO: Generate cursor commands removes obsolete files when behavior removed (edge_case)
        GIVEN: CLI instance is initialized
        AND: Bot previously had behavior "old_behavior"
        AND: Obsolete command file exists for removed behavior
        AND: Bot no longer has behavior "old_behavior"
        WHEN: Human calls generate_cursor_commands()
        THEN: CLI creates new command files for current behaviors
        AND: CLI removes obsolete command files for removed behaviors
        """
        # Given: Set up bot with one behavior
        bot_name = 'story_bot'
        behaviors = ['exploration']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        commands_dir = workspace_root / '.cursor' / 'commands'
        cli_script_path = Path('agile_bot/bots/story_bot/story_bot')
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # Generate initial commands (with old_behavior)
        old_behavior_file = commands_dir / f'{bot_name}-old_behavior.md'
        old_action_file = commands_dir / f'{bot_name}-old_behavior-old_action.md'
        commands_dir.mkdir(parents=True, exist_ok=True)
        old_behavior_file.write_text(f'{cli_script_path} {bot_name} old_behavior', encoding='utf-8')
        old_action_file.write_text(f'{cli_script_path} {bot_name} old_behavior old_action', encoding='utf-8')
        
        # Verify obsolete files exist
        assert old_behavior_file.exists()
        assert old_action_file.exists()
        
        # When: Generate cursor commands (bot no longer has old_behavior)
        commands = cli.generate_cursor_commands(commands_dir, cli_script_path)
        
        # Then: Verify obsolete files removed
        assert not old_behavior_file.exists()
        assert not old_action_file.exists()
        
        # Verify current files created
        assert f'{bot_name}' in commands
        assert f'{bot_name}-exploration' in commands
        assert f'{bot_name}-close' in commands

