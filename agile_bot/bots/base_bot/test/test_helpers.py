import json
import os
from pathlib import Path


# ============================================================================
# PATH HELPERS - Centralized path calculations
# ============================================================================

def get_bot_dir(repo_root: Path, bot_name: str) -> Path:
    """Get bot directory path (where bot code lives)."""
    return repo_root / 'agile_bot' / 'bots' / bot_name

def get_activity_log_path(workspace_dir: Path) -> Path:
    """Get activity_log.json path (in workspace directory)."""
    return workspace_dir / 'activity_log.json'

def get_workflow_state_path(workspace_dir: Path) -> Path:
    """Get workflow_state.json path (in workspace directory)."""
    return workspace_dir / 'workflow_state.json'

def get_bot_config_path(bot_dir: Path) -> Path:
    """Get bot config path (in bot directory)."""
    return bot_dir / 'config' / 'bot_config.json'

def get_behavior_dir(bot_dir: Path, behavior: str) -> Path:
    """Get behavior directory path (in bot directory)."""
    return bot_dir / 'behaviors' / behavior

def get_base_bot_dir(repo_root: Path) -> Path:
    """Get base_bot directory path."""
    return repo_root / 'agile_bot' / 'bots' / 'base_bot'

def get_base_actions_dir(repo_root: Path) -> Path:
    """Get base_actions directory path."""
    return get_base_bot_dir(repo_root) / 'base_actions'

def get_base_bot_rules_dir(repo_root: Path) -> Path:
    """Get base_bot rules directory path."""
    return get_base_bot_dir(repo_root) / 'rules'

def bootstrap_env(bot_dir: Path, workspace_dir: Path):
    """Bootstrap environment variables for tests."""
    os.environ['BOT_DIRECTORY'] = str(bot_dir)
    os.environ['WORKING_AREA'] = str(workspace_dir)

def create_agent_json(bot_dir: Path, workspace_dir: Path) -> Path:
    """Create agent.json file in bot directory."""
    agent_json = bot_dir / 'agent.json'
    agent_json.parent.mkdir(parents=True, exist_ok=True)
    agent_json.write_text(json.dumps({'WORKING_AREA': str(workspace_dir)}), encoding='utf-8')
    return agent_json

def create_bot_config(bot_dir: Path, bot_name: str, behaviors: list) -> Path:
    """Create bot configuration file."""
    config_path = get_bot_config_path(bot_dir)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_path

def create_activity_log_file(workspace_dir: Path) -> Path:
    """Create activity log file in workspace directory."""
    log_file = get_activity_log_path(workspace_dir)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
    return log_file

def create_workflow_state(workspace_dir: Path, bot_name: str, current_behavior: str = None, 
                         current_action: str = None, completed_actions: list = None) -> Path:
    """Create workflow state file in workspace directory."""
    state_file = get_workflow_state_path(workspace_dir)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    state_data = {}
    if current_behavior:
        state_data['current_behavior'] = current_behavior
    if current_action:
        state_data['current_action'] = current_action
    if completed_actions:
        state_data['completed_actions'] = completed_actions
    
    state_file.write_text(json.dumps(state_data), encoding='utf-8')
    return state_file

def create_guardrails_files(bot_dir: Path, behavior: str, questions: list, evidence: list) -> tuple:
    """Create guardrails files in behavior folder."""
    guardrails_dir = get_behavior_dir(bot_dir, behavior) / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text(json.dumps({'questions': questions}), encoding='utf-8')
    
    evidence_file = guardrails_dir / 'evidence.json'
    evidence_file.write_text(json.dumps({'evidence': evidence}), encoding='utf-8')
    
    return questions_file, evidence_file

