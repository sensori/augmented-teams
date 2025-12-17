from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.strategy.strategy import Strategy
from agile_bot.bots.base_bot.src.actions.strategy.strategy_decision import StrategyDecision


class StrategyAction(Action):
    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        self._strategy = Strategy(self.behavior.folder)
    
    @property
    def action_name(self) -> str:
        """Action name is always 'strategy' for StrategyAction."""
        return 'strategy'
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only for StrategyAction")
    
    @property
    def strategy(self) -> Strategy:
        return self._strategy
    
    @property
    def strategy_criteria(self):
        return self.strategy.strategy_criterias.strategy_criterias
    
    @property
    def typical_assumptions(self):
        return self.strategy.assumptions.assumptions
    
    @property
    def recommended_activities(self):
        return self.strategy.recommended_activities.recommended_activities
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        instructions = self.instructions.copy()
        instructions.update(self.strategy.instructions)
        
        if parameters.get('decisions_made') or parameters.get('assumptions_made'):
            self.save_strategy(parameters)
        
        return {'instructions': instructions}
    
    def save_strategy(self, parameters: Dict[str, Any]):
        strategy_decision = StrategyDecision(
            behavior_name=self.behavior.name,
            bot_paths=self.behavior.bot_paths,
            strategy=self.strategy,
            decisions_made=parameters.get('decisions_made', {}),
            assumptions_made=parameters.get('assumptions_made', [])
        )
        strategy_decision.save()

