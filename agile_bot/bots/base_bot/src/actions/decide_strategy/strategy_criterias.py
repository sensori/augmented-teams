"""
StrategyCriterias class.

Loads strategy criteria from guardrails/strategy/strategy_criteria/*.json files.
"""
from pathlib import Path
from typing import Dict
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.decide_strategy.strategy_criteria import StrategyCriteria


class StrategyCriterias:
    """Strategy criteria collection for strategy decisions.
    
    Domain Model:
        Property: strategy_criterias
    """
    
    def __init__(self, strategy_dir: Path):
        """Initialize StrategyCriterias.
        
        Args:
            strategy_dir: Path to guardrails/strategy directory
        """
        self._strategy_dir = strategy_dir
        self._strategy_criterias: Dict[str, StrategyCriteria] = {}
        self._load_strategy_criterias()
    
    def _load_strategy_criterias(self):
        """Load strategy criteria from strategy_criteria/*.json files."""
        criteria_dir = self._strategy_dir / 'strategy_criteria'
        
        # If criteria directory doesn't exist, that's okay - no criteria files to load
        if criteria_dir.exists() and criteria_dir.is_dir():
            for criteria_file in criteria_dir.glob('*.json'):
                criteria_data = read_json_file(criteria_file)
                criteria_key = criteria_file.stem
                self._strategy_criterias[criteria_key] = StrategyCriteria(criteria_data)
    
    @property
    def strategy_criterias(self) -> Dict[str, StrategyCriteria]:
        """Get strategy criteria dict.
        
        Domain Model: strategy_criterias
        """
        return self._strategy_criterias

