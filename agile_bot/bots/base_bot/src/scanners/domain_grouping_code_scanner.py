"""Scanner for validating domain grouping in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class DomainGroupingCodeScanner(CodeScanner):
    """Validates that code is organized by domain area, not technical layers."""
    
    TECHNICAL_LAYER_PATTERNS = [
        r'\blayer\b',
        r'\btier\b',
        r'\bservice\b',
        r'\brepository\b',
        r'\bdto\b',
    ]
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Check file path for technical layer patterns
        file_path_str = str(file_path)
        for pattern in self.TECHNICAL_LAYER_PATTERNS:
            if re.search(pattern, file_path_str, re.IGNORECASE):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'File path "{file_path}" uses technical layer terminology. Organize by domain area instead.',
                        location=str(file_path),
                        line_number=None,
                        severity='info'
                    ).to_dict()
                )
                break
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    violation = self._check_class_name(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_class_name(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if class name uses technical layer terminology."""
        class_name_lower = class_node.name.lower()
        
        for pattern in self.TECHNICAL_LAYER_PATTERNS:
            if re.search(pattern, class_name_lower):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Class "{class_node.name}" uses technical layer terminology. Group by domain area instead.',
                    location=str(file_path),
                    line_number=class_node.lineno,
                    severity='info'
                ).to_dict()
        
        return None


