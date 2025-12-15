"""
Instructions class.

Loads and manages base instructions and behavior instructions.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Instructions:
    """Manages base instructions and behavior instructions.
    
    Domain Model:
        Instantiated with: BaseActions, Behavior
        Properties: base_instructions, behavior_instructions
    """
    
    def __init__(self, base_action_config: BaseActionConfig, behavior: Behavior):
        """Initialize Instructions.
        
        Args:
            base_action_config: BaseActionConfig instance (provides base_instructions)
            behavior: Behavior instance (provides behavior_instructions)
        """
        self._base_action_config = base_action_config
        self._behavior = behavior
    
    @property
    def base_instructions(self) -> List[str]:
        """Get base instructions from base action config.
        
        Domain Model: base_instructions property
        
        Returns:
            List of instruction strings from base_actions/{action_name}/action_config.json
        """
        instructions = self._base_action_config.instructions
        if isinstance(instructions, list):
            return instructions
        elif isinstance(instructions, str):
            return [instructions]
        return []
    
    @property
    def behavior_instructions(self) -> Dict[str, Any]:
        """Get behavior instructions from behavior config.
        
        Domain Model: behavior_instructions property
        
        Returns:
            Dict of instructions from behavior.json
        """
        return self._behavior.behavior_config.instructions
    
    def merge(self) -> Dict[str, Any]:
        """Merge base instructions and behavior instructions.
        
        Returns:
            Dict with merged instructions structure
        """
        merged = {
            'base_instructions': self.base_instructions,
            'behavior_instructions': self.behavior_instructions
        }
        
        # If behavior_instructions is a dict with 'instructions' key, merge those too
        if isinstance(self.behavior_instructions, dict):
            behavior_instr_list = self.behavior_instructions.get('instructions', [])
            if isinstance(behavior_instr_list, list):
                # Combine base and behavior instructions
                merged['instructions'] = self.base_instructions + behavior_instr_list
            else:
                merged['instructions'] = self.base_instructions
        else:
            merged['instructions'] = self.base_instructions
        
        return merged

