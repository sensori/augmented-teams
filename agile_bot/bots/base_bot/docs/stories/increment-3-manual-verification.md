# Increment 3 Manual Verification Steps

Manual steps to verify each increment 3 story works in production.

## Prerequisites

1. Ensure bot config exists:
```bash
cat agile_bot/bots/story_bot/config/bot_config.json
# Should show: {"name": "story_bot", "behaviors": ["shape", "prioritization", "arrange", "discovery", "exploration", "scenarios", "examples", "tests"]}
```

2. Install dependencies:
```bash
pip install transitions==0.9.0 tinydb==4.8.0 pytest-asyncio==0.23.5
```

---

## Story 1: Generate Bot Tools

**Manual Steps:**

1. Run bot tool generator:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.bot_tool_generator import BotToolGenerator

workspace = Path('.')
config_path = Path('agile_bot/bots/story_bot/config/bot_config.json')

gen = BotToolGenerator('story_bot', config_path, workspace)
tool = gen.create_bot_tool()
print(f'Created tool: {tool.name}')
"
```

2. **Verify:** Output shows `Created tool: story_bot_tool`

---

## Story 2: Generate Behavior Tools

**Manual Steps:**

1. Run behavior tool generator:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.behavior_tool_generator import BehaviorToolGenerator

workspace = Path('.')
config_path = Path('agile_bot/bots/story_bot/config/bot_config.json')

gen = BehaviorToolGenerator('story_bot', config_path, workspace)
tools = gen.create_behavior_tools()
print(f'Created {len(tools)} behavior tools:')
for tool in tools:
    print(f'  - {tool.name}')
"
```

2. **Verify:** Output shows 8 tools (one per behavior):
   - `story_bot_shape_tool`
   - `story_bot_prioritization_tool`
   - `story_bot_arrange_tool`
   - `story_bot_discovery_tool`
   - `story_bot_exploration_tool`
   - `story_bot_scenarios_tool`
   - `story_bot_examples_tool`
   - `story_bot_tests_tool`

---

## Story 3: Forward To Current Behavior and Current Action

**Manual Steps (Using Chat + MCP):**

1. **Start fresh** - Clear workflow state:
```bash
rm project_area/workflow_state.json
```

2. **In chat, say:** "Use story bot to shape this project"

3. **Behind the scenes:** 
   - Cursor invokes MCP tool: `story_bot_tool` (bot tool)
   - Bot tool calls: `bot.forward_to_current_behavior_and_current_action()`
   - Since no workflow state exists, defaults to first behavior (shape) and first action (gather_context)

4. **Verify bot response shows:**
   - Bot executed shape behavior
   - Ran gather_context action (asked questions about project)

5. **Check workflow state file created:**
```bash
cat project_area/workflow_state.json
```
Expected content:
```json
{
  "current_behavior": "story_bot.shape",
  "current_action": "story_bot.shape.decide_planning_criteria",
  "timestamp": "2025-12-04T..."
}
```

6. **In chat, say:** "Continue with story bot"

7. **Verify:**
   - Bot resumes at `decide_planning_criteria` (not back at gather_context!)
   - Workflow state advances to `build_knowledge`

8. **Switch behaviors - In chat, say:** "Use story bot discovery behavior"

9. **Check workflow state updated:**
```bash
cat project_area/workflow_state.json
```
Expected: `current_behavior` changed to `story_bot.discovery`, action reset to `gather_context`

**Key Point:** Bot tool automatically routes to current behavior and action based on saved state!

---

## Story 4: Forward To Current Action

**Manual Steps (Using Chat + MCP):**

1. **Setup:** Create workflow state showing interrupted workflow:
```bash
mkdir -p project_area
echo '{"current_behavior": "story_bot.discovery", "current_action": "story_bot.discovery.build_knowledge"}' > project_area/workflow_state.json
```

2. **In chat, say:** "Run story bot discovery behavior"

3. **Behind the scenes:**
   - Cursor invokes: `story_bot_discovery_tool` (behavior tool)
   - Behavior tool calls: `bot.discovery.forward_to_current_action()`
   - State machine shows current state: `build_knowledge`
   - Executes: `build_knowledge()` action (NOT gather_context!)

4. **Verify bot response:**
   - Bot executed build_knowledge (not first action)
   - Resumed where you left off

5. **Check state transitioned:**
```bash
cat project_area/workflow_state.json
```
Expected: `current_action` changed to `story_bot.discovery.render_output` (next action)

6. **Continue - In chat, say:** "Continue story bot discovery"

7. **Verify:**
   - Bot runs `render_output` (next action after build_knowledge)
   - State advances to `validate_rules`

8. **Test behavior switching - In chat, say:** "Switch to story bot exploration"

9. **Check state:**
```bash
cat project_area/workflow_state.json
```
Expected: Behavior changed to `exploration`, action reset to `gather_context`

**Key Point:** Behavior tool automatically resumes at current action within that behavior!

---

## Story 5: Track Activity for Gather Context Action

**Manual Steps:**

1. Clear activity log:
```bash
rm project_area/activity_log.json
```

2. Execute gather_context with activity tracking:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.actions.gather_context_action import GatherContextAction

workspace = Path('.')
action = GatherContextAction('story_bot', 'shape', workspace)

action.track_activity_on_start()
print('Activity tracked on start')

