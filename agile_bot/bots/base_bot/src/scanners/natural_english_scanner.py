"""Scanner for validating natural English usage in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class NaturalEnglishScanner(StoryScanner):
    """Validates that domain concepts use natural English for plural, singular, and cardinality."""
    
    TECHNICAL_NOTATION_PATTERNS = [
        r'\[0\.\.1\]',
        r'\[1\.\.\*\]',
        r'\[0\.\.\*\]',
        r'\[0\.\.\]',
        r'\[1\.\.\]',
        r'\[0,1\]',
        r'\[1,\*\]',
        r'\[0,\*\]',
        r'\[0\.\.n\]',
        r'\[1\.\.n\]',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check responsibilities for technical notation
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            for pattern in self.TECHNICAL_NOTATION_PATTERNS:
                if re.search(pattern, responsibility_name):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" uses technical notation. Use natural English instead (e.g., "Get portfolio" not "Get portfolio [0..1]").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations


