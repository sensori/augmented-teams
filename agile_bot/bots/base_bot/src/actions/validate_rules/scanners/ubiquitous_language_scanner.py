"""Scanner for validating ubiquitous language consistency."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .test_scanner import TestScanner
from .violation import Violation


class UbiquitousLanguageScanner(TestScanner):
    """Validates domain language consistency (ubiquitous language)."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            
            # Extract domain terms from knowledge graph
            domain_terms = self._extract_domain_terms(knowledge_graph)
            
            # Check for ubiquitous language violations
            violations.extend(self._check_ubiquitous_language(content, domain_terms, test_file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _extract_domain_terms(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract domain terms from knowledge graph."""
        terms = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            # Extract from epic name, sub-epic names, story names, domain concepts
            epic_name = epic.get('name', '')
            if epic_name:
                terms.extend(epic_name.lower().split())
            
            domain_concepts = epic.get('domain_concepts', [])
            for concept in domain_concepts:
                if isinstance(concept, dict):
                    concept_name = concept.get('name', '')
                    if concept_name:
                        terms.extend(concept_name.lower().split())
        
        return list(set(terms))  # Unique terms
    
    def _check_ubiquitous_language(self, content: str, domain_terms: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for ubiquitous language violations."""
        violations = []
        
        # This is a basic check - could be enhanced to check against domain model
        # For now, just ensure test uses domain terms consistently
        
        content_lower = content.lower()
        
        # Check if content uses domain terms
        if domain_terms:
            # Check if test uses any domain terms
            uses_domain_terms = any(term in content_lower for term in domain_terms)
            
            if not uses_domain_terms and len(content) > 100:
                # Test doesn't use domain terms - might be using technical language
                violation = Violation(
                    rule=rule_obj,
                    violation_message='Test does not use domain terms from knowledge graph - use ubiquitous language consistently',
                    location=str(file_path),
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

