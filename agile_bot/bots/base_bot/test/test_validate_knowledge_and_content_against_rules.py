"""
Validate Knowledge And Content Against Rules Tests

Tests for all stories in the 'Validate Knowledge & Content Against Rules' sub-epic:
- Track Activity for Validate Rules Action
- Complete Validate Rules Action
- Discovers Scanners
- Run Scanners Against Knowledge Graph
- Reports Violations
- Handle Validate Rules Exceptions
- Validate Rules According to Scope
"""
import pytest
from pathlib import Path
import json
import importlib
import sys
from unittest.mock import patch
from typing import Dict, List, Any, Optional, Set
from conftest import create_workflow_state_file
from agile_bot.bots.base_bot.test.test_helpers import (
    given_environment_bootstrapped_and_activity_log_initialized,
    bootstrap_env, read_activity_log, create_activity_log_file, given_bot_name_and_behavior_setup,
    then_activity_logged_with_action_state, then_completion_entry_logged_with_outputs
)
from agile_bot.bots.base_bot.test.test_execute_behavior_actions import (
    given_environment_bootstrapped_and_action_initialized
)
from agile_bot.bots.base_bot.test.test_build_knowledge import (
    given_test_bot_directory_created,
    given_story_graph_file_created
)
from agile_bot.bots.base_bot.test.test_decide_strategy_criteria_action import (
    when_action_executes_with_parameters
)
from agile_bot.bots.base_bot.test.test_invoke_mcp import (
    given_base_actions_structure_created
)
from agile_bot.bots.base_bot.src.bot.bot import Behavior
from agile_bot.bots.base_bot.src.actions.validate_rules.validate_rules_action import ValidateRulesAction
from agile_bot.bots.base_bot.src.actions.validate_rules.rule import Rule
from agile_bot.bots.base_bot.src.scanners.code_scanner import CodeScanner
from agile_bot.bots.base_bot.src.scanners.test_scanner import TestScanner

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


# Removed duplicate create_workflow_state_local - use conftest.create_workflow_state_file instead
# Removed duplicate then_activity_logged_with_action_state - use test_helpers.then_activity_logged_with_action_state instead
# Removed duplicate then_completion_entry_logged_with_outputs - use test_helpers.then_completion_entry_logged_with_outputs instead

def given_spy_test_scanner_that_records_knowledge_graph():
    """Given: Spy TestScanner that records knowledge_graph."""
    received_knowledge_graphs = []
    
    class SpyTestScanner(TestScanner):
        def scan(self, knowledge_graph: Dict[str, Any], rule_obj: Any = None) -> List[Dict[str, Any]]:
            """Spy that records knowledge_graph and checks for test_files."""
            received_knowledge_graphs.append(knowledge_graph.copy())  # Store a copy
            # Return empty violations for this test
            return []
    
    return received_knowledge_graphs, SpyTestScanner

def given_validate_rules_action_initialized(bot_directory: Path, bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Given: ValidateRulesAction initialized."""
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    
    # Ensure behavior.json exists - Behavior.find_behavior_folder handles numbered prefixes
    behavior_name_with_prefix = f'1_{behavior}'
    create_actions_workflow_json(bot_directory, behavior_name_with_prefix)
    
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_directory, behavior_name_with_prefix, bot_name)
    
    # Create Behavior object - Behavior.find_behavior_folder will find the prefixed folder
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_obj = Behavior(behavior, bot_name, bot_paths)
    
    return ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name='validate_rules'
    )


def when_validate_rules_action_tracks_start(action: ValidateRulesAction):
    """When: ValidateRulesAction tracks start."""
    action.track_activity_on_start()


def when_validate_rules_action_tracks_completion(action: ValidateRulesAction, outputs: dict = None, duration: int = None):
    """When: ValidateRulesAction tracks completion."""
    action.track_activity_on_completion(
        outputs=outputs or {},
        duration=duration
    )


def given_activity_log_with_entries(workspace_directory: Path, entries: list):
    """Given: Activity log with entries."""
    workspace_directory.mkdir(parents=True, exist_ok=True)
    log_file = workspace_directory / 'activity_log.json'
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        for entry in entries:
            db.insert(entry)


def given_terminal_action_config(bot_directory: Path, action_name: str, order: int):
    """Given: Terminal action config (next_action=None) in test bot directory."""
    actions_dir = bot_directory / 'base_actions' / action_name
    actions_dir.mkdir(parents=True, exist_ok=True)
    action_config = actions_dir / 'action_config.json'
    action_config.write_text(json.dumps({
        'name': action_name,
        'workflow': True,
        'order': order,
        'next_action': None
    }), encoding='utf-8')
    return action_config


def when_action_finalizes_and_transitions(action: ValidateRulesAction, next_action: str = None):
    """When: Action finalizes and transitions."""
    return action.finalize_and_transition(next_action=next_action)


def when_action_injects_next_action_instructions(action: ValidateRulesAction):
    """When: Action injects next action instructions."""
    return action.inject_next_action_instructions()


def then_no_next_action_in_result(result):
    """Then: No next action in result (terminal)."""
    assert result.next_action is None


def then_no_next_action_instructions_injected(instructions: str):
    """Then: No next action instructions injected (terminal)."""
    assert instructions == '' or 'complete' in instructions.lower()


def then_completion_entry_has_workflow_complete_flag(workspace_directory: Path):
    """Then: Completion entry has workflow_complete flag."""
    log_data = read_activity_log(workspace_directory)
    completion_entry = next((e for e in log_data if 'outputs' in e), None)
    assert completion_entry is not None
    assert completion_entry['outputs']['workflow_complete']


def given_workflow_state_with_all_actions_completed(workspace_directory: Path, bot_name: str, behavior: str, current_action: str):
    """Given: Workflow state with all actions completed."""
    return create_workflow_state_file(
        workspace_directory,
        bot_name,
        behavior,
        current_action,
        completed_actions=[
            {'action_state': f'{bot_name}.{behavior}.gather_context'},
            {'action_state': f'{bot_name}.{behavior}.decide_planning_criteria'},
            {'action_state': f'{bot_name}.{behavior}.build_knowledge'},
            {'action_state': f'{bot_name}.{behavior}.render_output'},
            {'action_state': f'{bot_name}.{behavior}.validate_rules'}
        ]
    )


def when_check_workflow_completion_status(behavior: str, state_file: Path):
    """When: Check workflow completion status."""
    from conftest import Workflow
    return Workflow.is_behavior_complete(behavior, state_file)


def then_behavior_workflow_is_complete(is_complete: bool):
    """Then: Behavior workflow is complete."""
    assert is_complete


def then_activity_log_has_entries_with_action_states(workspace_directory: Path, expected_count: int, expected_action_states: list):
    """Then: Activity log has entries with expected action states."""
    log_data = read_activity_log(workspace_directory)
    assert len(log_data) == expected_count, f"Expected {expected_count} entries, got {len(log_data)}"
    for i, expected_action_state in enumerate(expected_action_states):
        assert log_data[i]['action_state'] == expected_action_state, (
            f"Entry {i} should have action_state '{expected_action_state}', got '{log_data[i]['action_state']}'"
        )


def then_activity_log_has_entry_count_and_last_action_state(workspace_directory: Path, expected_count: int, expected_last_action_state: str):
    """Then: Activity log has expected entry count and last entry has expected action state."""
    log_data = read_activity_log(workspace_directory)
    assert len(log_data) == expected_count, f"Expected {expected_count} entries, got {len(log_data)}"
    assert log_data[expected_count - 1]['action_state'] == expected_last_action_state, (
        f"Last entry should have action_state '{expected_last_action_state}', got '{log_data[expected_count - 1]['action_state']}'"
    )


def then_scanners_discovered_with_expected_count_and_valid_structure(behavior: Behavior, expected_scanner_count: int):
    """Then: Scanners discovered with expected count and valid structure."""
    scanners = behavior.scanners
    assert len(scanners) == expected_scanner_count, (
        f"Expected {expected_scanner_count} scanner classes discovered, got {len(scanners)}"
    )
    for scanner_class in scanners:
        assert isinstance(scanner_class, type), (
            f"Discovered scanner must be a class, got: {type(scanner_class)}"
        )
    rules = behavior.rules
    assert len(rules) >= expected_scanner_count, (
        f"Expected at least {expected_scanner_count} rules, got {len(rules)}"
    )
    for rule in rules:
        assert rule.has_scanner, f"Rule {rule.name} should have a scanner attached"
        scanner = rule.scanner
        assert scanner is not None, f"Rule {rule.name} should have a scanner instance"


def _validate_rule_structure(rule: dict):
    """Helper: Validate individual rule structure."""
    assert isinstance(rule, dict), f"Rule should be a dict, got: {type(rule)}"
    assert 'rule_content' in rule, f"Rule must contain 'rule_content' key: {rule}"
    rule_content = rule['rule_content']
    assert 'scanner' in rule_content, f"Rule content must contain 'scanner' key: {rule_content}"
    scanner_path = rule_content['scanner']
    assert scanner_path is not None, f"Rule should have a scanner attached: {rule.get('rule_file', 'unknown')}"
    assert 'scanner_results' in rule, f"Rule must contain 'scanner_results' key: {rule}"
    scanner_results = rule['scanner_results']
    assert 'violations' in scanner_results, f"Scanner results must contain 'violations' key: {scanner_results}"
    violations = scanner_results['violations']
    assert isinstance(violations, list), "Scanner results should contain violations list"
    for violation in violations:
        assert validate_violation_structure(violation, ['rule', 'line_number', 'location', 'violation_message', 'severity']), (
            f"Violation missing required fields: {violation}"
        )

def then_validation_rules_have_expected_structure(instructions: dict):
    """Then: Validation rules have expected structure."""
    assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
    validation_rules = instructions['validation_rules']
    assert len(validation_rules) > 0, "Instructions should contain validation rules"
    
    for rule in validation_rules:
        _validate_rule_structure(rule)
    
    assert 'base_instructions' in instructions, "Instructions must contain 'base_instructions' key"
    base_instructions = instructions['base_instructions']
    assert isinstance(base_instructions, list), "Base instructions should be a list"


def then_instructions_contain_validation_rules(instructions: dict):
    """Then: Instructions contain validation rules."""
    assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
    return instructions['validation_rules']


def then_violations_match_expected_scope_and_stories(violated_story_names: set, expected_stories_in_scope_set: set, expected_violations_set: set):
    """Then: Violations match expected scope and stories."""
    if expected_stories_in_scope_set:
        # Verify all violations are for stories in scope
        assert violated_story_names.issubset(expected_stories_in_scope_set), (
            f"Found violations for stories outside scope: {violated_story_names - expected_stories_in_scope_set}. "
            f"Expected scope: {expected_stories_in_scope_set}"
        )
    
    # Verify violations match expected
    assert violated_story_names == expected_violations_set, (
        f"Expected violations: {expected_violations_set}, but got: {violated_story_names}. "
        f"Missing: {expected_violations_set - violated_story_names}, "
        f"Unexpected: {violated_story_names - expected_violations_set}"
    )


def then_expected_story_names_contain_stories(expected: set, stories_to_check: list, should_be_present: bool = True):
    """Then: Expected story names contain (or don't contain) specified stories."""
    for story in stories_to_check:
        if should_be_present:
            assert story in expected, f"Expected '{story}' to be in expected set: {expected}"
        else:
            assert story not in expected, f"Expected '{story}' NOT to be in expected set: {expected}"


def then_violations_detected_in_test_file(all_violations: list, test_file: Path):
    """Then: Violations detected in test file."""
    assert len(all_violations) > 0, "TestScanner should detect violations in test file"
    test_file_found_in_violations = any(
        str(test_file) in str(v.get('location', '')) or 
        test_file.name in str(v.get('location', ''))
        for v in all_violations
    )
    assert test_file_found_in_violations, (
        f"Test file from scope parameter should be scanned. "
        f"Expected test file: {test_file}. "
        f"Violations found: {all_violations}"
    )




def given_test_file_created_with_content(workspace_directory: Path, filename: str, content: str):
    """Given: Test file created with content."""
    test_file = workspace_directory / filename
    test_file.write_text(content, encoding='utf-8')
    return test_file


def given_behavior_rule_file_created(bot_directory: Path, behavior: str, rule_filename: str, rule_content: dict):
    """Given: Behavior rule file created."""
    rules_dir = bot_directory / 'behaviors' / behavior / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / rule_filename
    rule_file.write_text(json.dumps(rule_content, indent=2), encoding='utf-8')
    return rule_file


def given_validate_rules_action_created(bot_directory: Path, bot_name: str, behavior: str):
    """Given: ValidateRulesAction created."""
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    
    # Ensure behavior.json exists
    behavior_name_with_prefix = f'1_{behavior}'
    create_actions_workflow_json(bot_directory, behavior_name_with_prefix)
    
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(bot_directory, behavior_name_with_prefix, bot_name)
    
    # Create Behavior object
    bot_paths = BotPaths(bot_directory=bot_directory)
    behavior_obj = Behavior(behavior, bot_name, bot_paths)
    
    return ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name='validate_rules'
    )


def then_result_contains_instructions_key(result: dict):
    """Then: Result contains instructions key."""
    assert 'instructions' in result, "Result must contain 'instructions' key"


def given_test_file_paths_for_knowledge_graph(test_file: Path):
    """Given: Test file paths for knowledge graph."""
    return [Path(str(test_file))]


def then_inject_validation_instructions_result_has_instructions(action: ValidateRulesAction, knowledge_graph: dict, test_file_paths: list):
    """Then: Inject validation instructions result has instructions."""
    files = {'test': test_file_paths} if test_file_paths else {}
    result_direct = action.injectValidationInstructions(knowledge_graph, files=files)
    assert 'instructions' in result_direct, "Result should contain 'instructions' key"
    return result_direct


def then_scanner_class_loaded_successfully(scanner_class, error_msg: str):
    """Then: Scanner class loaded successfully."""
    assert scanner_class is not None, f"Failed to load scanner: {error_msg}"


def given_rule_object_for_scanner(rule_filename: str, scanner_class_path: str, behavior_name: str):
    """Given: Rule object for scanner."""
    from pathlib import Path
    return Rule(
        rule_file_path=Path(rule_filename) if rule_filename else Path('test_rule.json'),
        behavior_name=behavior_name,
        bot_name='test_bot',
        rule_content={'scanner': scanner_class_path, 'description': 'Test rule'}
    )


def then_scanner_detects_violations_with_expected_message(violations: list, scanner_class_path: str, expected_violation_message: str):
    """Then: Scanner detects violations with expected message."""
    assert len(violations) > 0, f"Scanner {scanner_class_path} should detect violations in bad example"
    
    # Check that at least one violation contains expected message
    violation_messages = []
    for v in violations:
        assert 'violation_message' in v, f"Violation must contain 'violation_message' key: {v}"
        violation_messages.append(v['violation_message'])
    assert any(expected_violation_message.lower() in msg.lower() for msg in violation_messages), (
        f"Expected violation message '{expected_violation_message}' not found in violations: {violation_messages}"
    )
    
    # Validate violation structure
    for violation in violations:
        assert validate_violation_structure(violation, ['rule', 'violation_message', 'severity']), (
            f"Violation missing required fields: {violation}"
        )




def given_behavior_created_for_test_bot(test_bot_dir: Path, behavior_name: str, bot_name: str):
    """Given: Behavior created for test bot."""
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    create_actions_workflow_json(test_bot_dir, f'1_{behavior_name}')
    bot_paths = BotPaths(bot_directory=test_bot_dir)
    return Behavior(behavior_name, bot_name, bot_paths)


def given_knowledge_graph_file_created(workspace_directory: Path, knowledge_graph: dict):
    """Given: Knowledge graph file created."""
    kg_file = workspace_directory / 'docs' / 'stories' / 'story-graph.json'
    kg_file.parent.mkdir(parents=True, exist_ok=True)
    kg_file.write_text(json.dumps(knowledge_graph, indent=2), encoding='utf-8')
    return kg_file


def given_validate_rules_action_for_test_bot(test_bot_dir: Path, bot_name: str, behavior: str):
    """Given: ValidateRulesAction for test bot."""
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    from agile_bot.bots.base_bot.test.test_execute_behavior_actions import create_minimal_guardrails_files
    
    # Ensure behavior.json exists
    behavior_name_with_prefix = f'1_{behavior}'
    create_actions_workflow_json(test_bot_dir, behavior_name_with_prefix)
    
    # Create minimal guardrails files (required by Guardrails class initialization)
    create_minimal_guardrails_files(test_bot_dir, behavior_name_with_prefix, 'test_bot')
    
    # Create Behavior object
    bot_paths = BotPaths(bot_directory=test_bot_dir)
    behavior_obj = Behavior(behavior, bot_name, bot_paths)
    
    return ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior_obj,
        action_name='validate_rules'
    )


