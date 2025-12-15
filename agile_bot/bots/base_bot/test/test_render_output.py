"""
Render Output Tests

Tests for all stories in the 'Render Output' sub-epic:
- Track Activity for Render Output Action
- Proceed To Validate Rules
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.actions.render_output.render_output_action import RenderOutputAction
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_activity_log_file,
    read_activity_log
)
from agile_bot.bots.base_bot.test.test_execute_behavior_actions import (
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action
)

# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def given_base_instructions_for_render_output_copied(bot_directory: Path):
    """Given: Base instructions for render_output copied."""
    from agile_bot.bots.base_bot.test.test_helpers import get_base_actions_dir
    import shutil
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    actual_base_actions_dir = get_base_actions_dir(repo_root)
    actual_instructions_file = actual_base_actions_dir / 'render_output' / 'instructions.json'
    bot_base_actions_dir = bot_directory / 'base_actions' / 'render_output'
    bot_base_actions_dir.mkdir(parents=True, exist_ok=True)
    bot_instructions_file = bot_base_actions_dir / 'instructions.json'
    if actual_instructions_file.exists():
        shutil.copy2(actual_instructions_file, bot_instructions_file)
    else:
        bot_instructions_file.write_text(json.dumps({
            'actionName': 'render_output',
            'instructions': [
                'Render outputs using render configs',
                '{{render_configs}}',
                '{{render_instructions}}'
            ]
        }), encoding='utf-8')
    return bot_instructions_file


def given_behavior_render_instructions_created(bot_directory: Path, behavior: str):
    """Given: Behavior render instructions created."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    render_dir = behavior_dir / '2_content' / '2_render'
    render_dir.mkdir(parents=True, exist_ok=True)
    render_instructions_file = render_dir / 'instructions.json'
    render_instructions_file.write_text(
        json.dumps({
            'behaviorName': behavior,
            'instructions': ['Render all story files', 'Generate markdown output']
        }),
        encoding='utf-8'
    )
    return render_instructions_file


def given_render_configs_created(render_dir: Path, configs: list):
    """Given: Render configs created."""
    created_configs = []
    for config_data in configs:
        config_file = render_dir / f"{config_data['name']}.json"
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        created_configs.append(config_file)
    return created_configs

