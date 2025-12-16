# Robits Framework Documentation

## Understanding the System Through StoryBot

This documentation describes the Agile Bot framework—a system for building AI-powered workflow bots—through the lens of its primary implementation: **StoryBot**. StoryBot helps teams transform user needs into well-structured, testable stories using a progressive refinement workflow.

---

## Executive Summary

The Robits framework consists of:

1. **Base Bot** (Foundation Layer) - Provides core infrastructure: workflow state management, action execution, MCP server generation, activity tracking, and validation
2. **Specific Bots** (Implementation Layer) - Like StoryBot, which defines behaviors, rules, templates, and domain-specific logic
3. **MCP Integration** - Exposes bot functionality as tools that AI assistants can invoke

**Key Insight**: Base Bot is "invisible" infrastructure. Users interact with StoryBot, which uses Base Bot under the hood.

---

## Part 1: StoryBot Overview

### Purpose

StoryBot guides teams through a **7-behavior workflow** for story development:

```
Shape → Prioritization → Discovery → Exploration → Scenarios → Tests → Code
```

Each behavior represents a phase in progressive story refinement—from initial idea to executable specifications.

### The Seven Behaviors

| Behavior | Purpose | Primary Output |
|----------|---------|----------------|
| **Shape** | Create story map and domain model from user context | story-graph.json, story-map.md, domain_outline.md |
| **Prioritization** | Organize stories into increments and prioritize backlog | increment files, prioritized backlog |
| **Discovery** | Elaborate stories with flows, rules, integration details | enriched story-graph.json, discovery documents |
| **Exploration** | Define acceptance criteria and Given/When/Then statements | acceptance criteria in story documents |
| **Scenarios** | Write detailed BDD scenarios from acceptance criteria | scenario documents |
| **Tests** | Generate executable test code from scenarios | test files |
| **Code** | Review code quality and validate implementation | validation reports |

### Invoking StoryBot

StoryBot can be invoked through:

1. **CLI Commands**:
```bash
# Run specific behavior
story_bot_cli --behavior shape

# Run specific action within behavior
story_bot_cli --behavior shape --action clarify

# Continue from current state
story_bot_cli

# Close current action and move to next
story_bot_cli --close
```

2. **MCP Tools** (via AI assistant):
```
mcp_story-bot_shape       # Routes to current action in shape behavior
mcp_story-bot_discovery   # Routes to current action in discovery behavior
mcp_story-bot_tool        # Routes to current behavior and action
```

---

## Part 2: The Action Workflow

Every behavior follows the same **5-action workflow**:

```
clarify → strategy → build → validate → render
```

### Action Descriptions

#### 1. Clarify (Gather Context)
- **Purpose**: Gather context and clarify requirements before proceeding
- **Inputs**: Key questions to answer, evidence to collect
- **Outputs**: Answered questions stored in `clarification.json`
- **Guardrails**: `guardrails/required_context/` folder provides questions and evidence requirements

#### 2. Strategy (Planning)
- **Purpose**: Determine planning approach, make strategic decisions
- **Inputs**: Decision criteria, typical assumptions
- **Outputs**: Strategy decisions stored in `strategy.json`
- **Guardrails**: `guardrails/planning/` folder provides decision criteria and assumptions

#### 3. Build (Knowledge Graph)
- **Purpose**: Build structured knowledge from gathered context
- **Inputs**: Knowledge graph templates, build instructions
- **Outputs**: `story-graph.json` or domain-specific knowledge graph
- **Templates**: `content/knowledge_graph/` folder provides structure templates

#### 4. Validate (Rules Check)
- **Purpose**: Validate content against behavior-specific and common rules
- **Inputs**: Rules from `rules/` folder, knowledge graph to validate
- **Outputs**: Validation report with violations and suggestions
- **Scanners**: Python code scanners that programmatically check rules

#### 5. Render (Output Generation)
- **Purpose**: Generate human-readable outputs from knowledge graph
- **Inputs**: Templates, transformers, synchronizers
- **Outputs**: Markdown documents, diagrams, formatted files
- **Templates**: `content/render/` folder provides output templates

---

## Part 3: Base Bot Architecture (The Foundation)

### Core Concepts

```
Bot
 └── Behaviors Collection
      └── Behavior (e.g., "shape")
           └── Actions Collection
                └── Action (e.g., "clarify")
                     └── Guardrails
                     └── Content Templates
                     └── Rules
```

### Key Classes

#### Bot (`src/bot/bot.py`)
- Creates and manages behaviors from configuration
- Routes to current behavior based on workflow state
- Handles out-of-order execution confirmations

