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


class GenericCapabilityScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_capability_verbs(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_passive_states(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_generic_technical_verbs(name, node, node_type, rule_obj)
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
    
    def _check_capability_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        capability_verbs = ['exposes', 'provides', 'contains', 'represents', 'implements', 'supports']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        if words and words[0] in capability_verbs:
            location = node.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=f'{node_type.capitalize()} name "{name}" uses capability verb "{words[0]}" - describe what system DOES (behaviors), not what system IS (capabilities). Use specific actions with actors (e.g., "User invokes tool" not "Exposes tool")',
                location=location,
                severity='error'
            ).to_dict()
        
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                if tokens and tokens[0].lemma_.lower() in capability_verbs:
                    location = node.map_location()
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'{node_type.capitalize()} name "{name}" uses capability verb "{tokens[0].text}" - describe what system DOES (behaviors), not what system IS (capabilities). Use specific actions with actors (e.g., "User invokes tool" not "Exposes tool")',
                        location=location,
                        severity='error'
                    ).to_dict()
            except Exception:
                pass
        
        return None
    
    def _check_passive_states(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        passive_patterns = ['tracks', 'maintains', 'stores', 'holds', 'keeps']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        if words and words[0] in passive_patterns:
            location = node.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=f'{node_type.capitalize()} name "{name}" uses passive state verb "{words[0]}" - use active behaviors instead (e.g., "User updates order count" not "Tracks order count")',
                location=location,
                severity='error'
            ).to_dict()
        
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                if tokens and tokens[0].lemma_.lower() in passive_patterns:
                    location = node.map_location()
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'{node_type.capitalize()} name "{name}" uses passive state verb "{tokens[0].text}" - use active behaviors instead (e.g., "User updates order count" not "Tracks order count")',
                        location=location,
                        severity='error'
                    ).to_dict()
            except Exception:
                pass
        
        return None
    
    def _check_generic_technical_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check for generic technical verbs that don't describe outcomes (e.g., 'Invokes Payment API' -> should be 'Processes Payment')"""
        generic_technical_verbs = ['invokes', 'invoke', 'calls', 'call', 'executes', 'execute', 'triggers', 'trigger']
        technical_nouns = ['api', 'endpoint', 'service', 'method', 'function', 'handler', 'route', 'url']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        if not words:
            return None
        
        # Check if first word is a generic technical verb
        first_word = words[0]
        if first_word in generic_technical_verbs:
            # Check if it's followed by technical nouns (API, endpoint, etc.) without describing outcome
            remaining_text = ' '.join(words[1:])
            has_technical_noun = any(tech_noun in remaining_text for tech_noun in technical_nouns)
            
            # Also check if the noun describes a mechanism rather than an outcome
            # If it says "API", "endpoint", "service" without business context, it's too technical
            if has_technical_noun:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses generic technical verb "{first_word}" without describing outcome - describe what actually happens, not the technical mechanism (e.g., "Processes Payment" not "Invokes Payment API")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        # Check with spaCy for lemmatized forms
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                if tokens and tokens[0].lemma_.lower() in generic_technical_verbs:
                    remaining_text = ' '.join([t.text.lower() for t in tokens[1:]])
                    has_technical_noun = any(tech_noun in remaining_text for tech_noun in technical_nouns)
                    
                    if has_technical_noun:
                        location = node.map_location()
                        return Violation(
                            rule=rule_obj,
                            violation_message=f'{node_type.capitalize()} name "{name}" uses generic technical verb "{tokens[0].text}" without describing outcome - describe what actually happens, not the technical mechanism (e.g., "Processes Payment" not "Invokes Payment API")',
                            location=location,
                            severity='error'
                        ).to_dict()
            except Exception:
                pass
        
        return None

