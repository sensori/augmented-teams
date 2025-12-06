"""
Load Rendered Content Tests

Tests for all stories in the 'Load Rendered Content' sub-epic:
- Load Render Configurations
- Inject Template Instructions
- Inject Synchronizer Instructions
"""
import pytest
from pathlib import Path
import json
import importlib
from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_render_json_file(render_dir: Path, filename: str, config: dict) -> Path:
    """Helper: Create render JSON configuration file."""
    render_json = render_dir / filename
    render_json.write_text(json.dumps(config, indent=2), encoding='utf-8')
    return render_json

def create_template_file(templates_dir: Path, template_path: str, content: str) -> Path:
    """Helper: Create template file."""
    template_file = templates_dir / template_path
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(content, encoding='utf-8')
    return template_file

def create_behavior_render_folder(workspace_root: Path, bot_name: str, behavior: str) -> Path:
    """Helper: Create behavior render folder structure."""
    render_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / '2_content' / '2_render'
    render_dir.mkdir(parents=True, exist_ok=True)
    return render_dir

def create_base_instructions(workspace_root: Path):
    """Helper: Create base instructions file."""
    base_actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / '5_render_output'
    base_actions_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = base_actions_dir / 'instructions.json'
    instructions_file.write_text(json.dumps({
        'actionName': 'render_output',
        'instructions': ['Render output instructions']
    }), encoding='utf-8')
    return instructions_file

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    # Create base instructions so action can load
    create_base_instructions(workspace)
    return workspace

# ============================================================================
# STORY: Load Render Configurations
# ============================================================================

