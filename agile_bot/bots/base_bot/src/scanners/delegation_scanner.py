"""Scanner for validating delegation to lowest-level objects in domain models."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class DelegationScanner(StoryScanner):
    """Validates that domain concepts delegate responsibilities to the lowest-level object."""
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check for patterns where parent objects might be doing child's work
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            resp_lower = responsibility_name.lower()
            
            # Check for patterns like "Find X by Y" where X should be found by collection class
            if 'find' in resp_lower and 'by' in resp_lower:
                # If this is not a collection class, it might be doing child's work
                if not self._is_collection_class(node.name):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" may be doing what a collection class should do. Consider delegating to collection class.',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='info'
                        ).to_dict()
                    )
        
        return violations
    
    def _is_collection_class(self, name: str) -> bool:
        """Check if name indicates a collection class."""
        # Simple heuristic: plural forms or explicit "Collection" marker
        name_lower = name.lower()
        return (name_lower.endswith('s') and len(name_lower) > 3) or 'collection' in name_lower




