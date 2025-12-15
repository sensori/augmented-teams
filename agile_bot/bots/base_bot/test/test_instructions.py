"""
Instructions Tests

Tests for all stories in the 'Instructions' sub-epic:
- Get Base Instructions
- Get Behavior Instructions
- Merge Instructions
"""
import pytest
from pathlib import Path
from unittest.mock import Mock
from agile_bot.bots.base_bot.src.bot.instructions import Instructions
from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    given_bot_name_and_behavior_setup
)
from conftest import bot_directory, workspace_directory

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def given_base_action_config_with_instructions(instructions: list):
    """Given: BaseActionConfig with instructions."""
    base_action_config = Mock(spec=BaseActionConfig)
    base_action_config.instructions = instructions
    return base_action_config

def given_base_action_config_with_string_instructions(instructions: str):
    """Given: BaseActionConfig with string instructions."""
    base_action_config = Mock(spec=BaseActionConfig)
    base_action_config.instructions = instructions
    return base_action_config

def given_behavior_with_instructions(instructions: dict):
    """Given: Behavior with instructions."""
    behavior = Mock(spec=Behavior)
    behavior_config = Mock()
    behavior_config.instructions = instructions
    behavior.behavior_config = behavior_config
    return behavior

def when_instructions_instantiated(base_action_config, behavior):
    """When: Instructions instantiated."""
    return Instructions(base_action_config, behavior)

def when_base_instructions_accessed(instructions: Instructions):
    """When: base_instructions property accessed."""
    return instructions.base_instructions

def when_behavior_instructions_accessed(instructions: Instructions):
    """When: behavior_instructions property accessed."""
    return instructions.behavior_instructions

def when_merge_called(instructions: Instructions):
    """When: merge() called."""
    return instructions.merge()

def then_base_instructions_are(result: list, expected: list):
    """Then: Base instructions are expected."""
    assert result == expected

def then_behavior_instructions_are(result: dict, expected: dict):
    """Then: Behavior instructions are expected."""
    assert result == expected

def then_merged_contains_base_instructions(merged: dict, expected: list):
    """Then: Merged dict contains base instructions."""
    assert merged['base_instructions'] == expected

def then_merged_contains_behavior_instructions(merged: dict, expected: dict):
    """Then: Merged dict contains behavior instructions."""
    assert merged['behavior_instructions'] == expected

def then_merged_instructions_list_contains_all(merged: dict, base: list, behavior: list):
    """Then: Merged instructions list contains all instructions."""
    assert 'instructions' in merged
    assert merged['instructions'] == base + behavior

# ============================================================================
# TEST CLASSES
# ============================================================================

class TestGetBaseInstructions:
    """Test Get Base Instructions story."""
    
    def test_base_instructions_property_returns_list_from_config(self):
        """Test: base_instructions property returns list from config."""
        # Given: BaseActionConfig with list instructions
        base_action_config = given_base_action_config_with_instructions(['instruction1', 'instruction2'])
        behavior = given_behavior_with_instructions({})
        
        # When: Instructions instantiated and base_instructions accessed
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_base_instructions_accessed(instructions)
        
        # Then: Base instructions are from config
        then_base_instructions_are(result, ['instruction1', 'instruction2'])
    
    def test_base_instructions_property_converts_string_to_list(self):
        """Test: base_instructions property converts string to list."""
        # Given: BaseActionConfig with string instructions
        base_action_config = given_base_action_config_with_string_instructions('single instruction')
        behavior = given_behavior_with_instructions({})
        
        # When: Instructions instantiated and base_instructions accessed
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_base_instructions_accessed(instructions)
        
        # Then: Base instructions are converted to list
        then_base_instructions_are(result, ['single instruction'])
    
    def test_base_instructions_property_returns_empty_list_when_none(self):
        """Test: base_instructions property returns empty list when None."""
        # Given: BaseActionConfig with None instructions
        base_action_config = Mock(spec=BaseActionConfig)
        base_action_config.instructions = None
        behavior = given_behavior_with_instructions({})
        
        # When: Instructions instantiated and base_instructions accessed
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_base_instructions_accessed(instructions)
        
        # Then: Base instructions are empty list
        then_base_instructions_are(result, [])


