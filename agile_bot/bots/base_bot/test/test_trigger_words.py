"""
Trigger Words Tests

Tests for all stories in the 'Trigger Words' sub-epic:
- Match Trigger Pattern
- Get Trigger Priority
- Match Text Against Triggers
"""
import pytest
from pathlib import Path
from unittest.mock import Mock
from agile_bot.bots.base_bot.src.bot.trigger_words import TriggerWords
from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    given_bot_name_and_behavior_setup
)
from conftest import bot_directory, workspace_directory

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def given_behavior_config_with_trigger_patterns(patterns: list, priority: int = 0):
    """Given: BehaviorConfig with trigger patterns."""
    behavior_config = Mock(spec=BehaviorConfig)
    behavior_config.trigger_words = {
        'patterns': patterns,
        'priority': priority
    }
    return behavior_config

def given_behavior_config_with_list_triggers(patterns: list):
    """Given: BehaviorConfig with list trigger words."""
    behavior_config = Mock(spec=BehaviorConfig)
    behavior_config.trigger_words = patterns
    return behavior_config

def given_behavior_config_with_no_triggers():
    """Given: BehaviorConfig with no trigger words."""
    behavior_config = Mock(spec=BehaviorConfig)
    behavior_config.trigger_words = None
    return behavior_config

def when_trigger_words_instantiated(behavior_config, behavior=None):
    """When: TriggerWords instantiated."""
    return TriggerWords(behavior_config, behavior)

def when_match_pattern_called(trigger_words: TriggerWords, pattern: str, text: str):
    """When: match_pattern() called."""
    return trigger_words.match_pattern(pattern, text)

def when_matches_called(trigger_words: TriggerWords, text: str):
    """When: matches() called."""
    return trigger_words.matches(text)

def when_priority_accessed(trigger_words: TriggerWords):
    """When: priority property accessed."""
    return trigger_words.priority

def then_pattern_matches(result: bool):
    """Then: Pattern matches."""
    assert result is True

def then_pattern_does_not_match(result: bool):
    """Then: Pattern does not match."""
    assert result is False

def then_priority_is(result: int, expected: int):
    """Then: Priority is expected value."""
    assert result == expected

def then_no_match_returned(result: bool):
    """Then: No match returned."""
    assert result is False

# ============================================================================
# TEST CLASSES
# ============================================================================

class TestMatchTriggerPattern:
    """Test Match Trigger Pattern story."""
    
    def test_match_pattern_with_regex_pattern(self):
        """Test: match_pattern() matches regex pattern."""
        # Given: BehaviorConfig with regex pattern
        behavior_config = given_behavior_config_with_trigger_patterns(['test.*pattern'])
        
        # When: TriggerWords instantiated and match_pattern() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_match_pattern_called(trigger_words, 'test.*pattern', 'test this pattern')
        
        # Then: Pattern matches
        then_pattern_matches(result)
    
    def test_match_pattern_with_literal_string(self):
        """Test: match_pattern() matches literal string."""
        # Given: BehaviorConfig with literal pattern
        behavior_config = given_behavior_config_with_trigger_patterns(['test'])
        
        # When: TriggerWords instantiated and match_pattern() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_match_pattern_called(trigger_words, 'test', 'This is a test string')
        
        # Then: Pattern matches
        then_pattern_matches(result)
    
    def test_match_pattern_case_insensitive(self):
        """Test: match_pattern() is case insensitive."""
        # Given: BehaviorConfig with pattern
        behavior_config = given_behavior_config_with_trigger_patterns(['TEST'])
        
        # When: TriggerWords instantiated and match_pattern() called with lowercase
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_match_pattern_called(trigger_words, 'TEST', 'this is a test')
        
        # Then: Pattern matches (case insensitive)
        then_pattern_matches(result)
    
    def test_match_pattern_with_invalid_regex_falls_back_to_literal(self):
        """Test: match_pattern() falls back to literal matching for invalid regex."""
        # Given: BehaviorConfig with invalid regex pattern
        behavior_config = given_behavior_config_with_trigger_patterns(['['])
        
        # When: TriggerWords instantiated and match_pattern() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_match_pattern_called(trigger_words, '[', 'This contains [ bracket')
        
        # Then: Pattern matches (fallback to literal)
        then_pattern_matches(result)
    
    def test_match_pattern_does_not_match_when_text_does_not_contain_pattern(self):
        """Test: match_pattern() returns False when text doesn't contain pattern."""
        # Given: BehaviorConfig with pattern
        behavior_config = given_behavior_config_with_trigger_patterns(['xyz'])
        
        # When: TriggerWords instantiated and match_pattern() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_match_pattern_called(trigger_words, 'xyz', 'abc def')
        
        # Then: Pattern does not match
        then_pattern_does_not_match(result)


class TestGetTriggerPriority:
    """Test Get Trigger Priority story."""
    
    def test_priority_property_returns_configured_priority(self):
        """Test: priority property returns configured priority."""
        # Given: BehaviorConfig with priority
        behavior_config = given_behavior_config_with_trigger_patterns(['test'], priority=5)
        
        # When: TriggerWords instantiated and priority accessed
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_priority_accessed(trigger_words)
        
        # Then: Priority is configured value
        then_priority_is(result, 5)
    
    def test_priority_property_returns_zero_when_not_configured(self):
        """Test: priority property returns 0 when not configured."""
        # Given: BehaviorConfig without priority
        behavior_config = given_behavior_config_with_trigger_patterns(['test'])
        
        # When: TriggerWords instantiated and priority accessed
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_priority_accessed(trigger_words)
        
        # Then: Priority is 0
        then_priority_is(result, 0)
    
    def test_priority_property_returns_zero_for_list_triggers(self):
        """Test: priority property returns 0 for list trigger format."""
        # Given: BehaviorConfig with list triggers
        behavior_config = given_behavior_config_with_list_triggers(['test', 'pattern'])
        
        # When: TriggerWords instantiated and priority accessed
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_priority_accessed(trigger_words)
        
        # Then: Priority is 0
        then_priority_is(result, 0)


class TestMatchTextAgainstTriggers:
    """Test Match Text Against Triggers story."""
    
    def test_matches_returns_true_when_text_matches_any_pattern(self):
        """Test: matches() returns True when text matches any pattern."""
        # Given: BehaviorConfig with multiple patterns
        behavior_config = given_behavior_config_with_trigger_patterns(['test', 'pattern', 'xyz'])
        
        # When: TriggerWords instantiated and matches() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_matches_called(trigger_words, 'This is a test')
        
        # Then: Match returned
        then_pattern_matches(result)
    
    def test_matches_returns_false_when_no_patterns_match(self):
        """Test: matches() returns False when no patterns match."""
        # Given: BehaviorConfig with patterns
        behavior_config = given_behavior_config_with_trigger_patterns(['xyz', 'abc'])
        
        # When: TriggerWords instantiated and matches() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_matches_called(trigger_words, 'This is a test')
        
        # Then: No match returned
        then_no_match_returned(result)
    
    def test_matches_returns_false_when_no_triggers_configured(self):
        """Test: matches() returns False when no triggers configured."""
        # Given: BehaviorConfig with no triggers
        behavior_config = given_behavior_config_with_no_triggers()
        
        # When: TriggerWords instantiated and matches() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_matches_called(trigger_words, 'This is a test')
        
        # Then: No match returned
        then_no_match_returned(result)
    
    def test_matches_works_with_list_trigger_format(self):
        """Test: matches() works with list trigger format."""
        # Given: BehaviorConfig with list triggers
        behavior_config = given_behavior_config_with_list_triggers(['test', 'pattern'])
        
        # When: TriggerWords instantiated and matches() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_matches_called(trigger_words, 'This is a test')
        
        # Then: Match returned
        then_pattern_matches(result)
    
    def test_matches_checks_all_patterns_until_match_found(self):
        """Test: matches() checks all patterns until match found."""
        # Given: BehaviorConfig with multiple patterns where first doesn't match
        behavior_config = given_behavior_config_with_trigger_patterns(['xyz', 'abc', 'test'])
        
        # When: TriggerWords instantiated and matches() called
        trigger_words = when_trigger_words_instantiated(behavior_config)
        result = when_matches_called(trigger_words, 'This is a test')
        
        # Then: Match returned (third pattern matches)
        then_pattern_matches(result)

