"""Scanner for validating exception classification by caller needs."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class ExceptionClassificationScanner(CodeScanner):
    """Validates exceptions are classified by caller needs (not by component)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for component-based exception naming (should be caller-need-based)
            violations.extend(self._check_exception_naming(tree, content, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_exception_naming(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if exceptions are named by component (bad) vs caller needs (good)."""
        violations = []
        
        # Component-based exception patterns (bad)
        component_patterns = [
            r'Database\w+Exception',
            r'File\w+Exception',
            r'Network\w+Exception',
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in component_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} defines component-based exception - exceptions should be classified by how caller handles them, not by component',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

