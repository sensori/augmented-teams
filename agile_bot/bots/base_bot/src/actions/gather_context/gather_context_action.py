from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.gather_context.required_context import RequiredContext
from agile_bot.bots.base_bot.src.actions.gather_context.requirements_clarifications import RequirementsClarifications


class GatherContextAction(Action):
    """Gather context action for clarifying requirements.
    
    Domain Model:
        Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
        Properties: required_context, key_questions, evidence
    """
    
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None, 
                 bot_name: str = None, action_name: str = 'gather_context'):
        """Initialize GatherContextAction.
        
        Domain Model: Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
        """
        super().__init__(base_action_config=base_action_config, behavior=behavior, 
                        activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        
        # Instantiate RequiredContext from behavior folder
        if self.behavior:
            behavior_folder = self.behavior.folder
            self._required_context = RequiredContext(behavior_folder)
        else:
            self._required_context = None
    
    @property
    def required_context(self) -> RequiredContext:
        """Get required context.
        
        Domain Model: required_context
        """
        if self._required_context is None and self.behavior:
            behavior_folder = self.behavior.folder
            self._required_context = RequiredContext(behavior_folder)
        return self._required_context
    
    @property
    def key_questions(self):
        """Get key questions.
        
        Domain Model: key_questions
        """
        return self.required_context.key_questions
    
    @property
    def evidence(self):
        """Get evidence.
        
        Domain Model: evidence
        """
        return self.required_context.evidence
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute gather_context action logic."""
        # Get instructions from base class (already merged from BaseActionConfig and Behavior)
        instructions = self.instructions.copy()
        
        # Inject guardrails (key_questions and evidence) from RequiredContext
        # Only inject if there are actual questions or evidence requirements
        if self.required_context and self.required_context.instructions:
            questions = self.required_context.instructions.get('key_questions', [])
            evidence = self.required_context.instructions.get('evidence', [])
            if questions or evidence:
                instructions['guardrails'] = {
                    'required_context': self.required_context.instructions
                }
        
        # If clarification data is provided, save it
        if parameters and (parameters.get('key_questions_answered') or parameters.get('evidence_provided')):
            self.save_clarification(parameters)
        
        return {'instructions': instructions}
    
    def save_clarification(self, parameters: Dict[str, Any]):
        """Save clarification data to documentation folder (generated file, not original context)."""
        # Create RequirementsClarifications instance
        clarifications = RequirementsClarifications(
            behavior_name=self.behavior.name,
            bot_paths=self.behavior.bot_paths,
            required_context=self.required_context,
            key_questions_answered=parameters.get('key_questions_answered', {}),
            evidence_provided=parameters.get('evidence_provided', {})
        )
        
        # Save using RequirementsClarifications
        clarifications.save()
