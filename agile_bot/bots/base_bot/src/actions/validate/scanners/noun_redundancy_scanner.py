"""Scanner for detecting noun redundancy in story elements."""

from typing import List, Dict, Any
from .story_scanner import StoryScanner
from .story_map import StoryNode
from .violation import Violation
import re


class NounRedundancyScanner(StoryScanner):
    """Detects redundant nouns in story element names (e.g., 'Animation System', 'Animation Component')."""
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        name = node.name
        
        # Extract nouns (words that are capitalized or common nouns)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', name)
        
        # Check for repeated nouns across sibling nodes
        # This is a simplified check - full implementation would need parent context
        # For now, check if name has redundant patterns like "X Animation", "Y Animation"
        if len(words) >= 2:
            # Check for pattern: "Noun1 Noun2" where Noun2 appears in other names
            # This is a heuristic - full check needs sibling context
            pass
        
        # Check for numbered/generic qualifiers that suggest redundancy
        if re.search(r'\d+|System|Component|Module|Manager|Handler', name, re.IGNORECASE):
            # Check if removing qualifier would make it ambiguous
            base_name = re.sub(r'\s+(System|Component|Module|Manager|Handler|\d+)$', '', name, flags=re.IGNORECASE)
            if base_name and base_name != name:
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Story element "{name}" may have redundant noun - consider integrating with related concepts instead of using qualifiers',
                    location=node.name,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

