"""
Activity Tracking Tests for Project Area

Tests that activity logs are written to the PROJECT's project_area,
not the BOT's project_area.

SCENARIO: Story bot working on base_bot project should track activity 
in workspace_root/project_area/, NOT in story_bot/project_area/
"""
import pytest
from pathlib import Path
from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker


class TestActivityTrackingLocation:
    """Tests that activity is tracked in the correct project_area location."""

    def test_activity_logged_to_project_area_not_bot_area(self, tmp_path):
        """
        GIVEN: story_bot is working on a project (e.g., base_bot)
        WHEN: activity is tracked
        THEN: activity_log.json is written to workspace_root/
        AND NOT to workspace_root/agile_bot/bots/story_bot/
        """
        # Given: workspace root and current_project set
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Create current_project.json so activity tracking works
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Activity tracker tracks activity
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log exists in workspace root (no project_area subdirectory)
        expected_log = workspace / 'activity_log.json'
        assert expected_log.exists(), f"Activity log should be at {expected_log}"
        
        # And: Activity log does NOT exist in bot's area
        bot_area_log = workspace / 'agile_bot' / 'bots' / 'story_bot' / 'activity_log.json'
        assert not bot_area_log.exists(), f"Activity log should NOT be at {bot_area_log}"

    def test_activity_log_contains_correct_entry(self, tmp_path):
        """
        GIVEN: story_bot is working on a project
        WHEN: activity is tracked
        THEN: activity log contains the entry
        """
        # Given: workspace root and current_project set
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Create current_project.json so activity tracking works
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Activity tracker tracks activity
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log has entry
        from tinydb import TinyDB
        log_file = workspace / 'activity_log.json'
        with TinyDB(log_file) as db:
            entries = db.all()
            assert len(entries) == 1
            assert entries[0]['action_state'] == 'story_bot.shape.gather_context'
            assert entries[0]['status'] == 'started'



