# MCP Tool Decomposition Pattern

## Overview

MCP tools are decomposed into three levels of granularity: **Bot Tool**, **Behavior Tool**, and **Behavior-Action Tool**. This hierarchical decomposition provides multiple entry points for AI Chat to invoke bot functionality, from high-level routing to specific action execution.

## Pattern Structure

```
Bot Tool (Routes to current behavior and action)
    ↓
Behavior Tool (Routes to current action within behavior)
    ↓  
Behavior-Action Tool (Executes specific action)
    ↓
Action Method (Executes business logic)
```

## Tool Hierarchy

### Level 1: Bot Tool
**Pattern:** `{bot_name}_tool`  
**Example:** `story_bot_tool`

**Responsibility:**
- Routes to current behavior based on workflow state
- Routes to current action within that behavior
- Provides highest-level entry point

**Code:**
```python
@mcp_server.tool(name='story_bot_tool')
async def bot_tool(parameters: dict = None):
    result = bot.forward_to_current_behavior_and_current_action()
    return serialize(result)
```

**Forwarding Chain:**
1. Read workflow_state.json → Extract `current_behavior` and `current_action`
2. Forward to `bot.{behavior}.forward_to_current_action()`
3. Return result

**Use Case:** AI Chat says "continue story work" without knowing current behavior/action

---

### Level 2: Behavior Tool
**Pattern:** `{bot_name}_{behavior}_tool`  
**Example:** `story_bot_shape_tool`, `story_bot_discovery_tool`

**Responsibility:**
- Routes to current action within specific behavior
- Explicitly sets behavior context
- Allows jumping to specific behavior

**Code:**
```python
@mcp_server.tool(name='story_bot_shape_tool')
async def shape_tool(parameters: dict = None):
    behavior_obj = getattr(bot, 'shape')
    result = behavior_obj.forward_to_current_action()
    return serialize(result)
```

**Forwarding Chain:**
1. Get behavior object: `bot.shape`
2. Forward to `behavior.forward_to_current_action()`
3. Return result

**Use Case:** AI Chat says "work on shape" - jumps to shape behavior, executes current action

---

### Level 3: Behavior-Action Tool
**Pattern:** `{bot_name}_{behavior}_{action}`  
**Example:** `story_bot_shape_gather_context`, `story_bot_discovery_build_knowledge`

**Responsibility:**
- Executes specific action directly
- Bypasses current action routing
- Allows jumping to any action

**Code:**
```python
@mcp_server.tool(name='story_bot_shape_gather_context')
async def shape_gather_context(parameters: dict = None):
    behavior_obj = getattr(bot, 'shape')
    action_method = getattr(behavior_obj, 'gather_context')
    result = action_method(parameters=parameters)
    return serialize(result)
```

**Forwarding Chain:**
1. Get behavior object: `bot.shape`
2. Get action method: `behavior.gather_context`
3. Execute action: `action_method(parameters)`
4. Return result

**Use Case:** AI Chat says "gather context for discovery" - jumps directly to discovery.gather_context

---

## Forwarding Mechanisms

### Bot.forward_to_current_behavior_and_current_action()

**Purpose:** Route from bot level to specific behavior and action

**Algorithm:**
```python
def forward_to_current_behavior_and_current_action(self):
    # 1. Read workflow state from bot directory
    state_file = bot_dir / 'project_area' / 'workflow_state.json'
    
    # 2. Extract current behavior
    if state_file.exists():
        state_data = json.loads(state_file.read_text())
        current_behavior_path = state_data.get('current_behavior')
        # 'story_bot.shape' -> 'shape'
        current_behavior = current_behavior_path.split('.')[-1]
    else:
        # Default to first behavior
        current_behavior = self.behaviors[0]
    
    # 3. Forward to behavior
    behavior_obj = getattr(self, current_behavior)
    return behavior_obj.forward_to_current_action()
```

**Key Points:**
- Reads persisted workflow state
- Defaults to first behavior if no state
- Delegates to behavior's forwarding mechanism

---

### Behavior.forward_to_current_action()

**Purpose:** Route from behavior level to specific action

