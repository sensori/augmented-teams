"""Scanner for detecting code duplication (DRY principle)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation
import hashlib


class DuplicationScanner(CodeScanner):
    """Detects code duplication.
    
    CRITICAL: Every piece of knowledge should have a single, authoritative representation.
    Extract repeated logic into reusable functions.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Extract function bodies for comparison
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_body = ast.unparse(node.body) if hasattr(ast, 'unparse') else str(node.body)
                    functions.append((node.name, func_body, node.lineno))
            
            # Check for duplicate function bodies
            violations.extend(self._check_duplicate_functions(functions, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_duplicate_functions(self, functions: List[tuple], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for duplicate function bodies."""
        violations = []
        
        # Group functions by body hash
        body_hashes = {}
        for func_name, func_body, line_num in functions:
            body_hash = hashlib.md5(func_body.encode()).hexdigest()
            if body_hash not in body_hashes:
                body_hashes[body_hash] = []
            body_hashes[body_hash].append((func_name, line_num))
        
        # Find duplicates
        for body_hash, func_list in body_hashes.items():
            if len(func_list) > 1:
                # Multiple functions with same body
                func_names = [f[0] for f in func_list]
                line_numbers = [f[1] for f in func_list]
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Duplicate code detected: functions {", ".join(func_names)} have identical bodies - extract to shared function',
                    location=str(file_path),
                    line_number=line_numbers[0],
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations

