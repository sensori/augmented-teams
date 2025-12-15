"""Scanner for validating avoidance of technical abstractions in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class TechnicalAbstractionScanner(StoryScanner):
    """Validates that domain concepts stay at domain level, avoiding unnecessary technical abstractions."""
    
    TECHNICAL_ABSTRACTION_PATTERNS = [
        r'\bsaver\b',
        r'\bloader\b',
        r'\bstorage\b',
        r'\bsave\s+.*file\b',
        r'\bload\s+.*file\b',
        r'\bstore\s+.*file\b',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check node name for technical abstraction patterns
        node_name_lower = node.name.lower()
        for pattern in [r'\bsaver\b', r'\bloader\b', r'\bstorage\b']:
            if re.search(pattern, node_name_lower):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Domain concept "{node.name}" separates technical abstraction. Keep technical details (saving, loading) as part of domain concepts instead.',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='warning'
                    ).to_dict()
                )
                break
        
        # Check responsibilities for technical abstraction patterns
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            resp_lower = responsibility_name.lower()
            for pattern in self.TECHNICAL_ABSTRACTION_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" exposes technical abstraction. Stay at domain level (e.g., "Save portfolio" not "Save portfolio to file").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations

