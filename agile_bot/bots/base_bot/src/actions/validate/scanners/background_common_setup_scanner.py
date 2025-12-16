"""Scanner for validating Background section usage in scenarios."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryNode, Story
from .violation import Violation


class BackgroundCommonSetupScanner(StoryScanner):
    """Validates Background section is ONLY for common setup steps shared across 3+ scenarios.
    
    Background contains only Given/And steps (no When/Then).
    Scenario-specific setup goes in scenario Steps as Given steps, not in Background.
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            background = story_data.get('background', [])
            
            if background:
                # Check if background has When/Then (should only have Given/And)
                violation = self._check_background_has_when_then(background, node, rule_obj)
                if violation:
                    violations.append(violation)
                
                # Check if background is used for scenario-specific setup
                violation = self._check_background_scenario_specific(background, scenarios, node, rule_obj)
                if violation:
                    violations.append(violation)
            
            # Check if scenarios have 3+ but no background (might need one)
            if len(scenarios) >= 3 and not background:
                # Check if scenarios share common setup that should be in background
                violation = self._check_missing_background(scenarios, node, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_background_has_when_then(self, background: List[str], node: StoryNode, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if background contains When/Then steps (should only have Given/And)."""
        for step in background:
            step_lower = step.lower().strip()
            if step_lower.startswith('when ') or step_lower.startswith('then '):
                location = f"{node.map_location()}.background"
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Background contains "{step}" - Background should only contain Given/And steps, not When/Then',
                    location=location,
                    severity='error'
                ).to_dict()
        return None
    
    def _check_background_scenario_specific(self, background: List[str], scenarios: List[Dict[str, Any]], node: StoryNode, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if background contains scenario-specific setup (should be common to 3+ scenarios)."""
        # This is harder to validate automatically - would need to check if background steps
        # appear in all scenarios. For now, just check if background has very specific content
        # that suggests it's scenario-specific
        
        # If only 1-2 scenarios, background shouldn't exist (not common enough)
        if len(scenarios) < 3 and background:
            location = f"{node.map_location()}.background"
            return Violation(
                rule=rule_obj,
                violation_message=f'Background exists but story has only {len(scenarios)} scenario(s) - Background should only be used when 3+ scenarios share common setup',
                location=location,
                severity='warning'
            ).to_dict()
        
        return None
    
    def _check_missing_background(self, scenarios: List[Dict[str, Any]], node: StoryNode, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if scenarios share common setup that should be in background."""
        # Check if all scenarios start with same Given steps
        if len(scenarios) >= 3:
            first_scenario_steps = self._get_given_steps(scenarios[0])
            if first_scenario_steps:
                # Check if other scenarios start with same steps
                all_match = all(
                    self._get_given_steps(scenario)[:len(first_scenario_steps)] == first_scenario_steps
                    for scenario in scenarios[1:]
                )
                if all_match and len(first_scenario_steps) > 0:
                    location = f"{node.map_location()}"
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Story has {len(scenarios)} scenarios that all start with same Given steps - consider moving common setup to Background section',
                        location=location,
                        severity='info'
                    ).to_dict()
        
        return None
    
    def _get_given_steps(self, scenario: Dict[str, Any]) -> List[str]:
        """Extract Given/And steps from scenario."""
        steps = []
        scenario_steps = self._get_scenario_steps(scenario)
        for step in scenario_steps:
            step_lower = step.lower().strip()
            if step_lower.startswith('given ') or step_lower.startswith('and '):
                steps.append(step)
            else:
                break  # Stop at first When/Then
        return steps
    
    def _get_scenario_steps(self, scenario: Dict[str, Any]) -> List[str]:
        """Extract scenario steps from scenario dict."""
        if isinstance(scenario, dict):
            if 'steps' in scenario:
                return scenario['steps']
            elif 'scenario' in scenario:
                scenario_text = scenario['scenario']
                if isinstance(scenario_text, str):
                    return [s.strip() for s in scenario_text.split('\n') if s.strip()]
        return []

