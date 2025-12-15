"""Scanner for validating acceptance criteria are behavioral (not technical)."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryNode, Story
from .violation import Violation
import re


class BehavioralACScanner(StoryScanner):
    """Validates acceptance criteria are behavioral (not technical).
    
    Check AC are behavioral (not technical).
    Verify AC at story level.
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            
            # Check acceptance criteria
            acceptance_criteria = story_data.get('acceptance_criteria', [])
            
            for ac_idx, ac in enumerate(acceptance_criteria):
                ac_text = self._get_ac_text(ac)
                
                # Check if AC is technical (not behavioral)
                violation = self._check_technical_ac(ac_text, node, ac_idx, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _get_ac_text(self, ac: Any) -> str:
        """Extract AC text from AC dict or string."""
        if isinstance(ac, dict):
            return ac.get('criterion', '') or ac.get('description', '') or str(ac)
        return str(ac)
    
    def _check_technical_ac(self, ac_text: str, node: StoryNode, ac_idx: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if AC is technical (not behavioral)."""
        text_lower = ac_text.lower()
        
        # Technical indicators
        technical_terms = [
            'api', 'endpoint', 'http', 'json', 'xml', 'database', 'sql',
            'schema', 'class', 'function', 'method', 'variable', 'config',
            'parse', 'serialize', 'deserialize', 'encode', 'decode',
            'framework', 'library', 'dependency', 'import', 'module'
        ]
        
        for term in technical_terms:
            if term in text_lower:
                location = f"{node.map_location()}.acceptance_criteria[{ac_idx}]"
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Acceptance criterion contains technical term "{term}" - AC should describe behavioral outcomes, not technical implementation',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None

