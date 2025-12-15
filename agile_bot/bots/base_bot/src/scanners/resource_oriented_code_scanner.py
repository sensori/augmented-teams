"""Scanner for validating resource-oriented design in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class ResourceOrientedCodeScanner(CodeScanner):
    """Validates that code uses resource-oriented design instead of manager/doer/loader patterns."""
    
    MANAGER_PATTERNS = ['Manager', 'Loader', 'Handler', 'Doer', 'Processor', 'Executor']
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    violation = self._check_resource_oriented(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_resource_oriented(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if class follows resource-oriented design."""
        class_name = class_node.name
        
        # Check if class name indicates manager pattern
        for pattern in self.MANAGER_PATTERNS:
            if class_name.endswith(pattern):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Class "{class_name}" uses manager/doer/loader pattern. Use resource-oriented design instead (e.g., "{class_name.replace(pattern, "")}").',
                    location=str(file_path),
                    line_number=class_node.lineno,
                    severity='error'
                ).to_dict()
        
        return None


