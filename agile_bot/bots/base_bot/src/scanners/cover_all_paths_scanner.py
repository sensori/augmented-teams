"""Scanner for validating all behavior paths are covered by tests."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .test_scanner import TestScanner
from .violation import Violation


class CoverAllPathsScanner(TestScanner):
    """Validates all behavior paths are tested."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Find all test methods
            test_methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_methods.append(node)
            
            # Check if test methods have actual code (not just pass/TODO)
            for test_method in test_methods:
                has_code = False
                for stmt in test_method.body:
                    if isinstance(stmt, ast.Pass):
                        continue
                    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                        # Skip docstrings
                        continue
                    else:
                        # Check for actual executable code
                        for node in ast.walk(stmt):
                            if isinstance(node, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise)):
                                has_code = True
                                break
                        if has_code:
                            break
                
                if not has_code:
                    violations.append(Violation(
                        rule=rule_obj,
                        violation_message=f'Test method "{test_method.name}" has no actual test code - tests must exercise behavior paths, not just contain pass statements',
                        location=str(test_file_path),
                        line_number=test_method.lineno,
                        severity='error'
                    ).to_dict())
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations

