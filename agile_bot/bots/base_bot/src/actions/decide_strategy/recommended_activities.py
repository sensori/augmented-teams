"""
RecommendedActivities class.

Loads recommended activities from guardrails/strategy/recommended_activities.json.
"""
from pathlib import Path
from typing import List
from agile_bot.bots.base_bot.src.utils import read_json_file


class RecommendedActivities:
    """Recommended activities for strategy decisions.
    
    Domain Model:
        Property: recommended_activities
    """
    
    def __init__(self, strategy_dir: Path):
        self._strategy_dir = strategy_dir
        self._recommended_activities: List[str] = []
        self._load_recommended_activities()
    
    def _load_recommended_activities(self):
        """Load recommended activities from recommended_activities.json."""
        activities_file = self._strategy_dir / 'recommended_activities.json'
        activities_data = read_json_file(activities_file)
        self._recommended_activities = activities_data.get('recommended_activities', []) or activities_data.get('activities', [])
    
    @property
    def recommended_activities(self) -> List[str]:
        return self._recommended_activities

