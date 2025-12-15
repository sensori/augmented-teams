"""
Generate CLI Tests

Tests for all stories in the 'Generate CLI' sub-epic:
- Generate BOT CLI code
- Generate Cursor Command Files
- Generate Cursor Awareness Files
"""
import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch
from conftest import bootstrap_env, create_bot_config_file, given_bot_name_and_behaviors_setup, given_bot_name_and_behavior_setup
from agile_bot.bots.base_bot.test.test_helpers import create_base_actions_structure
from agile_bot.bots.base_bot.test.test_build_agile_bots import (
    given_bot_config_and_directory_setup,
    given_bot_configured_by_config,
    given_behavior_with_trigger_words
)

# ============================================================================
# HELPER FUNCTIONS - Sub-Epic Level (Used across multiple test classes)
# ============================================================================

# Consolidated helpers imported from test_generate_mcp_tools.py
from agile_bot.bots.base_bot.test.test_generate_mcp_tools import (
    given_bot_config_has_goal_and_description,
    given_behaviors_with_descriptions_and_trigger_words,
    when_generate_awareness_files_and_read_content,
    when_create_rules_directory_if_needed,
    when_generator_generates_awareness_files_direct,
    given_path_write_text_mocked_to_raise_permission_error,
    given_expected_awareness_filename,
    then_awareness_file_contains_bot_name,
    then_awareness_file_contains_behavior_sections,
    then_awareness_file_shape_section_contains_only_shape_words,
    then_awareness_file_contains_tool_patterns_for_behaviors,
    then_awareness_file_contains_priority_check_message,
    then_awareness_file_contains_behavior_format_sections,
    then_awareness_file_contains_error_handling_section,
    then_awareness_file_contains_repair_question,
    then_awareness_file_contains_tool_patterns,
    then_trigger_words_in_behavior_section,
    then_permission_error_raised_with_bot_specific_path,
    then_rules_directory_and_file_exist,
    then_awareness_file_contains_required_sections,
)

# Use shared helpers from conftest
# given_bot_name_and_behaviors_setup imported from conftest
# given_bot_name_and_behavior_setup imported from conftest


class TestGenerateBOTCLIcode:
    """Story: Generate BOT CLI code - Tests CLI code generation."""
    
    # TODO: Add test scenarios for Generate BOT CLI code story
    pass


class TestGenerateCursorCommandFiles:
    """Story: Generate Cursor Command Files - Tests Cursor command file generation."""
    
    # TODO: Add test scenarios for Generate Cursor Command Files story
    pass


