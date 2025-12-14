"""Scanner for validating single responsibility principle."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class SingleResponsibilityScanner(CodeScanner):
    """Validates functions/classes follow single responsibility principle.
    
    Only scans production code (not test files) and uses stricter patterns
    to avoid false positives on test helper functions.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Skip test files - only scan production code
        if self._is_test_file(file_path):
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_function_sr(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
                elif isinstance(node, ast.ClassDef):
                    violation = self._check_class_sr(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file and should be skipped."""
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Skip test directories
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        # Skip test files (files starting with test_)
        if file_name.startswith('test_'):
            return True
        
        # Skip conftest files
        if file_name == 'conftest.py':
            return True
        
        return False
    
    def _check_function_sr(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function has single responsibility.
        
        Uses stricter patterns to avoid false positives:
        - Only flags obvious violations like "and" separating two distinct actions
        - Ignores common patterns in test helpers and descriptive names
        """
        func_name = func_node.name.lower()
        
        # Skip test helper functions (even if they somehow got through)
        if func_name.startswith(('given_', 'when_', 'then_', 'test_')):
            return None
        
        # Stricter patterns - only flag obvious multiple responsibility violations
        # Pattern: verb_and_verb (e.g., "validate_and_save", "process_and_send")
        # But NOT: "given_bot_config_and_directory" (descriptive, not multiple actions)
        # Pattern must have action verb before AND and action verb after AND
        action_verbs = [
            'validate', 'save', 'load', 'process', 'send', 'create', 'update', 'delete',
            'calculate', 'compute', 'transform', 'convert', 'parse', 'format', 'render',
            'execute', 'run', 'invoke', 'call', 'fetch', 'retrieve', 'store', 'write',
            'read', 'parse', 'build', 'generate', 'compile', 'extract', 'merge', 'split'
        ]
        
        # Check for pattern: action_verb_and_action_verb
        # Build pattern once for efficiency
        verbs_pattern = '|'.join(action_verbs)
        for verb in action_verbs:
            pattern = rf'\b{verb}_and_({verbs_pattern})\b'
            if re.search(pattern, func_name):
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        # Also check for pattern: action_verb_and_action_verb (with underscores)
        # e.g., "validateAndSave" -> "validate_and_save"
        camel_case_pattern = r'([a-z]+)And([A-Z][a-z]+)'
        match = re.search(camel_case_pattern, func_node.name)
        if match:
            verb1 = match.group(1).lower()
            verb2 = match.group(2).lower()
            if verb1 in action_verbs and verb2 in action_verbs:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _check_class_sr(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if class has single responsibility."""
        # Count methods - too many methods might indicate multiple responsibilities
        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        
        if method_count > 15:
            line_number = class_node.lineno if hasattr(class_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Class "{class_node.name}" has {method_count} methods - consider if it has multiple responsibilities',
                location=str(file_path),
                line_number=line_number,
                severity='info'
            ).to_dict()
        
        return None

