"""Scanner for validating story filenames match story names."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .story_scanner import StoryScanner
from .story_map import StoryNode, Story
from .violation import Violation
import re


class StoryFilenameScanner(StoryScanner):
    """Validates story filenames match story names exactly (no actor prefix).
    
    Actor information belongs in story description or acceptance criteria, NOT in filename.
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_name = node.name
            if not story_name:
                return violations
            
            # This scanner would need access to actual file system to check filenames
            # For now, we can validate story names don't contain actor prefixes
            # that shouldn't be in filenames
            
            # Check for common actor prefixes that shouldn't be in story names
            violation = self._check_actor_in_story_name(story_name, node, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_actor_in_story_name(self, story_name: str, node: StoryNode, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if story name contains actor prefix that shouldn't be in filename."""
        # Common actor prefixes that shouldn't be in story names/filenames
        actor_prefixes = [
            'AI Chat', 'Router', 'Bot Behavior', 'GatherContextAction',
            'Agent', 'System', 'User', 'Admin', 'Customer'
        ]
        
        for prefix in actor_prefixes:
            if story_name.startswith(prefix + ' '):
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Story name "{story_name}" starts with actor prefix "{prefix}" - actor information should be in description/AC, not in story name/filename',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None

