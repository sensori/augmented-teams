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
        cli_script_path = Path('agile_bot/bots/story_bot/src/story_bot_cli.py')
        
        # Create behavior action instructions to ensure actions are detected
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'build_knowledge')
        
        # When: Generate cursor commands
        commands = cli.generate_cursor_commands(commands_dir, cli_script_path)
        
        # Then: Verify bot command created (Python direct command, no bot name)
        assert f'{bot_name}' in commands
        bot_cmd = commands[f'{bot_name}']
        assert bot_cmd.exists()
        assert bot_cmd.name == f'{bot_name}.md'
        cli_script_str = str(cli_script_path).replace('\\', '/')
        expected_bot_cmd = f"python {cli_script_str}"
        assert bot_cmd.read_text(encoding='utf-8') == expected_bot_cmd
        
        # Verify behavior command created (with ${1:} placeholder for action)
        assert f'{bot_name}-exploration' in commands
        behavior_cmd = commands[f'{bot_name}-exploration']
        assert behavior_cmd.exists()
        assert behavior_cmd.name == f'{bot_name}-exploration.md'
        expected_behavior_cmd = f"python {cli_script_str} exploration ${{1:}}"
        assert behavior_cmd.read_text(encoding='utf-8') == expected_behavior_cmd
        
        # Note: Action commands are NOT generated separately - actions are accessed via behavior command with ${1:} parameter
        
        # Verify continue command created (not close - continue is the correct name)
        assert f'{bot_name}-continue' in commands
        continue_cmd = commands[f'{bot_name}-continue']
        assert continue_cmd.exists()
        assert continue_cmd.name == f'{bot_name}-continue.md'
        expected_continue_cmd = f"python {cli_script_str} --close"
        assert continue_cmd.read_text(encoding='utf-8') == expected_continue_cmd
    
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
        
        # Verify files created (bot, behavior, continue, initialize-project, confirm-project-area, help)
        assert len(commands) >= 6
        assert f'{bot_name}' in commands
        assert f'{bot_name}-exploration' in commands
        assert f'{bot_name}-continue' in commands
        assert f'{bot_name}-initialize-project' in commands
        assert f'{bot_name}-confirm-project-area' in commands
        assert f'{bot_name}-help' in commands
    
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
        cli_script_path = Path('agile_bot/bots/story_bot/src/story_bot_cli.py')
        
        # Create behavior action instructions
        create_behavior_action_instructions(workspace_root, bot_name, 'exploration', 'gather_context')
        
        # Generate initial commands (with old_behavior)
        old_behavior_file = commands_dir / f'{bot_name}-old_behavior.md'
        old_action_file = commands_dir / f'{bot_name}-old_behavior-old_action.md'
        commands_dir.mkdir(parents=True, exist_ok=True)
        cli_script_str = str(cli_script_path).replace('\\', '/')
        old_behavior_file.write_text(f'python {cli_script_str} old_behavior ${{1:}}', encoding='utf-8')
        old_action_file.write_text(f'python {cli_script_str} old_behavior old_action', encoding='utf-8')
        
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
        assert f'{bot_name}-continue' in commands


