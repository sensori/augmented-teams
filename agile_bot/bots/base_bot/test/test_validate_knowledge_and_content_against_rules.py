"""
Validate Knowledge And Content Against Rules Tests

Tests for all stories in the 'Validate Knowledge & Content Against Rules' sub-epic:
- Track Activity for Validate Rules Action
- Complete Validate Rules Action
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, read_activity_log, create_activity_log_file, create_workflow_state
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_workflow_state_local(workspace_dir: Path, current_action: str, completed_actions: list = None) -> Path:
    """Helper: Create workflow state file in workspace directory."""
    state_file = workspace_dir / 'workflow_state.json'
    state_file.write_text(json.dumps({
        'current_behavior': 'story_bot.exploration',
        'current_action': current_action,
        'completed_actions': completed_actions or [],
        'timestamp': '2025-12-03T10:00:00Z'
    }), encoding='utf-8')
    return state_file

def create_validation_rules(bot_dir: Path, behavior: str, rules: list) -> Path:
    """Helper: Create validation rules file in bot directory."""
    rules_dir = bot_dir / 'behaviors' / behavior / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

# ============================================================================
# FIXTURES
# ============================================================================

# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# STORY: Track Activity for Validate Rules Action
# ============================================================================

class TestTrackActivityForValidateRulesAction:
    """Story: Track Activity for Validate Rules Action - Tests activity tracking for validate_rules."""

    def test_track_activity_when_validate_rules_action_starts(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when validate_rules action starts
        GIVEN: behavior is 'exploration' and action is 'validate_rules'
        WHEN: validate_rules action starts execution
        THEN: Activity logger creates entry with timestamp and action_state
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action starts execution
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
        )
        action.track_activity_on_start()
        
        # Then: Activity logged with full path
        log_data = read_activity_log(workspace_directory)
        assert any(
            e['action_state'] == 'story_bot.exploration.validate_rules'
            for e in log_data
        )

    def test_track_activity_when_validate_rules_action_completes(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when validate_rules action completes
        GIVEN: validate_rules action started at timestamp
        WHEN: validate_rules action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action completes with validation results
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
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
        log_data = read_activity_log(workspace_directory)
        completion_entry = next((e for e in log_data if 'outputs' in e), None)
        assert completion_entry is not None
        assert completion_entry['outputs']['violations_count'] == 2
        assert completion_entry['outputs']['rules_checked_count'] == 7
        assert completion_entry['duration'] == 240

    def test_track_multiple_validate_rules_invocations_across_behaviors(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track multiple validate_rules invocations across behaviors
        GIVEN: activity log contains entries for shape and exploration validate_rules
        WHEN: both entries are present
        THEN: activity log distinguishes same action in different behaviors
        """
        # Given: Activity log with multiple validate_rules entries (in workspace_directory)
        workspace_directory.mkdir(parents=True, exist_ok=True)
        log_file = workspace_directory / 'activity_log.json'
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
        log_data = read_activity_log(workspace_directory)
        
        # Then: 2 separate entries with full paths
        assert len(log_data) == 2
        assert log_data[0]['action_state'] == 'story_bot.shape.validate_rules'
        assert log_data[1]['action_state'] == 'story_bot.exploration.validate_rules'

    def test_activity_log_maintains_chronological_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity log maintains chronological order
        GIVEN: activity log contains 10 previous action entries
        WHEN: validate_rules entry is appended
        THEN: New entry appears at end of log in chronological order
        """
        # Given: Activity log with 10 entries (in workspace_directory)
        workspace_directory.mkdir(parents=True, exist_ok=True)
        
        # Bootstrap environment for activity tracking
        from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env
        bootstrap_env(bot_directory, workspace_directory)
        
        log_file = workspace_directory / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            for i in range(10):
                db.insert({'action_state': f'story_bot.discovery.action_{i}', 'timestamp': f'10:{i:02d}'})
        
        # When: Append validate_rules entry
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
        )
        action.track_activity_on_start()
        
        # Then: New entry at end in chronological order
        log_data = read_activity_log(workspace_directory)
        assert len(log_data) == 11
        assert log_data[10]['action_state'] == 'story_bot.exploration.validate_rules'


# ============================================================================
# STORY: Complete Validate Rules Action
# ============================================================================

class TestCompleteValidateRulesAction:
    """Story: Complete Validate Rules Action - Tests workflow completion at terminal action."""

    def test_validate_rules_marks_workflow_as_complete(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules marks workflow as complete
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action (next_action=null)
        WHEN: validate_rules finalizes
        THEN: Workflow is marked as complete (no next action)
        """
        # Given: Terminal action
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
        )
        
        # When: Action finalizes with no next action
        result = action.finalize_and_transition(next_action=None)
        
        # Then: No next action (terminal)
        assert result.next_action is None

    def test_validate_rules_does_not_inject_next_action_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules does NOT inject next action instructions
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules finalizes
        THEN: No next action instructions injected
        """
        # Given: Terminal action
        actions_dir = workspace_directory / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions' / 'validate_rules'
        actions_dir.mkdir(parents=True, exist_ok=True)
        action_config = actions_dir / 'action_config.json'
        action_config.write_text(json.dumps({
            'name': 'validate_rules',
            'workflow': True,
            'order': 5,
            'next_action': None
        }), encoding='utf-8')
        
        # When: Action injects instructions
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='scenarios',
            bot_directory=bot_directory
        )
        instructions = action.inject_next_action_instructions()
        
        # Then: No next action instructions (terminal)
        assert instructions == '' or 'complete' in instructions.lower()

    def test_workflow_state_shows_all_actions_completed(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow state shows all actions completed
        GIVEN: validate_rules completes as final action
        WHEN: Action tracks completion
        THEN: Activity log records the completion
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Final action completes
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
        )
        action.track_activity_on_completion(
            outputs={'violations_count': 0, 'workflow_complete': True},
            duration=180
        )
        
        # Then: Completion recorded in activity log
        log_data = read_activity_log(workspace_directory)
        completion_entry = next((e for e in log_data if 'outputs' in e), None)
        assert completion_entry is not None
        assert completion_entry['outputs']['workflow_complete']

    def test_activity_log_records_full_workflow_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity log records full workflow completion
        GIVEN: validate_rules completes at timestamp
        WHEN: Activity logger records completion
        THEN: Activity log shows validate_rules completed and workflow finished
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Terminal action logs completion
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='scenarios',
            bot_directory=bot_directory
        )
        action.track_activity_on_completion(
            outputs={'violations_count': 0, 'workflow_complete': True},
            duration=180
        )
        
        # Then: Completion logged with workflow_complete flag
        log_data = read_activity_log(workspace_directory)
        completion_entry = next((e for e in log_data if 'outputs' in e), None)
        assert completion_entry is not None
        assert completion_entry['outputs']['workflow_complete']

    def test_workflow_does_not_transition_after_validate_rules(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow does NOT transition after validate_rules
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules provides next action instructions
        THEN: No next action instructions (empty string indicates terminal action)
        """
        # Given: Terminal action
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='exploration',
            bot_directory=bot_directory
        )
        
        # When: Action provides next action instructions
        instructions = action.inject_next_action_instructions()
        
        # Then: No next action instructions (terminal)
        assert instructions == ""

    def test_behavior_workflow_completes_at_terminal_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Behavior workflow completes at terminal action
        GIVEN: exploration behavior has completed all 5 workflow actions
        WHEN: validate_rules (terminal) is marked complete
        THEN: Exploration behavior workflow is complete
        """
        # Given: Workflow state with all actions completed
        state_file = create_workflow_state(
            workspace_directory,
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
        from agile_bot.bots.base_bot.src.state.workflow import Workflow
        is_complete = Workflow.is_behavior_complete('exploration', state_file)
        
        # Then: Behavior workflow is complete
        assert is_complete

    def test_validate_rules_returns_instructions_with_rules_as_context(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules returns instructions with rules as supporting context
        GIVEN: validate_rules action has base instructions and validation rules
        WHEN: validate_rules action executes
        THEN: Return value contains base_instructions (primary) and validation_rules (context)
        AND: Return value contains content_to_validate information
        """
        # Given: Base action instructions exist
        # Use actual repo root (where base_actions_dir looks)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        validate_rules_dir = base_actions_dir / '7_validate_rules'
        validate_rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create action_config.json
        action_config_file = validate_rules_dir / 'action_config.json'
        action_config_file.write_text(json.dumps({
            'name': 'validate_rules',
            'workflow': True,
            'order': 7
        }), encoding='utf-8')
        
        # Create instructions.json with proper structure
        base_instructions = {
            'actionName': 'validate_rules',
            'instructions': [
                'Load and review clarification.json and planning.json',
                'Check Content Data against all rules listed above',
                'Generate a validation report'
            ]
        }
        instructions_file = validate_rules_dir / 'instructions.json'
        instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
        
        # Given: Behavior-specific rules exist
        # Rules should be in bot_directory, not workspace_directory
        behavior_dir = bot_directory / 'behaviors' / '1_shape'
        rules_dir = behavior_dir / '3_rules'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rule_file = rules_dir / 'test_rule.json'
        rule_file.write_text(json.dumps({
            'description': 'Test rule',
            'examples': []
        }), encoding='utf-8')
        
        # Bootstrap environment variables
        from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Action executes
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        result = action.do_execute(parameters={})
        
        # Then: Return value has instructions structure
        assert 'instructions' in result, "Result should contain 'instructions' key"
        instructions = result['instructions']
        
        # Then: base_instructions are primary (list of instruction strings)
        assert 'base_instructions' in instructions, (
            f"Expected 'base_instructions' in instructions, but got keys: {instructions.keys()}"
        )
        base_instructions_list = instructions['base_instructions']
        assert isinstance(base_instructions_list, list), (
            f"base_instructions should be a list, got: {type(base_instructions_list)}"
        )
        assert len(base_instructions_list) > 0, "base_instructions should not be empty"
        assert 'Load and review clarification.json' in ' '.join(base_instructions_list), (
            "base_instructions should contain the action instructions"
        )
        
        # Then: validation_rules are supporting context (not primary)
        assert 'validation_rules' in instructions, (
            f"Expected 'validation_rules' in instructions, but got keys: {instructions.keys()}"
        )
        validation_rules = instructions['validation_rules']
        assert isinstance(validation_rules, list), (
            f"validation_rules should be a list, got: {type(validation_rules)}"
        )
        # Should have at least the behavior rule we created
        assert len(validation_rules) > 0, "validation_rules should contain rules"
        
        # Then: content_to_validate provides workspace information
        assert 'content_to_validate' in instructions, (
            f"Expected 'content_to_validate' in instructions, but got keys: {instructions.keys()}"
        )
        content_info = instructions['content_to_validate']
        assert 'workspace_location' in content_info or 'project_location' in content_info, (
            "content_to_validate should contain workspace_location or project_location"
        )
        # Check that workspace_directory is referenced in the location
        location_key = 'workspace_location' if 'workspace_location' in content_info else 'project_location'
        location_value = content_info[location_key]
        assert str(workspace_directory) in str(location_value), (
            f"{location_key} should point to the workspace directory"
        )
        assert 'rendered_outputs' in content_info, (
            "content_to_validate should contain rendered_outputs list"
        )
        
        # Then: Action and behavior are specified
        assert instructions.get('action') == 'validate_rules', (
            "instructions should specify action='validate_rules'"
        )
        assert instructions.get('behavior') == 'shape', (
            "instructions should specify behavior='shape'"
        )
        
        # Then: report_path is provided for saving validation report
        assert 'report_path' in content_info, (
            "content_to_validate should contain report_path where validation report should be saved"
        )
        report_path = content_info['report_path']
        assert report_path.endswith('validation-report.md'), (
            f"report_path should point to validation-report.md, got: {report_path}"
        )
        # report_path should be in workspace directory structure
        assert str(workspace_directory) in report_path or 'docs' in report_path, (
            f"report_path should be in workspace directory, got: {report_path}"
        )

    def test_validate_rules_provides_report_path_for_saving_validation_report(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules provides report_path for saving validation report
        GIVEN: validate_rules action executes
        AND: workspace directory has docs/stories/ folder
        WHEN: Action identifies content to validate
        THEN: Action includes report_path in content_to_validate
        AND: report_path points to {workspace_area}/docs/stories/validation-report.md
        AND: base_instructions include instruction to save report to report_path
        AND: AI receives clear instruction to write validation report to file
        """
        # Given: Base action instructions exist with save report instruction
        # Use actual repo root (where base_actions_dir looks)
        from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        validate_rules_dir = base_actions_dir / '7_validate_rules'
        validate_rules_dir.mkdir(parents=True, exist_ok=True)
        
        base_instructions = {
            'instructions': [
                'Load and review clarification.json and planning.json',
                'Check Content Data against all rules listed above',
                'Generate a validation report',
                'Save the validation report to validation-report.md in docs/stories/'
            ]
        }
        instructions_file = validate_rules_dir / 'instructions.json'
        instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
        
        # Given: Workspace directory with docs/stories/ folder
        docs_dir = workspace_directory / 'docs' / 'stories'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Bootstrap environment variables
        from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Action executes
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        action = ValidateRulesAction(
            bot_name='story_bot',
            behavior='shape',
            bot_directory=bot_directory
        )
        result = action.do_execute(parameters={})
        
        # Then: report_path is included in content_to_validate
        instructions = result['instructions']
        content_info = instructions['content_to_validate']
        
        assert 'report_path' in content_info, (
            "content_to_validate must include report_path for saving validation report"
        )
        
        report_path = content_info['report_path']
        expected_report_path = docs_dir / 'validation-report.md'
        
        assert report_path == str(expected_report_path), (
            f"report_path should be {expected_report_path}, got: {report_path}"
        )
        
        # Then: base_instructions include instruction to save report
        base_instructions_list = instructions['base_instructions']
        instructions_text = ' '.join(base_instructions_list)
        assert 'save' in instructions_text.lower() or 'write' in instructions_text.lower() or 'validation-report' in instructions_text.lower(), (
            "base_instructions should include instruction to save/write validation report"
        )
        
        # Then: report_path is accessible and in correct location
        report_path_obj = Path(report_path)
        assert report_path_obj.parent == docs_dir, (
            f"report_path parent should be docs/stories directory, got: {report_path_obj.parent}"
        )
        assert report_path_obj.name == 'validation-report.md', (
            f"report_path filename should be validation-report.md, got: {report_path_obj.name}"
        )

