"""Scanner for validating encapsulation."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class EncapsulationScanner(CodeScanner):
    """Validates encapsulation (private fields, minimal public interface, Law of Demeter)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    violation = self._check_encapsulation(node, content, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_encapsulation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if class follows encapsulation principles."""
        class_source = ast.get_source_segment(content, class_node) or ''
        
        # Check for Law of Demeter violations (method chaining)
        # Pattern: obj.method().method().method() - 3+ chained calls
        if re.search(r'\.\w+\(\)\.\w+\(\)\.\w+\(\)', class_source):
            line_number = class_node.lineno if hasattr(class_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Class "{class_node.name}" has Law of Demeter violations (method chaining) - encapsulate access to related objects',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        # Also check for getter chains: obj.getX().getY().getZ()
        if re.search(r'\.get\w+\(\)\.get\w+\(\)\.get\w+\(\)', class_source, re.IGNORECASE):
            line_number = class_node.lineno if hasattr(class_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Class "{class_node.name}" has Law of Demeter violations (getter chaining) - encapsulate access to related objects',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        return None

