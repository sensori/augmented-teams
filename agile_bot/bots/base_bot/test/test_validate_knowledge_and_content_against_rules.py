"""
Validate Knowledge And Content Against Rules Tests

Tests for all stories in the 'Validate Knowledge & Content Against Rules' sub-epic:
- Track Activity for Validate Rules Action
- Complete Validate Rules Action
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.test.test_helpers import read_activity_log

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_activity_log_file(workspace: Path) -> Path:
    """Helper: Create activity log file."""
    log_dir = workspace / 'project_area'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'activity_log.json'
    log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
    return log_file

def create_workflow_state(workspace: Path, current_action: str, completed_actions: list = None) -> Path:
    """Helper: Create workflow state file."""
    state_dir = workspace / 'project_area'
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / 'workflow_state.json'
    state_file.write_text(json.dumps({
        'current_behavior': 'story_bot.exploration',
        'current_action': current_action,
        'completed_actions': completed_actions or [],
        'timestamp': '2025-12-03T10:00:00Z'
    }), encoding='utf-8')
    return state_file

def create_validation_rules(workspace: Path, bot_name: str, behavior: str, rules: list) -> Path:
    """Helper: Create validation rules file."""
    rules_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

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
# STORY: Track Activity for Validate Rules Action
# ============================================================================

class TestTrackActivityForValidateRulesAction:
    """Story: Track Activity for Validate Rules Action - Tests activity tracking for validate_rules."""

    def test_track_activity_when_validate_rules_action_starts(self, workspace_root):
        """
        SCENARIO: Track activity when validate_rules action starts
        GIVEN: behavior is 'exploration' and action is 'validate_rules'
        WHEN: validate_rules action starts execution
        THEN: Activity logger creates entry with timestamp and action_state
        """
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_root)
        
        # When: Action starts execution
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        action.track_activity_on_start()
        
        # Then: Activity logged with full path
        log_data = read_activity_log(log_file)
        assert any(
            e['action_state'] == 'story_bot.exploration.validate_rules'
            for e in log_data
        )

    def test_track_activity_when_validate_rules_action_completes(self, workspace_root):
        """
        SCENARIO: Track activity when validate_rules action completes
        GIVEN: validate_rules action started at timestamp
        WHEN: validate_rules action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_root)
        
        # When: Action completes with validation results
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        action.track_activity_on_completion(
            outputs={
                'violations_count': 2,
                'rules_checked_count': 7,
                'file_path': 'validation-report.md'
            },
            duration=240
        )
        
        # Then: Completion logged with validation metrics
        log_data = read_activity_log(log_file)
        completion_entry = next((e for e in log_data if 'outputs' in e), None)
        assert completion_entry is not None
        assert completion_entry['outputs']['violations_count'] == 2
        assert completion_entry['outputs']['rules_checked_count'] == 7
        assert completion_entry['duration'] == 240

    def test_track_multiple_validate_rules_invocations_across_behaviors(self, workspace_root):
        """
        SCENARIO: Track multiple validate_rules invocations across behaviors
        GIVEN: activity log contains entries for shape and exploration validate_rules
        WHEN: both entries are present
        THEN: activity log distinguishes same action in different behaviors
        """
        # Given: Activity log with multiple validate_rules entries
        log_dir = workspace_root / 'project_area'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            db.insert({
                'action_state': 'story_bot.shape.validate_rules',
                'timestamp': '2025-12-03T09:00:00Z',
                'outputs': {'violations_count': 0}
            })
            db.insert({
                'action_state': 'story_bot.exploration.validate_rules',
                'timestamp': '2025-12-03T10:00:00Z',
                'outputs': {'violations_count': 2}
            })
        
        # When: Read activity log
        log_data = read_activity_log(log_file)
        
        # Then: 2 separate entries with full paths
        assert len(log_data) == 2
        assert log_data[0]['action_state'] == 'story_bot.shape.validate_rules'
        assert log_data[1]['action_state'] == 'story_bot.exploration.validate_rules'

    def test_activity_log_maintains_chronological_order(self, workspace_root):
        """
        SCENARIO: Activity log maintains chronological order
        GIVEN: activity log contains 10 previous action entries
        WHEN: validate_rules entry is appended
        THEN: New entry appears at end of log in chronological order
        """
        # Given: Activity log with 10 entries
        log_dir = workspace_root / 'project_area'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            for i in range(10):
                db.insert({'action_state': f'story_bot.discovery.action_{i}', 'timestamp': f'10:{i:02d}'})
        
        # When: Append validate_rules entry
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        action.track_activity_on_start()
        
        # Then: New entry at end in chronological order
        log_data = read_activity_log(log_file)
        assert len(log_data) == 11
        assert log_data[10]['action_state'] == 'story_bot.exploration.validate_rules'


# ============================================================================
# STORY: Complete Validate Rules Action
# ============================================================================

