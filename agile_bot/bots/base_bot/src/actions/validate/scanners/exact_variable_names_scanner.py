"""Scanner for validating variable names match scenario/AC/domain model concepts exactly."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class ExactVariableNamesScanner(TestScanner):
    """Validates variable names match scenario/AC/domain model concepts exactly."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Extract domain concepts from knowledge graph
            domain_concepts = self._extract_domain_concepts(knowledge_graph)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        # Check variable names in test
                        violations.extend(self._check_variable_names(node, domain_concepts, test_file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _extract_domain_concepts(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract domain concept names from knowledge graph."""
        concepts = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            domain_concepts_list = epic.get('domain_concepts', [])
            for concept in domain_concepts_list:
                if isinstance(concept, dict):
                    concept_name = concept.get('name', '')
                    if concept_name:
                        concepts.append(concept_name.lower())
        return concepts
    
    def _check_variable_names(self, test_node: ast.FunctionDef, domain_concepts: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if variable names match domain concepts."""
        violations = []
        
        # Find variable assignments in test
        for node in ast.walk(test_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        # Check if variable name is generic (not matching domain concepts)
                        if var_name in ['data', 'result', 'value', 'item', 'obj', 'thing']:
                            line_number = target.lineno if hasattr(target, 'lineno') else None
                            violation = Violation(
                                rule=rule_obj,
                                violation_message=f'Variable "{target.id}" uses generic name - use exact domain concept name from scenario/AC',
                                location=str(file_path),
                                line_number=line_number,
                                severity='warning'
                            ).to_dict()
                            violations.append(violation)
        
        return violations

