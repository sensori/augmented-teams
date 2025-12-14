"""Scanner for detecting useless comments in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from .code_scanner import CodeScanner
from .violation import Violation


class UselessCommentsScanner(CodeScanner):
    """Detects useless AI-generated comments and docstrings.
    
    CRITICAL: Most comments are useless. Kill AI-generated docstrings that just
    repeat function names and parameters. Only write comments for complex
    non-obvious algorithms, business rules, warnings, or legal notices.
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for useless docstrings
            violations.extend(self._check_useless_docstrings(content, file_path, rule_obj))
            
            # Check for useless inline comments
            violations.extend(self._check_useless_comments(lines, file_path, rule_obj))
            
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_useless_docstrings(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for useless docstrings that repeat function/class names."""
        violations = []
        
        # Pattern for docstrings (triple quotes)
        docstring_pattern = r'"""(.*?)"""'
        matches = re.finditer(docstring_pattern, content, re.DOTALL)
        
        for match in matches:
            docstring_content = match.group(1).strip()
            
            # Check if docstring is useless
            if self._is_useless_docstring(docstring_content, content, match.start()):
                line_number = content[:match.start()].count('\n') + 1
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Useless docstring that repeats function/class name - delete it or explain WHY, not WHAT',
                    location=str(file_path),
                    line_number=line_number,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _check_useless_comments(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for useless inline comments."""
        violations = []
        
        useless_patterns = [
            r'#\s*(Load|Get|Set|Return|Execute|Perform|Handle|Process|Create|Delete|Update)\s+\w+',  # Obvious action comments
            r'#\s*(This|The)\s+(function|method|class|variable)\s+(does|gets|sets|returns)',  # "This function does X"
            r'#\s*(end|End)\s+(if|for|while|class|function)',  # Closing brace comments
            r'#\s*=\s*{10,}',  # Section dividers
            r'#\s*(Changed|Modified|Added|Removed)\s+by:',  # Change history
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip empty lines and non-comment lines
            if not line_stripped.startswith('#'):
                continue
            
            # Check if comment is actually useful (explains WHY, not WHAT)
            if self._is_useful_comment(line_stripped, lines, line_num):
                continue
            
            # Check against useless patterns
            for pattern in useless_patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Useless comment: "{line_stripped[:60]}" - delete it or improve the code instead',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations
    
    def _is_useful_comment(self, comment_line: str, lines: List[str], line_num: int) -> bool:
        """Check if comment is actually useful (explains WHY, not WHAT).
        
        Useful comments explain:
        - Business rules or domain logic
        - Non-obvious algorithms
        - Warnings or gotchas
        - Legal notices or licensing
        - TODO/FIXME with context
        """
        comment_lower = comment_line.lower()
        
        # Check for useful comment patterns
        useful_patterns = [
            r'(because|since|due to|as|when|if|unless)',  # Explains reason
            r'(warning|caution|note|important|critical)',  # Warnings/notes
            r'(todo|fixme|hack|workaround)',  # TODO/FIXME with context
            r'(license|copyright|legal)',  # Legal notices
            r'(algorithm|complex|non-obvious)',  # Complex logic explanation
            r'(business rule|domain|requirement)',  # Business logic
        ]
        
        for pattern in useful_patterns:
            if re.search(pattern, comment_lower):
                return True
        
        # Check if comment explains something non-obvious in the following code
        # (e.g., "Skip test files" before a conditional)
        if line_num < len(lines):
            next_line = lines[line_num].strip() if line_num < len(lines) else ""
            # If comment is followed by non-obvious code (if/for/while with complex condition), it might be useful
            if re.search(r'\b(if|for|while|with)\s+[^:]+:', next_line):
                # Comment might be explaining the condition
                return True
        
        return False
    
    def _is_useless_docstring(self, docstring: str, content: str, docstring_start: int) -> bool:
        """Check if docstring is useless (just repeats function/class name)."""
        # Get function/class name from context
        before_docstring = content[:docstring_start]
        
        # Find function/class definition before docstring
        func_match = re.search(r'def\s+(\w+)\s*\(', before_docstring)
        class_match = re.search(r'class\s+(\w+)', before_docstring)
        
        name = None
        if func_match:
            name = func_match.group(1)
        elif class_match:
            name = class_match.group(1)
        
        if not name:
            return False
        
        # Check if docstring just repeats the name
        docstring_lower = docstring.lower()
        name_lower = name.lower()
        
        # Common useless patterns
        useless_patterns = [
            f'{name_lower}\\s+with\\s+given\\s+parameters',  # "function_name with given parameters"
            f'(execute|perform|handle|process|get|set|return|create|delete|update)\\s+{name_lower}',  # "Execute function_name"
            f'{name_lower}\\s+(function|method|class)',  # "function_name function"
            f'get\\s+the\\s+{name_lower}',  # "Get the function_name"
            f'return\\s+the\\s+{name_lower}',  # "Return the function_name"
        ]
        
        for pattern in useless_patterns:
            if re.search(pattern, docstring_lower):
                return True
        
        # Check if docstring is just Args/Returns boilerplate
        if 'args:' in docstring_lower and 'returns:' in docstring_lower:
            # Check if Args/Returns just restate parameter names/types
            if len(docstring.split('\n')) < 5:  # Very short docstring with Args/Returns
                return True
        
        return False