def create_planning_guardrails(bot_dir: Path, behavior: str, assumptions: list, criteria: dict) -> tuple:
    """Create planning guardrails in behavior folder."""
    guardrails_dir = get_behavior_dir(bot_dir, behavior) / 'guardrails' / 'planning'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    assumptions_file = guardrails_dir / 'typical_assumptions.json'
    assumptions_file.write_text(json.dumps({'assumptions': assumptions}), encoding='utf-8')
    
    criteria_dir = guardrails_dir / 'decision_criteria'
    criteria_dir.mkdir(exist_ok=True)
    criteria_file = criteria_dir / 'test_criteria.json'
    criteria_file.write_text(json.dumps(criteria), encoding='utf-8')
    
    return assumptions_file, criteria_file

def create_knowledge_graph_template(bot_dir: Path, behavior: str, template_name: str) -> Path:
    """Create knowledge graph template in behavior folder."""
    kg_dir = get_behavior_dir(bot_dir, behavior) / 'content' / 'knowledge_graph'
    kg_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = kg_dir / f'{template_name}.json'
    template_file.write_text(json.dumps({'template': 'knowledge_graph'}), encoding='utf-8')
    return template_file

def create_validation_rules(bot_dir: Path, behavior: str, rules: list) -> Path:
    """Create validation rules in behavior folder."""
    rules_dir = get_behavior_dir(bot_dir, behavior) / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

def create_common_rules(repo_root: Path, rules: list) -> Path:
    """Create common rules in base_bot directory."""
    rules_dir = get_base_bot_rules_dir(repo_root)
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'common_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

def create_base_instructions(bot_directory: Path):
    """Create base action instructions in bot_directory (no fallback to repo root)."""
    base_actions = bot_directory / 'base_actions'
    for idx, action in enumerate(['gather_context', 'decide_planning_criteria', 
                                    'build_knowledge', 'validate_rules', 'render_output'], start=2):
        action_dir = base_actions / f'{idx}_{action}'
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(json.dumps({'instructions': [f'{action} base instructions']}), encoding='utf-8')

def create_base_action_instructions(bot_directory: Path, action: str) -> Path:
    """Create base action instructions for specific action in bot_directory (no fallback)."""
    base_actions_dir = bot_directory / 'base_actions'
    
    action_mapping = {
        'gather_context': '1_gather_context',
        'decide_planning_criteria': '2_decide_planning_criteria',
        'build_knowledge': '3_build_knowledge',
        'render_output': '4_render_output',
        'validate_rules': '5_validate_rules'
    }
    
    folder_name = action_mapping.get(action, action)
    action_dir = base_actions_dir / folder_name
    action_dir.mkdir(parents=True, exist_ok=True)
    
    instructions_file = action_dir / 'instructions.json'
    instructions_file.write_text(
        json.dumps({
            'actionName': action,
            'instructions': [f'{action} base instructions']
        }),
        encoding='utf-8'
    )
    return instructions_file

def create_behavior_folder(bot_dir: Path, folder_name: str) -> Path:
    """Create behavior folder in bot directory."""
    behavior_dir = get_behavior_dir(bot_dir, folder_name)
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir

def create_behavior_action_instructions(bot_dir: Path, behavior: str, action: str) -> Path:
    """Create behavior-specific action instructions."""
    instructions_dir = get_behavior_dir(bot_dir, behavior) / action
    instructions_dir.mkdir(parents=True, exist_ok=True)
    
    instructions_file = instructions_dir / 'instructions.json'
    instructions_file.write_text(json.dumps({
        'instructions': [f'{behavior}.{action} specific instructions']
    }), encoding='utf-8')
    return instructions_file

def create_trigger_words_file(bot_dir: Path, behavior: str, action: str, patterns: list) -> Path:
    """Create trigger words file for behavior action."""
    trigger_dir = get_behavior_dir(bot_dir, behavior) / action
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_file.write_text(json.dumps({'patterns': patterns}), encoding='utf-8')
    return trigger_file

