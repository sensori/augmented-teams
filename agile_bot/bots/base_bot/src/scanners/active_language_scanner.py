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

import re


class ActiveLanguageScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_passive_voice(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_capability_nouns(name, node, node_type, rule_obj)
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
    
    def _check_passive_voice(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                for i, token in enumerate(tokens):
                    if token.lemma_.lower() in ['be', 'is', 'are', 'was', 'were', 'been', 'being']:
                        if i + 1 < len(tokens):
                            next_token = tokens[i + 1]
                            if next_token.tag_ in ['VBN', 'VBD']:
                                location = node.map_location()
                                return Violation(
                                    rule=rule_obj,
                                    violation_message=f'{node_type.capitalize()} name "{name}" uses passive voice - use active voice (e.g., "Places Order" not "Order is placed")',
                                    location=location,
                                    severity='error'
                                ).to_dict()
            except Exception:
                pass
        
        passive_voice_patterns = [
            r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were|be|been|being)\s+\w+en\b',
        ]
        
        for pattern in passive_voice_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses passive voice - use active voice (e.g., "Places Order" not "Order is placed")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None
    
    def _check_capability_nouns(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if SPACY_AVAILABLE and nlp is not None:
            try:
                doc = nlp(name)
                tokens = [token for token in doc if not token.is_punct]
                
                for idx, token in enumerate(tokens):
                    is_last = (idx == len(tokens) - 1)
                    has_three_or_more_words = (len(tokens) >= 3)
                    if token.tag_ == 'VBG' and token.pos_ == 'NOUN' and is_last:
                        # Allow gerund as last word when name has 3 or more words (per user rule)
                        if has_three_or_more_words:
                            continue
                        if not any(exclude.lower() in name.lower() for exclude in ["User Story", "Epic", "Feature"]):
                            location = node.map_location()
                            return Violation(
                                rule=rule_obj,
                                violation_message=f'{node_type.capitalize()} name "{name}" uses capability noun (gerund) - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")',
                                location=location,
                                severity='error'
                            ).to_dict()
                    
                    if token.tag_ in ['NN', 'NNS'] and any(token.text.endswith(suffix) for suffix in ['ment', 'ance', 'ence']) and is_last:
                        # Allow abstract-noun suffix as last word when name has 3 or more words (per user rule)
                        if has_three_or_more_words:
                            continue
                        if not any(exclude.lower() in name.lower() for exclude in ["User Story", "Epic", "Feature"]):
                            location = node.map_location()
                            return Violation(
                                rule=rule_obj,
                                violation_message=f'{node_type.capitalize()} name "{name}" uses capability noun - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")',
                                location=location,
                                severity='error'
                            ).to_dict()
            except Exception:
                pass
        
        # Regex fallback: only flag if the last word ends with capability/gerund suffix
        capability_noun_patterns = [
            r'\b[A-Z]\w+(ing|ment|ance|ence)\b$',
            r'.*\s+[A-Z]\w+(ing|ment|ance|ence)\b$',
        ]
        
        for pattern in capability_noun_patterns:
            if re.search(pattern, name):
                # Allow when the name has 3 or more words (per user rule)
                if len(name.split()) >= 3:
                    break
                if not any(re.search(r'\b' + exclude + r'\b', name, re.IGNORECASE) for exclude in ["User Story", "Epic", "Feature"]):
                    location = node.map_location()
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'{node_type.capitalize()} name "{name}" uses capability noun - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")',
                        location=location,
                        severity='error'
                    ).to_dict()
        
        return None

