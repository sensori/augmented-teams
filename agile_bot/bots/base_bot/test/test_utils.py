"""
Base Bot Utils Tests

Tests for utility functions in base_bot/src/utils.py
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.bot import Behavior


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_behavior_folder(workspace: Path, bot_name: str, folder_name: str) -> Path:
    """Helper: Create behavior folder."""
    behavior_folder = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / folder_name
    behavior_folder.mkdir(parents=True, exist_ok=True)
    return behavior_folder


# ============================================================================
# TESTS: find_behavior_folder
# ============================================================================

class TestFindBehaviorFolder:
    """Tests for find_behavior_folder utility function."""

    def test_finds_behavior_folder_with_number_prefix(self, workspace_root):
        """
        SCENARIO: Find behavior folder with number prefix
        GIVEN: Behavior folder exists with number prefix (8_tests)
        WHEN: find_behavior_folder is called with behavior name without prefix (tests)
        THEN: Returns path to numbered folder (8_tests)
        """
        # Given: Create numbered behavior folder
        bot_name = 'test_bot'
        folder_name = '8_tests'
        behavior_name = 'tests'
        
        behavior_folder = create_behavior_folder(workspace_root, bot_name, folder_name)
        
        # When: Find folder using behavior name (without number)
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, behavior_name)
        
        # Then: Returns numbered folder
        assert found_folder == behavior_folder
        assert found_folder.name == '8_tests'

    def test_finds_shape_folder_with_number_prefix(self, workspace_root):
        """
        SCENARIO: Find shape folder with number prefix
        GIVEN: Behavior folder exists with number prefix (1_shape)
        WHEN: find_behavior_folder is called with behavior name (shape)
        THEN: Returns path to numbered folder (1_shape)
        """
        # Given: Create numbered behavior folder
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(workspace_root, bot_name, '1_shape')
        
        # When: Find folder using behavior name
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, 'shape')
        
        # Then: Returns numbered folder
        assert found_folder == behavior_folder
        assert found_folder.name == '1_shape'

    def test_finds_exploration_folder_with_number_prefix(self, workspace_root):
        """
        SCENARIO: Find exploration folder with number prefix
        GIVEN: Behavior folder exists with number prefix (5_exploration)
        WHEN: find_behavior_folder is called with behavior name (exploration)
        THEN: Returns path to numbered folder (5_exploration)
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(workspace_root, bot_name, '5_exploration')
        
        # When
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, 'exploration')
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == '5_exploration'

    def test_raises_error_when_behavior_folder_not_found(self, workspace_root):
        """
        SCENARIO: Raises error when behavior folder doesn't exist
        GIVEN: Behavior folder does not exist
        WHEN: find_behavior_folder is called
        THEN: Raises FileNotFoundError with clear message
        """
        # Given: No behavior folder exists
        bot_name = 'test_bot'
        behavior_name = 'nonexistent'
        
        # When/Then: Raises FileNotFoundError
        
        with pytest.raises(FileNotFoundError, match='Behavior folder not found'):
            Behavior.find_behavior_folder(workspace_root, bot_name, behavior_name)

    def test_handles_prioritization_folder_with_prefix(self, workspace_root):
        """
        SCENARIO: Find prioritization folder with number prefix
        GIVEN: Behavior folder exists as 2_prioritization
        WHEN: find_behavior_folder is called with behavior name (prioritization)
        THEN: Returns path to 2_prioritization
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(workspace_root, bot_name, '2_prioritization')
        
        # When
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, 'prioritization')
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == '2_prioritization'

    def test_handles_scenarios_folder_with_prefix(self, workspace_root):
        """
        SCENARIO: Find scenarios folder with number prefix
        GIVEN: Behavior folder exists as 6_scenarios
        WHEN: find_behavior_folder is called with behavior name (scenarios)
        THEN: Returns path to 6_scenarios
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(workspace_root, bot_name, '6_scenarios')
        
        # When
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, 'scenarios')
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == '6_scenarios'

    def test_handles_examples_folder_with_prefix(self, workspace_root):
        """
        SCENARIO: Find examples folder with number prefix
        GIVEN: Behavior folder exists as 7_examples
        WHEN: find_behavior_folder is called with behavior name (examples)
        THEN: Returns path to 7_examples
        """
        # Given
        bot_name = 'story_bot'
        behavior_folder = create_behavior_folder(workspace_root, bot_name, '7_examples')
        
        # When
        
        found_folder = Behavior.find_behavior_folder(workspace_root, bot_name, 'examples')
        
        # Then
        assert found_folder == behavior_folder
        assert found_folder.name == '7_examples'

