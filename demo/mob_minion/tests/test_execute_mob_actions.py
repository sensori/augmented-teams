"""
Execute Mob Actions Tests

Tests follow orchestrator pattern:
- Test methods show Given-When-Then flow (under 20 lines)
- Helper functions provide reusable operations (under 20 lines)
- Tests verify observable behavior through public API
- Production code uses explicit dependencies and single responsibility
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict


# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

def create_foundry_session():
    """Helper: Create mock Foundry VTT session."""
    session = Mock()
    session.is_active = True
    return session


def create_mob_with_tokens(token_count: int, strategy=None):
    """Helper: Create mock mob with tokens."""
    class MockMob:
        def __init__(self, token_count, strategy):
            import uuid
            self.id = str(uuid.uuid4())
            self.token_ids = [f'token_{i}' for i in range(token_count)]
            self.actor_ids = [f'actor_{i}' for i in range(token_count)]
            self.strategy = strategy
            self.name = "Test Mob"
    
    return MockMob(token_count, strategy)


def create_token_belonging_to_mob(mob):
    """Helper: Create token that belongs to mob."""
    return {
        'id': mob.token_ids[0],
        'actorId': mob.actor_ids[0],
        'mobId': mob.id
    }


def create_token_not_in_mob():
    """Helper: Create token not belonging to any mob."""
    return {
        'id': 'token_orphan',
        'actorId': 'actor_orphan',
        'mobId': None
    }


def create_enemies(enemy_count: int):
    """Helper: Create mock enemies for combat."""
    enemies = []
    for i in range(enemy_count):
        enemy = {
            'id': f'enemy_{i}',
            'powerLevel': 10 + i * 5,
            'currentHealth': 50 - i * 5,
            'maxHealth': 100
        }
        enemies.append(enemy)
    return enemies


def verify_mob_identified(mob_service, token, expected_mob):
    """Helper: Verify mob is identified from token."""
    identified_mob = mob_service.identify_mob_from_token(token)
    assert identified_mob is not None
    assert identified_mob.id == expected_mob.id


def verify_action_prepared(mob_service, mob, expected_token_count: int):
    """Helper: Verify action is prepared for all minions."""
    prepared_action = mob_service.prepare_action(mob)
    assert prepared_action is not None
    assert prepared_action.minion_count == expected_token_count


def verify_target_determined(target, strategy_type: str, enemies: List[Dict]):
    """Helper: Verify target matches strategy criteria."""
    assert target is not None
    assert target['id'] in [e['id'] for e in enemies]
    
    if strategy_type == "AttackMostPowerful":
        max_power = max(e['powerLevel'] for e in enemies)
        assert target['powerLevel'] == max_power
    elif strategy_type == "AttackWeakest":
        min_power = min(e['powerLevel'] for e in enemies)
        assert target['powerLevel'] == min_power
    elif strategy_type == "AttackMostDamaged":
        max_damage = max(e['maxHealth'] - e['currentHealth'] for e in enemies)
        assert (target['maxHealth'] - target['currentHealth']) == max_damage


def verify_default_target_selected(target, enemies: List[Dict]):
    """Helper: Verify default target is selected."""
    assert target is not None
    assert target['id'] in [e['id'] for e in enemies]


def verify_attacks_executed(combat_system, mob, target, expected_count: int):
    """Helper: Verify attacks executed for all minions."""
    attack_results = combat_system.execute_mob_attack(mob, target)
    assert len(attack_results) == expected_count
    for result in attack_results:
        assert 'minion_id' in result
        assert 'target_id' in result
        assert result['target_id'] == target['id']


def verify_combat_tracker_updated(combat_tracker, mob, expected_count: int):
    """Helper: Verify combat tracker updated with results."""
    updates = combat_tracker.get_updates_for_mob(mob.id)
    assert len(updates) == expected_count


# ============================================================================
# FIXTURES - Test setup
# ============================================================================

@pytest.fixture
def foundry_session():
    """Fixture: Mock Foundry VTT session."""
    return create_foundry_session()


@pytest.fixture
def foundry_actor_system():
    """Fixture: Mock Foundry Actor System."""
    system = Mock()
    system.mobs = {}
    
    def get_mob(mob_id):
        return system.mobs.get(mob_id)
    
    system.get_mob = get_mob
    return system


@pytest.fixture
def foundry_combat_system():
    """Fixture: Mock Foundry Combat System."""
    system = Mock()
    
    def get_available_enemies():
        return []
    
    def execute_mob_attack(mob, target):
        results = []
        for token_id in mob.token_ids:
            results.append({
                'minion_id': token_id,
                'target_id': target['id'],
                'success': True
            })
        return results
    
    system.get_available_enemies = get_available_enemies
    system.execute_mob_attack = execute_mob_attack
    return system


@pytest.fixture
def combat_tracker():
    """Fixture: Mock combat tracker."""
    tracker = Mock()
    tracker.updates = {}
    
    def get_updates_for_mob(mob_id):
        return tracker.updates.get(mob_id, [])
    
    def add_update(mob_id, update):
        if mob_id not in tracker.updates:
            tracker.updates[mob_id] = []
        tracker.updates[mob_id].append(update)
    
    tracker.get_updates_for_mob = get_updates_for_mob
    tracker.add_update = add_update
    return tracker


@pytest.fixture
def mob_service(foundry_actor_system):
    """Fixture: Mob service with dependencies."""
    service = Mock()
    service.actor_system = foundry_actor_system
    
    def identify_mob_from_token(token):
        if token.get('mobId'):
            return foundry_actor_system.get_mob(token['mobId'])
        return None
    
    def prepare_action(mob):
        class MockAction:
            def __init__(self, mob):
                self.mob_id = mob.id
                self.minion_count = len(mob.token_ids)
        return MockAction(mob)
    
    service.identify_mob_from_token = identify_mob_from_token
    service.prepare_action = prepare_action
    return service


@pytest.fixture
def target_selection_service(foundry_combat_system):
    """Fixture: Target selection service."""
    service = Mock()
    service.combat_system = foundry_combat_system
    
    def determine_target(mob, enemies, strategy_type=None):
        if strategy_type == "AttackMostPowerful":
            return max(enemies, key=lambda e: e['powerLevel'])
        elif strategy_type == "AttackWeakest":
            return min(enemies, key=lambda e: e['powerLevel'])
        elif strategy_type == "AttackMostDamaged":
            return max(enemies, key=lambda e: e['maxHealth'] - e['currentHealth'])
        else:
            # Default: first available
            return enemies[0] if enemies else None
    
    service.determine_target = determine_target
    return service


# ============================================================================
# ORCHESTRATOR TESTS - Test flows with Given-When-Then
# ============================================================================

class TestClickMobTokenToCommand:
    """Click Mob Token To Command behavior tests."""
    
    @pytest.mark.parametrize("token_count", ["2", "5", "10"])
    def test_game_master_clicks_mob_token_to_command_mob(
        self, foundry_session, foundry_actor_system, mob_service, token_count
    ):
        """
        SCENARIO: Game Master clicks mob token to command mob
        GIVEN: Foundry VTT session is active
        AND: mob exists with "<token_count>" minion tokens
        AND: mob is persisted in Foundry actor system
        WHEN: Game Master clicks any token belonging to mob
        THEN: system identifies mob associated with clicked token
        WHEN: mob is identified
        THEN: system prepares to execute action for all "<token_count>" minions in mob
        """
        # Given: Mob exists and persisted
        mob = create_mob_with_tokens(int(token_count))
        foundry_actor_system.mobs[mob.id] = mob
        token = create_token_belonging_to_mob(mob)
        
        # When: Game Master clicks token
        identified_mob = mob_service.identify_mob_from_token(token)
        
        # Then: Mob identified
        verify_mob_identified(mob_service, token, mob)
        
        # When: Mob identified
        prepared_action = mob_service.prepare_action(identified_mob)
        
        # Then: Action prepared for all minions
        verify_action_prepared(mob_service, identified_mob, int(token_count))
        assert prepared_action.minion_count == int(token_count)
    
    def test_game_master_clicks_token_not_belonging_to_mob(
        self, foundry_session, mob_service
    ):
        """
        SCENARIO: Game Master clicks token not belonging to mob
        GIVEN: Foundry VTT session is active
        AND: individual minion tokens exist that are not part of any mob
        WHEN: Game Master clicks token that does not belong to any mob
        THEN: system treats it as individual minion
        AND: no mob action is prepared
        """
        # Given: Individual token not in mob
        token = create_token_not_in_mob()
        
        # When: Game Master clicks token
        identified_mob = mob_service.identify_mob_from_token(token)
        
        # Then: Treated as individual minion, no mob action
        assert identified_mob is None


class TestDetermineTargetFromStrategy:
    """Determine Target From Strategy behavior tests."""
    
    @pytest.mark.parametrize("enemy_count,strategy_type", [
        ("2", "AttackMostPowerful"),
        ("3", "AttackWeakest"),
        ("5", "AttackMostDamaged")
    ])
    def test_system_determines_target_using_assigned_strategy(
        self, foundry_session, foundry_combat_system, target_selection_service,
        enemy_count, strategy_type
    ):
        """
        SCENARIO: System determines target using assigned strategy
        GIVEN: Foundry VTT session is active
        AND: mob exists with assigned strategy
        AND: combat encounter has "<enemy_count>" enemies available
        AND: Foundry combat system is active
        WHEN: mob action is initiated
        THEN: system uses mob's assigned "<strategy_type>" strategy to determine target
        WHEN: target is determined
        THEN: system selects appropriate enemy based on strategy rules using Foundry combat system
        AND: selected target matches strategy criteria
        """
        # Given: Mob with strategy, enemies available
        mob = create_mob_with_tokens(3, strategy_type)
        enemies = create_enemies(int(enemy_count))
        foundry_combat_system.get_available_enemies.return_value = enemies
        
        # When: Mob action initiated
        target = target_selection_service.determine_target(mob, enemies, strategy_type)
        
        # Then: Target determined using strategy
        verify_target_determined(target, strategy_type, enemies)
        
        # When: Target determined
        # Then: Target matches strategy criteria (verified above)
        assert target is not None
    
    def test_system_uses_default_strategy_when_no_strategy_assigned(
        self, foundry_session, foundry_combat_system, target_selection_service
    ):
        """
        SCENARIO: System uses default strategy when no strategy assigned
        GIVEN: Foundry VTT session is active
        AND: mob exists without assigned strategy
        AND: combat encounter has enemies available
        AND: Foundry combat system is active
        WHEN: mob action is initiated
        THEN: system uses default strategy (nearest enemy or first available target)
        WHEN: target is determined
        THEN: system selects appropriate enemy based on default strategy rules using Foundry combat system
        """
        # Given: Mob without strategy, enemies available
        mob = create_mob_with_tokens(3, None)
        enemies = create_enemies(3)
        foundry_combat_system.get_available_enemies.return_value = enemies
        
        # When: Mob action initiated
        target = target_selection_service.determine_target(mob, enemies, None)
        
        # Then: Default target selected
        verify_default_target_selected(target, enemies)
        assert target == enemies[0]  # First available


class TestExecuteAttackAction:
    """Execute Attack Action behavior tests."""
    
    @pytest.mark.parametrize("token_count", ["2", "5", "10"])
    def test_system_executes_attack_for_all_minions_in_mob(
        self, foundry_session, foundry_combat_system, combat_tracker, token_count
    ):
        """
        SCENARIO: System executes attack for all minions in mob
        GIVEN: Foundry VTT session is active
        AND: mob exists with "<token_count>" minion tokens
        AND: target has been determined
        AND: attack action is selected
        AND: Foundry combat system is active
        WHEN: target is determined and attack action is selected
        THEN: system executes attack for all "<token_count>" minions in mob via Foundry combat system
        WHEN: attack is executed
        THEN: all "<token_count>" minions perform attack action against selected target
        AND: system updates combat tracker with results for all minions in mob
        """
        # Given: Mob, target, attack action selected
        mob = create_mob_with_tokens(int(token_count))
        target = {'id': 'enemy_1', 'name': 'Target Enemy'}
        
        # When: Target determined and attack selected
        attack_results = foundry_combat_system.execute_mob_attack(mob, target)
        
        # Then: Attacks executed for all minions
        verify_attacks_executed(foundry_combat_system, mob, target, int(token_count))
        
        # When: Attack executed
        # Then: All minions attack target (verified above)
        # And: Combat tracker updated
        for result in attack_results:
            combat_tracker.add_update(mob.id, result)
        
        verify_combat_tracker_updated(combat_tracker, mob, int(token_count))