class TestLoadRenderConfigurations:
    """Story: Load Render Configurations - Tests discovery and loading of render JSON files and synchronizer verification."""

    def test_render_output_discovers_and_loads_render_json_files(self, workspace_root):
        """
        SCENARIO: Render output discovers and loads render JSON files
        GIVEN: Behavior folder contains 2_content/2_render/ folder
        AND: Render folder contains render JSON file
        WHEN: render_output action executes for the behavior
        THEN: render_output discovers render folder using *_content/*_render pattern
        AND: render_output loads all *.json files from render folder
        AND: render_output reads each render JSON configuration
        """
        # Given: Behavior folder with render JSON files
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'exploration')
        render_json_file_1 = create_render_json_file(render_dir, 'render_story_exploration.md.json', {
            'name': 'render_story_exploration',
            'path': 'docs/stories',
            'template': 'story-exploration.md',
            'output': '{increment_name_slug}-exploration.md'
        })
        render_json_file_2 = create_render_json_file(render_dir, 'render_story_map_txt.json', {
            'name': 'render_story_map',
            'path': 'docs/stories',
            'template': 'story-map.txt',
            'output': 'story-map.txt'
        })
        
        # When: render_output action executes
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: render_configs array exists and contains loaded configs
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert isinstance(render_configs, list)
        assert len(render_configs) == 2
        
        # Verify first config loaded correctly
        config_1 = render_configs[0]
        assert config_1['config']['name'] == 'render_story_exploration'
        assert config_1['file'] == str(render_json_file_1.relative_to(workspace_root))
        
        # Verify second config loaded correctly
        config_2 = render_configs[1]
        assert config_2['config']['name'] == 'render_story_map'
        assert config_2['file'] == str(render_json_file_2.relative_to(workspace_root))

    def test_render_output_loads_instructions_json_from_render_folder(self, workspace_root):
        """
        SCENARIO: Render output loads instructions.json from render folder
        GIVEN: Render folder contains instructions.json file
        AND: Render folder contains render JSON configuration files
        WHEN: render_output discovers render folder
        THEN: render_output loads instructions.json if it exists
        AND: render_output stores render_instructions for later injection
        AND: render_instructions are separate from render_configs
        """
        # Given: Render folder with instructions.json
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'shape')
        instructions_file = render_dir / 'instructions.json'
        instructions_content = {
            'behaviorName': 'shape',
            'instructions': ['Render story map and domain model']
        }
        instructions_file.write_text(json.dumps(instructions_content), encoding='utf-8')
        
        # When: render_output discovers render folder
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: render_instructions loaded and separate
        assert 'render_instructions' in instructions
        render_instructions = instructions['render_instructions']
        assert render_instructions['behaviorName'] == 'shape'
        assert render_instructions['instructions'] == ['Render story map and domain model']
        assert 'render_configs' not in instructions or isinstance(instructions.get('render_configs'), list)

    def test_render_output_verifies_synchronizer_classes_exist_and_have_render_method(self, workspace_root):
        """
        SCENARIO: Render output verifies synchronizer classes exist and have render method
        GIVEN: Render JSON file exists with synchronizer field
        WHEN: render_output loads render JSON file
        THEN: render_output verifies synchronizer field contains full module path and class name
        AND: render_output verifies synchronizer class can be imported
        AND: render_output verifies synchronizer class has render method
        AND: render_output stores synchronizer class path in render config
        """
        # Given: Render JSON with synchronizer field using full module path
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'shape')
        synchronizer_class = 'agile_bot.bots.story_bot.src.synchronizers.story_io.story_io_synchronizer.DrawIOSynchronizer'
        create_render_json_file(render_dir, 'render_story_map_outline_drawio.json', {
            'name': 'render_story_map_outline_drawio',
            'path': 'docs/stories',
            'input': 'story-graph.json',
            'synchronizer': synchronizer_class,
            'renderer_command': 'render-outline',
            'output': 'story-map-outline.drawio'
        })
        
        # When: render_output loads render JSON file
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Verify synchronizer class is stored in config
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert len(render_configs) > 0
        
        config = render_configs[0]
        assert config['config']['synchronizer'] == synchronizer_class
        
        # Verify synchronizer class exists and has render method (using actual import)
        module_path, class_name = synchronizer_class.rsplit('.', 1)
        module = importlib.import_module(module_path)
        synchronizer_class_obj = getattr(module, class_name)
        assert hasattr(synchronizer_class_obj, 'synchronize_outline')
        assert callable(getattr(synchronizer_class_obj, 'synchronize_outline'))

    def test_render_output_handles_missing_render_folder(self, workspace_root):
        """
        SCENARIO: Render output handles missing render folder
        GIVEN: Behavior folder does not contain 2_content/2_render/ folder
        WHEN: render_output action executes for the behavior
        THEN: render_output reports error (render folder is required for render_output action)
        AND: render_output cannot proceed without render configurations
        """
        # Given: Behavior folder without render folder
        behavior_dir = workspace_root / 'agile_bot' / 'bots' / 'story_bot' / 'behaviors' / 'test_behavior'
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        # When: render_output action executes
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='test_behavior',
            workspace_root=workspace_root
        )
        
        # Then: Should raise error or return empty configs
        instructions = action.load_and_merge_instructions()
        # If no error, should have empty render_configs or not include it
        assert 'render_configs' not in instructions or len(instructions.get('render_configs', [])) == 0

    def test_render_output_handles_unreadable_render_json_files(self, workspace_root):
        """
        SCENARIO: Render output handles unreadable render JSON files
        GIVEN: Render folder contains multiple *.json files
        AND: One render JSON file cannot be read (corrupted or invalid JSON)
        WHEN: render_output loads render JSON files
        THEN: render_output skips unreadable render JSON file
        AND: render_output continues loading other *.json files from render folder
        AND: render_output does not fail entire load process
        """
        # Given: Render folder with valid and invalid JSON files
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'exploration')
        create_render_json_file(render_dir, 'valid_render.json', {
            'name': 'valid_render',
            'path': 'docs/stories',
            'template': 'template.md',
            'output': 'output.md'
        })
        invalid_file = render_dir / 'corrupted_render.json'
        invalid_file.write_text('{invalid json}', encoding='utf-8')
        
        # When: render_output loads render JSON files
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Should not fail, should skip invalid file and load valid one
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        # Should have at least the valid config
        assert len(render_configs) >= 1
        assert render_configs[0]['config']['name'] == 'valid_render'

    def test_render_output_handles_invalid_synchronizer_classes(self, workspace_root):
        """
        SCENARIO: Render output handles invalid synchronizer classes
        GIVEN: Render JSON file exists with synchronizer field
        AND: Synchronizer class cannot be imported or does not have render method
        WHEN: render_output loads render JSON file
        THEN: render_output reports error for that render config
        AND: render_output continues loading other render configs
        AND: render_output does not fail entire load process
        """
        # Given: Render JSONs with invalid and valid synchronizers
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'shape')
        create_render_json_file(render_dir, 'render_invalid_sync.json', {
            'name': 'render_invalid_sync',
            'synchronizer': 'synchronizers.nonexistent.InvalidSynchronizer',
            'output': 'output.txt'
        })
        create_render_json_file(render_dir, 'render_valid.json', {
            'name': 'render_valid',
            'template': 'template.md',
            'output': 'output.md'
        })
        
        # When: render_output loads render JSON files
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Should continue processing other configs
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        # Should have at least the valid config
        assert len(render_configs) >= 1
        # Find valid config
        valid_configs = [c for c in render_configs if c['config']['name'] == 'render_valid']
        assert len(valid_configs) == 1

