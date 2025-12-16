"""Scanner for validating error handling is isolated."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class ErrorHandlingIsolationScanner(CodeScanner):
    """Validates error handling is isolated from business logic."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for mixed error handling and business logic
            violations.extend(self._check_mixed_error_handling(tree, content, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_mixed_error_handling(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if error handling is mixed with business logic."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has multiple try-except blocks (suggests mixed concerns)
                try_blocks = [n for n in ast.walk(node) if isinstance(n, ast.Try)]
                if len(try_blocks) > 2:
                    line_number = node.lineno if hasattr(node, 'lineno') else None
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Function "{node.name}" has {len(try_blocks)} try-except blocks - extract error handling to separate functions',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

