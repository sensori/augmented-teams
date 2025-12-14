"""Scanner for detecting bad comments (commented-out code, outdated, misleading)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from .code_scanner import CodeScanner
from .violation import Violation


class BadCommentsScanner(CodeScanner):
    """Detects bad comments: commented-out code, outdated comments, misleading comments.
    
    CRITICAL: Some comments actively harm readability. Delete commented-out code (it's in git),
    remove misleading or outdated comments, and eliminate redundant noise.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for commented-out code blocks
            violations.extend(self._check_commented_code(lines, file_path, rule_obj))
            
            # Check for HTML markup in comments
            violations.extend(self._check_html_in_comments(lines, file_path, rule_obj))
            
            # Check for misleading TODO comments
            violations.extend(self._check_misleading_todos(lines, file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_commented_code(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for commented-out code blocks.
        
        Only flags actual commented-out code, not comments that mention code keywords.
        Looks for actual executable code syntax patterns.
        """
        violations = []
        commented_block_start = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for commented lines
            if stripped.startswith('//') or stripped.startswith('#'):
                comment_content = stripped[2:].strip()
                
                # Only flag if this looks like actual executable code, not just a comment mentioning code
                if self._is_actual_commented_code(comment_content, lines, line_num):
                    if commented_block_start is None:
                        commented_block_start = line_num
                elif commented_block_start:
                    # Continue commented block if previous line was commented code
                    prev_comment = lines[line_num - 2].strip() if line_num > 1 else ""
                    if (prev_comment.startswith('//') or prev_comment.startswith('#')) and \
                       self._is_actual_commented_code(prev_comment[2:].strip(), lines, line_num - 1):
                        # Continue block
                        pass
                    else:
                        # End of commented block
                        if commented_block_start:
                            violation = Violation(
                                rule=rule_obj,
                                violation_message=f'Line {commented_block_start} has commented-out code - call production code directly, even if API doesn\'t exist yet',
                                location=str(file_path),
                                line_number=commented_block_start,
                                severity='warning'
                            ).to_dict()
                            violations.append(violation)
                            commented_block_start = None
                else:
                    # Not commented code, reset
                    commented_block_start = None
            else:
                # Not a comment line - end any commented block
                if commented_block_start:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {commented_block_start} has commented-out code - call production code directly, even if API doesn\'t exist yet',
                        location=str(file_path),
                        line_number=commented_block_start,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    commented_block_start = None
        
        # Check for any remaining commented block at end of file
        if commented_block_start:
            violation = Violation(
                rule=rule_obj,
                violation_message=f'Line {commented_block_start} has commented-out code - call production code directly, even if API doesn\'t exist yet',
                location=str(file_path),
                line_number=commented_block_start,
                severity='warning'
            ).to_dict()
            violations.append(violation)
        
        return violations
    
    def _is_actual_commented_code(self, comment_content: str, lines: List[str], line_num: int) -> bool:
        """Check if comment content is actual executable code, not just a comment about code.
        
        Returns True only if the comment contains actual code syntax patterns AND
        there's no production code immediately following it (which would indicate it's explanatory).
        """
        if not comment_content:
            return False
        
        # Check if there's production code immediately after this comment (within 2 lines)
        # If so, this is likely an explanatory comment, not commented-out code
        for i in range(1, min(3, len(lines) - line_num + 1)):
            if line_num + i - 1 < len(lines):
                next_line = lines[line_num + i - 1].strip()
                # Skip empty lines and comment lines
                if next_line and not next_line.startswith('//') and not next_line.startswith('#'):
                    # Check for actual code patterns (not just whitespace or docstrings)
                    if re.search(r'\b(def|class|if|for|while|return|import|from|=\s*[^=]|\(|\[|\{)\b', next_line):
                        # There's production code right after - this comment is explanatory
                        return False
        
        # Patterns that indicate actual executable code (not just mentions of code concepts)
        # These must be strict - looking for actual code syntax, not just keywords
        code_patterns = [
            # Variable assignments with actual assignment operator (not ==)
            r'^\s*\w+\s*=\s*[^=]',  # var = value (but not ==)
            r'\w+\s*\+=\s*',         # += operator
            r'\w+\s*-=\s*',          # -= operator
            r'\w+\s*\*=\s*',         # *= operator
            r'\w+\s*/=\s*',          # /= operator
            
            # Function/class definitions with proper syntax (must have opening paren or colon)
            r'\b(def|function|class|const|let|var)\s+\w+\s*[\(:]',  # def func( or class X:
            
            # Function calls with parentheses and arguments
            r'\w+\s*\([^)]+\)',      # function_call(args) - must have args
            r'\w+\.\w+\s*\(',        # obj.method(
            
            # Control flow with proper syntax and conditions
            r'\bif\s+[^:]+:',        # if condition: (Python)
            r'\bif\s*\([^)]+\)',     # if (condition) (JS/C)
            r'\bfor\s+[^:]+:',       # for item in items: (Python)
            r'\bfor\s*\([^)]+\)',    # for (init; condition; inc) (JS/C)
            r'\bwhile\s+[^:]+:',     # while condition: (Python)
            r'\bwhile\s*\([^)]+\)',  # while (condition) (JS/C)
            
            # Return statements with values
            r'\breturn\s+[^;]+;',    # return value; (with semicolon)
            r'\breturn\s+[^#\n]+$',  # return value (end of line, Python)
            
            # Array/object literals with content
            r'\[[^\]]+\]',           # [array with items]
            r'\{[^}]+\}',            # {object with props}
            
            # Operators and expressions (must have actual operators)
            r'[+\-*/%]=\s*\w',       # +=, -=, etc.
            r'\w+\s*[+\-*/%]\s*\w',  # arithmetic operations
            r'\w+\s*(==|!=|<=|>=|<|>)\s*\w',  # comparisons
            
            # Method chaining (multiple dots)
            r'\w+\.\w+\.\w+',        # obj.method.chain
            
            # Import/require statements
            r'^\s*(import|from|require)\s+',
        ]
        
        # Check if comment matches actual code patterns
        for pattern in code_patterns:
            if re.search(pattern, comment_content):
                # Additional check: exclude comments that are clearly explanatory text
                # These patterns suggest explanatory comments, not actual code
                explanatory_patterns = [
                    r'^\s*(case|return|tuple|is|are|will|should|does|do|use|create|set|get)\s+\w+',
                    r'^\s*\w+\s+(case|is|are|will|should|does|do)',
                    r'^\s*#\s*(Default|Likely|Use|Create|Set|Get|Ensure|Check)',
                ]
                
                is_explanatory = False
                for exp_pattern in explanatory_patterns:
                    if re.search(exp_pattern, comment_content, re.IGNORECASE):
                        # Might be explanatory - only flag if it has clear code syntax
                        if not re.search(r'[=\(\)\[\]\{\}\+\-\*/%;]', comment_content):
                            is_explanatory = True
                            break
                
                if not is_explanatory:
                    return True
        
        return False
    
    def _check_html_in_comments(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for HTML markup in comments."""
        violations = []
        
        html_patterns = [
            r'<p>', r'</p>', r'<ul>', r'</ul>', r'<li>', r'</li>',
            r'<div>', r'</div>', r'<span>', r'</span>', r'<br>', r'<br/>'
        ]
        
        for line_num, line in enumerate(lines, 1):
            if '//' in line or '#' in line or '/*' in line:
                for pattern in html_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Line contains HTML markup in comment - remove HTML, use plain text',
                            location=str(file_path),
                            line_number=line_num,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations
    
    def _check_misleading_todos(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for misleading TODO comments."""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                # Check if TODO says "needs to be implemented" but code exists
                if 'needs to be implemented' in line.lower() or 'not implemented' in line.lower():
                    # Check next few lines for actual implementation
                    next_lines = lines[line_num:line_num+5]
                    has_implementation = any(
                        re.search(r'\b(function|def|class|return|if|for|while)\b', l)
                        for l in next_lines
                    )
                    
                    if has_implementation:
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Misleading TODO comment: "{line.strip()}" - code IS implemented, update or delete TODO',
                            location=str(file_path),
                            line_number=line_num,
                            severity='warning'
                        ).to_dict()
                        violations.append(violation)
        
        return violations

