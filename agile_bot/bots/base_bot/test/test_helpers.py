import json
from pathlib import Path

def create_bot_config(workspace: Path, bot_name: str, behaviors: list) -> Path:
    config_path = workspace / 'agile_bot/bots' / bot_name / 'config/bot_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_path

def create_activity_log_file(workspace: Path, bot_name: str = 'story_bot') -> Path:
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    log_dir = bot_dir / 'project_area'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'activity_log.json'
    log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
    return log_file

def create_workflow_state(workspace: Path, bot_name: str, current_behavior: str = None, current_action: str = None, completed_actions: list = None) -> Path:
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    state_file = bot_dir / 'project_area' / 'workflow_state.json'
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

def create_saved_location(workspace: Path, bot_name: str, location: str):
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    location_file = bot_dir / 'project_area' / 'project_location.json'
    location_file.parent.mkdir(parents=True, exist_ok=True)
    location_file.write_text(json.dumps({'project_location': location}), encoding='utf-8')
    return location_file

def create_guardrails_files(workspace: Path, bot_name: str, behavior: str, questions: list, evidence: list) -> tuple:
    guardrails_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / behavior / 'guardrails/required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text(json.dumps({'questions': questions}), encoding='utf-8')
    
    evidence_file = guardrails_dir / 'evidence.json'
    evidence_file.write_text(json.dumps({'evidence': evidence}), encoding='utf-8')
    
    return questions_file, evidence_file

def create_planning_guardrails(workspace: Path, bot_name: str, behavior: str, assumptions: list, criteria: dict) -> tuple:
    guardrails_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / behavior / 'guardrails/planning'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    assumptions_file = guardrails_dir / 'typical_assumptions.json'
    assumptions_file.write_text(json.dumps({'assumptions': assumptions}), encoding='utf-8')
    
    criteria_dir = guardrails_dir / 'decision_criteria'
    criteria_dir.mkdir(exist_ok=True)
    criteria_file = criteria_dir / 'test_criteria.json'
    criteria_file.write_text(json.dumps(criteria), encoding='utf-8')
    
    return assumptions_file, criteria_file

def create_knowledge_graph_template(workspace: Path, bot_name: str, behavior: str, template_name: str) -> Path:
    kg_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / behavior / 'content/knowledge_graph'
    kg_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = kg_dir / f'{template_name}.json'
    template_file.write_text(json.dumps({'template': 'knowledge_graph'}), encoding='utf-8')
    return template_file

def create_validation_rules(workspace: Path, bot_name: str, behavior: str, rules: list) -> Path:
    rules_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / behavior / '3_rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

def create_common_rules(workspace: Path, rules: list) -> Path:
    rules_dir = workspace / 'agile_bot/bots/base_bot/rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'common_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}), encoding='utf-8')
    return rules_file

def create_base_instructions(workspace: Path):
    base_actions = workspace / 'agile_bot/bots/base_bot/base_actions'
    for idx, action in enumerate(['initialize_project', 'gather_context', 'decide_planning_criteria', 
                                    'build_knowledge', 'render_output', 'validate_rules'], start=1):
        action_dir = base_actions / f'{idx}_{action}'
        action_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = action_dir / 'instructions.json'
        instructions_file.write_text(json.dumps({'instructions': [f'{action} base instructions']}), encoding='utf-8')

def create_base_action_instructions(workspace: Path, action: str) -> Path:
    base_actions_dir = workspace / 'agile_bot/bots/base_bot/base_actions'
    
    action_mapping = {
        'gather_context': '2_gather_context',
        'decide_planning_criteria': '3_decide_planning_criteria',
        'build_knowledge': '4_build_knowledge',
        'render_output': '5_render_output',
        'validate_rules': '7_validate_rules'
    }
    
    folder_name = action_mapping.get(action, action)
    action_dir = base_actions_dir / folder_name
    action_dir.mkdir(parents=True, exist_ok=True)
    
    instructions_file = action_dir / 'instructions.json'
    instructions_file.write_text(json.dumps({'instructions': [f'{action} base instructions']}), encoding='utf-8')
    return instructions_file

def create_behavior_folder(workspace: Path, bot_name: str, folder_name: str) -> Path:
    behavior_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / folder_name
    behavior_dir.mkdir(parents=True, exist_ok=True)
    return behavior_dir

def create_behavior_action_instructions(workspace: Path, bot_name: str, behavior: str, action: str) -> Path:
    instructions_dir = workspace / 'agile_bot/bots' / bot_name / 'behaviors' / behavior / action
    instructions_dir.mkdir(parents=True, exist_ok=True)
    
    instructions_file = instructions_dir / 'instructions.json'
    instructions_file.write_text(json.dumps({
        'instructions': [f'{behavior}.{action} specific instructions']
    }), encoding='utf-8')
    return instructions_file

