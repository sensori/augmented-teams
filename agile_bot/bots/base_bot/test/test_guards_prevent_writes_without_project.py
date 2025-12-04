"""
Tests that guards prevent file writes until current_project.json exists.

These tests verify that activity logs and workflow state are NOT written
to disk until the project location has been confirmed and saved in current_project.json.
"""
import pytest
from pathlib import Path
from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker
from agile_bot.bots.base_bot.src.state.workflow import Workflow


class TestActivityTrackerGuard:
    """Tests that ActivityTracker guard prevents writes without current_project.json."""

    def test_activity_not_tracked_when_current_project_missing(self, tmp_path):
        """
        GIVEN: current_project.json does NOT exist
        WHEN: ActivityTracker.track_start() is called
        THEN: activity_log.json is NOT created
        """
        # Given: workspace without current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Verify current_project.json doesn't exist
        bot_dir = workspace / 'agile_bot' / 'bots' / 'story_bot'
        current_project_file = bot_dir / 'current_project.json'
        assert not current_project_file.exists()
        
        # When: Track activity
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log NOT created
        activity_log = workspace / 'activity_log.json'
        assert not activity_log.exists()

    def test_activity_tracked_when_current_project_exists(self, tmp_path):
        """
        GIVEN: current_project.json exists
        WHEN: ActivityTracker.track_start() is called
        THEN: activity_log.json IS created
        """
        # Given: workspace with current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Create current_project.json
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Track activity
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'gather_context')
        
        # Then: Activity log IS created
        activity_log = workspace / 'activity_log.json'
        assert activity_log.exists()

    def test_initialize_project_action_not_tracked_without_current_project(self, tmp_path):
        """
        GIVEN: current_project.json does NOT exist
        WHEN: ActivityTracker tracks 'initialize_project' action
        THEN: activity_log.json is NOT created (no exception - project location not confirmed yet)
        """
        # Given: workspace without current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # When: Track initialize_project action
        tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')
        tracker.track_start('story_bot', 'shape', 'initialize_project')
        
        # Then: Activity log is NOT created (project location not confirmed yet)
        activity_log = workspace / 'activity_log.json'
        assert not activity_log.exists()


class TestWorkflowGuard:
    """Tests that Workflow guard prevents writes without current_project.json."""

    def test_workflow_state_not_saved_when_current_project_missing(self, tmp_path):
        """
        GIVEN: current_project.json does NOT exist
        WHEN: Workflow.save_state() is called
        THEN: workflow_state.json is NOT created
        """
        # Given: workspace without current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Verify current_project.json doesn't exist
        bot_dir = workspace / 'agile_bot' / 'bots' / 'story_bot'
        current_project_file = bot_dir / 'current_project.json'
        assert not current_project_file.exists()
        
        # When: Save workflow state
        workflow = Workflow(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace,
            states=['initialize_project', 'gather_context'],
            transitions=[]
        )
        workflow.save_state()
        
        # Then: Workflow state NOT created
        workflow_state = workspace / 'workflow_state.json'
        assert not workflow_state.exists()

    def test_workflow_state_saved_when_current_project_exists(self, tmp_path):
        """
        GIVEN: current_project.json exists
        WHEN: Workflow.save_state() is called
        THEN: workflow_state.json IS created
        """
        # Given: workspace with current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # Create current_project.json
        from agile_bot.bots.base_bot.test.test_helpers import create_saved_location
        create_saved_location(workspace, 'story_bot', str(workspace))
        
        # When: Save workflow state
        workflow = Workflow(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace,
            states=['initialize_project', 'gather_context'],
            transitions=[]
        )
        workflow.save_state()
        
        # Then: Workflow state IS created
        workflow_state = workspace / 'workflow_state.json'
        assert workflow_state.exists()

    def test_completed_actions_not_saved_when_current_project_missing(self, tmp_path):
        """
        GIVEN: current_project.json does NOT exist
        WHEN: Workflow.save_completed_action() is called
        THEN: workflow_state.json is NOT created
        """
        # Given: workspace without current_project.json
        workspace = tmp_path / 'workspace'
        workspace.mkdir()
        
        # When: Save completed action
        workflow = Workflow(
            bot_name='story_bot',
            behavior='shape',
            workspace_root=workspace,
            states=['initialize_project', 'gather_context'],
            transitions=[]
        )
        workflow.save_completed_action('gather_context')
        
        # Then: Workflow state NOT created
        workflow_state = workspace / 'workflow_state.json'
        assert not workflow_state.exists()




