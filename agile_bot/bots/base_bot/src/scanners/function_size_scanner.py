"""Scanner for validating function size (keep functions small)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class FunctionSizeScanner(CodeScanner):
    """Validates functions are small enough to understand at a glance.
    
    Keep functions under 20 lines when possible.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods and special methods
                    if node.name.startswith('_') and node.name != '__init__':
                        continue
                    
                    violation = self._check_function_size(node, file_path, rule_obj, lines)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_function_size(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, source_lines: List[str]) -> Optional[Dict[str, Any]]:
        """Check if function exceeds size limit, excluding data structures, comments, docstrings, and multi-line expressions."""
        # Calculate function size (end_lineno - lineno + 1)
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            func_start_line = func_node.lineno - 1  # Convert to 0-indexed
            func_end_line = func_node.end_lineno  # end_lineno is 1-indexed, exclusive
        else:
            # Fallback: estimate from body
            func_start_line = func_node.lineno - 1
            func_end_line = func_start_line + len(func_node.body) * 3
        
        # Get function source lines
        if func_start_line < len(source_lines) and func_end_line <= len(source_lines):
            func_source_lines = source_lines[func_start_line:func_end_line]
        else:
            func_source_lines = []
        
        # Count lines that should be excluded:
        # 1. Data structures (lists, dicts, sets, tuples)
        data_structure_line_nums = self._get_data_structure_line_numbers(func_node)
        
        # 2. Comments and docstrings
        comment_and_docstring_line_nums = self._get_comment_and_docstring_line_numbers(func_node, func_source_lines, func_start_line)
        
        # 3. Multi-line expressions (single logical line spread across multiple physical lines)
        multi_line_expression_line_nums = self._get_multi_line_expression_line_numbers(func_node)
        
        # Count executable code lines (excluding data structures, comments, docstrings, multi-line expressions)
        executable_lines = 0
        for i, line in enumerate(func_source_lines):
            line_num = func_start_line + i + 1  # Convert back to 1-indexed
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Skip data structure lines
            if line_num in data_structure_line_nums:
                continue
            
            # Skip comment and docstring lines
            if line_num in comment_and_docstring_line_nums:
                continue
            
            # Skip multi-line expression continuation lines (not the first line)
            if line_num in multi_line_expression_line_nums:
                continue
            
            # This is executable code
            executable_lines += 1
        
        if executable_lines > 20:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Function "{func_node.name}" is {executable_lines} lines - should be under 20 lines (extract complex logic to helper functions)',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        return None
    
    def _get_multi_line_expression_line_numbers(self, func_node: ast.FunctionDef) -> set:
        """Get line numbers that are continuations of multi-line expressions.
        
        This identifies lines that are part of a single logical statement spread
        across multiple physical lines (e.g., function calls with parameters,
        method chaining, etc.). Only continuation lines are returned (not the first line).
        
        A multi-line expression counts as 1 logical line, so we exclude continuation lines.
        """
        multi_line_lines = set()
        
        def visit_statement(stmt_node):
            """Visit a statement node and find multi-line expressions within it."""
            # Check if this statement itself spans multiple lines
            if hasattr(stmt_node, 'end_lineno') and hasattr(stmt_node, 'lineno') and stmt_node.end_lineno and stmt_node.lineno:
                if stmt_node.end_lineno > stmt_node.lineno:
                    # This statement spans multiple lines
                    # Check what type of statement it is
                    if isinstance(stmt_node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                        # Assignment statement - check if the value/expression is multi-line
                        if hasattr(stmt_node, 'value') and stmt_node.value:
                            value = stmt_node.value
                            if hasattr(value, 'end_lineno') and hasattr(value, 'lineno') and value.end_lineno and value.lineno:
                                if value.end_lineno > value.lineno:
                                    # Multi-line expression in assignment
                                    # Exclude continuation lines (all except first)
                                    for line_num in range(value.lineno + 1, value.end_lineno + 1):
                                        multi_line_lines.add(line_num)
                    
                    elif isinstance(stmt_node, ast.Expr):
                        # Expression statement (e.g., function call)
                        if hasattr(stmt_node, 'value') and stmt_node.value:
                            value = stmt_node.value
                            if isinstance(value, ast.Call):
                                # Function call - check if it spans multiple lines
                                if hasattr(value, 'end_lineno') and hasattr(value, 'lineno') and value.end_lineno and value.lineno:
                                    if value.end_lineno > value.lineno:
                                        # Multi-line function call - exclude continuation lines
                                        for line_num in range(value.lineno + 1, value.end_lineno + 1):
                                            multi_line_lines.add(line_num)
                    
                    elif isinstance(stmt_node, ast.Return):
                        # Return statement - check if return value is multi-line
                        if stmt_node.value:
                            if hasattr(stmt_node.value, 'end_lineno') and hasattr(stmt_node.value, 'lineno') and stmt_node.value.end_lineno and stmt_node.value.lineno:
                                if stmt_node.value.end_lineno > stmt_node.value.lineno:
                                    # Multi-line return expression
                                    for line_num in range(stmt_node.value.lineno + 1, stmt_node.value.end_lineno + 1):
                                        multi_line_lines.add(line_num)
        
        # Visit each top-level statement in function body
        for stmt in func_node.body:
            visit_statement(stmt)
        
        return multi_line_lines
    
    def _get_data_structure_line_numbers(self, func_node: ast.FunctionDef) -> set:
        """Get line numbers that are part of data structures (lists, dicts, sets, tuples).
        
        This excludes data structure definitions from line count since they're
        configuration/data, not executable logic.
        """
        data_structure_lines = set()  # Use set to avoid double-counting overlapping ranges
        
        # Find all top-level data structures (not nested inside other data structures)
        # We'll collect them and then count their lines
        top_level_data_structures = []
        
        def visit_node(node, parent_is_ds=False):
            """Recursively visit nodes, identifying top-level data structures."""
            is_data_structure = isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple))
            
            if is_data_structure and not parent_is_ds:
                # This is a top-level data structure
                top_level_data_structures.append(node)
            
            # Recursively visit children
            for child in ast.iter_child_nodes(node):
                visit_node(child, parent_is_ds=is_data_structure)
        
        # Start visiting from function body
        for child in ast.iter_child_nodes(func_node):
            visit_node(child, parent_is_ds=False)
        
        # Count lines for each top-level data structure
        for ds_node in top_level_data_structures:
            if hasattr(ds_node, 'end_lineno') and hasattr(ds_node, 'lineno') and ds_node.end_lineno and ds_node.lineno:
                ds_lines = ds_node.end_lineno - ds_node.lineno + 1
                # Only count if it spans multiple lines (single-line data structures are fine)
                if ds_lines > 1:
                    # Add all line numbers in this range to the set
                    for line_num in range(ds_node.lineno, ds_node.end_lineno + 1):
                        data_structure_lines.add(line_num)
        
        return data_structure_lines
    
    def _get_comment_and_docstring_line_numbers(self, func_node: ast.FunctionDef, source_lines: List[str], func_start_line: int) -> set:
        """Get line numbers that are comments or docstrings.
        
        Excludes:
        - Docstrings (string literals that are the first statement)
        - Full comment lines (lines that contain only comments, no code)
        
        Does NOT exclude lines with trailing comments (code + comment on same line).
        """
        comment_and_docstring_lines = set()
        
        # Find docstring (first statement in function body if it's a string literal)
        if func_node.body:
            first_stmt = func_node.body[0]
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, (ast.Str, ast.Constant)):
                # Check if it's a string literal (docstring)
                string_value = first_stmt.value
                if isinstance(string_value, ast.Constant) and isinstance(string_value.value, str):
                    # This is a docstring
                    if hasattr(first_stmt, 'end_lineno') and hasattr(first_stmt, 'lineno') and first_stmt.end_lineno and first_stmt.lineno:
                        for line_num in range(first_stmt.lineno, first_stmt.end_lineno + 1):
                            comment_and_docstring_lines.add(line_num)
                elif isinstance(string_value, ast.Str):
                    # Old-style string literal (Python < 3.8)
                    if hasattr(first_stmt, 'end_lineno') and hasattr(first_stmt, 'lineno') and first_stmt.end_lineno and first_stmt.lineno:
                        for line_num in range(first_stmt.lineno, first_stmt.end_lineno + 1):
                            comment_and_docstring_lines.add(line_num)
        
        # Find full comment lines in the function (lines that are ONLY comments, no code)
        # We need to check within the function's line range
        func_start = func_node.lineno
        func_end = func_node.end_lineno if hasattr(func_node, 'end_lineno') and func_node.end_lineno else func_start + 20
        
        for line_num in range(func_start, func_end + 1):
            if line_num > len(source_lines):
                break
            
            line = source_lines[line_num - 1]  # Convert to 0-indexed
            line_stripped = line.strip()
            
            # Skip empty lines (they're already excluded in the main count)
            if not line_stripped:
                continue
            
            # Check if line is ONLY a comment (starts with # and has no code before it)
            # This handles both # comment and ## comment patterns
            if line_stripped.startswith('#'):
                # Check if there's any code before the comment
                # If the stripped line starts with #, it's a full comment line
                comment_and_docstring_lines.add(line_num)
        
        return comment_and_docstring_lines
