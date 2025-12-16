from typing import List, Dict, Any, Optional
from .story_scanner import StoryScanner
from .story_map import StoryNode, Epic, SubEpic, Story
from agile_bot.bots.base_bot.src.scanners.violation import Violation

try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None


class CommunicationVerbScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_communication_verbs(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_enablement_verbs(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _get_node_type(self, node: StoryNode) -> str:
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _check_communication_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        communication_verbs = ['showing', 'displaying', 'visualizing', 'presenting', 'rendering']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        for word in words:
            if word in communication_verbs:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses communication verb "{word}" - use outcome verbs instead (e.g., "Creates Animation" not "Showing Animation")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                for token in tokens:
                    if token.lemma_.lower() in communication_verbs:
                        location = node.map_location()
                        return Violation(
                            rule=rule_obj,
                            violation_message=f'{node_type.capitalize()} name "{name}" uses communication verb "{token.text}" - use outcome verbs instead (e.g., "Creates Animation" not "Showing Animation")',
                            location=location,
                            severity='error'
                        ).to_dict()
            except Exception:
                pass
        
        return None
    
    def _check_enablement_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        enablement_verbs = ['providing', 'enabling', 'allowing', 'supporting', 'facilitating']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        for word in words:
            if word in enablement_verbs:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses enablement verb "{word}" - use outcome verbs instead (e.g., "Creates Configuration" not "Providing Configuration")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                for token in tokens:
                    if token.lemma_.lower() in enablement_verbs:
                        location = node.map_location()
                        return Violation(
                            rule=rule_obj,
                            violation_message=f'{node_type.capitalize()} name "{name}" uses enablement verb "{token.text}" - use outcome verbs instead (e.g., "Creates Configuration" not "Providing Configuration")',
                            location=location,
                            severity='error'
                        ).to_dict()
            except Exception:
                pass
        
        return None








