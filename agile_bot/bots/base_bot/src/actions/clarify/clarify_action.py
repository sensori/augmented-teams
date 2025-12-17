from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.clarify.required_context import RequiredContext
from agile_bot.bots.base_bot.src.actions.clarify.requirements_clarifications import RequirementsClarifications


class ClarifyContextAction(Action):
    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        self._required_context = RequiredContext(self.behavior.folder)
    
    @property
    def action_name(self) -> str:
        """Action name is always 'clarify' for ClarifyContextAction."""
        return 'clarify'
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only for ClarifyContextAction")
    
    @property
    def required_context(self) -> RequiredContext:
        return self._required_context
    
    @property
    def key_questions(self):
        return self.required_context.key_questions
    
    @property
    def evidence(self):
        return self.required_context.evidence
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        instructions = self.instructions.copy()
        
        instructions['guardrails'] = {
            'required_context': self.required_context.instructions
        }
        
        if parameters.get('key_questions_answered') or parameters.get('evidence_provided'):
            self.save_clarification(parameters)
        
        return {'instructions': instructions}
    
    def save_clarification(self, parameters: Dict[str, Any]):
        clarifications = RequirementsClarifications(
            behavior_name=self.behavior.name,
            bot_paths=self.behavior.bot_paths,
            required_context=self.required_context,
            key_questions_answered=parameters.get('key_questions_answered', {}),
            evidence_provided=parameters.get('evidence_provided', {})
        )
        
        clarifications.save()
