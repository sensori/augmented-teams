from typing import List, Dict, Any, Optional, Tuple
from .story_scanner import StoryScanner
from .story_map import StoryNode, Epic, SubEpic, Story
from agile_bot.bots.base_bot.src.scanners.violation import Violation

import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


class VerbNounScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_verb_noun_order(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_gerund_ending(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_verb_noun_pattern(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_verb_pattern(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_actor_prefix(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_only(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_third_person_singular(name, node, node_type, rule_obj)
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
    
    def _get_tokens_and_tags(self, text: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Tokenize text and get POS tags using NLTK."""
        try:
            tokens = word_tokenize(text)
            # Filter out punctuation
            tokens = [t for t in tokens if t.isalnum() or any(c.isalnum() for c in t)]
            tags = pos_tag(tokens)
            return tokens, tags
        except Exception:
            return [], []
    
    def _is_verb(self, tag: str) -> bool:
        """Check if NLTK tag is a verb."""
        verb_tags = ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']
        return tag in verb_tags
    
    def _is_noun(self, tag: str) -> bool:
        """Check if NLTK tag is a noun."""
        noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
        return tag in noun_tags
    
    def _is_proper_noun(self, tag: str) -> bool:
        """Check if NLTK tag is a proper noun."""
        proper_noun_tags = ['NNP', 'NNPS']
        return tag in proper_noun_tags
    
    def _can_be_verb(self, word: str) -> bool:
        """Check if a word can be a verb using WordNet.
        
        Uses NLTK's WordNet to check if the word has verb senses.
        This is more reliable than maintaining a hardcoded list of verbs.
        """
        try:
            word_lower = word.lower()
            # Check if word has verb senses in WordNet
            synsets = wn.synsets(word_lower, pos=wn.VERB)
            if synsets:
                return True
            
            # Also check all synsets - sometimes verbs are stored without explicit pos filter
            for synset in wn.synsets(word_lower):
                if 'v' in synset.pos():
                    return True
            
            return False
        except Exception:
            # If WordNet lookup fails, return False
            return False
    
    def _check_verb_noun_order(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 2:
                return None
            
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            
            if self._is_verb(first_tag) and (self._is_noun(second_tag) or self._is_proper_noun(second_tag)):
                return None
            
        except Exception:
            pass
        
        return None
    
    def _check_gerund_ending(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            if tags[0][1] == "VBG":
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses gerund (-ing) form - use present tense verb (e.g., "Places Order" not "Placing Order")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            pass
        
        return None
    
    def _check_third_person_singular(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check for third-person singular verb forms (selects, groups, displays, adds, removes, etc.) and flag them.
        
        Third-person singular verbs end in -s/-es and are tagged as VBZ by NLTK.
        We want base verb forms (imperative/infinitive) instead.
        """
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            # Check if first word is third-person singular verb (VBZ tag)
            if tags[0][1] == "VBZ":
                first_word = tags[0][0]
                # Convert to base form (remove -s/-es ending)
                base_form = self._convert_to_base_form(first_word)
                
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses third-person singular verb form ("{first_word}") - use base verb form instead (e.g., "{base_form} Multiple Tokens" not "{first_word} Multiple Tokens")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            pass
        
        return None
    
    def _convert_to_base_form(self, verb: str) -> str:
        """Convert third-person singular verb to base form.
        
        Examples:
        - "selects" -> "select"
        - "groups" -> "group"
        - "displays" -> "display"
        - "adds" -> "add"
        - "removes" -> "remove"
        - "chooses" -> "choose"
        - "goes" -> "go"
        - "fixes" -> "fix"
        """
        verb_lower = verb.lower()
        
        # Handle truly irregular verbs that don't follow regular patterns
        irregular_map = {
            "goes": "go",
            "does": "do",
            "has": "have",
            "is": "be",
            "says": "say",
        }
        
        if verb_lower in irregular_map:
            base = irregular_map[verb_lower]
            # Preserve original capitalization
            if verb[0].isupper():
                return base.capitalize()
            return base
        
        # Regular verbs: remove -s or -es ending
        # Handle verbs ending in -ies (e.g., "tries" -> "try", "flies" -> "fly")
        if verb_lower.endswith("ies") and len(verb_lower) > 3:
            base = verb_lower[:-3] + "y"
        # Handle verbs ending in -es (e.g., "fixes" -> "fix", "watches" -> "watch", "goes" -> "go")
        elif verb_lower.endswith("es") and len(verb_lower) > 2:
            # Most verbs ending in -es just drop the -es
            base = verb_lower[:-2]
        # Handle verbs ending in -s (e.g., "selects" -> "select", "groups" -> "group")
        elif verb_lower.endswith("s") and len(verb_lower) > 1:
            base = verb_lower[:-1]
        else:
            # Doesn't end in -s/-es, return as-is (shouldn't happen for VBZ verbs)
            return verb
        
        # Preserve original capitalization
        if verb[0].isupper():
            return base.capitalize()
        return base
    
    def _check_noun_verb_noun_pattern(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 3:
                return None
            
            words = [tag[0].lower() for tag in tags]
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            third_tag = tags[2][1]
            
            if (self._is_noun(first_tag) or self._is_proper_noun(first_tag)) and \
               self._is_verb(second_tag) and \
               (self._is_noun(third_tag) or self._is_proper_noun(third_tag)):
                actor_words = ["customer", "user", "admin", "developer", "system", "api"]
                if words[0] in actor_words:
                    location = node.map_location()
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'{node_type.capitalize()} name "{name}" uses noun-verb-noun pattern (actor prefix) - use verb-noun format without actor (e.g., "Places Order" not "Customer places order")',
                        location=location,
                        severity='error'
                    ).to_dict()
        
        except Exception:
            pass
        
        return None
    
    def _check_noun_verb_pattern(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check for noun-verb pattern violations. Uses NLTK for accurate POS tagging."""
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 2:
                return None
            
            first_word = tags[0][0]
            first_word_lower = first_word.lower()
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            
            # If NLTK tags first word as verb, trust it - don't flag
            if self._is_verb(first_tag):
                return None
            
            # If WordNet says first word can be a verb, trust it - don't flag
            # This handles cases where NLTK mis-tags capitalized verbs as proper nouns
            if self._can_be_verb(first_word_lower):
                return None
            
            # Flag if first word is NOUN/PROPN and second is VERB (noun-verb pattern)
            # Only flag if first is definitely NOT a verb
            if (self._is_noun(first_tag) or self._is_proper_noun(first_tag)) and self._is_verb(second_tag):
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            # If NLTK fails, return None to avoid false positives
            return None
        
        return None
    
    def _check_actor_prefix(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        name_lower = name.lower().strip()
        words = name_lower.split()
        
        if not words:
            return None
        
        actor_words = ["customer", "user", "admin", "developer", "system", "api"]
        if words[0] in actor_words:
            location = node.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=f'{node_type.capitalize()} name "{name}" contains actor prefix (e.g., "Customer") - use verb-noun format without actor',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_noun_only(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if name appears to be noun-only (no verb)."""
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            # Check if any tag is a verb (trust NLTK)
            has_verb = any(self._is_verb(tag[1]) for tag in tags)
            
            # If NLTK didn't find a verb, check if first word can be a verb using WordNet
            # (NLTK often tags capitalized verbs as proper nouns NNP)
            if not has_verb and tokens:
                first_word_lower = tokens[0].lower()
                if self._can_be_verb(first_word_lower):
                    has_verb = True
            
            if not has_verb:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            # NLTK POS tagging failed - return None to avoid false positives
            pass
        
        return None

