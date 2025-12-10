"""
Create Mob Tests

Tests for all stories in the 'Create Mob' sub-epic:
- Select Minion Tokens
- Query Foundry VTT For Selected Tokens
- Group Minions Into Mob
- Mob Manager Creates Mob With Selected Tokens
- Assign Mob Name
- System Persists Mob Configuration

Tests follow orchestrator pattern:
- Test methods show Given-When-Then flow (under 20 lines)
- Helper functions provide reusable operations (under 20 lines)
- Tests verify observable behavior through public API
- Production code uses explicit dependencies and single responsibility
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Optional

from src.mob_minion.domain.minion import Minion
from src.mob_minion.domain.mob import Mob
from src.mob_minion.services.token_selector import TokenSelector
from src.mob_minion.integration.foundry_vtt_client import FoundryVTTClient, FoundryVTTConnectionError, FoundryVTTInvalidDataError
from src.mob_minion.services.mob_manager import MobManager
from src.mob_minion.services.mob_name_validator import MobNameValidator, EmptyMobNameError, DuplicateMobNameError
from src.mob_minion.persistence.mob_repository import MobRepository, MobRepositoryError

# ============================================================================
# HELPER FUNCTIONS - Reusable test operations
# ============================================================================

def create_foundry_vtt_mock(available: bool = True, token_data: Optional[List[Dict]] = None):
    """Helper: Create mock Foundry VTT API."""
    mock_vtt = Mock()
    mock_vtt.is_running = available
    mock_vtt.is_available = available
    
    if token_data is None:
        token_data = [
            {"actor_id": "actor_1", "name": "Goblin 1", "position": {"x": 100, "y": 200}},
            {"actor_id": "actor_2", "name": "Goblin 2", "position": {"x": 150, "y": 250}}
        ]
    
    mock_vtt.get_token_data = Mock(return_value=token_data)
    return mock_vtt

def create_minion_tokens(count: int = 2) -> List[str]:
    """Helper: Create list of minion token IDs."""
    return [f"token_{i}" for i in range(1, count + 1)]

def create_actor_data(tokens: List[str]) -> List[Dict]:
    """Helper: Create actor data for tokens."""
    return [
        {"actor_id": f"actor_{i}", "name": f"Minion {i}", "position": {"x": i * 100, "y": i * 200}}
        for i in range(1, len(tokens) + 1)
    ]

# ============================================================================
# FIXTURES - Test setup
# ============================================================================

@pytest.fixture
def foundry_vtt_running():
    """Fixture: Foundry VTT is running with tokens available."""
    return create_foundry_vtt_mock(available=True)

@pytest.fixture
def foundry_vtt_unavailable():
    """Fixture: Foundry VTT is unavailable."""
    return create_foundry_vtt_mock(available=False)

@pytest.fixture
def minion_tokens():
    """Fixture: Minion tokens available on scene."""
    return create_minion_tokens(count=2)

@pytest.fixture
def persistent_storage(tmp_path):
    """Fixture: Persistent storage directory."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    return storage_dir

# ============================================================================
# ORCHESTRATOR TESTS - Test flows with Given-When-Then
# ============================================================================

# ============================================================================
# STORY: Select Minion Tokens
# ============================================================================

class TestSelectMinionTokens:
    """Story: Select Minion Tokens - Tests token selection behavior."""
    
    def test_game_master_selects_minion_tokens(self, foundry_vtt_running, minion_tokens):
        """
        SCENARIO: Game Master selects minion tokens
        GIVEN: Foundry VTT is running
        AND: Game Master has minion tokens available on the scene
        WHEN: Game Master selects one or more minion tokens in Foundry VTT
        THEN: System highlights selected tokens
        AND: Selected tokens are stored in temporary selection state
        """
        # Given: Foundry VTT is running and tokens are available
        token_selector = TokenSelector()
        
        # When: Game Master selects tokens
        selected_tokens = minion_tokens[:2]
        token_selector.select_tokens(selected_tokens)
        
        # Then: Tokens are highlighted and stored
        assert token_selector.is_highlighted is True
        assert len(token_selector.selected_tokens) == 2
        assert token_selector.selected_tokens == selected_tokens
    
    def test_game_master_selects_zero_tokens(self, foundry_vtt_running):
        """
        SCENARIO: Game Master selects zero tokens
        GIVEN: Foundry VTT is running
        AND: Game Master has minion tokens available on the scene
        WHEN: Game Master selects zero tokens
        THEN: System shows error message indicating at least one token must be selected
        """
        # Given: Foundry VTT is running
        token_selector = TokenSelector()
        
        # When: Game Master selects zero tokens
        with pytest.raises(ValueError, match="At least one token must be selected"):
            token_selector.select_tokens([])

