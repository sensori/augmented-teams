"""Base CodeScanner class for validating source code files."""

from abc import abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path  # Needed at runtime for Path operations
import ast
from .scanner import Scanner
from .violation import Violation


class CodeScanner(Scanner):
    """Base class for code validation scanners.
    
    CodeScanners validate Python/JavaScript source code files against rules.
    Each scanner implements scan_code_file() to check a single file.
    """
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Scan code files for rule violations.
        
        Args:
            knowledge_graph: Story graph structure
            rule_obj: Rule object reference (for creating Violations)
            test_files: List of file paths to scan
            code_files: List of file paths to scan
            
        Returns:
            List of violation dictionaries
        """
        if not rule_obj:
            raise ValueError("rule_obj parameter is required for CodeScanner")
        
        violations = []
        
        # Combine all files to scan - no distinction between test_files and code_files
        all_files = []
        if code_files:
            all_files.extend(code_files)
        if test_files:
            all_files.extend(test_files)
        
        # Scan all files that were passed in
        for file_path in all_files:
            if file_path.exists():
                file_violations = self.scan_code_file(file_path, rule_obj)
                violations.extend(file_violations if isinstance(file_violations, list) else [])
        
        return violations
    
    @abstractmethod
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan a single code file for violations.
        
        Args:
            file_path: Path to code file to scan
            rule_obj: Rule object reference
            
        Returns:
            List of violation dictionaries
        """
        pass
    
    def _extract_domain_terms(self, knowledge_graph: Dict[str, Any]) -> set:
        """Extract domain language terms from story graph, epics, and stories.
        
        This method copies the exact approach from BusinessReadableTestNamesScanner._extract_domain_language.
        If a term appears in the story graph, it's part of the domain language and should be accepted.
        """
        domain_terms = set()
        
        # Add common domain terms that are legitimate in this codebase context
        # These are domain concepts, not technical jargon
        common_domain_terms = {
            'json', 'data', 'param', 'params', 'parameter', 'parameters',
            'var', 'vars', 'variable', 'variables',
            'method', 'methods', 'class', 'classes', 'call', 'calls',
            'config', 'configuration', 'configurations',
            'agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 'action',
            'behavior', 'rule', 'rules', 'validation', 'validate', 'scanner',
            'file', 'files', 'directory', 'directories', 'path', 'paths',
            'state', 'states', 'tool', 'tools', 'server', 'catalog', 'metadata'
        }
        domain_terms.update(common_domain_terms)
        
        if not knowledge_graph:
            return domain_terms
        
        # Extract from epics
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            if isinstance(epic, dict):
                # Epic name
                epic_name = epic.get('name', '')
                if epic_name:
                    domain_terms.update(self._extract_words_from_text(epic_name))
                
                # Sub-epics
                sub_epics = epic.get('sub_epics', [])
                for sub_epic in sub_epics:
                    if isinstance(sub_epic, dict):
                        sub_epic_name = sub_epic.get('name', '')
                        if sub_epic_name:
                            domain_terms.update(self._extract_words_from_text(sub_epic_name))
                        
                        # Stories
                        story_groups = sub_epic.get('story_groups', [])
                        for story_group in story_groups:
                            if isinstance(story_group, dict):
                                stories = story_group.get('stories', [])
                                for story in stories:
                                    if isinstance(story, dict):
                                        story_name = story.get('name', '')
                                        if story_name:
                                            domain_terms.update(self._extract_words_from_text(story_name))
                                        
                                        # Acceptance criteria
                                        acceptance_criteria = story.get('acceptance_criteria', [])
                                        for ac in acceptance_criteria:
                                            if isinstance(ac, dict):
                                                ac_text = ac.get('criterion', '')
                                                if ac_text:
                                                    domain_terms.update(self._extract_words_from_text(ac_text))
        
        return domain_terms
    
    def _extract_words_from_text(self, text: str) -> set:
        """Extract individual words from text, converting to lowercase.
        
        This method copies the exact approach from BusinessReadableTestNamesScanner._extract_words_from_text.
        """
        if not text:
            return set()
        
        import re
        # Split on spaces, underscores, hyphens, and other separators
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def scan_cross_file(
        self,
        rule_obj: Any = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None
    ) -> List[Dict[str, Any]]:
        """Scan across all code files for cross-file violations.
        
        Override this method in subclasses to detect violations that require
        analyzing multiple files together (e.g., duplication, inconsistent patterns,
        architectural violations).
        
        Args:
            rule_obj: Rule object reference
            test_files: List of test file paths to analyze together
            code_files: List of code file paths to analyze together
            
        Returns:
            List of violation dictionaries for cross-file issues
        """
        # Default implementation - subclasses override
        return []
    
    def _parse_code_file(self, file_path: Path) -> Optional[Tuple[str, ast.AST]]:
        """Parse a code file and return its content and AST tree.
        
        Reusable helper method for cross-file scanning.
        
        Args:
            file_path: Path to code file
            
        Returns:
            Tuple of (content, tree) or None if file cannot be parsed
        """
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            return (content, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None
    
    def _get_all_code_files_parsed(
        self, 
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None
    ) -> List[Tuple[Path, str, ast.AST]]:
        """Parse all code files and return list of (path, content, tree) tuples.
        
        Reusable helper method for cross-file scanning.
        Combines test_files and code_files into a single list.
        
        Args:
            test_files: List of test file paths
            code_files: List of code file paths
            
        Returns:
            List of tuples (file_path, content, tree) for successfully parsed files
        """
        parsed_files = []
        all_files = []
        if code_files:
            all_files.extend(code_files)
        if test_files:
            all_files.extend(test_files)
        
        for file_path in all_files:
            parsed = self._parse_code_file(file_path)
            if parsed:
                content, tree = parsed
                parsed_files.append((file_path, content, tree))
        
        return parsed_files