class TestGetBehaviorInstructions:
    """Test Get Behavior Instructions story."""
    
    def test_behavior_instructions_property_returns_from_behavior_config(self):
        """Test: behavior_instructions property returns from behavior config."""
        # Given: Behavior with instructions
        behavior_instructions = {'instructions': ['behavior1', 'behavior2']}
        base_action_config = given_base_action_config_with_instructions(['base1'])
        behavior = given_behavior_with_instructions(behavior_instructions)
        
        # When: Instructions instantiated and behavior_instructions accessed
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_behavior_instructions_accessed(instructions)
        
        # Then: Behavior instructions are from config
        then_behavior_instructions_are(result, behavior_instructions)
    
    def test_behavior_instructions_property_returns_empty_dict_when_none(self):
        """Test: behavior_instructions property returns empty dict when None."""
        # Given: Behavior with no instructions
        base_action_config = given_base_action_config_with_instructions(['base1'])
        behavior = given_behavior_with_instructions({})
        
        # When: Instructions instantiated and behavior_instructions accessed
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_behavior_instructions_accessed(instructions)
        
        # Then: Behavior instructions are empty dict
        then_behavior_instructions_are(result, {})


class TestMergeInstructions:
    """Test Merge Instructions story."""
    
    def test_merge_combines_base_and_behavior_instructions(self):
        """Test: merge() combines base and behavior instructions."""
        # Given: BaseActionConfig and Behavior with instructions
        base_action_config = given_base_action_config_with_instructions(['base1', 'base2'])
        behavior_instructions = {'instructions': ['behavior1', 'behavior2']}
        behavior = given_behavior_with_instructions(behavior_instructions)
        
        # When: Instructions instantiated and merge() called
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_merge_called(instructions)
        
        # Then: Merged dict contains both instruction sets
        then_merged_contains_base_instructions(result, ['base1', 'base2'])
        then_merged_contains_behavior_instructions(result, behavior_instructions)
        then_merged_instructions_list_contains_all(result, ['base1', 'base2'], ['behavior1', 'behavior2'])
    
    def test_merge_handles_behavior_instructions_without_instructions_key(self):
        """Test: merge() handles behavior instructions without 'instructions' key."""
        # Given: Behavior with instructions dict without 'instructions' key
        base_action_config = given_base_action_config_with_instructions(['base1'])
        behavior_instructions = {'other_key': 'value'}
        behavior = given_behavior_with_instructions(behavior_instructions)
        
        # When: Instructions instantiated and merge() called
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_merge_called(instructions)
        
        # Then: Merged dict contains base instructions only
        then_merged_contains_base_instructions(result, ['base1'])
        then_merged_contains_behavior_instructions(result, behavior_instructions)
        assert result['instructions'] == ['base1']
    
    def test_merge_handles_non_dict_behavior_instructions(self):
        """Test: merge() handles non-dict behavior instructions."""
        # Given: Behavior with non-dict instructions
        base_action_config = given_base_action_config_with_instructions(['base1'])
        behavior = Mock(spec=Behavior)
        behavior_config = Mock()
        behavior_config.instructions = 'not a dict'
        behavior.behavior_config = behavior_config
        
        # When: Instructions instantiated and merge() called
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_merge_called(instructions)
        
        # Then: Merged dict contains base instructions only
        then_merged_contains_base_instructions(result, ['base1'])
        assert result['instructions'] == ['base1']
    
    def test_merge_handles_empty_behavior_instructions_list(self):
        """Test: merge() handles empty behavior instructions list."""
        # Given: Behavior with empty instructions list
        base_action_config = given_base_action_config_with_instructions(['base1', 'base2'])
        behavior_instructions = {'instructions': []}
        behavior = given_behavior_with_instructions(behavior_instructions)
        
        # When: Instructions instantiated and merge() called
        instructions = when_instructions_instantiated(base_action_config, behavior)
        result = when_merge_called(instructions)
        
        # Then: Merged dict contains only base instructions
        then_merged_contains_base_instructions(result, ['base1', 'base2'])
        assert result['instructions'] == ['base1', 'base2']

