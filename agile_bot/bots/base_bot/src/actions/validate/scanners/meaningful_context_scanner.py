"""Scanner for validating meaningful context is provided in names."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class MeaningfulContextScanner(CodeScanner):
    """Validates names provide meaningful context (no magic numbers, appropriate scope-based naming)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for magic numbers
            violations.extend(self._check_magic_numbers(lines, file_path, rule_obj))
            
            # Check for numbered variables (data1, data2)
            violations.extend(self._check_numbered_variables(content, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_magic_numbers(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for magic numbers (should be named constants)."""
        violations = []
        
        # Common magic numbers that should be constants
        magic_number_patterns = [
            r'\b(200|404|500)\b',  # HTTP status codes
            r'\b(86400|3600|60)\b',  # Time constants (seconds in day/hour/minute)
            r'\b(1024|2048|4096)\b',  # Size constants
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in magic_number_patterns:
                if re.search(pattern, line):
                    # Check if it's already a constant definition
                    if '=' in line and ('const' in line or 'final' in line):
                        continue  # It's a constant definition, not magic number
                    
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} contains magic number - replace with named constant',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations
    
    def _check_numbered_variables(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for numbered variables (data1, data2, etc.)."""
        violations = []
        lines = content.split('\n')
        
        numbered_var_pattern = r'\b\w+\d+\b'  # word followed by number
        
        for line_num, line in enumerate(lines, 1):
            # Check for numbered variables (but exclude test names)
            if re.search(numbered_var_pattern, line):
                # Exclude common patterns that are OK
                if re.search(r'\btest_\w+\d+', line):
                    continue  # Test names are OK
                
                matches = re.findall(numbered_var_pattern, line)
                for match in matches:
                    if match not in ['test1', 'test2']:  # Common test patterns
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Line {line_num} uses numbered variable "{match}" - use meaningful descriptive name',
                            location=str(file_path),
                            line_number=line_num,
                            severity='warning'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations
