from pathlib import Path
from typing import Dict, Any
import json
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction
from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import find_nested_subfolder


class PlanningAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory, 'decide_planning_criteria')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decide_planning_criteria action logic."""
        instructions = self.inject_decision_criteria_and_assumptions()
        
        # If planning data is provided, save it
        if parameters and (parameters.get('decisions_made') or parameters.get('assumptions_made')):
            self.save_planning(parameters)
        
        return {'instructions': instructions}
    
    def _find_action_folder(self, action_name: str) -> Path:
        base_actions_dir = self.base_actions_dir
        
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
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            # Use centralized utility to find guardrails/planning folder
            planning_dir = find_nested_subfolder(behavior_folder, 'guardrails', 'planning')
        except FileNotFoundError:
            planning_dir = None
        
        instructions = {}
        
        if not planning_dir:
            return {'assumptions': [], 'decision_criteria': {}}
        
        # Load assumptions
        assumptions_file = planning_dir / 'typical_assumptions.json'
        if assumptions_file.exists():
            assumptions_data = read_json_file(assumptions_file)
            instructions['assumptions'] = assumptions_data.get('assumptions') or assumptions_data.get('typical_assumptions', [])
        else:
            instructions['assumptions'] = []
        
        # Load decision criteria
        criteria_dir = planning_dir / 'decision_criteria'
        if criteria_dir.exists() and criteria_dir.is_dir():
            decision_criteria = {}
            for criteria_file in criteria_dir.glob('*.json'):
                criteria_data = read_json_file(criteria_file)
                # Use filename (without .json) as the key to avoid overwriting
                criteria_key = criteria_file.stem
                decision_criteria[criteria_key] = criteria_data
            instructions['decision_criteria'] = decision_criteria
        else:
            instructions['decision_criteria'] = {}
        
        return instructions
    
    def save_planning(self, parameters: Dict[str, Any]):
        """Save planning data to docs/stories folder (generated file, not original context)."""
        try:
            # Use working_dir if set, otherwise skip
            if not self.working_dir:
                return
            
            # Generated files go to docs/stories/, not context folder
            docs_folder = self.working_dir / 'docs'
            stories_folder = docs_folder / 'stories'
            
            # Ensure docs/stories folder exists
            stories_folder.mkdir(parents=True, exist_ok=True)
            
            # Load existing planning data if file exists
            planning_file = stories_folder / 'planning.json'
            planning_data = {}
            if planning_file.exists():
                try:
                    planning_data = json.loads(planning_file.read_text(encoding='utf-8'))
                except (json.JSONDecodeError, IOError):
                    planning_data = {}
            
            # Build planning data structure for current behavior
            if self.behavior not in planning_data:
                planning_data[self.behavior] = {'decisions_made': {}, 'assumptions_made': []}
            
            # Update decisions_made if provided
            if parameters.get('decisions_made'):
                planning_data[self.behavior]['decisions_made'].update(parameters.get('decisions_made', {}))
            
            # Update assumptions_made if provided (replace, not merge, as it's a list)
            if parameters.get('assumptions_made'):
                planning_data[self.behavior]['assumptions_made'] = parameters.get('assumptions_made', [])
            
            # Save to docs/stories/ (generated file location)
            planning_file.write_text(
                json.dumps(planning_data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            # Log error and fail fast so callers can handle the problem.
            # Previously this swallowed the error; now we raise a clear exception.
            import logging
            logging.exception("Failed to save planning")
            # Raise a RuntimeError with context, preserving original exception
            raise RuntimeError(f"Failed to save planning for behavior '{self.behavior}': {e}") from e
     