"""
Tests for ValidateRulesAction exception handling - no fallbacks.

ValidateRulesAction should raise exceptions when:
- Story graph file doesn't exist
- Story graph file exists but fails to load (syntax error)
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
from agile_bot.bots.base_bot.test.test_helpers import bootstrap_env, create_base_actions_structure


def test_validate_rules_raises_exception_when_story_graph_not_found(tmp_path):
    """ValidateRulesAction should raise FileNotFoundError when story graph doesn't exist."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # Create base_actions structure
    create_base_actions_structure(bot_directory)
    
    # Set up workspace
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    
    # Create docs/stories directory but NO story-graph.json
    docs_dir = workspace_dir / 'docs' / 'stories'
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create action
    action = ValidateRulesAction(
        bot_name=bot_name,
        behavior='shape',
        bot_directory=bot_directory
    )
    
    # When executing without story graph
    with pytest.raises(FileNotFoundError, match="Story graph file.*not found"):
        action.do_execute(parameters={})


def test_validate_rules_raises_exception_when_story_graph_invalid_json(tmp_path):
    """ValidateRulesAction should raise exception when story graph has syntax error."""
    bot_name = 'test_bot'
    bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
    bot_directory.mkdir(parents=True, exist_ok=True)
    
    # Create base_actions structure
    create_base_actions_structure(bot_directory)
    
    # Set up workspace
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_env(bot_directory, workspace_dir)
    
    # Create docs/stories directory with INVALID JSON
    docs_dir = workspace_dir / 'docs' / 'stories'
    docs_dir.mkdir(parents=True, exist_ok=True)
    story_graph_file = docs_dir / 'story-graph.json'
    story_graph_file.write_text('{ invalid json }', encoding='utf-8')
    
    # Create action
    action = ValidateRulesAction(
        bot_name=bot_name,
        behavior='shape',
        bot_directory=bot_directory
    )
    
    # When executing with invalid JSON
    with pytest.raises((json.JSONDecodeError, ValueError), match=".*"):
        action.do_execute(parameters={})












