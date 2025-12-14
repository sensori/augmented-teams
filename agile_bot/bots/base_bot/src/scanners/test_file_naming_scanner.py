"""Scanner for validating test file naming matches sub-epic names."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class TestFileNamingScanner(TestScanner):
    """Validates test file names match sub-epic names."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        # Extract sub-epic names from knowledge graph
        sub_epic_names = self._extract_sub_epic_names(knowledge_graph)
        
        # Get expected file name from sub-epic
        file_name = test_file_path.stem  # Without .py extension
        
        # Check if file name matches a sub-epic name
        violation = self._check_file_name_matches_sub_epic(
            file_name, sub_epic_names, test_file_path, rule_obj, knowledge_graph
        )
        if violation:
            violations.append(violation)
        
        return violations
    
    def _extract_sub_epic_names(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract sub-epic names from knowledge graph (recursively including nested sub-epics)."""
        sub_epic_names = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            self._extract_sub_epic_names_recursive(epic.get('sub_epics', []), sub_epic_names)
        return sub_epic_names
    
    def _extract_sub_epic_names_recursive(self, sub_epics: List[Dict[str, Any]], result: List[str]) -> None:
        """Recursively extract sub-epic names including nested sub-epics.
        
        Stores original sub-epic names (not normalized) so they can be used
        for display in suggestions.
        """
        for sub_epic in sub_epics:
            sub_epic_name = sub_epic.get('name', '')
            if sub_epic_name:
                # Store original name (will be normalized during comparison)
                result.append(sub_epic_name)
            # Recursively process nested sub-epics
            nested_sub_epics = sub_epic.get('sub_epics', [])
            if nested_sub_epics:
                self._extract_sub_epic_names_recursive(nested_sub_epics, result)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case.
        
        Handles:
        - Spaces -> underscores
        - Ampersands (&, &amp;) -> 'and'
        - 'and ' (with trailing space) -> 'and'
        - Special characters -> removed
        - Capital letters -> lowercase with underscores
        """
        # Replace HTML entity &amp; with 'and' first
        name = name.replace('&amp;', 'and')
        # Replace ampersand with 'and' before other processing
        name = name.replace('&', 'and')
        # Normalize 'and ' (with trailing space) to 'and' before space processing
        name = re.sub(r'\band\s+', 'and', name)
        # Insert underscores before capital letters
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove special characters except underscores
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        # Convert to lowercase
        return name.lower()
    
    def _check_file_name_matches_sub_epic(self, file_name: str, sub_epic_names: List[str], file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if test file name matches a sub-epic name.
        
        If a test file doesn't match any sub-epic name:
        - If test methods span multiple sub-epics: OK (cross-epic test file)
        - Else: Violation (methods should be in files with sub-epic names)
        """
        # Remove 'test_' prefix if present
        name_without_prefix = file_name[5:] if file_name.startswith('test_') else file_name
        
        # Normalize for comparison
        name_normalized = self._to_snake_case(name_without_prefix)
        
        # Check if matches any sub-epic name (normalized)
        normalized_sub_epic_names = [self._to_snake_case(name) for name in sub_epic_names]
        matches = [name for name in normalized_sub_epic_names if name_normalized == name]
        
        # Also check for partial matches (file name contains sub-epic or vice versa)
        if not matches:
            matches = [name for name in normalized_sub_epic_names 
                      if name_normalized in name or name in name_normalized]
        
        # If file name matches a sub-epic, no violation
        if matches:
            return None
        
        # File name doesn't match any sub-epic - check if methods span multiple sub-epics
        sub_epics_spanned = self._get_sub_epics_spanned_by_test_methods(file_path, knowledge_graph)
        
        # If methods span multiple sub-epics, it's OK (cross-epic test file)
        if len(sub_epics_spanned) > 1:
            return None  # No violation - cross-epic test file is OK
        
        # Methods don't span multiple sub-epics - violation
        # Find closest matching sub-epic names for suggestions
        suggestions_normalized = self._find_closest_sub_epic_names(name_normalized, normalized_sub_epic_names)
        suggestion_text = ""
        if suggestions_normalized:
            suggestion_list = ", ".join([f"test_{s}.py" for s in suggestions_normalized[:5]])
            suggestion_text = f" Suggested names: {suggestion_list}"
        
        return Violation(
            rule=rule_obj,
            violation_message=f'Test file name "{file_name}" does not match any sub-epic name and test methods do not span multiple sub-epics - file should be named test_<sub_epic_name>.py.{suggestion_text}',
            location=str(file_path),
            severity='error'
        ).to_dict()
    
    def _get_sub_epics_spanned_by_test_methods(self, test_file_path: Path, knowledge_graph: Dict[str, Any]) -> set:
        """Get set of sub-epic names that test methods in this file span.
        
        Returns set of sub-epic names (normalized) that the test methods belong to.
        """
        sub_epics = set()
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Find all test methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Get class name for context
                        class_name = node.name
                        
                        # Check test methods in this class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('test_'):
                                    # Find which sub-epic this method belongs to
                                    sub_epic = self._find_sub_epic_for_method(item.name, class_name, knowledge_graph)
                                    if sub_epic:
                                        sub_epics.add(self._to_snake_case(sub_epic))
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return sub_epics
    
    def _find_sub_epic_for_method(self, method_name: str, class_name: str, knowledge_graph: Dict[str, Any]) -> Optional[str]:
        """Find the sub-epic name that a test method belongs to.
        
        Returns the sub-epic name if found, None otherwise.
        """
        method_name_norm = self._to_snake_case(method_name)
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        story_name_normalized = self._to_snake_case(story_name_from_class)
        
        epics = knowledge_graph.get('epics', [])
        
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                sub_epic_name_norm = self._to_snake_case(sub_epic_name) if sub_epic_name else ''
                
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        story_name_norm = self._to_snake_case(story_name) if story_name else ''
                        
                        # Check if story matches class name
                        story_matches_class = (story_name_norm == story_name_normalized or 
                                             story_name_norm.startswith(story_name_normalized) or
                                             story_name_normalized.startswith(story_name_norm))
                        
                        # Check scenarios
                        scenarios = story.get('scenarios', [])
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', '')
                            if not scenario_name:
                                continue
                            scenario_name_norm = self._to_snake_case(scenario_name)
                            
                            # Check if method name matches scenario
                            if (method_name_norm in scenario_name_norm or 
                                scenario_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(scenario_name_norm)):
                                # Found scenario match - return sub-epic
                                return sub_epic_name
                        
                        # Check if method name matches story name (and story matches class)
                        if story_matches_class:
                            if (method_name_norm in story_name_norm or 
                                story_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(story_name_norm)):
                                # Story match - return sub-epic
                                return sub_epic_name
                        
                        # Check acceptance criteria
                        acceptance_criteria = story.get('acceptance_criteria', [])
                        for ac in acceptance_criteria:
                            ac_text = ac.get('text', '') if isinstance(ac, dict) else str(ac)
                            if not ac_text:
                                continue
                            ac_norm = self._to_snake_case(ac_text)
                            
                            if (method_name_norm in ac_norm or 
                                ac_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(ac_norm)):
                                # AC match - return sub-epic
                                return sub_epic_name
                        
                        # Check if method name matches sub-epic name
                        if (method_name_norm in sub_epic_name_norm or 
                            sub_epic_name_norm.startswith(method_name_norm) or
                            method_name_norm.startswith(sub_epic_name_norm)):
                            # Sub-epic match
                            return sub_epic_name
        
        return None
    
    def _find_closest_sub_epic_names(self, file_name: str, sub_epic_names: List[str], max_suggestions: int = 5) -> List[str]:
        """Find the closest matching sub-epic names for suggestions using simple string similarity."""
        if not sub_epic_names:
            return []
        
        # Calculate similarity scores
        scored_names = []
        file_name_lower = file_name.lower()
        
        for sub_epic_name in sub_epic_names:
            sub_epic_lower = sub_epic_name.lower()
            
            # Simple similarity: check for common substrings
            score = 0
            
            # Exact match gets highest score
            if file_name_lower == sub_epic_lower:
                score = 1000
            # Check if file name is contained in sub-epic name or vice versa
            elif file_name_lower in sub_epic_lower:
                score = 50 + len(file_name_lower)  # Longer matches score higher
            elif sub_epic_lower in file_name_lower:
                score = 30 + len(sub_epic_lower)
            else:
                # Check for common words/parts
                file_parts = set(file_name_lower.split('_'))
                sub_epic_parts = set(sub_epic_lower.split('_'))
                common_parts = file_parts.intersection(sub_epic_parts)
                if common_parts:
                    score = len(common_parts) * 10
            
            if score > 0:
                scored_names.append((score, sub_epic_name))
        
        # Sort by score (descending) and return top matches
        scored_names.sort(key=lambda x: x[0], reverse=True)
        return [name for _, name in scored_names[:max_suggestions]]

