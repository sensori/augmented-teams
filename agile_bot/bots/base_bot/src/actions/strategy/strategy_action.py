from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.strategy.strategy import Strategy
from agile_bot.bots.base_bot.src.actions.strategy.strategy_decision import StrategyDecision


class StrategyAction(Action):
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = 'strategy'):
        super().__init__(base_action_config=base_action_config, behavior=behavior,
                        activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        
        # Instantiate Strategy from behavior folder
        if self.behavior:
            behavior_folder = self.behavior.folder
            self._strategy = Strategy(behavior_folder)
        else:
            self._strategy = None
    
    @property
    def strategy(self) -> Strategy:
        if self._strategy is None and self.behavior:
            behavior_folder = self.behavior.folder
            self._strategy = Strategy(behavior_folder)
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
        # Get instructions from base class (already merged from BaseActionConfig and Behavior)
        instructions = self.instructions.copy()
        
        # Inject strategy (strategy_criteria, assumptions, recommended_activities) from Strategy
        # Only inject if there are actual strategy criteria, assumptions, or recommended activities
        if self.strategy and self.strategy.instructions:
            strategy_criteria = self.strategy.instructions.get('strategy_criteria', {})
            assumptions = self.strategy.instructions.get('assumptions', [])
            recommended_activities = self.strategy.instructions.get('recommended_activities', [])
            if strategy_criteria or assumptions or recommended_activities:
                instructions.update(self.strategy.instructions)
        
        # If strategy data is provided, save it
        if parameters and (parameters.get('decisions_made') or parameters.get('assumptions_made')):
            self.save_strategy(parameters)
        
        return {'instructions': instructions}
    
    def save_strategy(self, parameters: Dict[str, Any]):
        # Create StrategyDecision instance
        strategy_decision = StrategyDecision(
            behavior_name=self.behavior.name,
            bot_paths=self.behavior.bot_paths,
            strategy=self.strategy,
            decisions_made=parameters.get('decisions_made', {}),
            assumptions_made=parameters.get('assumptions_made', [])
        )
        
        # Save using StrategyDecision
        strategy_decision.save()