def create_trigger_words_file(workspace: Path, bot_name: str, behavior: str, action: str, patterns: list) -> Path:
    trigger_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / action
    trigger_dir.mkdir(parents=True, exist_ok=True)
    trigger_file = trigger_dir / 'trigger_words.json'
    trigger_file.write_text(json.dumps({'patterns': patterns}), encoding='utf-8')
    return trigger_file

def create_base_actions_structure(workspace: Path):
    base_actions_dir = workspace / 'agile_bot/bots/base_bot/base_actions'
    workflow_actions = [
        ('1_initialize_project', 'initialize_project'),
        ('2_gather_context', 'gather_context'),
        ('3_decide_planning_criteria', 'decide_planning_criteria'),
        ('4_build_knowledge', 'build_knowledge'),
        ('5_render_output', 'render_output'),
        ('7_validate_rules', 'validate_rules')
    ]
    
    for folder_name, action_name in workflow_actions:
        action_dir = base_actions_dir / folder_name
        action_dir.mkdir(parents=True, exist_ok=True)
        
        action_config = {
            'action_name': action_name,
            'workflow_type': 'sequential'
        }
        (action_dir / 'action_config.json').write_text(json.dumps(action_config), encoding='utf-8')
    
    correct_bot_dir = base_actions_dir / 'correct_bot'
    correct_bot_dir.mkdir(parents=True, exist_ok=True)
    (correct_bot_dir / 'action_config.json').write_text(json.dumps({
        'action_name': 'correct_bot',
        'workflow_type': 'independent'
    }), encoding='utf-8')

def read_activity_log(workspace: Path, bot_name: str = 'story_bot') -> list:
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    log_file = bot_dir / 'project_area' / 'activity_log.json'
    if not log_file.exists():
        return []
    
    from tinydb import TinyDB
    with TinyDB(log_file) as db:
        return db.all()

def verify_action_tracks_start(workspace: Path, action_class, action_name: str, bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify that action tracks start in activity log."""
    create_activity_log_file(workspace, bot_name)
    
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=workspace
    )
    action.track_activity_on_start()
    
    log_data = read_activity_log(workspace, bot_name)
    assert any(
        e['action_state'] == f'{bot_name}.{behavior}.{action_name}'
        for e in log_data
    )

def verify_action_tracks_completion(workspace: Path, action_class, action_name: str, bot_name: str = 'story_bot', behavior: str = 'exploration', outputs: dict = None, duration: int = None):
    """Helper: Verify that action tracks completion in activity log."""
    create_activity_log_file(workspace, bot_name)
    
    action = action_class(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=workspace
    )
    action.track_activity_on_completion(
        outputs=outputs or {},
        duration=duration
    )
    
    log_data = read_activity_log(workspace, bot_name)
    completion_entry = next((e for e in log_data if 'outputs' in e or 'duration' in e), None)
    assert completion_entry is not None
    if outputs:
        assert completion_entry.get('outputs') == outputs
    if duration:
        assert completion_entry.get('duration') == duration

def verify_workflow_transition(workspace: Path, source_action: str, dest_action: str, bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow transitions from source to dest action."""
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    states = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 'render_output', 'validate_rules']
    transitions = [
        {'trigger': 'proceed', 'source': source_action, 'dest': dest_action}
    ]
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=workspace,
        states=states,
        transitions=transitions
    )
    workflow.machine.set_state(source_action)
    workflow.transition_to_next()
    assert workflow.state == dest_action

def verify_workflow_saves_completed_action(workspace: Path, action_name: str, bot_name: str = 'story_bot', behavior: str = 'exploration'):
    """Helper: Verify workflow saves completed action to state file."""
    from agile_bot.bots.base_bot.src.state.workflow import Workflow
    workflow = Workflow(
        bot_name=bot_name,
        behavior=behavior,
        workspace_root=workspace,
        states=['gather_context', 'decide_planning_criteria', 'build_knowledge', 'render_output', 'validate_rules'],
        transitions=[]
    )
    workflow.save_completed_action(action_name)
    
    bot_dir = workspace / 'agile_bot' / 'bots' / bot_name
    state_file = bot_dir / 'project_area' / 'workflow_state.json'
    state_data = json.loads(state_file.read_text(encoding='utf-8'))
    assert any(
        action_name in entry.get('action_state', '')
        for entry in state_data.get('completed_actions', [])
    )
