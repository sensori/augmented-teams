from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation


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


class Rule:
    """Represents a validation rule with optional scanner.
    
    Simple rule class loaded on bot load, contains link to scanner and provides
    property access to data like examples, descriptions, etc.
    """
    
    def __init__(self, rule_file: str, rule_content: Dict[str, Any], behavior_name: str = 'common'):
        self._name = rule_file.replace('.json', '') if rule_file else 'unknown'
        self._rule_file = rule_file
        self._rule_content = rule_content
        self._behavior_name = behavior_name
        self._scanner_class = None
        self._scanner_error = None
        
        # Load scanner if present
        scanner_path = rule_content.get('scanner')
        if scanner_path:
            self._scanner_class, self._scanner_error = self._load_scanner_class(scanner_path)
    
    @property
    def name(self) -> str:
        """Get rule name."""
        return self._name
    
    @property
    def rule_file(self) -> str:
        """Get rule file path."""
        return self._rule_file
    
    @property
    def behavior_name(self) -> str:
        """Get behavior name."""
        return self._behavior_name
    
    @property
    def scanner(self) -> Optional[type]:
        """Get scanner class for this rule (0 or 1 scanner per rule)."""
        return self._scanner_class
    
    @property
    def description(self) -> str:
        """Get rule description."""
        return self._rule_content.get('description', '')
    
    @property
    def examples(self) -> List[Dict[str, Any]]:
        """Get rule examples."""
        return self._rule_content.get('examples', [])
    
    @property
    def scanner_path(self) -> Optional[str]:
        """Get scanner module path if present."""
        return self._rule_content.get('scanner')
    
    @property
    def rule_content(self) -> Dict[str, Any]:
        """Get full rule content dictionary."""
        return self._rule_content
    
    def _load_scanner_class(self, scanner_module_path: str) -> tuple:
        """Load scanner class from module path.
        
        Tries multiple locations:
        1. Exact path specified
        2. base_bot/src/scanners/ (if path contains bot name)
        3. Bot's src/scanners/ (if path contains bot name)
        
        Validates that scanner class inherits from Scanner base class.
        """
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            
            paths_to_try = [module_path]
            
            scanner_name = class_name.lower().replace('scanner', '')
            base_bot_path = f'agile_bot.bots.base_bot.src.scanners.{scanner_name}_scanner'
            
            if 'story_bot' in module_path or 'test_story_bot' in module_path:
                bot_name = 'story_bot' if 'story_bot' in module_path else 'test_story_bot'
                bot_path = f'agile_bot.bots.{bot_name}.src.scanners.{scanner_name}_scanner'
                paths_to_try.extend([base_bot_path, bot_path])
            else:
                paths_to_try.append(base_bot_path)
            
            for path in paths_to_try:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        scanner_class = getattr(module, class_name)
                        
                        if isinstance(scanner_class, type):
                            if not issubclass(scanner_class, Scanner):
                                continue
                            if not hasattr(scanner_class, 'scan'):
                                continue
                            return scanner_class, None
                except (ImportError, AttributeError, TypeError):
                    continue
            
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"


class ValidateRulesAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory, 'validate_rules')
        self._violations = []  # Store violations from scanner execution
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate_rules action logic."""
        # Set up file logging for debugging (early, so we can use it throughout)
        import logging
        import sys
        log_file = self.workspace_directory / 'validation_debug.log'
        debug_logger = logging.getLogger('validate_rules_debug')
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            debug_logger.addHandler(file_handler)
            debug_logger.setLevel(logging.DEBUG)
        except Exception as e:
            pass  # debug_logger still exists, just no file handler
        
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
                f"Expected story graph to be created by build_knowledge action before validate_rules."
            )
        
        if not story_graph_path.exists():
            raise FileNotFoundError(
                f"Story graph file not found at {story_graph_path}. "
                f"Cannot validate rules without story graph. "
                f"Expected story graph to be created by build_knowledge action before validate_rules."
            )
        
        # Load story graph - if file exists, loading MUST succeed
        # This ensures syntax errors are reported, not hidden
        story_graph = read_json_file(story_graph_path)
        
        # Extract scope from parameters and add to story_graph for scanners
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
                test_files_list = parameters['test_files']
                if test_files_list:
                    # Ensure it's a list
                    if not isinstance(test_files_list, list):
                        test_files_list = [test_files_list]
                    # Convert all to strings and store in scope
                    scope_config['test_files'] = [str(Path(tf)) if isinstance(tf, str) else str(tf) for tf in test_files_list]
            
            # Support code_files as scope parameter - list of code files to validate (for CodeScanner)
            if 'code_files' in parameters:
                code_files_list = parameters['code_files']
                if code_files_list:
                    # Ensure it's a list
                    if not isinstance(code_files_list, list):
                        code_files_list = [code_files_list]
                    # Convert all to strings and store in scope
                    scope_config['code_files'] = [str(Path(cf)) if isinstance(cf, str) else str(cf) for cf in code_files_list]
            
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
        
        # Auto-discover test files if not provided and we're in 7_tests behavior
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
        if debug_logger:
            debug_logger.debug(f"[PATH RESOLUTION] Starting from workspace_path: {workspace_path}")
            debug_logger.debug(f"[PATH RESOLUTION] Resolved absolute path: {current}")
        
        for i in range(10):  # Look up to 10 levels up
            if debug_logger:
                debug_logger.debug(f"[PATH RESOLUTION] Checking level {i}: {current}")
            if (current / '.git').exists() or (current / 'agile_bot').exists():
                repo_root = current
                if debug_logger:
                    debug_logger.debug(f"[PATH RESOLUTION] Found repo root: {repo_root}")
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
            if debug_logger:
                debug_logger.debug(f"[PATH RESOLUTION] Using fallback repo root: {repo_root}")
        
        if test_files_to_scan:
            test_file_paths = []
            for tf in test_files_to_scan:
                test_path = Path(tf)
                if debug_logger:
                    debug_logger.debug(f"[PATH RESOLUTION] Processing test file: {test_path}")
                # If absolute path, use as-is
                if test_path.is_absolute():
                    if debug_logger:
                        debug_logger.debug(f"[PATH RESOLUTION] Path is absolute, using as-is: {test_path}")
                    test_file_paths.append(test_path)
                else:
                    # Always resolve against repo root (test files are relative to repo root)
                    if repo_root:
                        resolved_path = repo_root / test_path
                        if debug_logger:
                            debug_logger.debug(f"[PATH RESOLUTION] Resolved against repo_root {repo_root}: {resolved_path}")
                            debug_logger.debug(f"[PATH RESOLUTION] Resolved path exists: {resolved_path.exists()}")
                        test_file_paths.append(resolved_path)
                    else:
                        # Fallback: resolve against workspace (shouldn't happen if repo_root detection works)
                        if debug_logger:
                            debug_logger.debug(f"[PATH RESOLUTION] No repo_root found, using workspace fallback")
                        resolved_path = self.workspace_directory / test_path
                        test_file_paths.append(resolved_path)
        else:
            test_file_paths = None
        
        if code_files_to_scan:
            code_file_paths = []
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
        else:
            code_file_paths = None
        
        # Run scanners with story graph and optional test/code files (one-off, not persisted)
        result = self.injectValidationInstructions(story_graph, test_files=test_file_paths, code_files=code_file_paths)
        
        # Write validation report with scanner results
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
        # Load action-specific instructions from base_actions
        action_instructions = []
        base_actions_path = self.base_actions_dir
        
        # Find the validate_rules action folder (may have number prefix)
        action_folder = None
        if base_actions_path.exists():
            # Use glob pattern to find action folder (handles numbered prefixes like '5_validate_rules')
            matching_folders = list(base_actions_path.glob('*validate_rules'))
            if matching_folders:
                action_folder = matching_folders[0]  # Take first match
        
        if action_folder:
            instructions_file = action_folder / 'instructions.json'
            if instructions_file.exists():
                instructions_data = read_json_file(instructions_file)
                action_instructions = instructions_data.get('instructions', [])
        
        # Load common rules - try multiple paths
        common_rules = []
        
        # Try bot's own rules directory first (for test bots)
        bot_rules_dir = self.bot_directory / 'rules'
        if bot_rules_dir.exists() and bot_rules_dir.is_dir():
            for rule_file in bot_rules_dir.glob('*.json'):
                rule_data = read_json_file(rule_file)
                common_rules.append({
                    'rule_file': str(rule_file.relative_to(self.bot_directory)),
                    'rule_content': rule_data
                })
        
        # Try base_bot rules directory (common/bot-level rules)
        base_bot_rules_dir = self.bot_dir.parent / 'base_bot' / 'rules'
        
        if base_bot_rules_dir.exists() and base_bot_rules_dir.is_dir():
            for rule_file in base_bot_rules_dir.glob('*.json'):
                rule_data = read_json_file(rule_file)
                common_rules.append({
                    'rule_file': f'agile_bot/bots/base_bot/rules/{rule_file.name}',
                    'rule_content': rule_data
                })
        
        # Load behavior-specific rules
        behavior_rules = []
        
        # Find behavior folder (handles numbered prefixes)
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            # Use utility to find rules folder (handles numbered prefixes like '3_rules')
            from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import find_behavior_subfolder
            behavior_rules_dir = find_behavior_subfolder(behavior_folder, 'rules')
        except FileNotFoundError:
            behavior_rules_dir = None
        
        # Check for single validation_rules.json file
        if behavior_rules_dir and behavior_rules_dir.exists():
            behavior_file = behavior_rules_dir / 'validation_rules.json'
            if behavior_file.exists():
                behavior_data = read_json_file(behavior_file)
                behavior_rules = behavior_data.get('rules', [])
            # Otherwise load all .json files from rules directory
            elif behavior_rules_dir.is_dir():
                for rule_file in behavior_rules_dir.glob('*.json'):
                    rule_data = read_json_file(rule_file)
                    # Add the rule file content with filename as identifier
                    behavior_rules.append({
                        'rule_file': rule_file.name,
                        'rule_content': rule_data
                    })
        
        # Merge rules
        all_rules = common_rules + behavior_rules
        
        return {
            'action_instructions': action_instructions,
            'validation_rules': all_rules
        }
    
    def inject_next_action_instructions(self):
        return ""  # Empty string for terminal action
    
    def _identify_content_to_validate(self) -> Dict[str, Any]:
        """Identify what content needs to be validated from the project."""
        project_dir = self.working_dir
        content_info = {
            'project_location': str(project_dir),
            'rendered_outputs': [],
            'clarification_file': None,
            'planning_file': None,
            'report_path': None
        }
        
        # Find docs_path from behavior config or default
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            # Try to find config that specifies docs_path from behavior.json (new format)
            behavior_file = behavior_folder / 'behavior.json'
            docs_path = 'docs/stories'
            if behavior_file.exists():
                behavior_data = read_json_file(behavior_file)
                docs_path = behavior_data.get('docs_path', 'docs/stories')
            else:
                # Fallback to old format for backward compatibility
                config_file = behavior_folder / 'instructions.json'
                if config_file.exists():
                    config_data = read_json_file(config_file)
                    docs_path = config_data.get('docs_path', 'docs/stories')
        except FileNotFoundError:
            docs_path = 'docs/stories'
        
        docs_dir = project_dir / docs_path
        
        # Find clarification.json and planning.json
        clarification_file = docs_dir / 'clarification.json'
        planning_file = docs_dir / 'planning.json'
        
        if clarification_file.exists():
            content_info['clarification_file'] = str(clarification_file)
        if planning_file.exists():
            content_info['planning_file'] = str(planning_file)
        
        # Set validation report path (where AI should save the report)
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
        rules_data = self.inject_behavior_specific_and_bot_rules()
        validation_rules = rules_data.get('validation_rules', [])
        
        scanners = []
        errors = []
        
        for rule_dict in validation_rules:
            if isinstance(rule_dict, dict):
                rule_content = rule_dict.get('rule_content', rule_dict)
                scanner_path = rule_content.get('scanner')
                if scanner_path:
                    scanner_class, error_msg = self._load_scanner_class(scanner_path)
                    if scanner_class:
                        scanners.append(scanner_class)
                    else:
                        errors.append(error_msg)
        
        return {
            'scanners': scanners,
            'errors': errors
        }
    
    def _load_scanner_class(self, scanner_module_path: str) -> tuple:
        """Load scanner class from module path.
        
        Tries multiple locations:
        1. Exact path specified
        2. base_bot/src/scanners/ (always checked)
        3. Bot's src/scanners/ (if bot_name is set)
        """
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            
            paths_to_try = [module_path]
            
            scanner_name = class_name.lower().replace('scanner', '')
            base_bot_path = f'agile_bot.bots.base_bot.src.scanners.{scanner_name}_scanner'
            paths_to_try.append(base_bot_path)
            
            if self.bot_name and self.bot_name != 'base_bot':
                bot_path = f'agile_bot.bots.{self.bot_name}.src.scanners.{scanner_name}_scanner'
                paths_to_try.append(bot_path)
            
            for path in paths_to_try:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        scanner_class = getattr(module, class_name)
                        
                        if isinstance(scanner_class, type) and hasattr(scanner_class, 'scan'):
                            return scanner_class, None
                except (ImportError, AttributeError):
                    continue
            
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"
    
    def injectValidationInstructions(self, knowledge_graph: Dict[str, Any], test_files: Optional[List[Path]] = None, code_files: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Inject validation instructions with scanner results.
        
        For each rule: inject rule, run scanner (if exists), add results to rule.
        Adds instructions to edit built knowledge based on code diagnostics.
        
        Args:
            knowledge_graph: The knowledge graph to validate against
            test_files: Optional list of test file paths for validation (not persisted in knowledge_graph)
            code_files: Optional list of code file paths for validation (not persisted in knowledge_graph)
            
        Returns:
            Dictionary with 'instructions' containing rules with scanner_results
        """
        # Set up file logging for debugging
        import logging
        import sys
        log_file = self.workspace_directory / 'validation_debug.log'
        print(f"[DEBUG] Setting up logging to: {log_file}", file=sys.stderr)
        print(f"[DEBUG] Workspace directory: {self.workspace_directory}", file=sys.stderr)
        
        # Ensure log file can be created
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            debug_logger = logging.getLogger('validate_rules_debug')
            debug_logger.addHandler(file_handler)
            debug_logger.setLevel(logging.DEBUG)
            # Also set up loggers for scanner modules
            for logger_name in ['test_scanner_debug', 'real_implementations_scanner_debug']:
                scanner_logger = logging.getLogger(logger_name)
                scanner_logger.addHandler(file_handler)
                scanner_logger.setLevel(logging.DEBUG)
            print(f"[DEBUG] Logging setup complete. Log file: {log_file}", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG] Failed to set up logging: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Process each rule: run scanner if exists, add results
        processed_rules = []
        import sys
        print(f"[VALIDATE_RULES] Processing {len(validation_rules)} validation rules", file=sys.stderr)
        for idx, rule_dict in enumerate(validation_rules):
            if isinstance(rule_dict, dict):
                rule_content = rule_dict.get('rule_content', rule_dict)
                scanner_path = rule_content.get('scanner')
                
                # Create Rule object for this rule
                rule_file = rule_dict.get('rule_file', 'unknown.json')
                print(f"[VALIDATE_RULES] Rule {idx+1}/{len(validation_rules)}: {rule_file}", file=sys.stderr)
                print(f"[VALIDATE_RULES]   Has scanner: {scanner_path is not None}", file=sys.stderr)
                if scanner_path:
                    print(f"[VALIDATE_RULES]   Scanner path: {scanner_path}", file=sys.stderr)
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
                        # Run scanner against knowledge graph
                        try:
                            scanner_instance = scanner_class()
                            scanner_name = scanner_class.__name__
                            
                            # LOG BEFORE SCANNER CALL
                            import sys
                            print(f"[BEFORE SCANNER] About to call scanner: {scanner_name}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] Rule file: {rule_file}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] Scanner class: {scanner_class}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] Scanner instance created: {scanner_instance}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] test_files parameter: {test_files}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] test_files type: {type(test_files)}", file=sys.stderr)
                            print(f"[BEFORE SCANNER] test_files is None: {test_files is None}", file=sys.stderr)
                            if test_files:
                                print(f"[BEFORE SCANNER] test_files count: {len(test_files)}", file=sys.stderr)
                                for idx, tf in enumerate(test_files):
                                    print(f"[BEFORE SCANNER]   test_files[{idx}]: {tf} (type: {type(tf)}, exists: {tf.exists() if hasattr(tf, 'exists') else 'N/A'})", file=sys.stderr)
                            
                            debug_logger.debug(f"[LOG validate_rules_action] Calling scanner: {scanner_name}")
                            debug_logger.debug(f"[LOG validate_rules_action] test_files: {test_files}")
                            debug_logger.debug(f"[LOG validate_rules_action] test_files type: {type(test_files)}")
                            debug_logger.debug(f"[LOG validate_rules_action] test_files is None: {test_files is None}")
                            if test_files:
                                debug_logger.debug(f"[LOG validate_rules_action] test_files count: {len(test_files)}")
                                for idx, tf in enumerate(test_files):
                                    debug_logger.debug(f"[LOG validate_rules_action]   test_files[{idx}]: {tf} (type: {type(tf)}, exists: {tf.exists() if hasattr(tf, 'exists') else 'N/A'})")
                            
                            print(f"[BEFORE SCANNER] About to call scanner_instance.scan()", file=sys.stderr)
                            print(f"[BEFORE SCANNER] Parameters being passed:", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   knowledge_graph type: {type(knowledge_graph)}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   knowledge_graph keys: {list(knowledge_graph.keys()) if isinstance(knowledge_graph, dict) else 'N/A'}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   rule_obj: {rule_obj}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   rule_obj type: {type(rule_obj)}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   test_files: {test_files}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   test_files type: {type(test_files)}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   test_files is None: {test_files is None}", file=sys.stderr)
                            if test_files:
                                print(f"[BEFORE SCANNER]   test_files length: {len(test_files)}", file=sys.stderr)
                                for i, tf in enumerate(test_files):
                                    print(f"[BEFORE SCANNER]     test_files[{i}]: {tf}", file=sys.stderr)
                                    print(f"[BEFORE SCANNER]     test_files[{i}] type: {type(tf)}", file=sys.stderr)
                                    if hasattr(tf, 'exists'):
                                        print(f"[BEFORE SCANNER]     test_files[{i}] exists: {tf.exists()}", file=sys.stderr)
                                    if hasattr(tf, '__str__'):
                                        print(f"[BEFORE SCANNER]     test_files[{i}] str: {str(tf)}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   code_files: {code_files}", file=sys.stderr)
                            print(f"[BEFORE SCANNER]   code_files type: {type(code_files)}", file=sys.stderr)
                            
                            # Pass test_files and code_files directly to scanners via scan() parameters
                            # Scanners get files from parameters, not from knowledge_graph
                            violations = scanner_instance.scan(
                                knowledge_graph, 
                                rule_obj=rule_obj,
                                test_files=test_files,
                                code_files=code_files
                            )
                            
                            print(f"[AFTER SCANNER] Scanner {scanner_name} returned {len(violations) if isinstance(violations, list) else 'N/A'} violations", file=sys.stderr)
                            debug_logger.debug(f"[LOG validate_rules_action] Scanner {scanner_name} returned {len(violations) if isinstance(violations, list) else 'N/A'} violations")
                            violations_list = violations if isinstance(violations, list) else []
                            
                            # Convert violations to dictionaries if they're Violation objects
                            violations_dicts = []
                            
                            for violation in violations_list:
                                if isinstance(violation, Violation):
                                    # Violation already has Rule object reference
                                    violation_dict = violation.to_dict()
                                    violations_dicts.append(violation_dict)
                                elif isinstance(violation, dict):
                                    # Dict violation - ensure it has rule name
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
                            # Log the error for debugging
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
                            
                            # Raise exception with context - don't swallow scanner crashes
                            # User needs to know when scanners fail so they can fix the issue
                            rule_file = rule_dict.get('rule_file', 'unknown')
                            scanner_path = rule_content.get('scanner', 'unknown')
                            raise ScannerExecutionError(rule_file, scanner_path, e) from e
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
                "Based on code scanner diagnostics, edit the knowledge graph to fix violations:",
                *violation_summary,
                "Review each violation and update the knowledge graph accordingly."
            ]
            action_instructions.extend(edit_instructions)
        
        instructions = {
            'action': 'validate_rules',
            'behavior': self.behavior,
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
        from datetime import datetime
        
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate report content
        lines = []
        lines.append(f"# Validation Report - {self.behavior.replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project:** {Path(content_info.get('project_location', '')).name}")
        lines.append(f"**Behavior:** {self.behavior}")
        lines.append(f"**Action:** validate_rules")
        lines.append("")
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
        
        # Violations summary
        lines.append("## Violations Found")
        lines.append("")
        
        total_violations = 0
        violations_by_rule = {}
        
        for rule_dict in validation_rules:
            rule_file = rule_dict.get('rule_file', 'unknown')
            scanner_results = rule_dict.get('scanner_results', {})
            violations = scanner_results.get('violations', [])
            
            if violations:
                rule_name = Path(rule_file).stem if rule_file else 'unknown'
                violations_by_rule[rule_name] = violations
                total_violations += len(violations)
        
        if total_violations == 0:
            lines.append("✅ **No violations found.** All rules passed validation.")
            lines.append("")
        else:
            lines.append(f"**Total Violations:** {total_violations}")
            lines.append("")
            
            # Group violations by rule
            for rule_name, violations in violations_by_rule.items():
                lines.append(f"### {rule_name.replace('_', ' ').title()}: {len(violations)} violation(s)")
                lines.append("")
                
                # Show all violations (no truncation)
                for violation in violations:
                    location = violation.get('location', 'unknown')
                    message = violation.get('violation_message', 'No message')
                    severity = violation.get('severity', 'error')
                    severity_icon = '🔴' if severity == 'error' else '🟡' if severity == 'warning' else '🔵'
                    lines.append(f"- {severity_icon} **{severity.upper()}** - `{location}`: {message}")
                
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
        report_file.write_text('\n'.join(lines), encoding='utf-8')
    
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


