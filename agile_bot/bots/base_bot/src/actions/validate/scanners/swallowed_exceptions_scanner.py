"""Scanner for detecting swallowed exceptions."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class SwallowedExceptionsScanner(CodeScanner):
    """Detects swallowed exceptions (empty catch blocks).
    
    CRITICAL: Never swallow exceptions silently.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for swallowed exceptions
            violations.extend(self._check_swallowed_exceptions(tree, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_swallowed_exceptions(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for swallowed exceptions (empty except blocks)."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    # Check if handler body is empty or just 'pass'
                    handler_body = handler.body
                    if len(handler_body) == 0:
                        # Empty except block
                        line_number = handler.lineno if hasattr(handler, 'lineno') else None
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Empty except block at line {line_number} - exceptions must be logged or rethrown, never swallowed',
                            location=str(file_path),
                            line_number=line_number,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
                    elif len(handler_body) == 1:
                        # Check if it's just 'pass'
                        if isinstance(handler_body[0], ast.Pass):
                            line_number = handler.lineno if hasattr(handler, 'lineno') else None
                            violation = Violation(
                                rule=rule_obj,
                                violation_message=f'Except block only contains pass at line {line_number} - exceptions must be logged or rethrown, never swallowed',
                                location=str(file_path),
                                line_number=line_number,
                                severity='error'
                            ).to_dict()
                            violations.append(violation)
        
        return violations

