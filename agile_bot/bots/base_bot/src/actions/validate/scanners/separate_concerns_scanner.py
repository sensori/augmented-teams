"""Scanner for validating concerns are separated."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class SeparateConcernsScanner(CodeScanner):
    """Validates concerns are separated (pure logic from side effects, business logic from infrastructure)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_mixed_concerns(node, content, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_mixed_concerns(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function mixes concerns (I/O with calculations, business logic with infrastructure)."""
        func_source = ast.get_source_segment(content, func_node) or ''
        func_source_lower = func_source.lower()
        
        # Check for mixed concerns
        has_calculation = any(keyword in func_source_lower for keyword in ['calculate', 'compute', 'total', 'sum', 'multiply'])
        has_io = any(keyword in func_source_lower for keyword in ['print', 'write', 'read', 'save', 'load', 'open', 'close', 'file'])
        has_db = any(keyword in func_source_lower for keyword in ['query', 'execute', 'commit', 'database', 'sql', 'db.'])
        has_logging = any(keyword in func_source_lower for keyword in ['log', 'logger', 'logging', 'console.log'])
        
        # Mixed concerns: calculation + I/O, business logic + infrastructure
        if has_calculation and (has_io or has_db or has_logging):
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Function "{func_node.name}" mixes calculations with I/O/infrastructure - separate pure logic from side effects',
                location=str(file_path),
                line_number=line_number,
                severity='error'
            ).to_dict()
        
        return None

