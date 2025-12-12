from typing import List, Dict, Any, Optional
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from agile_bot.bots.base_bot.src.scanners.violation import Violation
from agile_bot.bots.base_bot.src.scanners.story_map import StoryMap, StoryNode, Story


class ParameterizedTestsScanner(Scanner):
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        if not rule_obj:
            raise ValueError("rule_obj parameter is required for ParameterizedTestsScanner")
        
        violations = []
        story_map = StoryMap(knowledge_graph)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if isinstance(node, Story):
                    for scenario_outline in node.scenario_outlines:
                        if scenario_outline.examples_rows and len(scenario_outline.examples_rows) > 1:
                            location = scenario_outline.map_location()
                            violations.append(Violation(
                                rule=rule_obj,
                                violation_message=f"Scenario outline '{scenario_outline.name}' has {len(scenario_outline.examples_rows)} examples but may not use @pytest.mark.parametrize",
                                location=location,
                                severity='warning'
                            ).to_dict())
        
        return violations