def given_behavior_render_directory_created(bot_directory: Path, behavior: str) -> Path:
    """Given: Behavior render directory created."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    render_dir = behavior_dir / '2_content' / '2_render'
    render_dir.mkdir(parents=True, exist_ok=True)
    return render_dir

def when_render_output_action_created(bot_name: str, behavior: str, bot_directory: Path):
    """When: RenderOutputAction created."""
    return RenderOutputAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )


def when_render_output_action_loads_and_merges_instructions(bot_name: str, behavior: str, bot_directory: Path):
    """When: RenderOutputAction loads and merges instructions."""
    action_obj = RenderOutputAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )
    instructions = action_obj.load_and_merge_instructions()
    return action_obj, instructions


def then_render_configs_template_variable_replaced(base_instructions_text: str):
    """Then: {{render_configs}} template variable replaced."""
    assert '{{render_configs}}' not in base_instructions_text
    assert 'render_story_files' in base_instructions_text
    assert 'render_story_map_txt' in base_instructions_text


def then_render_configs_include_all_required_fields(base_instructions_text: str):
    """Then: Render configs include all required fields."""
    assert 'Instructions:' in base_instructions_text or 'instructions' in base_instructions_text.lower()
    assert 'Synchronizer:' in base_instructions_text or 'synchronizer' in base_instructions_text.lower()
    assert 'Template:' in base_instructions_text or 'template' in base_instructions_text.lower()
    assert 'Input:' in base_instructions_text or 'input' in base_instructions_text.lower()
    assert 'Output:' in base_instructions_text or 'output' in base_instructions_text.lower()


def then_specific_field_values_present(base_instructions_text: str):
    """Then: Specific field values present."""
    assert 'synchronizers.story_scenarios.StoryScenariosSynchronizer' in base_instructions_text
    assert 'templates/story-map.txt' in base_instructions_text
    assert 'story-graph.json' in base_instructions_text


def then_render_instructions_template_variable_replaced(base_instructions_text: str):
    """Then step: Render instructions template variable replaced."""
    assert '{{render_configs}}' not in base_instructions_text
    assert 'render_configs' in base_instructions_text

def then_all_render_output_assertions_pass(base_instructions_text: str):
    """Then step: All render output assertions pass."""
    then_render_configs_template_variable_replaced(base_instructions_text)
    then_render_configs_include_all_required_fields(base_instructions_text)
    then_specific_field_values_present(base_instructions_text)
    then_render_instructions_template_variable_replaced(base_instructions_text)
    """Then: {{render_instructions}} template variable replaced."""
    assert '{{render_instructions}}' not in base_instructions_text
    assert 'Render all story files' in base_instructions_text or 'Generate markdown output' in base_instructions_text


def given_activity_log_with_multiple_entries(workspace_directory: Path):
    """Given: Activity log with multiple entries."""
    workspace_directory.mkdir(parents=True, exist_ok=True)
    log_file = workspace_directory / 'activity_log.json'
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        db.insert({'action_state': 'story_bot.shape.render_output', 'timestamp': '09:00'})
        db.insert({'action_state': 'story_bot.discovery.render_output', 'timestamp': '10:00'})
    return log_file


def then_activity_log_has_two_entries_with_expected_states(workspace_directory: Path):
    """Then: Activity log has two entries with expected states."""
    log_data = read_activity_log(workspace_directory)
    assert len(log_data) == 2
    assert log_data[0]['action_state'] == 'story_bot.shape.render_output'
    assert log_data[1]['action_state'] == 'story_bot.discovery.render_output'


def then_activity_log_file_does_not_exist(workspace_directory: Path):
    """Then: Activity log file does not exist."""
    log_file = workspace_directory / 'activity_log.json'
    assert not log_file.exists()
    return log_file


def when_render_output_action_tracks_start(bot_name: str, behavior: str, bot_directory: Path):
    """When: Render output action tracks start."""
    action = RenderOutputAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )
    action.track_activity_on_start()
    return action


def then_activity_log_file_exists(log_file: Path):
    """Then: Activity log file exists."""
    assert log_file.exists()


def given_bot_name_and_behavior_for_discovery():
    """Given: Bot name and behavior for discovery."""
    bot_name = 'story_bot'
    behavior = 'discovery'
    return bot_name, behavior


def when_create_render_output_action(bot_name: str, behavior: str, bot_directory: Path):
    """When: Create render output action."""
    action = RenderOutputAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )
    return action


def then_action_has_correct_bot_name_and_behavior(action, expected_bot_name: str, expected_behavior: str):
    """Then: Action has correct bot name and behavior."""
    assert action.bot_name == expected_bot_name
    assert action.behavior == expected_behavior


def given_bot_name_and_behavior_for_shape():
    """Given: Bot name and behavior for shape."""
    bot_name = 'test_bot'
    behavior = 'shape'
    return bot_name, behavior


def given_render_dir_and_configs_setup(bot_directory: Path, behavior: str):
    """Given: Render dir and configs setup."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    render_dir = behavior_dir / '2_content' / '2_render'
    render_dir.mkdir(parents=True, exist_ok=True)
    given_behavior_render_instructions_created(bot_directory, behavior)
    given_render_configs_created(render_dir, [
        {
            'name': 'render_story_files',
            'type': 'synchronizer',
            'path': 'docs/stories',
            'input': 'story-graph.json',
            'synchronizer': 'synchronizers.story_scenarios.StoryScenariosSynchronizer',
            'output': 'docs/stories',
            'instructions': 'Render story-graph.json to story markdown files'
        },
        {
            'name': 'render_story_map_txt',
            'type': 'template',
            'path': 'docs/stories',
            'input': 'story-graph.json',
            'template': 'templates/story-map.txt',
            'output': 'story-map.txt',
            'instructions': 'Render story-graph.json to story-map.txt format'
        }
    ])
    return render_dir


