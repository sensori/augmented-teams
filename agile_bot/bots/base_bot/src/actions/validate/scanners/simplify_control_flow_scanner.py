"""Scanner for validating control flow is simple."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class SimplifyControlFlowScanner(CodeScanner):
    """Validates control flow is simple (minimal nesting, guard clauses)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_nesting_depth(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_nesting_depth(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function has excessive nesting."""
        max_depth = self._get_max_nesting_depth(func_node)
        
        if max_depth > 3:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Function "{func_node.name}" has nesting depth of {max_depth} - use guard clauses and extract nested blocks to reduce nesting',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        return None
    
    def _get_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in function."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._get_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, depth)
        
        return max_depth