**Algorithm:**
```python
def forward_to_current_action(self):
    # 1. Reload workflow state from file (sync in-memory with disk)
    self.workflow.load_state()
    
    # 2. Get current action from workflow state machine
    current_action = self.workflow.current_state
    
    # 3. Get action method
    action_method = getattr(self, current_action)
    
    # 4. Execute action
    result = action_method()
    
    # 5. Check if action marked itself complete
    if self.workflow.is_action_completed(current_action):
        # Action is done - transition to next
        self.workflow.transition_to_next()
    
    return result
```

**Key Points:**
- Reloads state from file (handles in-memory staleness)
- Uses workflow state machine to determine current action
- Only transitions if action marked itself complete
- Preserves action completion semantics

---

### Action Method Execution

**Purpose:** Delegate to template method for common workflow management

**Simple Pattern (Just 2 Lines!):**
```python
def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
    from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
    return self.execute_action('gather_context', GatherContextAction, parameters)
```

**Template Method Handles Everything:**
```python
def execute_action(self, action_name: str, action_class, parameters: Dict = None):
    # 1. Set state machine to this action (handles direct calls)
    if self.workflow.current_state != action_name:
        self.workflow.machine.set_state(action_name)
    
    # 2. Save workflow state (sets current_behavior and current_action)
    self.workflow.save_state()
    
    # 3. Instantiate action with standard parameters
    action = action_class(
        bot_name=self.bot_name,
        behavior=self.name,
        workspace_root=self.workspace_root
    )
    
    # 4. Execute action and get data
    try:
        data = action.execute(parameters)
    except FileNotFoundError:
        data = {'instructions': {}}  # Template may be missing
    
    # 5. Wrap in BotResult (generic)
    return BotResult(
        status='completed',
        behavior=self.name,
        action=action_name,
        data=data
    )
```

**Key Points:**
- **Action methods are just 2 lines** - import and delegate to template
- Template handles all state management (no duplication)
- Template instantiates action with standard parameters
- Template wraps result in BotResult
- **90% code reduction** per action method

---

## State Management

### Workflow State Persistence

**Location:** `{current_project}/workflow_state.json`

**Content:**
```json
{
  "current_behavior": "story_bot.shape",
  "current_action": "story_bot.shape.gather_context",
  "timestamp": "2025-12-04T19:57:07.276186",
  "completed_actions": [
    {
      "action_state": "story_bot.shape.initialize_project",
      "timestamp": "2025-12-04T19:57:07.029592"
    }
  ]
}
```

**Fields:**
- `current_behavior`: Full path to current behavior (bot.behavior)
- `current_action`: Full path to current action (bot.behavior.action)
- `timestamp`: Last state update time
- `completed_actions`: Audit trail of completed actions

---

### State Machine vs Completed Actions

**State Machine (In-Memory):**
- Managed by `transitions` library
- Tracks current state (action name)
- Transitions between actions
- **Problem:** Persists in memory between MCP calls
- **Solution:** Reload from file on each forward call

**Completed Actions (Persistent):**
- Stored in workflow_state.json
- Source of truth for action completion
- Used to determine next action
- Survives server restarts

**Synchronization:**
- `load_state()`: Reads file → Sets state machine
- `save_state()`: Reads state machine → Writes file
- `forward_to_current_action()`: Calls `load_state()` first

---

## Action Completion Flow

### Completion Semantics

**Actions do NOT auto-complete** - they must be explicitly marked complete:

1. **Action returns instructions** → AI follows them
2. **Human reviews results** → Confirms completion
3. **Close tool called** → Marks action complete
4. **Workflow transitions** → Moves to next action

**Code:**
```python
# Step 1: Execute action (returns instructions)
result = bot.shape.gather_context()
# Action NOT marked complete yet

# Step 2: AI follows instructions, human reviews
# ...

# Step 3: Human says "done", close tool called
close_current_action()
# → Calls: workflow.save_completed_action('gather_context')
# → Calls: workflow.transition_to_next()
# → Workflow moves to 'decide_planning_criteria'
```

---

