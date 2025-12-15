"""Scanner for validating business-readable test names."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class BusinessReadableTestNamesScanner(TestScanner):
    """Validates test names read like plain English business language.
    
    Use domain language stakeholders understand, not technical jargon.
    Test names should read naturally when spoken aloud.
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Extract domain language from story graph
            domain_language = self._extract_domain_language(knowledge_graph)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        # Check if test name is business-readable
                        violation = self._check_business_readable(node.name, test_file_path, node, rule_obj, domain_language)
                        if violation:
                            violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _extract_domain_language(self, knowledge_graph: Dict[str, Any]) -> set:
        """Extract domain language terms from story graph, epics, and stories."""
        domain_terms = set()
        
        # Add common domain terms that are legitimate in this codebase context
        # These are domain concepts, not technical jargon
        common_domain_terms = {
            'json', 'data', 'param', 'params', 'parameter', 'parameters',
            'var', 'vars', 'variable', 'variables',
            'method', 'methods', 'class', 'classes', 'call', 'calls',
            'config', 'configuration', 'configurations',
            'agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 'action',
            'behavior', 'rule', 'rules', 'validation', 'validate', 'scanner',
            'file', 'files', 'directory', 'directories', 'path', 'paths',
            'state', 'states', 'tool', 'tools', 'server', 'catalog', 'metadata'
        }
        domain_terms.update(common_domain_terms)
        
        if not knowledge_graph:
            return domain_terms
        
        # Extract from epics
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            if isinstance(epic, dict):
                # Epic name
                epic_name = epic.get('name', '')
                if epic_name:
                    domain_terms.update(self._extract_words_from_text(epic_name))
                
                # Sub-epics
                sub_epics = epic.get('sub_epics', [])
                for sub_epic in sub_epics:
                    if isinstance(sub_epic, dict):
                        sub_epic_name = sub_epic.get('name', '')
                        if sub_epic_name:
                            domain_terms.update(self._extract_words_from_text(sub_epic_name))
                        
                        # Stories
                        story_groups = sub_epic.get('story_groups', [])
                        for story_group in story_groups:
                            if isinstance(story_group, dict):
                                stories = story_group.get('stories', [])
                                for story in stories:
                                    if isinstance(story, dict):
                                        story_name = story.get('name', '')
                                        if story_name:
                                            domain_terms.update(self._extract_words_from_text(story_name))
                                        
                                        # Acceptance criteria
                                        acceptance_criteria = story.get('acceptance_criteria', [])
                                        for ac in acceptance_criteria:
                                            if isinstance(ac, dict):
                                                ac_text = ac.get('criterion', '')
                                                if ac_text:
                                                    domain_terms.update(self._extract_words_from_text(ac_text))
        
        return domain_terms
    
    def _extract_words_from_text(self, text: str) -> set:
        """Extract individual words from text, converting to lowercase."""
        if not text:
            return set()
        
        # Split on spaces, underscores, hyphens, and other separators
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def _check_business_readable(self, test_name: str, file_path: Path, node: ast.FunctionDef, rule_obj: Any, domain_language: set) -> Optional[Dict[str, Any]]:
        """Check if test name is business-readable (not technical jargon).
        
        If test name uses domain language from story graph/epics/stories, it's considered business-readable.
        """
        # Remove 'test_' prefix
        name_without_prefix = test_name[5:] if test_name.startswith('test_') else test_name
        
        # Extract words from test name
        test_words = self._extract_words_from_text(name_without_prefix)
        
        # Check if test name uses domain language
        # If ANY domain term matches, consider it business-readable and skip all technical jargon checks
        if domain_language and test_words:
            # Check if test name contains domain language terms
            matching_domain_terms = test_words.intersection(domain_language)
            # If ANY domain term matches, skip all technical jargon checks
            # This prevents false positives for legitimate domain terms like 'param', 'method', 'data'
            if len(matching_domain_terms) >= 1:
                # Test name uses domain language - consider it business-readable
                return None
        
        # Technical jargon indicators - only flag truly technical terms that are NOT domain language
        # These are implementation details, not domain concepts
        # Note: Terms like 'json', 'data', 'param', 'method', 'class', 'call' are now considered
        # legitimate domain terms when used in context (e.g., "agent_json", "planning_data")
        technical_terms = [
            'constructor', 'init', 'parse', 'serialize', 'deserialize',
            'xml', 'http', 'api', 'endpoint', 'request', 'response',
            'schema', 'transform', 'convert', 'encode', 'decode',
            'execute', 'invoke', 'function', 'obj', 'cfg'
        ]
        
        # Check for technical jargon (excluding terms that are domain language)
        name_lower = name_without_prefix.lower()
        for term in technical_terms:
            if term in name_lower:
                # Check if this term is actually domain language
                if term in domain_language:
                    continue  # Skip - it's domain language
                
                # Only flag if it's clearly technical jargon (not part of a compound domain term)
                # For example, "parse_json" is technical, but "agent_json" is domain
                if self._is_clearly_technical_jargon(term, name_lower, domain_language):
                    line_number = node.lineno if hasattr(node, 'lineno') else None
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Test name "{test_name}" contains technical jargon "{term}" - use business-readable domain language instead',
                        location=str(file_path),
                        line_number=line_number,
                        severity='error'
                    ).to_dict()
        
        # Check for abbreviations (often technical) - but skip if domain language
        # Only flag truly technical abbreviations, not domain terms
        technical_abbrevs = r'\b(init|cfg|obj|req|resp|api|http|xml)\b'
        if re.search(technical_abbrevs, name_lower):
            # Check if any abbreviations are domain language
            abbrev_matches = re.findall(technical_abbrevs, name_lower)
            is_domain_abbrev = any(abbrev in domain_language for abbrev in abbrev_matches)
            
            if not is_domain_abbrev:
                line_number = node.lineno if hasattr(node, 'lineno') else None
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test name "{test_name}" contains abbreviations - use full business-readable words',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        # Check if name is too short/vague
        words = name_without_prefix.split('_')
        if len(words) < 3:
            line_number = node.lineno if hasattr(node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Test name "{test_name}" is too vague - add context about what happens and when',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        return None
    
    def _is_clearly_technical_jargon(self, term: str, test_name_lower: str, domain_language: set) -> bool:
        """Check if a term is clearly technical jargon (not domain language).
        
        Returns True only if the term appears in a clearly technical context.
        For example:
        - "parse_json" -> True (technical)
        - "agent_json" -> False (domain term)
        - "serialize_data" -> True (technical)
        - "planning_data" -> False (domain term)
        """
        # If term is in domain language, it's not technical jargon
        if term in domain_language:
            return False
        
        # Check if term appears as part of a compound word that's domain-specific
        # Look for patterns like: <domain_term>_<term> or <term>_<domain_term>
        # Examples: "agent_json", "workflow_json", "planning_data", "story_graph_json"
        domain_prefixes = ['agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 
                          'action', 'behavior', 'rule', 'validation', 'planning',
                          'config', 'state', 'tool', 'server', 'catalog']
        
        for prefix in domain_prefixes:
            # Check if term follows a domain prefix (e.g., "agent_json")
            if f'{prefix}_{term}' in test_name_lower:
                return False
            # Check if term precedes a domain term (e.g., "json_file" - but this is less common)
            if f'{term}_{prefix}' in test_name_lower and prefix in domain_language:
                return False
        
        # Check for common domain compound patterns
        domain_compound_patterns = [
            r'agent[_\s]json', r'workflow[_\s]json', r'story[_\s]graph[_\s]json',
            r'planning[_\s]data', r'config[_\s]data', r'validation[_\s]data',
            r'environment[_\s]var', r'working[_\s]area', r'bot[_\s]config',
            r'action[_\s]method', r'behavior[_\s]action', r'close[_\s]current[_\s]action'
        ]
        
        for pattern in domain_compound_patterns:
            if re.search(pattern, test_name_lower):
                # If the term appears near domain language, it's likely domain, not technical
                return False
        
        # If we get here, it's likely technical jargon
        return True

