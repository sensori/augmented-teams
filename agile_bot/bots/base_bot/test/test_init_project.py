"""
Init Project Tests

Tests for all stories in the 'Init Project' sub-epic (in story map order):
- Initialize Project Location (Increment 3)
"""
import pytest
from pathlib import Path
import json
import tempfile
import shutil
from agile_bot.bots.base_bot.src.bot.bot import Bot


# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

def create_bot_config(workspace: Path, bot_name: str, behaviors: list) -> Path:
    """Helper: Create bot configuration file."""
    config_path = workspace / 'agile_bot/bots' / bot_name / 'config/bot_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_path


def create_saved_location(workspace: Path, bot_name: str, location: str):
    """Helper: Create saved current_project file."""
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    current_project_file = bot_dir / 'current_project.json'
    current_project_file.parent.mkdir(parents=True, exist_ok=True)
    current_project_file.write_text(json.dumps({'current_project': location}), encoding='utf-8')
    return current_project_file


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root():
    """Fixture: Temporary workspace directory."""
    test_dir = Path(tempfile.mkdtemp())
    workspace = test_dir / 'workspace'
    workspace.mkdir(exist_ok=True)
    
    yield workspace
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)


# ============================================================================
# STORY: Initialize Project Location (Increment 3)
# ============================================================================

