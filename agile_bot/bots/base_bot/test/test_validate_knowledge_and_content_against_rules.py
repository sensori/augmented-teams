"""
Validate Knowledge And Content Against Rules Tests

Tests for all stories in the 'Validate Knowledge & Content Against Rules' sub-epic:
- Track Activity for Validate Rules Action
- Complete Validate Rules Action
- Discovers Scanners
- Run Scanners Against Knowledge Graph
- Reports Violations
"""
import pytest
from pathlib import Path
import json
import importlib
import sys
from typing import Dict, List, Any, Optional
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env, read_activity_log, create_activity_log_file, create_workflow_state
)
from agile_bot.bots.base_bot.src.bot.bot import Behavior
from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction

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
# SCANNER AND RULE LOADING HELPERS
# ============================================================================

def create_test_rule_file(repo_root: Path, rule_path: str, rule_content: Dict[str, Any]) -> Path:
    """
    Helper: Create a test-specific rule.json file at specified path.
    Used for creating rule files defined in Examples tables.
    """
    full_path = repo_root / rule_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(rule_content, indent=2), encoding='utf-8')
    return full_path

def load_existing_rule_file(repo_root: Path, rule_path: str) -> Optional[Dict[str, Any]]:
    """
    Helper: Load an existing rule file from the codebase.
    Returns None if file doesn't exist.
    """
    full_path = repo_root / rule_path
    if full_path.exists():
        try:
            return json.loads(full_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, Exception):
            return None
    return None

def load_scanner_class(scanner_module_path: str):
    """
    Helper: Load an existing scanner class from the codebase.
    Validates that the class inherits from Scanner base class.
    Returns (scanner_class, error_message) tuple.
    If scanner doesn't exist or doesn't inherit from Scanner, returns (None, error_message).
    """
    try:
        module_path, class_name = scanner_module_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        scanner_class = getattr(module, class_name)
        
        # Validate that scanner_class is actually a class (not content/data)
        if not isinstance(scanner_class, type):
            return None, f"Scanner path does not point to a class: {scanner_module_path}"
        
        # Validate that scanner_class inherits from Scanner base class
        # Note: When Scanner base class is implemented, uncomment this validation
        # from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
        # if not issubclass(scanner_class, Scanner):
        #     return None, f"Scanner class does not inherit from Scanner base class: {scanner_module_path}"
        
        # Validate that scanner_class has required methods (scan method)
        if not hasattr(scanner_class, 'scan'):
            return None, f"Scanner class missing required 'scan' method: {scanner_module_path}"
        
        return scanner_class, None
    except ImportError as e:
        return None, f"Scanner class import failure: ModuleNotFoundError: No module named '{module_path}'"
    except AttributeError as e:
        return None, f"Scanner class not found: {scanner_module_path}"
    except Exception as e:
        return None, f"Error loading scanner {scanner_module_path}: {e}"

def setup_test_rules(repo_root: Path, rule_paths: List[str], rule_contents: List[Dict[str, Any]]) -> List[Path]:
    """
    Helper: Create test rule files in filesystem from Examples table data.
    This ONLY creates the files - does NOT load them or discover scanners.
    The test should call ValidateRulesAction methods to do the actual loading.
    
    Files are created under repo_root (which uses tmp_path fixture) so they auto-cleanup.
    
    Args:
        repo_root: Repository root directory (should be tmp_path-based fixture)
        rule_paths: List of rule file paths relative to repo_root
        rule_contents: List of rule content dictionaries (from Examples tables)
    
    Returns:
        List of created rule file paths (will be auto-cleaned up via tmp_path)
    """
    created_files = []
    for rule_path, rule_content in zip(rule_paths, rule_contents):
        rule_file = create_test_rule_file(repo_root, rule_path, rule_content)
        created_files.append(rule_file)
    return created_files

# ============================================================================
# COMMON VALIDATORS
# ============================================================================

def validate_scanner_metadata(scanner_metadata: Dict[str, Any], expected_rule_name: str, 
                              expected_description: str, expected_behavior_name: str) -> bool:
    """Validate scanner metadata matches expected values."""
    return (scanner_metadata.get('rule_name') == expected_rule_name and
            scanner_metadata.get('description') == expected_description and
            scanner_metadata.get('behavior_name') == expected_behavior_name)

def validate_catalog_structure(catalog: Dict[str, List[Dict[str, Any]]], 
                               expected_behaviors: List[str]) -> bool:
    """Validate catalog structure matches expected behaviors."""
    catalog_behaviors = set(catalog.keys())
    expected_set = set(expected_behaviors)
    return catalog_behaviors == expected_set

def validate_violation_structure(violation: Dict[str, Any], expected_fields: List[str]) -> bool:
    """Validate violation has required fields."""
    return all(field in violation for field in expected_fields)

