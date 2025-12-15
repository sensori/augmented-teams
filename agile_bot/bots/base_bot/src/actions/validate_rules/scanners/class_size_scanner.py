"""Scanner for validating class size (keep classes small)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class ClassSizeScanner(CodeScanner):
    """Validates classes are small and free of dead code.
    
    Keep classes under 200-300 lines.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    violation = self._check_class_size(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_class_size(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if class exceeds size limit."""
        # Calculate class size (end_lineno - lineno + 1)
        if hasattr(class_node, 'end_lineno') and class_node.end_lineno:
            class_size = class_node.end_lineno - class_node.lineno + 1
        else:
            # Fallback: estimate from body
            class_size = len(class_node.body) * 10  # Rough estimate
        
        if class_size > 300:
            line_number = class_node.lineno if hasattr(class_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Class "{class_node.name}" is {class_size} lines - should be under 300 lines (extract related methods into separate classes)',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        return None

