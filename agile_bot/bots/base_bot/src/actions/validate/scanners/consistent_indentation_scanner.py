"""Scanner for validating consistent indentation."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .code_scanner import CodeScanner
from .violation import Violation


class ConsistentIndentationScanner(CodeScanner):
    """Validates indentation is consistent throughout file."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for mixed indentation (tabs vs spaces)
            violations.extend(self._check_mixed_indentation(lines, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_mixed_indentation(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for mixed indentation (tabs and spaces)."""
        violations = []
        
        has_tabs = False
        has_spaces = False
        
        for line_num, line in enumerate(lines, 1):
            if line.startswith('\t'):
                has_tabs = True
            elif line.startswith(' '):
                has_spaces = True
        
        if has_tabs and has_spaces:
            violation = Violation(
                rule=rule_obj,
                violation_message='File mixes tabs and spaces for indentation - use consistent indentation (prefer spaces)',
                location=str(file_path),
                severity='error'
            ).to_dict()
            violations.append(violation)
        
        return violations

