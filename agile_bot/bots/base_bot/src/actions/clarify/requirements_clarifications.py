from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.actions.strategy.json_persistent import JsonPersistent
from agile_bot.bots.base_bot.src.actions.clarify.required_context import RequiredContext


class RequirementsClarifications(JsonPersistent):
    
    def __init__(self, behavior_name: str, bot_paths: BotPaths, 
                 required_context: RequiredContext,
                 key_questions_answered: Dict[str, Any] = None, 
                 evidence_provided: Dict[str, Any] = None):
        super().__init__(bot_paths, 'clarification.json')
        self.behavior_name = behavior_name
        self.required_context = required_context
        self.key_questions_answered = key_questions_answered or {}
        self.evidence_provided = evidence_provided or {}
    
    def save(self):
        existing_data = self.load()
        
        original_questions = self.required_context.key_questions.questions
        original_evidence_requirements = self.required_context.evidence.evidence_list
        
        new_data = {
            'key_questions': {
                'questions': original_questions,
                'answers': self.key_questions_answered
            },
            'evidence': {
                'required': original_evidence_requirements,
                'provided': self.evidence_provided
            }
        }
        
        merged_data = self.merge(existing_data, new_data, self.behavior_name)
        super().save(merged_data)
    
    @classmethod
    def load_all(cls, bot_paths: BotPaths) -> Dict[str, Any]:
        instance = cls.__new__(cls)
        instance.bot_paths = bot_paths
        instance.filename = 'clarification.json'
        return instance.load()

