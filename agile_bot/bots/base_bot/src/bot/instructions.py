from pathlib import Path
from typing import Dict, Any, List, Optional

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Instructions:
    def __init__(self, base_action_config: BaseActionConfig, behavior: Behavior):
        self._base_action_config = base_action_config
        self._behavior = behavior
    
    @property
    def base_instructions(self) -> List[str]:
        instructions = self._base_action_config.instructions
        if isinstance(instructions, list):
            return instructions
        elif isinstance(instructions, str):
            return [instructions]
        return []
    
    @property
    def behavior_instructions(self) -> Dict[str, Any]:
        return self._behavior.behavior_config.instructions
    
    def merge(self) -> Dict[str, Any]:
        merged = {
            'base_instructions': self.base_instructions,
            'behavior_instructions': self.behavior_instructions
        }
        
        if isinstance(self.behavior_instructions, dict):
            behavior_instr_list = self.behavior_instructions.get('instructions', [])
            merged['instructions'] = self.base_instructions + behavior_instr_list
        else:
            merged['instructions'] = self.base_instructions
        
        return merged

