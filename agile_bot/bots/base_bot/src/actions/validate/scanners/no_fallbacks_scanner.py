"""Scanner for detecting fallback/default values in tests."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class NoFallbacksScanner(TestScanner):
    """Detects fallback/default values in tests.
    
    Tests should not use fallback/default values - use explicit test data.
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for fallback patterns
            violations.extend(self._check_fallback_patterns(lines, test_file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_fallback_patterns(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for fallback/default value patterns."""
        violations = []
        
        fallback_patterns = [
            r'\bor\s+[A-Z]\w+\(\)',  # or DefaultValue()
            r'\bdefault\s*=',  # default =
            r'\bfallback\s*=',  # fallback =
            r'\bor\s+None',  # or None (as fallback)
            r'\bif\s+.*\s+else\s+["\']',  # if ... else "default"
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in fallback_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} uses fallback/default value - tests should use explicit test data, not fallbacks',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

