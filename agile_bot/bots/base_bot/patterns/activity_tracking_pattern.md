# Activity Tracking Pattern Using TinyDB

## Overview

TinyDB tracks complete audit trail of all action executions.

**Location**: `project_area/activity_log.json`  
**Purpose**: "What happened?" (complete history)  
**Format**: TinyDB database (queryable, immutable)

---

## Core Pattern

### 1. ActivityTracker Class

```python
from tinydb import TinyDB

class ActivityTracker:
    def __init__(self, workspace_root: Path):
        self.db_path = workspace_root / 'project_area' / 'activity_log.json'
    
    def track_start(self, bot_name: str, behavior: str, action: str):
        with TinyDB(self.db_path) as db:
            db.insert({
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'started',
                'timestamp': datetime.now().isoformat()
            })
    
    def track_completion(self, bot_name: str, behavior: str, action: str, 
                        outputs: dict = None, duration: int = None):
        with TinyDB(self.db_path) as db:
            db.insert({
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'outputs': outputs,
                'duration': duration
            })
```

### 2. Action Class Pattern

```python
class {ActionName}Action:
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        self.tracker = ActivityTracker(workspace_root)  # ← Create tracker
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior, '{action_name}')
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior, '{action_name}', outputs, duration)
```

### 3. Template Method Pattern (Base Class)

```python
class Behavior:
    def execute(self, action_class, action_name: str, 
                execute_fn, parameters: Dict = None) -> BotResult:
        """Template method: wraps action execution with activity tracking."""
        action = action_class(self.bot_name, self.name, self.workspace_root)
        
        action.track_activity_on_start()        # ← Log start
        result = execute_fn(action, parameters) # ← Execute (injected)
        action.track_activity_on_completion(outputs=result)  # ← Log completion
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action=action_name,
            data=result
        )
```

### 4. Behavior Method Pattern (Uses Template)

```python
def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
    return self.execute(
        action_class=GatherContextAction,
        action_name='gather_context',
        execute_fn=lambda action, params: action.load_and_merge_instructions(),
        parameters=parameters
    )

def build_knowledge(self, parameters: Dict[str, Any] = None) -> BotResult:
    return self.execute(
        action_class=BuildKnowledgeAction,
        action_name='build_knowledge',
        execute_fn=lambda action, params: action.inject_knowledge_graph_template(),
        parameters=parameters
    )
```

---

## Querying Activity Log

```python
from tinydb import TinyDB, Query

log_file = workspace_root / 'project_area' / 'activity_log.json'

# Get all activities
with TinyDB(log_file) as db:
    all_activities = db.all()

# Query by status, action, behavior
Activity = Query()
with TinyDB(log_file) as db:
    completed = db.search(Activity.status == 'completed')
    shape_activities = db.search(Activity.action_state.matches(r'.*\.shape\..*'))
```

---

## Activity vs Workflow State

| Feature | Activity (TinyDB) | Workflow State (JSON) |
|---------|-------------------|----------------------|
| **Purpose** | Audit trail | Current state |
| **File** | `activity_log.json` | `workflow_state.json` |
| **Entries** | Multiple per action | Single state |
| **Grows** | Forever | Updated |
| **Use** | "What happened?" | "Where am I?" |

---

## Integration Checklist

- ✅ Action `__init__` creates `ActivityTracker`
- ✅ Action provides `track_activity_on_start()`
- ✅ Action provides `track_activity_on_completion()`
- ✅ Behavior method calls tracking before/after execution
- ✅ TinyDB logs to `project_area/activity_log.json`
