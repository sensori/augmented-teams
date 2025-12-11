# Bot Architecture Pattern

## Overview

**Bot** → creates **Behaviors** → execute **Actions**

All wired together via **bot_config.json**

---

## Configuration Structure

### bot_config.json
```json
{
  "name": "story_bot",
  "behaviors": ["shape", "prioritization", "discovery", "exploration"]
}
```

### Folder Structure

```
agile_bot/bots/story_bot/
├── config/
│   └── bot_config.json              ← Bot configuration (name, behaviors list)
├── behaviors/
│   ├── 1_shape/
│   │   ├── instructions.json        ← Behavior-level instructions
│   │   ├── trigger_words.json       ← Trigger patterns for Behavor Tool
│   │   ├── 1_guardrails/            ← Guardrails (questions, evidence, planning)
│   │   │   ├── 1_required_context/  ← Key questions, evidence for gather_context
│   │   │   └── 2_planning/          ← Assumptions, decision criteria for decide_planning
│   │   ├── 2_content/               ← Content (templates, knowledge graphs)
│   │   │   ├── 1_knowledge_graph/   ← Templates for build_knowledge
│   │   │   └── 2_render/            ← Templates, transformers for render_output
│   │   └── 3_rules/                 ← Behavior-specific validation rules
│   ├── 2_prioritization/
│   ├── 4_discovery/
│   └── 5_exploration/
├── rules/                           ← Bot-level rules (apply to all behaviors)
└── src/
    └── story_bot_mcp_server.py      ← MCP server entry point

agile_bot/bots/base_bot/
├── base_actions/                    ← Action definitions (shared across all bots)
│   ├── 1_initialize_project/
│   │   ├── action_config.json       ← Action config (workflow, order, next_action)
│   │   ├── instructions.json        ← Base instructions for action
│   │   └── trigger_words.json       ← Trigger patterns
│   ├── 1_gather_context/
│   ├── 2_decide_planning_criteria/
│   ├── 3_build_knowledge/
│   ├── 4_render_output/
│   └── 5_validate_rules/
└── rules/
    └── common_rules.json            ← Common rules for all bots
```

### Folder Purposes