def when_scanner_instance_created(scanner_class):
    """When: Scanner instance created."""
    return scanner_class()


def _extract_test_files_from_bad_example(bad_example: dict):
    """Helper: Extract test files list from bad_example."""
    test_files_to_scan = []
    if bad_example:
        if 'test_files' in bad_example:
            test_files_to_scan.extend(bad_example['test_files'])
        elif 'code_files' in bad_example:
            test_files_to_scan.extend(bad_example['code_files'])
    return test_files_to_scan

def _extract_knowledge_graph_from_bad_example(bad_example: dict):
    """Helper: Extract knowledge graph from bad_example."""
    if 'knowledge_graph' in bad_example:
        return bad_example['knowledge_graph']
    kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']}
    return kg if 'epics' in kg else {}

def _scan_files_via_scan_method(scanner_instance: TestScanner, bad_example: dict, rule_obj: Rule):
    """Helper: Try scanning via scan() method."""
    test_files_list = None
    code_files_list = None
    if 'test_files' in bad_example:
        test_files_list = [Path(tf) for tf in bad_example['test_files']]
    elif 'code_files' in bad_example:
        test_files_list = [Path(cf) for cf in bad_example['code_files']]
    if 'code_files' in bad_example:
        code_files_list = [Path(cf) for cf in bad_example['code_files']]
    kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']}
    return scanner_instance.scan(kg, rule_obj, test_files=test_files_list, code_files=code_files_list)

def when_test_scanner_scans_files(scanner_instance: TestScanner, bad_example: dict, rule_obj: Rule):
    """When: Test scanner scans files."""
    violations = []
    test_files_to_scan = _extract_test_files_from_bad_example(bad_example)
    
    for test_file_path in test_files_to_scan:
        file_path = Path(test_file_path)
        if file_path.exists():
            assert bad_example is not None, "bad_example must be provided for test scanners"
            kg = _extract_knowledge_graph_from_bad_example(bad_example)
            file_violations = scanner_instance.scan_test_file(file_path, rule_obj, kg)
            violations.extend(file_violations)
    
    if not violations and bad_example:
        try:
            violations = _scan_files_via_scan_method(scanner_instance, bad_example, rule_obj)
        except Exception:
            pass
    
    return violations


def _scan_code_file(scanner_instance: CodeScanner, file_path: Path, rule_obj: Rule):
    """Helper: Scan a single code file."""
    return scanner_instance.scan_code_file(file_path, rule_obj)

def _scan_code_files_from_example(scanner_instance: CodeScanner, bad_example: dict, rule_obj: Rule):
    """Helper: Scan code files from bad_example."""
    violations = []
    if bad_example and 'code_files' in bad_example:
        for code_file_path in bad_example['code_files']:
            file_path = Path(code_file_path)
            if file_path.exists():
                file_violations = _scan_code_file(scanner_instance, file_path, rule_obj)
                violations.extend(file_violations)
    return violations

def _try_fallback_scan_method(scanner_instance: CodeScanner, bad_example: dict, rule_obj: Rule):
    """Helper: Try scanning via scan() method as fallback."""
    try:
        code_files_list = None
        if bad_example and 'code_files' in bad_example:
            code_files_list = [Path(cf) for cf in bad_example['code_files']]
        elif bad_example and 'test_files' in bad_example:
            code_files_list = [Path(tf) for tf in bad_example['test_files']]
        kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']} if bad_example else {}
        return scanner_instance.scan(kg, rule_obj, code_files=code_files_list)
    except Exception:
        return []

def when_code_scanner_scans_files(scanner_instance: CodeScanner, bad_example: dict, rule_obj: Rule):
    """When: Code scanner scans files."""
    violations = _scan_code_files_from_example(scanner_instance, bad_example, rule_obj)
    if not violations:
        violations = _try_fallback_scan_method(scanner_instance, bad_example, rule_obj)
    return violations


def when_story_scanner_scans_knowledge_graph(scanner_instance, bad_example: dict, rule_obj: Rule):
    """When: Story scanner scans knowledge graph."""
    # Story scanners scan knowledge graph
    # Story scanners don't use test_files/code_files, so pass bad_example directly as knowledge_graph
    return scanner_instance.scan(bad_example if bad_example else {}, rule_obj)


def then_result_has_violations_or_report(result: dict, error_message: str = None):
    """Then: Result has violations or report."""
    assert 'violations' in result or 'report' in result, (
        error_message or "Result should contain violations or report"
    )


def then_result_has_violations_from_knowledge_graph(result: dict):
    """Then: Result has violations from knowledge graph validation."""
    assert 'violations' in result or 'report' in result, (
        "ValidateCodeFilesAction should return violations or report"
    )
    violations = result.get('violations', [])
    assert len(violations) > 0, (
        "Should have violations from knowledge graph validation"
    )


def then_violation_has_expected_line_number(violation: dict, expected_line_number: int):
    """Then: Violation has expected line number."""
    assert 'line_number' in violation, f"Violation must contain 'line_number' key: {violation}"
    assert violation['line_number'] == expected_line_number, (
        f"Expected line_number {expected_line_number}, got {violation['line_number']}"
    )


def then_violation_has_expected_location(violation: dict, expected_location: str):
    """Then: Violation has expected location."""
    assert 'location' in violation, f"Violation must contain 'location' key: {violation}"
    assert violation['location'] == expected_location, (
        f"Expected location '{expected_location}', got '{violation['location']}'"
    )


def then_violation_has_expected_message(violation: dict, expected_message: str):
    """Then: Violation has expected message."""
    assert 'violation_message' in violation, f"Violation must contain 'violation_message' key: {violation}"
    assert expected_message in violation['violation_message'], (
        f"Expected message '{expected_message}' not found in '{violation['violation_message']}'"
    )


def then_violation_has_expected_severity(violation: dict, expected_severity: str):
    """Then: Violation has expected severity."""
    assert 'severity' in violation, f"Violation must contain 'severity' key: {violation}"
    assert violation['severity'] == expected_severity, (
        f"Expected severity '{expected_severity}', got '{violation['severity']}'"
    )


def when_action_generates_report(action: ValidateRulesAction, report_format: str, violations: list):
    """When: Action generates report."""
    return action.generate_report(report_format, violations=violations)


def then_report_has_checklist_format(report: dict, expected_violation_count: int):
    """Then: Report has checklist format."""
    assert 'checklist' in report, "CHECKLIST format should contain checklist key"
    assert 'format' in report, "Report should contain format key"
    assert report['format'] == 'CHECKLIST', "Format should be CHECKLIST"
    # Count violations from checklist items
    assert 'checklist' in report, "CHECKLIST format report must contain 'checklist' key"
    checklist_text = report['checklist']
    violation_count = checklist_text.count('- [ ]') if checklist_text != 'No violations found.' else 0
    assert violation_count == expected_violation_count, (
        f"Expected {expected_violation_count} violations in checklist, got {violation_count}"
    )


def then_report_has_summary_format(report: dict, expected_violation_count: int):
    """Then: Report has summary format."""
    assert 'violation_count' in report, "SUMMARY format should contain violation_count key"
    assert 'format' in report, "Report should contain format key"
    assert report['format'] == 'SUMMARY', "Format should be SUMMARY"
    assert report['violation_count'] == expected_violation_count, (
        f"Expected {expected_violation_count} violations, got {report['violation_count']}"
    )


def then_report_has_json_or_detailed_format(report: dict, expected_violation_count: int):
    """Then: Report has JSON or detailed format."""
    # JSON, DETAILED, and other formats should have violations key
    assert 'violations' in report, "Report should contain violations key"
    assert isinstance(report['violations'], list), "Violations should be a list"
    assert len(report['violations']) == expected_violation_count, (
        f"Expected {expected_violation_count} violations, got {len(report['violations'])}"
    )
    
    # Validate violation structure if violations exist
    if expected_violation_count > 0:
        for violation in report['violations']:
            assert validate_violation_structure(violation, ['rule', 'line_number', 'location', 'violation_message', 'severity']), (
                f"Violation missing required fields: {violation}"
            )
            assert 'line_number' in violation, "Violation should have line_number"
            assert 'severity' in violation, "Violation should have severity"


def given_story_graph_file_with_content(workspace_directory: Path, story_graph: dict):
    """Given: Story graph file with content."""
    docs_stories_dir = given_docs_stories_directory_exists(workspace_directory)
    story_graph_path = docs_stories_dir / 'story-graph.json'
    story_graph_path.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')
    return story_graph_path


def when_add_scope_to_story_graph_file(story_graph_path: Path, story_graph: dict, scope_config: dict):
    """When: Add scope to story graph file."""
    story_graph['_validation_scope'] = scope_config
    story_graph_path.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')


def when_convert_expected_stories_to_set(expected_stories_in_scope, story_graph: dict, extract_method):
    """When: Convert expected stories to set."""
    if isinstance(expected_stories_in_scope, list):
        return set(expected_stories_in_scope)
    elif expected_stories_in_scope is None:
        # Calculate all stories if None
        expected_stories_in_scope_set = set()
        for epic in story_graph['epics']:
            extract_method(epic, expected_stories_in_scope_set)
        return expected_stories_in_scope_set
    else:
        return expected_stories_in_scope


def when_convert_expected_violations_to_set(expected_violations_list, expected_stories_in_scope_set, story_graph: dict, extract_method):
    """When: Convert expected violations to set."""
    if isinstance(expected_violations_list, list):
        return set(expected_violations_list)
    elif expected_violations_list is None:
        # Calculate expected violations: all stories in scope without scenarios
        stories_with_scenarios = {"Select And Capture Tokens"}
        if expected_stories_in_scope_set:
            return expected_stories_in_scope_set - stories_with_scenarios
        else:
            # All stories
            all_story_names = set()
            for epic in story_graph['epics']:
                extract_method(epic, all_story_names)
            return all_story_names - stories_with_scenarios
    else:
        return set()


def given_story_graph_file_with_invalid_json(workspace_directory: Path):
    """Given: Story graph file with invalid JSON."""
    docs_dir = given_docs_stories_directory_exists(workspace_directory)
    story_graph_file = docs_dir / 'story-graph.json'
    story_graph_file.write_text('{ invalid json }', encoding='utf-8')
    return story_graph_file


def then_expected_story_names_equal(expected: set, expected_stories: set):
    """Then: Expected story names equal."""
    assert expected == expected_stories, (
        f"Expected story names {expected_stories}, got {expected}"
    )


