"""
Evidence class.

Loads evidence from guardrails/required_context/evidence.json.
"""
from pathlib import Path
from typing import List, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class Evidence:
    """Evidence for required context.
    
    Domain Model:
        Property: evidence_list
    """
    
    def __init__(self, guardrails_dir: Path):
        self._guardrails_dir = guardrails_dir
        self._evidence_list: List[Any] = []
        self._load_evidence()
    
    def _load_evidence(self):
        """Load evidence from evidence.json."""
        evidence_file = self._guardrails_dir / 'evidence.json'
        if evidence_file.exists():
            evidence_data = read_json_file(evidence_file)
            self._evidence_list = evidence_data.get('evidence', [])
    
    @property
    def evidence_list(self) -> List[Any]:
        return self._evidence_list