### Special Case: initialize_project

**initialize_project** is the ONLY action that auto-marks itself complete:

```python
def initialize_project(self, parameters: Dict[str, Any] = None):
    # Execute logic
    data = action.initialize_location(...)
    
    # Auto-mark complete if no confirmation required
    if not data.get('requires_confirmation'):
        self.workflow.save_completed_action('initialize_project')
    
    return BotResult(...)
```

**Why:** Project initialization must complete before workflow can proceed

---

## Generator Pattern

### MCPServerGenerator

**Purpose:** Dynamically generate MCP tools for all bot behaviors and actions

**Discovery:**
```python
def discover_actions(self):
    # Scan base_actions/ directory
    for action_dir in base_actions_dir.iterdir():
        config_file = action_dir / 'action_config.json'
        config = json.loads(config_file.read_text())
        
        if config.get('workflow'):
            # Workflow action
            self.workflow_actions.append(config)
        else:
            # Independent action  
            self.independent_actions.append(config)
```

**Registration:**
```python
def register_all_behavior_action_tools(self, mcp_server):
    # 1. Register bot tool
    self.register_bot_tool(mcp_server)
    
    # 2. Register close tool
    self.register_close_current_action_tool(mcp_server)
    
    # 3. Register restart tool
    self.register_restart_server_tool(mcp_server)
    
    # 4. Register behavior tools
    for behavior in behaviors:
        self.register_behavior_tool(mcp_server, behavior)
    
    # 5. Register behavior-action tools
    for behavior in behaviors:
        for action in all_actions:
            self.register_behavior_action_tool(
                mcp_server, behavior, action
            )
```

**Result:** Generates ~60+ MCP tools for a typical bot (8 behaviors × 7 actions + extras)

---

## Tool Invocation Examples

### Example 1: Continue Current Work

**User:** "Continue where I left off"  
**AI Chat:** Invokes `story_bot_tool`  
**Flow:**
1. Bot tool reads workflow_state.json
2. Finds current_behavior: "story_bot.shape"
3. Finds current_action: "story_bot.shape.gather_context"
4. Forwards to `bot.shape.forward_to_current_action()`
5. Executes `gather_context()` action
6. Returns instructions to AI Chat

---

### Example 2: Jump to Specific Behavior

**User:** "Start discovery phase"  
**AI Chat:** Invokes `story_bot_discovery_tool`  
**Flow:**
1. Discovery tool gets `bot.discovery` object
2. Forwards to `discovery.forward_to_current_action()`
3. Workflow loads state, determines current action
4. If no discovery actions complete → defaults to `initialize_project`
5. Executes action, returns instructions
6. **Updates workflow_state.json** with current_behavior: "story_bot.discovery"

---

### Example 3: Jump to Specific Action

**User:** "Gather context for exploration"  
**AI Chat:** Invokes `story_bot_exploration_gather_context`  
**Flow:**
1. Exploration-gather_context tool gets `bot.exploration` object
2. Directly calls `exploration.gather_context(parameters)`
3. Action sets state machine to `gather_context`
4. Action saves workflow state
5. Action executes logic, returns instructions
6. **Updates workflow_state.json** with:
   - current_behavior: "story_bot.exploration"
   - current_action: "story_bot.exploration.gather_context"

---

### Example 4: Close Current Action

**User:** "Done with gather context"  
**AI Chat:** Invokes `story_bot_close_current_action`  
**Flow:**
1. Close tool reads workflow_state.json
2. Extracts current_action: "gather_context"
3. Calls `workflow.save_completed_action('gather_context')`
4. Calls `workflow.transition_to_next()`
5. Workflow moves to `decide_planning_criteria`
6. Returns status: completed, next action

---

## State Synchronization

### Problem: In-Memory State Staleness

**Issue:** Bot instance created once at MCP server startup, reused for all calls

**Scenario:**
1. Call `story_bot_tool` → Executes gather_context → State machine at `gather_context`
2. Delete workflow_state.json file
3. Call `story_bot_tool` again → State machine STILL at `gather_context` (stale!)

**Solution:** Reload state from file on each forward call

