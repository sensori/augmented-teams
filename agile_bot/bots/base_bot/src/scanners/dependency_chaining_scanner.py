"""Scanner for validating dependency chaining in domain models."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class DependencyChainingScanner(StoryScanner):
    """Validates that domain concepts chain dependencies properly with constructor injection."""
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check if "Instantiated with" is present (constructor injection)
        has_instantiation = False
        instantiation_collaborators = []
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            resp_lower = responsibility_name.lower()
            
            if 'instantiated with' in resp_lower:
                has_instantiation = True
                collaborators = responsibility_data.get('collaborators', [])
                instantiation_collaborators = [c.strip() for c in collaborators]
                break
        
        # Check if methods use collaborators that weren't in instantiation
        # This is a simplified check - full implementation would track dependency chain
        if has_instantiation:
            for i, responsibility_data in enumerate(node.responsibilities):
                responsibility_name = responsibility_data.get('name', '')
                if 'instantiated with' in responsibility_name.lower():
                    continue
                
                collaborators = responsibility_data.get('collaborators', [])
                
                # Check if method uses collaborators that should come through owning objects
                for collab in collaborators:
                    collab = collab.strip()
                    if collab and collab not in instantiation_collaborators:
                        # Check if it's a sub-collaborator that should be accessed through owner
                        if self._might_be_sub_collaborator(collab, instantiation_collaborators):
                            violations.append(
                                Violation(
                                    rule=rule_obj,
                                    violation_message=f'Responsibility "{responsibility_name}" may be accessing sub-collaborator "{collab}" directly. Access through owning object instead.',
                                    location=node.map_location(f'responsibilities[{i}].collaborators'),
                                    line_number=None,
                                    severity='info'
                                ).to_dict()
                            )
        
        return violations
    
    def _might_be_sub_collaborator(self, collaborator: str, instantiation_collaborators: List[str]) -> bool:
        """Heuristic to check if collaborator might be a sub-collaborator."""
        # Simple heuristic: if collaborator is more specific than instantiation collaborators
        # This is a simplified check
        return len(collaborator.split()) > 1

