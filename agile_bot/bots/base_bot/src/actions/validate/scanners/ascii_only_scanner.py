"""Scanner for validating ASCII-only characters in test code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .test_scanner import TestScanner
from .violation import Violation
import re


class AsciiOnlyScanner(TestScanner):
    """Validates all test code uses ASCII-only characters.
    
    No Unicode symbols, emojis, or special characters in test code,
    assertions, print statements, or output messages.
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for Unicode characters (non-ASCII)
                violation = self._check_unicode_characters(line, test_file_path, line_num, rule_obj)
                if violation:
                    violations.append(violation)
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_unicode_characters(self, line: str, file_path: Path, line_num: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check for Unicode characters in line."""
        # Check for non-ASCII characters
        try:
            line.encode('ascii')
        except UnicodeEncodeError:
            # Found non-ASCII characters
            # Find the problematic characters
            unicode_chars = []
            for char in line:
                try:
                    char.encode('ascii')
                except UnicodeEncodeError:
                    unicode_chars.append(char)
            
            if unicode_chars:
                # Common Unicode characters to flag
                problematic = [c for c in unicode_chars if ord(c) > 127]
                if problematic:
                    location = f"{file_path}:{line_num}"
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Line contains Unicode characters: {", ".join(set(problematic[:3]))} - use ASCII alternatives like [PASS], [ERROR], [FAIL]',
                        location=location,
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
        
        return None