class TestInitializeProjectLocation:
    """Story: Initialize Project Location - Confirms project location for workflow state persistence."""
    
    def test_first_time_initialization_detects_and_requests_confirmation(self, workspace_root):
        """
        SCENARIO: First time initialization with no saved location
        GIVEN: No project location has been saved
        WHEN: Bot behavior is invoked
        THEN: Bot detects current directory and requests confirmation
        """
        # Given: No saved location
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Bot detects current directory (cwd) and requests confirmation
        assert result.status == 'completed'
        assert 'proposed_location' in result.data
        assert result.data['requires_confirmation'] == True
        assert 'Confirm?' in result.data['message']
    
    def test_subsequent_invocation_same_location_skips_confirmation(self, workspace_root):
        """
        SCENARIO: Subsequent invocation with same location (no confirmation bias)
        GIVEN: Project location is saved and current directory matches saved location
        WHEN: Bot behavior is invoked
        THEN: Bot does NOT ask user for confirmation and says 'Resuming in...'
        """
        # Given: Saved location matches current directory
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        # Save current_project as cwd (which is what it will detect)
        import os
        current_dir = Path(os.getcwd())
        create_saved_location(workspace_root, 'test_bot', str(current_dir))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Bot skips confirmation and says resuming
        assert result.status == 'completed'
        assert result.data.get('requires_confirmation') == False
        assert 'Resuming in' in result.data['message']
    
    def test_location_changed_requests_confirmation(self, workspace_root):
        """
        SCENARIO: Location changed - ask for confirmation
        GIVEN: Project location is saved and current directory is DIFFERENT
        WHEN: Bot behavior is invoked
        THEN: Bot detects mismatch and asks if user wants to switch to current directory
        """
        # Given: Saved location differs from current
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        old_location = Path('C:/dev/old-project')
        create_saved_location(workspace_root, 'test_bot', str(old_location))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Bot asks if user wants to switch to current directory
        assert result.status == 'completed'
        assert 'saved_location' in result.data
        assert 'current_location' in result.data
        assert result.data['requires_confirmation'] == True
        assert 'Switch to current directory?' in result.data['message']
    
    def test_location_file_saved_when_no_confirmation_needed(self, workspace_root):
        """
        SCENARIO: Location file persistence when no confirmation needed
        GIVEN: Saved location matches current location
        WHEN: Bot behavior is invoked
        THEN: Bot saves location to current_project.json file
        """
        # Given: Saved location matches current
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        import os
        current_dir = Path(os.getcwd())
        current_project_file = create_saved_location(workspace_root, 'test_bot', str(current_dir))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Location persisted without confirmation
        assert result.data['requires_confirmation'] == False
        assert current_project_file.exists()
        
        saved_data = json.loads(current_project_file.read_text(encoding='utf-8'))
        assert saved_data['current_project'] == str(current_dir)
    
    def test_user_provides_custom_project_area_via_parameters(self, workspace_root):
        """
        SCENARIO: User provides different location during initialization via parameters
        GIVEN: No saved location exists
        WHEN: Bot behavior is invoked with project_area parameter
        THEN: Bot uses the provided project_area location
        """
        # Given: No saved location, custom project_area provided
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        custom_area = 'agile_bot/bots/base_bot/docs/stories'
        
        # When: Bot behavior is invoked with project_area parameter
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project(parameters={'project_area': custom_area})
        
        # Then: Bot proposes the custom location
        expected_location = workspace_root / custom_area
        assert result.status == 'completed'
        assert result.data['proposed_location'] == str(expected_location)
        assert result.data['requires_confirmation'] == True
    
    def test_user_changes_project_area_with_initialize_project_action(self, workspace_root):
        """
        SCENARIO: User changes project area via initialize_project action with parameters
        GIVEN: Project location is already saved
        WHEN: User invokes initialize_project with different project_area parameter
        THEN: Bot detects change and asks if user wants to switch to current directory
        """
        # Given: Old location is saved
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        old_area = 'agile_bot/bots/story_bot'
        old_location = workspace_root / old_area
        create_saved_location(workspace_root, 'test_bot', str(old_location))
        
        # When: User provides new project_area parameter
        new_area = 'agile_bot/bots/base_bot/docs/stories'
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project(parameters={'project_area': new_area})
        
        # Then: Bot detects location change and asks to switch
        expected_new_location = workspace_root / new_area
        assert result.status == 'completed'
        assert 'saved_location' in result.data
        assert 'current_location' in result.data
        assert result.data['requires_confirmation'] == True
        assert 'Switch to current directory?' in result.data['message']
    
    def test_project_area_parameter_as_hint_still_requests_confirmation(self, workspace_root):
        """
        SCENARIO: First time with project_area parameter as hint
        GIVEN: No saved location exists
        WHEN: Bot is invoked with project_area parameter
        THEN: Bot uses parameter as hint but still requests confirmation
        AND: Location is NOT saved until user confirms
        """
        # Given: No saved location
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        current_project_file = bot_dir / 'current_project.json'
        
        # When: Bot invoked with project_area parameter (as hint)
        hint_area = 'agile_bot/bots/base_bot/docs/stories'
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project(parameters={'project_area': hint_area})
        
        # Then: Bot presents hint location but requests confirmation
        expected_location = workspace_root / hint_area
        assert result.status == 'completed'
        assert result.data['proposed_location'] == str(expected_location)
        assert result.data['requires_confirmation'] == True
        
        # AND: Location NOT saved yet (waiting for confirmation)
        assert not current_project_file.exists()
    
    def test_user_confirms_proposed_location(self, workspace_root):
        """
        SCENARIO: User confirms proposed location
        GIVEN: Bot proposed a location requiring confirmation
        WHEN: User responds with confirm=True and same location
        THEN: Bot saves the confirmed location
        """
        # Given: Initial call proposes location
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        bot = Bot('test_bot', workspace_root, config_path)
        hint_area = 'agile_bot/bots/base_bot'
        expected_location = workspace_root / hint_area
        
        result1 = bot.shape.initialize_project(parameters={'project_area': hint_area})
        proposed = result1.data['proposed_location']
        
        # When: User confirms
        result2 = bot.shape.initialize_project(parameters={
            'confirm': True,
            'project_area': proposed
        })
        
        # Then: Location is saved
        assert result2.status == 'completed'
        assert result2.data['saved'] == True
        assert result2.data.get('requires_confirmation', False) == False
        
        # Verify file was saved
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        current_project_file = bot_dir / 'current_project.json'
        assert current_project_file.exists()
        
        saved_data = json.loads(current_project_file.read_text(encoding='utf-8'))
        assert saved_data['current_project'] == proposed
    
    def test_user_provides_different_location_as_confirmation_response(self, workspace_root):
        """
        SCENARIO: User provides different location as response to confirmation
        GIVEN: Bot proposed a location requiring confirmation
        WHEN: User responds with confirm=True and DIFFERENT location
        THEN: Bot saves the user's choice (not the proposed location)
        """
        # Given: Initial call proposes location
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        bot = Bot('test_bot', workspace_root, config_path)
        
        result1 = bot.shape.initialize_project()
        proposed = result1.data['proposed_location']
        
        # When: User confirms with DIFFERENT location
        user_choice = str(workspace_root / 'different-area')
        result2 = bot.shape.initialize_project(parameters={
            'confirm': True,
            'project_area': user_choice
        })
        
        # Then: User's choice is saved (not proposed location)
        assert result2.status == 'completed'
        assert result2.data['saved'] == True
        
        # Verify user's choice was saved, NOT proposed location
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        current_project_file = bot_dir / 'current_project.json'
        assert current_project_file.exists()
        
        saved_data = json.loads(current_project_file.read_text(encoding='utf-8'))
        assert saved_data['current_project'] == user_choice
        assert saved_data['current_project'] != proposed

