"""Scanner for validating third-party code is isolated."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class ThirdPartyIsolationScanner(CodeScanner):
    """Validates third-party code is isolated (wrapped behind interfaces)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for third-party imports used directly in business logic
            violations.extend(self._check_third_party_usage(lines, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_third_party_usage(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for direct third-party API usage (should be wrapped)."""
        violations = []
        
        # Common third-party libraries that should be wrapped
        third_party_patterns = [
            r'from\s+requests\s+import',  # HTTP library
            r'from\s+boto3\s+import',  # AWS SDK
            r'from\s+sqlalchemy\s+import',  # ORM
            r'import\s+requests',  # HTTP library
            r'import\s+boto3',  # AWS SDK
        ]
        
        # Check imports
        has_third_party_import = False
        for line_num, line in enumerate(lines, 1):
            for pattern in third_party_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    has_third_party_import = True
                    # Check if it's used directly (not wrapped)
                    # This is a simplified check - could be enhanced
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} imports third-party library directly - wrap third-party APIs behind your own interfaces',
                        location=str(file_path),
                        line_number=line_num,
                        severity='info'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

