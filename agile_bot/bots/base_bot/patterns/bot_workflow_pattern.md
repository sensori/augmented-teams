# Bot Workflow Pattern Using transitions

## Overview

This document describes the pattern for using `transitions` state machine library to manage workflow state across:
- **Project-level** isolation (each project has independent workflows)
- **Bot-level** workflow tracking (each bot in a project has independent state)
- **Behavior-level** execution (shape, prioritize, discovery, etc.)
- **Action-level** states (gather_context, plan, build_knowledge, etc.)

## Key Concepts

- **State Machine** = Behavior workflow with defined states and transitions
- **States** = Individual actions (gather_context, build_knowledge, etc.)
- **Transitions** = Valid moves between actions (gather_context → decide_planning_criteria)
- **State Persistence** = Workflow state saved to `workflow_state.json`
- **Automatic validation** = transitions prevents invalid state changes

---

## Pattern: Action Classes

**Action classes contain pure business logic with NO state knowledge.**

```python
class {ActionName}Action:
    """Action implementation - pure business logic."""
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = workspace_root
    
    def execute(self):
        """Execute action business logic."""
        # Load config, process data, return result
        return {action_result_data}
```

**Examples:**
- `GatherContextAction`
- `BuildKnowledgeAction`
- `ValidateRulesAction`

---

## Pattern: Workflow Class

**Workflow encapsulates state machine and state persistence (Single Responsibility).**

```python
from transitions import Machine

class Workflow:
    """Manages workflow state machine and persistence."""
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path,
                 states: List[str], transitions: List[Dict]):
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = workspace_root
        self.workflow_states = states
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=states[0],
            auto_transitions=False
        )
        
        # Load saved state
        self.load_state()
    
    @property
    def current_state(self) -> str:
        """Get current state from state machine."""
        return self.state
    
    def transition_to_next(self):
        """Transition to next state and save."""
        try:
            self.proceed()  # Trigger transition
            self.save_state()
        except Exception:
            pass  # Already at final state
    
    def load_state(self):
        """Load workflow state from file."""
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            action_name = state_data.get('current_action', '').split('.')[-1]
            if action_name in self.workflow_states:
                self.state = action_name
    
    def save_state(self):
        """Save workflow state to file."""
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({
            'current_behavior': f'{self.bot_name}.{self.behavior}',
            'current_action': f'{self.bot_name}.{self.behavior}.{self.state}',
            'timestamp': datetime.now().isoformat()
        }), encoding='utf-8')
```

## Pattern: Behavior Class

**Behavior focuses on action execution for a particular Behavior of a Bot, delegates workflow to Workflow object.**

```python
class Behavior:
    """Behavior executes actions, delegates state management to Workflow."""
    
    def __init__(self, name: str, bot_name: str, workspace_root: Path):
        self.name = name
        self.bot_name = bot_name
        self.workspace_root = workspace_root
        
        # Load workflow configuration
        states, transitions = load_workflow_states_and_transitions(workspace_root)
        
        # Initialize workflow (contains state machine)
        self.workflow = Workflow(bot_name, name, workspace_root, states, transitions)
    
    @property
    def state(self):
        """Delegate to workflow current state."""
        return self.workflow.current_state
    
    def {action_name}(self, parameters: dict = None):
        """Execute {action_name} action."""
        action = {ActionName}Action(self.bot_name, self.name, self.workspace_root)
        result = action.execute()
        
        return BotResult(status='completed', behavior=self.name, 
                        action='{action_name}', data=result)
    
    def forward_to_current_action(self):
        """Forward to current action using workflow."""
        current_action = self.workflow.current_state
        
        action_method = getattr(self, current_action)
        result = action_method()
        
        self.workflow.transition_to_next()  # ← Delegate to workflow
        
        return result
```

---

## Pattern: State Configuration

**Workflow states and transitions loaded dynamically from action_config.json files.**

```python
def load_workflow_states_and_transitions(workspace_root: Path):
    """
    Load workflow configuration from action_config.json files.
    
    Reads all action configs from base_actions/, sorts by order,
    builds state list and transition list.
    
    Returns:
        (states, transitions)
    """
    base_actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    # Load all action configs
    actions = []
    for action_dir in base_actions_dir.iterdir():
        config_file = action_dir / 'action_config.json'
        if config_file.exists():
            config = json.loads(config_file.read_text())
            if config.get('workflow'):  # Only workflow actions
                actions.append(config)
    
    # Sort by order
    actions.sort(key=lambda x: x['order'])
    
    # Build states list
    states = [action['name'] for action in actions]
    
    # Build transitions list
    transitions = []
    for action in actions:
        if 'next_action' in action:
            transitions.append({
                'trigger': 'proceed',
                'source': action['name'],
                'dest': action['next_action']
            })
    
    return states, transitions
```

### Example action_config.json

