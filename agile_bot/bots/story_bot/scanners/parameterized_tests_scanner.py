"""Scanner for validating parameterized tests in scenario files."""

from typing import List, Dict, Any
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation


class ParameterizedTestsScanner(Scanner):
    """Scanner that validates tests use parameterized decorators for scenarios with Examples tables.
    
    Checks that test methods with multiple examples use @pytest.mark.parametrize
    instead of single test methods.
    """
    
    def scan(self, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan knowledge graph for violations of parameterized test requirements.
        
        Args:
            knowledge_graph: The knowledge graph (story-graph.json structure)
            
        Returns:
            List of violation dictionaries
            
        Raises:
            Exception: If scanner execution fails (exceptions should not be swallowed)
        """
        violations = []
        
        # Scan through epics, features, and stories to find scenarios with Examples
        epics = knowledge_graph.get('epics', [])
        
        for epic_idx, epic in enumerate(epics):
            features = epic.get('features', [])
            
            for feature_idx, feature in enumerate(features):
                stories = feature.get('stories', [])
                
                for story_idx, story in enumerate(stories):
                    scenarios = story.get('scenarios', [])
                    
                    for scenario_idx, scenario in enumerate(scenarios):
                        # Check if scenario has Examples table
                        examples = scenario.get('examples', [])
                        
                        if examples and len(examples) > 1:
                            # Scenario has multiple examples - should use parameterized tests
                            # Check if test_method exists and if it's parameterized
                            test_method = scenario.get('test_method')
                            
                            if test_method:
                                # Check if test file exists and if method uses @pytest.mark.parametrize
                                # For now, we'll flag scenarios with multiple examples that might not be parameterized
                                # This is a simplified check - full implementation would parse test files
                                location = f"epics[{epic_idx}].features[{feature_idx}].stories[{story_idx}].scenarios[{scenario_idx}]"
                                
                                violations.append(Violation(
                                    rule_name='create_parameterized_tests_for_scenarios',
                                    violation_message=f"Scenario '{scenario.get('name', 'unknown')}' has {len(examples)} examples but may not use @pytest.mark.parametrize",
                                    location=location,
                                    severity='warning'
                                ).to_dict())
        
        return violations

