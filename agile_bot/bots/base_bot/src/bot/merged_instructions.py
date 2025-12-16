from pathlib import Path
from typing import Dict, Any, List, Optional

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.actions.render.render_spec import RenderSpec


class MergedInstructions:
    def __init__(self, base_action_config: BaseActionConfig, render_instructions: Optional[Dict[str, Any]] = None):
        self._base_action_config = base_action_config
        self._render_instructions = render_instructions
    
    @property
    def base_instructions(self) -> List[str]:
        instructions = self._base_action_config.instructions
        if isinstance(instructions, list):
            return instructions.copy()
        elif isinstance(instructions, str):
            return [instructions]
        return []
    
    @property
    def render_instructions(self) -> Optional[Dict[str, Any]]:
        return self._render_instructions
    
    def merge(self) -> Dict[str, Any]:
        merged = {
            'base_instructions': self.base_instructions
        }
        
        if self.render_instructions is not None:
            merged['render_instructions'] = self.render_instructions
        
        return merged
