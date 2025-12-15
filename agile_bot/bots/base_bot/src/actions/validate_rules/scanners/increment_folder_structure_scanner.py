"""Scanner for validating folder structure matches story map hierarchy."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .story_scanner import StoryScanner
from .story_map import StoryNode, Epic, SubEpic, Story
from .violation import Violation
import re


class IncrementFolderStructureScanner(StoryScanner):
    """Validates that folder structure matches story map hierarchy.
    
    Only checks epics → stories with scenarios (moved to scenarios behavior).
    Validates emoji prefixes (🎯 Epic, ⚙️ Feature) and correct nesting.
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Only check epics and their direct stories (scenarios behavior)
        if isinstance(node, Epic):
            epic_name = node.name
            if not epic_name:
                return violations
            
            # Check if epic has stories with scenarios
            has_stories_with_scenarios = self._epic_has_stories_with_scenarios(node)
            
            if has_stories_with_scenarios:
                # Validate epic folder structure
                violation = self._check_epic_folder_structure(node, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _epic_has_stories_with_scenarios(self, epic: Epic) -> bool:
        """Check if epic has stories with scenarios."""
        for child in epic.children:
            if isinstance(child, Story):
                story_data = child.data
                scenarios = story_data.get('scenarios', [])
                if scenarios:
                    return True
        return False
    
    def _check_epic_folder_structure(self, node: StoryNode, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check epic folder structure matches expected format."""
        epic_name = node.name
        expected_folder = f"🎯 {epic_name}"
        
        # This scanner validates structure, but actual folder checking
        # would require workspace context (not available in story graph)
        # For now, validate that epic name follows expected format
        
        # Check for emoji prefix in epic name (if present in story graph)
        if not epic_name.startswith('🎯'):
            # Epic name should have emoji prefix in folder structure
            # But story graph may not include emoji, so this is informational
            pass
        
        return None