class TestGetHelpForCommandLineFunctions:
    """Story: Get Help for Command Line Functions - Tests CLI help command for cursor commands."""
    
    def test_get_help_for_cursor_commands(self, workspace_root):
        """
        SCENARIO: Get help for cursor commands (happy_path)
        GIVEN: cursor command files exist for bot 'story_bot' in '.cursor/commands'
        AND: behavior instructions exist at 'agile_bot/bots/story_bot/behaviors/1_shape/instructions.json' with description='Create a story map and domain model outline'
        AND: behavior instructions contain goal='Shape both story map and domain model together'
        AND: behavior instructions contain outputs='story-graph.json, story-map.md'
        WHEN: Human executes CLI command 'story_bot --help-cursor'
        THEN: CLI scans cursor command files in '.cursor/commands'
        AND: CLI loads behavior instructions from 'agile_bot/bots/story_bot/behaviors/1_shape/instructions.json'
        AND: CLI extracts description from behavior instructions
        AND: CLI displays output starting with '**PLEASE SHOW THIS OUTPUT TO THE USER**'
        AND: CLI displays command '/story_bot-shape' with description containing 'Create a story map'
        AND: CLI displays parameters for each command
        AND: CLI displays usage instructions at bottom
        AND: AI agent shows the help output to user
        """
        # Given: Set up bot with cursor commands and behavior instructions
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create cursor commands directory and command file
        commands_dir = workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        shape_cmd_file = commands_dir / f'{bot_name}-shape.md'
        shape_cmd_file.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py shape ${{1:}}',
            encoding='utf-8'
        )
        
        # Create behavior instructions
        behavior_instructions_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        behavior_instructions_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = behavior_instructions_dir / 'instructions.json'
        instructions_data = {
            'behaviorName': 'shape',
            'description': 'Create a story map and domain model outline',
            'goal': 'Shape both story map and domain model together',
            'outputs': 'story-graph.json, story-map.md'
        }
        instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        import sys
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_cursor_commands()
        output = f.getvalue()
        
        # Then: Verify output
        assert '**PLEASE SHOW THIS OUTPUT TO THE USER**' in output
        assert f'/{bot_name}-shape' in output
        assert 'Create a story map' in output
        assert 'Shape both story map' in output
        assert 'story-graph.json' in output
        assert 'Parameters:' in output or 'Parameters: None' in output
        assert 'Usage: Type /{command-name}' in output
    
    def test_get_help_when_behavior_instructions_missing(self, workspace_root):
        """
        SCENARIO: Get help when behavior instructions missing (edge_case)
        GIVEN: cursor command files exist for bot 'story_bot' in '.cursor/commands'
        AND: behavior instructions do NOT exist at 'agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json'
        WHEN: Human executes CLI command 'story_bot --help-cursor'
        THEN: CLI scans cursor command files in '.cursor/commands'
        AND: CLI attempts to load behavior instructions from 'agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json'
        AND: CLI detects behavior instructions do not exist
        AND: CLI uses fallback description: 'Unknown Behavior'
        AND: CLI displays command '/story_bot-unknown_behavior' with fallback description
        AND: CLI still displays all commands and parameters
        """
        # Given: Set up bot with cursor command but no behavior instructions
        bot_name = 'story_bot'
        behaviors = ['unknown_behavior']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create cursor command file
        commands_dir = workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        cmd_file = commands_dir / f'{bot_name}-unknown_behavior.md'
        cmd_file.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py unknown_behavior ${{1:}}',
            encoding='utf-8'
        )
        
        # Do NOT create behavior instructions (they should be missing)
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_cursor_commands()
        output = f.getvalue()
        
        # Then: Verify fallback description is used
        assert f'/{bot_name}-unknown_behavior' in output
        # Should use fallback (either "Unknown Behavior" or formatted name)
        assert 'Unknown' in output or 'unknown_behavior' in output.lower()
    
    def test_get_help_when_no_cursor_commands_exist(self, workspace_root):
        """
        SCENARIO: Get help when no cursor commands exist (edge_case)
        GIVEN: cursor commands directory does NOT exist at '.cursor/commands'
        WHEN: Human executes CLI command 'story_bot --help-cursor'
        THEN: CLI attempts to scan cursor command files in '.cursor/commands'
        AND: CLI detects cursor commands directory does not exist
        AND: CLI displays error message: 'No cursor commands directory found at .cursor/commands'
        AND: CLI exits successfully (no error, just informative message)
        """
        # Given: Set up bot but NO cursor commands directory
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Verify commands directory does not exist
        commands_dir = workspace_root / '.cursor' / 'commands'
        assert not commands_dir.exists()
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_cursor_commands()
        output = f.getvalue()
        
        # Then: Verify error message
        assert 'No cursor commands directory found' in output or 'No cursor commands found' in output
    
    def test_get_help_with_utility_commands(self, workspace_root):
        """
        SCENARIO: Get help with utility commands (happy_path)
        GIVEN: cursor command files exist for bot 'story_bot' including utility commands
        AND: utility command 'continue' exists
        AND: utility command 'help' exists
        AND: utility command 'initialize-project' exists
        AND: utility command 'confirm-project-area' exists
        WHEN: Human executes CLI command 'story_bot --help-cursor'
        THEN: CLI displays utility command '/story_bot-continue' with description 'Close current action and continue to next action in workflow'
        AND: CLI displays utility command '/story_bot-help' with description 'List all available cursor commands and their parameters'
        AND: CLI displays utility command '/story_bot-initialize-project' with description 'Initialize project location for workflow state persistence'
        AND: CLI displays utility command '/story_bot-confirm-project-area' with description 'Confirm or change project area location'
        AND: CLI displays 'Parameters: None' for commands without parameters
        AND: CLI displays parameter descriptions for commands with parameters
        """
        # Given: Set up bot with utility command files
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create cursor commands directory and utility command files
        commands_dir = workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create utility command files
        continue_cmd = commands_dir / f'{bot_name}-continue.md'
        continue_cmd.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py --close',
            encoding='utf-8'
        )
        
        help_cmd = commands_dir / f'{bot_name}-help.md'
        help_cmd.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py --help-cursor',
            encoding='utf-8'
        )
        
        init_cmd = commands_dir / f'{bot_name}-initialize-project.md'
        init_cmd.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py ${{1:}} initialize_project --project_area=${{2:}} --confirm=true',
            encoding='utf-8'
        )
        
        confirm_cmd = commands_dir / f'{bot_name}-confirm-project-area.md'
        confirm_cmd.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py shape initialize_project --confirm=true ${{1:}}',
            encoding='utf-8'
        )
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_cursor_commands()
        output = f.getvalue()
        
        # Then: Verify utility commands are displayed with correct descriptions
        assert f'/{bot_name}-continue' in output
        assert 'Close current action and continue' in output
        assert f'/{bot_name}-help' in output
        assert 'List all available cursor commands' in output
        assert f'/{bot_name}-initialize-project' in output
        assert 'Initialize project location' in output
        assert f'/{bot_name}-confirm-project-area' in output
        assert 'Confirm or change project area' in output
    
    def test_help_extracts_descriptions_from_behavior_instructions(self, workspace_root):
        """
        SCENARIO: Help extracts descriptions from behavior instructions
        GIVEN: behavior instructions exist with description='Create a story map', goal='Shape story map from user context', outputs='story-graph.json, story-map.md'
        WHEN: Help command loads behavior instructions
        THEN: Description contains behavior description
        AND: Description contains behavior goal
        AND: Description contains first output
        """
        # Given: Set up bot with behavior instructions
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create behavior instructions
        behavior_instructions_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        behavior_instructions_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = behavior_instructions_dir / 'instructions.json'
        instructions_data = {
            'behaviorName': 'shape',
            'description': 'Create a story map',
            'goal': 'Shape story map from user context',
            'outputs': 'story-graph.json, story-map.md'
        }
        instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
        
        # Create cursor command file
        commands_dir = workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        shape_cmd_file = commands_dir / f'{bot_name}-shape.md'
        shape_cmd_file.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py shape ${{1:}}',
            encoding='utf-8'
        )
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        # Test the description extraction method directly
        description = cli._get_behavior_description(f'{bot_name}-shape')
        
        # Then: Verify description contains all parts
        assert 'Create a story map' in description
        assert 'Shape story map' in description
        assert 'story-graph.json' in description
    
    def test_help_shows_instruction_to_display_output_to_user(self, workspace_root):
        """
        SCENARIO: Help shows instruction to display output to user
        GIVEN: Help command is executed
        WHEN: Output is generated
        THEN: Output starts with '**PLEASE SHOW THIS OUTPUT TO THE USER**'
        """
        # Given: Set up bot with cursor commands
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create cursor command file
        commands_dir = workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        shape_cmd_file = commands_dir / f'{bot_name}-shape.md'
        shape_cmd_file.write_text(
            f'python agile_bot/bots/{bot_name}/src/{bot_name}_cli.py shape ${{1:}}',
            encoding='utf-8'
        )
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_cursor_commands()
        output = f.getvalue()
        
        # Then: Verify instruction is at the top
        assert '**PLEASE SHOW THIS OUTPUT TO THE USER**' in output
        # Check it appears early in the output (first few lines)
        lines = output.split('\n')
        instruction_found = False
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if '**PLEASE SHOW THIS OUTPUT TO THE USER**' in line:
                instruction_found = True
                break
        assert instruction_found, "Instruction should appear near the top of output"
    
    def test_get_help_for_behaviors_and_actions(self, workspace_root):
        """
        SCENARIO: Get help for behaviors and actions (happy_path)
        GIVEN: bot configuration exists for bot 'story_bot' with behaviors='shape'
        AND: behavior instructions exist at 'agile_bot/bots/story_bot/behaviors/1_shape/instructions.json' with description='Create a story map and domain model outline'
        AND: behavior instructions contain goal='Shape both story map and domain model together'
        AND: behavior instructions contain outputs='story-graph.json, story-map.md'
        AND: base action instructions exist at 'agile_bot/bots/base_bot/base_actions/2_gather_context/instructions.json' for action 'gather_context'
        WHEN: Human executes CLI command 'story_bot --help'
        THEN: CLI loads all behaviors from bot configuration
        AND: CLI loads behavior instructions from 'agile_bot/bots/story_bot/behaviors/1_shape/instructions.json'
        AND: CLI extracts description from behavior instructions
        AND: CLI loads action instructions from 'agile_bot/bots/base_bot/base_actions/2_gather_context/instructions.json'
        AND: CLI extracts action description from base_actions
        AND: CLI displays output starting with '**PLEASE SHOW THIS OUTPUT TO THE USER**'
        AND: CLI displays behavior 'shape' with description containing 'Create a story map'
        AND: CLI displays action 'gather_context' with description from base_actions
        AND: CLI displays usage instructions at bottom
        AND: AI agent shows the help output to user
        """
        # Given: Set up bot with behaviors and behavior instructions
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create behavior instructions
        behavior_instructions_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / '1_shape'
        behavior_instructions_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = behavior_instructions_dir / 'instructions.json'
        instructions_data = {
            'behaviorName': 'shape',
            'description': 'Create a story map and domain model outline',
            'goal': 'Shape both story map and domain model together',
            'outputs': 'story-graph.json, story-map.md'
        }
        instructions_file.write_text(json.dumps(instructions_data), encoding='utf-8')
        
        # Create base action instructions
        base_actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / '2_gather_context'
        base_actions_dir.mkdir(parents=True, exist_ok=True)
        base_action_file = base_actions_dir / 'instructions.json'
        base_action_data = {
            'actionName': 'gather_context',
            'instructions': ['Gather context for the behavior workflow']
        }
        base_action_file.write_text(json.dumps(base_action_data), encoding='utf-8')
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_behaviors_and_actions()
        output = f.getvalue()
        
        # Then: Verify output
        assert '**PLEASE SHOW THIS OUTPUT TO THE USER**' in output
        assert 'Behavior: shape' in output
        assert 'Create a story map' in output
        assert 'Shape both story map' in output
        assert 'story-graph.json' in output
        assert 'gather_context' in output
        assert 'Usage:' in output
    
    def test_get_help_when_behavior_instructions_missing_for_help(self, workspace_root):
        """
        SCENARIO: Get help when behavior instructions missing for --help (edge_case)
        GIVEN: bot configuration exists for bot 'story_bot' with behavior 'unknown_behavior'
        AND: behavior instructions do NOT exist at 'agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json'
        WHEN: Human executes CLI command 'story_bot --help'
        THEN: CLI loads behaviors from bot configuration
        AND: CLI attempts to load behavior instructions from 'agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json'
        AND: CLI detects behavior instructions do not exist
        AND: CLI uses fallback description: 'Unknown Behavior'
        AND: CLI displays behavior 'unknown_behavior' with fallback description
        AND: CLI still displays all behaviors and actions
        """
        # Given: Set up bot with behavior but no instructions
        bot_name = 'story_bot'
        behaviors = ['unknown_behavior']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Do NOT create behavior instructions (they should be missing)
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        with redirect_stdout(f):
            cli.help_behaviors_and_actions()
        output = f.getvalue()
        
        # Then: Verify fallback description is used
        assert 'Behavior: unknown_behavior' in output
        # Should use fallback (either "Unknown Behavior" or formatted name)
        assert 'Unknown' in output or 'unknown_behavior' in output.lower()
    
    def test_help_extracts_action_descriptions_from_base_actions(self, workspace_root):
        """
        SCENARIO: Help extracts action descriptions from base_actions
        GIVEN: base action instructions exist at 'agile_bot/bots/base_bot/base_actions/2_gather_context/instructions.json'
        AND: base action instructions contain meaningful description
        WHEN: Help command loads action descriptions
        THEN: Action descriptions are extracted from base_actions instructions
        AND: Descriptions are meaningful (not just action name)
        """
        # Given: Set up bot with base action instructions
        bot_name = 'story_bot'
        behaviors = ['shape']
        bot_config, project_dir = setup_bot_for_testing(workspace_root, bot_name, behaviors)
        
        # Create base action instructions with meaningful description
        base_actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / '2_gather_context'
        base_actions_dir.mkdir(parents=True, exist_ok=True)
        base_action_file = base_actions_dir / 'instructions.json'
        base_action_data = {
            'actionName': 'gather_context',
            'instructions': ['Gather context for the behavior workflow', 'Review all provided context']
        }
        base_action_file.write_text(json.dumps(base_action_data), encoding='utf-8')
        
        # When: Execute help command
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        cli = BaseBotCli(
            bot_name=bot_name,
            bot_config_path=bot_config,
            workspace_root=workspace_root
        )
        
        # Test the action description extraction method directly
        action_description = cli._get_action_description('gather_context')
        
        # Then: Verify description is meaningful
        assert 'gather_context' not in action_description.lower() or len(action_description) > len('gather_context')
        # Description should contain meaningful text from instructions
        assert len(action_description) > 10, "Description should be meaningful, not just action name"