```json
{
  "name": "gather_context",
  "workflow": true,
  "order": 2,
  "next_action": "decide_planning_criteria"
}
```

### Generated State Machine

```python
states = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 
          'render_output', 'validate_rules', 'correct_bot']

transitions = [
    {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
    {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
    {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
    {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
    {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'correct_bot'},
]
```

---

## Pattern: Bot Class

**Bot forwards to current behavior based on workflow state file.**

```python
class Bot:
    """Bot creates behavior instances and forwards to current behavior."""
    
    def __init__(self, bot_name: str, workspace_root: Path, config_path: Path):
        self.name = bot_name
        self.workspace_root = workspace_root
        self.config = read_json_file(config_path)
        
        # Create behavior instances from config
        # Each behavior has its own state machine
        for behavior_name in self.config['behaviors']:
            behavior_obj = Behavior(
                name=behavior_name,
                bot_name=bot_name,
                workspace_root=workspace_root
            )
            setattr(self, behavior_name, behavior_obj)
    
    def forward_to_current_behavior_and_current_action(self):
        """Forward to current behavior and current action."""
        # Read workflow state file
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        
        current_behavior = None
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_behavior_path = state_data.get('current_behavior', '')
            # Extract: 'story_bot.discovery' -> 'discovery'
            current_behavior = current_behavior_path.split('.')[-1]
        
        if not current_behavior or current_behavior not in self.behaviors:
            # Default to FIRST behavior in bot config
            current_behavior = self.config['behaviors'][0]
        
        # Forward to behavior (behavior's state machine knows current action)
        behavior_instance = getattr(self, current_behavior)
        return behavior_instance.forward_to_current_action()
```

---

## Concrete Example

### Scenario
- **Project:** `mob_rule`
- **Bot:** `story_bot`
- **Bot Config:** `{'behaviors': ['shape', 'prioritize', 'arrange', 'discovery']}`
- **Current State:** `prioritize / build_knowledge` ← We are here!

### Workflow State File
```json
{
  "current_behavior": "story_bot.prioritize",
  "current_action": "story_bot.prioritize.build_knowledge",
  "timestamp": "2025-12-04T10:00:00Z"
}
```

### Execution Flow

```python
bot = Bot('story_bot', Path('/workspace/mob_rule'), config_path)
result = bot.forward_to_current_behavior_and_current_action()
```

**What happens:**

1. **Bot.forward_to_current_behavior_and_current_action()** reads `workflow_state.json`
2. Extracts: `current_behavior='prioritize'` from state file
3. Forwards to: `bot.prioritize.forward_to_current_action()`
4. **Behavior.forward_to_current_action()** reads state machine: `self.state == 'build_knowledge'`
5. **Executes:** `self.build_knowledge()` method
6. **Transitions:** state machine proceeds to `'render_output'`
7. **Saves state:** writes updated state to `workflow_state.json`

```python
assert result.behavior == 'prioritize'
assert result.action == 'build_knowledge'
# After execution, state machine now at: 'render_output'
```

---

## Test Pattern

**Tests use `prefect_test_harness()` and call normal Bot API.**

```python
from prefect.testing.utilities import prefect_test_harness

class Test{StoryName}:
    """Story: {Story Name}."""
    
    def test_{scenario_name}(self, workspace_root):
        """
        SCENARIO: {Scenario description}
        GIVEN: {preconditions}
        WHEN: {action}
        THEN: {expected result}
        """
        with prefect_test_harness():
            # Given
            bot = Bot('{bot_name}', workspace_root, config_path)
            
            # When
            result = bot.invoke_current_action()
            
            # Then: Prefect tracked state, resumed at correct behavior/action
            assert result.behavior == '{behavior_name}'
            assert result.action == '{action_name}'
            
            # NO manual workflow_state.json files needed!
            # Prefect manages all state in its database
```

---

## Key Benefits

### No Manual State Files
- ❌ No `workflow_state.json` files
- ❌ No manual state reading/writing
- ✅ Prefect database stores everything

### Automatic Resumption
- Prefect remembers:
  - Which behavior was running
  - Which task was executing
  - Which tasks completed
- Just call `bot.invoke_current_action()` → resumes automatically

### Multi-Project Support
- Each `(project, bot)` = separate flow
- `mob_rule.story_bot` state independent from `mm3e.story_bot`

### Observability
- Prefect UI shows all workflow states
- Task durations tracked automatically
- Failure/retry handled by Prefect

---

## Summary

**Flow Hierarchy:**
```
Prefect Flow Identity: (project_path, bot_name)
  ↓
Flow State Parameter: current_behavior
  ↓  
Prefect Task Tracking: current_task (automatic)
```

**Example:**
```
Flow: ('mob_rule', 'story_bot')
  → Behavior: 'prioritize' (in flow parameters)
    → Task: 'plan' (tracked by Prefect)
```

**Result:** Prefect knows we're at `mob_rule / story_bot / prioritize / plan` ✅

