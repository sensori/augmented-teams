"""
Strategy class.

Aggregates StrategyCriterias, Assumptions, and RecommendedActivities for strategy decisions.
"""
from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.decide_strategy.strategy_criterias import StrategyCriterias
from agile_bot.bots.base_bot.src.actions.decide_strategy.assumptions import Assumptions
from agile_bot.bots.base_bot.src.actions.decide_strategy.recommended_activities import RecommendedActivities


class Strategy:
    """Strategy for decision-making.
    
    Domain Model:
        Properties: StrategyCriterias, Assumptions, RecommendedActivities, Instructions
    """
    
    def __init__(self, behavior_folder: Path):
        self._behavior_folder = behavior_folder
        self._strategy_dir = behavior_folder / 'guardrails' / 'strategy'
        
        # Instantiate StrategyCriterias, Assumptions, and RecommendedActivities
        self.strategy_criterias = StrategyCriterias(self._strategy_dir)
        self.assumptions = Assumptions(self._strategy_dir)
        self.recommended_activities = RecommendedActivities(self._strategy_dir)
    
    @property
    def instructions(self) -> Dict[str, Any]:
        # Convert StrategyCriteria objects to dicts for instructions
        strategy_criteria_dict = {}
        for key, criteria in self.strategy_criterias.strategy_criterias.items():
            strategy_criteria_dict[key] = {
                'question': criteria.question,
                'options': criteria.options,
                'outcome': criteria.outcome
            }
        
        return {
            'strategy_criteria': strategy_criteria_dict,
            'assumptions': self.assumptions.assumptions,
            'recommended_activities': self.recommended_activities.recommended_activities
        }

