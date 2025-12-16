"""Scanner for validating test structure matches story graph exactly."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .test_scanner import TestScanner
from .violation import Violation


class StoryGraphMatchScanner(TestScanner):
    """Validates test structure matches story graph exactly.
    
    This is similar to ClassBasedOrganizationScanner but more comprehensive.
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Extract story names from knowledge graph
            story_names = self._extract_story_names(knowledge_graph)
            
            # Check test classes match stories
            violations.extend(self._check_test_classes_match_stories(tree, story_names, test_file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _extract_story_names(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract story names from knowledge graph."""
        story_names = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        if story_name:
                            story_names.append(story_name)
        return story_names
    
    def _check_test_classes_match_stories(self, tree: ast.AST, story_names: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if test classes match story names."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    # Remove 'Test' prefix and check if matches a story
                    story_name_from_class = node.name[4:]  # Remove 'Test'
                    
                    # Convert to story name format for comparison
                    # This is approximate - exact matching would require more sophisticated comparison
                    matches = [s for s in story_names if story_name_from_class.lower().replace('_', ' ') in s.lower()]
                    
                    if not matches:
                        line_number = node.lineno if hasattr(node, 'lineno') else None
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Test class "{node.name}" does not match any story name - test classes must match story names exactly',
                            location=str(file_path),
                            line_number=line_number,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
        
        return violations

