from typing import Dict, Any, List, Optional


class StrategyCriteria:
    def __init__(self, criteria_data: Dict[str, Any]):
        self.question = criteria_data.get('question', '')
        self.options = criteria_data.get('options', [])
        self.outcome = criteria_data.get('outcome', None)
    
    @property
    def question(self) -> str:
        return self._question
    
    @question.setter
    def question(self, value: str):
        self._question = value
    
    @property
    def options(self) -> List[Any]:
        return self._options
    
    @options.setter
    def options(self, value: List[Any]):
        self._options = value
    
    @property
    def outcome(self) -> Optional[Any]:
        return self._outcome
    
    @outcome.setter
    def outcome(self, value: Optional[Any]):
        self._outcome = value