```python
def forward_to_current_action(self):
    # Reload from file (sync in-memory with disk)
    self.workflow.load_state()
    
    # Now state machine reflects file state
    current_action = self.workflow.current_state
    # ...
```

---

### State Reset on Missing File

**Problem:** When file deleted, in-memory state stays at last position

**Solution:**
```python
def load_state(self):
    if self.file.exists():
        # Load from file
        # ...
    else:
        # No file - reset to first action
        first_action = self.states[0]
        self.machine.set_state(first_action)
```

**Result:** Deleting workflow_state.json resets to first action

---

## Trigger Words

### Pattern: Natural Language → Tool Routing

**Configuration:** `trigger_words.json` per action

```json
{
  "trigger_patterns": [
    "gather context",
    "clarify requirements",
    "ask questions"
  ]
}
```

**Tool Annotation:**
```python
@mcp_server.tool(
    name='story_bot_shape_gather_context',
    description='gather context for story_bot\nTrigger patterns: gather context, clarify requirements'
)
```

**AI Chat Behavior:**
- Sees trigger patterns in tool catalog
- Matches user intent to tools
- Invokes appropriate tool

---

## Tool Generation

### Generator Workflow

```
1. Load bot config (behaviors list)
   ↓
2. Discover actions (scan base_actions/ directory)
   ↓
3. Register Bot Tool (routes to behavior and action)
   ↓
4. Register Close Tool (marks complete, transitions)
   ↓
5. Register Restart Tool (clears cache, restarts)
   ↓
6. FOR EACH behavior:
   ├─ Register Behavior Tool (routes to action)
   └─ FOR EACH action:
      └─ Register Behavior-Action Tool (executes action)
   ↓
7. Deploy MCP Server (serve tools via protocol)
```

### Tool Count Formula

**For a bot with:**
- 8 behaviors
- 7 workflow actions per behavior

**Total tools:**
- 1 bot tool
- 1 close tool
- 1 restart tool
- 8 behavior tools (one per behavior)
- 64 behavior-action tools (8 behaviors × 8 actions)

**= 75 total MCP tools**

---

## Workflow State Sources of Truth

### Multiple State Representations

**1. workflow_state.json (Persistent)**
- `current_behavior` - String path
- `current_action` - String path
- `completed_actions` - Array of completed action states
- **Use:** Persists across sessions, survives server restarts

**2. State Machine (In-Memory)**
- `workflow.current_state` - Current action name
- `workflow.machine` - transitions library state machine
- **Use:** Manages transitions, enforces valid state changes

**3. current_action (Source of Truth)**
- String format: `bot.behavior.action`
- **Use:** Determines which action to execute next
- **Why:** This is the authoritative current state

**4. completed_actions (Fallback)**
- Array of `{action_state, timestamp}` entries
- **Use:** Fallback when current_action is missing or invalid
- **Why:** Provides backup when current_action unavailable

### Precedence Rules

When determining next action:

1. **Primary:** `current_action` field
   - Extract action name from format: `bot.behavior.action` → `action`
   - Set state machine to that action
   - Use this as source of truth

2. **Fallback:** `completed_actions` array (if current_action missing/invalid)
   - Find last completed action for this behavior
   - Look up next action in transitions
   - Set state machine to that action

2. **Fallback:** `current_action` field
   - Only if completed_actions missing
   - May be stale - use with caution

3. **Default:** First action
   - If no state found
   - Fresh start scenario

**Code:**
```python
def _determine_next_action_from_completed(self, completed_actions):
    if not completed_actions:
        return self.states[0]  # First action
    
    # Find last completed for this behavior
    last_completed = find_last_completed_for_behavior(completed_actions)
    
    if last_completed:
        # Look up next in transitions
        return find_next_action(last_completed, transitions)
    
    return self.states[0]  # Default to first
```

---

## Direct Call vs Forward Call

### Direct Call (Behavior-Action Tool)

**Path:** MCP Tool → Action Method

```
story_bot_shape_gather_context
    ↓
bot.shape.gather_context(parameters)
    ↓ Sets state machine to 'gather_context'
    ↓ Saves workflow state
    ↓ Executes logic
    ↓ Returns instructions
```

