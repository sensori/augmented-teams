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
    """Helper: Create saved project location file."""
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    location_file = bot_dir / 'project_area' / 'project_location.json'
    location_file.parent.mkdir(parents=True, exist_ok=True)
    location_file.write_text(json.dumps({'project_location': location}), encoding='utf-8')
    return location_file


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
        
        # Then: Bot detects bot directory and requests confirmation
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        assert result.status == 'completed'
        assert result.data['proposed_location'] == str(bot_dir)
        assert result.data['requires_confirmation'] == True
        assert 'Confirm?' in result.data['message']
    
    def test_subsequent_invocation_same_location_skips_confirmation(self, workspace_root):
        """
        SCENARIO: Subsequent invocation with same location (no confirmation bias)
        GIVEN: Project location is saved and current directory matches saved location
        WHEN: Bot behavior is invoked
        THEN: Bot does NOT ask user for confirmation
        """
        # Given: Saved location matches current bot directory
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        create_saved_location(workspace_root, 'test_bot', str(bot_dir))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Bot skips confirmation
        assert result.status == 'completed'
        assert result.data.get('requires_confirmation') == False
        assert result.data['project_location'] == str(bot_dir)
    
    def test_location_changed_requests_confirmation(self, workspace_root):
        """
        SCENARIO: Location changed - ask for confirmation
        GIVEN: Project location is saved and current directory is DIFFERENT
        WHEN: Bot behavior is invoked
        THEN: Bot detects mismatch and requests confirmation
        """
        # Given: Saved location differs from current
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        old_location = Path('C:/dev/old-project')
        create_saved_location(workspace_root, 'test_bot', str(old_location))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Bot requests confirmation for location change
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        assert result.status == 'completed'
        assert result.data['saved_location'] == str(old_location)
        assert result.data['current_location'] == str(bot_dir)
        assert result.data['requires_confirmation'] == True
        assert 'Switch to new location?' in result.data['message']
    
    def test_location_file_saved_when_no_confirmation_needed(self, workspace_root):
        """
        SCENARIO: Location file persistence when no confirmation needed
        GIVEN: Saved location matches current location
        WHEN: Bot behavior is invoked
        THEN: Bot saves location to persistent storage file
        """
        # Given: Saved location matches current
        config_path = create_bot_config(workspace_root, 'test_bot', ['shape'])
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        location_file = create_saved_location(workspace_root, 'test_bot', str(bot_dir))
        
        # When: Bot behavior is invoked
        bot = Bot('test_bot', workspace_root, config_path)
        result = bot.shape.initialize_project()
        
        # Then: Location persisted without confirmation
        bot_dir = workspace_root / 'agile_bot' / 'bots' / 'test_bot'
        assert result.data['requires_confirmation'] == False
        assert location_file.exists()
        
        saved_data = json.loads(location_file.read_text(encoding='utf-8'))
        assert saved_data['project_location'] == str(bot_dir)
    
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
        THEN: Bot detects change and requests confirmation for new location
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
        
        # Then: Bot detects location change and requests confirmation
        expected_new_location = workspace_root / new_area
        assert result.status == 'completed'
        assert result.data['saved_location'] == str(old_location)
        assert result.data['current_location'] == str(expected_new_location)
        assert result.data['requires_confirmation'] == True
        assert 'Switch to new location?' in result.data['message']