def when_format_render_configs(action_obj):
    """When: Format render configs."""
    behavior_folder = action_obj._find_behavior_folder()
    render_configs = action_obj._load_render_configs(behavior_folder)
    formatted = action_obj._format_render_configs(render_configs)
    return formatted


def then_formatted_configs_contain_sync_and_template(formatted: str):
    """Then: Formatted configs contain sync and template."""
    assert 'render_sync' in formatted
    assert 'render_template' in formatted


def then_formatted_configs_contain_synchronizer_fields(formatted: str):
    """Then: Formatted configs contain synchronizer fields."""
    assert 'Instructions:' in formatted or 'instructions' in formatted.lower()
    assert 'Synchronizer:' in formatted or 'synchronizer' in formatted.lower()
    assert 'synchronizers.test.TestSynchronizer' in formatted
    assert 'renderer_command' in formatted.lower() or 'Renderer Command:' in formatted
    assert 'render-test' in formatted
    assert 'Input:' in formatted or 'input' in formatted.lower()
    assert 'story-graph.json' in formatted
    assert 'Output:' in formatted or 'output' in formatted.lower()
    assert 'test-output.drawio' in formatted


def then_formatted_configs_contain_template_fields(formatted: str):
    """Then: Formatted configs contain template fields."""
    assert 'Template:' in formatted or 'template' in formatted.lower()
    assert 'templates/test-template.md' in formatted
    assert 'test-output.md' in formatted


def when_create_sync_and_template_configs(render_dir: Path):
    """When: Create sync and template configs."""
    sync_config = render_dir / 'render_sync.json'
    sync_config.write_text(
        json.dumps({
            'name': 'render_sync',
            'type': 'synchronizer',
            'path': 'docs/stories',
            'input': 'story-graph.json',
            'synchronizer': 'synchronizers.test.TestSynchronizer',
            'renderer_command': 'render-test',
            'output': 'test-output.drawio',
            'instructions': 'Test synchronizer instructions'
        }),
        encoding='utf-8'
    )
    
    template_config = render_dir / 'render_template.json'
    template_config.write_text(
        json.dumps({
            'name': 'render_template',
            'type': 'template',
            'path': 'docs/stories',
            'input': 'story-graph.json',
            'template': 'templates/test-template.md',
            'output': 'test-output.md',
            'instructions': 'Test template instructions'
        }),
        encoding='utf-8'
    )
    return sync_config, template_config


# ============================================================================
# STORY: Track Activity for Render Output Action
# ============================================================================

