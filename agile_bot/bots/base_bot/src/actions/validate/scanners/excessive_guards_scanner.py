"""Scanner for detecting excessive guard clauses in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class ExcessiveGuardsScanner(CodeScanner):
    """Detects guard clauses that check for None/existence, adding cyclomatic complexity.
    
    Guards that only check if variables exist or are None make code harder to read
    and hide problems. Error handling should be centralized rather than scattered
    throughout the code. Let code fail fast with clear errors rather than silently
    handling missing components.
    
    Detects:
    - hasattr() checks before attribute access
    - File existence checks before file operations
    - Variable truthiness checks (if not X:, if X:)
    - None checks (if X is None:, if X is not None:)
    - Guard clauses that silently return None/empty
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for excessive guards using AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip test functions (covered by NoGuardClausesScanner)
                    if node.name.startswith('test_'):
                        continue
                    
                    # Skip private methods (they might need guards for internal validation)
                    if node.name.startswith('_') and node.name != '__init__':
                        continue
                    
                    func_violations = self._check_function_guards(node, file_path, rule_obj, lines)
                    violations.extend(func_violations)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_function_guards(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, source_lines: List[str]) -> List[Dict[str, Any]]:
        """Check a function for guard clauses that check for None/existence."""
        violations = []
        
        # Find all guard clause patterns in function
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                if self._is_guard_clause(node, source_lines):
                    violation = self._check_guard_pattern(node, file_path, rule_obj, source_lines)
                    if violation:
                        violations.append(violation)
        
        return violations
    
    def _is_guard_clause(self, if_node: ast.If, source_lines: List[str]) -> bool:
        """Check if an if statement is a guard clause pattern."""
        # Guard clauses typically:
        # 1. Return early or set default values
        # 2. Check for None/existence/type
        # 3. Have simple bodies (return, continue, break, or single assignment)
        
        # Check if body is simple (return, continue, break, or single statement)
        body_is_simple = len(if_node.body) == 1
        if body_is_simple:
            first_stmt = if_node.body[0]
            is_early_exit = isinstance(first_stmt, (ast.Return, ast.Continue, ast.Break))
            is_simple_assign = isinstance(first_stmt, ast.Assign) and len(first_stmt.targets) == 1
            
            if is_early_exit or is_simple_assign:
                # Check if test is a guard pattern
                return self._is_guard_pattern(if_node.test)
        
        return False
    
    def _is_guard_pattern(self, test_node: ast.AST) -> bool:
        """Check if test expression matches guard clause patterns."""
        # hasattr() checks
        if isinstance(test_node, ast.Call):
            if isinstance(test_node.func, ast.Name):
                if test_node.func.id == 'hasattr':
                    return True
        
        # isinstance() checks (defensive, not polymorphic)
        if isinstance(test_node, ast.Call):
            if isinstance(test_node.func, ast.Name):
                if test_node.func.id == 'isinstance':
                    return True
        
        # File existence checks
        if isinstance(test_node, ast.Call):
            if isinstance(test_node.func, ast.Attribute):
                if test_node.func.attr == 'exists':
                    return True
        
        # Variable truthiness checks (if variable:, if not variable:)
        if isinstance(test_node, ast.Name):
            return True
        if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
            if isinstance(test_node.operand, ast.Name):
                return True
        
        # Comparison with None
        if isinstance(test_node, ast.Compare):
            for op in test_node.ops:
                if isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
                    for comparator in test_node.comparators:
                        if isinstance(comparator, ast.Constant) and comparator.value is None:
                            return True
                        if isinstance(comparator, ast.NameConstant) and comparator.value is None:
                            return True
        
        return False
    
    def _check_guard_pattern(self, guard_node: ast.If, file_path: Path, rule_obj: Any, source_lines: List[str]) -> Optional[Dict[str, Any]]:
        """Check specific guard clause patterns and return violation if found."""
        test = guard_node.test
        
        # hasattr() check
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == 'hasattr':
            return Violation(
                rule=rule_obj,
                violation_message=f'Line {guard_node.lineno}: hasattr() guard clause detected. Assume attributes exist - let AttributeError propagate if missing.',
                location=str(file_path),
                line_number=guard_node.lineno,
                severity='warning'
            ).to_dict()
        
        # File existence check
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Attribute) and test.func.attr == 'exists':
            return Violation(
                rule=rule_obj,
                violation_message=f'Line {guard_node.lineno}: File existence check detected. Let file operations fail if file missing - handle errors centrally.',
                location=str(file_path),
                line_number=guard_node.lineno,
                severity='warning'
            ).to_dict()
        
        # None checks (if X is None:, if X is not None:)
        if isinstance(test, ast.Compare):
            for op in test.ops:
                if isinstance(op, (ast.Is, ast.IsNot)):
                    for comparator in test.comparators:
                        if isinstance(comparator, ast.Constant) and comparator.value is None:
                            return Violation(
                                rule=rule_obj,
                                violation_message=f'Line {guard_node.lineno}: None check guard clause detected. Assume variables are initialized - let code fail fast if None.',
                                location=str(file_path),
                                line_number=guard_node.lineno,
                                severity='warning'
                            ).to_dict()
                        if isinstance(comparator, ast.NameConstant) and comparator.value is None:
                            return Violation(
                                rule=rule_obj,
                                violation_message=f'Line {guard_node.lineno}: None check guard clause detected. Assume variables are initialized - let code fail fast if None.',
                                location=str(file_path),
                                line_number=guard_node.lineno,
                                severity='warning'
                            ).to_dict()
        
        # Variable truthiness checks (if not X:, if X:)
        if isinstance(test, ast.Name):
            return Violation(
                rule=rule_obj,
                violation_message=f'Line {guard_node.lineno}: Variable truthiness check detected (if {self._get_variable_name(test)}:). Assume variable exists - let code fail fast if missing.',
                location=str(file_path),
                line_number=guard_node.lineno,
                severity='warning'
            ).to_dict()
        
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Name):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Line {guard_node.lineno}: Variable truthiness check detected (if not {self._get_variable_name(test.operand)}:). Assume variable exists - let code fail fast if missing.',
                    location=str(file_path),
                    line_number=guard_node.lineno,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _get_variable_name(self, node: ast.AST) -> str:
        """Extract variable name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        return 'variable'

