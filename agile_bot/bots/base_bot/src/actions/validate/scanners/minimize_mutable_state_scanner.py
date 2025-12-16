"""Scanner for validating mutable state is minimized."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class MinimizeMutableStateScanner(CodeScanner):
    """Validates mutable state is minimized (prefer immutable data structures)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for mutable patterns
            violations.extend(self._check_mutable_patterns(lines, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_mutable_patterns(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for mutable state patterns."""
        violations = []
        
        mutable_patterns = [
            r'\.push\s*\(',  # Array mutation
            r'\.pop\s*\(',  # Array mutation
            r'\.splice\s*\(',  # Array mutation
            r'\+\+\s*;',  # Increment mutation
            r'--\s*;',  # Decrement mutation
            r'=\s*\{.*\}\s*\.\w+\s*=',  # Object mutation
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in mutable_patterns:
                if re.search(pattern, line):
                    # Check if it's in a test (tests can mutate test data)
                    if 'test_' in line.lower() or 'def test' in line.lower():
                        continue
                    
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} mutates state - prefer immutable data structures (create new objects instead of mutating)',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