**Effects:**
- ✅ Sets current_behavior to 'shape'
- ✅ Sets current_action to 'gather_context'
- ✅ Saves workflow_state.json
- ❌ Does NOT mark action complete
- ❌ Does NOT transition

---

### Forward Call (Bot Tool or Behavior Tool)

**Path:** MCP Tool → forward_to_current_action() → Action Method

```
story_bot_tool
    ↓
bot.forward_to_current_behavior_and_current_action()
    ↓ Reads workflow_state.json
    ↓ Determines current behavior and action
    ↓
bot.shape.forward_to_current_action()
    ↓ Reloads state from file
    ↓ Gets current_action from workflow
    ↓
bot.shape.gather_context()
    ↓ Sets state machine
    ↓ Saves workflow state
    ↓ Executes logic
    ↓ Returns instructions
    ↓
Checks if action complete
    ↓ If complete: transition_to_next()
```

**Effects:**
- ✅ Sets current_behavior and current_action
- ✅ Saves workflow_state.json
- ✅ Checks completion status
- ✅ Auto-transitions if complete

---

## Close Current Action Pattern

### Purpose: Explicit Action Completion

**Tool:** `{bot_name}_close_current_action`  
**Example:** `story_bot_close_current_action`

**Algorithm:**
```python
async def close_current_action(parameters: dict = None):
    # 1. Read workflow state
    state_data = json.loads(state_file.read_text())
    behavior_name = extract_behavior(state_data)
    action_name = extract_action(state_data)
    
    # 2. Get behavior object
    behavior_obj = getattr(bot, behavior_name)
    
    # 3. Mark action complete
    behavior_obj.workflow.save_completed_action(action_name)
    
    # 4. Transition to next
    previous = behavior_obj.workflow.current_state
    behavior_obj.workflow.transition_to_next()
    new_state = behavior_obj.workflow.current_state
    
    # 5. Check if behavior complete (final action)
    if previous == new_state and is_final_action:
        # Transition to next behavior
        return transition_to_next_behavior()
    
    # 6. Return status
    return {
        'status': 'completed',
        'completed_action': action_name,
        'next_action': new_state
    }
```

**Use Cases:**
- Mark action complete after human review
- Transition to next action in workflow
- Transition to next behavior when final action complete

---

## Number Prefix Handling

### Pattern: Folders with Order Prefixes

**Directory Structure:**
```
behaviors/
  1_shape/
    1_guardrails/
      1_required_context/
        key_questions.json
  2_prioritization/
```

**Finding Folders:**
```python
def find_behavior_folder(workspace_root, bot_name, behavior):
    behaviors_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors'
    
    # Try exact match first
    exact = behaviors_dir / behavior
    if exact.exists():
        return exact
    
    # Try with number prefix
    for folder in behaviors_dir.iterdir():
        if folder.is_dir():
            # Strip number prefix: '1_shape' -> 'shape'
            name = folder.name
            if name[0].isdigit() and '_' in name:
                name = name.split('_', 1)[1]
            
            if name == behavior:
                return folder
    
    raise FileNotFoundError(f'Behavior {behavior} not found')
```

**Why:** Allows ordering folders visually while referencing by clean name

---

## Design Principles

### 1. Separation of Concerns

- **MCP Layer:** Tool registration, serialization, parameter handling
- **Bot Layer:** Behavior routing, state management
- **Action Layer:** Business logic, instruction generation

### 2. Explicit State Management

- State persisted to disk (workflow_state.json)
- State reloaded from disk on each call
- In-memory state synced with persistent state

### 3. Completion Semantics

- Actions return instructions (not complete)
- Human explicitly marks complete (via close tool)
- Workflow only transitions when explicitly told

### 4. Source of Truth

- `current_action` field = primary source of truth
- Current action extracted directly from current_action field
- State machine follows current_action
- `completed_actions` array = fallback when current_action missing/invalid
- Current action derived from completed actions
- State machine follows completed actions

### 5. Flexibility