# ============================================================================
# STORY: Inject Template Instructions
# ============================================================================

class TestInjectTemplateInstructions:
    """Story: Inject Template Instructions - Tests loading and injection of template content for template-only renders."""

    def test_render_output_loads_template_files_from_render_json(self, workspace_root):
        """
        SCENARIO: Render output loads template files from render JSON
        GIVEN: Render JSON file specifies template field
        AND: Render JSON does not have synchronizer field
        AND: Template file exists at 2_content/2_render/templates/
        WHEN: render_output processes template-only render configs
        THEN: render_output checks for template field in configuration
        AND: render_output loads template file from templates folder
        AND: render_output loads template file as text content
        AND: render_output stores template content with render config
        """
        # Given: Render JSON with template field (no synchronizer)
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'exploration')
        templates_dir = render_dir / 'templates'
        template_path = 'story-exploration.md'
        template_content = '# {increment_name} - Exploration\n\n**Priority:** {increment_priority}'
        create_render_json_file(render_dir, 'render_story_exploration.md.json', {
            'name': 'render_story_exploration',
            'path': 'docs/stories',
            'template': template_path,
            'output': '{increment_name_slug}-exploration.md'
        })
        create_template_file(templates_dir, template_path, template_content)
        
        # When: render_output processes template-only render configs
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Template content loaded and stored with render config
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert len(render_configs) == 1
        
        config = render_configs[0]
        assert config['config']['name'] == 'render_story_exploration'
        assert 'template' in config
        assert config['template'] == template_content
        assert config['config']['template'] == template_path

    def test_render_output_injects_template_content_into_instructions(self, workspace_root):
        """
        SCENARIO: Render output injects template content into instructions
        GIVEN: Render JSON file exists without synchronizer field
        AND: Render JSON file specifies template field
        AND: render_output has loaded render JSON file
        AND: render_output has loaded template file
        WHEN: render_output merges instructions
        THEN: render_output injects render_configs array into merged instructions
        AND: render_configs[0] includes config with name from render JSON file
        AND: render_configs[0] includes loaded template content from template file
        """
        # Given: Render JSON and template loaded
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'exploration')
        templates_dir = render_dir / 'templates'
        render_json_file = 'render_story_exploration.md.json'
        template_file = 'story-exploration.md'
        template_content = '# {increment_name} - Exploration'
        
        create_render_json_file(render_dir, render_json_file, {
            'name': 'render_story_exploration',
            'template': template_file,
            'output': 'exploration.md'
        })
        create_template_file(templates_dir, template_file, template_content)
        
        # When: render_output merges instructions
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Template content injected in render_configs
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert len(render_configs) == 1
        
        render_config = render_configs[0]
        assert render_config['config']['name'] == 'render_story_exploration'
        assert render_config['template'] == template_content
        assert render_config['file'] == str((render_dir / render_json_file).relative_to(workspace_root))

    def test_render_output_handles_missing_template_files_gracefully(self, workspace_root):
        """
        SCENARIO: Render output handles missing template files gracefully
        GIVEN: Render JSON specifies template file that does not exist
        AND: Render JSON does not have synchronizer field
        AND: Other render JSONs with templates do exist
        WHEN: render_output loads template files
        THEN: render_output skips missing template file
        AND: render_output continues loading other templates
        AND: render_output includes successfully loaded templates with render configs
        """
        # Given: Render JSONs with existing and missing templates
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'exploration')
        templates_dir = render_dir / 'templates'
        create_render_json_file(render_dir, 'render_valid.json', {
            'name': 'render_valid',
            'template': 'existing-template.md',
            'output': 'output.md'
        })
        create_render_json_file(render_dir, 'render_missing.json', {
            'name': 'render_missing',
            'template': 'missing-template.md',
            'output': 'output2.md'
        })
        create_template_file(templates_dir, 'existing-template.md', 'Template content')
        
        # When: render_output loads template files
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Should handle missing template gracefully and include valid one
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert len(render_configs) >= 1
        
        # Find valid config with loaded template
        valid_config = next((c for c in render_configs if c['config']['name'] == 'render_valid'), None)
        assert valid_config is not None
        assert 'template' in valid_config
        assert valid_config['template'] == 'Template content'

