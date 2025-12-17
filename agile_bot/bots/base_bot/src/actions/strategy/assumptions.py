from pathlib import Path
from typing import List
from agile_bot.bots.base_bot.src.utils import read_json_file


class Assumptions:
    def __init__(self, strategy_dir: Path):
        self._strategy_dir = strategy_dir
        self._assumptions: List[str] = []
        self._load_assumptions()
    
    def _load_assumptions(self):
        assumptions_file = self._strategy_dir / 'typical_assumptions.json'
        assumptions_data = read_json_file(assumptions_file)
        self._assumptions = assumptions_data.get('assumptions', []) or assumptions_data.get('typical_assumptions', [])
    
    @property
    def assumptions(self) -> List[str]:
        return self._assumptions

