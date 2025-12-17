"""Scanner for detecting unnecessary guard clauses in tests."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class NoGuardClausesScanner(TestScanner):
    """CRITICAL: Detects guard clauses in test code.
    
    Guard clauses are FORBIDDEN in tests. Tests must assume the code we write
    works correctly. If setup is wrong, tests MUST fail - guard clauses hide
    problems and reduce test reliability. We control test setup, so we assume
    positive outcomes. If different behavior is needed, write a different test.
    
    Detects:
    - File existence checks (if file.exists())
    - Type checks (if isinstance())
    - Attribute checks (if hasattr())
    - Variable truthiness checks (if variable:)
    - Any defensive conditionals in test functions
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            violations.extend(self._check_guard_clause_patterns(lines, test_file_path, rule_obj))
            violations.extend(self._check_ast_guard_clauses(test_file_path, rule_obj))
        
        except (UnicodeDecodeError, SyntaxError, Exception):
            pass
        
        return violations
    
    def _check_guard_clause_patterns(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for guard clause patterns using regex."""
        violations = []
        
        guard_patterns = [
            # File existence checks
            (r'if\s+(not\s+)?\w+\.exists\(\):', 'File existence check - test should fail if file missing'),
            # Type checks (isinstance)
            (r'if\s+(not\s+)?isinstance\([^)]+\):', 'Type check guard clause - test should fail if wrong type'),
            # Attribute checks (hasattr)
            (r'if\s+(not\s+)?hasattr\([^)]+\):', 'Attribute existence check - test should fail if attribute missing'),
            # Variable truthiness checks in test functions
            (r'if\s+(not\s+)?\w+:', 'Variable truthiness check - test should fail if variable is None/empty'),
        ]
        
        in_test_function = False
        test_function_indent = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            # Track if we're in a test function
            if re.match(r'^\s*def\s+test_', line):
                in_test_function = True
                test_function_indent = current_indent
            elif in_test_function and stripped and current_indent <= test_function_indent and not stripped.startswith('@'):
                # We've left the test function
                in_test_function = False
            
            # Only check guard clauses inside test functions
            if not in_test_function:
                continue
            
            # Skip docstrings and comments
            if stripped.startswith('"""') or stripped.startswith("'''") or stripped.startswith('#'):
                continue
            
            # Check each pattern
            for pattern, message in guard_patterns:
                if re.search(pattern, line):
                    # Exclude legitimate assertions (assert isinstance, assert hasattr)
                    if 'assert' in line.lower():
                        continue
                    
                    # Exclude fixture definitions
                    if '@pytest.fixture' in '\n'.join(lines[max(0, line_num-3):line_num]):
                        continue
                    
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num}: CRITICAL - {message}. Guard clauses are FORBIDDEN in tests. Assume test code works - if setup is wrong, let the test fail. Remove the guard clause.',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations
    
    def _check_ast_guard_clauses(self, test_file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for guard clauses using AST parsing."""
        violations = []
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    violations.extend(self._check_function_guard_clauses(node, test_file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError, Exception):
            pass
        
        return violations
    
    def _check_function_guard_clauses(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check a test function for guard clause patterns."""
        violations = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                # Check if this is a guard clause pattern
                guard_patterns = [
                    self._is_file_exists_check,
                    self._is_type_check,
                    self._is_hasattr_check,
                    self._is_variable_truthiness_check,
                ]
                
                for pattern_check in guard_patterns:
                    if pattern_check(node):
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Line {node.lineno}: CRITICAL - Guard clause detected. Guard clauses are FORBIDDEN in tests. Assume test code works correctly - if setup is wrong, let the test fail. Remove defensive checks.',
                            location=str(file_path),
                            line_number=node.lineno,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations
    
    def _is_file_exists_check(self, if_node: ast.If) -> bool:
        """Check if if statement is checking file.exists()."""
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Attribute):
                if if_node.test.func.attr == 'exists':
                    return True
        return False
    
    def _is_type_check(self, if_node: ast.If) -> bool:
        """Check if if statement is checking isinstance()."""
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Name):
                if if_node.test.func.id == 'isinstance':
                    return True
        return False
    
    def _is_hasattr_check(self, if_node: ast.If) -> bool:
        """Check if if statement is checking hasattr()."""
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Name):
                if if_node.test.func.id == 'hasattr':
                    return True
        return False
    
    def _is_variable_truthiness_check(self, if_node: ast.If) -> bool:
        """Check if if statement is checking variable truthiness (simple variable check)."""
        # Simple variable checks like "if variable:" or "if not variable:"
        if isinstance(if_node.test, ast.Name):
            return True
        if isinstance(if_node.test, ast.UnaryOp) and isinstance(if_node.test.op, ast.Not):
            if isinstance(if_node.test.operand, ast.Name):
                return True
        return False