```python
# Bot usage example
bot = Bot(bot_name='story_bot', bot_directory=path, config_path=config)
result = bot.forward_to_current_behavior_and_current_action()
```

#### Behavior (`src/bot/behavior.py`)
- Manages actions within a behavior phase
- Tracks workflow state for its actions
- Provides navigation between actions

#### Action (`src/actions/action.py`)
- Base class for all action implementations
- Loads and merges instructions from multiple sources
- Tracks activity (start/completion) for audit trail

### Folder Structure

```
agile_bot/bots/
├── base_bot/                      # Foundation layer
│   ├── base_actions/              # Shared action definitions
│   │   ├── build/
│   │   ├── clarify/
│   │   ├── render/
│   │   ├── strategy/
│   │   └── validate/
│   ├── src/
│   │   ├── actions/               # Action implementations
│   │   ├── bot/                   # Core bot classes
│   │   ├── cli/                   # CLI generation
│   │   ├── mcp/                   # MCP server generation
│   │   └── scanners/              # Validation scanners
│   ├── patterns/                  # Architecture documentation
│   └── rules/                     # Common validation rules
│
└── story_bot/                     # StoryBot implementation
    ├── bot_config.json            # Bot configuration
    ├── behaviors/
    │   ├── shape/
    │   │   ├── behavior.json      # Behavior configuration
    │   │   ├── guardrails/        # Questions, planning criteria
    │   │   ├── content/           # Templates, knowledge graph specs
    │   │   └── rules/             # Behavior-specific validation rules
    │   ├── discovery/
    │   ├── exploration/
    │   └── ... (other behaviors)
    └── src/
        └── story_bot_mcp_server.py  # MCP server entry point
```

---

## Part 4: Configuration System

### Bot Configuration (`bot_config.json`)

```json
{
  "name": "story_bot",
  "behaviors": ["shape", "prioritization", "discovery", "exploration", "scenarios", "tests", "code"],
  "description": "Helps teams create, refine, and specify user stories",
  "goal": "Transform user needs into well-structured, testable stories",
  "baseActionsPath": "agile_bot/bots/base_bot/base_actions",
  "mcp": {
    "server_name": "story_bot",
    "command": "python",
    "args": ["agile_bot/bots/story_bot/src/story_bot_mcp_server.py"]
  },
  "cli": { ... },
  "trigger_words": ["stories", "story", "story map", ...]
}
```

### Behavior Configuration (`behavior.json`)

```json
{
  "behaviorName": "shape",
  "order": 1,
  "description": "Create a story map and domain model outline",
  "goal": "Shape both story map and domain model together from user context",
  "inputs": "User context, interviews, vision documents",
  "outputs": "story-graph.json, story-map.md, domain_outline.md",
  "actions_workflow": {
    "actions": [
      { "name": "clarify", "order": 1, "next_action": "strategy" },
      { "name": "strategy", "order": 2, "next_action": "build" },
      { "name": "build", "order": 3, "next_action": "validate" },
      { "name": "validate", "order": 4, "next_action": "render" },
      { "name": "render", "order": 5 }
    ]
  },
  "trigger_words": {
    "patterns": ["start.*shaping", "let.*s.*shape", "new.*project", ...]
  }
}
```

---

## Part 5: Workflow State Management

### State File (`behavior_action_state.json`)

Located in the workspace directory, this file tracks:

```json
{
  "current_behavior": "story_bot.discovery",
  "current_action": "story_bot.discovery.build",
  "completed_actions": [
    {
      "action_state": "story_bot.shape.clarify",
      "timestamp": "2025-12-16T10:00:00Z"
    }
  ],
  "timestamp": "2025-12-16T11:30:00Z"
}
```

### State Transitions

1. **Normal Flow**: Actions execute in sequence within a behavior
   - clarify → strategy → build → validate → render
   
