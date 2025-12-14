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

# Removed duplicate create_bot_config - use conftest.create_bot_config_file instead
# Import conftest functions when needed: from conftest import create_bot_config_file

def create_activity_log_file(workspace_dir: Path) -> Path:
    """Create activity log file in workspace directory."""
    log_file = get_activity_log_path(workspace_dir)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
    return log_file

# Removed duplicate create_workflow_state - use conftest.create_workflow_state_file instead
# Import conftest functions when needed: from conftest import create_workflow_state_file

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

# Removed create_actions_workflow_json - moved to test_build_agile_bots_helpers.py (epic-level)
# Import when needed: from agile_bot.bots.base_bot.test.test_build_agile_bots_helpers import create_actions_workflow_json

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

# ============================================================================
# COMMON GIVEN/WHEN/THEN HELPERS - Used across multiple test files
# ============================================================================

def given_bot_name_and_behavior_setup(bot_name: str = 'story_bot', behavior: str = 'shape'):
    """Given: Bot name and behavior setup.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    """
    return bot_name, behavior

def given_bot_instance_created(bot_name: str, bot_directory: Path, config_path: Path):
    """Given: Bot instance created.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    """
    from agile_bot.bots.base_bot.src.bot.bot import Bot
    return Bot(bot_name=bot_name, bot_directory=bot_directory, config_path=config_path)

def then_completed_actions_include(workflow_file: Path, expected_action_states: list):
    """Then: Completed actions include expected action states.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    """
    state_data = json.loads(workflow_file.read_text(encoding='utf-8'))
    completed_states = [entry.get('action_state') for entry in state_data.get('completed_actions', [])]
    for expected_state in expected_action_states:
        assert expected_state in completed_states, f"Expected {expected_state} in completed_actions"

def then_workflow_current_state_is(workflow, expected_state: str):
    """Then: Workflow current state is expected.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    """
    assert workflow.current_state == expected_state or workflow.state == expected_state

def then_activity_logged_with_action_state(log_file_or_workspace: Path, expected_action_state: str):
    """Then: Activity logged with expected action_state.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    Accepts either log_file Path or workspace_directory Path.
    """
    from tinydb import TinyDB
    if (log_file_or_workspace / 'activity_log.json').exists():
        # It's a workspace directory
        log_file = log_file_or_workspace / 'activity_log.json'
    else:
        # It's already a log file
        log_file = log_file_or_workspace
    
    with TinyDB(log_file) as db:
        entries = db.all()
        assert any(entry.get('action_state') == expected_action_state for entry in entries)

def then_completion_entry_logged_with_outputs(log_file_or_workspace: Path, expected_outputs: dict = None, expected_duration: int = None):
    """Then: Completion entry logged with outputs and duration.
    
    Used across multiple test files. Consolidate here to avoid duplication.
    Accepts either log_file Path or workspace_directory Path.
    """
    from tinydb import TinyDB
    if (log_file_or_workspace / 'activity_log.json').exists():
        # It's a workspace directory
        log_file = log_file_or_workspace / 'activity_log.json'
    else:
        # It's already a log file
        log_file = log_file_or_workspace
    
    with TinyDB(log_file) as db:
        entries = db.all()
        completion_entry = next((e for e in entries if 'outputs' in e), None)
        assert completion_entry is not None
        if expected_outputs is not None:
            assert completion_entry['outputs'] == expected_outputs
        if expected_duration is not None:
            assert completion_entry['duration'] == expected_duration