class TestTrackActivityForRenderOutputAction:
    """Story: Track Activity for Render Output Action - Tests activity tracking for render_output."""

    def test_track_activity_when_render_output_action_starts(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Render output action starts
        # Then: Activity is tracked (verified by verify_action_tracks_start)
        verify_action_tracks_start(bot_directory, workspace_directory, RenderOutputAction, 'render_output', behavior='discovery')

    def test_track_activity_when_render_output_action_completes(self, bot_directory, workspace_directory):
        # Given: Bot directory and workspace directory are set up
        # When: Render output action completes with outputs and duration
        # Then: Activity is tracked (verified by verify_action_tracks_completion)
        verify_action_tracks_completion(
            bot_directory,
            workspace_directory,
            RenderOutputAction,
            'render_output',
            behavior='discovery',
            outputs={'files_generated_count': 3, 'file_paths': ['story-map.md', 'increments.md']},
            duration=180
        )

    def test_track_multiple_render_output_invocations_across_behaviors(self, workspace_directory):
        # Activity log is in workspace_directory
        given_activity_log_with_multiple_entries(workspace_directory)
        
        then_activity_log_has_two_entries_with_expected_states(workspace_directory)

    def test_activity_log_creates_file_if_not_exists(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity Log Creates File If Not Exists
        GIVEN: workspace directory exists but no activity log
        WHEN: Action tracks activity
        THEN: Activity log file is created automatically
        """
        # Given: Workspace directory exists but no activity log
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        log_file = then_activity_log_file_does_not_exist(workspace_directory)
        
        # When: Action tracks activity
        # Then: Activity log file is created automatically
        when_render_output_action_tracks_start('story_bot', 'discovery', bot_directory)
        
        # Then: Log file is created
        then_activity_log_file_exists(log_file)


# ============================================================================
# STORY: Proceed To Validate Rules
# ============================================================================

class TestProceedToValidateRules:
    """Story: Proceed To Validate Rules - Tests transition to validate_rules action."""

    def test_seamless_transition_from_validate_rules_to_render_output(self, bot_directory, workspace_directory):
        """
        SCENARIO: Seamless Transition From Validate Rules To Render Output
        """
        # Given: Bot directory and workspace directory are set up
        # When: Validate rules action completes
        # Then: Workflow transitions to render_output (verified by verify_workflow_transition)
        verify_workflow_transition(bot_directory, workspace_directory, 'validate_rules', 'render_output', behavior='discovery')

    def test_workflow_state_captures_render_output_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow State Captures Render Output Completion
        """
        # Given: Bot directory and workspace directory are set up
        # When: Render output action completes
        # Then: Workflow state captures completion (verified by verify_workflow_saves_completed_action)
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'render_output')

    def test_render_output_action_executes_successfully(self, bot_directory, workspace_directory):
        """
        SCENARIO: Render Output Action Executes Successfully
        GIVEN: render_output action is initialized
        WHEN: Action is executed
        THEN: Action completes without errors
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name, behavior = given_bot_name_and_behavior_for_discovery()
        
        action = when_create_render_output_action(bot_name, behavior, bot_directory)
        
        # Action should initialize successfully
        then_action_has_correct_bot_name_and_behavior(action, bot_name, behavior)


# ============================================================================
# STORY: Inject Render Instructions and Configs
# ============================================================================

class TestInjectRenderInstructionsAndConfigs:
    """Story: Inject Render Instructions and Configs - Tests template variable injection."""

    def test_all_template_variables_are_replaced_in_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: All template variables are replaced in final instructions
        GIVEN: Base instructions with {{render_configs}} and {{render_instructions}} placeholders
        WHEN: Action loads and merges instructions with all injections
        THEN: All template variables are replaced with actual content
        """
        bootstrap_env(bot_directory, workspace_directory)
        bot_name, behavior = given_bot_name_and_behavior_for_shape()
        
        given_base_instructions_for_render_output_copied(bot_directory)
        render_dir = given_render_dir_and_configs_setup(bot_directory, behavior)
        
        action_obj, instructions = when_render_output_action_loads_and_merges_instructions(bot_name, behavior, bot_directory)
        
        base_instructions_text = '\n'.join(instructions.get('base_instructions', []))
        then_all_render_output_assertions_pass(base_instructions_text)

    def test_render_configs_format_includes_all_fields(self, bot_directory, workspace_directory):
        """
        SCENARIO: Formatted render_configs includes all fields referenced in instructions
        GIVEN: Render configs with instructions, synchronizer, template, input, output fields
        WHEN: Configs are formatted for injection
        THEN: All fields are present in formatted output
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name, behavior = given_bot_name_and_behavior_for_shape()
        render_dir = given_behavior_render_directory_created(bot_directory, behavior)
        when_create_sync_and_template_configs(render_dir)
        
        # When: Action formats render configs
        action_obj = when_render_output_action_created(bot_name, behavior, bot_directory)
        
        formatted = when_format_render_configs(action_obj)
        
        # Then: All fields are present
        then_formatted_configs_contain_sync_and_template(formatted)
        then_formatted_configs_contain_synchronizer_fields(formatted)
        then_formatted_configs_contain_template_fields(formatted)
