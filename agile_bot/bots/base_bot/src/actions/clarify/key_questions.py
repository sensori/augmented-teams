from pathlib import Path
from typing import List, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class KeyQuestions:
    
    def __init__(self, guardrails_dir: Path):
        self._guardrails_dir = guardrails_dir
        self._questions: List[str] = []
        self._load_questions()
    
    def _load_questions(self):
        questions_file = self._guardrails_dir / 'key_questions.json'
        if questions_file.exists():
            questions_data = read_json_file(questions_file)
            self._questions = questions_data.get('questions', [])
    
    @property
    def questions(self) -> List[str]:
        return self._questions

