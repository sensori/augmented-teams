"""
Build Knowledge Tests

Tests for all stories in the 'Build Knowledge' sub-epic:
- Track Activity for Build Knowledge Action
- Proceed To Render Output
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.build_knowledge_action import BuildKnowledgeAction
from agile_bot.bots.base_bot.test.test_helpers import (
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action,
    create_knowledge_graph_template
)

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
# STORY: Track Activity for Build Knowledge Action
# ============================================================================

class TestTrackActivityForBuildKnowledgeAction:
    """Story: Track Activity for Build Knowledge Action - Tests activity tracking for build_knowledge."""

    def test_track_activity_when_build_knowledge_action_starts(self, workspace_root):
        verify_action_tracks_start(workspace_root, BuildKnowledgeAction, 'build_knowledge')

    def test_track_activity_when_build_knowledge_action_completes(self, workspace_root):
        verify_action_tracks_completion(
            workspace_root,
            BuildKnowledgeAction,
            'build_knowledge',
            outputs={'knowledge_items_count': 12, 'file_path': 'knowledge.json'},
            duration=420
        )


# ============================================================================
# STORY: Proceed To Render Output
# ============================================================================

class TestProceedToRenderOutput:
    """Story: Proceed To Render Output - Tests transition to render_output action."""

    def test_seamless_transition_from_build_knowledge_to_render_output(self, workspace_root):
        verify_workflow_transition(workspace_root, 'build_knowledge', 'render_output')

    def test_workflow_state_captures_build_knowledge_completion(self, workspace_root):
        verify_workflow_saves_completed_action(workspace_root, 'build_knowledge')


# ============================================================================
# STORY: Inject Knowledge Graph Template for Build Knowledge
# ============================================================================

class TestInjectKnowledgeGraphTemplateForBuildKnowledge:
    """Story: Inject Knowledge Graph Template for Build Knowledge - Tests template injection."""

    def test_action_injects_knowledge_graph_template(self, workspace_root):
        bot_name = 'test_bot'
        behavior = 'exploration'
        template_name = 'story-graph-explored-outline.json'
        
        template_file = create_knowledge_graph_template(workspace_root, bot_name, behavior, template_name)
        
        action_obj = BuildKnowledgeAction(bot_name=bot_name, behavior=behavior, workspace_root=workspace_root)
        instructions = action_obj.inject_knowledge_graph_template()
        
        assert 'knowledge_graph_template' in instructions
        assert template_name in instructions['knowledge_graph_template']
        assert Path(instructions['knowledge_graph_template']).exists()

    def test_action_raises_error_when_template_missing(self, workspace_root):
        bot_name = 'test_bot'
        behavior = 'exploration'
        
        behavior_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        action_obj = BuildKnowledgeAction(bot_name=bot_name, behavior=behavior, workspace_root=workspace_root)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            action_obj.inject_knowledge_graph_template()
        
        assert 'Knowledge graph template not found' in str(exc_info.value) or 'template' in str(exc_info.value).lower()

