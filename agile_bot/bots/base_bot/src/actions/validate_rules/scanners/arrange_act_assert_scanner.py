"""Scanner for validating Arrange-Act-Assert structure in tests."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .test_scanner import TestScanner
from .violation import Violation


class ArrangeActAssertScanner(TestScanner):
    """Validates tests follow Arrange-Act-Assert structure."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        violation = self._check_aaa_structure(node, content, test_file_path, rule_obj)
                        if violation:
                            violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_aaa_structure(self, test_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if test follows AAA structure AND has actual code."""
        # Get test function source
        test_lines = content.split('\n')
        start_line = test_node.lineno - 1
        end_line = test_node.end_lineno if hasattr(test_node, 'end_lineno') else start_line + 50
        
        test_body_lines = test_lines[start_line:end_line]
        test_body = '\n'.join(test_body_lines)
        
        # Check for AAA comments/sections
        has_given_comment = any('# Given' in line or '# Arrange' in line for line in test_body_lines)
        has_when_comment = any('# When' in line or '# Act' in line for line in test_body_lines)
        has_then_comment = any('# Then' in line or '# Assert' in line for line in test_body_lines)
        
        # Check for AAA method names (given_*, when_*, then_*)
        has_given_method = False
        has_when_method = False
        has_then_method = False
        
        # Walk AST to find function calls
        for node in ast.walk(test_node):
            if isinstance(node, ast.Call):
                # Get function name from call
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.given_something()
                    func_name = node.func.attr
                
                if func_name:
                    if func_name.startswith('given_'):
                        has_given_method = True
                    elif func_name.startswith('when_'):
                        has_when_method = True
                    elif func_name.startswith('then_'):
                        has_then_method = True
        
        # Combine comment and method checks
        has_given = has_given_comment or has_given_method
        has_when = has_when_comment or has_when_method
        has_then = has_then_comment or has_then_method
        
        # Check if there's actual code (not just comments and pass)
        has_actual_code = False
        if test_node.body:
            for stmt in test_node.body:
                if isinstance(stmt, ast.Pass):
                    continue
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                    # Skip docstrings
                    continue
                else:
                    # Check for actual executable statements
                    for node in ast.walk(stmt):
                        if isinstance(node, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise)):
                            has_actual_code = True
                            break
                    if has_actual_code:
                        break
        
        # Violation if missing AAA structure
        if not (has_given and has_when and has_then):
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Test "{test_node.name}" does not follow Arrange-Act-Assert structure - add # Given/When/Then comments or use given_*/when_*/then_* method names',
                location=str(file_path),
                line_number=line_number,
                severity='error'
            ).to_dict()
        
        # Violation if has AAA comments but no actual code
        if not has_actual_code:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Test "{test_node.name}" has AAA comments but no actual code - tests must call production code, not just contain comments and pass statements',
                location=str(file_path),
                line_number=line_number,
                severity='error'
            ).to_dict()
        
        return None

