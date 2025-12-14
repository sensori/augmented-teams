"""Scanner for validating tests use Given/When/Then helper functions instead of inline code."""

from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class GivenWhenThenHelpersScanner(TestScanner):
    """Validates tests use Given/When/Then helper functions instead of inline code.
    
    Detects violations where test methods contain multiple inline steps that should be
    extracted into reusable Given/When/Then helper functions following the BDD pattern.
    
    The scanner looks for blocks of consecutive code lines (2+) that together form a
    logical step (setup, action, or assertion) but aren't already wrapped in helper
    function calls.
    """
    
    # Minimum number of consecutive non-helper lines to flag as violation
    MIN_INLINE_LINES = 2
    
    # Helper function name patterns (these are OK - code calling these is not a violation)
    HELPER_PATTERNS = [
        r'given_\w+',
        r'when_\w+',
        r'then_\w+',
        r'create_\w+',  # Some create functions are helpers
        r'verify_\w+',  # Some verify functions are helpers
    ]
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Get all helper function names defined in the file and imported
            helper_functions = self._get_helper_functions(tree, content)
            
            # Check each test method
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_violations = self._check_test_method(
                            node, content, test_file_path, rule_obj, helper_functions, tree
                        )
                        violations.extend(test_violations)
        
        except (SyntaxError, UnicodeDecodeError) as e:
            # Skip files with syntax errors - log but don't fail
            violation = Violation(
                rule=rule_obj,
                violation_message=f'File has syntax error, cannot scan: {e}',
                location=str(test_file_path),
                line_number=1,
                severity='warning'
            ).to_dict()
            violations.append(violation)
        
        return violations
    
    def _get_helper_functions(self, tree: ast.AST, content: str) -> Set[str]:
        """Extract all helper function names from the file (defined and imported)."""
        helpers = set()
        
        # Get functions defined in this file
        defined_helpers = self._get_defined_helper_functions(tree)
        helpers.update(defined_helpers.keys())
        
        # Also check for imported helper functions (from conftest, test_helpers, etc.)
        # Look for imports and add any functions that match helper patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Check if importing from common helper modules
                module = node.module or ''
                if any(helper_mod in module for helper_mod in ['conftest', 'test_helpers', '_helpers']):
                    for alias in node.names:
                        name = alias.name
                        for pattern in self.HELPER_PATTERNS:
                            if re.match(pattern, name, re.IGNORECASE):
                                helpers.add(name)
                                break
        
        return helpers
    
    def _get_defined_helper_functions(self, tree: ast.AST) -> Dict[str, int]:
        """Extract helper function names defined in this file (not imported).
        
        Returns:
            Dictionary mapping function name to line number
        """
        helpers = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Check if it matches helper patterns
                for pattern in self.HELPER_PATTERNS:
                    if re.match(pattern, func_name, re.IGNORECASE):
                        helpers[func_name] = node.lineno
                        break
        
        return helpers
    
    def _get_helper_calls_in_file(self, tree: ast.AST, content: str) -> Set[str]:
        """Extract all helper function names that are called in this file.
        
        Returns:
            Set of helper function names that are called
        """
        helper_calls = set()
        helper_functions = self._get_helper_functions(tree, content)
        
        # Walk through all call nodes to find helper function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handle self.given_*() calls
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                        func_name = node.func.attr
                
                if func_name and func_name in helper_functions:
                    helper_calls.add(func_name)
        
        return helper_calls
    
    def _parse_test_file(self, test_file_path: Path) -> Optional[Tuple[str, ast.AST]]:
        """Parse a test file and return its content and AST tree.
        
        Returns:
            Tuple of (content, tree) or None if file cannot be parsed
        """
        if not test_file_path.exists():
            return None
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            return (content, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None
    
    def _check_test_method(self, test_node: ast.FunctionDef, content: str, file_path: Path, 
                          rule_obj: Any, helper_functions: Set[str], tree: ast.AST) -> List[Dict[str, Any]]:
        """Check a test method for inline code blocks that should be extracted."""
        violations = []
        
        # Get test method source lines
        test_lines = content.split('\n')
        start_line = test_node.lineno - 1
        end_line = test_node.end_lineno if hasattr(test_node, 'end_lineno') else len(test_lines)
        
        test_body_lines = test_lines[start_line:end_line]
        
        # Parse the test method body to identify code blocks
        inline_blocks = self._find_inline_code_blocks(test_node, test_body_lines, helper_functions, tree)
        
        # Report violations for blocks that are too long
        for block_start, block_end, block_lines in inline_blocks:
            if len(block_lines) >= self.MIN_INLINE_LINES:
                # Create violation for this block
                block_text = '\n'.join(block_lines[:3])  # Show first 3 lines
                if len(block_lines) > 3:
                    block_text += '\n...'
                
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f'Lines {block_start}-{block_end}: Multiple inline steps ({len(block_lines)} lines) '
                        f'should be extracted into a Given/When/Then helper function. '
                        f'Block:\n{block_text}'
                    ),
                    location=str(file_path),
                    line_number=block_start,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _get_docstring_line_range(self, test_node: ast.FunctionDef) -> Optional[Tuple[int, int]]:
        """Get the line range of the docstring in a function, if it exists.
        
        Returns:
            Tuple of (start_line, end_line) inclusive, or None if no docstring
        """
        if not test_node.body:
            return None
        
        # Check if first statement is a docstring (Expr with Constant/String)
        first_stmt = test_node.body[0]
        if isinstance(first_stmt, ast.Expr):
            # Check for ast.Constant (Python 3.8+) - must be a string
            is_string_literal = (isinstance(first_stmt.value, ast.Constant) and 
                                isinstance(first_stmt.value.value, str))
            # Check for ast.Str (older Python versions)
            if not is_string_literal and hasattr(ast, 'Str'):
                is_string_literal = isinstance(first_stmt.value, ast.Str)
            
            if is_string_literal:
                # This is a docstring
                docstring_start = first_stmt.lineno
                # Use end_lineno if available, otherwise calculate from lineno
                if hasattr(first_stmt, 'end_lineno') and first_stmt.end_lineno:
                    docstring_end = first_stmt.end_lineno
                else:
                    # Fallback: estimate end line from string content
                    # Count newlines in the string value
                    if isinstance(first_stmt.value, ast.Constant):
                        string_value = first_stmt.value.value
                    elif hasattr(ast, 'Str'):
                        string_value = first_stmt.value.s
                    else:
                        string_value = ''
                    newline_count = string_value.count('\n')
                    docstring_end = docstring_start + newline_count
                return (docstring_start, docstring_end)
        
        return None
    
    def _find_inline_code_blocks(self, test_node: ast.FunctionDef, test_body_lines: List[str],
                                 helper_functions: Set[str], tree: ast.AST) -> List[Tuple[int, int, List[str]]]:
        """Find blocks of consecutive inline code (non-helper function calls) in test method."""
        blocks = []
        current_block_start = None
        current_block_lines = []
        
        # Get the actual starting line number of the test method body
        # test_body_lines includes the def line, so body starts at lineno + 1
        body_start_line = test_node.lineno
        
        # Get docstring line range to skip
        docstring_range = self._get_docstring_line_range(test_node)
        
        # Track if we're in a multi-line function call and parenthesis balance
        in_multiline_call = False
        paren_balance = 0
        
        # Parse lines in the test body
        for i, line in enumerate(test_body_lines):
            # Calculate actual line number (test_body_lines starts from def line)
            line_num = body_start_line + i
            stripped = line.strip()
            
            # Skip lines that are part of the docstring
            if docstring_range and docstring_range[0] <= line_num <= docstring_range[1]:
                # If we have a current block, end it
                if current_block_start is not None:
                    blocks.append((current_block_start, line_num - 1, current_block_lines))
                    current_block_start = None
                    current_block_lines = []
                in_multiline_call = False
                paren_balance = 0
                continue
            
            # Skip empty lines, comments, decorators
            if (not stripped or 
                stripped.startswith('#') or 
                stripped.startswith('@')):
                # If we have a current block, end it
                if current_block_start is not None:
                    blocks.append((current_block_start, line_num - 1, current_block_lines))
                    current_block_start = None
                    current_block_lines = []
                # Empty lines don't break multi-line calls
                if in_multiline_call:
                    continue
                in_multiline_call = False
                paren_balance = 0
                continue
            
            # Check if this line starts a helper function call
            is_helper_call_start = self._is_helper_function_call(stripped, helper_functions, tree)
            
            if is_helper_call_start:
                # Start of a helper call - calculate initial paren balance
                paren_balance = stripped.count('(') - stripped.count(')')
                # Mark as multi-line if paren balance > 0
                in_multiline_call = paren_balance > 0
                # End current block if exists
                if current_block_start is not None:
                    blocks.append((current_block_start, line_num - 1, current_block_lines))
                    current_block_start = None
                    current_block_lines = []
            elif in_multiline_call:
                # Continuation of multi-line helper call - update paren balance and skip this line
                paren_balance += stripped.count('(') - stripped.count(')')
                if paren_balance == 0:
                    # End of multi-line call
                    in_multiline_call = False
                continue
            else:
                # This is inline code - add to current block or start new one
                if current_block_start is None:
                    current_block_start = line_num
                current_block_lines.append(stripped)
                paren_balance = 0
        
        # Don't forget the last block
        if current_block_start is not None:
            last_line_num = body_start_line + len(test_body_lines) - 1
            blocks.append((current_block_start, last_line_num, current_block_lines))
        
        return blocks
    
    def _is_helper_function_call(self, line: str, helper_functions: Set[str], tree: ast.AST) -> bool:
        """Check if line is calling a helper function."""
        # Check if any helper function name appears as a function call
        for helper_name in helper_functions:
            # Look for pattern: helper_name( or helper_name = helper_name(
            if re.search(rf'\b{re.escape(helper_name)}\s*\(', line):
                return True
        
        # Also check for method calls on self (class helper methods)
        if re.search(r'self\.(given_|when_|then_)\w+\s*\(', line):
            return True
        
        # Check for helper function patterns even if not in helper_functions set
        # This handles imported helpers that might not be detected
        helper_patterns = [
            r'\b(given_|when_|then_|verify_|create_|setup_|bootstrap_)\w+\s*\(',
            r'self\.(given_|when_|then_|verify_|create_|setup_)\w+\s*\(',
        ]
        for pattern in helper_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _get_defined_helper_functions(self, tree: ast.AST) -> Dict[str, int]:
        """Extract helper function names defined in this file (not imported).
        
        Returns:
            Dictionary mapping function name to line number
        """
        helpers = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Check if it matches helper patterns
                for pattern in self.HELPER_PATTERNS:
                    if re.match(pattern, func_name, re.IGNORECASE):
                        helpers[func_name] = node.lineno
                        break
        
        return helpers
    
    def _get_helper_calls_in_file(self, tree: ast.AST, content: str) -> Set[str]:
        """Extract all helper function names that are called in this file.
        
        Returns:
            Set of helper function names that are called
        """
        helper_calls = set()
        helper_functions = self._get_helper_functions(tree, content)
        
        # Walk through all call nodes to find helper function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handle self.given_*() calls
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                        func_name = node.func.attr
                
                if func_name and func_name in helper_functions:
                    helper_calls.add(func_name)
        
        return helper_calls
    
    def scan_cross_file(
        self,
        rule_obj: Any = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None
    ) -> List[Dict[str, Any]]:
        """Scan across all test files for cross-file violations.
        
        Detects:
        1. Duplicate helper functions across files (should be consolidated)
        
        NOTE: Only reports ERRORS for duplicate definitions. Does NOT generate warnings
        about functions used in multiple files - that's not a problem.
        
        Args:
            rule_obj: Rule object reference
            test_files: List of all test file paths to analyze together
            code_files: Not used by TestScanner
            
        Returns:
            List of violation dictionaries for cross-file issues (only duplicates)
        """
        violations = []
        
        if not test_files or len(test_files) < 2:
            # Need at least 2 files to detect cross-file issues
            return violations
        
        # Reuse base class method to parse all test files
        parsed_files = self._get_all_test_files_parsed(test_files)
        
        # Extract helper function definitions using existing method
        helper_definitions = {}  # func_name -> list of (file_path, line_number)
        
        for test_file_path, content, tree in parsed_files:
            # Reuse existing method to get defined helpers
            defined_helpers = self._get_defined_helper_functions(tree)
            
            for func_name, line_number in defined_helpers.items():
                if func_name not in helper_definitions:
                    helper_definitions[func_name] = []
                helper_definitions[func_name].append((
                    str(test_file_path),
                    line_number
                ))
        
        # Check: Duplicate helper functions across files (ONLY - no usage warnings)
        for func_name, definitions in helper_definitions.items():
            if len(definitions) > 1:
                # Same helper function defined in multiple files - should be consolidated
                files_list = ', '.join([f"{Path(f).name}:{line}" for f, line in definitions])
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f'Helper function "{func_name}" is defined in {len(definitions)} different files. '
                        f'Consolidate into a shared helper file based on reuse scope. '
                        f'Found in: {files_list}'
                    ),
                    location=definitions[0][0],  # First occurrence
                    line_number=definitions[0][1],
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        # DO NOT generate warnings about functions used in multiple files - that's fine
        # Functions can be used across multiple files without being a problem
        
        return violations


