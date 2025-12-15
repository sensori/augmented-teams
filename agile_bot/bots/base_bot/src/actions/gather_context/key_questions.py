"""
KeyQuestions class.

Loads key questions from guardrails/required_context/key_questions.json.
"""
from pathlib import Path
from typing import List, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class KeyQuestions:
    """Key questions for required context.
    
    Domain Model:
        Property: questions
    """
    
    def __init__(self, guardrails_dir: Path):
        """Initialize KeyQuestions.
        
        Args:
            guardrails_dir: Path to guardrails/required_context directory
        """
        self._guardrails_dir = guardrails_dir
        self._questions: List[str] = []
        self._load_questions()
    
    def _load_questions(self):
        """Load questions from key_questions.json."""
        questions_file = self._guardrails_dir / 'key_questions.json'
        questions_data = read_json_file(questions_file)
        self._questions = questions_data.get('questions', [])
    
    @property
    def questions(self) -> List[str]:
        """Get list of key questions.
        
        Domain Model: questions
        """
        return self._questions

