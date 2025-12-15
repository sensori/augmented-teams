"""Scanner for validating code representation in domain models."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class CodeRepresentationScanner(StoryScanner):
    """Validates that domain models represent code as closely as possible."""
    
    ABSTRACT_PATTERNS = [
        'concept',
        'insight',
        'pattern',
        'knowledge',
        'abstract',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check node name for abstract patterns
        node_name_lower = node.name.lower()
        for pattern in self.ABSTRACT_PATTERNS:
            if pattern in node_name_lower:
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Domain concept "{node.name}" uses abstract terminology. Domain models should represent code closely - refactor code if needed.',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='info'
                    ).to_dict()
                )
                break
        
        # Check responsibilities for abstract collaborators
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            
            for collab in collaborators:
                collab_lower = collab.strip().lower()
                for pattern in self.ABSTRACT_PATTERNS:
                    if pattern in collab_lower:
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=f'Responsibility "{responsibility_name}" uses abstract collaborator "{collab.strip()}". Use concrete domain concepts that exist in code.',
                                location=node.map_location(f'responsibilities[{i}].collaborators'),
                                line_number=None,
                                severity='info'
                            ).to_dict()
                        )
                        break
        
        return violations