# ============================================================================
# STORY: Query Foundry VTT For Selected Tokens
# ============================================================================

class TestQueryFoundryVTTForSelectedTokens:
    """Story: Query Foundry VTT For Selected Tokens - Tests API query behavior."""
    
    def test_system_queries_foundry_vtt_api_successfully(self, foundry_vtt_running):
        """
        SCENARIO: System queries Foundry VTT API successfully
        GIVEN: Tokens are selected
        AND: Foundry VTT API is available
        WHEN: System queries Foundry VTT API for token actor data
        THEN: System retrieves actor ID, name, and position for each selected token
        """
        # Given: Tokens are selected and API is available
        selected_tokens = create_minion_tokens(count=2)
        mock_vtt = foundry_vtt_running
        client = FoundryVTTClient(mock_vtt)
        
        # When: System queries API
        actor_data = client.get_token_data(selected_tokens)
        
        # Then: System retrieves actor data
        assert len(actor_data) == 2
        assert "actor_id" in actor_data[0]
        assert "name" in actor_data[0]
        assert "position" in actor_data[0]
    
    def test_foundry_vtt_api_returns_invalid_token_data(self, foundry_vtt_running):
        """
        SCENARIO: Foundry VTT API returns invalid token data
        GIVEN: Tokens are selected
        AND: Foundry VTT API is available
        WHEN: Foundry VTT API returns invalid token data
        THEN: System shows error message
        AND: System excludes invalid tokens from selection
        """
        # Given: Tokens are selected and API is available
        selected_tokens = create_minion_tokens(count=2)
        mock_vtt = foundry_vtt_running
        invalid_data = [{"invalid": "data"}]
        mock_vtt.get_token_data = Mock(return_value=invalid_data)
        client = FoundryVTTClient(mock_vtt)
        
        # When: API returns invalid data
        # Then: System shows error
        with pytest.raises(FoundryVTTInvalidDataError, match="Invalid token data received"):
            client.get_token_data(selected_tokens)
    
    def test_foundry_vtt_api_is_unavailable(self, foundry_vtt_unavailable):
        """
        SCENARIO: Foundry VTT API is unavailable
        GIVEN: Tokens are selected
        AND: Foundry VTT API is unavailable
        WHEN: System attempts to query Foundry VTT API
        THEN: System shows error message indicating connection failure
        """
        # Given: Tokens are selected but API is unavailable
        selected_tokens = create_minion_tokens(count=2)
        mock_vtt = foundry_vtt_unavailable
        client = FoundryVTTClient(mock_vtt)
        
        # When: System attempts to query API
        # Then: System shows connection failure error
        with pytest.raises(FoundryVTTConnectionError, match="Connection failure: Foundry VTT API is unavailable"):
            client.get_token_data(selected_tokens)

# ============================================================================
# STORY: Group Minions Into Mob
# ============================================================================

class TestGroupMinionsIntoMob:
    """Story: Group Minions Into Mob - Tests mob grouping behavior."""
    
    def test_game_master_confirms_grouping(self, minion_tokens):
        """
        SCENARIO: Game Master confirms grouping
        GIVEN: Tokens are selected
        AND: System has retrieved actor data for selected tokens
        WHEN: Game Master confirms grouping of selected tokens
        THEN: System creates temporary mob group with selected tokens
        AND: Mob group displays list of included minion names
        """
        # Given: Tokens are selected and actor data retrieved
        selected_tokens = minion_tokens
        actor_data = create_actor_data(selected_tokens)
        mob_manager = MobManager()
        
        # When: Game Master confirms grouping
        mob_group = mob_manager.create_temporary_mob_group(selected_tokens, actor_data)
        
        # Then: Temporary mob group is created with names
        assert len(mob_group["tokens"]) == len(selected_tokens)
        assert len(mob_group["minion_names"]) == len(actor_data)
        assert mob_group["minion_names"] == [actor["name"] for actor in actor_data]
    
    def test_game_master_cancels_grouping(self, minion_tokens):
        """
        SCENARIO: Game Master cancels grouping
        GIVEN: Tokens are selected
        AND: System has retrieved actor data for selected tokens
        WHEN: Game Master cancels grouping
        THEN: System clears selection
        AND: System returns to token selection state
        """
        # Given: Tokens are selected and actor data retrieved
        token_selector = TokenSelector()
        token_selector.select_tokens(minion_tokens)
        
        # When: Game Master cancels grouping
        token_selector.clear_selection()
        
        # Then: Selection is cleared and returns to selection state
        assert not token_selector.has_selection
        assert not token_selector.is_highlighted