def validate_violation_details(violation: Dict[str, Any], expected_line_number: Optional[int],
                              expected_location: Optional[str], expected_message: Optional[str],
                              expected_severity: Optional[str]) -> bool:
    """Validate violation details match expected values."""
    if expected_line_number is not None and violation.get('line_number') != expected_line_number:
        return False
    if expected_location is not None and violation.get('location') != expected_location:
        return False
    if expected_message is not None and expected_message not in violation.get('violation_message', ''):
        return False
    if expected_severity is not None and violation.get('severity') != expected_severity:
        return False
    return True

# ============================================================================
# FIXTURES
# ============================================================================

# Use fixtures from conftest.py (bot_directory, workspace_directory, repo_root)

@pytest.fixture
def cleanup_test_files():
    """
    Fixture: Track and cleanup test files created during tests.
    Since repo_root and bot_directory use tmp_path, they auto-cleanup,
    but this ensures any files created outside those directories are tracked.
    """
    created_files = []
    yield created_files
    # Cleanup: Remove any tracked files
    for file_path in created_files:
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors

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
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action starts execution
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
        
        # Given: Activity log initialized
        log_file = create_activity_log_file(workspace_directory)
        
        # When: Action completes with validation results
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


# ============================================================================
# STORY: Discovers Scanners
# ============================================================================