| Folder | Purpose |
|--------|---------|
| **config/** | Bot configuration (behaviors list) |
| **behaviors/{behavior}/** | Behavior-specific content and rules |
| **behaviors/{behavior}/guardrails/** | Questions, evidence, planning criteria |
| **behaviors/{behavior}/content/** | Templates, knowledge graphs, transformers |
| **behaviors/{behavior}/rules/** | Behavior-specific validation rules |
| **base_actions/{action}/** | Shared action logic and instructions |
| **base_actions/{action}/action_config.json** | Workflow configuration (order, next_action) |
| **rules/** | Bot-level or common rules |

---

## How Actions Use Folder Content

### initialize_project
Loads base instructions from `base_actions/1_initialize_project/instructions.json`. Detects project location and saves to `project_area/project_location.json` for workflow state persistence.

### gather_context
Loads base instructions from `base_actions/1_gather_context/instructions.json` and merges with behavior-specific instructions. Loads guardrails from `behaviors/{behavior}/guardrails/required_context/` (key_questions.json, evidence.json) to guide context gathering.

### decide_planning_criteria
Loads base instructions from `base_actions/2_decide_planning_criteria/instructions.json`. Loads planning guardrails from `behaviors/{behavior}/guardrails/planning/` (typical_assumptions.json, decision_criteria/*.json) to inject planning criteria and assumptions.

### build_knowledge
Loads base instructions from `base_actions/3_build_knowledge/instructions.json`. Loads knowledge graph template from `behaviors/{behavior}/content/knowledge_graph/*.json` to guide knowledge graph construction.

### render_output
Loads base instructions from `base_actions/4_render_output/instructions.json`. Loads templates from `behaviors/{behavior}/content/render/templates/` and transformers from `behaviors/{behavior}/content/render/transformers/` to render structured output.

### validate_rules
Loads base instructions from `base_actions/5_validate_rules/instructions.json`. Loads common rules from `base_bot/rules/common_rules.json` and behavior-specific rules from `behaviors/{behavior}/rules/*.json` to validate content.

---

## Pattern: Bot Class

**Bot reads config and creates Behavior instances.**

```python
class Bot:
    def __init__(self, bot_name: str, workspace_root: Path, config_path: Path):
        self.name = bot_name
        self.workspace_root = workspace_root
        
        # Load config
        self.config = read_json_file(config_path)
        
        # Create behavior instances from config
        self.behaviors = self.config.get('behaviors', [])
        for behavior_name in self.behaviors:
            behavior_obj = Behavior(
                name=behavior_name,
                bot_name=self.name,
                workspace_root=self.workspace_root
            )
            setattr(self, behavior_name, behavior_obj)  # ← Creates bot.shape, bot.discovery, etc.
```

**Usage:**
```python
bot = Bot('story_bot', workspace, config_path)

# Bot now has behavior properties from config:
bot.shape           # ← Behavior instance for 'shape'
bot.prioritization  # ← Behavior instance for 'prioritization'
bot.discovery       # ← Behavior instance for 'discovery'
bot.exploration     # ← Behavior instance for 'exploration'
```

---

## Pattern: Behavior Class

**Behavior executes actions and manages workflow state.**

```python
class Behavior:
    def __init__(self, name: str, bot_name: str, workspace_root: Path):
        self.name = name          # 'shape', 'discovery', etc.
        self.bot_name = bot_name  # 'story_bot'
        self.workspace_root = workspace_root
        
        # Initialize workflow (state machine)
        states, transitions = load_workflow_states_and_transitions(workspace_root)
        self.workflow = Workflow(bot_name, name, workspace_root, states, transitions)
    
    def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute gather_context action."""
        action = GatherContextAction(self.bot_name, self.name, self.workspace_root)
        ...  # Track activity, execute, return result
    
    def build_knowledge(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute build_knowledge action."""
        action = BuildKnowledgeAction(self.bot_name, self.name, self.workspace_root)
        ...  # Track activity, execute, return result
```

**Usage:**
```python
bot = Bot('story_bot', workspace, config_path)

# Execute actions via behavior:
result = bot.shape.gather_context()        # ← Executes GatherContextAction
result = bot.shape.build_knowledge()       # ← Executes BuildKnowledgeAction
result = bot.discovery.gather_context()    # ← Same action, different behavior context
```

---

## Pattern: Action Classes

**Action classes contain business logic, no state knowledge.**

```python
class GatherContextAction:
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        self.bot_name = bot_name       # 'story_bot'
        self.behavior = behavior       # 'shape', 'discovery', etc.
        self.workspace_root = workspace_root
        self.tracker = ActivityTracker(workspace_root)
    
    def load_and_merge_instructions(self) -> Dict[str, Any]:
        """Load instructions from base_actions and behavior folder."""
        base_path = workspace_root / 'agile_bot/bots/base_bot/base_actions/1_gather_context/instructions.json'
        behavior_path = workspace_root / f'agile_bot/bots/{bot_name}/behaviors/{behavior}/instructions.json'
        ...  # Load, merge, return
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior, 'gather_context')
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior, 'gather_context', outputs, duration)
```

---

## How It Ties Together

### Configuration → Bot → Behaviors → Actions

```
bot_config.json: {"behaviors": ["shape", "discovery"]}
        ↓
Bot.__init__ reads config
        ↓
Creates: bot.shape = Behavior('shape', 'story_bot', workspace)
Creates: bot.discovery = Behavior('discovery', 'story_bot', workspace)
        ↓
bot.shape.gather_context() called
        ↓
Creates: GatherContextAction('story_bot', 'shape', workspace)
        ↓
Action loads instructions from:
  - base_actions/1_gather_context/instructions.json
  - behaviors/shape/instructions.json
```

### Example Execution Flow

```python
# 1. Create bot from config
config_path = workspace / 'agile_bot/bots/story_bot/config/bot_config.json'
bot = Bot('story_bot', workspace, config_path)

# 2. Bot has behaviors from config
assert hasattr(bot, 'shape')
assert hasattr(bot, 'discovery')

# 3. Execute action through behavior
result = bot.shape.gather_context()

# Behind the scenes:
# - bot.shape (Behavior instance) creates GatherContextAction
# - GatherContextAction loads instructions from base_actions + behavior folders
# - Activity tracked to activity_log.json
# - Workflow state saved to workflow_state.json
```

---

## Key Relationships

| Class | Responsibility | Created By | Creates |
|-------|---------------|------------|---------|
| **Bot** | Manages behaviors | User/MCP Server | Behavior instances |
| **Behavior** | Executes actions | Bot from config | Action instances |
| **Action** | Business logic | Behavior methods | Results |
| **Workflow** | State management | Behavior | State machine |

---

## Configuration Examples

### Single Behavior Bot
```json
{
  "name": "domain_bot",
  "behaviors": ["event_storming"]
}
```
Result: `bot.event_storming` available

### Multi-Behavior Bot
```json
{
  "name": "story_bot",
  "behaviors": ["shape", "prioritization", "discovery", "exploration", "scenarios", "examples", "tests"]
}
```
Result: `bot.shape`, `bot.prioritization`, `bot.discovery`, etc. available

---

## Summary

**Configuration drives everything:**

1. Config lists behaviors → Bot creates Behavior instances
2. Behavior names become Bot properties → `bot.shape`, `bot.discovery`
3. Each Behavior has action methods → `bot.shape.gather_context()`
4. Action methods create Action classes → `GatherContextAction`, `BuildKnowledgeAction`
5. Actions load content from behavior-specific folders → Customize per behavior

**Result**: One Bot, multiple Behaviors, shared Actions with behavior-specific content ✅

