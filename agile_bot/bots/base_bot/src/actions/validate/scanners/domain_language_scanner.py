"""Scanner for validating domain-specific language in domain models."""

from typing import List, Dict, Any, Optional
import re
from .story_scanner import StoryScanner
from .story_map import StoryMap, StoryNode
from .domain_concept_node import DomainConceptNode
from .violation import Violation


class DomainLanguageScanner(StoryScanner):
    """Validates that domain concepts use domain-specific language, not generic terms."""
    
    GENERIC_TERMS = [
        r'\bdata\b',
        r'\bconfig\b',
        r'\bparameter\b',
        r'\bresult\b',
        r'\bvalue\b',  # Only if used generically
    ]
    
    GENERATE_PATTERNS = [
        r'^generate\s+',
        r'^calculate\s+',
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check node name for generic terms
        node_name_lower = node.name.lower()
        for term in ['data', 'config', 'parameter', 'result']:
            if term in node_name_lower and not self._is_domain_specific(node.name):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Domain concept "{node.name}" uses generic term "{term}". Use domain-specific language instead (e.g., "PortfolioData" → "Portfolio", "TargetConfig" → "TargetAllocation").',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='warning'
                    ).to_dict()
                )
        
        # Check responsibilities for generic terms and generate/calculate patterns
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            resp_lower = responsibility_name.lower()
            
            # Check for generic terms in collaborators
            for collab in collaborators:
                collab_lower = collab.lower()
                for term in self.GENERIC_TERMS:
                    if term in collab_lower and not self._is_domain_specific(collab):
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=f'Responsibility "{responsibility_name}" uses generic collaborator "{collab}". Use domain-specific language instead.',
                                location=node.map_location(f'responsibilities[{i}].collaborators'),
                                line_number=None,
                                severity='warning'
                            ).to_dict()
                        )
                        break
            
            # Check for generate/calculate patterns
            for pattern in self.GENERATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Responsibility "{responsibility_name}" uses generate/calculate. Use property instead (e.g., "Get recommended trades" not "Generate recommendation").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations
    
    def _is_domain_specific(self, name: str) -> bool:
        """Check if name contains domain-specific context."""
        # Simple heuristic: if it's just "Data" or "Config" it's generic
        # If it's "PortfolioData" it might be okay in some contexts, but ideally should be "Portfolio"
        return len(name.split()) > 1 or name.lower() not in ['data', 'config', 'parameter', 'result']
    
    def _is_generic_usage(self, responsibility: str, pattern: str) -> bool:
        """Check if generic term is used generically (not as part of domain term)."""
        # Simple heuristic: if it's standalone or with generic context, it's generic
        matches = re.findall(pattern, responsibility.lower())
        for match in matches:
            # Check if it's part of a domain term (e.g., "PortfolioData" vs "data")
            if match.strip() == 'data' or match.strip() == 'config':
                return True
        return False




