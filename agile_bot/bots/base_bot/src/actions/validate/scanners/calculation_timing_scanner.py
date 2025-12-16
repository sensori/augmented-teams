"""Scanner for validating that calculation timing is hidden in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class CalculationTimingScanner(StoryScanner):
    """Validates that domain concepts hide calculation timing."""
    
    TIMING_EXPOSURE_PATTERNS = [
        r'^calculate\s+',
        r'^compute\s+',
        r'^derive\s+',
        r'\bcached\s+',
        r'\bpre-computed\s+',
        r'\bon-demand\s+',
        r'\bprecomputed\s+',
        r'\bprecomputed\s+',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check responsibilities for timing exposure
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            resp_lower = responsibility_name.lower()
            
            for pattern in self.TIMING_EXPOSURE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" exposes calculation timing. Use "Get X" instead to hide when calculations occur.',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations




