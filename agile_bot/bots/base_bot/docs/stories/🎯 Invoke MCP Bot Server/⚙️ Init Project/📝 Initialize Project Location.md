# 📝 Initialize Project Location

**Epic:** Invoke MCP Bot Server  
**Feature:** Init Project  
**Increment:** 3 - Workflow

**Actor:** Bot Behavior  
**Story Type:** system

## Story Descriptio

Bot initializes and confirms project location where workflow state will be persisted. System asks user for confirmation only when location is new or changed, avoiding repeated confirmations for same location.

## Acceptance Criteria



- **(AC) WHEN** Bot behavior is invoked for the first time (no saved location exists)
- **(AC) AND** No `project_area` parameter is provided
- **(AC) THEN** Bot detects current directory from context, or as an explicit parameter
- **(AC) AND** Bot presents detected location to user
- **(AC) AND** Bot waits for user to confirm the proposed location

When User confirms location
- **(AC) then** Bot saves location

When User provides `project_area` parameter with explicit location as response to confirmation
- **(AC) THEN** Bot saves the provided location immediately to persistent storage
- **(AC) AND** Bot proceeds to next action without asking for confirmation

- **(AC) WHEN** Bot behavior is invoked
- **(AC) AND** Saved location exists
- **(AC) AND** Current directory matches saved location
- **(AC) THEN** Bot uses saved location without asking for confirmation
- **(AC) AND** Bot proceeds directly to next action

- **(AC) WHEN** Bot behavior is invoked
- **(AC) AND** Saved location exists
- **(AC) AND** Current directory is DIFFERENT from saved location
- **(AC) THEN** Bot presents new location to user for confirmation
- **(AC) AND** Bot asks if user wants to switch to new location
- **(AC) AND** Bot saves confirmed location if user approves change

## Scenarios

### Scenario: First time initialization with no saved location (detects current directory)

**Steps:**
```gherkin
Given no project location has been saved
And current directory is 'C:/dev/my-project'
When Bot behavior is invoked (no project_area parameter)
Then Bot detects current directory as 'C:/dev/my-project'
And Bot returns: requires_confirmation=True, proposed_location='C:/dev/my-project'
And Bot presents message: "Project location will be: C:/dev/my-project. Confirm?"
And Bot waits for user response

When User confirms with confirm=True (no project_area parameter)
Then Bot saves location 'C:/dev/my-project' to storage file
And Bot returns: requires_confirmation=False, saved=True
And Bot proceeds to gather_context action
```

### Scenario: First time initialization with project_area parameter hint

**Steps:**
```gherkin
Given no project location has been saved
And current directory is 'C:/dev/augmented-teams'
When Bot behavior is invoked with project_area='C:/dev/my-project'
Then Bot uses provided parameter as 'C:/dev/my-project'
And Bot returns: requires_confirmation=True, proposed_location='C:/dev/my-project'
And Bot presents message: "Project location will be: C:/dev/my-project. Confirm?"
And Bot waits for user response

When User confirms with confirm=True (no project_area parameter)
Then Bot saves location 'C:/dev/my-project' to storage file
And Bot returns: requires_confirmation=False, saved=True
And Bot proceeds to gather_context action
```

### Scenario: Subsequent invocation with same location (no confirmation bias)

**Steps:**
```gherkin
Given project location 'C:/dev/my-project' is saved
And current directory is 'C:/dev/my-project'
When Bot behavior is invoked
Then Bot loads saved location 'C:/dev/my-project'
And Bot compares with current directory 'C:/dev/my-project'
And Bot confirms locations match
And Bot does NOT ask user for confirmation
And Bot proceeds directly to gather_context action
```

### Scenario: Location changed - ask for confirmation

**Steps:**
```gherkin
Given project location 'C:/dev/old-project' is saved
And current directory is 'C:/dev/new-project'
When Bot behavior is invoked
Then Bot detects location mismatch
And Bot presents message: "Saved location: C:/dev/old-project. Current: C:/dev/new-project. Switch to new location?"
And Bot waits for user response
When User confirms with "yes"
Then Bot saves new location 'C:/dev/new-project' to storage file
And Bot proceeds to gather_context action
```

### Scenario: User provides different location as response to confirmation

**Steps:**
```gherkin
Given no project location has been saved
And current directory is 'C:/dev/augmented-teams'
When Bot behavior is invoked (no project_area parameter)
Then Bot returns: requires_confirmation=True, proposed_location='C:/dev/augmented-teams'
And Bot presents message: "Project location will be: C:/dev/augmented-teams. Confirm?"

When User responds with confirm=True AND project_area='C:/projects/my-app'
Then Bot saves location 'C:/projects/my-app' to storage file (not the proposed one)
And Bot returns: requires_confirmation=False, saved=True
And Bot proceeds to gather_context action
```

