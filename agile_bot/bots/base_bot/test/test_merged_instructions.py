"""
Merged Instructions Tests

Tests for all stories in the 'Merged Instructions' sub-epic:
- Get Base Instructions
- Get Render Instructions
- Merge Base and Render Instructions
"""
import pytest
from pathlib import Path
from unittest.mock import Mock
from agile_bot.bots.base_bot.src.bot.merged_instructions import MergedInstructions
from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
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

def given_render_instructions(instructions: dict):
    """Given: Render instructions dict."""
    return instructions

def when_merged_instructions_instantiated(base_action_config, render_instructions=None):
    """When: MergedInstructions instantiated."""
    return MergedInstructions(base_action_config, render_instructions)

def when_base_instructions_accessed(merged_instructions: MergedInstructions):
    """When: base_instructions property accessed."""
    return merged_instructions.base_instructions

def when_render_instructions_accessed(merged_instructions: MergedInstructions):
    """When: render_instructions property accessed."""
    return merged_instructions.render_instructions

def when_merge_called(merged_instructions: MergedInstructions):
    """When: merge() called."""
    return merged_instructions.merge()

def then_base_instructions_are(result: list, expected: list):
    """Then: Base instructions are expected."""
    assert result == expected

def then_render_instructions_are(result: dict, expected: dict):
    """Then: Render instructions are expected."""
    assert result == expected

def then_render_instructions_is_none(result):
    """Then: Render instructions is None."""
    assert result is None

def then_merged_contains_base_instructions(merged: dict, expected: list):
    """Then: Merged dict contains base instructions."""
    assert merged['base_instructions'] == expected

def then_merged_contains_render_instructions(merged: dict, expected: dict):
    """Then: Merged dict contains render instructions."""
    assert 'render_instructions' in merged
    assert merged['render_instructions'] == expected

def then_merged_does_not_contain_render_instructions(merged: dict):
    """Then: Merged dict does not contain render instructions."""
    assert 'render_instructions' not in merged

# ============================================================================
# TEST CLASSES
# ============================================================================

class TestGetBaseInstructions:
    """Test Get Base Instructions story."""
    
    def test_base_instructions_property_returns_list_from_config(self):
        """Test: base_instructions property returns list from config."""
        # Given: BaseActionConfig with list instructions
        base_action_config = given_base_action_config_with_instructions(['instruction1', 'instruction2'])
        
        # When: MergedInstructions instantiated and base_instructions accessed
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_base_instructions_accessed(merged_instructions)
        
        # Then: Base instructions are from config
        then_base_instructions_are(result, ['instruction1', 'instruction2'])
    
    def test_base_instructions_property_converts_string_to_list(self):
        """Test: base_instructions property converts string to list."""
        # Given: BaseActionConfig with string instructions
        base_action_config = given_base_action_config_with_string_instructions('single instruction')
        
        # When: MergedInstructions instantiated and base_instructions accessed
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_base_instructions_accessed(merged_instructions)
        
        # Then: Base instructions are converted to list
        then_base_instructions_are(result, ['single instruction'])
    
    def test_base_instructions_property_returns_empty_list_when_none(self):
        """Test: base_instructions property returns empty list when None."""
        # Given: BaseActionConfig with None instructions
        base_action_config = Mock(spec=BaseActionConfig)
        base_action_config.instructions = None
        
        # When: MergedInstructions instantiated and base_instructions accessed
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_base_instructions_accessed(merged_instructions)
        
        # Then: Base instructions are empty list
        then_base_instructions_are(result, [])
    
    def test_base_instructions_returns_copy_not_reference(self):
        """Test: base_instructions property returns copy, not reference."""
        # Given: BaseActionConfig with list instructions
        original_list = ['instruction1', 'instruction2']
        base_action_config = given_base_action_config_with_instructions(original_list)
        
        # When: MergedInstructions instantiated and base_instructions accessed
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_base_instructions_accessed(merged_instructions)
        
        # Then: Modifying result doesn't affect original
        result.append('new')
        assert len(original_list) == 2
        assert len(result) == 3


class TestGetRenderInstructions:
    """Test Get Render Instructions story."""
    
    def test_render_instructions_property_returns_provided_instructions(self):
        """Test: render_instructions property returns provided instructions."""
        # Given: BaseActionConfig and render instructions
        base_action_config = given_base_action_config_with_instructions(['base1'])
        render_instructions = {'instructions': ['render1', 'render2']}
        
        # When: MergedInstructions instantiated with render instructions
        merged_instructions = when_merged_instructions_instantiated(base_action_config, render_instructions)
        result = when_render_instructions_accessed(merged_instructions)
        
        # Then: Render instructions are returned
        then_render_instructions_are(result, render_instructions)
    
    def test_render_instructions_property_returns_none_when_not_provided(self):
        """Test: render_instructions property returns None when not provided."""
        # Given: BaseActionConfig without render instructions
        base_action_config = given_base_action_config_with_instructions(['base1'])
        
        # When: MergedInstructions instantiated without render instructions
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_render_instructions_accessed(merged_instructions)
        
        # Then: Render instructions is None
        then_render_instructions_is_none(result)


class TestMergeBaseAndRenderInstructions:
    """Test Merge Base and Render Instructions story."""
    
    def test_merge_combines_base_and_render_instructions(self):
        """Test: merge() combines base and render instructions."""
        # Given: BaseActionConfig and render instructions
        base_action_config = given_base_action_config_with_instructions(['base1', 'base2'])
        render_instructions = {'instructions': ['render1', 'render2']}
        
        # When: MergedInstructions instantiated and merge() called
        merged_instructions = when_merged_instructions_instantiated(base_action_config, render_instructions)
        result = when_merge_called(merged_instructions)
        
        # Then: Merged dict contains both instruction sets
        then_merged_contains_base_instructions(result, ['base1', 'base2'])
        then_merged_contains_render_instructions(result, render_instructions)
    
    def test_merge_handles_missing_render_instructions(self):
        """Test: merge() handles missing render instructions."""
        # Given: BaseActionConfig without render instructions
        base_action_config = given_base_action_config_with_instructions(['base1', 'base2'])
        
        # When: MergedInstructions instantiated and merge() called
        merged_instructions = when_merged_instructions_instantiated(base_action_config)
        result = when_merge_called(merged_instructions)
        
        # Then: Merged dict contains only base instructions
        then_merged_contains_base_instructions(result, ['base1', 'base2'])
        then_merged_does_not_contain_render_instructions(result)
    
    def test_merge_handles_empty_render_instructions(self):
        """Test: merge() handles empty render instructions."""
        # Given: BaseActionConfig with empty render instructions dict
        base_action_config = given_base_action_config_with_instructions(['base1'])
        render_instructions = {}
        
        # When: MergedInstructions instantiated and merge() called
        merged_instructions = when_merged_instructions_instantiated(base_action_config, render_instructions)
        result = when_merge_called(merged_instructions)
        
        # Then: Merged dict contains base instructions and empty render instructions
        then_merged_contains_base_instructions(result, ['base1'])
        then_merged_contains_render_instructions(result, render_instructions)
