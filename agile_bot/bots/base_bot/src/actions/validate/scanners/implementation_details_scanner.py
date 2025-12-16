"""Scanner for detecting implementation details as stories."""

from typing import List, Dict, Any
from .story_scanner import StoryScanner
from .story_map import StoryNode
from .violation import Violation
import re


class ImplementationDetailsScanner(StoryScanner):
    """Detects implementation operations that should be steps within stories, not stories themselves."""
    
    # Implementation operation verbs (should be steps, not stories)
    IMPLEMENTATION_VERBS = [
        'serialize', 'deserialize', 'convert', 'transform', 'format',
        'calculate', 'compute', 'generate', 'create',  # when referring to technical artifacts
        'apply', 'set', 'configure',  # technical settings
        'save', 'write', 'store'  # without user context
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        name_lower = node.name.lower()
        
        # Check for implementation operation verbs
        for verb in self.IMPLEMENTATION_VERBS:
            # Check if verb appears as main action (start of name or after "to")
            pattern = rf'\b{verb}\b'
            if re.search(pattern, name_lower):
                # Check if it's describing an outcome vs implementation
                # If it's just "Verb Noun" without user context, it's likely implementation
                words = name_lower.split()
                # Check if verb is at the start (most common pattern for implementation operations)
                if verb in words[0] or (len(words) > 1 and verb in words[0:2]):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Story "{node.name}" appears to be an implementation operation - should be a step within a story that describes user/system outcome',
                        location=node.name,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