class TestGenerateCursorAwarenessFiles:
    """Story: Generate Cursor Awareness Files - Tests awareness file generation."""

    def test_generator_creates_workspace_rules_file_with_trigger_patterns(self, workspace_root):
        """
        SCENARIO: Generator creates workspace rules file with trigger patterns
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behaviors have trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: Generator runs generate_awareness_files() method
        THEN: Generator creates file with bot-specific filename: mcp-test-bot-awareness.mdc
        AND: Filename includes bot name with hyphens
        AND: Generated rules file includes ACTUAL trigger words from bot
        AND: File includes bot name from config
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config, bot_dir = given_bot_config_and_directory_setup(workspace_root, bot_name, behaviors)
        # And: Behaviors have trigger words configured
        given_behavior_with_trigger_words(bot_dir, '1_shape', ['shape story', 'define story outline', 'create story map'])
        given_behavior_with_trigger_words(bot_dir, '4_discovery', ['discover stories', 'break down stories', 'enumerate stories'])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator runs generate_awareness_files() method
        gen, rules_file, content = when_generate_awareness_files_and_read_content(bot_dir, bot_name)
        
        # Then: File includes bot name
        then_awareness_file_contains_bot_name(content, bot_name)
        
        # And: Trigger words are SECTIONED by behavior (not flat list)
        then_awareness_file_contains_behavior_sections(content, ['Shape', 'Discovery'])
        
        # And: Shape section includes ONLY shape trigger words
        then_awareness_file_shape_section_contains_only_shape_words(content)
        
        # And: Each behavior section shows tool pattern
        then_awareness_file_contains_tool_patterns_for_behaviors(content, bot_name, ['1_shape', '4_discovery'])

    def test_rules_file_includes_bot_goal_and_behavior_descriptions(self, workspace_root):
        """
        SCENARIO: Rules file includes bot goal and behavior descriptions
        GIVEN: Bot config has goal and description
        WHEN: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
        THEN: File includes bot's goal from bot_config.json
        AND: Critical rule mentions bot's goal: "When user is trying to [goal], check MCP tools FIRST"
        AND: Each behavior section includes "When user is trying to [behavior description]"
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config, bot_dir = given_bot_config_and_directory_setup(workspace_root, bot_name, behaviors)
        # And: Bot config has goal and description
        from agile_bot.bots.base_bot.test.test_generate_mcp_tools import given_bot_config_has_goal_and_description
        given_bot_config_has_goal_and_description(
            workspace_root,
            bot_name,
            'Transform user needs into well-structured stories',
            'Helps teams create and refine user stories'
        )
        # And: Behaviors have descriptions and trigger words configured
        given_behaviors_with_descriptions_and_trigger_words(bot_dir, [
            {
                'name': '1_shape',
                'description': 'Create initial story map outline from user context',
                'patterns': ['shape story', 'create story map']
            },
            {
                'name': '4_discovery',
                'description': 'Elaborate stories with user flows and domain rules',
                'patterns': ['discover stories', 'elaborate stories']
            }
        ])
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        
        # When: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
        gen, rules_file, content = when_generate_awareness_files_and_read_content(bot_dir, bot_name)
        
        # Then: File contains priority check message
        then_awareness_file_contains_priority_check_message(content, bot_name)
        
        # And: Each behavior follows explicit format
        then_awareness_file_contains_behavior_format_sections(content, bot_name)
        
        # And: File includes error handling section
        then_awareness_file_contains_error_handling_section(content)
        then_awareness_file_contains_repair_question(content)

    def test_rules_file_maps_trigger_patterns_to_tool_naming_conventions(self, workspace_root):
        """
        SCENARIO: Rules file maps trigger patterns to tool naming conventions
        GIVEN: A bot configuration file with a working directory and behaviors
        AND: Behaviors have trigger words configured
        AND: A bot that has been initialized with that config file
        WHEN: File is written to .cursor/rules/mcp-test-bot-awareness.mdc
        THEN: Each behavior section includes tool pattern with ACTUAL bot name
        AND: Tool patterns appear in behavior sections (not flat list)
        """
        # Given: A bot configuration file with a working directory and behaviors
        bot_name, behaviors = given_bot_name_and_behaviors_setup('test_bot', ['1_shape', '4_discovery'])
        bot_config, bot_dir = given_bot_config_and_directory_setup(workspace_root, bot_name, behaviors)
        # And: Behaviors have trigger words configured
        given_behavior_with_trigger_words(bot_dir, '1_shape', ['shape story', 'define outline'])
        given_behavior_with_trigger_words(bot_dir, '4_discovery', ['discover stories', 'enumerate stories'])
        
        # And: A bot that has been initialized with that config file
        bot_dir, workspace_directory = given_bot_configured_by_config(workspace_root, bot_name)
        # When: File is written to .cursor/rules/mcp-test-bot-awareness.mdc
        gen, rules_file, content = when_generate_awareness_files_and_read_content(bot_dir, bot_name)
        
        # Then: Each behavior section includes tool pattern with ACTUAL bot name
        then_awareness_file_contains_behavior_sections(content, behaviors)
        # And: Tool patterns appear in behavior sections (not flat list)
        then_awareness_file_contains_tool_patterns(content, bot_name, behaviors)
        # And: Trigger words are in correct sections
        then_trigger_words_in_behavior_section(content, '1_shape', ['shape story', 'define outline'])
        then_trigger_words_in_behavior_section(content, '4_discovery', ['discover stories', 'enumerate stories'])

    def test_generator_handles_file_write_errors_gracefully_creates_directory(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors gracefully creates directory
        GIVEN: MCP Server Generator attempts to create awareness files
        WHEN: .cursor/rules/ directory does not exist
        THEN: Generator creates directory before writing file
        AND: File write succeeds with bot-specific filename
        """
        # When: Generate awareness files
        when_generator_generates_awareness_files_direct(generator)
        
        # Then: Directory exists (created if needed)
        rules_dir, rules_file = then_rules_directory_and_file_exist()

    def test_generator_handles_file_write_errors_with_clear_error_message(self, generator, workspace_root):
        """
        SCENARIO: Generator handles file write errors with clear error message
        GIVEN: .cursor/rules/ directory is write-protected
        WHEN: Generator attempts to write file
        THEN: Generator raises clear error message indicating permission issue
        AND: Error includes bot-specific path attempted
        """
        # Given: Rules directory exists
        rules_dir = when_create_rules_directory_if_needed()
        # And: Path.write_text is mocked to raise PermissionError
        expected_filename = given_expected_awareness_filename()
        with given_path_write_text_mocked_to_raise_permission_error(expected_filename):
            # When: Generator attempts to write file
            # Then: Generator raises error with clear message
            then_permission_error_raised_with_bot_specific_path(generator.generate_awareness_files, expected_filename)

    def test_full_awareness_generation_workflow(self, generator, workspace_root):
        """
        SCENARIO: Full awareness generation workflow
        GIVEN: MCP Server Generator initialized
        WHEN: generate_awareness_files() called
        THEN: Bot-specific rules file is created
        AND: Rules file has all required sections
        """
        # When: Generate awareness files
        when_generator_generates_awareness_files_direct(generator)
        
        # Then: Rules file created with bot-specific filename
        rules_dir, rules_file = then_rules_directory_and_file_exist()
        # And: Rules file has all required sections
        then_awareness_file_contains_required_sections(rules_file, 'test_bot')





