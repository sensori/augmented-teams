"""
RequiredContext class.

Aggregates KeyQuestions and Evidence for guardrails.
"""
from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.clarify.key_questions import KeyQuestions
from agile_bot.bots.base_bot.src.actions.clarify.evidence import Evidence


class RequiredContext:
    """Required context for clarifying requirements.
    
    Domain Model:
        Properties: KeyQuestions, Evidence, Instructions
    """
    
    def __init__(self, behavior_folder: Path):
        """Initialize RequiredContext.
        
        Args:
            behavior_folder: Path to behavior folder
        """
        self._behavior_folder = behavior_folder
        self._guardrails_dir = behavior_folder / 'guardrails' / 'required_context'
        
        # Instantiate KeyQuestions and Evidence
        self.key_questions = KeyQuestions(self._guardrails_dir)
        self.evidence = Evidence(self._guardrails_dir)
    
    @property
    def instructions(self) -> Dict[str, Any]:
        """Get instructions dict with key_questions and evidence.
        
        Domain Model: Instructions
        """
        return {
            'key_questions': self.key_questions.questions,
            'evidence': self.evidence.evidence_list
        }

