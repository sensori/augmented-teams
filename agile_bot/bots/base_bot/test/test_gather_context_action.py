"""
Test that gather_context action properly injects guardrails (key_questions and evidence).
"""
import pytest
import json
from pathlib import Path
from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction


def test_gather_context_injects_guardrails_from_behavior_folder(tmp_path):
    """
    BUG: gather_context returns instructions with placeholders {{key_questions}} and {{evidence}}
    instead of actual questions and evidence from guardrails folder.
    
    Given:
      - behavior folder: 1_shape (with number prefix)
      - guardrails/required_context/key_questions.json exists
      - guardrails/required_context/evidence.json exists
    
    When: gather_context action executes
    
    Then:
      - instructions should contain actual questions (not {{key_questions}} placeholder)
      - instructions should contain actual evidence (not {{evidence}} placeholder)
    """
    # Setup
    bot_name = 'story_bot'
    behavior_name = 'shape'
    
    # Create bot structure with NUMBERED behavior folder
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    behaviors_dir = bot_dir / 'behaviors'
    behavior_folder = behaviors_dir / '1_shape'  # Note: number prefix!
    guardrails_dir = behavior_folder / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    # Create key_questions.json
    key_questions = {
        'questions': [
            'What is the scope of this work?',
            'Who are the users?',
            'What is the desired outcome?'
        ]
    }
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text(json.dumps(key_questions))
    
    # Create evidence.json
    evidence = {
        'evidence': [
            'Story map document',
            'User research notes',
            'Product requirements'
        ]
    }
    evidence_file = guardrails_dir / 'evidence.json'
    evidence_file.write_text(json.dumps(evidence))
    
    # Create base_actions/gather_context/instructions.json
    base_actions_dir = tmp_path / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    gather_context_dir = base_actions_dir / '2_gather_context'
    gather_context_dir.mkdir(parents=True, exist_ok=True)
    
    base_instructions = {
        'instructions': [
            'Review context',
            'Required Key Questions: {{key_questions}}',
            'Required Evidence: {{evidence}}'
        ]
    }
    instructions_file = gather_context_dir / 'instructions.json'
    instructions_file.write_text(json.dumps(base_instructions))
    
    # Execute
    action = GatherContextAction(
        bot_name=bot_name,
        behavior=behavior_name,
        workspace_root=tmp_path
    )
    
    result = action.do_execute(parameters={})
    
    # Assert
    instructions = result.get('instructions', {})
    
    # Should have guardrails with actual data (not placeholders)
    assert 'guardrails' in instructions, (
        f"Expected 'guardrails' in instructions, but got keys: {instructions.keys()}"
    )
    
    guardrails = instructions['guardrails']
    
    # Check key_questions loaded
    assert 'key_questions' in guardrails, (
        f"Expected 'key_questions' in guardrails, but got keys: {guardrails.keys()}"
    )
    assert guardrails['key_questions'] == key_questions['questions'], (
        f"Expected actual questions, but got: {guardrails['key_questions']}"
    )
    
    # Check evidence loaded
    assert 'evidence' in guardrails, (
        f"Expected 'evidence' in guardrails, but got keys: {guardrails.keys()}"
    )
    assert guardrails['evidence'] == evidence['evidence'], (
        f"Expected actual evidence, but got: {guardrails['evidence']}"
    )


def test_gather_context_handles_missing_guardrails_gracefully(tmp_path):
    """
    When guardrails don't exist, gather_context should not fail.
    """
    bot_name = 'story_bot'
    behavior_name = 'shape'
    
    # Create minimal structure (no guardrails)
    base_actions_dir = tmp_path / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    gather_context_dir = base_actions_dir / '2_gather_context'
    gather_context_dir.mkdir(parents=True, exist_ok=True)
    
    base_instructions = {
        'instructions': ['Review context']
    }
    instructions_file = gather_context_dir / 'instructions.json'
    instructions_file.write_text(json.dumps(base_instructions))
    
    # Create behavior folder but no guardrails
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    behaviors_dir = bot_dir / 'behaviors'
    behavior_folder = behaviors_dir / '1_shape'
    behavior_folder.mkdir(parents=True, exist_ok=True)
    
    # Execute
    action = GatherContextAction(
        bot_name=bot_name,
        behavior=behavior_name,
        workspace_root=tmp_path
    )
    
    result = action.do_execute(parameters={})
    
    # Should succeed without guardrails
    assert 'instructions' in result













