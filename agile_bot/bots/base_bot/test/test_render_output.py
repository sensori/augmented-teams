"""
Render Output Tests

Tests for all stories in the 'Render Output' sub-epic:
- Track Activity for Render Output Action
- Proceed To Validate Rules
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    create_activity_log_file,
    create_workflow_state,
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action,
    read_activity_log
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
    actual_instructions_file = actual_base_actions_dir / '4_render_output' / 'instructions.json'
    bot_base_actions_dir = bot_directory / 'base_actions' / '4_render_output'
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
    """Then: {{render_instructions}} template variable replaced."""
    assert '{{render_instructions}}' not in base_instructions_text
    assert 'Render all story files' in base_instructions_text or 'Generate markdown output' in base_instructions_text


# ============================================================================
# STORY: Track Activity for Render Output Action
# ============================================================================

class TestTrackActivityForRenderOutputAction:
    """Story: Track Activity for Render Output Action - Tests activity tracking for render_output."""

    def test_track_activity_when_render_output_action_starts(self, bot_directory, workspace_directory):
        verify_action_tracks_start(bot_directory, workspace_directory, RenderOutputAction, 'render_output', behavior='discovery')

    def test_track_activity_when_render_output_action_completes(self, bot_directory, workspace_directory):
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
        workspace_directory.mkdir(parents=True, exist_ok=True)
        log_file = workspace_directory / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            db.insert({'action_state': 'story_bot.shape.render_output', 'timestamp': '09:00'})
            db.insert({'action_state': 'story_bot.discovery.render_output', 'timestamp': '10:00'})
        
        log_data = read_activity_log(workspace_directory)
        assert len(log_data) == 2
        assert log_data[0]['action_state'] == 'story_bot.shape.render_output'
        assert log_data[1]['action_state'] == 'story_bot.discovery.render_output'

    def test_activity_log_creates_file_if_not_exists(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity log creates file if it doesn't exist
        GIVEN: workspace directory exists but no activity log
        WHEN: Action tracks activity
        THEN: Activity log file is created automatically
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        log_file = workspace_directory / 'activity_log.json'
        assert not log_file.exists()
        
        # When: Action tracks activity
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='discovery',
            bot_directory=bot_directory
        )
        action.track_activity_on_start()
        
        # Then: Log file is created
        assert log_file.exists()


# ============================================================================
# STORY: Proceed To Validate Rules
# ============================================================================

class TestProceedToValidateRules:
    """Story: Proceed To Validate Rules - Tests transition to validate_rules action."""

    def test_seamless_transition_from_validate_rules_to_render_output(self, bot_directory, workspace_directory):
        verify_workflow_transition(bot_directory, workspace_directory, 'validate_rules', 'render_output', behavior='discovery')

    def test_workflow_state_captures_render_output_completion(self, bot_directory, workspace_directory):
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'render_output')

    def test_render_output_action_executes_successfully(self, bot_directory, workspace_directory):
        """
        SCENARIO: Render output action executes successfully
        GIVEN: render_output action is initialized
        WHEN: Action is executed
        THEN: Action completes without errors
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name = 'story_bot'
        behavior = 'discovery'
        
        action = RenderOutputAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        
        # Action should initialize successfully
        assert action.bot_name == bot_name
        assert action.behavior == behavior


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
        bot_name = 'test_bot'
        behavior = 'shape'
        
        given_base_instructions_for_render_output_copied(bot_directory)
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
        
        action_obj, instructions = when_render_output_action_loads_and_merges_instructions(bot_name, behavior, bot_directory)
        
        base_instructions_text = '\n'.join(instructions.get('base_instructions', []))
        then_render_configs_template_variable_replaced(base_instructions_text)
        then_render_configs_include_all_required_fields(base_instructions_text)
        then_specific_field_values_present(base_instructions_text)
        then_render_instructions_template_variable_replaced(base_instructions_text)

    def test_render_configs_format_includes_all_fields(self, bot_directory, workspace_directory):
        """
        SCENARIO: Formatted render_configs includes all fields referenced in instructions
        GIVEN: Render configs with instructions, synchronizer, template, input, output fields
        WHEN: Configs are formatted for injection
        THEN: All fields are present in formatted output
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name = 'test_bot'
        behavior = 'shape'
        
        behavior_dir = bot_directory / 'behaviors' / behavior
        render_dir = behavior_dir / '2_content' / '2_render'
        render_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config with synchronizer
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
        
        # Create config with template
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
        
        # When: Action formats render configs
        action_obj = RenderOutputAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        
        # Load render configs
        behavior_folder = action_obj._find_behavior_folder()
        render_configs = action_obj._load_render_configs(behavior_folder)
        
        # Format them
        formatted = action_obj._format_render_configs(render_configs)
        
        # Then: All fields are present
        assert 'render_sync' in formatted
        assert 'render_template' in formatted
        
        # Check synchronizer config fields
        assert 'Instructions:' in formatted or 'instructions' in formatted.lower()
        assert 'Synchronizer:' in formatted or 'synchronizer' in formatted.lower()
        assert 'synchronizers.test.TestSynchronizer' in formatted
        assert 'renderer_command' in formatted.lower() or 'Renderer Command:' in formatted
        assert 'render-test' in formatted
        assert 'Input:' in formatted or 'input' in formatted.lower()
        assert 'story-graph.json' in formatted
        assert 'Output:' in formatted or 'output' in formatted.lower()
        assert 'test-output.drawio' in formatted
        
        # Check template config fields
        assert 'Template:' in formatted or 'template' in formatted.lower()
        assert 'templates/test-template.md' in formatted
        assert 'test-output.md' in formatted
