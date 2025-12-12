"""Scanner for validating vertical slices in increments."""

from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryNode, Epic
from .violation import Violation


class VerticalSliceScanner(StoryScanner):
    """Validates increments span multiple epics (vertical slices).
    
    Detects single-epic increments (horizontal layer violation).
    """
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # This scanner works on increments, not individual story nodes
        # It needs to check increment structure
        return violations
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Scan increments for vertical slice violations."""
        violations = []
        
        if not rule_obj:
            raise ValueError("rule_obj parameter is required")
        
        # Check increments
        increments = knowledge_graph.get('increments', [])
        
        for increment_idx, increment in enumerate(increments):
            increment_epics = increment.get('epics', [])
            
            # Check if increment spans only one epic (horizontal layer violation)
            if len(increment_epics) == 1:
                location = f"increments[{increment_idx}]"
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Increment "{increment.get("name", f"Increment {increment_idx+1}")}" spans only 1 epic - increments should be vertical slices spanning multiple epics',
                    location=location,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations

