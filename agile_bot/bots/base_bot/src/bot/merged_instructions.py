"""
MergedInstructions class.

Manages merging of base instructions and render instructions.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.actions.render_output.render_spec import RenderSpec


class MergedInstructions:
    """Manages base instructions and render instructions merging.
    
    Domain Model:
        Instantiated with: BaseActions, RenderSpec
        Properties: base_instructions, render_instructions
    """
    
    def __init__(self, base_action_config: BaseActionConfig, render_instructions: Optional[Dict[str, Any]] = None):
        """Initialize MergedInstructions.
        
        Args:
            base_action_config: BaseActionConfig instance (provides base_instructions)
            render_instructions: Optional dict of render instructions from render folder
        """
        self._base_action_config = base_action_config
        self._render_instructions = render_instructions
    
    @property
    def base_instructions(self) -> List[str]:
        """Get base instructions from base action config.
        
        Domain Model: base_instructions property
        
        Returns:
            List of instruction strings from base_actions/{action_name}/action_config.json
        """
        instructions = self._base_action_config.instructions
        if isinstance(instructions, list):
            return instructions.copy()
        elif isinstance(instructions, str):
            return [instructions]
        return []
    
    @property
    def render_instructions(self) -> Optional[Dict[str, Any]]:
        """Get render instructions from render folder.
        
        Domain Model: render_instructions property
        
        Returns:
            Dict of render instructions from render folder's instructions.json, or None if not available
        """
        return self._render_instructions
    
    def merge(self) -> Dict[str, Any]:
        """Merge base instructions and render instructions.
        
        Returns:
            Dict with merged instructions structure containing base_instructions
            and render_instructions (if available)
        """
        merged = {
            'base_instructions': self.base_instructions
        }
        
        # Add render_instructions if provided (including empty dict)
        if self.render_instructions is not None:
            merged['render_instructions'] = self.render_instructions
        
        return merged