# ============================================================================
# STORY: Mob Manager Creates Mob With Selected Tokens
# ============================================================================

class TestMobManagerCreatesMobWithSelectedTokens:
    """Story: Mob Manager Creates Mob With Selected Tokens - Tests mob creation behavior."""
    
    def test_mob_manager_creates_mob_with_valid_tokens(self):
        """
        SCENARIO: Mob Manager creates mob with valid tokens
        GIVEN: Temporary mob group is confirmed
        AND: Mob group contains one or more valid minion tokens
        WHEN: Mob Manager creates new Mob domain object
        THEN: Mob object contains collection of Minion objects from selected tokens
        AND: Each Minion object references its Foundry VTT actor ID
        """
        # Given: Temporary mob group is confirmed with valid tokens
        tokens = create_minion_tokens(count=2)
        actor_data = create_actor_data(tokens)
        mob_manager = MobManager()
        
        # When: Mob Manager creates Mob domain object
        mob = mob_manager.create_mob_from_tokens(tokens, actor_data)
        
        # Then: Mob contains Minion objects with actor IDs
        assert len(mob.minions) == 2
        assert all(isinstance(minion, Minion) for minion in mob.minions)
        assert mob.minions[0].actor_id == "actor_1"
    
    def test_mob_group_contains_less_than_one_minion(self):
        """
        SCENARIO: Mob group contains less than one minion
        GIVEN: Temporary mob group is confirmed
        AND: Mob group contains less than one minion
        WHEN: System attempts to create Mob domain object
        THEN: System shows error message indicating mob must contain at least one minion
        """
        # Given: Mob group with less than one minion
        tokens = []
        actor_data = []
        mob_manager = MobManager()
        
        # When: System attempts to create Mob
        # Then: System shows error message
        with pytest.raises(ValueError, match="Mob must contain at least one minion"):
            mob_manager.create_mob_from_tokens(tokens, actor_data)
    
    def test_duplicate_tokens_are_detected(self):
        """
        SCENARIO: Duplicate tokens are detected
        GIVEN: Temporary mob group is confirmed
        AND: Mob group contains duplicate tokens
        WHEN: Mob Manager creates new Mob domain object
        THEN: System removes duplicates
        AND: System shows notification
        """
        # Given: Mob group with duplicate tokens
        tokens = ["token_1", "token_1", "token_2"]
        actor_data = create_actor_data(["token_1", "token_2"])
        mob_manager = MobManager()
        
        # When: Mob Manager creates Mob
        mob = mob_manager.create_mob_from_tokens(tokens, actor_data)
        
        # Then: Duplicates are removed (mob should have unique minions)
        assert len(mob.minions) == 2
        actor_ids = [minion.actor_id for minion in mob.minions]
        assert len(actor_ids) == len(set(actor_ids))

# ============================================================================
# STORY: Assign Mob Name
# ============================================================================

