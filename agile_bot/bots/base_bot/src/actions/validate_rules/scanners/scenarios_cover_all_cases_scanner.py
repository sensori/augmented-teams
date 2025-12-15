"""Scanner for validating scenarios cover all cases (happy path, edge cases, error cases)."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryNode, Story
from .violation import Violation
import re


class ScenariosCoverAllCasesScanner(StoryScanner):
    """Validates scenarios cover happy path, edge cases, and error cases."""
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            if len(scenarios) > 0:
                # Check scenario coverage
                has_happy_path = False
                has_edge_case = False
                has_error_case = False
                
                for scenario_idx, scenario in enumerate(scenarios):
                    scenario_text = self._get_scenario_text(scenario)
                    
                    if self._is_happy_path(scenario_text):
                        has_happy_path = True
                    if self._is_edge_case(scenario_text):
                        has_edge_case = True
                    if self._is_error_case(scenario_text):
                        has_error_case = True
                
                # Report missing coverage
                if not has_happy_path:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no happy path scenario - add a scenario covering the normal success case',
                        location=node.map_location(),
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                
                if not has_edge_case and len(scenarios) > 1:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no edge case scenario - add scenarios covering boundary values and edge conditions',
                        location=node.map_location(),
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                
                if not has_error_case and len(scenarios) > 1:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no error case scenario - add scenarios covering invalid inputs and error conditions',
                        location=node.map_location(),
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations
    
    def _get_scenario_text(self, scenario: Dict[str, Any]) -> str:
        """Extract scenario text from scenario dict."""
        if isinstance(scenario, dict):
            return scenario.get('scenario', '') or scenario.get('name', '') or str(scenario)
        return str(scenario)
    
    def _is_happy_path(self, scenario_text: str) -> bool:
        """Check if scenario is a happy path (success case)."""
        text_lower = scenario_text.lower()
        # Happy path indicators: valid, success, saves, completes, etc.
        happy_indicators = ['valid', 'success', 'saves', 'completes', 'accepts', 'processes']
        return any(indicator in text_lower for indicator in happy_indicators)
    
    def _is_edge_case(self, scenario_text: str) -> bool:
        """Check if scenario is an edge case (boundary values)."""
        text_lower = scenario_text.lower()
        # Edge case indicators: boundary, edge, limit, maximum, minimum, empty, null, zero
        edge_indicators = ['boundary', 'edge', 'limit', 'maximum', 'minimum', 'max', 'min', 'empty', 'null', 'zero', 'first', 'last']
        return any(indicator in text_lower for indicator in edge_indicators)
    
    def _is_error_case(self, scenario_text: str) -> bool:
        """Check if scenario is an error case (invalid inputs, failures)."""
        text_lower = scenario_text.lower()
        # Error case indicators: error, invalid, fails, rejects, exception, wrong
        error_indicators = ['error', 'invalid', 'fails', 'rejects', 'exception', 'wrong', 'missing', 'not found']
        return any(indicator in text_lower for indicator in error_indicators)

