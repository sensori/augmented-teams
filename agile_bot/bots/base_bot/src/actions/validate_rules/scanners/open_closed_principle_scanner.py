"""Scanner for validating open-closed principle."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class OpenClosedPrincipleScanner(CodeScanner):
    """Validates open-closed principle (open for extension, closed for modification)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for violations of open-closed principle
            violations.extend(self._check_type_switches(tree, content, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_type_switches(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for type-based if/switch statements (violates open-closed)."""
        violations = []
        lines = content.split('\n')
        
        # Check for type-based conditionals (should use polymorphism)
        type_switch_patterns = [
            r'\.type\s*==',  # obj.type == 'credit'
            r'\.kind\s*==',  # obj.kind == 'user'
            r'\.type\s*!=',  # obj.type != 'credit'
            r'\.kind\s*!=',  # obj.kind != 'user'
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            for pattern in type_switch_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} uses type-based conditional - use polymorphism instead to follow open-closed principle',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

