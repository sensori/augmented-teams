"""Scanner for validating vertical density (related code close together)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class VerticalDensityScanner(CodeScanner):
    """Validates vertical density (related code close together, variables near usage)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_variable_declaration_distance(node, content, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_variable_declaration_distance(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if variables are declared far from usage."""
        # This is a simplified check - could be enhanced
        # For now, check if function is very long (suggests poor vertical density)
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            func_size = func_node.end_lineno - func_node.lineno + 1
            if func_size > 50:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" is {func_size} lines - consider improving vertical density by declaring variables near usage',
                    location=str(file_path),
                    line_number=line_number,
                    severity='info'
                ).to_dict()
        
        return None