- Three entry points (bot, behavior, action)
- Can follow workflow or jump anywhere
- Can complete actions or skip ahead

---

## Anti-Patterns

### ❌ Auto-Transitioning Actions

**Wrong:**
```python
def gather_context(self):
    data = execute_logic()
    self.workflow.transition_to_next()  # ❌ Auto-transition
    return data
```

**Why Wrong:** Action transitions before human reviews

**Right:**
```python
def gather_context(self):
    data = execute_logic()
    # No transition - wait for close_current_action
    return data
```

---

### ❌ Trusting current_action from File

**Wrong:**
```python
def load_state(self):
    state_data = json.loads(self.file.read_text())
    current_action = state_data.get('current_action')
    self.machine.set_state(current_action)  # ❌ May be stale
```

**Why Wrong:** current_action may be corrupted or stale

**Right:**
```python
def load_state(self):
    state_data = json.loads(self.file.read_text())
    completed_actions = state_data.get('completed_actions', [])
    next_action = self._determine_next_action_from_completed(completed_actions)
    self.machine.set_state(next_action)  # ✅ Derived from source of truth
```

---

### ❌ Not Reloading State on Forward

**Wrong:**
```python
def forward_to_current_action(self):
    current_action = self.workflow.current_state  # ❌ Stale
    action_method = getattr(self, current_action)
    return action_method()
```

**Why Wrong:** In-memory state may be stale from previous calls

**Right:**
```python
def forward_to_current_action(self):
    self.workflow.load_state()  # ✅ Reload from file
    current_action = self.workflow.current_state
    action_method = getattr(self, current_action)
    return action_method()
```

---

### ❌ Swallowing Exceptions

**Wrong:**
```python
try:
    state_data = json.loads(file.read_text())
except Exception:
    pass  # ❌ Silent failure
```

**Why Wrong:** Hides bugs, makes debugging impossible

**Right:**
```python
try:
    state_data = json.loads(file.read_text())
except Exception as e:
    logger.warning(f'Failed to load state from {file}: {e}')  # ✅ Log error
```

---

## Testing Strategy

### Unit Tests

**Test individual components:**
- Workflow state machine transitions
- Action completion tracking
- State file persistence

**Example:**
```python
def test_workflow_determines_next_action_from_completed_actions():
    workflow = Workflow(...)
    workflow_state = {'completed_actions': [...]}
    workflow.load_state()
    assert workflow.current_state == expected_action
```

---

### Integration Tests

**Test complete flows:**
- Bot → Behavior → Action execution
- Direct action calls
- Close action and transition
- Jump to different behavior

**Example:**
```python
def test_complete_workflow_end_to_end():
    bot = Bot(...)
    bot.shape.initialize_project({'confirm': True})
    bot.shape.forward_to_current_action()
    bot.shape.workflow.save_completed_action('gather_context')
    bot.discovery.gather_context()
    # Verify state shows discovery.gather_context
```

---

### MCP Integration Tests

**Test via MCP tools:**
- Call bot tool, behavior tool, action tool
- Verify forwarding works
- Verify state persisted
- Verify close tool works

**Example:**
```python
mcp_story-bot_story_bot_tool()
# → Returns initialize_project

mcp_story-bot_story_bot_close_current_action()
# → Transitions to gather_context
```

---

## Summary

**Key Patterns:**
1. **Three-level decomposition** - Bot, Behavior, Action tools
2. **Forwarding chain** - Each level delegates to next
3. **State synchronization** - Reload from file on each forward
4. **Explicit completion** - Close tool marks actions complete
5. **Source of truth** - current_action drives state determination (with completed_actions as fallback)
6. **Direct calls** - Actions set state before saving
7. **Generator** - Dynamically creates all tools from config

**Benefits:**
- Flexible invocation (continue, jump to behavior, jump to action)
- Resilient state management (survives restarts, handles staleness)
- Explicit workflow control (human controls transitions)
- Easy testing (three levels of granularity)
- Discoverable (trigger words, tool descriptions)

**Result:** ~75 MCP tools per bot, all automatically generated and managed!

