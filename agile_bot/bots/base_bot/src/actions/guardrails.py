"""
Guardrails class.

Aggregates RequiredContext and Planning for guardrails.
"""
from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.gather_context.required_context import RequiredContext
from agile_bot.bots.base_bot.src.actions.decide_strategy.strategy import Strategy


class Guardrails:
    """Guardrails for a behavior.
    
    Domain Model:
        Properties: RequiredContext, Strategy, Instructions
    """
    
    def __init__(self, behavior_config):
        """Initialize Guardrails.
        
        Args:
            behavior_config: BehaviorConfig instance (has behavior_name and bot_paths)
        """
        self._behavior_config = behavior_config
        behavior_folder = behavior_config.bot_paths.bot_directory / "behaviors" / behavior_config.behavior_name
        
        # Instantiate RequiredContext and Strategy
        self.required_context = RequiredContext(behavior_folder)
        self.strategy = Strategy(behavior_folder)
    
    @property
    def instructions(self) -> Dict[str, Any]:
        """Get instructions dict with guardrails.
        
        Domain Model: Instructions
        """
        return {
            'guardrails': {
                'required_context': self.required_context.instructions,
                'strategy': self.strategy.instructions
            }
        }

