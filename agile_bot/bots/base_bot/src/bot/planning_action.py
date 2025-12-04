from pathlib import Path
from typing import Dict, Any
import json
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class PlanningAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'decide_planning_criteria')
    
    def _find_action_folder(self, action_name: str) -> Path:
        base_actions_dir = self.workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
        # Try to find folder with action name (with or without number prefix)
        for folder in base_actions_dir.glob(f'*{action_name}'):
            if folder.is_dir():
                return folder
        
        return base_actions_dir / action_name
    
    def inject_decision_criteria_and_assumptions(self) -> Dict[str, Any]:
        # Find behavior folder (handles numbered prefixes)
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
            planning_dir = behavior_folder / 'guardrails' / 'planning'
        except FileNotFoundError:
            planning_dir = None
        
        instructions = {}
        
        if not planning_dir or not planning_dir.exists():
            return {'assumptions': [], 'decision_criteria': {}}
        
        # Load assumptions
        assumptions_file = planning_dir / 'typical_assumptions.json'
        if assumptions_file.exists():
            assumptions_data = read_json_file(assumptions_file)
            instructions['assumptions'] = assumptions_data.get('assumptions', [])
        else:
            instructions['assumptions'] = []
        
        # Load decision criteria
        criteria_dir = planning_dir / 'decision_criteria'
        if criteria_dir.exists() and criteria_dir.is_dir():
            decision_criteria = {}
            for criteria_file in criteria_dir.glob('*.json'):
                criteria_data = read_json_file(criteria_file)
                decision_criteria.update(criteria_data)
            instructions['decision_criteria'] = decision_criteria
        else:
            instructions['decision_criteria'] = {}
        
        return instructions
    