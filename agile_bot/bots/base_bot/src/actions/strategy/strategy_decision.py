from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.actions.strategy.json_persistent import JsonPersistent
from agile_bot.bots.base_bot.src.actions.strategy.strategy import Strategy


class StrategyDecision(JsonPersistent):
    def __init__(self, behavior_name: str, bot_paths: BotPaths,
                 strategy: Strategy,
                 decisions_made: Dict[str, Any] = None,
                 assumptions_made: list = None):
        super().__init__(bot_paths, 'strategy.json')
        self.behavior_name = behavior_name
        self.strategy = strategy
        self.decisions_made = decisions_made or {}
        self.assumptions_made = assumptions_made or []
    
    def save(self):
        existing_data = self.load()
        
        original_strategy_criteria = {}
        for key, criteria in self.strategy.strategy_criterias.strategy_criterias.items():
            original_strategy_criteria[key] = {
                'question': criteria.question,
                'options': criteria.options
            }
        
        original_assumptions = self.strategy.assumptions.assumptions
        original_recommended_activities = self.strategy.recommended_activities.recommended_activities
        
        new_data = {
            'strategy_criteria': {
                'criteria': original_strategy_criteria,
                'decisions_made': self.decisions_made
            },
            'assumptions': {
                'typical_assumptions': original_assumptions,
                'assumptions_made': self.assumptions_made
            },
            'recommended_activities': original_recommended_activities
        }
        
        merged_data = self.merge(existing_data, new_data, self.behavior_name)
        super().save(merged_data)
    
    @classmethod
    def load_all(cls, bot_paths: BotPaths) -> Dict[str, Any]:
        instance = cls.__new__(cls)
        instance.bot_paths = bot_paths
        instance.filename = 'strategy.json'
        return instance.load()

