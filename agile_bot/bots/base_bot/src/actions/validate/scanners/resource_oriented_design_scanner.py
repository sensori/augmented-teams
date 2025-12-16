"""Scanner for validating resource-oriented design in domain models."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class ResourceOrientedDesignScanner(StoryScanner):
    """Validates that domain concepts use resource-oriented design instead of manager/doer/loader patterns."""
    
    MANAGER_PATTERNS = ['manager', 'loader', 'handler', 'doer', 'processor', 'executor']
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        # This scanner is for domain concepts, not story nodes
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check if node name indicates manager pattern
        node_name_lower = node.name.lower()
        for pattern in self.MANAGER_PATTERNS:
            if pattern in node_name_lower and node_name_lower.endswith(pattern):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Domain concept "{node.name}" uses manager/doer/loader pattern. Use resource-oriented design instead (e.g., "{node.name.replace(pattern, "").title()}").',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='error'
                    ).to_dict()
                )
        
        return violations