---

## Test Implementation

```python
# agile_bot/bots/base_bot/test/test_initialize_project_location.py

from pathlib import Path
import json
from mamba import description, it, before
from expects import expect, equal, be_true, contain
from agile_bot.bots.base_bot.src.bot import Bot


with description('Initialize Project Location') as self:
    with before.each:
        self.workspace = Path('test_workspace')
        self.workspace.mkdir(exist_ok=True)
        self.config_path = self.workspace / 'agile_bot/bots/test_bot/config/bot_config.json'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps({'name': 'test_bot', 'behaviors': ['shape']}))
        
        self.location_file = self.workspace / 'project_area' / 'project_location.json'
        
    with description('First time initialization with no saved location'):
        with it('detects current directory and requests confirmation'):
            bot = Bot('test_bot', self.workspace, self.config_path)
            
            result = bot.shape.initialize_project()
            
            expect(result.status).to(equal('completed'))
            expect(result.data['proposed_location']).to(equal(str(self.workspace)))
            expect(result.data['requires_confirmation']).to(be_true)
    
    with description('Subsequent invocation with same location'):
        with it('skips confirmation when location matches'):
            # Save location first
            self.location_file.parent.mkdir(parents=True, exist_ok=True)
            self.location_file.write_text(json.dumps({'project_location': str(self.workspace)}))
            
            bot = Bot('test_bot', self.workspace, self.config_path)
            result = bot.shape.initialize_project()
            
            expect(result.status).to(equal('completed'))
            expect(result.data.get('requires_confirmation')).to(equal(False))
    
    with description('Location changed'):
        with it('requests confirmation when location differs'):
            # Save old location
            self.location_file.parent.mkdir(parents=True, exist_ok=True)
            old_location = Path('C:/dev/old-project')
            self.location_file.write_text(json.dumps({'project_location': str(old_location)}))
            
            bot = Bot('test_bot', self.workspace, self.config_path)
            result = bot.shape.initialize_project()
            
            expect(result.status).to(equal('completed'))
            expect(result.data['saved_location']).to(equal(str(old_location)))
            expect(result.data['current_location']).to(equal(str(self.workspace)))
            expect(result.data['requires_confirmation']).to(be_true)
```

---

## Code Implementation

Update `agile_bot/bots/base_bot/src/bot.py` - `Behavior.initialize_project()` method:

```python
def initialize_project(self, parameters: Dict[str, Any] = None) -> BotResult:
    """Execute initialize project action - confirms project location for workflow state persistence."""
    if parameters is None:
        parameters = {}
    
    # Determine current location
    current_location = self.workspace_root
    
    # Check for saved location
    location_file = self.workspace_root / 'project_area' / 'project_location.json'
    saved_location = None
    
    if location_file.exists():
        try:
            location_data = json.loads(location_file.read_text(encoding='utf-8'))
            saved_location = Path(location_data.get('project_location', ''))
        except Exception:
            pass
    
    # Determine if confirmation needed
    requires_confirmation = False
    data = {}
    
    if not saved_location:
        # First time - need confirmation
        requires_confirmation = True
        data = {
            'proposed_location': str(current_location),
            'requires_confirmation': True,
            'message': f'Project location will be: {current_location}. Confirm?'
        }
    elif saved_location != current_location:
        # Location changed - need confirmation
        requires_confirmation = True
        data = {
            'saved_location': str(saved_location),
            'current_location': str(current_location),
            'requires_confirmation': True,
            'message': f'Saved location: {saved_location}. Current: {current_location}. Switch to new location?'
        }
    else:
        # Same location - skip confirmation
        data = {
            'project_location': str(current_location),
            'requires_confirmation': False
        }
    
    # Save location if confirmed (in real usage, this would be called after user confirms)
    if not requires_confirmation:
        location_file.parent.mkdir(parents=True, exist_ok=True)
        location_file.write_text(
            json.dumps({'project_location': str(current_location)}),
            encoding='utf-8'
        )
    
    return BotResult(
        status='completed',
        behavior=self.name,
        action='initialize_project',
        data=data
    )
```

---

## Implementation Notes

**Location Storage:**
- Stored in: `{workspace_root}/project_area/project_location.json`
- Format: `{"project_location": "C:/dev/my-project"}`

**Confirmation Flow:**
- First time: Always confirm
- Same location: Skip confirmation (no bias)
- Different location: Confirm switch

**Integration:**
- This action runs BEFORE `gather_context` in workflow
- Establishes where workflow_state.json will be saved
- Order 1 in workflow sequence