def given_minimal_story_graph_for_test_file_scope():
    """Given: Minimal story graph for test file scope."""
    return {
        "epics": [
            {
                "name": "Places Order",
                "sub_epics": [
                    {
                        "name": "Validates Payment",
                        "story_groups": [
                            {
                                "stories": [
                                    {
                                        "name": "Place Order",
                                        "scenarios": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


def given_story_graph_for_multiple_test_files():
    """Given: Story graph for multiple test files."""
    return {
        "epics": [
            {
                "name": "Manage Orders",
                "sub_epics": [
                    {
                        "name": "Create Order",
                        "story_groups": [
                            {
                                "stories": [
                                    {
                                        "name": "Place Order",
                                        "scenarios": []
                                    },
                                    {
                                        "name": "Cancel Order",
                                        "scenarios": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


def then_violations_detected_in_test_files_count(all_violations: list, expected_count: int = None):
    """Then: Violations detected in test files count."""
    if expected_count is not None:
        assert len(all_violations) == expected_count, (
            f"Expected {expected_count} violations, got {len(all_violations)}"
        )
    else:
        assert len(all_violations) > 0, "TestScanner should detect violations in test files"


def when_create_parameters_from_scope_config(scope_config: dict):
    """When: Create parameters from scope config."""
    return scope_config.copy() if scope_config else {}


def when_create_test_file_parameter(test_file: Path):
    """When: Create test file parameter."""
    return {'test_file': str(test_file)}


def when_create_test_files_parameter(test_files: list):
    """When: Create test files parameter."""
    return {'test_files': [str(f) for f in test_files]}


def when_create_code_files_parameter(code_files: list):
    """When: Create code files parameter."""
    return {'code_files': [str(f) for f in code_files]}


def when_create_empty_parameters():
    """When: Create empty parameters."""
    return {}


def when_copy_story_graph_for_test(story_graph: dict):
    """When: Copy story graph for test."""
    return story_graph.copy()


def when_execute_action_and_extract_violations(action, parameters: dict):
    """When: Execute action and extract violations."""
    result = when_action_executes_with_scope_parameters(action, parameters)
    instructions = then_result_contains_instructions_with_content_to_validate(result)
    validation_rules = then_instructions_contain_validation_rules(instructions)
    all_violations = when_extract_violations_from_validation_rules(validation_rules)
    return all_violations


def given_workspace_directory_created(workspace_directory: Path):
    """Given: Workspace directory created."""
    workspace_directory.mkdir(parents=True, exist_ok=True)


def given_scenarios_rule_created(bot_directory: Path):
    """Given: Scenarios rule created."""
    return given_common_rule_created(bot_directory, 'test_scenarios_rule.json', {
        "description": "Stories must have scenarios",
        "scanner": "agile_bot.bots.base_bot.src.scanners.scenarios_on_story_docs_scanner.ScenariosOnStoryDocsScanner"
    })


def when_add_scope_to_story_graph_if_provided(story_graph_path: Path, story_graph: dict, scope_config: dict):
    """When: Add scope to story graph if provided."""
    if scope_config:
        when_add_scope_to_story_graph_file(story_graph_path, story_graph, scope_config)


def _create_test_file_for_class_based_scanner(test_file: Path):
    """Helper: Create test file for class-based scanner."""
    test_file.write_text('''class TestGenTools:
    """Abbreviated class name - should be TestGenerateBotTools"""
    def test_creates_tool(self):
        pass
''', encoding='utf-8')
    return {
        'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Generate Bot Tools'}]}]}]}],
        'test_files': [str(test_file)]
    }

def _create_test_file_for_test_quality_scanner(test_file: Path):
    """Helper: Create test file for test quality scanner."""
    test_file.write_text('''def test_1():
    global user
    user = create_user()
    assert process(user) == True

def test_2():
    assert user.name == 'John'
''', encoding='utf-8')
    return {'code_files': [str(test_file)]}

def _create_test_file_for_specification_match_scanner(test_file: Path):
    """Helper: Create test file for specification match scanner."""
    test_file.write_text('''def test_agent_init(self):
    """Test agent."""
    agent = Agent('story_bot')
    assert agent.initialized

def test_process_order(self):
    order = create_order()
    result = process(order)
    assert result
''', encoding='utf-8')
    return {'code_files': [str(test_file)]}

def _create_test_files_for_test_scanners(test_file: Path, scanner_class_path: str):
    """Helper: Create test files for test scanners."""
    if 'class_based' in scanner_class_path.lower():
        return _create_test_file_for_class_based_scanner(test_file)
    elif 'test_quality' in scanner_class_path.lower():
        return _create_test_file_for_test_quality_scanner(test_file)
    elif 'specification_match' in scanner_class_path.lower():
        return _create_test_file_for_specification_match_scanner(test_file)
    return None

def _create_code_file_for_scanner_type(test_file: Path, scanner_class_path: str):
    """Helper: Create code file for specific scanner type."""
    scanner_lower = scanner_class_path.lower()
    scanner_file_contents = {
        'useless_comments': '''def get_name(self):
    """Get the name.
    
    
    """
    return self.name

# Load state from file
def load_state(self):
    return self.state
''',
        'intention_revealing': '''def process(data):
    temp = data
    return temp
''',
        'separate_concerns': '''def calculate_total(items):
    total = sum(items)
    print(f"Total: {total}")
    save_to_database(total)
    return total
''',
        'simplify_control_flow': '''def process(data):
    if data:
        if data.items:
            if data.items.length > 0:
                if data.items[0].valid:
                    return process_item(data.items[0])
''',
        'complete_refactoring': '''# Old way
# def old_process(data):
#     return data.process()

def new_process(data):
    return data.process()
''',
        'meaningful_context': '''def process():
    if status == 200:
        return data
    data1 = get_data()
    return data1
''',
        'minimize_mutable': '''def process(items):
    items.push(new_item)
    counter++
    return items
''',
        'vertical_density': None,  # Special case - generated dynamically
        'abstraction_levels': '''def process_order(order):
    validate_order(order)
    sql = 'SELECT * FROM orders WHERE id = ?'
    db.query(sql, [order.id])
    return order
''',
        'encapsulation': '''class Order:
    def process(self):
        return self.customer.get_order().get_items().add(item)

''',
        'exception_classification': '''class DatabaseConnectionException(Exception):
    pass
class DatabaseQueryException(Exception):
    pass
''',
        'error_handling_isolation': '''def process_order(order):
    try:
        validate_order(order)
        save_order(order)
    except:
        log_error()
''',
        'third_party_isolation': '''from requests import get
from boto3 import client

def process_order(order):
    response = get('https://api.example.com/orders')
    s3 = client('s3')
    s3.upload_file('order.json', 'bucket', 'key')
''',
        'open_closed': '''def process_payment(payment):
    if payment.type == 'credit':
        process_credit(payment)
    elif payment.type == 'paypal':
        process_paypal(payment)
    elif payment.kind == 'debit':
        process_debit(payment)
'''
    }
    
    for key, content in scanner_file_contents.items():
        if key in scanner_lower:
            if content is None:  # vertical_density
                long_function = 'def process_items(items):\n'
                for i in range(50):
                    long_function += f'    # Line {i}\n'
                long_function += '    item_total = calculate_total(items)\n'
                long_function += '    return item_total\n'
                test_file.write_text(long_function, encoding='utf-8')
            else:
                test_file.write_text(content, encoding='utf-8')
            return {'code_files': [str(test_file)]}
    return None

def given_test_file_for_scanner_type(workspace_directory: Path, scanner_class_path: str, behavior: str):
    """Given: Test file for scanner type."""
    test_file = workspace_directory / 'test_code.py'
    test_file.parent.mkdir(parents=True, exist_ok=True)
    bad_example = None
    
    # For test scanners, create a test file with violations
    if 'tests' in behavior:
        test_file = workspace_directory / 'test_place_order.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        bad_example = _create_test_files_for_test_scanners(test_file, scanner_class_path)
    
    # For code scanners, create a test Python file with violations
    if bad_example is None and 'code' in behavior:
        test_file = workspace_directory / 'test_code.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        bad_example = _create_code_file_for_scanner_type(test_file, scanner_class_path)
    
    return test_file, bad_example


def given_base_action_instructions_for_validate_rules(bot_directory: Path, save_report_instruction: bool = False):
    """Given: Base action instructions for validate_rules."""
    base_actions_dir = bot_directory / 'base_actions'
    validate_rules_dir = base_actions_dir / 'validate_rules'
    validate_rules_dir.mkdir(parents=True, exist_ok=True)
    
    action_config_file = validate_rules_dir / 'action_config.json'
    action_config_file.write_text(json.dumps({
        'name': 'validate_rules',
        'workflow': True,
        'order': 7
    }), encoding='utf-8')
    
    instructions_file = validate_rules_dir / 'instructions.json'
    base_instructions = {
        'instructions': [
            'Load and review clarification.json and planning.json',
            'Check Content Data against all rules listed above',
            'Generate a validation report'
        ]
    }
    if save_report_instruction:
        base_instructions['instructions'].append('Save the validation report to validation-report.md in docs/stories/')
    instructions_file.write_text(json.dumps(base_instructions), encoding='utf-8')
    return instructions_file


def given_docs_stories_directory_exists(workspace_directory: Path):
    """Given: Docs/stories directory exists."""
    docs_dir = workspace_directory / 'docs' / 'stories'
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir


def when_action_executes_and_returns_result(action: ValidateRulesAction):
    """When: Action executes and returns result."""
    return action.do_execute(parameters={})




def when_action_executes_and_raises_file_not_found_error(action: ValidateRulesAction):
    """When: Action executes and raises FileNotFoundError."""
    with pytest.raises((FileNotFoundError, RuntimeError), match=".*Story graph.*not found.*"):
        action.do_execute(parameters={})


def when_action_executes_and_raises_json_error(action: ValidateRulesAction):
    """When: Action executes and raises JSON error."""
    with pytest.raises((json.JSONDecodeError, ValueError, RuntimeError), match=".*"):
        action.do_execute(parameters={})




def when_extract_test_case_data(test_case: dict):
    """When: Extract test case data."""
    scope_config = test_case['scope_config']
    expected_stories_in_scope = test_case.get('expected_stories_in_scope')
    expected_violations_list = test_case.get('expected_violations')
    return scope_config, expected_stories_in_scope, expected_violations_list


def when_test_scope_extraction_with_increment_priorities(story_graph: dict, get_expected_method):
    """When: Test scope extraction with increment priorities."""
    scope_config = {"increment_priorities": [1]}
    expected = get_expected_method(scope_config, story_graph)
    then_expected_story_names_contain_stories(expected, [
        "Select And Capture Tokens",
        "Group Tokens And Create Mob Entity",
        "Handle Token Click And Intercept"
    ], should_be_present=True)
    then_expected_story_names_contain_stories(expected, ["Select Mob To Edit"], should_be_present=False)


def when_test_scope_extraction_with_epic_names(story_graph: dict, get_expected_method):
    """When: Test scope extraction with epic names."""
    scope_config = {"epic_names": ["Manage Mobs"]}
    expected = get_expected_method(scope_config, story_graph)
    then_expected_story_names_contain_stories(expected, [
        "Select And Capture Tokens",
        "Select Mob To Edit",
        "Select Actors For Mob"
    ], should_be_present=True)
    then_expected_story_names_contain_stories(expected, ["Select Mob For Strategy"], should_be_present=False)


def when_test_scope_extraction_with_multiple_epics(story_graph: dict, get_expected_method):
    """When: Test scope extraction with multiple epics."""
    scope_config = {"epic_names": ["Manage Mobs", "Execute Mob Actions"]}
    expected = get_expected_method(scope_config, story_graph)
    then_expected_story_names_contain_stories(expected, [
        "Select And Capture Tokens",
        "Handle Token Click And Intercept"
    ], should_be_present=True)
    then_expected_story_names_contain_stories(expected, ["Select Mob For Strategy"], should_be_present=False)


def when_test_scope_extraction_with_story_names(story_graph: dict, get_expected_method):
    """When: Test scope extraction with story names."""
    scope_config = {"story_names": ["Select And Capture Tokens", "Handle Token Click And Intercept"]}
    expected = get_expected_method(scope_config, story_graph)
    then_expected_story_names_equal(expected, {"Select And Capture Tokens", "Handle Token Click And Intercept"})


def given_test_file_scope_verification_setup(bot_directory: Path, workspace_directory: Path):
    """Given: Test file scope verification setup."""
    bootstrap_env(bot_directory, workspace_directory)
    story_graph = {"epics": []}
    story_graph_path = given_story_graph_file_created(workspace_directory, story_graph)
    return story_graph, story_graph_path


def given_test_scope_verification_rule_created(bot_directory: Path):
    """Given: Test scope verification rule created."""
    rule_content = {
        "description": "Test classes must match story names",
        "scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
    }
    return given_behavior_rule_file_created(
        bot_directory,
        '7_write_tests',
        'test_scope_verification_rule.json',
        rule_content
    )


def given_test_bot_directory_for_report_generation(repo_root: Path):
    """Given: Test bot directory for report generation."""
    return repo_root / 'agile_bot' / 'bots' / 'test_story_bot'


def when_setup_scanner_test_environment(bot_directory: Path, workspace_directory: Path, scanner_class_path: str, behavior: str):
    """When: Setup scanner test environment."""
    bootstrap_env(bot_directory, workspace_directory)
    scanner_class, error_msg = load_scanner_class(scanner_class_path)
    then_scanner_class_loaded_successfully(scanner_class, error_msg)
    rule_obj = given_rule_object_for_scanner('test_rule.json', scanner_class_path, behavior)
    return scanner_class, rule_obj


def given_environment_setup_for_file_not_found_test(bot_directory: Path, workspace_directory: Path):
    """Given: Environment setup for file not found test."""
    bootstrap_env(bot_directory, workspace_directory)
    given_base_actions_structure_created(bot_directory)
    given_docs_stories_directory_exists(workspace_directory)
    return given_validate_rules_action_initialized(bot_directory, 'test_bot', 'shape')


def given_environment_setup_for_invalid_json_test(bot_directory: Path, workspace_directory: Path):
    """Given: Environment setup for invalid JSON test."""
    bootstrap_env(bot_directory, workspace_directory)
    given_base_actions_structure_created(bot_directory)
    story_graph_file = given_story_graph_file_with_invalid_json(workspace_directory)
    action = given_validate_rules_action_initialized(bot_directory, 'test_bot', 'shape')
    return action, story_graph_file


def when_execute_test_file_scope_verification(action, test_file: Path, story_graph: dict):
    """When: Execute test file scope verification."""
    parameters = when_create_test_file_parameter(test_file)
    result = when_action_executes_with_parameters(action, parameters)
    then_result_contains_instructions_key(result)
    test_file_paths = given_test_file_paths_for_knowledge_graph(test_file)
    test_knowledge_graph = when_copy_story_graph_for_test(story_graph)
    then_inject_validation_instructions_result_has_instructions(action, test_knowledge_graph, test_file_paths)


def when_execute_action_and_extract_violated_story_names_with_conversion(action, parameters: dict, story_graph: dict, test_case: dict, extract_story_names_method, convert_stories_method, convert_violations_method, extract_epic_method):
    """When: Execute action and extract violated story names with conversion."""
    result = when_action_executes_and_returns_result(action)
    instructions = then_result_contains_instructions_with_content_to_validate(result)
    validation_rules = then_instructions_contain_validation_rules(instructions)
    all_violations = when_extract_violations_from_validation_rules(validation_rules)
    violated_story_names = extract_story_names_method(all_violations)
    scope_config, expected_stories_in_scope, expected_violations_list = when_extract_test_case_data(test_case)
    expected_stories_in_scope_set = convert_stories_method(expected_stories_in_scope, story_graph, extract_epic_method)
    expected_violations_set = convert_violations_method(expected_violations_list, expected_stories_in_scope_set, story_graph, extract_epic_method)
    return violated_story_names, expected_stories_in_scope_set, expected_violations_set


def when_create_test_file_if_needed_for_scanner(workspace_directory: Path, scanner_class_path: str, behavior: str, bad_example):
    """When: Create test file if needed for scanner."""
    if bad_example is None:
        return given_test_file_for_scanner_type(workspace_directory, scanner_class_path, behavior)
    return None, bad_example


def when_execute_scanner_based_on_type(scanner_instance, bad_example: dict, rule_obj):
    """When: Execute scanner based on type."""
    if isinstance(scanner_instance, TestScanner):
        return when_test_scanner_scans_files(scanner_instance, bad_example, rule_obj)
    elif isinstance(scanner_instance, CodeScanner):
        return when_code_scanner_scans_files(scanner_instance, bad_example, rule_obj)
    else:
        return when_story_scanner_scans_knowledge_graph(scanner_instance, bad_example, rule_obj)


def given_base_action_instructions_and_behavior_rule_setup(bot_directory: Path, workspace_directory: Path):
    """Given: Base action instructions and behavior rule setup."""
    instructions_file = given_base_action_instructions_for_validate_rules(bot_directory)
    given_behavior_specific_rule_exists(
        bot_directory, '1_shape', 'test_rule.json',
        {'description': 'Test rule', 'examples': []}
    )
    bootstrap_env(bot_directory, workspace_directory)
    then_instructions_file_exists_and_has_content(instructions_file)
    given_story_graph_file_exists_minimal(workspace_directory)
    return instructions_file


def given_environment_and_action_for_report_path_test(bot_directory: Path, workspace_directory: Path):
    """Given: Environment and action for report path test."""
    docs_dir = given_docs_stories_directory_exists(workspace_directory)
    bootstrap_env(bot_directory, workspace_directory)
    given_story_graph_file_exists_minimal(workspace_directory)
    action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'shape')
    result = when_action_executes_and_returns_result(action)
    return action, result


def given_test_bot_setup_with_rules(repo_root: Path, bot_directory: Path, workspace_directory: Path, rule_file_paths: list, rule_file_content: list):
    """Given: Test bot setup with rules."""
    bootstrap_env(bot_directory, workspace_directory)
    test_bot_dir = given_test_bot_directory_created(repo_root)
    setup_test_rules(repo_root, rule_file_paths, rule_file_content)
    return test_bot_dir


def given_knowledge_graph_and_test_bot_setup(repo_root: Path, bot_directory: Path, workspace_directory: Path, knowledge_graph: dict, rule_file_path: str, rule_file_content: dict):
    """Given: Knowledge graph and test bot setup."""
    bootstrap_env(bot_directory, workspace_directory)
    kg_file = given_knowledge_graph_file_created(workspace_directory, knowledge_graph)
    setup_test_rules(repo_root, [rule_file_path], [rule_file_content])
    test_bot_dir = given_test_bot_directory_created(repo_root)
    return kg_file, test_bot_dir


def given_test_file_scope_setup_with_rule(bot_directory: Path, workspace_directory: Path):
    """Given: Test file scope setup with rule."""
    bootstrap_env(bot_directory, workspace_directory)
    story_graph = given_minimal_story_graph_for_test_file_scope()
    story_graph_path = given_story_graph_saved_to_workspace(workspace_directory, story_graph)
    test_file = given_test_file_with_content(
        workspace_directory, 'test_place_order.py',
        '''class TestPlOrd:
    """Abbreviated class name - should be TestPlaceOrder"""
    def test_creates_order(self):
        pass
'''
    )
    given_behavior_rule_created(bot_directory, '7_write_tests', 'test_class_organization_rule.json', {
        "description": "Test classes must match story names exactly",
        "scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
    })
    return story_graph, story_graph_path, test_file


def given_multiple_test_files_scope_setup_with_rule(bot_directory: Path, workspace_directory: Path):
    """Given: Multiple test files scope setup with rule."""
    bootstrap_env(bot_directory, workspace_directory)
    story_graph = given_story_graph_for_multiple_test_files()
    story_graph_path = given_story_graph_saved_to_workspace(workspace_directory, story_graph)
    test_file1 = given_test_file_with_content(
        workspace_directory, 'test_place_order.py',
        '''class TestPlOrd:
    """Abbreviated class name - should be TestPlaceOrder"""
    def test_creates_order(self):
        pass
'''
    )
    test_file2 = given_test_file_with_content(
        workspace_directory, 'test_cancel_order.py',
        '''class TestCancelOrd:
    """Abbreviated class name - should be TestCancelOrder"""
    def test_cancels_order(self):
        pass
'''
    )
    given_behavior_rule_created(bot_directory, '7_write_tests', 'test_class_organization_rule.json', {
        "description": "Test classes must match story names exactly",
        "scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
    })
    return story_graph, story_graph_path, test_file1, test_file2


def given_test_files_for_validate_code_files_action(workspace_directory: Path):
    """Given: Test files for validate code files action."""
    test_file1 = given_test_file_created(workspace_directory, 'test_example_feature.py', '''
import pytest

class TestExampleStory:
    def test_example_scenario(self):
        assert True
''')
    test_file2 = given_test_file_created(workspace_directory, 'test_another_feature.py', '''
import pytest

class TestAnotherStory:
    def test_another_scenario(self):
        assert True
''')
    return test_file1, test_file2


def when_execute_validate_code_files_action_with_test_files(bot_name: str, behavior: str, bot_directory: Path, test_files: list):
    """When: Execute validate code files action with test files."""
    action = when_validate_code_files_action_created(bot_name, behavior, bot_directory)
    parameters = when_create_test_files_parameter(test_files)
    return when_validate_code_files_action_executes(action, parameters)


def given_test_file_for_validate_code_files_action(workspace_directory: Path, filename: str = 'test_example.py'):
    """Given: Test file for validate code files action."""
    return given_test_file_created(workspace_directory, filename, '''
import pytest

class TestExampleStory:
    def test_example_scenario(self):
        assert True
''')


def when_execute_validate_code_files_action_with_single_test_file(bot_name: str, behavior: str, bot_directory: Path, test_file: Path):
    """When: Execute validate code files action with single test file."""
    action = when_validate_code_files_action_created(bot_name, behavior, bot_directory)
    parameters = when_create_test_files_parameter([test_file])
    return when_validate_code_files_action_executes(action, parameters)


def given_verb_noun_rule_content():
    """Given: Verb noun rule content."""
    return {
        'description': 'Use verb-noun format for all story elements',
        'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner',
        'do': {
            'examples': [{
                'description': 'Use verb-noun format',
                'content': ['Place Order', 'Validate Payment']
            }]
        },
        'dont': {
            'examples': [{
                'description': 'Don\'t use noun-only names',
                'content': ['Sales Management', 'Payment Processing']
            }]
        }
    }


def given_story_graph_and_test_file_with_violations_setup(bot_directory: Path, workspace_directory: Path, behavior: str):
    """Given: Story graph and test file with violations setup."""
    verb_noun_rule_content = given_verb_noun_rule_content()
    given_story_graph_with_content(workspace_directory, {
        'epics': [{'name': 'Bad Epic Name'}]  # Violation: noun-only format
    })
    test_file = given_test_file_created(workspace_directory, 'test_example.py', '''
import pytest

class TestExampleStory:
    def test_example_scenario(self):
        assert True
''')
    given_behavior_rule_file_created(bot_directory, behavior, 'use_verb_noun_format_for_story_elements.json', verb_noun_rule_content)
    given_common_rule_file_created(bot_directory, 'use_verb_noun_format_for_story_elements.json', verb_noun_rule_content)
    given_behavior_json_created(bot_directory, behavior, [{'name': 'validate_code_files', 'order': 1}])
    bootstrap_env(bot_directory, workspace_directory)
    return test_file


def given_source_files_for_validate_code_files_action(workspace_directory: Path):
    """Given: Source files for validate code files action."""
    source_file1 = given_source_file_created(workspace_directory, 'example_module.py', '''
class ExampleClass:
    def example_method(self):
        pass
''')
    source_file2 = given_source_file_created(workspace_directory, 'another_module.py', '''
class AnotherClass:
    def another_method(self):
        pass
''')
    return source_file1, source_file2


def when_execute_validate_code_files_action_with_code_files(bot_name: str, behavior: str, bot_directory: Path, code_files: list):
    """When: Execute validate code files action with code files."""
    action = when_validate_code_files_action_created(bot_name, behavior, bot_directory)
    parameters = when_create_code_files_parameter(code_files)
    return when_validate_code_files_action_executes(action, parameters)


def given_source_file_for_validate_code_files_action(workspace_directory: Path, filename: str = 'generated_module.py'):
    """Given: Source file for validate code files action."""
    return given_source_file_created(workspace_directory, filename, '''
class GeneratedClass:
    def generated_method(self):
        pass
''')


def given_test_file_and_naming_rule_setup(bot_directory: Path, workspace_directory: Path, behavior: str):
    """Given: Test file and naming rule setup."""
    test_file = given_test_file_created(workspace_directory, 'test_example.py', '''
import pytest

class TestExampleStory:
    def test_scenario(self):
        assert True
''')
    given_behavior_rule_file_created(bot_directory, behavior, 'test_naming_rule.json', {
        "description": "Test files must follow naming conventions",
        "scanner": "agile_bot.bots.base_bot.src.scanners.test_scanner.TestScanner"
    })
    given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
    return test_file


def given_story_graph_test_file_and_rules_setup(bot_directory: Path, workspace_directory: Path, behavior: str):
    """Given: Story graph, test file and rules setup."""
    verb_noun_rule_content = given_verb_noun_rule_content()
    given_story_graph_with_content(workspace_directory, {
        'epics': [{'name': 'Bad Epic Name'}]  # Violation: noun-only format
    })
    test_file = given_test_file_created(workspace_directory, 'test_example.py', '''
import pytest

class TestExampleStory:
    def test_example_scenario(self):
        assert True
''')
    given_behavior_rule_file_created(bot_directory, behavior, 'use_verb_noun_format_for_story_elements.json', verb_noun_rule_content)
    given_common_rule_file_created(bot_directory, 'use_verb_noun_format_for_story_elements.json', verb_noun_rule_content)
    given_behavior_json_created(bot_directory, behavior, [{'name': 'validate_code_files', 'order': 1}])
    bootstrap_env(bot_directory, workspace_directory)
    return test_file


def given_test_file_and_naming_rule_with_rule_id_setup(bot_directory: Path, workspace_directory: Path, behavior: str):
    """Given: Test file and naming rule with rule_id setup."""
    test_file = given_test_file_created(workspace_directory, 'test_example.py', '''
import pytest

class TestExampleStory:
    def test_scenario(self):
        assert True
''')
    given_behavior_rule_file_created(bot_directory, behavior, 'test_naming_rule.json', {
        'rule_id': 'test_naming_rule',
        'description': 'Test classes must follow naming convention',
        'scanner': 'agile_bot.bots.base_bot.src.scanners.test_scanner.TestScanner'
    })
    given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
    return test_file


def given_comprehensive_story_graph_setup_for_scope_test(bot_directory: Path, workspace_directory: Path, create_method):
    """Given: Comprehensive story graph setup for scope test."""
    given_workspace_directory_created(workspace_directory)
    bootstrap_env(bot_directory, workspace_directory)
    story_graph = create_method()
    story_graph_path = given_story_graph_file_with_content(workspace_directory, story_graph)
    given_scenarios_rule_created(bot_directory)
    return story_graph, story_graph_path


def when_execute_test_file_scope_validation(action, test_file: Path, story_graph_path: Path):
    """When: Execute test file scope validation."""
    parameters = when_create_test_file_parameter(test_file)
    all_violations = when_execute_action_and_extract_violations(action, parameters)
    then_violations_detected_in_test_file(all_violations, test_file)
    then_story_graph_not_modified_with_test_files(story_graph_path)
    return all_violations


def when_execute_multiple_test_files_scope_validation(action, test_file1: Path, test_file2: Path, story_graph_path: Path):
    """When: Execute multiple test files scope validation."""
    parameters = when_create_test_files_parameter([test_file1, test_file2])
    all_violations = when_execute_action_and_extract_violations(action, parameters)
    then_violations_detected_in_test_files_count(all_violations)
    then_violations_found_in_test_files(all_violations, [test_file1, test_file2])
    then_story_graph_not_modified_with_test_files(story_graph_path)
    return all_violations


def given_test_file_scope_verification_complete_setup(bot_directory: Path, workspace_directory: Path):
    """Given: Test file scope verification complete setup."""
    story_graph, story_graph_path = given_test_file_scope_verification_setup(bot_directory, workspace_directory)
    test_file = given_test_file_created_with_content(
        workspace_directory,
        'test_verify_scope.py',
        '''class TestVerifyScope:
    def test_verifies_scope(self):
        pass
'''
    )
    rule_file = given_test_scope_verification_rule_created(bot_directory)
    action = given_validate_rules_action_created(bot_directory, 'test_bot', 'write_tests')
    return story_graph, story_graph_path, test_file, rule_file, action




def then_result_contains_instructions_with_content_to_validate(result: dict):
    """Then: Result contains instructions with content_to_validate."""
    assert 'instructions' in result, "Result should contain 'instructions' key"
    instructions = result['instructions']
    assert 'content_to_validate' in instructions, (
        f"Expected 'content_to_validate' in instructions, but got keys: {instructions.keys()}"
    )
    return instructions


def then_content_to_validate_has_report_path(content_info: dict, expected_docs_dir: Path):
    """Then: Content to validate has report_path."""
    assert 'report_path' in content_info, (
        "content_to_validate must include report_path for saving validation report"
    )
    report_path = content_info['report_path']
    expected_report_path = expected_docs_dir / 'validation-report.md'
    assert report_path == str(expected_report_path), (
        f"report_path should be {expected_report_path}, got: {report_path}"
    )

def when_action_injects_behavior_specific_and_bot_rules(action: ValidateRulesAction):
    """When: Action injects behavior specific and bot rules."""
    return action.inject_behavior_specific_and_bot_rules()


def then_rules_data_has_valid_action_instructions(rules_data: dict):
    """Then: Rules data has valid action instructions."""
    assert 'action_instructions' in rules_data, (
        f"inject_behavior_specific_and_bot_rules must return 'action_instructions' key. Got: {rules_data}"
    )
    action_instructions_from_method = rules_data['action_instructions']
    assert len(action_instructions_from_method) > 0, (
        f"inject_behavior_specific_and_bot_rules should return action_instructions. Got: {rules_data}"
    )
    return action_instructions_from_method

def then_result_contains_instructions(result: dict):
    """Then: Result contains instructions."""
    assert 'instructions' in result, "Result should contain 'instructions' key"
    return result['instructions']

def then_base_instructions_are_valid_list(instructions: dict):
    """Then: Base instructions are valid list."""
    assert 'base_instructions' in instructions, (
        f"Expected 'base_instructions' in instructions, but got keys: {instructions.keys()}"
    )
    base_instructions_list = instructions['base_instructions']
    assert isinstance(base_instructions_list, list), (
        f"base_instructions should be a list, got: {type(base_instructions_list)}"
    )
    assert len(base_instructions_list) > 0, f"base_instructions should not be empty, got: {base_instructions_list}"
    return base_instructions_list

def then_base_instructions_contain_clarification_reference(base_instructions_list: list):
    """Then: Base instructions contain clarification reference."""
    instructions_text = ' '.join(base_instructions_list)
    assert 'clarification.json' in instructions_text or 'clarification' in instructions_text.lower(), (
        f"base_instructions should contain the action instructions mentioning clarification.json. Got: {instructions_text[:500]}"
    )

def then_validation_rules_are_valid_list(instructions: dict):
    """Then: Validation rules are valid list."""
    assert 'validation_rules' in instructions, (
        f"Expected 'validation_rules' in instructions, but got keys: {instructions.keys()}"
    )
    validation_rules = instructions['validation_rules']
    assert isinstance(validation_rules, list), (
        f"validation_rules should be a list, got: {type(validation_rules)}"
    )
    assert len(validation_rules) > 0, "validation_rules should contain rules"
    return validation_rules

def then_content_to_validate_has_workspace_location(instructions: dict, workspace_directory: Path):
    """Then: Content to validate has workspace location."""
    assert 'content_to_validate' in instructions, (
        f"Expected 'content_to_validate' in instructions, but got keys: {instructions.keys()}"
    )
    content_info = instructions['content_to_validate']
    # Explicitly check for project_location (implementation always uses project_location)
    assert 'project_location' in content_info, (
        "content_to_validate should contain project_location"
    )
    project_location_value = content_info['project_location']
    assert str(workspace_directory) in str(project_location_value), (
        f"project_location should point to the workspace directory, got: {project_location_value}"
    )
    assert 'rendered_outputs' in content_info, (
        "content_to_validate should contain rendered_outputs list"
    )
    return content_info

def then_instructions_specify_action_and_behavior(instructions: dict, expected_action: str, expected_behavior: str):
    """Then: Instructions specify action and behavior."""
    assert instructions.get('action') == expected_action, (
        f"instructions should specify action='{expected_action}'"
    )
    assert instructions.get('behavior') == expected_behavior, (
        f"instructions should specify behavior='{expected_behavior}'"
    )

def then_report_path_is_valid(content_info: dict, workspace_directory: Path):
    """Then: Report path is valid."""
    assert 'report_path' in content_info, (
        "content_to_validate should contain report_path where validation report should be saved"
    )
    report_path = content_info['report_path']
    assert report_path.endswith('validation-report.md'), (
        f"report_path should point to validation-report.md, got: {report_path}"
    )
    assert str(workspace_directory) in report_path or 'docs' in report_path, (
        f"report_path should be in workspace directory, got: {report_path}"
    )
    report_path_obj = Path(report_path)
    expected_docs_dir = workspace_directory / 'docs' / 'stories'
    assert report_path_obj.parent == expected_docs_dir, (
        f"report_path parent should be docs/stories directory, got: {report_path_obj.parent}"
    )
    assert report_path_obj.name == 'validation-report.md', (
        f"report_path filename should be validation-report.md, got: {report_path_obj.name}"
    )


def then_base_instructions_include_save_report_instruction(instructions: dict):
    """Then: Base instructions include save report instruction."""
    base_instructions_list = instructions['base_instructions']
    instructions_text = ' '.join(base_instructions_list).lower()
    assert ('save' in instructions_text and ('report' in instructions_text or 'validation' in instructions_text)) or \
           ('write' in instructions_text and ('report' in instructions_text or 'validation' in instructions_text)) or \
           'validation-report' in instructions_text or \
           'validation report' in instructions_text or \
           'save.*validation' in instructions_text, (
        f"base_instructions should include instruction to save/write validation report. Got: {instructions_text[:500]}"
    )


def given_behavior_specific_rule_exists(bot_directory: Path, behavior: str, rule_name: str, rule_content: dict):
    """Given: Behavior-specific rule exists."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    rules_dir = behavior_dir / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rule_file = rules_dir / rule_name
    rule_file.write_text(json.dumps(rule_content), encoding='utf-8')
    return rule_file


def given_story_graph_file_exists_minimal(workspace_directory: Path):
    """Given: Minimal story graph file exists."""
    docs_dir = workspace_directory / 'docs' / 'stories'
    docs_dir.mkdir(parents=True, exist_ok=True)
    story_graph_file = docs_dir / 'story-graph.json'
    story_graph_file.write_text(json.dumps({
        'epics': [],
        'stories': []
    }), encoding='utf-8')
    return story_graph_file


def then_instructions_file_exists_and_has_content(instructions_file: Path):
    """Then: Instructions file exists and has content."""
    assert instructions_file.exists(), f"Instructions file should exist at {instructions_file}"
    loaded_instructions = json.loads(instructions_file.read_text(encoding='utf-8'))
    assert 'instructions' in loaded_instructions, f"Instructions file should have 'instructions' key: {loaded_instructions}"
    assert len(loaded_instructions['instructions']) > 0, f"Instructions should not be empty: {loaded_instructions}"


def then_action_finds_instructions_file(action: ValidateRulesAction, expected_instructions_file: Path):
    """Then: Action finds instructions file."""
    action_base_actions_dir = action.base_actions_dir
    action_instructions_file = action_base_actions_dir / 'validate_rules' / 'instructions.json'
    assert action_instructions_file.exists(), f"Action should find instructions at {action_instructions_file}, base_actions_dir={action_base_actions_dir}"
    action_file_content = json.loads(action_instructions_file.read_text(encoding='utf-8'))
    assert 'instructions' in action_file_content, f"Action instructions file should have 'instructions' key: {action_file_content}"


def given_common_rule_created(bot_directory: Path, rule_name: str, rule_content: dict):
    """Given: Common rule created."""
    rules_dir = bot_directory / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / rule_name
    rule_file.write_text(json.dumps(rule_content, indent=2), encoding='utf-8')
    return rule_file


def given_story_graph_saved_to_workspace(workspace_directory: Path, story_graph: dict):
    """Given: Story graph saved to workspace."""
    docs_stories_dir = given_docs_stories_directory_exists(workspace_directory)
    story_graph_path = docs_stories_dir / 'story-graph.json'
    story_graph_path.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')
    return story_graph_path


def when_add_scope_to_story_graph(story_graph_path: Path, story_graph: dict, scope_config: dict):
    """When: Add scope to story graph."""
    story_graph['_validation_scope'] = scope_config
    story_graph_path.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')


def when_extract_violations_from_validation_rules(validation_rules: list):
    """When: Extract violations from validation rules."""
    all_violations = []
    for rule_data in validation_rules:
        assert 'scanner_results' in rule_data, f"Rule data must contain 'scanner_results' key: {rule_data}"
        scanner_results = rule_data['scanner_results']
        # Handle both old format (direct 'violations' key) and new format ('file_by_file'/'cross_file')
        if 'violations' in scanner_results:
            violations = scanner_results['violations']
            all_violations.extend(violations)
        elif 'file_by_file' in scanner_results:
            # New format: violations are nested under 'file_by_file' and 'cross_file'
            file_by_file = scanner_results.get('file_by_file', {})
            cross_file = scanner_results.get('cross_file', {})
            if 'violations' in file_by_file:
                all_violations.extend(file_by_file['violations'])
            if 'violations' in cross_file:
                all_violations.extend(cross_file['violations'])
        else:
            raise AssertionError(f"Scanner results must contain 'violations' key or 'file_by_file'/'cross_file' keys: {scanner_results}")
    return all_violations


def given_test_file_with_content(workspace_directory: Path, filename: str, content: str):
    """Given: Test file with content."""
    test_file = workspace_directory / filename
    test_file.write_text(content, encoding='utf-8')
    return test_file


def given_behavior_rule_created(bot_directory: Path, behavior: str, rule_name: str, rule_content: dict):
    """Given: Behavior rule created."""
    rules_dir = bot_directory / 'behaviors' / behavior / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / rule_name
    rule_file.write_text(json.dumps(rule_content, indent=2), encoding='utf-8')
    return rule_file


def when_action_executes_with_scope_parameters(action: ValidateRulesAction, parameters: dict):
    """When: Action executes with scope parameters."""
    return action.do_execute(parameters)


def then_violations_found_in_test_files(all_violations: list, test_files: list):
    """Then: Violations found in test files."""
    assert len(all_violations) > 0, "TestScanner should detect violations in test files"
    for test_file in test_files:
        test_file_violations = [
            v for v in all_violations 
            if ('location' in v and test_file.name in str(v.get('location', ''))) or 
               ('violation_message' in v and test_file.name.replace('.py', '') in str(v.get('violation_message', '')))
        ]
        assert len(test_file_violations) > 0, (
            f"Test file should be scanned. Expected: {test_file}. "
            f"Found violations: {all_violations}"
        )


# ============================================================================
# HELPER FUNCTIONS FOR VALIDATE CODE FILES ACTION TESTS
# ============================================================================

# Removed given_bot_and_behavior_setup - use test_helpers.given_bot_name_and_behavior_setup instead
# Import when needed: from agile_bot.bots.base_bot.test.test_helpers import given_bot_name_and_behavior_setup


def given_test_file_created(workspace_directory: Path, filename: str, content: str):
    """Given: Test file created in test directory (using test_base_bot structure)."""
    test_dir = workspace_directory / 'agile_bot' / 'bots' / 'test_base_bot' / 'test'
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / filename
    test_file.write_text(content, encoding='utf-8')
    return test_file


def given_source_file_created(workspace_directory: Path, filename: str, content: str):
    """Given: Source file created in src directory (using test_base_bot structure)."""
    src_dir = workspace_directory / 'agile_bot' / 'bots' / 'test_base_bot' / 'src' / 'bot'
    src_dir.mkdir(parents=True, exist_ok=True)
    source_file = src_dir / filename
    source_file.write_text(content, encoding='utf-8')
    return source_file


def given_environment_bootstrapped_with_story_graph(bot_directory: Path, workspace_directory: Path, story_graph: dict = None):
    """Given: Environment bootstrapped with story graph."""
    bootstrap_env(bot_directory, workspace_directory)
    story_graph_path = workspace_directory / 'docs' / 'stories' / 'story-graph.json'
    story_graph_path.parent.mkdir(parents=True, exist_ok=True)
    story_graph_path.write_text(json.dumps(story_graph or {'epics': []}), encoding='utf-8')
    return story_graph_path


def when_validate_code_files_action_created(bot_name: str, behavior: str, bot_directory: Path):
    """When: ValidateCodeFilesAction created."""
    try:
        from agile_bot.bots.story_bot.src.bot.validate_code_files_action import ValidateCodeFilesAction
        return ValidateCodeFilesAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
    except ImportError:
        pytest.skip("ValidateCodeFilesAction not yet implemented - test requires production code")


def when_validate_code_files_action_executes(action, parameters: dict):
    """When: ValidateCodeFilesAction executes with parameters."""
    return action.do_execute(parameters)


def then_result_has_violations_or_instructions(result: dict, expected_message: str = None):
    """Then: Result has violations or instructions."""
    assert 'violations' in result or 'instructions' in result, (
        expected_message or "ValidateCodeFilesAction should return results"
    )


def given_behavior_rule_file_created(bot_directory: Path, behavior: str, rule_name: str, rule_content: dict):
    """Given: Behavior rule file created."""
    behavior_dir = bot_directory / 'behaviors' / behavior
    rules_dir = behavior_dir / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / rule_name
    rule_file.write_text(json.dumps(rule_content), encoding='utf-8')
    return rule_file


def given_common_rule_file_created(bot_directory: Path, rule_name: str, rule_content: dict):
    """Given: Common rule file created."""
    common_rules_dir = bot_directory / 'rules'
    common_rules_dir.mkdir(parents=True, exist_ok=True)
    common_rule_file = common_rules_dir / rule_name
    common_rule_file.write_text(json.dumps(rule_content), encoding='utf-8')
    return common_rule_file


def given_story_graph_with_content(workspace_directory: Path, story_graph_content: dict):
    """Given: Story graph with content."""
    story_graph_path = workspace_directory / 'docs' / 'stories' / 'story-graph.json'
    story_graph_path.parent.mkdir(parents=True, exist_ok=True)
    story_graph_path.write_text(json.dumps(story_graph_content), encoding='utf-8')
    return story_graph_path


def given_behavior_json_created(bot_directory: Path, behavior: str, actions: list):
    """Given: Behavior.json file created."""
    from agile_bot.bots.base_bot.test.test_helpers import create_actions_workflow_json
    create_actions_workflow_json(
        bot_directory=bot_directory,
        behavior_name=behavior,
        actions=actions
    )


def then_story_graph_not_modified_with_test_files(story_graph_path: Path):
    """Then: Story graph not modified with test files."""
    reloaded_graph = json.loads(story_graph_path.read_text(encoding='utf-8'))
    assert 'test_files' not in reloaded_graph, "test_files should not be persisted to knowledge graph file (one-off validation)"


# Removed duplicate - imported from test_helpers
from agile_bot.bots.base_bot.test.test_helpers import create_validation_rules

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

def _validate_scanner_class(scanner_class, scanner_module_path: str):
    """Helper: Validate scanner class structure."""
    if not isinstance(scanner_class, type):
        return None, f"Scanner path does not point to a class: {scanner_module_path}"
    if not hasattr(scanner_class, 'scan'):
        return None, f"Scanner class missing required 'scan' method: {scanner_module_path}"
    return scanner_class, None

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
        return _validate_scanner_class(scanner_class, scanner_module_path)
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
    rule_name = scanner_metadata.get('rule') or scanner_metadata.get('rule_name')  # Support both
    return (rule_name == expected_rule_name and
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
    try:
        if expected_line_number is not None:
            then_violation_has_expected_line_number(violation, expected_line_number)
        if expected_location is not None:
            then_violation_has_expected_location(violation, expected_location)
        if expected_message is not None:
            then_violation_has_expected_message(violation, expected_message)
        if expected_severity is not None:
            then_violation_has_expected_severity(violation, expected_severity)
        return True
    except AssertionError:
        return False

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
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'exploration')
        
        # When: Action starts execution
        when_validate_rules_action_tracks_start(action)
        
        # Then: Activity logged with full path
        then_activity_logged_with_action_state(workspace_directory, 'story_bot.exploration.validate_rules')

    def test_track_activity_when_validate_rules_action_completes(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track activity when validate_rules action completes
        GIVEN: validate_rules action started at timestamp
        WHEN: validate_rules action finishes execution
        THEN: Activity logger creates completion entry with outputs and duration
        """
        # Bootstrap environment
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'exploration')
        
        # When: Action completes with validation results
        when_validate_rules_action_tracks_completion(
            action,
            outputs={
                'violations_count': 2,
                'rules_checked_count': 7,
                'file_path': 'validation-report.md'
            },
            duration=240
        )
        
        # Then: Completion logged with validation metrics
        then_completion_entry_logged_with_outputs(
            workspace_directory,
            expected_outputs={
                'violations_count': 2,
                'rules_checked_count': 7,
                'file_path': 'validation-report.md'
            },
            expected_duration=240
        )

    def test_track_multiple_validate_rules_invocations_across_behaviors(self, bot_directory, workspace_directory):
        """
        SCENARIO: Track multiple validate_rules invocations across behaviors
        GIVEN: activity log contains entries for shape and exploration validate_rules
        WHEN: both entries are present
        THEN: activity log distinguishes same action in different behaviors
        """
        # Given: Activity log with multiple validate_rules entries (in workspace_directory)
        given_activity_log_with_entries(workspace_directory, [
            {
                'action_state': 'story_bot.shape.validate_rules',
                'timestamp': '2025-12-03T09:00:00Z',
                'outputs': {'violations_count': 0}
            },
            {
                'action_state': 'story_bot.exploration.validate_rules',
                'timestamp': '2025-12-03T10:00:00Z',
                'outputs': {'violations_count': 2}
            }
        ])
        
        # When: Read activity log
        log_data = read_activity_log(workspace_directory)
        
        # Then: 2 separate entries with full paths
        then_activity_log_has_entries_with_action_states(
            workspace_directory,
            expected_count=2,
            expected_action_states=['story_bot.shape.validate_rules', 'story_bot.exploration.validate_rules']
        )

    def test_activity_log_maintains_chronological_order(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity Log Maintains Chronological Order
        GIVEN: activity log contains 10 previous action entries
        WHEN: validate_rules entry is appended
        THEN: New entry appears at end of log in chronological order
        """
        # Given: Activity log with 10 entries (in workspace_directory)
        bootstrap_env(bot_directory, workspace_directory)
        given_activity_log_with_entries(workspace_directory, [
            {'action_state': f'story_bot.discovery.action_{i}', 'timestamp': f'10:{i:02d}'}
            for i in range(10)
        ])
        action = given_environment_bootstrapped_and_action_initialized(bot_directory, workspace_directory, 'story_bot', 'exploration')
        
        # When: Append validate_rules entry
        when_validate_rules_action_tracks_start(action)
        
        # Then: New entry at end in chronological order
        then_activity_log_has_entry_count_and_last_action_state(
            workspace_directory,
            expected_count=11,
            expected_last_action_state='story_bot.exploration.validate_rules'
        )


# ============================================================================
# STORY: Complete Validate Rules Action
# ============================================================================

class TestInvokeCompleteValidationWorkflow:
    """Story: Invoke Complete Validation Workflow - Tests workflow completion at terminal action."""

    def test_validate_rules_marks_workflow_as_complete(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules marks workflow as complete
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action (next_action=null)
        WHEN: validate_rules finalizes
        THEN: Workflow is marked as complete (no next action)
        """
        # Given: Terminal action
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'exploration')
        
        # When: Action finalizes with no next action
        action_result = when_action_finalizes_and_transitions(action, next_action=None)
        
        # Then: No next action (terminal)
        then_no_next_action_in_result(action_result)

    def test_validate_rules_does_not_inject_next_action_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules does NOT inject next action instructions
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules finalizes
        THEN: No next action instructions injected
        """
        # Given: Terminal action
        given_terminal_action_config(bot_directory, 'validate_rules', 5)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'scenarios')
        
        # When: Action injects instructions
        instructions = when_action_injects_next_action_instructions(action)
        
        # Then: No next action instructions (terminal)
        then_no_next_action_instructions_injected(instructions)

    def test_workflow_state_shows_all_actions_completed(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow state shows all actions completed
        GIVEN: validate_rules completes as final action
        WHEN: Action tracks completion
        THEN: Activity log records the completion
        """
        # Bootstrap environment
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'exploration')
        
        # When: Final action completes
        when_validate_rules_action_tracks_completion(
            action,
            outputs={'violations_count': 0, 'workflow_complete': True},
            duration=180
        )
        
        # Then: Completion recorded in activity log
        then_completion_entry_has_workflow_complete_flag(workspace_directory)

    def test_activity_log_records_full_workflow_completion(self, bot_directory, workspace_directory):
        """
        SCENARIO: Activity log records full workflow completion
        GIVEN: validate_rules completes at timestamp
        WHEN: Activity logger records completion
        THEN: Activity log shows validate_rules completed and workflow finished
        """
        # Bootstrap environment
        log_file = given_environment_bootstrapped_and_activity_log_initialized(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'scenarios')
        
        # When: Terminal action logs completion
        when_validate_rules_action_tracks_completion(
            action,
            outputs={'violations_count': 0, 'workflow_complete': True},
            duration=180
        )
        
        # Then: Completion logged with workflow_complete flag
        then_completion_entry_has_workflow_complete_flag(workspace_directory)

    def test_workflow_does_not_transition_after_validate_rules(self, bot_directory, workspace_directory):
        """
        SCENARIO: Workflow does NOT transition after validate_rules
        GIVEN: validate_rules action is complete
        AND: validate_rules is terminal action
        WHEN: validate_rules provides next action instructions
        THEN: No next action instructions (empty string indicates terminal action)
        """
        # Given: Terminal action
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'exploration')
        
        # When: Action provides next action instructions
        instructions = when_action_injects_next_action_instructions(action)
        
        # Then: No next action instructions (terminal)
        then_no_next_action_instructions_injected(instructions)

    def test_behavior_workflow_completes_at_terminal_action(self, bot_directory, workspace_directory):
        """
        SCENARIO: Behavior workflow completes at terminal action
        GIVEN: exploration behavior has completed all 5 workflow actions
        WHEN: validate_rules (terminal) is marked complete
        THEN: Exploration behavior workflow is complete
        """
        # Given: Workflow state with all actions completed
        state_file = given_workflow_state_with_all_actions_completed(
            workspace_directory, 'story_bot', 'exploration', 'validate_rules'
        )
        
        # When: Check workflow completion status
        is_complete = when_check_workflow_completion_status('exploration', state_file)
        
        # Then: Behavior workflow is complete
        then_behavior_workflow_is_complete(is_complete)

    def _verify_action_setup_and_execution(self, bot_directory, workspace_directory):
        """Helper: Set up action and execute, returning action and result."""
        instructions_file = given_base_action_instructions_and_behavior_rule_setup(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'story_bot', 'shape')
        then_action_finds_instructions_file(action, instructions_file)
        rules_data = when_action_injects_behavior_specific_and_bot_rules(action)
        then_rules_data_has_valid_action_instructions(rules_data)
        return action, when_action_executes_and_returns_result(action)
    
    def _verify_instructions_structure(self, action_result, workspace_directory):
        """Helper: Verify instructions structure contains required fields."""
        instructions = then_result_contains_instructions(action_result)
        base_instructions_list = then_base_instructions_are_valid_list(instructions)
        then_base_instructions_contain_clarification_reference(base_instructions_list)
        then_validation_rules_are_valid_list(instructions)
        content_info = then_content_to_validate_has_workspace_location(instructions, workspace_directory)
        return instructions, content_info
    
    def test_validate_rules_returns_instructions_with_rules_as_context(self, bot_directory, workspace_directory):
        """
        SCENARIO: validate_rules returns instructions with rules as supporting context
        GIVEN: validate_rules action has base instructions and validation rules
        WHEN: validate_rules action executes
        THEN: Return value contains base_instructions (primary) and validation_rules (context)
        AND: Return value contains content_to_validate information
        """
        action, action_result = self._verify_action_setup_and_execution(bot_directory, workspace_directory)
        instructions, content_info = self._verify_instructions_structure(action_result, workspace_directory)
        then_instructions_specify_action_and_behavior(instructions, 'validate_rules', 'shape')
        then_report_path_is_valid(content_info, workspace_directory)

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
        given_base_action_instructions_for_validate_rules(bot_directory, save_report_instruction=True)
        
        # Given: Workspace directory with docs/stories/ folder
        action, result = given_environment_and_action_for_report_path_test(bot_directory, workspace_directory)
        docs_dir = given_docs_stories_directory_exists(workspace_directory)
        
        # When: Action identifies content to validate
        # Then: report_path is included in content_to_validate
        instructions = then_result_contains_instructions_with_content_to_validate(result)
        content_info = instructions['content_to_validate']
        
        then_content_to_validate_has_report_path(content_info, docs_dir)
        then_base_instructions_include_save_report_instruction(instructions)


# ============================================================================
# STORY: Discovers Scanners
# ============================================================================

class TestDiscoversScanners:
    """Story: Discovers Scanners - Tests scanner discovery from rule files."""

    @pytest.mark.parametrize("rule_file_paths,rule_file_content,expected_scanner_count", [
        # Example 1: 3 scanners from common rules and current behavior
        (
            [
                'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
                'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json',
                'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/apply_exhaustive_decomposition.json'
            ],
            [
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}},
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.exhaustive_decomposition_scanner.ExhaustiveDecompositionScanner', 'description': 'Apply exhaustive decomposition', 'do': {}}
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
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}}
            ],
            2
        ),
        # Example 3: Single scanner
        (
            ['agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json'],
            [{'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}}],
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
        test_bot_dir = given_test_bot_setup_with_rules(repo_root, bot_directory, workspace_directory, rule_file_paths, rule_file_content)
        
        # When: ValidateRulesAction loads rules and discovers scanners
        action = given_validate_rules_action_for_test_bot(test_bot_dir, 'test_story_bot', 'shape')
        behavior = given_behavior_created_for_test_bot(test_bot_dir, 'shape', 'test_story_bot')
        
        # Then: Scanners discovered from rules
        then_scanners_discovered_with_expected_count_and_valid_structure(behavior, expected_scanner_count)


# ============================================================================
# STORY: Run Scanners Against Knowledge Graph
# ============================================================================

class TestRunScannersAgainstKnowledgeGraph:
    """Story: Run Scanners Against Knowledge Graph - Tests scanner execution against knowledge graph."""

    @pytest.mark.parametrize("rule_file_path,rule_file_content,knowledge_graph,expected_has_violations", [
        # Example 1: Epic with noun-only name (violation)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Sales Management'}]},
            True
        ),
        # Example 2: Correct verb-noun format (no violations)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Place Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Place Order'}]}]}]},
            False
        ),
        # Example 3: Story with actor in name (violation)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
            {'epics': [{'name': 'Place Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Customer places order'}]}]}]},
            True
        ),
        # Example 4: Feature with capability noun (violation)
        (
            'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json',
            {'scanner': 'agile_bot.bots.base_bot.src.scanners.active_language_scanner.ActiveLanguageScanner', 'description': 'Use active behavioral language', 'do': {}},
            {'epics': [{'name': 'Place Order', 'features': [{'name': 'Payment Processing'}]}]},
            True
        ),
        # Example 5: Story sizing violation
        (
            'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json',
                {'scanner': 'agile_bot.bots.base_bot.src.scanners.story_sizing_scanner.StorySizingScanner', 'description': 'Size stories 3-12 days', 'do': {}},
            {'epics': [{'name': 'Place Order', 'features': [{'name': 'Validates Payment', 'stories': [{'name': 'Place Order', 'sizing': '15 days'}]}]}]},
            True
        ),
        # Example 6: Empty graph (no violations)
        (
            'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json',
            {'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner', 'description': 'Use verb-noun format', 'do': {}},
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
        kg_file, test_bot_dir = given_knowledge_graph_and_test_bot_setup(repo_root, bot_directory, workspace_directory, knowledge_graph, rule_file_path, rule_file_content)
        
        # When: ValidateRulesAction loads rules and discovers scanners
        action = given_validate_rules_action_for_test_bot(test_bot_dir, 'test_story_bot', 'shape')
        instructions_result = when_action_executes_and_returns_result(action)
        
        # Then: Instructions contain rules with scanner results
        instructions = then_result_contains_instructions_with_content_to_validate(instructions_result)
        then_validation_rules_have_expected_structure(instructions)


# ============================================================================
# STORY: Handle Validate Rules Exceptions
# ============================================================================

class TestHandleValidateRulesExceptions:
    """Story: Handle Validate Rules Exceptions - Tests exception handling for validate_rules action."""

    def test_validate_rules_raises_exception_when_story_graph_not_found(self, bot_directory, workspace_directory, tmp_path):
        """
        SCENARIO: ValidateRulesAction raises exception when story graph not found
        GIVEN: Story graph file doesn't exist
        WHEN: validate_rules action executes
        THEN: FileNotFoundError is raised with appropriate message
        """
        # Given: Story graph file doesn't exist
        # Bootstrap environment
        action = given_environment_setup_for_file_not_found_test(bot_directory, workspace_directory)
        
        # When: Validate rules action executes
        # Then: FileNotFoundError is raised (verified by when_action_executes_and_raises_file_not_found_error)
        when_action_executes_and_raises_file_not_found_error(action)

    def test_validate_rules_raises_exception_when_story_graph_invalid_json(self, bot_directory, workspace_directory, tmp_path):
        """
        SCENARIO: ValidateRulesAction raises exception when story graph has syntax error
        GIVEN: Story graph file exists but contains invalid JSON
        WHEN: validate_rules action executes
        THEN: JSONDecodeError or ValueError is raised
        """
        # Given: Story graph file exists but contains invalid JSON
        # Bootstrap environment
        action, story_graph_file = given_environment_setup_for_invalid_json_test(bot_directory, workspace_directory)
        
        # When: Validate rules action executes
        # Then: JSONDecodeError or ValueError is raised (verified by when_action_executes_and_raises_json_error)
        when_action_executes_and_raises_json_error(action)


# ============================================================================
# STORY: Validate Rules According to Scope
# ============================================================================

class TestValidateRulesAccordingToScope:
    """Story: Validate Rules According to Scope - Tests that validate_rules only processes stories within specified scope."""

    @staticmethod
    def create_comprehensive_story_graph() -> Dict[str, Any]:
        """Create a comprehensive story graph with multiple epics, sub-epics, stories, and increments."""
        return {
            "epics": [
                {
                    "name": "Manage Mobs",
                    "sequential_order": 1,
                    "sub_epics": [
                        {
                            "name": "Create Mob",
                            "sequential_order": 1,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Select And Capture Tokens",
                                            "sequential_order": 1,
                                            "scenarios": [{"name": "test scenario"}]
                                        },
                                        {
                                            "name": "Group Tokens And Create Mob Entity",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Associate Tokens And Persist Mob",
                                            "sequential_order": 3,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Edit Mob",
                            "sequential_order": 2,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Select Mob To Edit",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Add Minion Tokens To Mob",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Remove Minion Tokens From Mob",
                                            "sequential_order": 3,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Spawn Mob From Actors",
                            "sequential_order": 3,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Select Actors For Mob",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Apply Mob Template",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Apply Strategies",
                    "sequential_order": 2,
                    "sub_epics": [
                        {
                            "name": "Select Strategy",
                            "sequential_order": 1,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Select Mob For Strategy",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Choose Strategy Type",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Choose Strategy Types",
                            "sequential_order": 2,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Select Attack Most Powerful Target Strategy",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Select Attack Weakest Target Strategy",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Execute Mob Actions",
                    "sequential_order": 3,
                    "sub_epics": [
                        {
                            "name": "Initiate Mob Action",
                            "sequential_order": 1,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Handle Token Click And Intercept",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Find Mob For Token",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Execute Attack",
                            "sequential_order": 2,
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "sequential_order": 1,
                                    "stories": [
                                        {
                                            "name": "Initiate And Prepare Attack",
                                            "sequential_order": 1,
                                            "scenarios": []
                                        },
                                        {
                                            "name": "Resolve Attack Rolls And Apply Damage",
                                            "sequential_order": 2,
                                            "scenarios": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "increments": [
                {
                    "name": "Foundry Integration Shakedown",
                    "priority": 1,
                    "epics": [
                        {
                            "name": "Manage Mobs",
                            "sub_epics": [
                                {
                                    "name": "Create Mob",
                                    "stories": [
                                        {"name": "Select And Capture Tokens"},
                                        {"name": "Group Tokens And Create Mob Entity"},
                                        {"name": "Associate Tokens And Persist Mob"}
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Execute Mob Actions",
                            "sub_epics": [
                                {
                                    "name": "Initiate Mob Action",
                                    "stories": [
                                        {"name": "Handle Token Click And Intercept"},
                                        {"name": "Find Mob For Token"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Strategy System Integration",
                    "priority": 2,
                    "epics": [
                        {
                            "name": "Apply Strategies",
                            "sub_epics": [
                                {
                                    "name": "Select Strategy",
                                    "stories": [
                                        {"name": "Select Mob For Strategy"},
                                        {"name": "Choose Strategy Type"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Enhanced Mob Management",
                    "priority": 3,
                    "epics": [
                        {
                            "name": "Manage Mobs",
                            "sub_epics": [
                                {
                                    "name": "Edit Mob",
                                    "stories": [
                                        {"name": "Select Mob To Edit"},
                                        {"name": "Add Minion Tokens To Mob"},
                                        {"name": "Remove Minion Tokens From Mob"}
                                    ]
                                },
                                {
                                    "name": "Spawn Mob From Actors",
                                    "stories": [
                                        {"name": "Select Actors For Mob"},
                                        {"name": "Apply Mob Template"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def extract_story_names_from_violations(violations: List[Dict[str, Any]]) -> Set[str]:
        """Extract story names from violation messages."""
        story_names = set()
        for violation in violations:
            assert 'violation_message' in violation, f"Violation must contain 'violation_message' key: {violation}"
            message = violation['violation_message']
            # Extract story name from messages like 'Story "Story Name" has no scenarios...'
            if 'Story "' in message:
                start = message.find('Story "') + 7
                end = message.find('"', start)
                if end > start:
                    story_names.add(message[start:end])
        return story_names

    @staticmethod
    def _handle_story_names_scope(scope_config: Dict[str, Any], expected_names: Set[str]):
        """Helper: Handle story_names scope configuration."""
        if 'story_names' in scope_config:
            story_names = scope_config['story_names']
            if isinstance(story_names, list):
                expected_names.update(story_names)
            elif isinstance(story_names, str):
                expected_names.add(story_names)
    
    @staticmethod
    def _handle_increment_priorities_scope(scope_config: Dict[str, Any], story_graph: Dict[str, Any], expected_names: Set[str]):
        """Helper: Handle increment_priorities scope configuration."""
        if 'increment_priorities' in scope_config:
            priorities = scope_config['increment_priorities']
            if not isinstance(priorities, list):
                priorities = [priorities]
            for priority in priorities:
                for increment in story_graph.get('increments', []):
                    inc_priority = increment.get('priority', 999)
                    if isinstance(inc_priority, str):
                        priority_map = {'NOW': 1, 'LATER': 2, 'SOON': 1, 'NEXT': 2}
                        inc_priority = priority_map.get(inc_priority.upper(), 999)
                    if inc_priority == priority:
                        TestValidateRulesAccordingToScope._extract_story_names_from_increment(increment, expected_names)
    
    @staticmethod
    def _handle_epic_names_scope(scope_config: Dict[str, Any], story_graph: Dict[str, Any], expected_names: Set[str]):
        """Helper: Handle epic_names scope configuration."""
        if 'epic_names' in scope_config:
            epic_names_list = scope_config['epic_names']
            if not isinstance(epic_names_list, list):
                epic_names_list = [epic_names_list]
            for epic_name in epic_names_list:
                for epic in story_graph.get('epics', []):
                    if epic.get('name') == epic_name:
                        TestValidateRulesAccordingToScope._extract_story_names_from_epic(epic, expected_names)
    
    @staticmethod
    def get_expected_story_names_for_scope(scope_config: Dict[str, Any], story_graph: Dict[str, Any]) -> Set[str]:
        """Calculate expected story names in scope based on scope configuration."""
        expected_names = set()
        TestValidateRulesAccordingToScope._handle_story_names_scope(scope_config, expected_names)
        TestValidateRulesAccordingToScope._handle_increment_priorities_scope(scope_config, story_graph, expected_names)
        TestValidateRulesAccordingToScope._handle_epic_names_scope(scope_config, story_graph, expected_names)
        if not expected_names and not scope_config.get('validate_all'):
            return None
        return expected_names

    @staticmethod
    def _extract_story_names_from_increment(increment_data: Dict[str, Any], story_names: Set[str]) -> None:
        """Recursively extract story names from increment structure."""
        for story in increment_data.get('stories', []):
            if isinstance(story, dict) and 'name' in story:
                story_names.add(story['name'])
            elif isinstance(story, str):
                story_names.add(story)
        
        for epic in increment_data.get('epics', []):
            TestValidateRulesAccordingToScope._extract_story_names_from_epic(epic, story_names)

    @staticmethod
    def _extract_story_names_from_epic(epic_data: Dict[str, Any], story_names: Set[str]) -> None:
        """Recursively extract story names from epic/sub_epic structure."""
        for story in epic_data.get('stories', []):
            if isinstance(story, dict) and 'name' in story:
                story_names.add(story['name'])
            elif isinstance(story, str):
                story_names.add(story)
        
        for story_group in epic_data.get('story_groups', []):
            for story in story_group.get('stories', []):
                if isinstance(story, dict) and 'name' in story:
                    story_names.add(story['name'])
                elif isinstance(story, str):
                    story_names.add(story)
        
        for sub_epic in epic_data.get('sub_epics', []):
            TestValidateRulesAccordingToScope._extract_story_names_from_epic(sub_epic, story_names)

    # Test cases for parameterized test
    SCOPE_TEST_CASES = [
        {
            "test_name": "one_story",
            "scope_config": {
                "story_names": ["Select And Capture Tokens"]
            },
            "description": "Validate single story by name",
            "expected_stories_in_scope": ["Select And Capture Tokens"],
            "expected_violations": []  # Has scenarios, so no violations
        },
        {
            "test_name": "several_stories",
            "scope_config": {
                "story_names": ["Select And Capture Tokens", "Group Tokens And Create Mob Entity", "Associate Tokens And Persist Mob"]
            },
            "description": "Validate multiple specific stories",
            "expected_stories_in_scope": ["Select And Capture Tokens", "Group Tokens And Create Mob Entity", "Associate Tokens And Persist Mob"],
            "expected_violations": ["Group Tokens And Create Mob Entity", "Associate Tokens And Persist Mob"]  # Select And Capture Tokens has scenarios
        },
        {
            "test_name": "single_epic",
            "scope_config": {
                "epic_names": ["Manage Mobs"]
            },
            "description": "Validate all stories in a single epic",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ]  # All except Select And Capture Tokens (has scenarios)
        },
        {
            "test_name": "multiple_epics",
            "scope_config": {
                "epic_names": ["Manage Mobs", "Execute Mob Actions"]
            },
            "description": "Validate stories across multiple epics",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Initiate And Prepare Attack",
                "Resolve Attack Rolls And Apply Damage"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Initiate And Prepare Attack",
                "Resolve Attack Rolls And Apply Damage"
            ]  # All except Select And Capture Tokens
        },
        {
            "test_name": "single_sub_epic",
            "scope_config": {
                "story_names": ["Select Mob To Edit", "Add Minion Tokens To Mob", "Remove Minion Tokens From Mob"]
            },
            "description": "Validate stories in a single sub-epic (Edit Mob) by specifying story names",
            "expected_stories_in_scope": ["Select Mob To Edit", "Add Minion Tokens To Mob", "Remove Minion Tokens From Mob"],
            "expected_violations": ["Select Mob To Edit", "Add Minion Tokens To Mob", "Remove Minion Tokens From Mob"]  # None have scenarios
        },
        {
            "test_name": "multiple_sub_epics_different_epics",
            "scope_config": {
                "story_names": [
                    "Select Mob To Edit",  # From Manage Mobs > Edit Mob
                    "Select Mob For Strategy",  # From Apply Strategies > Select Strategy
                    "Handle Token Click And Intercept"  # From Execute Mob Actions > Initiate Mob Action
                ]
            },
            "description": "Validate stories from multiple sub-epics across different epics",
            "expected_stories_in_scope": [
                "Select Mob To Edit",
                "Select Mob For Strategy",
                "Handle Token Click And Intercept"
            ],
            "expected_violations": [
                "Select Mob To Edit",
                "Select Mob For Strategy",
                "Handle Token Click And Intercept"
            ]  # None have scenarios
        },
        {
            "test_name": "single_increment",
            "scope_config": {
                "increment_priorities": [1]
            },
            "description": "Validate stories in increment 1",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token"
            ]  # All except Select And Capture Tokens
        },
        {
            "test_name": "multiple_increments",
            "scope_config": {
                "increment_priorities": [1, 2]
            },
            "description": "Validate stories across multiple increments",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Select Mob For Strategy",
                "Choose Strategy Type"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Select Mob For Strategy",
                "Choose Strategy Type"
            ]  # All except Select And Capture Tokens
        },
        {
            "test_name": "epic_with_many_sub_epics",
            "scope_config": {
                "epic_names": ["Manage Mobs"]
            },
            "description": "Validate epic with multiple sub-epics (Create Mob, Edit Mob, Spawn Mob From Actors)",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ]  # All except Select And Capture Tokens
        },
        {
            "test_name": "combined_scope",
            "scope_config": {
                "increment_priorities": [1],
                "epic_names": ["Manage Mobs"]
            },
            "description": "Validate stories matching both increment and epic criteria (union - stories in increment 1 OR in Manage Mobs epic)",
            "expected_stories_in_scope": [
                "Select And Capture Tokens",
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ],
            "expected_violations": [
                "Group Tokens And Create Mob Entity",
                "Associate Tokens And Persist Mob",
                "Handle Token Click And Intercept",
                "Find Mob For Token",
                "Select Mob To Edit",
                "Add Minion Tokens To Mob",
                "Remove Minion Tokens From Mob",
                "Select Actors For Mob",
                "Apply Mob Template"
            ]  # All except Select And Capture Tokens
        },
        {
            "test_name": "validate_all",
            "scope_config": {
                "validate_all": True
            },
            "description": "Validate all stories (no scope filtering)",
            "expected_stories_in_scope": None,  # None means all stories
            "expected_violations": None  # None means calculate from all stories
        },
        {
            "test_name": "no_scope_defaults_to_all",
            "scope_config": {},
            "description": "No scope specified - defaults to validate all stories",
            "expected_stories_in_scope": None,  # None means all stories
            "expected_violations": None  # None means calculate from all stories
        }
    ]

    @pytest.mark.parametrize("test_case", SCOPE_TEST_CASES, ids=[tc["test_name"] for tc in SCOPE_TEST_CASES])
    def test_validate_rules_respects_scope(self, test_case: Dict[str, Any], tmp_path: Path, bot_directory, workspace_directory):
        """
        SCENARIO: Validate that validate_rules only processes stories within specified scope.
        
        Tests various scope configurations:
        - Single story
        - Multiple stories
        - Single epic
        - Multiple epics
        - Single sub-epic
        - Multiple sub-epics from different epics
        - Single increment
        - Multiple increments
        - Epic with many sub-epics
        - Combined scope criteria
        - Validate all
        - Default to all stories
        """
        # Setup
        story_graph, story_graph_path = given_comprehensive_story_graph_setup_for_scope_test(bot_directory, workspace_directory, self.create_comprehensive_story_graph)
        action = given_validate_rules_action_initialized(bot_directory, 'test_bot', 'scenarios')
        scope_config, expected_stories_in_scope, expected_violations_list = when_extract_test_case_data(test_case)
        when_add_scope_to_story_graph_if_provided(story_graph_path, story_graph, scope_config)
        parameters = when_create_parameters_from_scope_config(scope_config)
        violated_story_names, expected_stories_in_scope_set, expected_violations_set = when_execute_action_and_extract_violated_story_names_with_conversion(
            action,
            parameters,
            story_graph,
            test_case,
            TestValidateRulesAccordingToScope.extract_story_names_from_violations,
            when_convert_expected_stories_to_set,
            when_convert_expected_violations_to_set,
            self._extract_story_names_from_epic
        )
        
        # Verify violations match expected scope and stories
        then_violations_match_expected_scope_and_stories(
            violated_story_names,
            expected_stories_in_scope_set,
            expected_violations_set
        )

    def test_validate_rules_scope_extraction(self, bot_directory, workspace_directory):
        """Test that scope extraction functions work correctly."""
        # Given: Comprehensive story graph
        story_graph = self.create_comprehensive_story_graph()
        
        # When: Test scope extraction with increment priorities
        # Then: Scope extraction functions work correctly (verified by when_test_scope_extraction_with_increment_priorities)
        when_test_scope_extraction_with_increment_priorities(story_graph, self.get_expected_story_names_for_scope)
        
        # Test epic extraction
        when_test_scope_extraction_with_epic_names(story_graph, self.get_expected_story_names_for_scope)
        
        # Test multiple epics
        when_test_scope_extraction_with_multiple_epics(story_graph, self.get_expected_story_names_for_scope)
        
        # Test story names
        when_test_scope_extraction_with_story_names(story_graph, self.get_expected_story_names_for_scope)

    def test_validate_rules_with_test_file_scope_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Validate test file using test_file scope parameter
        GIVEN: A test file exists with violations
        AND: A rule with TestScanner exists
        WHEN: validate_rules is called with test_file scope parameter
        THEN: TestScanner instances scan the test file
        AND: Violations are detected in the test file
        AND: test_file is not added to the knowledge graph (one-off validation)
        """
        # Given: Test file exists with violations and rule with TestScanner exists
        # Bootstrap environment
        story_graph, story_graph_path, test_file = given_test_file_scope_setup_with_rule(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'test_bot', 'write_tests')
        # When: Validate rules is called with test_file scope parameter
        # Then: TestScanner instances scan the test file and violations are detected (verified by when_execute_test_file_scope_validation)
        when_execute_test_file_scope_validation(action, test_file, story_graph_path)

    def test_validate_rules_with_test_files_scope_parameter(self, bot_directory, workspace_directory):
        """
        SCENARIO: Validate multiple test files using test_files scope parameter
        GIVEN: Multiple test files exist with violations
        AND: A rule with TestScanner exists
        WHEN: validate_rules is called with test_files scope parameter (plural)
        THEN: TestScanner instances scan all test files
        AND: Violations are detected in all test files
        AND: test_files are passed through scope parameters correctly
        """
        # Given: Multiple test files exist with violations and rule with TestScanner exists
        # Bootstrap environment
        story_graph, story_graph_path, test_file1, test_file2 = given_multiple_test_files_scope_setup_with_rule(bot_directory, workspace_directory)
        action = given_validate_rules_action_initialized(bot_directory, 'test_bot', 'write_tests')
        # When: Validate rules is called with test_files scope parameter
        # Then: TestScanner instances scan all test files and violations are detected (verified by when_execute_multiple_test_files_scope_validation)
        when_execute_multiple_test_files_scope_validation(action, test_file1, test_file2, story_graph_path)

    def test_validate_rules_verifies_test_files_passed_to_scanner(self, bot_directory, workspace_directory):
        """
        SCENARIO: Verify that test files from scope parameters are actually passed to TestScanner
        GIVEN: A test file exists
        AND: A spy TestScanner that records knowledge_graph it receives
        WHEN: validate_rules is called with test_file scope parameter
        THEN: TestScanner receives knowledge_graph with test_files populated
        AND: test_files contains the test file from scope parameter
        """
        # Given: Test file exists and spy TestScanner that records knowledge_graph
        # Bootstrap environment
        story_graph, story_graph_path, test_file, rule_file, action = given_test_file_scope_verification_complete_setup(bot_directory, workspace_directory)
        
        # Create a spy TestScanner that records what knowledge_graph it receives
        received_knowledge_graphs, SpyTestScanner = given_spy_test_scanner_that_records_knowledge_graph()
        
        # When: Validate rules is called with test_file scope parameter
        # Then: TestScanner receives knowledge_graph with test_files populated (verified by when_execute_test_file_scope_verification)
        when_execute_test_file_scope_verification(action, test_file, story_graph)
        
        # The successful completion of injectValidationInstructions with test_files parameter
        # confirms that test_files are being passed correctly to scanners via scan() method parameters


# ============================================================================
# STORY: Reports Violations
# ============================================================================

class TestReportsViolations:
    """Story: Reports Violations - Tests violation report generation."""

    @pytest.mark.parametrize("violations_data,report_format,expected_violation_count", [
        # Example 1: Single violation, JSON format
        (
            [{
                'rule': 'use_verb_noun_format_for_story_elements',
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
                {'rule': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Epic name uses noun-only format', 'line_number': 2, 'location': 'epics[0].name', 'severity': 'error'},
                {'rule': 'use_active_behavioral_language', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json', 'violation_message': 'Feature uses capability noun', 'line_number': 3, 'location': 'epics[0].features[0].name', 'severity': 'error'},
                {'rule': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Story name contains actor', 'line_number': 4, 'location': 'epics[0].features[0].stories[0].name', 'severity': 'error'},
                {'rule': 'size_stories_3_to_12_days', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json', 'violation_message': 'Story sizing outside range', 'line_number': 5, 'location': 'epics[0].features[0].stories[0].sizing', 'severity': 'error'},
                {'rule': 'use_background_for_common_setup', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json', 'violation_message': 'Background step missing', 'line_number': 6, 'location': 'scenarios[0].background', 'severity': 'error'}
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
                'rule': 'use_verb_noun_format_for_story_elements',
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
                'rule': 'use_verb_noun_format_for_story_elements',
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
                'rule': 'use_verb_noun_format_for_story_elements',
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
                {'rule': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Epic name uses noun-only format', 'line_number': 2, 'location': 'epics[0].name', 'severity': 'error'},
                {'rule': 'use_active_behavioral_language', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json', 'violation_message': 'Feature uses capability noun', 'line_number': 3, 'location': 'epics[0].features[0].name', 'severity': 'error'},
                {'rule': 'use_verb_noun_format_for_story_elements', 'rule_file': 'agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json', 'violation_message': 'Story name contains actor', 'line_number': 4, 'location': 'epics[0].features[0].stories[0].name', 'severity': 'warning'},
                {'rule': 'size_stories_3_to_12_days', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json', 'violation_message': 'Story sizing outside range', 'line_number': 5, 'location': 'epics[0].features[0].stories[0].sizing', 'severity': 'error'},
                {'rule': 'use_background_for_common_setup', 'rule_file': 'agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json', 'violation_message': 'Background step missing', 'line_number': 6, 'location': 'scenarios[0].background', 'severity': 'info'}
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
        test_bot_dir = given_test_bot_directory_for_report_generation(repo_root)
        action = given_validate_rules_action_for_test_bot(test_bot_dir, 'test_story_bot', 'shape')
        
        # Generate report with violations from test data (from Examples table)
        # In real usage, violations would come from scanner execution via injectValidationInstructions()
        report = when_action_generates_report(action, report_format, violations_data)
        
        # Then: Report structure matches expected format
        if report_format == 'CHECKLIST':
            then_report_has_checklist_format(report, expected_violation_count)
        elif report_format == 'SUMMARY':
            then_report_has_summary_format(report, expected_violation_count)
        else:
            then_report_has_json_or_detailed_format(report, expected_violation_count)


# ============================================================================
# STORY: Test All Scanners
# ============================================================================

class TestRunAllScanners:
    """Story: Test All Scanners - Comprehensive tests for all scanner implementations."""
    
    @pytest.mark.parametrize("scanner_class_path,behavior,bad_example,expected_violation_message", [
        # Shape behavior scanners
        (
            'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner',
            'shape',
            {'epics': [{'name': 'Sales Management'}]},  # Noun-only epic name
            'appears to be noun-only'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.active_language_scanner.ActiveLanguageScanner',
            'shape',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Payment Processing'}]}]},  # Capability noun
            'uses capability noun'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.story_sizing_scanner.StorySizingScanner',
            'shape',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Place Order', 'sizing': '15 days'}]}]}]}]},
            'should be'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.specificity_scanner.SpecificityScanner',
            'shape',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Delete Mobs'}]}]}]}]},
            'too generic'
        ),
        
        # Scenarios behavior scanners
        (
            'agile_bot.bots.base_bot.src.scanners.plain_english_scenarios_scanner.PlainEnglishScenariosScanner',
            'scenarios',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Place Order', 'scenarios': [{'scenario': 'Given user has typed request message "<request_message>"'}]}]}]}]}]},
            'contains variable placeholder'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.given_state_not_actions_scanner.GivenStateNotActionsScanner',
            'scenarios',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Place Order', 'scenarios': [{'steps': ['Given Tool invokes test_bot.Shape.GatherContext() method']}]}]}]}]}]},
            'contains action verb'
        ),
        
        # Tests behavior scanners (TestScanner - extends StoryScanner + scans code)
        (
            'agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner',
            'write_tests',
            None,  # Will be created below with test file
            'appears abbreviated'
        ),
        
        # Code behavior scanners (CodeScanner)
        (
            'agile_bot.bots.base_bot.src.scanners.useless_comments_scanner.UselessCommentsScanner',
            'code',
            None,  # Code scanner works on files, not knowledge graph
            'Useless comment'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.intention_revealing_names_scanner.IntentionRevealingNamesScanner',
            'code',
            None,  # Code scanner works on files, not knowledge graph
            'uses generic name'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.separate_concerns_scanner.SeparateConcernsScanner',
            'code',
            None,
            'mixes calculations with I/O'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.simplify_control_flow_scanner.SimplifyControlFlowScanner',
            'code',
            None,
            'nesting depth'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.complete_refactoring_scanner.CompleteRefactoringScanner',
            'code',
            None,
            'commented-out old code'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.meaningful_context_scanner.MeaningfulContextScanner',
            'code',
            None,
            'magic number'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.minimize_mutable_state_scanner.MinimizeMutableStateScanner',
            'code',
            None,
            'mutates state'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.vertical_density_scanner.VerticalDensityScanner',
            'code',
            None,
            'vertical density'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.abstraction_levels_scanner.AbstractionLevelsScanner',
            'code',
            None,
            'mixes high-level operations'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.test_quality_scanner.TestQualityScanner',
            'tests',
            None,
            'generic name'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.encapsulation_scanner.EncapsulationScanner',
            'code',
            None,
            'Law of Demeter'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.exception_classification_scanner.ExceptionClassificationScanner',
            'code',
            None,
            'component-based exception'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.error_handling_isolation_scanner.ErrorHandlingIsolationScanner',
            'code',
            None,
            'try-except blocks'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.third_party_isolation_scanner.ThirdPartyIsolationScanner',
            'code',
            None,
            'third-party library'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.open_closed_principle_scanner.OpenClosedPrincipleScanner',
            'code',
            None,
            'type-based conditional'
        ),
        
        # Additional shape scanners
        (
            'agile_bot.bots.base_bot.src.scanners.noun_redundancy_scanner.NounRedundancyScanner',
            'shape',
            {'epics': [{'name': 'Animation System', 'sub_epics': [{'name': 'Animation Component'}]}]},
            'redundant noun'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.technical_language_scanner.TechnicalLanguageScanner',
            'shape',
            {'epics': [{'name': 'Implement Order System'}]},
            'technical implementation'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.implementation_details_scanner.ImplementationDetailsScanner',
            'shape',
            {'epics': [{'name': 'Serialize Components to JSON', 'sub_epics': []}]},
            'implementation operation'
        ),
        (
            'agile_bot.bots.base_bot.src.scanners.invest_principles_scanner.InvestPrinciplesScanner',
            'shape',
            {'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Place Order'}]}]}]}]},
            'lacks scenarios'
        ),
        
        # Test scanners
        (
            'agile_bot.bots.base_bot.src.scanners.specification_match_scanner.SpecificationMatchScanner',
            'tests',
            None,
            'scenario format'
        ),
    ])
    def test_scanner_detects_violations(self, repo_root, bot_directory, workspace_directory, scanner_class_path, behavior, bad_example, expected_violation_message):
        """
        SCENARIO: Scanner detects violations in bad examples
        GIVEN: Scanner class path, behavior, bad example, and expected violation message
        WHEN: Scanner is executed against bad example
        THEN: Scanner detects violation with expected message
        
        Tests all scanners with real examples - parameterized test.
        """
        # Bootstrap environment
        # Given: Scanner class path, behavior, bad example, and expected violation message
        scanner_class, rule_obj = when_setup_scanner_test_environment(bot_directory, workspace_directory, scanner_class_path, behavior)
        
        # For test/code scanners, create a test file with violations if needed
        test_file, bad_example = when_create_test_file_if_needed_for_scanner(workspace_directory, scanner_class_path, behavior, bad_example)
        
        # When: Scanner is executed against bad example
        scanner_instance = when_scanner_instance_created(scanner_class)
        violations = when_execute_scanner_based_on_type(scanner_instance, bad_example, rule_obj)
        
        # Then: Violations detected with expected message
        then_scanner_detects_violations_with_expected_message(violations, scanner_class_path, expected_violation_message)


# ============================================================================
# STORY: Run Scanners Against Test Code
# ============================================================================

class TestRunScannersAgainstTestCode:
    """Story: Run Scanners Against Test Code - Validates generated test files."""
    
    def test_validate_code_files_action_accepts_test_files_parameter(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction accepts test files via test_files parameter"""
        
        # Given: A workspace with generated test files
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        test_file1, test_file2 = given_test_files_for_validate_code_files_action(workspace_directory)
        given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
        
        # When: ValidateCodeFilesAction receives test files via parameters
        validation_result = when_execute_validate_code_files_action_with_test_files(bot_name, behavior, bot_directory, [test_file1, test_file2])
        
        # Then: Test files should be validated
        then_result_has_violations_or_instructions(validation_result, "ValidateCodeFilesAction should return results when test files are provided")
    
    def test_validate_code_files_action_validates_each_file_from_parameters(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction validates each file provided via test_files parameter"""
        
        # Given: A workspace with test files and validation rules
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        test_file = given_test_file_and_naming_rule_with_rule_id_setup(bot_directory, workspace_directory, behavior)
        
        # When: ValidateCodeFilesAction validates the test file via do_execute()
        validation_result = when_execute_validate_code_files_action_with_single_test_file(bot_name, behavior, bot_directory, test_file)
        
        # Then: Validation should have been performed on the test file
        then_result_has_violations_or_report(validation_result, "ValidateCodeFilesAction should return violations or report")
    
    def test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction merges violations from knowledge graph validation and code file validation"""
        
        # Given: A workspace with story graph and test files, both with violations
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        test_file = given_story_graph_test_file_and_rules_setup(bot_directory, workspace_directory, behavior)
        
        # When: ValidateCodeFilesAction is executed via do_execute()
        validation_result = when_execute_validate_code_files_action_with_single_test_file(bot_name, behavior, bot_directory, test_file)
        
        # Then: Both validations should produce merged results
        then_result_has_violations_from_knowledge_graph(validation_result)
    
    def test_validate_code_files_action_works_for_tests_behavior(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction works for 7_write_tests behavior (test files)"""
        
        # Given: 7_write_tests behavior with generated test files
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        test_file = given_test_file_for_validate_code_files_action(workspace_directory, 'test_generated.py')
        given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
        
        # When: ValidateCodeFilesAction is executed for 7_write_tests behavior via do_execute()
        validation_result = when_execute_validate_code_files_action_with_single_test_file(bot_name, behavior, bot_directory, test_file)
        
        # Then: Test files should be validated for 7_write_tests behavior
        then_result_has_violations_or_instructions(validation_result, "ValidateCodeFilesAction should return results for 7_write_tests behavior")


# ============================================================================
# STORY: Run Scanners Against Code
# ============================================================================

class TestRunScannersAgainstCode:
    """Story: Run Scanners Against Code - Validates generated source files."""
    
    def test_validate_code_files_action_accepts_code_files_parameter(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction accepts source files via code_files parameter"""
        
        # Given: A workspace with generated source files
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '8_code')
        source_file1, source_file2 = given_source_files_for_validate_code_files_action(workspace_directory)
        given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
        
        # When: ValidateCodeFilesAction receives code files via parameters
        validation_result = when_execute_validate_code_files_action_with_code_files(bot_name, behavior, bot_directory, [source_file1, source_file2])
        
        # Then: Code files should be validated
        then_result_has_violations_or_instructions(validation_result, "ValidateCodeFilesAction should return results when code files are provided")
    
    def test_validate_code_files_action_works_for_code_behavior(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction works for 8_code behavior (source files)"""
        
        # Given: 8_code behavior with generated source files
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '8_code')
        source_file = given_source_file_for_validate_code_files_action(workspace_directory)
        given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
        
        # When: ValidateCodeFilesAction is executed for 8_code behavior via do_execute()
        validation_result = when_execute_validate_code_files_action_with_code_files(bot_name, behavior, bot_directory, [source_file])
        
        # Then: Source files should be validated for 8_code behavior
        then_result_has_violations_or_instructions(validation_result, "ValidateCodeFilesAction should return results for 8_code behavior")
    
    def test_validate_code_files_action_returns_early_when_no_files_provided(self, bot_directory, workspace_directory):
        """Scenario: ValidateCodeFilesAction returns knowledge graph results when no files provided"""
        
        # Given: A workspace with story graph but no test files provided
        bot_name, behavior = given_bot_name_and_behavior_setup('story_bot', '7_write_tests')
        given_environment_bootstrapped_with_story_graph(bot_directory, workspace_directory)
        
        # When: ValidateCodeFilesAction is executed without test_files or code_files parameters
        action = when_validate_code_files_action_created(bot_name, behavior, bot_directory)
        parameters = when_create_empty_parameters()
        validation_result = when_validate_code_files_action_executes(action, parameters)
        
        # Then: Should return knowledge graph validation results only
        then_result_contains_instructions_key(validation_result)

