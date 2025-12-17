"""Scanner for validating import statements are at the top of files."""

from typing import List, Dict, Any
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class ImportPlacementScanner(CodeScanner):
    """Validates that all import statements are at the top of the file."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan a file for import placement violations.
        
        Args:
            file_path: Path to code file to scan
            rule_obj: Rule object reference
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find the end of the import section (after docstrings/comments)
            import_section_end = self._find_import_section_end(lines)
            
            # Find all import statements and check if they're in the import section
            violations.extend(self._check_import_placement(lines, import_section_end, file_path, rule_obj))
        
        except (UnicodeDecodeError, SyntaxError, Exception):
            # Skip binary files, files with encoding issues, or syntax errors
            pass
        
        return violations
    
    def _find_import_section_end(self, lines: List[str]) -> int:
        """Find the line number where the import section ends.
        
        Import section includes:
        - Module docstring (triple-quoted string at start)
        - Comments
        - Blank lines
        - Import statements
        
        Returns:
            Line number (1-indexed) where import section ends, or len(lines) if all imports
        """
        import_section_end = 0
        
        # Skip leading blank lines
        while import_section_end < len(lines) and not lines[import_section_end].strip():
            import_section_end += 1
        
        # Skip module docstring (triple-quoted string)
        if import_section_end < len(lines):
            line = lines[import_section_end].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Find end of docstring
                quote_char = line[:3]
                import_section_end += 1
                while import_section_end < len(lines):
                    if quote_char in lines[import_section_end]:
                        import_section_end += 1
                        break
                    import_section_end += 1
        
        # Skip blank lines and comments after docstring
        while import_section_end < len(lines):
            line = lines[import_section_end].strip()
            if not line or line.startswith('#'):
                import_section_end += 1
            elif self._is_import_statement(line):
                import_section_end += 1
            else:
                # Found non-import, non-comment, non-blank line - import section ends here
                break
        
        return import_section_end
    
    def _is_import_statement(self, line: str) -> bool:
        """Check if a line is an import statement.
        
        Args:
            line: Line of code to check
            
        Returns:
            True if line is an import statement
        """
        stripped = line.strip()
        return (stripped.startswith('import ') or 
                stripped.startswith('from ') and ' import ' in stripped)
    
    def _check_import_placement(
        self, 
        lines: List[str], 
        import_section_end: int,
        file_path: Path, 
        rule_obj: Any
    ) -> List[Dict[str, Any]]:
        """Check for imports that appear after the import section.
        
        Args:
            lines: All lines in the file
            import_section_end: Line number (1-indexed) where import section should end
            file_path: Path to file being scanned
            rule_obj: Rule object reference
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        # Check each line after the import section for import statements
        for line_num in range(import_section_end, len(lines)):
            line = lines[line_num]
            
            # Skip blank lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check if this line is an import statement
            if self._is_import_statement(line):
                # Found import after import section - violation!
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Import statement found at line {line_num + 1} after non-import code. Move all imports to the top of the file.',
                    location=f'{file_path}:{line_num + 1}',
                    line_number=line_num + 1,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations


