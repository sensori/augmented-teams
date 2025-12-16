"""Scanner for detecting incomplete refactoring (old and new patterns coexisting)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class CompleteRefactoringScanner(CodeScanner):
    """Detects incomplete refactoring (old and new patterns coexisting)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for commented-out old code (incomplete refactoring)
            violations.extend(self._check_commented_old_code(lines, file_path, rule_obj))
            
            # Check for conditional logic supporting both old and new patterns
            violations.extend(self._check_dual_pattern_support(content, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_commented_old_code(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for commented-out old code (incomplete refactoring)."""
        violations = []
        commented_block_start = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('//') or stripped.startswith('#'):
                # Check for commented-out function/class definitions
                if re.search(r'\b(function|def|class|const|let|var)\s+\w+', stripped):
                    if commented_block_start is None:
                        commented_block_start = line_num
            else:
                # End of commented block
                if commented_block_start:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Commented-out old code found (lines {commented_block_start}-{line_num-1}) - complete refactoring by deleting old code',
                        location=str(file_path),
                        line_number=commented_block_start,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    commented_block_start = None
        
        return violations
    
    def _check_dual_pattern_support(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for conditional logic supporting both old and new patterns."""
        violations = []
        
        # Patterns that suggest dual pattern support
        dual_pattern_patterns = [
            r'if\s*\(.*old.*\)|if\s*\(.*legacy.*\)|if\s*\(.*deprecated.*\)',
            r'#\s*Old\s+way|#\s*Legacy|#\s*Deprecated',
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in dual_pattern_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} supports both old and new patterns - complete refactoring by removing old pattern support',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

