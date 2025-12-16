"""
RequirementsClarifications class.

Handles saving clarification data (answers to key questions and evidence).
"""
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.actions.strategy.json_persistent import JsonPersistent
from agile_bot.bots.base_bot.src.actions.clarify.required_context import RequiredContext


class RequirementsClarifications(JsonPersistent):
    """Requirements clarifications for a behavior.
    
    Domain Model:
        Answered For RequiredContext
        Answers: RequiredContext, Key Questions
        Evidence provided: RequiredContext, Evidence
    """
    
    def __init__(self, behavior_name: str, bot_paths: BotPaths, 
                 required_context: RequiredContext,
                 key_questions_answered: Dict[str, Any] = None, 
                 evidence_provided: Dict[str, Any] = None):
        """Initialize RequirementsClarifications.
        
        Args:
            behavior_name: Name of the behavior
            bot_paths: BotPaths instance for accessing paths
            required_context: RequiredContext instance with original questions and evidence requirements
            key_questions_answered: Answers to key questions
            evidence_provided: Evidence provided
        """
        super().__init__(bot_paths, 'clarification.json')
        self.behavior_name = behavior_name
        self.required_context = required_context
        self.key_questions_answered = key_questions_answered or {}
        self.evidence_provided = evidence_provided or {}
    
    def save(self):
        """Save clarification data to documentation folder."""
        # Load existing data
        existing_data = self.load()
        
        # Get original questions and evidence requirements from RequiredContext
        original_questions = self.required_context.key_questions.questions if self.required_context else []
        original_evidence_requirements = self.required_context.evidence.evidence_list if self.required_context else []
        
        # Prepare new data for this behavior
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
        
        # Merge and save
        merged_data = self.merge(existing_data, new_data, self.behavior_name)
        super().save(merged_data)
    
    @classmethod
    def load_all(cls, bot_paths: BotPaths) -> Dict[str, Any]:
        """Load all clarification data for all behaviors.
        
        Args:
            bot_paths: BotPaths instance for accessing paths
            
        Returns:
            Dictionary with all clarification data (keyed by behavior name), or empty dict if not found
        """
        instance = cls.__new__(cls)
        instance.bot_paths = bot_paths
        instance.filename = 'clarification.json'
        return instance.load()

