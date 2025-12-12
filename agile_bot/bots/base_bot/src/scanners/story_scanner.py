from abc import abstractmethod
from typing import List, Dict, Any, Optional
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from .story_map import StoryMap, StoryNode, StoryGroup


class StoryScanner(Scanner):
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        if not rule_obj:
            raise ValueError("rule_obj parameter is required for StoryScanner")
        
        violations = []
        story_map = StoryMap(knowledge_graph)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if not isinstance(node, StoryGroup):
                    node_violations = self.scan_story_node(node, rule_obj)
                    violations.extend(node_violations)
        
        return violations
    
    @abstractmethod
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        pass