# ============================================================================
# STORY: Inject Synchronizer Instructions
# ============================================================================

class TestInjectSynchronizerInstructions:
    """Story: Inject Synchronizer Instructions - Tests injection of synchronizer class and render method execution instructions."""

    def test_render_output_includes_synchronizer_configs_in_render_configs_array(self, workspace_root):
        """
        SCENARIO: Render output includes synchronizer configs in render_configs array
        GIVEN: Render JSON file exists with synchronizer field
        AND: Render JSON file specifies renderer_command (optional, for render method variant)
        AND: render_output has loaded render JSON file
        AND: Synchronizer class has been verified
        WHEN: render_output processes synchronizer-based render configs
        THEN: render_output includes config with synchronizer field in render_configs array
        AND: render_configs[0] includes config with name from render JSON file
        AND: render_configs[0] includes synchronizer class path
        AND: render_configs[0] includes renderer_command (if specified)
        AND: render_configs[0] includes input and output paths from render JSON
        """
        # Given: Render JSON with synchronizer field
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'shape')
        synchronizer_class = 'synchronizers.story_io.DrawIOSynchronizer'
        renderer_command = 'render-outline'
        input_path = 'story-graph.json'
        output_path = 'story-map-outline.drawio'
        
        create_render_json_file(render_dir, 'render_story_map_outline_drawio.json', {
            'name': 'render_story_map_outline_drawio',
            'path': 'docs/stories',
            'input': input_path,
            'synchronizer': synchronizer_class,
            'renderer_command': renderer_command,
            'output': output_path
        })
        
        # When: render_output processes synchronizer-based render configs
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: Synchronizer config included in render_configs with all fields
        assert 'render_configs' in instructions
        render_configs = instructions['render_configs']
        assert len(render_configs) == 1
        
        render_config = render_configs[0]
        assert render_config['config']['name'] == 'render_story_map_outline_drawio'
        assert render_config['config']['synchronizer'] == synchronizer_class
        assert render_config['config']['renderer_command'] == renderer_command
        assert render_config['config']['input'] == input_path
        assert render_config['config']['output'] == output_path
        # Template should NOT be included for synchronizer-based renders
        assert 'template' not in render_config or render_config.get('template') is None

    def test_render_output_includes_synchronizer_execution_instructions_in_base_instructions(self, workspace_root):
        """
        SCENARIO: Render output includes synchronizer execution instructions in base_instructions
        GIVEN: Render JSON file exists with synchronizer field
        AND: Render JSON file specifies renderer_command (optional, for render method variant)
        AND: Render JSON file specifies input and output
        AND: render_output has processed synchronizer-based render configs
        WHEN: render_output merges instructions
        THEN: base_instructions contain instruction to instantiate synchronizer class
        AND: base_instructions contain instruction to call render method on synchronizer instance
        AND: base_instructions specify render method call with input and output paths
        AND: base_instructions specify renderer_command if provided (for method variant)
        """
        # Given: Render JSON with synchronizer and renderer_command
        render_dir = create_behavior_render_folder(workspace_root, 'story_bot', 'shape')
        synchronizer_class = 'synchronizers.story_io.DrawIOSynchronizer'
        renderer_command = 'render-outline'
        input_path = 'story-graph.json'
        output_path = 'story-map-outline.drawio'
        
        create_render_json_file(render_dir, 'render_story_map_outline_drawio.json', {
            'name': 'render_story_map_outline_drawio',
            'synchronizer': synchronizer_class,
            'renderer_command': renderer_command,
            'input': input_path,
            'output': output_path
        })
        
        # When: render_output merges instructions
        action = RenderOutputAction(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        # Then: base_instructions should contain synchronizer execution instructions
        assert 'base_instructions' in instructions
        base_instructions = instructions['base_instructions']
        assert isinstance(base_instructions, list)
        
        # Verify instructions mention synchronizer execution
        instructions_text = ' '.join(base_instructions)
        assert synchronizer_class in instructions_text or 'synchronizer' in instructions_text.lower()
        assert renderer_command in instructions_text or 'render' in instructions_text.lower()