def create_actions_workflow_json(bot_directory: Path, behavior_name: str, actions: list = None) -> Path:
    """Create behavior.json file for a behavior (new format).
    
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

def create_base_actions_structure(bot_directory: Path):
    """Create base actions directory structure in bot_directory (no fallback).
    
    NOTE: This is deprecated. Behaviors should use actions-workflow.json instead.
    This function is kept for backward compatibility with tests that haven't been updated yet.
    """
    base_actions_dir = bot_directory / 'base_actions'
    workflow_actions = [
        ('1_gather_context', 'gather_context'),
        ('2_decide_planning_criteria', 'decide_planning_criteria'),
        ('3_build_knowledge', 'build_knowledge'),
        ('4_render_output', 'render_output'),
        ('5_validate_rules', 'validate_rules')
    ]
    
    for folder_name, action_name in workflow_actions:
        action_dir = base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        action_config = {
            'action_name': action_name,
            'workflow_type': 'sequential'
        }
        (action_dir / 'action_config.json').write_text(json.dumps(action_config), encoding='utf-8')
    

def read_activity_log(workspace_dir: Path) -> list:
    """Read activity log from workspace directory."""
    log_file = get_activity_log_path(workspace_dir)
    if not log_file.exists():
        return []
    
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        return db.all()

def verify_action_tracks_start(bot_dir: Path, workspace_dir: Path, action_class, action_name: str, 
                               bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify that action tracks start in activity log."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    create_activity_log_file(workspace_dir)
    
    # Create action (no workspace_root parameter)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir
    )
    action.track_activity_on_start()
    
    log_data = read_activity_log(workspace_dir)
    assert any(
        e['action_state'] == f'{bot_name}.{behavior}.{action_name}'
        for e in log_data
    )

def verify_action_tracks_completion(bot_dir: Path, workspace_dir: Path, action_class, action_name: str, 
                                   bot_name: str = 'story_bot', behavior: str = 'exploration', 
                                   outputs: dict = None, duration: int = None):
    """Helper: Verify that action tracks completion in activity log."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    create_activity_log_file(workspace_dir)
    
    # Create action (no workspace_root parameter)
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir
    )
    action.track_activity_on_completion(
        outputs=outputs or {},
        duration=duration
    )
    
    log_data = read_activity_log(workspace_dir)
    completion_entry = next((e for e in log_data if 'outputs' in e or 'duration' in e), None)
    assert completion_entry is not None
    if outputs:
        assert completion_entry.get('outputs') == outputs
    if duration:
        assert completion_entry.get('duration') == duration

def verify_workflow_transition(bot_dir: Path, workspace_dir: Path, source_action: str, dest_action: str, 
                              bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow transitions from source to dest action."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    states = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output']
    # Create all transitions, not just the one we're testing
    transitions = [
        {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
        {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
        {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'validate_rules'},
        {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'render_output'},
    ]
    # No workspace_root parameter
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=states,
        transitions=transitions
    )
    # Set state and save it so load_state() doesn't reset it
    workflow.machine.set_state(source_action)
    workflow.save_state()
    # Mark action as completed
    workflow.save_completed_action(source_action)
    # Now transition
    workflow.transition_to_next()
    assert workflow.state == dest_action

def verify_workflow_saves_completed_action(bot_dir: Path, workspace_dir: Path, action_name: str, 
                                          bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow saves completed action to state file."""
    # Bootstrap environment
    bootstrap_env(bot_dir, workspace_dir)
    
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    # No workspace_root parameter
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_dir,
        states=['gather_context', 'decide_planning_criteria', 'build_knowledge', 'validate_rules', 'render_output'],
        transitions=[]
    )
    workflow.save_completed_action(action_name)
    
    # Workflow state is in workspace directory
    state_file = get_workflow_state_path(workspace_dir)
    state_data = json.loads(state_file.read_text(encoding='utf-8'))
    assert any(
        action_name in entry.get('action_state', '')
        for entry in state_data.get('completed_actions', [])
    )