2. **Closing Actions**: Use `close_current_action` to mark complete and advance
   - This is the **only** way to transition (actions don't auto-complete)
   
3. **Out-of-Order Execution**: Requires explicit human confirmation
   - Prevents accidental workflow jumps
   - Tracked in `out_of_order_confirmations`

---

## Part 6: MCP Server Integration

### Tool Hierarchy

The MCP server exposes tools at three levels:

```
Level 1: Bot Tool
├── story_bot_tool           → Routes to current behavior & action

Level 2: Behavior Tools
├── story_bot_shape          → Routes to current action in shape
├── story_bot_discovery      → Routes to current action in discovery
└── ... (one per behavior)

Level 3: Utility Tools
├── story_bot_close_current_action    → Marks action complete, advances
├── story_bot_get_working_dir         → Shows current working directory
├── story_bot_confirm_out_of_order    → Human confirmation for skipping
└── story_bot_restart_server          → Restarts MCP server
```

### Tool Generation

The `MCPServerGenerator` dynamically creates all tools:

```python
generator = MCPServerGenerator(bot_directory=path)
mcp_server = generator.create_server_instance()
generator.register_all_behavior_action_tools(mcp_server)
mcp_server.run()
```

### Trigger Words

Each behavior has trigger patterns that help AI assistants recognize when to invoke tools:

```json
"trigger_words": {
  "patterns": [
    "start.*discovery",
    "let.*s.*discover",
    "discovery",
    "what.*are.*we.*building.*next"
  ]
}
```

---

## Part 7: Guardrails System

### Purpose
Guardrails guide AI assistants through each action by providing:
- **Required Context**: Questions that must be answered
- **Evidence**: Information that must be collected
- **Planning Criteria**: Decision frameworks for strategy

### Structure

```
behaviors/shape/guardrails/
├── required_context/
│   ├── key_questions.json      # Questions to ask user
│   └── evidence.json           # Evidence to collect
└── planning/
    ├── decision_criteria.json  # Criteria for strategy decisions
    ├── typical_assumptions.json
    └── recommended_activities.json
```

### Example Key Questions

```json
{
  "key_questions": [
    {
      "question": "Who are the primary users of this system?",
      "context": "Understanding user personas helps shape appropriate stories"
    },
    {
      "question": "What business outcomes should this initiative achieve?",
      "context": "Connects stories to measurable business value"
    }
  ]
}
```

---

## Part 8: Validation & Rules System

### Rule Structure

Rules are JSON files with validation logic:

```json
{
  "rule_id": "ensure_vertical_slices",
  "name": "Stories Must Be Vertical Slices",
  "description": "Each story should deliver end-to-end value",
  "context": "when shaping stories",
  "examples": {
    "do": ["User can view their profile (covers UI → API → DB)"],
    "dont": ["Create user table (pure backend)"]
  },
  "scanner": "ensure_vertical_slices_scanner.py"
}
```

### Scanner Implementation

Scanners are Python classes that programmatically validate rules:

```python
class EnsureVerticalSlicesScanner:
    def scan(self, knowledge_graph: dict, rule: Rule) -> list[Violation]:
        violations = []
        for story in knowledge_graph.get('stories', []):
            if not self._is_vertical_slice(story):
                violations.append(Violation(
                    rule_id=rule.rule_id,
                    message=f"Story '{story['name']}' is not a vertical slice",
                    location=story['path'],
                    severity="warning"
                ))
        return violations
```

### Rule Hierarchy

1. **Common Rules**: Apply to all bots (`base_bot/rules/`)
2. **Bot Rules**: Apply to all behaviors in a bot (`story_bot/rules/`)
3. **Behavior Rules**: Apply only to specific behavior (`behaviors/shape/rules/`)

---

## Part 9: Content & Templates

### Knowledge Graph Templates

Define the structure of data to be built:

```json
{
  "schema": {
    "epics": [{
      "name": "string",
      "description": "string",
      "features": [{
        "name": "string",
        "stories": [{
          "name": "string",
          "acceptance_criteria": ["string"]
        }]
      }]
    }]
  }
}
```

### Render Templates

Define how to transform knowledge graph into outputs:

```json
{
  "template_type": "story_map_markdown",
  "output_file": "story-map.md",
  "sections": [
    {
      "heading": "# Story Map: {{project_name}}",
      "content": "{{epics}}"
    }
  ]
}
```

### Synchronizers

Bi-directional sync between knowledge graph and documents:
- **Extract**: Parse documents → Update knowledge graph
- **Render**: Knowledge graph → Generate documents

---

## Part 10: Activity Tracking

### Audit Trail

Every action execution is logged to `activity_log.json`:

```json
{
  "action_state": "story_bot.shape.clarify",
  "status": "started",
  "timestamp": "2025-12-16T10:00:00Z"
}
{
  "action_state": "story_bot.shape.clarify",
  "status": "completed",
  "timestamp": "2025-12-16T10:15:00Z",
  "duration": 900000,
  "outputs": { ... }
}
```

### Purpose
- Audit trail of all work performed
- Timing information for workflow optimization
- Debugging failed actions

---

## Part 11: Usage Patterns

### Pattern 1: Starting Fresh

```bash
# Start a new project with shaping
story_bot_cli --behavior shape

# Or via MCP tool
mcp_story-bot_shape
```

### Pattern 2: Continuing Work

```bash
# Resume from where you left off
story_bot_cli

# Via MCP tool
mcp_story-bot_tool
```

### Pattern 3: Scoped Work

```bash
# Work on specific stories
story_bot_cli --behavior discovery --story_names='["Login","Register"]'

# Work on specific increment
story_bot_cli --behavior prioritization --increment_priorities=[1,2]
```

### Pattern 4: Workflow Transitions

```bash
# Complete current action and move to next
story_bot_cli --close

# Via MCP tool
mcp_story-bot_close_current_action
```

---

## Part 12: Extension Points

### Creating a New Bot

1. Create bot directory: `agile_bot/bots/my_bot/`
2. Create `bot_config.json` with behaviors list
3. Create behavior folders with `behavior.json`
4. Add guardrails, content templates, rules as needed
5. Generate MCP server: `MCPServerGenerator(path).generate_server()`

### Adding a New Behavior

1. Create folder: `behaviors/my_behavior/`
2. Create `behavior.json` with workflow configuration
3. Add guardrails folders for clarify and strategy
4. Add content templates for build and render
5. Add rules for validate

### Adding Custom Rules

1. Create rule JSON in `behaviors/{behavior}/rules/`
2. Optionally create Python scanner in `src/actions/validate/scanners/`
3. Scanner implements `scan(knowledge_graph, rule) -> List[Violation]`

---

## Part 13: CLI Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `story_bot_cli --list` | List all behaviors |
| `story_bot_cli --behavior <name> --list` | List actions for behavior |
| `story_bot_cli --help` | Show comprehensive help |
| `story_bot_cli --close` | Close current action |

### Behavior Commands

| Command | Description |
|---------|-------------|
| `--behavior shape` | Run shape behavior |
| `--behavior prioritization` | Run prioritization behavior |
| `--behavior discovery` | Run discovery behavior |
| `--behavior exploration` | Run exploration behavior |
| `--behavior scenarios` | Run scenarios behavior |
| `--behavior tests` | Run tests behavior |
| `--behavior code` | Run code behavior |

### Scope Parameters

| Parameter | Description |
|-----------|-------------|
| `--story_names=[...]` | Scope to specific stories |
| `--epic_names=[...]` | Scope to specific epics |
| `--increment_priorities=[...]` | Scope to specific increments |
| `--test=<file>` | Test files to validate |
| `--src=<file>` | Source files to validate |

---

## Part 14: Key Files Reference

| File | Purpose |
|------|---------|
| `bot_config.json` | Bot configuration (behaviors, MCP, CLI) |
| `behavior.json` | Behavior configuration (actions, triggers) |
| `behavior_action_state.json` | Current workflow state |
| `activity_log.json` | Action execution audit trail |
| `story-graph.json` | Knowledge graph (main data structure) |
| `clarification.json` | Stored answers from clarify phase |
| `strategy.json` | Strategic decisions from strategy phase |
| `validation-report.md` | Output from validate action |

---

## Part 15: Troubleshooting

### Common Issues

**"No workflow state found"**
- Start a behavior: `story_bot_cli --behavior shape`

**"Behavior not found"**
- Check bot_config.json behaviors list
- Use `--list` to see available behaviors

**"Out-of-order execution blocked"**
- Human must call `confirm_out_of_order` tool
- Or proceed with expected workflow order

**"Scanner execution failed"**
- Check Python scanner code for errors
- Review scanner logs for stack trace

### Debug Mode

Enable verbose logging in bot_config.json:
```json
{
  "verbose_mode": true
}
```

---

## Appendix: Domain Graph

The domain graph visualizes the framework's conceptual model:

```
Base Bot
├── Executes Actions → Workflow, Behavior, Action
├── Tracks Activity → Behavior, Action
├── Routes to behaviors → Router, Trigger Words
├── Persists content → Content
└── Manages project state → Project

Specific Bot (e.g., StoryBot)
├── Provides Behavior config → Bot Config, Behavior
├── Provides MCP config → MCP Config
├── Provides Renderers, Extractors, Synchronizers
└── Provides Trigger Words

Behavior
├── Performs Configured Actions → Actions
├── Invokes On Trigger Words → List
├── Injects Instructions → Text
├── Provides Guardrails → GuardRails
├── Provides Rules → Rule, Validation
└── Provides Content Specs → Content

Action (clarify, strategy, build, validate, render)
├── Injects Instructions → Behavior
├── Loads Relevant Content → Content
└── Saves content changes → Content
```

---

*This documentation describes the Robits framework as implemented in the augmented-teams repository. For the latest updates, consult the pattern files in `base_bot/patterns/` and the source code.*

