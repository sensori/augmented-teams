"""Test validation action - automatically runs TestScanner instances."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .validate_rules_action import ValidateRulesAction, Rule
from agile_bot.bots.base_bot.src.scanners.test_scanner import TestScanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation


class TestValidateAction(ValidateRulesAction):
    """Action that automatically runs TestScanner instances.
    
    This action filters rules to only those with TestScanner instances and
    automatically discovers test files if not provided in parameters.
    """
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory)
        self.action_name = 'test_validate'
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test validation action logic."""
        # Identify content to validate
        content_info = self._identify_content_to_validate()
        
        # Load story graph to run scanners - REQUIRED, no fallback
        story_graph_path = None
        for output in content_info.get('rendered_outputs', []):
            if 'story-graph.json' in output:
                story_graph_path = Path(output)
                break
        
        if not story_graph_path:
            raise FileNotFoundError(
                f"Story graph file (story-graph.json) not found in rendered outputs. "
                f"Cannot validate rules without story graph. "
                f"Expected story graph to be created by build_knowledge action before test_validate."
            )
        
        if not story_graph_path.exists():
            raise FileNotFoundError(
                f"Story graph file not found at {story_graph_path}. "
                f"Cannot validate rules without story graph. "
                f"Expected story graph to be created by build_knowledge action before test_validate."
            )
        
        # Load story graph
        from agile_bot.bots.base_bot.src.utils import read_json_file
        story_graph = read_json_file(story_graph_path)
        
        # Extract scope from parameters
        scope_config = {}
        if parameters:
            # Support explicit story names list
            if 'story_names' in parameters:
                scope_config['story_names'] = parameters['story_names']
            
            # Support multiple increment priorities
            if 'increment_priorities' in parameters:
                scope_config['increment_priorities'] = parameters['increment_priorities']
            
            # Support multiple epic names
            if 'epic_names' in parameters:
                scope_config['epic_names'] = parameters['epic_names']
            
            # Support 'all' flag
            if parameters.get('validate_all') is True:
                scope_config['all'] = True
        
        # Add scope to story_graph
        if scope_config:
            story_graph['_validation_scope'] = scope_config
        
        # Auto-discover test files if not provided
        test_files_to_scan = []
        if parameters and 'test_files' in parameters:
            test_files_list = parameters['test_files']
            if test_files_list:
                if not isinstance(test_files_list, list):
                    test_files_list = [test_files_list]
                test_files_to_scan = [str(Path(tf)) if isinstance(tf, str) else str(tf) for tf in test_files_list]
        
        # Auto-discover test files if not provided
        if not test_files_to_scan:
            project_location = content_info.get('project_location')
            if project_location:
                project_path = Path(project_location)
                # Look for test directories
                test_dirs = [project_path / 'test', project_path / 'tests']
                for test_dir in test_dirs:
                    if test_dir.exists() and test_dir.is_dir():
                        # Find all test_*.py files
                        discovered_tests = list(test_dir.glob('test_*.py'))
                        if discovered_tests:
                            test_files_to_scan.extend([str(tf) for tf in discovered_tests])
                            break
        
        # Resolve test file paths
        project_location = content_info.get('project_location')
        workspace_path = Path(project_location) if project_location else self.workspace_directory
        
        # Find repo root
        repo_root = None
        current = workspace_path.resolve()
        for i in range(10):
            if (current / '.git').exists() or (current / 'agile_bot').exists():
                repo_root = current
                break
            if current.parent == current:
                break
            current = current.parent
        
        if not repo_root:
            workspace_str = str(workspace_path.resolve())
            if 'demo' in workspace_str:
                parts = workspace_path.resolve().parts
                if 'demo' in parts:
                    demo_idx = parts.index('demo')
                    repo_root = Path(*parts[:demo_idx]) if demo_idx > 0 else workspace_path.resolve().parent
                else:
                    repo_root = workspace_path.resolve().parent
            else:
                repo_root = workspace_path.resolve().parent
        
        test_file_paths = []
        if test_files_to_scan:
            for tf in test_files_to_scan:
                test_path = Path(tf)
                if test_path.is_absolute():
                    test_file_paths.append(test_path)
                else:
                    if repo_root:
                        resolved_path = repo_root / test_path
                        test_file_paths.append(resolved_path)
                    else:
                        resolved_path = self.workspace_directory / test_path
                        test_file_paths.append(resolved_path)
        
        # Run scanners with story graph and test files (only TestScanner instances)
        result = self.injectValidationInstructions(
            story_graph, 
            test_files=test_file_paths if test_file_paths else None,
            code_files=None,  # Never pass code_files to test_validate
            scanner_filter=lambda scanner_class: issubclass(scanner_class, TestScanner)
        )
        
        # Write validation report
        report_path = content_info.get('report_path')
        if report_path:
            try:
                instructions = result.get('instructions', {})
                validation_rules = instructions.get('validation_rules', [])
                self._write_validation_report(report_path, instructions, validation_rules, content_info)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to write validation report to {report_path}: {e}", exc_info=True)
        
        return result
    
    def injectValidationInstructions(
        self, 
        knowledge_graph: Dict[str, Any], 
        test_files: Optional[List[Path]] = None, 
        code_files: Optional[List[Path]] = None,
        scanner_filter=None
    ) -> Dict[str, Any]:
        """Inject validation instructions with scanner results, filtering by scanner type.
        
        Args:
            knowledge_graph: The knowledge graph to validate against
            test_files: Optional list of test file paths (auto-discovered if not provided)
            code_files: Not used by TestValidateAction (always None)
            scanner_filter: Function to filter scanner classes (default: TestScanner only)
            
        Returns:
            Dictionary with 'instructions' containing rules with scanner_results
        """
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Default filter: only TestScanner instances
        if scanner_filter is None:
            scanner_filter = lambda scanner_class: issubclass(scanner_class, TestScanner)
        
        # Process each rule: run scanner if exists and matches filter, add results
        processed_rules = []
        for idx, rule_dict in enumerate(validation_rules):
            if isinstance(rule_dict, dict):
                rule_content = rule_dict.get('rule_content', rule_dict)
                scanner_path = rule_content.get('scanner')
                
                # Create Rule object for this rule
                rule_file = rule_dict.get('rule_file', 'unknown.json')
                behavior_name = 'common'
                if '/behaviors/' in rule_file:
                    parts = rule_file.split('/behaviors/')
                    if len(parts) > 1:
                        behavior_part = parts[1].split('/')[0]
                        if '_' in behavior_part:
                            behavior_name = behavior_part.split('_', 1)[1]
                
                rule_obj = Rule(rule_file, rule_content, behavior_name)
                
                rule_result = dict(rule_dict)  # Copy rule
                rule_result['scanner_results'] = {}
                
                if scanner_path:
                    scanner_class, error_msg = self._load_scanner_class(scanner_path)
                    if scanner_class:
                        # Only run scanners that match the filter (TestScanner instances)
                        if scanner_filter(scanner_class):
                            # Run scanner against knowledge graph
                            try:
                                scanner_instance = scanner_class()
                                
                                # Pass test_files to scanners (never code_files for test validation)
                                violations = scanner_instance.scan(
                                    knowledge_graph, 
                                    rule_obj=rule_obj,
                                    test_files=test_files,
                                    code_files=None  # Never pass code_files
                                )
                                violations_list = violations if isinstance(violations, list) else []
                                
                                # Convert violations to dictionaries if they're Violation objects
                                violations_dicts = []
                                
                                for violation in violations_list:
                                    if isinstance(violation, Violation):
                                        violation_dict = violation.to_dict()
                                        violations_dicts.append(violation_dict)
                                    elif isinstance(violation, dict):
                                        if 'rule' not in violation:
                                            violation['rule'] = rule_obj.name
                                        if 'rule_file' not in violation:
                                            violation['rule_file'] = rule_obj.rule_file
                                        violations_dicts.append(violation)
                                
                                # Store violations in action instance for report generation
                                self._violations.extend(violations_dicts)
                                
                                rule_result['scanner_results'] = {
                                    'violations': violations_dicts
                                }
                            except Exception as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
                                
                                rule_file = rule_dict.get('rule_file', 'unknown')
                                scanner_path = rule_content.get('scanner', 'unknown')
                                from .validate_rules_action import ScannerExecutionError
                                raise ScannerExecutionError(rule_file, scanner_path, e) from e
                        else:
                            # Scanner doesn't match filter - skip it
                            rule_result['scanner_results'] = {
                                'violations': [],
                                'skipped': f"Scanner is not a TestScanner instance"
                            }
                    else:
                        rule_result['scanner_results'] = {
                            'violations': [],
                            'error': error_msg
                        }
                
                processed_rules.append(rule_result)
        
        # Add instructions to edit knowledge graph based on violations
        violation_summary = []
        for rule in processed_rules:
            scanner_results = rule.get('scanner_results', {})
            violations = scanner_results.get('violations', [])
            if violations:
                violation_summary.append(f"Rule {rule.get('rule_file', 'unknown')}: {len(violations)} violations")
        
        if violation_summary:
            edit_instructions = [
                "Based on test scanner diagnostics, edit the knowledge graph to fix violations:",
                *violation_summary,
                "Review each violation and update the knowledge graph accordingly."
            ]
            action_instructions.extend(edit_instructions)
        
        instructions = {
            'action': 'test_validate',
            'behavior': self.behavior,
            'base_instructions': action_instructions,
            'validation_rules': processed_rules,
            'content_to_validate': self._identify_content_to_validate()
        }
        
        return {'instructions': instructions}