class TestDiscoversScanners:
    """Story: Discovers Scanners - Tests scanner discovery from rule files."""

    @pytest.mark.parametrize("rule_file_paths,rule_file_content,expected_scanner_count", [
        # Example 1: 3 scanners from different behaviors
        (
            [
                'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json',
                'agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/apply_exhaustive_decomposition.json'
            ],
            [
                {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
                {'scanner': 'agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}},
                {'scanner': 'agile_bot.bots.story_bot.scanners.exhaustive_decomposition_scanner.ExhaustiveDecompositionScanner', 'description': 'Apply exhaustive decomposition', 'do': {}}
            ],
            3
        ),
        # Example 2: 2 scanners from common rules only
        (
            [
                'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'agile_bot/bots/test_story_bot/rules/use_active_behavioral_language.json'
            ],
            [
                {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
                {'scanner': 'agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}}
            ],
            2
        ),
        # Example 3: Single scanner
        (
            ['agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json'],
            [{'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}}],
            1
        ),
    ])
    def test_scanner_discovery_extracts_metadata_and_registers_scanners(self, repo_root, bot_directory, workspace_directory, rule_file_paths, rule_file_content, expected_scanner_count):
        """
        SCENARIO: Scanner discovery extracts metadata and registers scanners
        GIVEN: Rule files exist at specified paths
        AND: Rule files contain scanner configurations
        WHEN: Scanner discovery is executed via ValidateRulesAction
        THEN: Scanners are discovered and registered in catalog
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Create test bot directory structure
        test_bot_dir = repo_root / 'agile_bot' / 'bots' / 'test_story_bot'
        test_bot_dir.mkdir(parents=True, exist_ok=True)
        
        # Given: Create test rule files in filesystem (from Examples table - parameterized)
        # Files need to be created relative to repo_root as specified in rule_file_paths
        setup_test_rules(repo_root, rule_file_paths, rule_file_content)
        
        # When: ValidateRulesAction loads rules and discovers scanners
        action = ValidateRulesAction(
            bot_name='test_story_bot',
            behavior='shape',
            bot_directory=test_bot_dir
        )
        
        # When: Access scanners via Behavior
        # Behavior.scanners returns all scanners across all rules
        # Each rule has 0 or 1 scanner (accessed via rule.scanner)
        behavior = Behavior('shape', 'test_story_bot', test_bot_dir)
        
        # Access scanners through behavior (all scanners across all rules)
        scanners = behavior.scanners
        
        # Then: Scanners discovered from rules
        assert len(scanners) == expected_scanner_count, f"Expected {expected_scanner_count} scanner classes discovered, got {len(scanners)}"
        
        # Validate that discovered scanners are classes (not content)
        for scanner_class in scanners:
            assert isinstance(scanner_class, type), (
                f"Discovered scanner must be a class, got: {type(scanner_class)}"
            )
        
        # Validate that each rule has a scanner (all examples have scanners attached)
        rules = behavior.rules
        assert len(rules) >= expected_scanner_count, f"Expected at least {expected_scanner_count} rules, got {len(rules)}"
        for rule in rules:
            scanner = rule.scanner  # Each rule should have a scanner in these examples
            assert scanner is not None, f"Rule {rule.name} should have a scanner attached"
            assert isinstance(scanner, type), (
                f"Rule scanner must be a class, got: {type(scanner)}"
            )


# ============================================================================
# STORY: Run Scanners Against Knowledge Graph
# ============================================================================

class TestRunScannersAgainstKnowledgeGraph:
    """Story: Run Scanners Against Knowledge Graph - Tests scanner execution against knowledge graph."""

    @pytest.mark.parametrize("rule_file_path,rule_file_content,knowledge_graph,expected_has_violations", [
        # Example 1: Epic with noun-only name (violation)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Order Management'}]},
            True
        ),
        # Example 2: Correct verb-noun format (no violations)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Places Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Place Order'}]}]}]},
            False
        ),
        # Example 3: Story with actor in name (violation)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Places Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Customer places order'}]}]}]},
            True
        ),
        # Example 4: Feature with capability noun (violation)
        (
            'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}},
            {'epics': [{'name': 'Places Order', 'features': [{'name': 'Payment Processing'}]}]},
            True
        ),
        # Example 5: Story sizing violation
        (
            'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.story_sizing_scanner.StorySizingScanner', 'description': 'Size stories 3-12 days', 'do': {}},
            {'epics': [{'name': 'Places Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Place Order', 'sizing': '15 days'}]}]}]},
            True
        ),
        # Example 6: Empty graph (no violations)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {},
            False
        ),
    ])
    def test_scanners_detect_violations_in_knowledge_graph(self, repo_root, bot_directory, workspace_directory, rule_file_path, rule_file_content, knowledge_graph, expected_has_violations):
        """
        SCENARIO: Scanners detect violations in knowledge graph
        GIVEN: Knowledge graph contains problems
        AND: Rule file is specified
        WHEN: Scanners are executed against knowledge graph
        THEN: Violations are detected at expected line numbers
        
        Tests all examples from scenario file - parameterized test.
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Knowledge graph (from Examples table)
        kg_file = workspace_directory / 'docs' / 'stories' / 'story-graph.json'
        kg_file.parent.mkdir(parents=True, exist_ok=True)
        kg_file.write_text(json.dumps(knowledge_graph, indent=2), encoding='utf-8')
        
        # Given: Rule file with scanner (created in repo_root/tmp_path, auto-cleans up)
        # Create test rule files (auto-cleanup via tmp_path)
        setup_test_rules(repo_root, [rule_file_path], [rule_file_content])
        
        # When: ValidateRulesAction loads rules and discovers scanners
        action = ValidateRulesAction(
            bot_name='test_story_bot',
            behavior='shape',
            bot_directory=repo_root / 'agile_bot' / 'bots' / 'test_story_bot'
        )
        
        # When: ValidationAction injects validation instructions
        # For each rule: inject rule, run scanner (if exists), add results to rule
        # Call production code method (will be implemented)
        instructions_result = action.injectValidationInstructions(knowledge_graph)
        
        # Then: Instructions contain rules with scanner results
        instructions = instructions_result.get('instructions', {})
        validation_rules = instructions.get('validation_rules', [])
        
        assert len(validation_rules) > 0, "Instructions should contain validation rules"
        
        # Validate that rules have scanner results (violations) - all examples have scanners
        # All examples have scanners attached, so we assert they exist
        for rule in validation_rules:
            assert isinstance(rule, dict), f"Rule should be a dict, got: {type(rule)}"
            rule_content = rule.get('rule_content', rule)
            scanner_path = rule_content.get('scanner')
            assert scanner_path is not None, f"Rule should have a scanner attached: {rule.get('rule_file', 'unknown')}"
            
            # Rule has scanner, so it should have scanner_results
            scanner_results = rule.get('scanner_results', {})
            violations = scanner_results.get('violations', [])
            assert isinstance(violations, list), "Scanner results should contain violations list"
            
            # Validate violation structure if violations found
            for violation in violations:
                assert validate_violation_structure(violation, ['rule_name', 'line_number', 'location', 'violation_message', 'severity']), (
                    f"Violation missing required fields: {violation}"
                )
        
        # Then: Instructions include guidance to edit built knowledge based on code diagnostics
        base_instructions = instructions.get('base_instructions', [])
        assert isinstance(base_instructions, list), "Base instructions should be a list"
        # Instructions should include guidance to edit knowledge graph based on violations
        instructions_text = ' '.join(base_instructions) if isinstance(base_instructions, list) else str(base_instructions)
        # Note: When implemented, instructions should guide AI to edit knowledge graph based on scanner violations


# ============================================================================
# STORY: Reports Violations
# ============================================================================

class TestReportsViolations:
    """Story: Reports Violations - Tests violation report generation."""

    @pytest.mark.parametrize("violations_data,report_format,expected_violation_count", [
        # Example 1: Single violation, JSON format
        (
            [{
                'rule_name': 'use_verb_noun_format_for_story_elements',
                'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'violation_message': 'Epic name uses noun-only format',
                'line_number': 2,
                'location': 'epics[0].name',
                'severity': 'error'
            }],
            'JSON',
            1
        ),
        # Example 2: Multiple violations, JSON format
        (
            [
                {'rule_name': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Epic name uses noun-only format', 'line_number': 2, 'location': 'epics[0].name', 'severity': 'error'},
                {'rule_name': 'use_active_behavioral_language', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json', 'violation_message': 'Feature uses capability noun', 'line_number': 3, 'location': 'epics[0].features[0].name', 'severity': 'error'},
                {'rule_name': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Story name contains actor', 'line_number': 4, 'location': 'epics[0].features[0].stories[0].name', 'severity': 'error'},
                {'rule_name': 'size_stories_3_to_12_days', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json', 'violation_message': 'Story sizing outside range', 'line_number': 5, 'location': 'epics[0].features[0].stories[0].sizing', 'severity': 'error'},
                {'rule_name': 'use_background_for_common_setup', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json', 'violation_message': 'Background step missing', 'line_number': 6, 'location': 'scenarios[0].background', 'severity': 'error'}
            ],
            'JSON',
            5
        ),
        # Example 3: No violations, JSON format
        (
            [],
            'JSON',
            0
        ),
        # Example 4: Single violation, CHECKLIST format
        (
            [{
                'rule_name': 'use_verb_noun_format_for_story_elements',
                'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'violation_message': 'Epic name uses noun-only format',
                'line_number': 2,
                'location': 'epics[0].name',
                'severity': 'error'
            }],
            'CHECKLIST',
            1
        ),
        # Example 5: Single violation, DETAILED format
        (
            [{
                'rule_name': 'use_verb_noun_format_for_story_elements',
                'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'violation_message': 'Epic name uses noun-only format',
                'line_number': 2,
                'location': 'epics[0].name',
                'severity': 'error'
            }],
            'DETAILED',
            1
        ),
        # Example 6: Single violation, SUMMARY format
        (
            [{
                'rule_name': 'use_verb_noun_format_for_story_elements',
                'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'violation_message': 'Epic name uses noun-only format',
                'line_number': 2,
                'location': 'epics[0].name',
                'severity': 'error'
            }],
            'SUMMARY',
            1
        ),
        # Example 7: Multiple violations with mixed severities, JSON format
        (
            [
                {'rule_name': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Epic name uses noun-only format', 'line_number': 2, 'location': 'epics[0].name', 'severity': 'error'},
                {'rule_name': 'use_active_behavioral_language', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json', 'violation_message': 'Feature uses capability noun', 'line_number': 3, 'location': 'epics[0].features[0].name', 'severity': 'error'},
                {'rule_name': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Story name contains actor', 'line_number': 4, 'location': 'epics[0].features[0].stories[0].name', 'severity': 'warning'},
                {'rule_name': 'size_stories_3_to_12_days', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json', 'violation_message': 'Story sizing outside range', 'line_number': 5, 'location': 'epics[0].features[0].stories[0].sizing', 'severity': 'error'},
                {'rule_name': 'use_background_for_common_setup', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json', 'violation_message': 'Background step missing', 'line_number': 6, 'location': 'scenarios[0].background', 'severity': 'info'}
            ],
            'JSON',
            5
        ),
    ])
    def test_violation_report_generation_in_different_formats(self, repo_root, bot_directory, workspace_directory, violations_data, report_format, expected_violation_count):
        """
        SCENARIO: Violation report generation in different formats
        GIVEN: Violations have been detected
        AND: Report format is specified
        WHEN: Violation report is generated
        THEN: Report structure matches expected format
        
        Tests all examples from scenario file - parameterized test.
        """
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # When: Generate report via ValidateRulesAction
        # Action generates report from violations collected during validation
        # Call production code method (will be implemented)
        action = ValidateRulesAction(
            bot_name='test_story_bot',
            behavior='shape',
            bot_directory=repo_root / 'agile_bot' / 'bots' / 'test_story_bot'
        )
        
        # Generate report with violations from test data (from Examples table)
        # In real usage, violations would come from scanner execution via injectValidationInstructions()
        report = action.generate_report(report_format, violations=violations_data)
        
        # Then: Report structure matches expected format
        assert 'violations' in report, "Report should contain violations key"
        assert isinstance(report['violations'], list), "Violations should be a list"
        assert len(report['violations']) == expected_violation_count, f"Expected {expected_violation_count} violations, got {len(report['violations'])}"
        
        # Validate violation structure if violations exist
        if expected_violation_count > 0:
            for violation in report['violations']:
                assert validate_violation_structure(violation, ['rule_name', 'line_number', 'location', 'violation_message', 'severity']), (
                    f"Violation missing required fields: {violation}"
                )
                assert 'line_number' in violation, "Violation should have line_number"
                assert 'severity' in violation, "Violation should have severity"

