"""Scanner for validating vocabulary consistency across tests."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .test_scanner import TestScanner
from .violation import Violation
from collections import defaultdict


class ConsistentVocabularyScanner(TestScanner):
    """Validates vocabulary consistency across tests."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            
            # Extract domain terms from knowledge graph
            domain_terms = self._extract_domain_terms(knowledge_graph)
            
            # Check for inconsistent vocabulary
            violations.extend(self._check_vocabulary_consistency(content, domain_terms, test_file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _extract_domain_terms(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract domain terms from knowledge graph."""
        terms = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            # Extract from epic name, sub-epic names, story names
            epic_name = epic.get('name', '')
            if epic_name:
                terms.extend(epic_name.lower().split())
            
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                if sub_epic_name:
                    terms.extend(sub_epic_name.lower().split())
        
        return list(set(terms))  # Unique terms
    
    def _check_vocabulary_consistency(self, content: str, domain_terms: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for vocabulary consistency."""
        violations = []
        
        # Check if content uses domain terms consistently
        content_lower = content.lower()
        
        # Look for common synonyms that should use domain terms instead
        synonym_map = {
            'data': ['info', 'information', 'content'],
            'user': ['person', 'customer', 'client'],
            'system': ['application', 'app', 'service'],
        }
        
        for domain_term, synonyms in synonym_map.items():
            if domain_term in domain_terms:
                # Domain term exists, check for synonyms
                for synonym in synonyms:
                    if synonym in content_lower and domain_term not in content_lower:
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Test uses "{synonym}" instead of domain term "{domain_term}" - use consistent vocabulary',
                            location=str(file_path),
                            severity='warning'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations

