from pathlib import Path
from typing import Dict, Any, List, Optional

from agile_bot.bots.base_bot.src.actions.render.render_spec import RenderSpec


class MergedInstructions:
    def __init__(self, base_instructions: List[str], render_instructions: Optional[Dict[str, Any]] = None):
        if isinstance(base_instructions, list):
            self._base_instructions = base_instructions.copy()
        elif isinstance(base_instructions, str):
            self._base_instructions = [base_instructions]
        else:
            self._base_instructions = []
        self._render_instructions = render_instructions
    
    @property
    def base_instructions(self) -> List[str]:
        return self._base_instructions
    
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
