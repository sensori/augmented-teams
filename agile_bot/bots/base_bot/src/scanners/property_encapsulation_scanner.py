"""Scanner for validating property encapsulation in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class PropertyEncapsulationScanner(StoryScanner):
    """Validates that domain concepts encapsulate state and behavior through properties."""
    
    EXPOSED_STATE_PATTERNS = [
        r'\blist\b',
        r'\barray\b',
        r'\bdictionary\b',
        r'\bdict\b',
        r'\bset\s+',
        r'\bmodify\s+',
        r'\bupdate\s+.*list',
        r'\bexpose\s+',
    ]
    
    CALCULATE_PATTERNS = [
        r'^calculate\s+',
        r'^compute\s+',
        r'^derive\s+',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        # This scanner is for domain concepts, not story nodes
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check responsibilities for exposed state patterns
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            resp_lower = responsibility_name.lower()
            
            # Check for exposed internal structure
            for pattern in self.EXPOSED_STATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" exposes internal structure. Use property encapsulation instead (e.g., "Get holdings: Holdings" not "Get holdings list: List").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
            
            # Check for calculate/compute methods instead of properties
            for pattern in self.CALCULATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" uses calculate/compute instead of property. Use "Get X" instead of "Calculate X" to hide calculation timing.',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations

