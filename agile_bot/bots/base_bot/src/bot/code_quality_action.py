"""Code quality action - automatically runs CodeScanner instances."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .validate_rules_action import ValidateRulesAction, Rule
from agile_bot.bots.base_bot.src.scanners.code_scanner import CodeScanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation


class CodeQualityAction(ValidateRulesAction):
    """Action that automatically runs CodeScanner instances.
    
    This action filters rules to only those with CodeScanner instances and
    automatically discovers code files if not provided in parameters.
    """
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory)
        self.action_name = 'code_quality'
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code quality action logic."""
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
                f"Expected story graph to be created by build_knowledge action before code_quality."
            )
        
        if not story_graph_path.exists():
            raise FileNotFoundError(
                f"Story graph file not found at {story_graph_path}. "
                f"Cannot validate rules without story graph. "
                f"Expected story graph to be created by build_knowledge action before code_quality."
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
        
        # Auto-discover code files if not provided
        code_files_to_scan = []
        if parameters and 'code_files' in parameters:
            code_files_list = parameters['code_files']
            if code_files_list:
                if not isinstance(code_files_list, list):
                    code_files_list = [code_files_list]
                code_files_to_scan = [str(Path(cf)) if isinstance(cf, str) else str(cf) for cf in code_files_list]
        
        # Auto-discover code files if not provided
        if not code_files_to_scan:
            project_location = content_info.get('project_location')
            if project_location:
                project_path = Path(project_location)
                # Look for source code directories
                src_dirs = [
                    project_path / 'src',
                    project_path,
                    project_path / 'lib',
                    project_path / 'app'
                ]
                for src_dir in src_dirs:
                    if src_dir.exists() and src_dir.is_dir():
                        # Find all Python files (excluding test files)
                        discovered_code = [
                            f for f in src_dir.rglob('*.py')
                            if not f.name.startswith('test_') and 'test' not in str(f)
                        ]
                        if discovered_code:
                            code_files_to_scan.extend([str(cf) for cf in discovered_code[:100]])  # Limit to first 100 files
                            break
        
        # Resolve code file paths
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
        
        code_file_paths = []
        if code_files_to_scan:
            for cf in code_files_to_scan:
                code_path = Path(cf)
                if code_path.is_absolute():
                    code_file_paths.append(code_path)
                else:
                    if repo_root:
                        resolved_path = repo_root / code_path
                        code_file_paths.append(resolved_path)
                    else:
                        resolved_path = self.workspace_directory / code_path
                        code_file_paths.append(resolved_path)
        
        # Run scanners with story graph and code files (only CodeScanner instances)
        result = self.injectValidationInstructions(
            story_graph, 
            test_files=None,  # Never pass test_files to code_quality
            code_files=code_file_paths if code_file_paths else None,
            scanner_filter=lambda scanner_class: issubclass(scanner_class, CodeScanner)
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
            test_files: Not used by CodeQualityAction (always None)
            code_files: Optional list of code file paths (auto-discovered if not provided)
            scanner_filter: Function to filter scanner classes (default: CodeScanner only)
            
        Returns:
            Dictionary with 'instructions' containing rules with scanner_results
        """
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Default filter: only CodeScanner instances
        if scanner_filter is None:
            scanner_filter = lambda scanner_class: issubclass(scanner_class, CodeScanner)
        
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
                rule_result['scanner_results'] = {
                    'file_by_file': {'violations': []},
                    'cross_file': {'violations': []}
                }
                
                if scanner_path:
                    scanner_class, error_msg = self._load_scanner_class(scanner_path)
                    if scanner_class:
                        # Only run scanners that match the filter (CodeScanner instances)
                        if scanner_filter(scanner_class):
                            try:
                                scanner_instance = scanner_class()
                                
                                # PASS 1: File-by-file scanning
                                violations_file_by_file = scanner_instance.scan(
                                    knowledge_graph, 
                                    rule_obj=rule_obj,
                                    test_files=None,  # Never pass test_files
                                    code_files=code_files
                                )
                                violations_list_file = violations_file_by_file if isinstance(violations_file_by_file, list) else []
                                
                                violations_dicts_file = []
                                for violation in violations_list_file:
                                    if isinstance(violation, Violation):
                                        violation_dict = violation.to_dict()
                                        violations_dicts_file.append(violation_dict)
                                    elif isinstance(violation, dict):
                                        if 'rule' not in violation:
                                            violation['rule'] = rule_obj.name
                                        if 'rule_file' not in violation:
                                            violation['rule_file'] = rule_obj.rule_file
                                        violations_dicts_file.append(violation)
                                
                                self._violations.extend(violations_dicts_file)
                                rule_result['scanner_results']['file_by_file']['violations'] = violations_dicts_file
                                
                                # PASS 2: Cross-file scanning (if files provided)
                                if code_files and hasattr(scanner_instance, 'scan_cross_file'):
                                    violations_cross_file = scanner_instance.scan_cross_file(
                                        knowledge_graph,
                                        rule_obj=rule_obj,
                                        test_files=None,
                                        code_files=code_files
                                    )
                                    violations_list_cross = violations_cross_file if isinstance(violations_cross_file, list) else []
                                    
                                    violations_dicts_cross = []
                                    for violation in violations_list_cross:
                                        if isinstance(violation, Violation):
                                            violation_dict = violation.to_dict()
                                            violations_dicts_cross.append(violation_dict)
                                        elif isinstance(violation, dict):
                                            if 'rule' not in violation:
                                                violation['rule'] = rule_obj.name
                                            if 'rule_file' not in violation:
                                                violation['rule_file'] = rule_obj.rule_file
                                            violation['_pass'] = 'cross_file'
                                            violations_dicts_cross.append(violation)
                                    
                                    self._violations.extend(violations_dicts_cross)
                                    rule_result['scanner_results']['cross_file']['violations'] = violations_dicts_cross
                                
                            except Exception as e:
                                logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
                                rule_file = rule_dict.get('rule_file', 'unknown')
                                scanner_path = rule_content.get('scanner', 'unknown')
                                from .validate_rules_action import ScannerExecutionError
                                raise ScannerExecutionError(rule_file, scanner_path, e) from e
                        else:
                            # Scanner doesn't match filter - skip it
                            rule_result['scanner_results'] = {
                                'file_by_file': {'violations': []},
                                'cross_file': {'violations': []},
                                'skipped': f"Scanner is not a CodeScanner instance"
                            }
                    else:
                        rule_result['scanner_results'] = {
                            'file_by_file': {'violations': [], 'error': error_msg},
                            'cross_file': {'violations': []}
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
                "Based on code quality scanner diagnostics, edit the knowledge graph to fix violations:",
                *violation_summary,
                "Review each violation and update the knowledge graph accordingly."
            ]
            action_instructions.extend(edit_instructions)
        
        instructions = {
            'action': 'code_quality',
            'behavior': self.behavior,
            'base_instructions': action_instructions,
            'validation_rules': processed_rules,
            'content_to_validate': self._identify_content_to_validate()
        }
        
        return {'instructions': instructions}

