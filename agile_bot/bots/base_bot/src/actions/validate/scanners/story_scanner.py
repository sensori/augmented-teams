from abc import abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner
from .story_map import StoryMap, StoryNode, StoryGroup

if TYPE_CHECKING:
    from .domain_concept_node import DomainConceptNode
else:
    from .domain_concept_node import DomainConceptNode


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
        # Extract story_graph from knowledge_graph if nested
        story_graph_data = knowledge_graph.get('story_graph', knowledge_graph)
        story_map = StoryMap(story_graph_data)
        
        # Scan domain concepts from epics and sub_epics
        for epic in story_map.epics():
            # Scan domain concepts at epic level
            epic_violations = self._scan_domain_concepts(
                epic.data.get('domain_concepts', []),
                epic.epic_idx,
                None,
                rule_obj
            )
            violations.extend(epic_violations)
            
            # Walk through all nodes (including sub_epics)
            for node in story_map.walk(epic):
                # Scan domain concepts at sub_epic level
                if hasattr(node, 'data') and 'domain_concepts' in node.data:
                    sub_epic_violations = self._scan_domain_concepts(
                        node.data.get('domain_concepts', []),
                        epic.epic_idx,
                        getattr(node, 'sub_epic_path', None),
                        rule_obj
                    )
                    violations.extend(sub_epic_violations)
                
                # Also scan story nodes if needed (for other validations)
                if not isinstance(node, StoryGroup):
                    node_violations = self.scan_story_node(node, rule_obj)
                    violations.extend(node_violations)
        
        return violations
    
    def _scan_domain_concepts(
        self,
        domain_concepts: List[Dict[str, Any]],
        epic_idx: int,
        sub_epic_path: Optional[List[int]],
        rule_obj: Any
    ) -> List[Dict[str, Any]]:
        """Scan domain concepts for violations."""
        violations = []
        
        for concept_idx, concept_data in enumerate(domain_concepts):
            concept_name = concept_data.get('name', '')
            responsibilities = concept_data.get('responsibilities', [])
            
            # Create a domain concept node for scanning
            domain_concept_node = DomainConceptNode(
                concept_data,
                epic_idx,
                sub_epic_path,
                concept_idx
            )
            
            # Scan the domain concept
            concept_violations = self.scan_domain_concept(domain_concept_node, rule_obj)
            violations.extend(concept_violations)
        
        return violations
    
    @abstractmethod
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        pass
    
    def scan_domain_concept(self, node: 'DomainConceptNode', rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan a domain concept node. Override in subclasses to validate domain concepts."""
        # Default implementation calls scan_story_node for compatibility
        return self.scan_story_node(node, rule_obj)

