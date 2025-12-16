"""Scanner for validating domain grouping in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class DomainGroupingScanner(StoryScanner):
    """Validates that domain concepts are grouped by domain area, not technical layers."""
    
    TECHNICAL_LAYER_PATTERNS = [
        r'\blayer\b',
        r'\btier\b',
        r'\bservice\b',
        r'\brepository\b',
        r'\bdto\b',
        r'\bpresentation\b',
        r'\bbusiness\b',
        r'\bdata\s+access\b',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check node name for technical layer patterns
        node_name_lower = node.name.lower()
        for pattern in self.TECHNICAL_LAYER_PATTERNS:
            if re.search(pattern, node_name_lower):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Domain concept "{node.name}" uses technical layer terminology. Group by domain area instead.',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='warning'
                    ).to_dict()
                )
                break
        
        return violations




