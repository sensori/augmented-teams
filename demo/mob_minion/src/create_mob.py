"""
Create Mob Module

Implements the Create Mob sub-epic functionality for grouping minion tokens into mobs.
This module handles token selection, mob creation, and confirmation.
"""
import uuid
from typing import List, Dict, Optional


class TokenSelector:
    """Handles selection of multiple minion tokens.
    
    Story: Select Multiple Tokens
    """
    
    def __init__(self, foundry_token_api):
        """Initialize TokenSelector with Foundry Token API dependency.
        
        Args:
            foundry_token_api: Foundry VTT Token API dependency
        """
        self.foundry_token_api = foundry_token_api
    
    def select_multiple_tokens(self) -> List[Dict]:
        """Select multiple minion tokens from Foundry canvas.
        
        Scenario: Game Master selects multiple tokens successfully
        
        Returns:
            List[Dict]: Array of selected token objects with id and actorId
            
        Raises:
            ValueError: If zero tokens are selected
        """
        selected_tokens = self.foundry_token_api.get_selected_tokens()
        
        if len(selected_tokens) == 0:
            raise ValueError("At least one token must be selected")
        
        return [
            {
                'id': token['id'],
                'actorId': token['actorId'],
                'name': token.get('name', '')
            }
            for token in selected_tokens
        ]


class MobCreator:
    """Handles creation of mob entities from selected tokens.
    
    Story: Group Tokens Into Mob
    """
    
    def __init__(self, foundry_token_api, foundry_actor_system):
        """Initialize MobCreator with dependencies.
        
        Args:
            foundry_token_api: Foundry VTT Token API dependency
            foundry_actor_system: Foundry VTT Actor System dependency
        """
        self.foundry_token_api = foundry_token_api
        self.foundry_actor_system = foundry_actor_system
    
    def group_tokens_into_mob(self, selected_tokens: List[Dict]) -> 'Mob':
        """Create a new mob entity containing selected tokens.
        
        Scenario: Game Master groups tokens into mob successfully
        
        Args:
            selected_tokens: List of token objects to group
            
        Returns:
            Mob: Mob entity with id, token_ids, and actor_ids
        """
        mob_id = str(uuid.uuid4())
        
        token_ids = [token['id'] for token in selected_tokens]
        actor_ids = [token['actorId'] for token in selected_tokens]
        
        # Link all tokens to mob entity via Foundry Token API
        self._link_tokens_to_mob(token_ids, mob_id)
        
        return Mob(mob_id, token_ids, actor_ids)
    
    def _link_tokens_to_mob(self, token_ids: List[str], mob_id: str):
        """Link tokens to mob entity via Foundry Token API.
        
        Args:
            token_ids: List of token IDs
            mob_id: Mob entity ID
        """
        for token_id in token_ids:
            token = self.foundry_token_api.get_token_by_id(token_id)
            if token:
                token.set_flag('mob-minion', 'mobId', mob_id)


class Mob:
    """Mob entity representing a collection of minions."""
    
    def __init__(self, mob_id: str, token_ids: List[str], actor_ids: List[str]):
        """Initialize Mob entity.
        
        Args:
            mob_id: Unique mob identifier
            token_ids: List of token IDs belonging to mob
            actor_ids: List of actor IDs belonging to mob
        """
        self.id = mob_id
        self.token_ids = token_ids
        self.actor_ids = actor_ids
        self.strategy = None
        self.name = None


class MobCreationConfirmation:
    """Handles confirmation dialog and persistence.
    
    Story: Display Mob Creation Confirmation
    """
    
    def __init__(self, foundry_actor_system, dialog_manager):
        """Initialize MobCreationConfirmation with dependencies.
        
        Args:
            foundry_actor_system: Foundry VTT Actor System dependency
            dialog_manager: Dialog management dependency
        """
        self.foundry_actor_system = foundry_actor_system
        self.dialog_manager = dialog_manager
    
    def display_confirmation(self, mob: Mob) -> bool:
        """Display confirmation dialog showing mob name and token count.
        
        Scenario: Game Master confirms mob creation
        
        Args:
            mob: Mob entity to confirm
            
        Returns:
            bool: True if confirmed, False if cancelled
        """
        mob_name = mob.name or f"Mob {mob.id}"
        token_count = len(mob.token_ids)
        
        return self.dialog_manager.show_dialog({
            'title': 'Confirm Mob Creation',
            'content': f'Create mob "{mob_name}" with {token_count} tokens?',
            'buttons': {
                'confirm': {
                    'label': 'Confirm',
                    'callback': lambda: True
                },
                'cancel': {
                    'label': 'Cancel',
                    'callback': lambda: False
                }
            }
        })
    
    def persist_mob(self, mob: Mob):
        """Persist mob in Foundry actor system.
        
        Args:
            mob: Mob entity to persist
        """
        self.foundry_actor_system.save_mob(mob)
    
    def discard_mob(self, mob: Mob):
        """Discard mob entity (cancel creation).
        
        Args:
            mob: Mob entity to discard
        """
        self.foundry_actor_system.delete_mob(mob.id)
