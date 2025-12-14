"""Scanner for validating tests match specification scenarios."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class SpecificationMatchScanner(TestScanner):
    """Validates test methods, variables, and assertions match specification scenarios exactly."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Check test method names match specification
            violations.extend(self._check_test_method_names(tree, test_file_path, rule_obj))
            
            # Check variable names match specification (exact names)
            violations.extend(self._check_variable_names(tree, content, test_file_path, rule_obj))
            
            # Check assertions match specification exactly
            violations.extend(self._check_assertions(tree, content, test_file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_test_method_names(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check test method names describe behavior from specification.
        
        Test method names should clearly describe what behavior is being tested,
        matching the specification scenario. Vague names like 'test_init' or 'test_agent'
        are flagged.
        """
        violations = []
        
        vague_patterns = [
            r'^test_(init|setup|create|new|get|set|run|execute|do|handle|process|check|verify|test)$',
            r'^test_\w+_(init|setup|create|new|get|set|run|execute|do|handle|process|check|verify)$',
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Check if method name is too vague
                is_vague = False
                for pattern in vague_patterns:
                    if re.match(pattern, node.name, re.IGNORECASE):
                        is_vague = True
                        break
                
                # Also check if it's a thin wrapper delegating to helper
                # (these are acceptable even if name is vague)
                is_thin_wrapper = self._is_thin_wrapper(node)
                
                if is_vague and not is_thin_wrapper:
                    line_number = node.lineno if hasattr(node, 'lineno') else None
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Test method "{node.name}" has vague name - should clearly describe behavior from specification scenario',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations
    
    def _is_thin_wrapper(self, test_node: ast.FunctionDef) -> bool:
        """Check if test method is a thin wrapper delegating to a helper function."""
        # If body is just a single statement (likely a function call), it's a thin wrapper
        if len(test_node.body) == 1:
            stmt = test_node.body[0]
            # Check if it's a function call or expression statement with a call
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                return True
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
                return True
        return False
    
    def _check_variable_names(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check variable names match specification exactly.
        
        Flags generic variable names that don't match specification terminology.
        Test variables should use exact names from specification (e.g., 'agent_name' not 'name').
        """
        violations = []
        
        # Generic names that suggest mismatch with specification
        generic_names = ['data', 'result', 'value', 'item', 'obj', 'thing', 'name', 'root', 'path', 'config']
        
        # Extract test methods to check variable names within them
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node)
        
        for test_method in test_methods:
            # Check variable assignments in this test method
            for child in ast.walk(test_method):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # Check if it's a generic name
                            if var_name.lower() in generic_names:
                                # Check if it's part of a helper function call (these are OK)
                                if not self._is_in_helper_call(child, test_method):
                                    line_number = child.lineno if hasattr(child, 'lineno') else None
                                    violation = Violation(
                                        rule=rule_obj,
                                        violation_message=f'Line {line_number} uses generic variable name "{var_name}" - use exact variable names from specification',
                                        location=str(file_path),
                                        line_number=line_number,
                                        severity='warning'
                                    ).to_dict()
                                    violations.append(violation)
        
        return violations
    
    def _is_in_helper_call(self, assign_node: ast.Assign, test_method: ast.FunctionDef) -> bool:
        """Check if assignment is part of a helper function call (like verify_* or given_*)."""
        # Check if assignment value is a function call
        if isinstance(assign_node.value, ast.Call):
            func = assign_node.value.func
            if isinstance(func, ast.Name):
                func_name = func.id
                # Helper functions typically start with verify_, given_, when_, then_
                if func_name.startswith(('verify_', 'given_', 'when_', 'then_', 'create_', 'setup_')):
                    return True
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
                if func_name.startswith(('verify_', 'given_', 'when_', 'then_', 'create_', 'setup_')):
                    return True
        return False
    
    def _check_assertions(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check assertions verify exactly what specification states.
        
        Flags assertions that check implementation details (private attributes, internal flags)
        or things not mentioned in specification.
        """
        violations = []
        
        # Patterns that suggest implementation detail assertions
        implementation_patterns = [
            r'\._(private|internal|_flag|_state|_cache)',
            r'\.called\b',  # Mock call checks
            r'\.assert_called',  # Mock assertion
            r'\._validate',  # Internal validation
        ]
        
        # Extract test methods to check assertions within them
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node)
        
        for test_method in test_methods:
            # Check assertions in this test method
            for child in ast.walk(test_method):
                if isinstance(child, ast.Assert):
                    # Get the assertion as a string for pattern matching
                    assertion_line = self._get_assertion_line(child, content, child.lineno)
                    
                    # Check for implementation detail patterns
                    for pattern in implementation_patterns:
                        if re.search(pattern, assertion_line, re.IGNORECASE):
                            line_number = child.lineno if hasattr(child, 'lineno') else None
                            violation = Violation(
                                rule=rule_obj,
                                violation_message=f'Line {line_number} assertion checks implementation detail - verify exactly what specification states, no more, no less',
                                location=str(file_path),
                                line_number=line_number,
                                severity='warning'
                            ).to_dict()
                            violations.append(violation)
                            break
        
        return violations
    
    def _get_assertion_line(self, assert_node: ast.Assert, content: str, line_num: int) -> str:
        """Get the line containing the assertion as a string."""
        lines = content.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""
    
    def scan_story_node(self, node: Any, rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan story node for violations (required by StoryScanner)."""
        return []