class TestCompleteValidateRulesAction:
    """Story: Complete Validate Rules Action - Tests workflow completion at terminal action."""

    def test_validate_rules_marks_workflow_as_complete(self, workspace_root):
        """
        SCENARIO: validate_rules marks workflow as complete
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action (next_action=null)
        WHEN: validate_rules finalizes
        THEN: Workflow is marked as complete
        """
        # Given: Terminal action config
        actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / 'validate_rules'
        actions_dir.mkdir(parents=True, exist_ok=True)
        action_config = actions_dir / 'action_config.json'
        action_config.write_text(json.dumps({
            'name': 'validate_rules',
            'workflow': True,
            'order': 5,
            'next_action': None
        }), encoding='utf-8')
        
        # When: Action finalizes
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        result = action.finalize_and_complete_workflow()
        
        # Then: Workflow marked as complete
        assert result.workflow_complete
        assert result.next_action is None

    def test_validate_rules_does_not_inject_next_action_instructions(self, workspace_root):
        """
        SCENARIO: validate_rules does NOT inject next action instructions
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules finalizes
        THEN: No next action instructions injected
        """
        # Given: Terminal action
        actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / 'validate_rules'
        actions_dir.mkdir(parents=True, exist_ok=True)
        action_config = actions_dir / 'action_config.json'
        action_config.write_text(json.dumps({
            'name': 'validate_rules',
            'workflow': True,
            'order': 5,
            'next_action': None
        }), encoding='utf-8')
        
        # When: Action injects instructions
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='scenarios',
            workspace_root=workspace_root
        )
        instructions = action.inject_next_action_instructions()
        
        # Then: No next action instructions (terminal)
        assert instructions == '' or 'complete' in instructions.lower()

    def test_workflow_state_shows_all_actions_completed(self, workspace_root):
        """
        SCENARIO: Workflow state shows all actions completed
        GIVEN: validate_rules completes as final action
        WHEN: Action saves workflow state
        THEN: completed_actions contains all 5 workflow actions
        """
        # Given: Workflow state with 4 completed actions
        state_file = create_workflow_state(
            workspace_root,
            'story_bot.exploration.validate_rules',
            completed_actions=[
                {'action_state': 'story_bot.exploration.gather_context', 'timestamp': '10:00'},
                {'action_state': 'story_bot.exploration.decide_planning_criteria', 'timestamp': '10:15'},
                {'action_state': 'story_bot.exploration.build_knowledge', 'timestamp': '10:30'},
                {'action_state': 'story_bot.exploration.render_output', 'timestamp': '10:45'}
            ]
        )
        
        # When: Final action completes
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        action.save_state_on_completion()
        
        # Then: All 5 actions in completed_actions
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        assert len(state_data['completed_actions']) == 5

    def test_activity_log_records_full_workflow_completion(self, workspace_root):
        """
        SCENARIO: Activity log records full workflow completion
        GIVEN: validate_rules completes at timestamp
        WHEN: Activity logger records completion
        THEN: Activity log shows validate_rules completed and workflow finished
        """
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_root)
        
        # When: Terminal action logs completion
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='scenarios',
            workspace_root=workspace_root
        )
        action.track_activity_on_completion(
            outputs={'violations_count': 0, 'workflow_complete': True},
            duration=180
        )
        
        # Then: Completion logged with workflow_complete flag
        log_data = read_activity_log(log_file)
        completion_entry = next((e for e in log_data if 'outputs' in e), None)
        assert completion_entry is not None
        assert completion_entry['outputs']['workflow_complete']

    def test_workflow_does_not_transition_after_validate_rules(self, workspace_root):
        """
        SCENARIO: Workflow does NOT transition after validate_rules
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules attempts to transition
        THEN: No transition occurs and workflow ends
        """
        # Given: Terminal action config
        actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / 'validate_rules'
        actions_dir.mkdir(parents=True, exist_ok=True)
        action_config = actions_dir / 'action_config.json'
        action_config.write_text(json.dumps({
            'name': 'validate_rules',
            'workflow': True,
            'order': 5,
            'next_action': None
        }), encoding='utf-8')
        
        # When: Action attempts to get next action
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            workspace_root=workspace_root
        )
        next_action = action.get_next_action()
        
        # Then: No next action (terminal)
        assert next_action is None

    def test_behavior_workflow_completes_at_terminal_action(self, workspace_root):
        """
        SCENARIO: Behavior workflow completes at terminal action
        GIVEN: exploration behavior has completed all 5 workflow actions
        WHEN: validate_rules (terminal) is marked complete
        THEN: Exploration behavior workflow is complete
        """
        # Given: Workflow state with all actions completed
        state_file = create_workflow_state(
            workspace_root,
            'story_bot.exploration.validate_rules',
            completed_actions=[
                {'action_state': 'story_bot.exploration.gather_context'},
                {'action_state': 'story_bot.exploration.decide_planning_criteria'},
                {'action_state': 'story_bot.exploration.build_knowledge'},
                {'action_state': 'story_bot.exploration.render_output'},
                {'action_state': 'story_bot.exploration.validate_rules'}
            ]
        )
        
        # When: Check workflow completion status
        from agile_bot.bots.base_bot.src.workflow import Workflow
        is_complete = Workflow.is_behavior_complete('exploration', state_file)
        
        # Then: Behavior workflow is complete
        assert is_complete

