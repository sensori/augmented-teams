"""Scanner for validating test class-based organization."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .story_map import StoryNode
from .violation import Violation


class ClassBasedOrganizationScanner(TestScanner):
    """Validates test class-based organization.
    
    Validates:
    - Test file names match sub-epic names (test_<sub_epic_name>.py)
    - Test classes match story names exactly (Test<ExactStoryName>)
    - Test methods match scenario names exactly (test_<scenario_name_snake_case>)
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan story node (required by StoryScanner, but not used for test scanning)."""
        return []  # Test scanning happens in scan_test_file, not scan_story_node
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        # Check file naming matches sub-epic
        sub_epic_names = self._extract_sub_epic_names(knowledge_graph)
        file_name = test_file_path.stem  # Without .py extension
        violation = self._check_file_name_matches_sub_epic(file_name, sub_epic_names, test_file_path, rule_obj, knowledge_graph)
        if violation:
            violations.append(violation)
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Extract story names from knowledge graph
            story_names = self._extract_story_names(knowledge_graph)
            
            # Find test classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Check if class name matches a story name
                        violation = self._check_class_name_matches_story(node.name, story_names, test_file_path, rule_obj)
                        if violation:
                            violations.append(violation)
                        
                        # Check test methods in this class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('test_'):
                                    # Check method name matches scenario
                                    violation = self._check_method_name_matches_scenario(
                                        item.name, node.name, story_names, knowledge_graph, test_file_path, rule_obj
                                    )
                                    if violation:
                                        violations.append(violation)
        except (SyntaxError, UnicodeDecodeError) as e:
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _extract_story_names(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract story names from knowledge graph."""
        story_names = []
        
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        if story_name:
                            story_names.append(story_name)
        
        return story_names
    
    def _check_class_name_matches_story(self, class_name: str, story_names: List[str], file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if test class name matches a story name exactly."""
        # Remove 'Test' prefix
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        
        # Convert to story name format (PascalCase to story name)
        # This is approximate - exact matching would require story graph lookup
        expected_story_name = self._pascal_to_story_name(story_name_from_class)
        
        # Check if any story name matches (allowing for variations)
        matches = [s for s in story_names if self._names_match(s, expected_story_name)]
        
        if not matches:
            # Check for common violations: abbreviations, generic names
            if self._is_abbreviated(class_name, story_names):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test class "{class_name}" appears abbreviated - should match story name exactly (Test<ExactStoryName>)',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
            
            if self._is_generic(class_name):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test class "{class_name}" uses generic name - should match story name exactly',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
        
        return None
    
    def _check_method_name_matches_scenario(self, method_name: str, class_name: str, story_names: List[str], 
                                           knowledge_graph: Dict[str, Any], file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if test method name matches scenario name."""
        # Remove 'test_' prefix
        scenario_name_from_method = method_name[5:] if method_name.startswith('test_') else method_name
        
        # Check for abbreviations
        if len(scenario_name_from_method) < 20:  # Very short names are likely abbreviated
            # Try to find matching epic/story/scenario from knowledge graph
            expected_name = self._find_expected_scenario_name(scenario_name_from_method, knowledge_graph, class_name)
            
            if expected_name:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test method "{method_name}" appears abbreviated - should match scenario name exactly. Expected name based on epic/story: "{expected_name}"',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
            else:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test method "{method_name}" appears abbreviated - should match scenario name exactly',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
        
        return None
    
    def _find_expected_scenario_name(self, method_name: str, knowledge_graph: Dict[str, Any], class_name: str) -> Optional[str]:
        """Find the expected scenario/epic/story/sub-epic name based on the test method and class name.
        
        Args:
            method_name: Method name WITHOUT 'test_' prefix (e.g., 'epic_has_sub_epics')
        
        Returns the most specific match found: scenario > story > sub-epic > epic
        """
        # Reconstruct full method name with 'test_' prefix for test_method field comparison
        full_method_name = f"test_{method_name}" if not method_name.startswith('test_') else method_name
        method_name_norm = self._normalize_name(method_name)
        
        # Extract story name from class name (remove 'Test' prefix)
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        story_name_normalized = self._normalize_name(story_name_from_class)
        
        # Extract all information from knowledge graph
        epics = knowledge_graph.get('epics', [])
        
        best_match = None
        best_match_type = None  # 'scenario', 'story', 'sub_epic', 'epic'
        
        for epic in epics:
            epic_name = epic.get('name', '')
            epic_name_norm = self._normalize_name(epic_name) if epic_name else ''
            
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                sub_epic_name_norm = self._normalize_name(sub_epic_name) if sub_epic_name else ''
                
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        story_name_norm = self._normalize_name(story_name) if story_name else ''
                        
                        # Check if story matches class name
                        story_matches_class = (story_name_norm == story_name_normalized or 
                                             story_name_norm.startswith(story_name_normalized) or
                                             story_name_normalized.startswith(story_name_norm))
                        
                        # Check scenarios (most specific match)
                        scenarios = story.get('scenarios', [])
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', '')
                            test_method = scenario.get('test_method', '')
                            
                            # First check: exact match on test_method field (most reliable)
                            # test_method field includes 'test_' prefix, so compare with full_method_name
                            if test_method and full_method_name == test_method:
                                # Found exact test_method match - this is the best match
                                if epic_name:
                                    return f"{epic_name} - {scenario_name}"
                                return scenario_name
                            
                            # Second check: match on scenario name (normalized)
                            if not scenario_name:
                                continue
                            scenario_name_norm = self._normalize_name(scenario_name)
                            
                            # Check if method name matches scenario
                            if (method_name_norm in scenario_name_norm or 
                                scenario_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(scenario_name_norm)):
                                # Found scenario match - this is the best match
                                if epic_name:
                                    return f"{epic_name} - {scenario_name}"
                                return scenario_name
                        
                        # Check if method name matches story name (and story matches class)
                        if story_matches_class:
                            if (method_name_norm in story_name_norm or 
                                story_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(story_name_norm)):
                                # Story match - good match if no scenario found
                                if not best_match or best_match_type in ['epic', 'sub_epic']:
                                    best_match = f"{epic_name} - {story_name}" if epic_name else story_name
                                    best_match_type = 'story'
                        
                        # Check acceptance criteria
                        acceptance_criteria = story.get('acceptance_criteria', [])
                        for ac in acceptance_criteria:
                            ac_text = ac.get('text', '') if isinstance(ac, dict) else str(ac)
                            if not ac_text:
                                continue
                            ac_norm = self._normalize_name(ac_text)
                            
                            if (method_name_norm in ac_norm or 
                                ac_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(ac_norm)):
                                # AC match - story level match
                                if not best_match or best_match_type in ['epic', 'sub_epic']:
                                    best_match = f"{epic_name} - {story_name}" if epic_name else story_name
                                    best_match_type = 'story'
                        
                        # Check if method name matches sub-epic name
                        if (method_name_norm in sub_epic_name_norm or 
                            sub_epic_name_norm.startswith(method_name_norm) or
                            method_name_norm.startswith(sub_epic_name_norm)):
                            # Sub-epic match
                            if not best_match or best_match_type == 'epic':
                                best_match = f"{epic_name} - {sub_epic_name}" if epic_name else sub_epic_name
                                best_match_type = 'sub_epic'
                        
                        # Check if method name matches epic name
                        if epic_name_norm and (method_name_norm in epic_name_norm or 
                                             epic_name_norm.startswith(method_name_norm) or
                                             method_name_norm.startswith(epic_name_norm)):
                            # Epic match - least specific, only if nothing else found
                            if not best_match:
                                best_match = epic_name
                                best_match_type = 'epic'
        
        # Special handling for epic/sub-epic related test names
        if 'epic' in method_name_norm.lower():
            for epic in epics:
                epic_name = epic.get('name', '')
                if not epic_name:
                    continue
                
                if 'sub' in method_name_norm.lower():
                    # Looking for sub-epic related test
                    sub_epics = epic.get('sub_epics', [])
                    for sub_epic in sub_epics:
                        sub_epic_name = sub_epic.get('name', '')
                        if sub_epic_name:
                            # Prefer sub-epic match over epic match
                            if not best_match or best_match_type == 'epic':
                                best_match = f"{epic_name} - {sub_epic_name}" if epic_name else sub_epic_name
                                best_match_type = 'sub_epic'
                else:
                    # Looking for epic related test
                    if not best_match:
                        best_match = epic_name
                        best_match_type = 'epic'
        
        return best_match
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a name for comparison (lowercase, remove spaces/punctuation)."""
        return re.sub(r'[^\w]', '', name.lower())
    
    def _pascal_to_story_name(self, pascal_name: str) -> str:
        """Convert PascalCase to story name format."""
        # Insert spaces before capital letters
        return re.sub(r'([A-Z])', r' \1', pascal_name).strip()
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two names match (allowing for variations)."""
        # Normalize: lowercase, remove spaces/punctuation
        n1 = re.sub(r'[^\w]', '', name1.lower())
        n2 = re.sub(r'[^\w]', '', name2.lower())
        return n1 == n2
    
    def _is_abbreviated(self, class_name: str, story_names: List[str]) -> bool:
        """Check if class name appears abbreviated."""
        # Check if class name is much shorter than story names
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        if len(story_name_from_class) < 10:
            return True
        
        # Check for common abbreviations (as standalone words, not part of longer words)
        # Use word boundaries to avoid false positives like "Generate" containing "Gen"
        abbrev_patterns = [r'\bGen\b', r'\bMgr\b', r'\bCfg\b', r'\bSvc\b', r'\bUtil\b', r'\bHelper\b']
        for pattern in abbrev_patterns:
            if re.search(pattern, class_name):
                return True
        
        return False
    
    def _is_generic(self, class_name: str) -> bool:
        """Check if class name is generic."""
        generic_names = ['TestToolGeneration', 'TestValidation', 'TestHelpers', 'TestUtils']
        return class_name in generic_names
    
    def _extract_epic_names(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract epic names from knowledge graph."""
        epic_names = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            epic_name = epic.get('name', '')
            if epic_name:
                # Convert to snake_case for comparison
                snake_case = self._to_snake_case(epic_name)
                epic_names.append(snake_case)
        return epic_names
    
    def _extract_sub_epic_names(self, knowledge_graph: Dict[str, Any]) -> List[str]:
        """Extract sub-epic names from knowledge graph (recursively including nested sub-epics)."""
        sub_epic_names = []
        epics = knowledge_graph.get('epics', [])
        for epic in epics:
            self._extract_sub_epic_names_recursive(epic.get('sub_epics', []), sub_epic_names)
        return sub_epic_names
    
    def _extract_sub_epic_names_recursive(self, sub_epics: List[Dict[str, Any]], result: List[str]) -> None:
        """Recursively extract sub-epic names including nested sub-epics.
        
        CRITICAL: All sub-epic names are normalized via _to_snake_case, which converts
        "&" to "and" so that "Validate Knowledge & Content" matches "validate_knowledge_and_content".
        """
        for sub_epic in sub_epics:
            sub_epic_name = sub_epic.get('name', '')
            if sub_epic_name:
                # Convert to snake_case for comparison
                # This normalization ensures "&" and "and" are treated identically
                snake_case = self._to_snake_case(sub_epic_name)
                result.append(snake_case)
            # Recursively process nested sub-epics
            nested_sub_epics = sub_epic.get('sub_epics', [])
            if nested_sub_epics:
                self._extract_sub_epic_names_recursive(nested_sub_epics, result)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case.
        
        Handles:
        - Spaces -> underscores
        - Ampersands (&, &amp;) -> 'and' (CRITICAL: & and 'and' are treated identically)
        - 'and ' (with trailing space) -> 'and'
        - Special characters -> removed
        - Capital letters -> lowercase with underscores
        
        CRITICAL: This method MUST normalize "&" and "and" to the same value so that
        "Validate Knowledge & Content" matches "validate_knowledge_and_content".
        """
        # Replace HTML entity &amp; with 'and' first (before other processing)
        name = name.replace('&amp;', 'and')
        # Replace ampersand with 'and' before other processing (CRITICAL: & becomes 'and')
        name = name.replace('&', 'and')
        # Normalize 'and ' (with trailing space) to 'and' before space processing
        # This handles cases like "and " -> "and" but doesn't affect "&" -> "and" conversion
        name = re.sub(r'\band\s+', 'and', name)
        # Insert underscores before capital letters (e.g., "ValidateKnowledge" -> "Validate_Knowledge")
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove special characters except underscores (this removes any remaining & that wasn't converted)
        # But we already converted & to 'and' above, so this is just cleanup
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        # Convert to lowercase
        return name.lower()
    
    def _check_file_name_matches_sub_epic(self, file_name: str, sub_epic_names: List[str], file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if test file name matches a sub-epic name.
        
        If a test file doesn't match any sub-epic name:
        - If file name matches an epic name: OK (epic-level helper file or cross-sub-epic test file)
        - If test methods span multiple sub-epics: OK (cross-sub-epic test file)
        - Else: Violation (methods should be in files with sub-epic names)
        """
        # Remove 'test_' prefix if present
        name_without_prefix = file_name[5:] if file_name.startswith('test_') else file_name
        
        # Normalize for comparison
        # CRITICAL: Both file name and sub-epic names must use the same normalization
        # to ensure "&" and "and" are treated identically
        name_normalized = self._to_snake_case(name_without_prefix)
        
        # Check if matches any sub-epic name (exact match or contains)
        # All sub-epic names are already normalized via _to_snake_case in _extract_sub_epic_names_recursive
        matches = [name for name in sub_epic_names if name_normalized == name or name_normalized in name or name in name_normalized]
        
        # If file name matches a sub-epic, no violation
        if matches:
            return None
        
        # Check if file name matches an epic name
        epic_names = self._extract_epic_names(knowledge_graph)
        epic_matches = [name for name in epic_names if name_normalized == name or name_normalized in name or name in name_normalized]
        
        # If file name matches an epic name, check if it's a helper file or spans multiple sub-epics
        if epic_matches:
            # Check if file contains only helper functions (no test classes/methods)
            if self._is_helper_file_only(file_path):
                return None  # No violation - epic-level helper file is OK
            
            # Check if test methods span multiple sub-epics within this epic
            sub_epics_spanned = self._get_sub_epics_spanned_by_test_methods(file_path, knowledge_graph)
            if len(sub_epics_spanned) > 1:
                return None  # No violation - epic-level test file spanning multiple sub-epics is OK
        
        # File name doesn't match any sub-epic or epic - check if methods span multiple sub-epics
        sub_epics_spanned = self._get_sub_epics_spanned_by_test_methods(file_path, knowledge_graph)
        
        # If methods span multiple sub-epics, it's OK (cross-sub-epic test file)
        if len(sub_epics_spanned) > 1:
            return None  # No violation - cross-sub-epic test file is OK
        
        # Methods don't span multiple sub-epics - violation
        suggestions = self._find_closest_sub_epic_names(name_normalized, sub_epic_names)
        suggestion_text = ""
        if suggestions:
            suggestion_list = ", ".join([f"test_{s}.py" for s in suggestions[:5]])  # Limit to top 5
            suggestion_text = f" Suggested names: {suggestion_list}"
        
        return Violation(
            rule=rule_obj,
            violation_message=f'Test file name "{file_name}" does not match any sub-epic name and test methods do not span multiple sub-epics - file should be named test_<sub_epic_name>.py.{suggestion_text}',
            location=str(file_path),
            severity='error'
        ).to_dict()
    
    def _get_sub_epics_spanned_by_test_methods(self, test_file_path: Path, knowledge_graph: Dict[str, Any]) -> set:
        """Get set of sub-epic names that test methods in this file span.
        
        Returns set of sub-epic names (normalized) that the test methods belong to.
        """
        sub_epics = set()
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            # Find all test methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Get class name for context
                        class_name = node.name
                        
                        # Check test methods in this class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('test_'):
                                    # Find which sub-epic this method belongs to
                                    sub_epic = self._find_sub_epic_for_method(item.name, class_name, knowledge_graph)
                                    if sub_epic:
                                        sub_epics.add(self._to_snake_case(sub_epic))
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return sub_epics
    
    def _find_sub_epic_for_method(self, method_name: str, class_name: str, knowledge_graph: Dict[str, Any]) -> Optional[str]:
        """Find the sub-epic name that a test method belongs to.
        
        Returns the sub-epic name if found, None otherwise.
        Uses similar logic to _find_expected_scenario_name but returns sub-epic name.
        """
        method_name_norm = self._normalize_name(method_name)
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        story_name_normalized = self._normalize_name(story_name_from_class)
        
        epics = knowledge_graph.get('epics', [])
        
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                sub_epic_name_norm = self._normalize_name(sub_epic_name) if sub_epic_name else ''
                
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        story_name_norm = self._normalize_name(story_name) if story_name else ''
                        
                        # Check if story matches class name
                        story_matches_class = (story_name_norm == story_name_normalized or 
                                             story_name_norm.startswith(story_name_normalized) or
                                             story_name_normalized.startswith(story_name_norm))
                        
                        # Check scenarios
                        scenarios = story.get('scenarios', [])
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', '')
                            if not scenario_name:
                                continue
                            scenario_name_norm = self._normalize_name(scenario_name)
                            
                            # Check if method name matches scenario
                            if (method_name_norm in scenario_name_norm or 
                                scenario_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(scenario_name_norm)):
                                # Found scenario match - return sub-epic
                                return sub_epic_name
                        
                        # Check if method name matches story name (and story matches class)
                        if story_matches_class:
                            if (method_name_norm in story_name_norm or 
                                story_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(story_name_norm)):
                                # Story match - return sub-epic
                                return sub_epic_name
                        
                        # Check acceptance criteria
                        acceptance_criteria = story.get('acceptance_criteria', [])
                        for ac in acceptance_criteria:
                            ac_text = ac.get('text', '') if isinstance(ac, dict) else str(ac)
                            if not ac_text:
                                continue
                            ac_norm = self._normalize_name(ac_text)
                            
                            if (method_name_norm in ac_norm or 
                                ac_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(ac_norm)):
                                # AC match - return sub-epic
                                return sub_epic_name
                        
                        # Check if method name matches sub-epic name
                        if (method_name_norm in sub_epic_name_norm or 
                            sub_epic_name_norm.startswith(method_name_norm) or
                            method_name_norm.startswith(sub_epic_name_norm)):
                            # Sub-epic match
                            return sub_epic_name
        
        return None
    
    def _find_closest_sub_epic_names(self, file_name: str, sub_epic_names: List[str], max_suggestions: int = 5) -> List[str]:
        """Find the closest matching sub-epic names for suggestions using simple string similarity."""
        if not sub_epic_names:
            return []
        
        # Calculate similarity scores
        scored_names = []
        file_name_lower = file_name.lower()
        
        for sub_epic_name in sub_epic_names:
            sub_epic_lower = sub_epic_name.lower()
            
            # Simple similarity: check for common substrings
            score = 0
            
            # Exact match gets highest score
            if file_name_lower == sub_epic_lower:
                score = 1000
            # Check if file name is contained in sub-epic name or vice versa
            elif file_name_lower in sub_epic_lower:
                score = 50 + len(file_name_lower)  # Longer matches score higher
            elif sub_epic_lower in file_name_lower:
                score = 30 + len(sub_epic_lower)
            else:
                # Check for common words/parts
                file_parts = set(file_name_lower.split('_'))
                sub_epic_parts = set(sub_epic_lower.split('_'))
                common_parts = file_parts.intersection(sub_epic_parts)
                if common_parts:
                    score = len(common_parts) * 10
            
            if score > 0:
                scored_names.append((score, sub_epic_name))
        
        # Sort by score (descending) and return top matches
        scored_names.sort(key=lambda x: x[0], reverse=True)
        return [name for _, name in scored_names[:max_suggestions]]
    
    def _is_helper_file_only(self, file_path: Path) -> bool:
        """Check if file contains only helper functions (no test classes or test methods).
        
        Returns True if file has no test classes (classes starting with 'Test') 
        and no test methods (functions starting with 'test_').
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for test classes or test methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        return False  # Has test class
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        return False  # Has test method
            
            # No test classes or test methods found - it's a helper file
            return True
        except (SyntaxError, UnicodeDecodeError):
            # If we can't parse, assume it's not a helper-only file
            return False
    

