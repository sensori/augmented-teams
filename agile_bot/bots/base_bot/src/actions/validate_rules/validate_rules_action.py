from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.scanners.violation import Violation
from agile_bot.bots.base_bot.src.bot.rule import Rule
from agile_bot.bots.base_bot.src.bot.rules import Rules
from agile_bot.bots.base_bot.src.bot.scanner_loader import ScannerLoader

logger = logging.getLogger(__name__)


class ScannerExecutionError(Exception):
    """Exception raised when a scanner crashes during execution.
    
    Provides context about which scanner/rule failed so the error can be reported
    back to the user with full details.
    """
    def __init__(self, rule_file: str, scanner_path: str, original_error: Exception):
        self.rule_file = rule_file
        self.scanner_path = scanner_path
        self.original_error = original_error
        message = (
            f"Scanner execution failed for rule '{rule_file}' "
            f"(scanner: {scanner_path}): {original_error}"
        )
        super().__init__(message)


class ValidateRulesAction(Action):
    """Validate rules action for validating content against rules.
    
    Domain Model:
        Instantiated with: Behavior
        Properties: rules, validation_context, validation_scope
    """
    
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = 'validate_rules'):
        """Initialize ValidateRulesAction.
        
        Supports both signatures:
        - New: (base_action_config, behavior, activity_tracker)
        - Old: (bot_name, behavior, action_name) for backward compatibility
        """
        super().__init__(base_action_config=base_action_config, behavior=behavior,
                        activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        self._violations = []  # Store violations from scanner execution
        
        # Instantiate Rules collection
        if self.behavior:
            self._rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths if self.behavior else None)
        else:
            self._rules = None
    
    @property
    def rules(self) -> Optional[Rules]:
        """Get Rules collection.
        
        Domain Model: rules: Rules
        """
        if self._rules is None and self.behavior:
            self._rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths if self.behavior else None)
        return self._rules
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate_rules action logic."""
        logger.info("=== validate_rules action START ===")
        logger.info(f"Parameters: {parameters}")
        try:
            # Identify content to validate
            logger.info("Step 1: Identifying content to validate...")
            content_info = self._identify_content_to_validate()
            logger.info(f"Content info identified: {list(content_info.keys())}")
            
            # Load story graph to run scanners - REQUIRED, no fallback
            logger.info("Step 2: Loading story graph...")
            story_graph_path = None
            for output in content_info.get('rendered_outputs', []):
                if 'story-graph.json' in output:
                    story_graph_path = Path(output)
                    break
            
            if not story_graph_path:
                logger.error("Story graph not found in rendered outputs")
                raise FileNotFoundError(
                    f"Story graph file (story-graph.json) not found in rendered outputs. "
                    f"Cannot validate rules without story graph. "
                    f"Expected story graph to be created by build_knowledge action before validate_rules."
                )
            
            logger.info(f"Story graph path: {story_graph_path}")
            if not story_graph_path.exists():
                logger.error(f"Story graph file does not exist at {story_graph_path}")
                raise FileNotFoundError(
                    f"Story graph file not found at {story_graph_path}. "
                    f"Cannot validate rules without story graph. "
                    f"Expected story graph to be created by build_knowledge action before validate_rules."
                )
            
            # Load story graph - if file exists, loading MUST succeed
            # This ensures syntax errors are reported, not hidden
            logger.info("Step 3: Reading story graph JSON file...")
            story_graph = read_json_file(story_graph_path)
            logger.info("Story graph loaded successfully")
            
            # Extract scope from parameters and add to story_graph for scanners
            logger.info("Step 4: Processing parameters and scope config...")
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
            
            # Support test_file as scope parameter (one-off validation, not persisted)
            if 'test_file' in parameters:
                test_file_path = parameters['test_file']
                if test_file_path:
                    # Convert to Path if string
                    if isinstance(test_file_path, str):
                        test_file_path = Path(test_file_path)
                    scope_config['test_file'] = str(test_file_path)
            
            # Support test_files (plural) as scope parameter - list of test files to validate
            if 'test_files' in parameters:
                logger.info(f"Processing test_files parameter: {parameters['test_files']}")
                test_files_list = parameters['test_files']
                if test_files_list:
                    # Ensure it's a list
                    if not isinstance(test_files_list, list):
                        test_files_list = [test_files_list]
                    # Convert all to strings and normalize to forward slashes to avoid escape sequence issues
                    logger.info(f"Converting {len(test_files_list)} test files to normalized paths...")
                    scope_config['test_files'] = [str(Path(tf)).replace('\\', '/') if isinstance(tf, str) else str(Path(tf)).replace('\\', '/') for tf in test_files_list]
                    logger.info(f"Normalized test_files: {scope_config['test_files']}")
            
            # Support code_files as scope parameter - list of code files to validate (for CodeScanner)
            if 'code_files' in parameters:
                code_files_list = parameters['code_files']
                if code_files_list:
                    # Ensure it's a list
                    if not isinstance(code_files_list, list):
                        code_files_list = [code_files_list]
                    # Convert all to strings and normalize to forward slashes to avoid escape sequence issues
                    scope_config['code_files'] = [str(Path(cf)).replace('\\', '/') if isinstance(cf, str) else str(Path(cf)).replace('\\', '/') for cf in code_files_list]
            
            # Support 'all' flag
            if parameters.get('validate_all') is True:
                scope_config['all'] = True
            
            # Add scope to story_graph (scanners will read this)
            if scope_config:
                story_graph['_validation_scope'] = scope_config
            
            # Extract test files from scope for TestScanner (one-off, add to temporary copy only)
            test_files_to_scan = []
            if scope_config.get('test_file'):
                test_files_to_scan.append(scope_config['test_file'])
            if scope_config.get('test_files'):
                test_files_to_scan.extend(scope_config['test_files'])
            
            # Auto-discover test files if not provided and we're in 7_write_tests behavior
            if not test_files_to_scan and self.behavior.name == '7_write_tests':
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
            
            # Extract code files from scope for CodeScanner (one-off, add to temporary copy only)
            code_files_to_scan = []
            if scope_config.get('code_files'):
                code_files_to_scan.extend(scope_config['code_files'])
            
            # Convert to Path objects for processing, resolving relative paths
            # Test file paths are typically relative to repo root (e.g., demo/mob_minion/test/file.py)
            # Workspace is typically a subdirectory (e.g., demo/mob_minion)
            # So we need to resolve against repo root, not workspace root
            project_location = content_info.get('project_location')
            workspace_path = Path(project_location) if project_location else self.workspace_directory
            
            # Find repo root by looking for common markers (starting from workspace and going up)
            repo_root = None
            current = workspace_path.resolve()  # Resolve to absolute path first
            
            for i in range(10):  # Look up to 10 levels up
                if (current / '.git').exists() or (current / 'agile_bot').exists():
                    repo_root = current
                    break
                if current.parent == current:  # Reached filesystem root
                    break
                current = current.parent
            
            # Fallback: use workspace's absolute path parent if we're in a demo subdirectory
            if not repo_root:
                # If workspace path ends with something like 'demo/mob_minion', 
                # and test file path starts with 'demo/mob_minion/test/...',
                # then repo root should be the parent of the 'demo' directory
                workspace_str = str(workspace_path.resolve())
                if 'demo' in workspace_str:
                    # Find where 'demo' appears and use that as a hint
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
                    # If absolute path, use as-is
                    if test_path.is_absolute():
                        test_file_paths.append(test_path)
                    else:
                        # Always resolve against repo root (test files are relative to repo root)
                        if repo_root:
                            resolved_path = repo_root / test_path
                            test_file_paths.append(resolved_path)
                        else:
                            # Fallback: resolve against workspace (shouldn't happen if repo_root detection works)
                            resolved_path = self.workspace_directory / test_path
                            test_file_paths.append(resolved_path)
            
            code_file_paths = []
            if code_files_to_scan:
                for cf in code_files_to_scan:
                    code_path = Path(cf)
                    # If absolute path, use as-is
                    if code_path.is_absolute():
                        code_file_paths.append(code_path)
                    else:
                        # Always resolve against repo root (code files are relative to repo root)
                        if repo_root:
                            resolved_path = repo_root / code_path
                            code_file_paths.append(resolved_path)
                        else:
                            # Fallback: resolve against workspace
                            resolved_path = self.workspace_directory / code_path
                            code_file_paths.append(resolved_path)
        
            # Run scanners with story graph and optional test/code files (one-off, not persisted)
            logger.info("Step 5: Running scanners via injectValidationInstructions...")
            logger.info(f"Test files to scan: {test_file_paths}")
            logger.info(f"Code files to scan: {code_file_paths}")
            result = self.injectValidationInstructions(story_graph, test_files=test_file_paths, code_files=code_file_paths)
            logger.info("Scanners completed successfully")
            
            # Write validation report with scanner results
            logger.info("Step 6: Preparing to write validation report...")
            report_path = content_info.get('report_path')
            logger.info(f"Report path: {report_path}")
            if report_path:
                logger.info("Step 7: Extracting instructions and validation rules from result...")
                instructions = result.get('instructions', {})
                validation_rules = instructions.get('validation_rules', [])
                logger.info(f"Found {len(validation_rules)} validation rules")
                
                # Add test files and code files to content_info for report
                if test_file_paths:
                    content_info['test_files_scanned'] = [str(tf) for tf in test_file_paths]
                if code_file_paths:
                    content_info['code_files_scanned'] = [str(cf) for cf in code_file_paths]
                
                logger.info("Step 8: Calling _write_validation_report...")
                logger.info(f"Report path: {report_path}")
                logger.info(f"Instructions keys: {list(instructions.keys())}")
                logger.info(f"Content info keys: {list(content_info.keys())}")
                self._write_validation_report(report_path, instructions, validation_rules, content_info)
                logger.info("Report written successfully")
            else:
                logger.warning("No report_path in content_info, skipping report writing")
            
            logger.info("=== validate_rules action COMPLETE ===")
            return result
        except Exception as e:
            # Log error with full context to help debug regex errors
            import traceback
            logger.error("=== ERROR in validate_rules action ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            # Re-raise with full context
            error_msg = (
                f"Error in validate_rules action: {e}\n"
                f"Parameters: {parameters}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise RuntimeError(error_msg) from e
    
    def inject_common_bot_rules(self) -> Dict[str, Any]:
        """Load common bot-level rules from base_bot/rules/ directory."""
        base_bot_rules_dir = self.bot_dir.parent / 'base_bot' / 'rules'
        
        common_rules = []
        if base_bot_rules_dir.exists() and base_bot_rules_dir.is_dir():
            for rule_file in base_bot_rules_dir.glob('*.json'):
                rule_data = read_json_file(rule_file)
                common_rules.append({
                    'rule_file': f'agile_bot/bots/base_bot/rules/{rule_file.name}',
                    'rule_content': rule_data
                })
        
        return {
            'validation_rules': common_rules
        }
    
    def inject_behavior_specific_and_bot_rules(self) -> Dict[str, Any]:
        """Load behavior-specific and bot-level rules.
        
        Uses Rules collection to load rules, then converts to legacy format for backward compatibility.
        """
        # Load action-specific instructions from base_actions
        action_instructions = []
        base_actions_path = self.base_actions_dir
        
        # Action folders no longer have number prefixes
        config_path = base_actions_path / 'validate_rules' / 'action_config.json'
        
        if config_path.exists():
            config = read_json_file(config_path)
            action_instructions = config.get('instructions', [])
        
        # Use Rules collection to load rules
        if not self.rules:
            return {
                'action_instructions': action_instructions,
                'validation_rules': []
            }
        
        # Convert Rule objects to legacy dict format for backward compatibility
        validation_rules = []
        for rule in self.rules.iterate():
            validation_rules.append({
                'rule_file': rule.rule_file,
                'rule_content': rule.rule_content
            })
        
        return {
            'action_instructions': action_instructions,
            'validation_rules': validation_rules
        }
    
    def inject_next_action_instructions(self):
        return ""  # Empty string for terminal action
    
    def _identify_content_to_validate(self) -> Dict[str, Any]:
        """Identify what content needs to be validated from the project."""
        # Use workspace_directory property which gets path from workspace tool/environment
        project_dir = self.workspace_directory
        content_info = {
            'project_location': str(project_dir),
            'rendered_outputs': [],
            'clarification_file': None,
            'planning_file': None,
            'report_path': None
        }
        
        # Find docs_path from behavior config or default
        # Get documentation path from bot_paths
        docs_path = self.behavior.bot.bot_paths.documentation_path
        
        # Build docs directory path relative to workspace directory
        docs_dir = project_dir / docs_path
        
        # Find clarification.json and planning.json
        clarification_file = docs_dir / 'clarification.json'
        planning_file = docs_dir / 'planning.json'
        
        if clarification_file.exists():
            content_info['clarification_file'] = str(clarification_file)
        if planning_file.exists():
            content_info['planning_file'] = str(planning_file)
        
        # Set validation report path using workspace directory (where AI should save the report)
        report_file = docs_dir / 'validation-report.md'
        content_info['report_path'] = str(report_file)
        
        # Find rendered outputs (story maps, domain models, etc.)
        if docs_dir.exists():
            # Look for common rendered output files
            rendered_patterns = [
                '*-story-map.md',
                '*-domain-model-description.md',
                '*-domain-model-diagram.md',
                'story-graph.json',
                '*-increments.md'
            ]
            for pattern in rendered_patterns:
                for file_path in docs_dir.glob(pattern):
                    content_info['rendered_outputs'].append(str(file_path))
        
        return content_info
    
    def discover_scanners(self) -> Dict[str, Any]:
        """Discover scanners from loaded rules.
        
        Returns:
            Dictionary with 'scanners' (list of scanner classes), 'errors' (list of error messages)
        """
        if not self.rules:
            return {
                'scanners': [],
                'errors': []
            }
        
        scanners = []
        errors = []
        
        for rule in self.rules.iterate():
            scanner = rule.scanner
            if scanner:
                scanners.append(scanner)
            elif rule.scanner_path:
                # Scanner failed to load - error was already logged during Rule creation
                errors.append(f"Scanner failed to load for rule {rule.rule_file}: {rule.scanner_path}")
        
        return {
            'scanners': scanners,
            'errors': errors
        }
    
    def injectValidationInstructions(self, knowledge_graph: Dict[str, Any], test_files: Optional[List[Path]] = None, code_files: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Inject validation instructions with scanner results.
        
        For each rule: inject rule, run scanner (if exists), add results to rule.
        Adds instructions to edit built knowledge based on code diagnostics.
        
        Args:
            knowledge_graph: The knowledge graph to validate against
            test_files: Optional list of test file paths for validation (passed directly to scanners)
            code_files: Optional list of code file paths for validation (passed directly to scanners)
            
        Returns:
            Dictionary with 'instructions' containing rules with scanner_results
        """
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Process each rule: run scanner if exists, add results
        # TWO-PASS SYSTEM: First pass (file-by-file), then second pass (cross-file)
        processed_rules = []
        
        # Use Rules collection to get Rule objects
        rule_objects = []
        if self.rules:
            rule_objects = list(self.rules.iterate())
        
        # Map rule_file to Rule object for quick lookup
        rule_by_file = {rule.rule_file: rule for rule in rule_objects}
        
        for idx, rule_dict in enumerate(validation_rules):
            if isinstance(rule_dict, dict):
                rule_file = rule_dict.get('rule_file', 'unknown.json')
                
                # Get Rule object from collection (already has scanner loaded)
                rule_obj = rule_by_file.get(rule_file)
                if not rule_obj:
                    # Fallback: create Rule object from dict (shouldn't happen if Rules collection is working)
                    rule_content = rule_dict.get('rule_content', rule_dict)
                    behavior_name = 'common'
                    if '/behaviors/' in rule_file:
                        parts = rule_file.split('/behaviors/')
                        if len(parts) > 1:
                            behavior_name = parts[1].split('/')[0]
                    scanner_loader = ScannerLoader(self.bot_name)
                    scanner = scanner_loader.load_scanner(rule_content.get('scanner')) if rule_content.get('scanner') else None
                    rule_obj = Rule(rule_file, rule_content, behavior_name, scanner)
                
                rule_result = dict(rule_dict)  # Copy rule
                
                # Check scanner type to determine format
                from agile_bot.bots.base_bot.src.scanners.test_scanner import TestScanner
                from agile_bot.bots.base_bot.src.scanners.code_scanner import CodeScanner
                
                scanner_class = rule_obj.scanner if rule_obj else None
                scanner_path = rule_obj.scanner_path if rule_obj else None
                
                is_test_or_code_scanner = (
                    scanner_class and (
                        issubclass(scanner_class, TestScanner) or 
                        issubclass(scanner_class, CodeScanner)
                    )
                )
                
                # Use two-pass format only for TestScanner and CodeScanner
                if is_test_or_code_scanner:
                    rule_result['scanner_results'] = {
                        'file_by_file': {'violations': []},
                        'cross_file': {'violations': []}
                    }
                else:
                    # Old format for StoryScanner and other scanners
                    rule_result['scanner_results'] = {}
                
                if scanner_path and scanner_class:
                    try:
                        scanner_instance = scanner_class()
                        
                        # PASS 1: File-by-file scanning (current behavior)
                        logger.info(f"Running file-by-file scan for rule: {rule_file}")
                        violations_file_by_file = scanner_instance.scan(
                            knowledge_graph, 
                            rule_obj=rule_obj,
                            test_files=test_files,
                            code_files=code_files
                        )
                        violations_list_file = violations_file_by_file if isinstance(violations_file_by_file, list) else []
                        
                        # Convert violations to dictionaries
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
                        
                        # Store violations based on scanner type
                        self._violations.extend(violations_dicts_file)
                        
                        if is_test_or_code_scanner:
                            # Two-pass format
                            rule_result['scanner_results']['file_by_file']['violations'] = violations_dicts_file
                        else:
                            # Old format (for StoryScanner and others)
                            rule_result['scanner_results']['violations'] = violations_dicts_file
                        
                        # PASS 2: Cross-file scanning (ONLY for TestScanner and CodeScanner)
                        if is_test_or_code_scanner and (test_files or code_files) and hasattr(scanner_instance, 'scan_cross_file'):
                            logger.info(f"Running cross-file scan for rule: {rule_file}")
                            violations_cross_file = scanner_instance.scan_cross_file(
                                rule_obj=rule_obj,
                                test_files=test_files,
                                code_files=code_files
                            )
                            violations_list_cross = violations_cross_file if isinstance(violations_cross_file, list) else []
                            
                            # Convert violations to dictionaries
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
                                    # Mark as cross-file violation
                                    violation['_pass'] = 'cross_file'
                                    violations_dicts_cross.append(violation)
                            
                            # Store cross-file violations separately
                            self._violations.extend(violations_dicts_cross)
                            rule_result['scanner_results']['cross_file']['violations'] = violations_dicts_cross
                    
                    except Exception as e:
                        # Log the error for debugging
                        logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
                        
                        # Raise exception with context - don't swallow scanner crashes
                        rule_file = rule_dict.get('rule_file', 'unknown')
                        scanner_path = rule_obj.scanner_path if rule_obj else 'unknown'
                        raise ScannerExecutionError(rule_file, scanner_path, e) from e
                elif scanner_path and not scanner_class:
                    # Error loading scanner - use appropriate format
                    error_msg = f"Scanner failed to load: {scanner_path}"
                    if is_test_or_code_scanner:
                        rule_result['scanner_results'] = {
                            'file_by_file': {'violations': [], 'error': error_msg},
                            'cross_file': {'violations': []}
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
            file_by_file = scanner_results.get('file_by_file', {}).get('violations', [])
            cross_file = scanner_results.get('cross_file', {}).get('violations', [])
            total_violations = len(file_by_file) + len(cross_file)
            if total_violations > 0:
                violation_summary.append(
                    f"Rule {rule.get('rule_file', 'unknown')}: "
                    f"{len(file_by_file)} file-by-file, {len(cross_file)} cross-file violations"
                )
        
        if violation_summary:
            edit_instructions = [
                "Based on code scanner diagnostics, edit the knowledge graph to fix violations:",
                *violation_summary,
                "Review each violation and update the knowledge graph accordingly."
            ]
            action_instructions.extend(edit_instructions)
        
        instructions = {
            'action': 'validate_rules',
            'behavior': self.behavior.name,
            'base_instructions': action_instructions,
            'validation_rules': processed_rules,
            'content_to_validate': self._identify_content_to_validate()
        }
        
        return {'instructions': instructions}
    
    def _write_validation_report(self, report_path: str, instructions: Dict[str, Any], validation_rules: List[Dict[str, Any]], content_info: Dict[str, Any]) -> None:
        """Write validation report to file.
        
        Args:
            report_path: Path where report should be written
            instructions: Instructions structure with base_instructions and validation_rules
            validation_rules: List of validation rules
            content_info: Content information including project location, rendered outputs, etc.
        """
        logger.info("=== _write_validation_report START ===")
        logger.info(f"Report path: {report_path}")
        logger.info(f"Number of validation rules: {len(validation_rules)}")
        logger.info(f"Content info keys: {list(content_info.keys())}")
        
        try:
            from datetime import datetime
            
            logger.info("Step 1: Creating report file path object...")
            report_file = Path(report_path)
            logger.info(f"Report file path object created: {report_file}")
            
            logger.info("Step 2: Creating parent directories...")
            report_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Parent directories created")
            
            # Generate report content
            logger.info("Step 3: Generating report content...")
            lines = []
            logger.info("Step 3a: Adding header...")
            lines.append(f"# Validation Report - {self.behavior.replace('_', ' ').title()}")
            lines.append("")
            logger.info("Step 3b: Adding metadata...")
            lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Project:** {Path(content_info.get('project_location', '')).name}")
            lines.append(f"**Behavior:** {self.behavior.name}")
            lines.append(f"**Action:** validate_rules")
            lines.append("")
            logger.info("Step 3c: Adding summary section...")
            lines.append("## Summary")
            lines.append("")
            
            # Count rules
            total_rules = len(validation_rules)
            lines.append(f"Validated story map and domain model against **{total_rules} validation rules**.")
            lines.append("")
            
            # List content validated
            lines.append("## Content Validated")
            lines.append("")
            if content_info.get('clarification_file'):
                lines.append(f"- **Clarification:** `{Path(content_info['clarification_file']).name}`")
            if content_info.get('planning_file'):
                lines.append(f"- **Planning:** `{Path(content_info['planning_file']).name}`")
            if content_info.get('rendered_outputs'):
                lines.append("- **Rendered Outputs:**")
                for output in content_info['rendered_outputs']:
                    lines.append(f"  - `{Path(output).name}`")
            
            # Add test files section if any were scanned
            test_files_scanned = content_info.get('test_files_scanned', [])
            logger.info(f"Test files scanned from content_info: {len(test_files_scanned) if test_files_scanned else 0} files")
            if test_files_scanned:
                lines.append("- **Test Files Scanned:**")
                # Sort for consistent output
                for test_file_str in sorted(test_files_scanned):
                    test_path = Path(test_file_str)
                    # Show relative path if possible, otherwise just filename
                    try:
                        if test_path.is_absolute() and self.workspace_directory:
                            rel_path = test_path.relative_to(self.workspace_directory)
                            lines.append(f"  - `{rel_path}`")
                        else:
                            # Try to resolve and show relative to workspace
                            if self.workspace_directory and not test_path.is_absolute():
                                try:
                                    resolved = (self.workspace_directory / test_path).resolve()
                                    rel_path = resolved.relative_to(self.workspace_directory)
                                    lines.append(f"  - `{rel_path}`")
                                except (ValueError, AttributeError):
                                    lines.append(f"  - `{test_path.name}`")
                            else:
                                lines.append(f"  - `{test_path.name}`")
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not create relative path for {test_file_str}: {e}")
                        lines.append(f"  - `{test_path.name}`")
                lines.append(f"  - **Total:** {len(test_files_scanned)} test file(s)")
            
            # Add code files section if any were scanned
            code_files_scanned = content_info.get('code_files_scanned', [])
            logger.info(f"Code files scanned from content_info: {len(code_files_scanned) if code_files_scanned else 0} files")
            if code_files_scanned:
                lines.append("- **Code Files Scanned:**")
                # Sort for consistent output
                for code_file_str in sorted(code_files_scanned):
                    code_path = Path(code_file_str)
                    # Show relative path if possible, otherwise just filename
                    try:
                        if code_path.is_absolute() and self.workspace_directory:
                            rel_path = code_path.relative_to(self.workspace_directory)
                            lines.append(f"  - `{rel_path}`")
                        else:
                            # Try to resolve and show relative to workspace
                            if self.workspace_directory and not code_path.is_absolute():
                                try:
                                    resolved = (self.workspace_directory / code_path).resolve()
                                    rel_path = resolved.relative_to(self.workspace_directory)
                                    lines.append(f"  - `{rel_path}`")
                                except (ValueError, AttributeError):
                                    lines.append(f"  - `{code_path.name}`")
                            else:
                                lines.append(f"  - `{code_path.name}`")
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not create relative path for {code_file_str}: {e}")
                        lines.append(f"  - `{code_path.name}`")
                lines.append(f"  - **Total:** {len(code_files_scanned)} code file(s)")
            
            lines.append("")
            
            # List validation rules checked
            lines.append("## Validation Rules Checked")
            lines.append("")
            for rule_dict in validation_rules[:20]:  # Show first 20 rules
                rule_file = rule_dict.get('rule_file', 'unknown')
                rule_content = rule_dict.get('rule_content', rule_dict)
                description = rule_content.get('description', 'No description')
                rule_name = Path(rule_file).stem if rule_file else 'unknown'
                lines.append(f"### Rule: {rule_name.replace('_', ' ').title()}")
                lines.append(f"**Description:** {description}")
                lines.append("")
            
            if total_rules > 20:
                lines.append(f"*... and {total_rules - 20} more rules*")
                lines.append("")
            
            # Violations summary - TWO-PASS SYSTEM
            lines.append("## Violations Found")
            lines.append("")
            
            # Separate violations by pass type
            file_by_file_violations_by_rule = {}
            cross_file_violations_by_rule = {}
            total_file_by_file = 0
            total_cross_file = 0
            
            for rule_dict in validation_rules:
                rule_file = rule_dict.get('rule_file', 'unknown')
                scanner_results = rule_dict.get('scanner_results', {})
                rule_name = Path(rule_file).stem if rule_file else 'unknown'
                
                # Handle both old format (backward compatibility) and new two-pass format
                if 'file_by_file' in scanner_results or 'cross_file' in scanner_results:
                    # New two-pass format
                    file_by_file_violations = scanner_results.get('file_by_file', {}).get('violations', [])
                    cross_file_violations = scanner_results.get('cross_file', {}).get('violations', [])
                    
                    if file_by_file_violations:
                        file_by_file_violations_by_rule[rule_name] = file_by_file_violations
                        total_file_by_file += len(file_by_file_violations)
                    if cross_file_violations:
                        cross_file_violations_by_rule[rule_name] = cross_file_violations
                        total_cross_file += len(cross_file_violations)
                else:
                    # Old format (backward compatibility) - treat as file-by-file
                    violations = scanner_results.get('violations', [])
                    if violations:
                        file_by_file_violations_by_rule[rule_name] = violations
                        total_file_by_file += len(violations)
            
            total_violations = total_file_by_file + total_cross_file
            
            if total_violations == 0:
                lines.append("✅ **No violations found.** All rules passed validation.")
                lines.append("")
            else:
                lines.append(f"**Total Violations:** {total_violations}")
                lines.append(f"- **File-by-File Violations:** {total_file_by_file}")
                lines.append(f"- **Cross-File Violations:** {total_cross_file}")
                lines.append("")
                
                # PASS 1: File-by-File Violations
                if file_by_file_violations_by_rule:
                    lines.append("### File-by-File Violations (Pass 1)")
                    lines.append("")
                    lines.append("These violations were detected by scanning each file individually.")
                    lines.append("")
                    
                    for rule_name, violations in file_by_file_violations_by_rule.items():
                        lines.append(f"#### {rule_name.replace('_', ' ').title()}: {len(violations)} violation(s)")
                        lines.append("")
                        
                        for violation in violations:
                            location = violation.get('location', 'unknown')
                            message = violation.get('violation_message', 'No message')
                            severity = violation.get('severity', 'error')
                            line_number = violation.get('line_number')
                            severity_icon = '🔴' if severity == 'error' else '🟡' if severity == 'warning' else '🔵'
                            
                            location_link = self._create_file_link(location, line_number)
                            test_info = self._extract_test_info(message, location, line_number)
                            
                            if test_info:
                                lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {test_info}")
                            else:
                                lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {message}")
                        
                        lines.append("")
                
                # PASS 2: Cross-File Violations
                if cross_file_violations_by_rule:
                    lines.append("### Cross-File Violations (Pass 2)")
                    lines.append("")
                    lines.append("These violations were detected by analyzing all files together to find patterns that span multiple files.")
                    lines.append("")
                    
                    for rule_name, violations in cross_file_violations_by_rule.items():
                        lines.append(f"#### {rule_name.replace('_', ' ').title()}: {len(violations)} violation(s)")
                        lines.append("")
                        
                        for violation in violations:
                            location = violation.get('location', 'unknown')
                            message = violation.get('violation_message', 'No message')
                            severity = violation.get('severity', 'error')
                            line_number = violation.get('line_number')
                            severity_icon = '🔴' if severity == 'error' else '🟡' if severity == 'warning' else '🔵'
                            
                            location_link = self._create_file_link(location, line_number)
                            test_info = self._extract_test_info(message, location, line_number)
                            
                            if test_info:
                                lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {test_info}")
                            else:
                                lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {message}")
                        
                        lines.append("")
            
            # Instructions summary
            lines.append("## Validation Instructions")
            lines.append("")
            base_instructions = instructions.get('base_instructions', [])
            if base_instructions:
                lines.append("The following validation steps were performed:")
                lines.append("")
                for i, instruction in enumerate(base_instructions[:10], 1):  # Show first 10 instructions
                    lines.append(f"{i}. {instruction}")
                if len(base_instructions) > 10:
                    lines.append(f"*... and {len(base_instructions) - 10} more instructions*")
            lines.append("")
            
            # Report path reminder
            lines.append("## Report Location")
            lines.append("")
            lines.append(f"This report was automatically generated and saved to:")
            lines.append(f"`{report_path}`")
            lines.append("")
            
            # Write file
            logger.info("Step 4: Writing report to file...")
            logger.info(f"Report file path: {report_file}")
            logger.info(f"Number of lines to write: {len(lines)}")
            report_file.write_text('\n'.join(lines), encoding='utf-8')
            logger.info("Report file written successfully")
            logger.info("=== _write_validation_report COMPLETE ===")
        except Exception as e:
            import traceback
            logger.error("=== ERROR in _write_validation_report ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Report path: {report_path}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
    
    def _create_file_link(self, location: str, line_number: Optional[int] = None) -> str:
        """Create a clickable file link for the validation report using VS Code URIs.
        
        Args:
            location: File path (can be absolute or relative)
            line_number: Optional line number to link to
            
        Returns:
            Markdown link string with VS Code URI
        """
        if location == 'unknown' or not location:
            return f"`{location}`"
        
        try:
            # Convert to Path to normalize
            file_path = Path(location)
            
            # Check if it's an absolute path (Windows paths start with drive letter or \\)
            is_absolute = file_path.is_absolute() or (len(location) > 1 and location[1] == ':') or location.startswith('\\\\')
            
            # Get VS Code URI using the helper method
            file_uri = self._get_file_uri(location, line_number)
            
            if is_absolute:
                # Use filename for display, VS Code URI in link
                try:
                    resolved_path = file_path.resolve() if file_path.exists() else file_path
                    display_name = resolved_path.name
                except Exception:
                    display_name = file_path.name
                return f"[`{display_name}`]({file_uri})"
            else:
                # Relative path - use relative path for display
                return f"[`{location}`]({file_uri})"
        except Exception:
            # Fallback: use VS Code URI helper
            try:
                file_uri = self._get_file_uri(location, line_number)
                return f"[`{Path(location).name if location else location}`]({file_uri})"
            except Exception:
                # Final fallback: just show the location as-is
                if line_number:
                    return f"`{location}:{line_number}`"
                return f"`{location}`"
    
    def _extract_test_info(self, message: str, location: str, line_number: Optional[int] = None) -> Optional[str]:
        """Extract test class and method information from violation message and create links.
        
        Args:
            message: Violation message that may contain test names
            location: File path
            line_number: Line number where violation occurs
            
        Returns:
            Formatted message with clickable links to test class/method, or None if no test info found
        """
        import re
        
        # Try to extract test method name from various patterns:
        # - 'Test "test_method_name"'
        # - 'test method "test_method_name"'
        # - 'Test method "test_method_name"'
        # - Test "test_method_name" appears to...
        test_method_patterns = [
            r'Test\s+method\s+["\']([^"\']+)["\']',
            r'Test\s+["\']([^"\']+)["\']',
            r'test\s+method\s+["\']([^"\']+)["\']',
        ]
        
        # Try to extract test class name
        test_class_patterns = [
            r'Test\s+class\s+["\']([^"\']+)["\']',
            r'class\s+["\']([^"\']+)["\']',
        ]
        
        test_method_match = None
        for pattern in test_method_patterns:
            test_method_match = re.search(pattern, message, re.IGNORECASE)
            if test_method_match:
                break
        
        test_class_match = None
        for pattern in test_class_patterns:
            test_class_match = re.search(pattern, message, re.IGNORECASE)
            if test_class_match:
                break
        
        if not test_method_match and not test_class_match:
            return None
        
        # Get file URI for linking
        file_uri = self._get_file_uri(location, line_number)
        
        # Replace the original test reference in message with linked version
        # IMPORTANT: Use string replacement instead of regex to avoid escape sequence issues with Windows paths
        try:
            if test_method_match:
                test_method_name = test_method_match.group(1)
                # Use simple string replacement to avoid regex escape sequence parsing issues
                replacement = f'Test method [{test_method_name}]({file_uri})'
                # Replace all variations using string replace (safer than regex for paths with backslashes)
                message = message.replace(f'Test method "{test_method_name}"', replacement)
                message = message.replace(f"Test method '{test_method_name}'", replacement)
                message = message.replace(f'Test "{test_method_name}"', replacement)
                message = message.replace(f"Test '{test_method_name}'", replacement)
                message = message.replace(f'test method "{test_method_name}"', replacement)
                message = message.replace(f"test method '{test_method_name}'", replacement)
            
            if test_class_match:
                test_class_name = test_class_match.group(1)
                # Use simple string replacement to avoid regex escape sequence parsing issues
                replacement = f'Test class [{test_class_name}]({file_uri})'
                message = message.replace(f'Test class "{test_class_name}"', replacement)
                message = message.replace(f"Test class '{test_class_name}'", replacement)
                message = message.replace(f'class "{test_class_name}"', replacement)
                message = message.replace(f"class '{test_class_name}'", replacement)
        except Exception as e:
            # If replacement fails, log and return original message
            logger.warning(f"Failed to create test info links: {e}, returning original message")
            return None
        
        return message
    
    def _get_file_uri(self, location: str, line_number: Optional[int] = None) -> str:
        """Get VS Code-compatible file URI for markdown links.
        
        Args:
            location: File path
            line_number: Optional line number
            
        Returns:
            VS Code URI format: vscode://file/C:/path/to/file.py:123
        """
        try:
            file_path = Path(location)
            if file_path.is_absolute():
                resolved_path = file_path.resolve() if file_path.exists() else file_path
            else:
                # Try to resolve relative to workspace
                workspace_path = self.workspace_directory
                if workspace_path:
                    resolved_path = (workspace_path / file_path).resolve()
                else:
                    # Fallback: use location as-is
                    resolved_path = Path(location)
            
            # Convert to VS Code URI format: vscode://file/C:/path/to/file.py:123
            # Use forward slashes and ensure drive letter is uppercase
            file_str = str(resolved_path).replace('\\', '/')
            # Ensure drive letter is uppercase (C: not c:)
            if len(file_str) >= 2 and file_str[1] == ':':
                file_str = file_str[0].upper() + ':' + file_str[2:]
            
            # Build VS Code URI
            vscode_uri = f"vscode://file/{file_str}"
            
            # Add line number with colon (VS Code format uses colon, not #L)
            if line_number:
                vscode_uri = f"{vscode_uri}:{line_number}"
            
            return vscode_uri
        except Exception:
            # Fallback - try to construct VS Code URI from location as-is
            file_str = location.replace('\\', '/')
            # Ensure drive letter is uppercase
            if len(file_str) >= 2 and file_str[1] == ':':
                file_str = file_str[0].upper() + ':' + file_str[2:]
            vscode_uri = f"vscode://file/{file_str}"
            if line_number:
                vscode_uri = f"{vscode_uri}:{line_number}"
            return vscode_uri
    
    def generate_report(self, report_format: str = 'JSON', violations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate violation report in specified format.
        
        Args:
            report_format: Format of report ('JSON', 'CHECKLIST', 'DETAILED', 'SUMMARY')
            violations: Optional list of violations to include in report. If None, uses violations from scanner execution.
            
        Returns:
            Report dictionary in requested format
        """
        # Use provided violations or stored violations from scanner execution
        violations = violations if violations is not None else self._violations
        
        # For now, return empty report structure
        # When scanner execution is implemented, violations will be populated
        if report_format == 'JSON':
            return {
                'violations': violations,
                'format': 'JSON'
            }
        elif report_format == 'CHECKLIST':
            checklist_items = []
            for violation in violations:
                line_num = violation.get('line_number', '?')
                location = violation.get('location', 'unknown')
                message = violation.get('violation_message', '')
                severity = violation.get('severity', 'error')
                checklist_items.append(
                    f"- [ ] Line {line_num} ({location}) [{severity.upper()}]: {message}"
                )
            return {
                'checklist': '\n'.join(checklist_items) if checklist_items else 'No violations found.',
                'format': 'CHECKLIST'
            }
        elif report_format == 'DETAILED':
            return {
                'violations': violations,
                'format': 'DETAILED',
                'total_count': len(violations)
            }
        elif report_format == 'SUMMARY':
            severity_breakdown = {}
            rule_count = set()
            for violation in violations:
                severity = violation.get('severity', 'error')
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
                rule_name = violation.get('rule') or violation.get('rule_name')  # Support both for backward compatibility
                if rule_name:
                    rule_count.add(rule_name)
            
            return {
                'violation_count': len(violations),
                'rule_count': len(rule_count),
                'severity_breakdown': severity_breakdown,
                'format': 'SUMMARY'
            }
        else:
            return {
                'violations': violations,
                'format': report_format
            }


