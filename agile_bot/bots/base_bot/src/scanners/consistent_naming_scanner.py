"""Scanner for validating consistent naming across codebase."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation
from collections import defaultdict


class ConsistentNamingScanner(CodeScanner):
    """Validates naming consistency across codebase."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Skip test files - they may have different naming conventions
        if self._is_test_file(file_path):
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Collect naming patterns
            function_names = []
            class_names = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods and special methods
                    if not (node.name.startswith('_') and node.name != '__init__'):
                        function_names.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    class_names.append(node.name)
            
            # Check for inconsistent naming patterns (only check functions, not classes)
            # Classes often use PascalCase while functions use snake_case - that's OK
            violations.extend(self._check_naming_consistency(function_names, class_names, file_path, rule_obj))
        
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
    
    def _check_naming_consistency(self, function_names: List[str], class_names: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for inconsistent naming patterns."""
        violations = []
        
        if not function_names:
            return violations
        
        # Check for mixed naming conventions in functions (snake_case vs camelCase)
        # Python convention: functions use snake_case, classes use PascalCase
        has_snake_case = any('_' in name for name in function_names)
        has_camel_case = any(name[0].isupper() and '_' not in name for name in function_names if name)
        
        # Only flag if there's a significant mix (more than 1 camelCase function)
        camel_case_count = sum(1 for name in function_names if name and name[0].isupper() and '_' not in name)
        
        if has_snake_case and camel_case_count > 1:
            violation = Violation(
                rule=rule_obj,
                violation_message=f'File mixes snake_case and camelCase naming conventions ({camel_case_count} camelCase functions) - use consistent naming style (snake_case for functions)',
                location=str(file_path),
                severity='warning'
            ).to_dict()
            violations.append(violation)
        
        return violations