class TestAssignMobName:
    """Story: Assign Mob Name - Tests mob naming behavior."""
    
    def test_game_master_enters_valid_and_unique_mob_name(self):
        """
        SCENARIO: Game Master enters valid and unique mob name
        GIVEN: Mob domain object is created
        AND: Mob object contains collection of Minion objects
        WHEN: Game Master enters mob name
        THEN: System validates name is not empty
        AND: System checks name uniqueness against existing mobs
        AND: System assigns name to Mob object
        """
        # Given: Mob domain object is created
        minions = [Minion(actor_id="actor_1", name="Minion 1")]
        mob = Mob(name="", minions=minions)
        validator = MobNameValidator(existing_mob_names=[])
        
        # When: Game Master enters mob name
        mob_name = "Goblin Squad"
        validator.validate_and_assign_name(mob, mob_name)
        
        # Then: Name is validated, checked, and assigned
        assert mob.name == "Goblin Squad"
    
    def test_game_master_enters_empty_mob_name(self):
        """
        SCENARIO: Game Master enters empty mob name
        GIVEN: Mob domain object is created
        AND: Mob object contains collection of Minion objects
        WHEN: Game Master enters empty mob name
        THEN: System shows error message requiring non-empty name
        """
        # Given: Mob domain object is created
        minions = [Minion(actor_id="actor_1", name="Minion 1")]
        mob = Mob(name="", minions=minions)
        validator = MobNameValidator(existing_mob_names=[])
        
        # When: Game Master enters empty name
        # Then: System shows error message
        with pytest.raises(EmptyMobNameError, match="Mob name must not be empty"):
            validator.validate_and_assign_name(mob, "")
    
    def test_game_master_enters_duplicate_mob_name(self):
        """
        SCENARIO: Game Master enters duplicate mob name
        GIVEN: Mob domain object is created
        AND: Mob object contains collection of Minion objects
        AND: Existing mob with same name already exists
        WHEN: Game Master enters mob name that already exists
        THEN: System shows error message indicating name must be unique
        """
        # Given: Mob domain object and existing mob with same name
        minions = [Minion(actor_id="actor_1", name="Minion 1")]
        mob = Mob(name="", minions=minions)
        validator = MobNameValidator(existing_mob_names=["Goblin Squad"])
        
        # When: Game Master enters duplicate name
        # Then: System shows uniqueness error
        with pytest.raises(DuplicateMobNameError, match="Mob name must be unique"):
            validator.validate_and_assign_name(mob, "Goblin Squad")

# ============================================================================
# STORY: System Persists Mob Configuration
# ============================================================================

class TestSystemPersistsMobConfiguration:
    """Story: System Persists Mob Configuration - Tests persistence behavior."""
    
    def test_system_persists_mob_configuration_successfully(self, persistent_storage):
        """
        SCENARIO: System persists mob configuration successfully
        GIVEN: Mob object is created with valid name and minions
        AND: Persistent storage is available
        WHEN: System saves Mob configuration to persistent storage
        THEN: Persisted configuration includes mob name
        AND: Persisted configuration includes minion actor IDs
        AND: Persisted configuration includes creation timestamp
        AND: System shows success message to Game Master
        AND: Mob becomes available for selection in future operations
        """
        # Given: Mob object with valid name and minions, storage available
        minions = [Minion(actor_id="actor_1", name="Minion 1")]
        mob = Mob(name="Goblin Squad", minions=minions)
        repository = MobRepository(persistent_storage)
        
        # When: System saves configuration
        success_message = repository.save(mob)
        
        # Then: Configuration includes all required fields and success shown
        assert success_message == "Mob configuration saved successfully"
        config_data = repository.load("Goblin Squad")
        assert config_data is not None
        assert config_data["name"] == "Goblin Squad"
        assert len(config_data["minion_actor_ids"]) == 1
        assert "created_at" in config_data
    
    def test_persistence_operation_fails(self, tmp_path, monkeypatch):
        """
        SCENARIO: Persistence operation fails
        GIVEN: Mob object is created with valid name and minions
        AND: Persistent storage is unavailable or fails
        WHEN: System attempts to save Mob configuration to persistent storage
        THEN: System shows error message
        AND: System retains mob in memory for retry
        """
        # Given: Mob object but storage unavailable (simulate failure)
        minions = [Minion(actor_id="actor_1", name="Minion 1")]
        mob = Mob(name="Goblin Squad", minions=minions)
        storage = tmp_path / "storage"
        repository = MobRepository(storage)
        
        # When: System attempts to save but storage fails (simulate write failure)
        def mock_write_text_fails(*args, **kwargs):
            raise IOError("Permission denied")
        
        monkeypatch.setattr(Path, "write_text", mock_write_text_fails)
        
        # Then: Error shown and mob retained in memory
        with pytest.raises(MobRepositoryError):
            repository.save(mob)
        
        # Mob is still in memory (not deleted)
        assert mob is not None
        assert mob.name == "Goblin Squad"