action.track_activity_on_completion(
    outputs={'questions_count': 5}, 
    duration=120
)
print('Activity tracked on completion')
"
```

3. **Verify:** Check activity log contains entries:
```bash
python -c "
from pathlib import Path
from tinydb import TinyDB

log_file = Path('project_area/activity_log.json')
with TinyDB(log_file) as db:
    entries = db.all()
    print(f'Total entries: {len(entries)}')
    for entry in entries:
        print(f'  - {entry[\"action_state\"]} ({entry[\"status\"]})')
"
```

4. **Verify:** Output shows 2 entries:
   - `story_bot.shape.gather_context (started)`
   - `story_bot.shape.gather_context (completed)`

---

## Story 6: Generate MCP Bot Server

**Manual Steps:**

1. Generate MCP server:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.mcp_server_generator import MCPServerGenerator

workspace = Path('.')
gen = MCPServerGenerator(workspace, 'agile_bot/bots/story_bot')

server = gen.create_server_instance()
print(f'Created server: {server.name}')
print(f'Bot initialized: {gen.bot is not None}')
print(f'Behaviors: {gen.bot.behaviors}')
"
```

2. **Verify:** Output shows:
   - `Created server: story_bot_server`
   - `Bot initialized: True`
   - `Behaviors: ['shape', 'prioritization', 'arrange', ...]`

---

## Story 7: Generate Behavior Action Tools

**Manual Steps:**

1. Generate and register all behavior-action tools:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.mcp_server_generator import MCPServerGenerator

workspace = Path('.')
gen = MCPServerGenerator(workspace, 'agile_bot/bots/story_bot')

server = gen.create_server_instance()
gen.register_all_behavior_action_tools(server)

print(f'Total tools registered: {len(gen.registered_tools)}')
print('Sample tools:')
for tool in gen.registered_tools[:5]:
    print(f'  - {tool[\"name\"]}')
"
```

2. **Verify:** Output shows:
   - `Total tools registered: 48` (8 behaviors × 6 actions)
   - Sample tools like:
     - `story_bot_shape_gather_context`
     - `story_bot_shape_decide_planning`
     - `story_bot_discovery_build_knowledge`

---

## Story 8: MCP Server Integration Test

**Manual Steps:**

1. Start MCP server:
```bash
cd agile_bot/bots/story_bot
python -m agile_bot.bots.base_bot.src.mcp_server
```

2. In another terminal, call MCP tool:
```bash
# Using MCP CLI or Cursor
mcp call story_bot_shape_gather_context {}
```

3. **Verify:** 
   - Tool responds with BotResult
   - Workflow state file created at `project_area/workflow_state.json`
   - Activity log updated at `project_area/activity_log.json`

4. Check workflow progressed:
```bash
cat project_area/workflow_state.json
# Should show: current_action='story_bot.shape.decide_planning_criteria' (next action)
```

---

## Story 9: Workflow State Machine

**Manual Steps:**

1. Check state machine transitions:
```bash
python -c "
from pathlib import Path
from agile_bot.bots.base_bot.src.bot import Bot

workspace = Path('.')
config = Path('agile_bot/bots/story_bot/config/bot_config.json')

bot = Bot('story_bot', workspace, config)
print(f'Initial state: {bot.shape.state}')
print(f'Workflow states: {bot.shape.workflow_states}')

# Execute action (transitions automatically)
result = bot.shape.forward_to_current_action()
print(f'After execution, state: {bot.shape.state}')
"
```

2. **Verify:** Output shows:
   - `Initial state: gather_context`
   - `Workflow states: ['gather_context', 'decide_planning_criteria', ...]`
   - `After execution, state: decide_planning_criteria` (transitioned)

---

## Complete End-to-End Verification

**Manual Steps:**

1. Clear all state:
```bash
rm -rf project_area
```

2. Run full workflow through MCP:
```bash
# Call 1: First action
mcp call story_bot_shape_gather_context {}

# Call 2: Next action (state machine advanced)
mcp call story_bot_shape_tool {}  # Bot tool routes to current

# Call 3: Continue workflow
mcp call story_bot_shape_tool {}

# etc...
```

3. Verify at each step:
```bash
# Check state file
cat project_area/workflow_state.json

# Check activity log
python -c "
from pathlib import Path
from tinydb import TinyDB
with TinyDB(Path('project_area/activity_log.json')) as db:
    print(f'Total activities: {len(db.all())}')
    for entry in db.all():
        print(f'  {entry[\"action_state\"]} - {entry[\"status\"]}')
"
```

4. **Verify workflow progression:**
   - State advances through: gather_context → decide_planning_criteria → build_knowledge → render_output → validate_rules
   - Activity log grows with each action
   - Bot tool routes to correct behavior/action based on state

---

## Validation Checklist

- [ ] Bot tools can be generated
- [ ] Behavior tools can be generated  
- [ ] Bot forwards to first behavior/action when no state
- [ ] Bot resumes at saved behavior/action from state file
- [ ] Behavior forwards to current action from state machine
- [ ] State machine transitions automatically after each action
- [ ] Activity tracking logs start and completion
- [ ] Workflow state persists across invocations
- [ ] MCP tools invoke real bot behavior actions
- [ ] State machine validates transitions (can't skip actions)

**All increment 3 stories verified!** ✅

