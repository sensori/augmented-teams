"""
Epic-Level Helpers for "Build Agile Bots"

This module contains helper functions used across MULTIPLE sub-epics within the 
"Build Agile Bots" epic. Functions here are shared by:
- Generate MCP Tools
- Invoke Bot (Base Bot)
- Build Knowledge
- Execute Behavior
- Validate Rules
- Close Current Action
- Workflow Action Sequence

For functions used by only ONE sub-epic, place them in that sub-epic's test file.
For functions used across ALL epics, place them in conftest.py.
"""
import json
from pathlib import Path


def create_actions_workflow_json(bot_directory: Path, behavior_name: str, actions: list = None) -> Path:
    """Given step: Behavior exists with actions workflow.
    
    Creates behavior.json file for a behavior (new format).
    
    Used by:
    - test_generate_bot_server_and_tools.py (Generate MCP Tools sub-epic)
    - test_invoke_bot_tool.py (Invoke Bot sub-epic)
    - test_bot_execute_behavior.py (Execute Behavior sub-epic)
    - test_invoke_bot_cli.py (Invoke Bot CLI sub-epic)
    - test_base_action.py (Base Action sub-epic)
    - test_validate_knowledge_and_content_against_rules.py (Validate Rules sub-epic)
    - test_bot_behavior_exceptions.py (Execute Behavior sub-epic)
    - test_close_current_action.py (Close Current Action sub-epic)
    
    Args:
        bot_directory: Bot directory
        behavior_name: Behavior name (e.g., 'shape', '1_shape')
        actions: Optional list of action configs. If None, uses standard workflow.
    
    Returns:
        Path to created behavior.json file
    """
    behavior_dir = bot_directory / 'behaviors' / behavior_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    
    if actions is None:
        # Standard workflow order - new format with instructions array per action
        actions = [
            {
                "name": "gather_context",
                "order": 1,
                "next_action": "decide_planning_criteria",
                "instructions": [
                    f"Follow agile_bot/bots/base_bot/base_actions/1_gather_context/instructions.json",
                    f"Test instructions for gather_context in {behavior_name}"
                ]
            },
            {
                "name": "decide_planning_criteria",
                "order": 2,
                "next_action": "build_knowledge",
                "instructions": [
                    f"Follow agile_bot/bots/base_bot/base_actions/2_decide_planning_criteria/instructions.json",
                    f"Test instructions for decide_planning_criteria in {behavior_name}"
                ]
            },
            {
                "name": "build_knowledge",
                "order": 3,
                "next_action": "validate_rules",
                "instructions": [
                    f"Follow agile_bot/bots/base_bot/base_actions/3_build_knowledge/instructions.json",
                    f"Test instructions for build_knowledge in {behavior_name}"
                ]
            },
            {
                "name": "validate_rules",
                "order": 4,
                "next_action": "render_output",
                "instructions": [
                    f"Follow agile_bot/bots/base_bot/base_actions/4_validate_rules/instructions.json",
                    f"Test instructions for validate_rules in {behavior_name}"
                ]
            },
            {
                "name": "render_output",
                "order": 5,
                "instructions": [
                    f"Follow agile_bot/bots/base_bot/base_actions/5_render_output/instructions.json",
                    f"Test instructions for render_output in {behavior_name}"
                ]
            }
        ]
    
    # Create behavior.json with all sections
    behavior_config = {
        "behaviorName": behavior_name.split('_')[-1] if '_' in behavior_name and behavior_name[0].isdigit() else behavior_name,
        "description": f"Test behavior: {behavior_name}",
        "goal": f"Test goal for {behavior_name}",
        "inputs": "Test inputs",
        "outputs": "Test outputs",
        "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
        "instructions": [
            f"**BEHAVIOR WORKFLOW INSTRUCTIONS:**",
            "",
            f"Test instructions for {behavior_name}."
        ],
        "actions_workflow": {
            "actions": actions
        },
        "trigger_words": {
            "description": f"Trigger words for {behavior_name}",
            "patterns": [f"test.*{behavior_name}"],
            "priority": 10
        }
    }
    behavior_file = behavior_dir / 'behavior.json'
    behavior_file.write_text(json.dumps(behavior_config, indent=2), encoding='utf-8')
    return behavior_file

