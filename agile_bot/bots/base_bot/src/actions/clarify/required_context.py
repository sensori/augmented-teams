from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.clarify.key_questions import KeyQuestions
from agile_bot.bots.base_bot.src.actions.clarify.evidence import Evidence


class RequiredContext:
    
    def __init__(self, behavior_folder: Path):
        guardrails_dir = behavior_folder / 'guardrails' / 'required_context'
        self.key_questions = KeyQuestions(guardrails_dir)
        self.evidence = Evidence(guardrails_dir)
    
    @property
    def instructions(self) -> Dict[str, Any]:
        return {
            'key_questions': self.key_questions.questions,
            'evidence': self.evidence.evidence_list
        }

