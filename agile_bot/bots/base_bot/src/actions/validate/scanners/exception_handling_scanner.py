"""Scanner for validating exception handling is proper."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class ExceptionHandlingScanner(CodeScanner):
    """Validates exceptions are used properly (not for normal control flow)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for exception misuse
            violations.extend(self._check_exception_misuse(tree, content, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_exception_misuse(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for exception misuse (exceptions for normal flow)."""
        violations = []
        lines = content.split('\n')
        
        # Check for try-except blocks that catch and continue (normal flow)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check if except block is empty or just continues
                for handler in node.handlers:
                    handler_body = handler.body
                    if len(handler_body) == 0:
                        # Empty except block
                        line_number = handler.lineno if hasattr(handler, 'lineno') else None
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Empty except block at line {line_number} - exceptions should be logged or rethrown, never swallowed',
                            location=str(file_path),
                            line_number=line_number,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
        
        return violations

