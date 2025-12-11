from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation


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
        
        Validates that scanner class inherits from Scanner base class.
        """
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            scanner_class = getattr(module, class_name)
            
            if not isinstance(scanner_class, type):
                return None, f"Scanner path does not point to a class: {scanner_module_path}"
            
            # Validate that scanner_class inherits from Scanner base class
            if not issubclass(scanner_class, Scanner):
                return None, f"Scanner class does not inherit from Scanner base class: {scanner_module_path}"
            
            if not hasattr(scanner_class, 'scan'):
                return None, f"Scanner class missing required 'scan' method: {scanner_module_path}"
            
            return scanner_class, None
        except ImportError as e:
            return None, f"Scanner class import failure: {e}"
        except AttributeError as e:
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"


class ValidateRulesAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory, 'validate_rules')
        self._violations = []  # Store violations from scanner execution
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate_rules action logic."""
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Format instructions properly - action_instructions are primary, rules are context
        instructions = {
            'action': 'validate_rules',
            'behavior': self.behavior,
            'base_instructions': action_instructions,  # Primary instructions from instructions.json
            'validation_rules': validation_rules,  # Rules to validate against (supporting context)
            'content_to_validate': self._identify_content_to_validate()
        }
        
        return {'instructions': instructions}
    
    def inject_common_bot_rules(self) -> Dict[str, Any]:
        # Try both potential paths for common rules
        rules_file = (
            self.bot_directory /
            'agile_bot' / 'bots' / 'base_bot' / 'rules' / 'common_rules.json'
        )
        if not rules_file.exists():
            rules_file = (
                self.bot_directory /
                'base_bot' / 'rules' / 'common_rules.json'
            )
        
        if not rules_file.exists():
            raise FileNotFoundError(
                f'Common bot rules not found at {rules_file}'
            )
        
        rules_data = read_json_file(rules_file)
        
        return {
            'validation_rules': rules_data.get('rules', [])
        }
    
    def inject_behavior_specific_and_bot_rules(self) -> Dict[str, Any]:
        # Load action-specific instructions from base_actions
        action_instructions = []
        base_actions_path = self.base_actions_dir
        
        # Find the validate_rules action folder (may have number prefix)
        action_folder = None
        if base_actions_path.exists():
            # Use glob pattern to find action folder (handles numbered prefixes like '7_validate_rules')
            matching_folders = list(base_actions_path.glob('*validate_rules'))
            if matching_folders:
                action_folder = matching_folders[0]  # Take first match
        
        if action_folder:
            instructions_file = action_folder / 'instructions.json'
            if instructions_file.exists():
                instructions_data = read_json_file(instructions_file)
                action_instructions = instructions_data.get('instructions', [])
        
        # Load common rules - try both paths
        common_rules = []
        common_file = (
            self.bot_directory /
            'agile_bot' / 'bots' / 'base_bot' / 'rules' / 'common_rules.json'
        )
        if not common_file.exists():
            common_file = (
                self.bot_directory /
                'base_bot' / 'rules' / 'common_rules.json'
            )
        
        if common_file.exists():
            common_data = read_json_file(common_file)
            common_rules = common_data.get('rules', [])
        
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
            # Try to find config that specifies docs_path
            config_file = behavior_folder / 'instructions.json'
            if config_file.exists():
                config_data = read_json_file(config_file)
                docs_path = config_data.get('docs_path', 'docs/stories')
            else:
                docs_path = 'docs/stories'
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
        """Load scanner class from module path."""
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            scanner_class = getattr(module, class_name)
            
            if not isinstance(scanner_class, type):
                return None, f"Scanner path does not point to a class: {scanner_module_path}"
            
            if not hasattr(scanner_class, 'scan'):
                return None, f"Scanner class missing required 'scan' method: {scanner_module_path}"
            
            return scanner_class, None
        except ImportError as e:
            return None, f"Scanner class import failure: {e}"
        except AttributeError as e:
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"
    
    def injectValidationInstructions(self, knowledge_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Inject validation instructions with scanner results.
        
        For each rule: inject rule, run scanner (if exists), add results to rule.
        Adds instructions to edit built knowledge based on code diagnostics.
        
        Args:
            knowledge_graph: The knowledge graph to validate against
            
        Returns:
            Dictionary with 'instructions' containing rules with scanner_results
        """
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Process each rule: run scanner if exists, add results
        processed_rules = []
        for rule_dict in validation_rules:
            if isinstance(rule_dict, dict):
                rule_content = rule_dict.get('rule_content', rule_dict)
                scanner_path = rule_content.get('scanner')
                
                rule_result = dict(rule_dict)  # Copy rule
                rule_result['scanner_results'] = {}
                
                if scanner_path:
                    scanner_class, error_msg = self._load_scanner_class(scanner_path)
                    if scanner_class:
                        # Run scanner against knowledge graph
                        try:
                            scanner_instance = scanner_class()
                            violations = scanner_instance.scan(knowledge_graph)
                            violations_list = violations if isinstance(violations, list) else []
                            
                            # Convert violations to dictionaries if they're Violation objects
                            violations_dicts = []
                            rule_name = rule_dict.get('rule_file', 'unknown').replace('.json', '')
                            rule_file = rule_dict.get('rule_file', 'unknown')
                            
                            for violation in violations_list:
                                if isinstance(violation, Violation):
                                    # Convert Violation DTO to dict
                                    violation_dict = violation.to_dict()
                                    violation_dict['rule_name'] = violation_dict.get('rule_name', rule_name)
                                    violation_dict['rule_file'] = violation_dict.get('rule_file', rule_file)
                                    violations_dicts.append(violation_dict)
                                elif isinstance(violation, dict):
                                    # Already a dict, just ensure rule metadata
                                    violation['rule_name'] = violation.get('rule_name', rule_name)
                                    violation['rule_file'] = violation.get('rule_file', rule_file)
                                    violations_dicts.append(violation)
                            
                            # Store violations in action instance for report generation
                            self._violations.extend(violations_dicts)
                            
                            rule_result['scanner_results'] = {
                                'violations': violations_dicts
                            }
                        except Exception as e:
                            # Store error but log it - don't swallow exceptions silently
                            # Per planning: "Exception-based, don't swallow"
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
                            
                            rule_result['scanner_results'] = {
                                'violations': [],
                                'error': f"Scanner execution failed: {e}"
                            }
                            # Continue processing other rules - don't fail entire validation
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Scanner execution failed for rule {rule_dict.get('rule_file', 'unknown')}: {e}", exc_info=True)
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
                rule_name = violation.get('rule_name')
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


