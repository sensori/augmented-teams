# Shaping Workflow End-to-End Test Instructions

**Purpose:** This file contains step-by-step instructions for an AI to execute and validate the entire shaping workflow for the mob_minion project.

**Project Location:** `demo/mob_minion/`

**Important:** This is a TEST workflow. A backup has been created. Follow these instructions exactly to validate the entire shaping process works correctly.

---

## Test Variant Configuration

**Current Variant:** {{VARIANT}}
**Valid Variants:** CLI_BEHAVIOR | CLI_ACTION | MCP_BEHAVIOR | MCP_ACTION

### Variant Definitions

| Variant | Channel | Granularity | Entry Pattern | Progression Method |
|---------|---------|-------------|---------------|-------------------|
| CLI_BEHAVIOR | CLI | Behavior | `/story_bot-shape @input.txt` | Auto (use `/story_bot-continue` between phases) |
| CLI_ACTION | CLI | Action | `/story_bot-shape initialize_project @input.txt` | Manual (explicit action calls for each phase) |
| MCP_BEHAVIOR | MCP | Behavior | "shape stories for mob minion" | Auto (use `story_bot_close_current_action` to mark done, then call behavior tool again with trigger words to continue) |
| MCP_ACTION | MCP | Action | "initialize project for mob minion" | Manual (trigger words invoke specific action tools) |

### Entry Point Mapping Table

| Phase | Action | CLI_BEHAVIOR | CLI_ACTION | MCP_BEHAVIOR | MCP_ACTION |
|-------|--------|--------------|-----------|--------------|------------|
| 1 | initialize_project | `/story_bot-shape @input.txt` | `/story_bot-shape initialize_project @input.txt` | "shape stories for mob minion" → `story_bot_shape_tool` | "initialize project" or "set project location" → `story_bot_shape_initialize_project` |
| 2 | gather_context | `/story_bot-continue` | `/story_bot-shape gather_context` | `story_bot_close_current_action` then "continue shaping" → `story_bot_shape_tool` | "gather context" → `story_bot_shape_gather_context` |
| 3 | decide_planning_criteria | `/story_bot-continue` | `/story_bot-shape decide_planning_criteria` | `story_bot_close_current_action` then "continue shaping" → `story_bot_shape_tool` | "decide planning" → `story_bot_shape_decide_planning` |
| 4 | build_knowledge | `/story_bot-continue` | `/story_bot-shape build_knowledge` | `story_bot_close_current_action` then "continue shaping" → `story_bot_shape_tool` | "build knowledge" or "create structure" → `story_bot_shape_build_knowledge` |
| 5 | render_output | `/story_bot-continue` | `/story_bot-shape render_output` | `story_bot_close_current_action` then "continue shaping" → `story_bot_shape_tool` | "render output" → `story_bot_shape_render_output` |
| 6 | validate_rules | `/story_bot-continue` | `/story_bot-shape validate_rules` | `story_bot_close_current_action` then "continue shaping" → `story_bot_shape_tool` | "validate rules" or "check against rules" → `story_bot_shape_validate_rules` |

### MCP Tool Names Reference

**Bot-Level Tools:**
- `story_bot_tool` - Routes to current behavior and action
- `story_bot_close_current_action` - Marks current action complete and transitions to next

**Behavior-Level Tools:**
- `story_bot_shape_tool` - Routes to current action in shape behavior

**Action-Level Tools:**
- `story_bot_shape_initialize_project` - Execute initialize_project action
- `story_bot_shape_gather_context` - Execute gather_context action
- `story_bot_shape_decide_planning` - Execute decide_planning_criteria action (normalized name)
- `story_bot_shape_build_knowledge` - Execute build_knowledge action
- `story_bot_shape_render_output` - Execute render_output action
- `story_bot_shape_validate_rules` - Execute validate_rules action

### Trigger Words Reference

**Behavior-Level Trigger Words** (from `1_shape/trigger_words.json`):
- "shape.*capability", "story.*shape", "new.*project", "begin.*new", "start.*new", "create.*new", "want.*to.*build", etc.

**Action-Level Trigger Words** (from `base_actions/{action}/trigger_words.json`):
- `initialize_project`: "update.*project.*location", "set.*project.*to", "project.*location", "change.*project.*location"
- `build_knowledge`: "create.*structure", "build.*content"
- `validate_rules`: "check.*against.*rule", "validate.*content", "verify.*compliance"
- `correct_bot`: "please make.*correction", "fix.*because", "apply.*correction"

**Note:** Actions without explicit trigger_words.json files should use the action name as trigger (e.g., "gather context", "decide planning", "render output")

---

## Execution Modes

This test can be run in two modes:

### Mode 1: Straight-Through Passing (Automated)

**Purpose:** Run the entire workflow automatically and provide a comprehensive report at the end.

**Instructions for AI:**
- Execute ALL phases (0-7) sequentially without stopping
- Complete each step and move immediately to the next
- Do NOT pause for user confirmation between steps
- At the end, provide a comprehensive report with:
  - Summary of all phases completed
  - Files created and their locations
  - Any issues or errors encountered
  - Validation results for each phase
  - Final state of workflow_state.json
  - List of all files in docs/stories/ directory

**When to use:** When you want to quickly validate the entire workflow runs end-to-end.

---

### Mode 2: Pause Mode (Step-by-Step with Review)

**Purpose:** Go through each step one at a time, pausing after each step for user review.

**Instructions for AI:**
- Execute ONE step at a time
- After completing each step:
  1. **STOP and report completion**
  2. **Show what was created/changed** (file paths, key content snippets)
  3. **Wait for user confirmation** before proceeding to next step
  4. Use format: "✅ Step X.Y completed. [Summary]. Waiting for your confirmation to proceed to Step X.Y+1."
- Do NOT proceed to the next step until user explicitly confirms
- After user confirms, proceed to the next step and repeat

**Step Completion Report Format:**
```
✅ Step X.Y: [Step Name] - COMPLETED

**What was done:**
- [Action taken]

**Files created/modified:**
- [File path 1] - [Brief description]
- [File path 2] - [Brief description]

**Validation results:**
- ✅ [Validation check 1]
- ✅ [Validation check 2]

**Ready for next step:** Step X.Y+1: [Next Step Name]

[WAITING FOR USER CONFIRMATION TO PROCEED]
```

**When to use:** When you want to review each step individually and see the state at each point.

---

## Mode Selection

**At the start of execution, AI must:**
1. Determine which mode to use based on user instruction:
   - User says "straight-through", "automated", "run all", "no pauses" → Use **Straight-Through Mode**
   - User says "pause mode", "step by step", "one at a time", "pause after each" → Use **Pause Mode**
   - No mode specified → Use **Pause Mode** (default for safety)
2. Determine which variant to use based on user instruction or test context:
   - User says "CLI behavior", "CLI_BEHAVIOR" → Use **CLI_BEHAVIOR** variant
   - User says "CLI action", "CLI_ACTION" → Use **CLI_ACTION** variant
   - User says "MCP behavior", "MCP_BEHAVIOR" → Use **MCP_BEHAVIOR** variant
   - User says "MCP action", "MCP_ACTION" → Use **MCP_ACTION** variant
   - No variant specified → Use **CLI_BEHAVIOR** (default)
3. Announce the selected mode and variant clearly:
   - **Straight-Through:** "Running in STRAIGHT-THROUGH mode with {{VARIANT}} variant - will complete all phases automatically and provide final report at the end"
   - **Pause Mode:** "Running in PAUSE mode with {{VARIANT}} variant - will pause after each step for your review and confirmation"

**Default:** If mode not specified, use **Pause Mode** for safety. If variant not specified, use **CLI_BEHAVIOR**.

---

## Phase 0: Cleanup and Preparation

### Step 0.1: Delete All Generated Files (Keep Only input.txt and Instructions)

**Action:** Delete all files and directories EXCEPT `input.txt` and `SHAPING_WORKFLOW_INSTRUCTIONS.md`:
- Delete: `docs/` directory (and all contents)
- Delete: `workflow_state.json`
- Delete: `activity_log.json`
- Keep: `input.txt` (this is the source material)
- Keep: `SHAPING_WORKFLOW_INSTRUCTIONS.md` (this instruction file - needed to run the test!)

**Validation:** 
- Verify only `input.txt` and `SHAPING_WORKFLOW_INSTRUCTIONS.md` remain in `demo/mob_minion/`
- Verify `docs/` directory does not exist

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 1.1

---

## Phase 1: Initialize Project

### Step 1.1: Entry Point (Variant-Specific)

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Command:** `/story_bot-shape @demo/mob_minion/input.txt`

**Expected Behavior:**
- Command should forward to `initialize_project` action
- Instructions should ask to confirm project location

**Validation:**
- Instructions received should specify project location: `demo/mob_minion/`
- Instructions should ask for confirmation
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Command:** `/story_bot-shape initialize_project @demo/mob_minion/input.txt`

**Expected Behavior:**
- Command should execute `initialize_project` action directly
- Instructions should ask to confirm project location

**Validation:**
- Instructions received should specify project location: `demo/mob_minion/`
- Instructions should ask for confirmation
- Action executed directly (not routed through behavior)
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**User Input:** "shape stories for mob minion" (matches trigger pattern from `1_shape/trigger_words.json`)

**AI Action:**
1. Recognize trigger words match behavior-level patterns (e.g., "shape.*capability", "story.*shape", "new.*project")
2. Check available MCP tools
3. Invoke `story_bot_shape_tool` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_tool` should be called
- Tool should route to current action (initialize_project if no state exists)
- Instructions should be returned for initialize_project action
- Instructions should ask to confirm project location

**Validation:**
- MCP tool `story_bot_shape_tool` was called
- Tool returned instructions for initialize_project action
- Instructions specify project location: `demo/mob_minion/`
- Instructions ask for confirmation
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**User Input:** "initialize project for mob minion" or "set project location to demo/mob_minion"
**Note:** These match trigger patterns from `base_actions/1_initialize_project/trigger_words.json` (e.g., "update.*project.*location", "set.*project.*to", "project.*location")

**AI Action:**
1. Recognize trigger words match action-level patterns
2. Check available MCP tools
3. Invoke `story_bot_shape_initialize_project` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_initialize_project` should be called
- Tool should execute initialize_project action directly
- Instructions should be returned for initialize_project action
- Instructions should ask to confirm project location

**Validation:**
- MCP tool `story_bot_shape_initialize_project` was called
- Tool executed initialize_project action
- Instructions specify project location: `demo/mob_minion/`
- Instructions ask for confirmation
<!-- END_VARIANT:MCP_ACTION -->

### Step 1.2: Confirm Project Location

**Action:** Follow the instructions to confirm the project location is `demo/mob_minion/`

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Action:** Confirm the project location when prompted

**Validation:**
- `agile_bot/bots/story_bot/current_project.json` should be created
- File should contain: `{"current_project": "C:\\dev\\augmented-teams\\demo\\mob_minion"}`
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Action:** Confirm the project location when prompted

**Validation:**
- `agile_bot/bots/story_bot/current_project.json` should be created
- File should contain: `{"current_project": "C:\\dev\\augmented-teams\\demo\\mob_minion"}`
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**Action:** When `initialize_project` returns `requires_confirmation: true`, you MUST call the action-level tool with `confirm=True` to actually confirm and create the workflow state:

1. Call `story_bot_shape_initialize_project` MCP tool with parameters:
   - `{"confirm": True, "project_area": "C:\\dev\\augmented-teams\\demo\\mob_minion"}`

**Expected Behavior:**
- Action-level tool should execute with confirmation
- `workflow_state.json` should be created
- `current_project.json` should be updated/confirmed

**Validation:**
- `agile_bot/bots/story_bot/current_project.json` should exist with correct location
- `demo/mob_minion/workflow_state.json` should be created
- Workflow state should contain `completed_actions` with `initialize_project` entry
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**Action:** When `initialize_project` returns `requires_confirmation: true`, call the action-level tool again with `confirm=True`:

1. Call `story_bot_shape_initialize_project` MCP tool with parameters:
   - `{"confirm": True, "project_area": "C:\\dev\\augmented-teams\\demo\\mob_minion"}`

**Expected Behavior:**
- Action-level tool should execute with confirmation
- `workflow_state.json` should be created
- `current_project.json` should be updated/confirmed

**Validation:**
- `agile_bot/bots/story_bot/current_project.json` should exist with correct location
- `demo/mob_minion/workflow_state.json` should be created
- Workflow state should contain `completed_actions` with `initialize_project` entry
<!-- END_VARIANT:MCP_ACTION -->

### Step 1.3: Continue to Next Action (Variant-Specific)

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Command:** `/story_bot-continue` (or use `--close` flag)

**Expected Behavior:**
- Workflow should transition to `gather_context` action
- Instructions should be returned for gathering context

**Validation:**
- `demo/mob_minion/workflow_state.json` should be created
- State should show: `current_action: "story_bot.shape.gather_context"`
- Instructions should contain key questions to ask
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Command:** `/story_bot-shape gather_context`

**Expected Behavior:**
- Command should execute `gather_context` action directly
- Instructions should be returned for gathering context

**Validation:**
- `demo/mob_minion/workflow_state.json` should be created (if not already exists)
- Instructions should contain key questions to ask
- Action executed directly (not routed through continue)
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**AI Action:** After completing initialize_project, invoke `story_bot_close_current_action` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_close_current_action` should be called
- Tool should mark initialize_project as complete
- Tool should transition workflow to `gather_context` action
- Tool should NOT execute the next action - it only marks complete and transitions

**Validation:**
- MCP tool `story_bot_close_current_action` was called
- `demo/mob_minion/workflow_state.json` should be created
- State should show: `current_action: "story_bot.shape.gather_context"`
- `completed_actions` should include `initialize_project`
- No instructions returned (tool only transitions, doesn't execute)

**Next Step:** To actually execute the next action, call the behavior tool again using trigger words (e.g., "I want to continue shaping" or "shape stories for mob minion")
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**User Input:** "gather context"

**AI Action:**
1. Recognize trigger words match action name (or check for action-level trigger words if they exist)
2. Check available MCP tools
3. Invoke `story_bot_shape_gather_context` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_gather_context` should be called
- Tool should execute gather_context action directly
- Instructions should be returned for gathering context

**Validation:**
- MCP tool `story_bot_shape_gather_context` was called
- Tool executed gather_context action
- Instructions should contain key questions to ask
<!-- END_VARIANT:MCP_ACTION -->

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 2.0

---

## Phase 2: Gather Context

### Step 2.0: Execute Next Action (MCP_BEHAVIOR Only)

<!-- START_VARIANT:MCP_BEHAVIOR -->
**User Input:** "I want to continue shaping" or "shape stories for mob minion" (trigger words to continue workflow)

**AI Action:**
1. Recognize trigger words match behavior-level patterns
2. Check available MCP tools
3. Invoke `story_bot_shape_tool` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_tool` should be called
- Tool should route to current action (gather_context after transition)
- Instructions should be returned for gather_context action

**Validation:**
- MCP tool `story_bot_shape_tool` was called
- Tool returned instructions for gather_context action
- Instructions contain key questions to ask
<!-- END_VARIANT:MCP_BEHAVIOR -->

### Step 2.1: Review Gather Context Instructions

**Action:** Review the instructions returned from gather_context action

**Expected Content:**
- Instructions should list key questions from `agile_bot/bots/story_bot/behaviors/1_shape/1_guardrails/1_required_context/key_questions.json`
- Instructions should ask AI to present questions to user and gather answers

### Step 2.2: Execute Gather Context (Human-in-the-Loop Simulation)

**Action:** As the AI, simulate answering the key questions based on the content in `input.txt`:
- Answer questions about users, goals, problems, domain concepts, etc.
- Use information from the input.txt file to provide answers

**Validation:**
- After providing answers, `demo/mob_minion/docs/stories/clarification.json` should be created
- File should contain answers organized under `shape.key_questions`
- Verify all key questions have been answered

### Step 2.3: Continue to Next Action (Variant-Specific)

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `decide_planning_criteria` action
- Instructions should be returned for planning

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.decide_planning_criteria"`
- `completed_actions` should include `gather_context`
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Command:** `/story_bot-shape decide_planning_criteria`

**Expected Behavior:**
- Command should execute `decide_planning_criteria` action directly
- Instructions should be returned for planning

**Validation:**
- Instructions should be returned for planning
- Action executed directly
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**AI Action:** After completing gather_context, invoke `story_bot_close_current_action` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_close_current_action` should be called
- Tool should mark gather_context as complete
- Tool should transition workflow to `decide_planning_criteria` action
- Tool should NOT execute the next action - it only marks complete and transitions

**Validation:**
- MCP tool `story_bot_close_current_action` was called
- `workflow_state.json` should show: `current_action: "story_bot.shape.decide_planning_criteria"`
- `completed_actions` should include `gather_context`
- No instructions returned (tool only transitions, doesn't execute)

**Next Step:** To actually execute the next action, call the behavior tool again using trigger words (e.g., "I want to continue shaping")
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**User Input:** "decide planning" or "decide planning criteria"

**AI Action:**
1. Recognize trigger words match action name (decide_planning_criteria normalizes to decide_planning)
2. Check available MCP tools
3. Invoke `story_bot_shape_decide_planning` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_decide_planning` should be called
- Tool should execute decide_planning_criteria action directly
- Instructions should be returned for planning

**Validation:**
- MCP tool `story_bot_shape_decide_planning` was called
- Tool executed decide_planning_criteria action
- Instructions should be returned for planning
<!-- END_VARIANT:MCP_ACTION -->

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 3.0

---

## Phase 3: Decide Planning Criteria

### Step 3.0: Execute Next Action (MCP_BEHAVIOR Only)

<!-- START_VARIANT:MCP_BEHAVIOR -->
**User Input:** "I want to continue shaping" or "shape stories for mob minion" (trigger words to continue workflow)

**AI Action:**
1. Recognize trigger words match behavior-level patterns
2. Check available MCP tools
3. Invoke `story_bot_shape_tool` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_tool` should be called
- Tool should route to current action (decide_planning_criteria after transition)
- Instructions should be returned for decide_planning_criteria action

**Validation:**
- MCP tool `story_bot_shape_tool` was called
- Tool returned instructions for decide_planning_criteria action
- Instructions contain assumptions and decision criteria
<!-- END_VARIANT:MCP_BEHAVIOR -->

### Step 3.1: Review Planning Instructions

**Action:** Review the instructions returned from decide_planning_criteria action

**Expected Content:**
- Instructions should present assumptions and decision criteria
- Instructions should ask AI to present options to user and gather decisions

### Step 3.2: Execute Planning (Human-in-the-Loop Simulation)

**Action:** As the AI, simulate making planning decisions:
- Review assumptions (focus_user_flow, end_to_end, etc.)
- Make decisions about drill_down_approach, flow_scope_and_granularity, etc.
- Use reasonable defaults based on the project type

**Validation:**
- After making decisions, `demo/mob_minion/docs/stories/planning.json` should be created
- File should contain `shape.assumptions_made` and `shape.decisions_made`
- Verify decisions are appropriate for a story mapping project

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 3.3

### Step 3.3: Continue to Next Action (Variant-Specific)

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `build_knowledge` action
- Instructions should be returned for building knowledge graph

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.build_knowledge"`
- `completed_actions` should include both `gather_context` and `decide_planning_criteria`
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Command:** `/story_bot-shape build_knowledge`

**Expected Behavior:**
- Command should execute `build_knowledge` action directly
- Instructions should be returned for building knowledge graph

**Validation:**
- Instructions should be returned for building knowledge graph
- Action executed directly
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**AI Action:** After completing decide_planning_criteria, invoke `story_bot_close_current_action` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_close_current_action` should be called
- Tool should mark decide_planning_criteria as complete
- Tool should transition workflow to `build_knowledge` action
- Tool should NOT execute the next action - it only marks complete and transitions

**Validation:**
- MCP tool `story_bot_close_current_action` was called
- `workflow_state.json` should show: `current_action: "story_bot.shape.build_knowledge"`
- `completed_actions` should include both `gather_context` and `decide_planning_criteria`
- No instructions returned (tool only transitions, doesn't execute)

**Next Step:** To actually execute the next action, call the behavior tool again using trigger words (e.g., "I want to continue shaping")
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**User Input:** "build knowledge" or "create structure" (matches trigger patterns from `base_actions/4_build_knowledge/trigger_words.json`)

**AI Action:**
1. Recognize trigger words match action-level patterns ("create.*structure", "build.*content")
2. Check available MCP tools
3. Invoke `story_bot_shape_build_knowledge` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_build_knowledge` should be called
- Tool should execute build_knowledge action directly
- Instructions should be returned for building knowledge graph

**Validation:**
- MCP tool `story_bot_shape_build_knowledge` was called
- Tool executed build_knowledge action
- Instructions should be returned for building knowledge graph
<!-- END_VARIANT:MCP_ACTION -->

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 4.0

---

## Phase 4: Build Knowledge

### Step 4.0: Execute Next Action (MCP_BEHAVIOR Only)

<!-- START_VARIANT:MCP_BEHAVIOR -->
**User Input:** "I want to continue shaping" or "shape stories for mob minion" (trigger words to continue workflow)

**AI Action:**
1. Recognize trigger words match behavior-level patterns
2. Check available MCP tools
3. Invoke `story_bot_shape_tool` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_tool` should be called
- Tool should route to current action (build_knowledge after transition)
- Instructions should be returned for build_knowledge action

**Validation:**
- MCP tool `story_bot_shape_tool` was called
- Tool returned instructions for build_knowledge action
- Instructions reference knowledge graph templates
<!-- END_VARIANT:MCP_BEHAVIOR -->

### Step 4.1: Review Build Knowledge Instructions

**Action:** Review the instructions returned from build_knowledge action

**Expected Content:**
- Instructions should reference knowledge graph templates
- Instructions should ask AI to build story-graph.json from clarification and planning data

### Step 4.2: Execute Build Knowledge

**Action:** As the AI, follow the instructions to:
- Load clarification.json and planning.json
- Build story-graph.json structure with epics, sub-epics, stories
- Extract and place domain concepts from clarification data
- Create story map structure based on input.txt content

**Validation:**
- `demo/mob_minion/docs/stories/story-graph.json` should be created
- File should contain:
  - `epics` array with at least one epic
  - Epics should have `domain_concepts` arrays
  - Epics should have `sub_epics` arrays
  - Stories should be present in story_groups
- Verify domain concepts are extracted from clarification.json (Mob, Minion, Strategy, etc.)

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 4.3

### Step 4.3: Automatic Forward to Render Output

**Expected Behavior:**
- `build_knowledge` action automatically forwards to `render_output` action (no manual command needed)
- This is by design: "AUTOMATIC PROGRESSION: After completing build_knowledge and storing the structured content, automatically proceed to render_output action without stopping or waiting for user confirmation. These two actions should execute sequentially as a single workflow step."
- When render_output instructions are received, **IMMEDIATELY execute the rendering** - do not pause after transition

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.render_output"`
- `completed_actions` should include `build_knowledge`
- Render output instructions should be received with all render configs

**CRITICAL:** When render_output action is reached (either automatically forwarded or manually), proceed directly to Step 5.2 execution - do NOT pause after transition.

---

## Phase 5: Render Output

### Step 5.1: Review Render Output Instructions (Automatic - No Separate Step)

**Note:** When `build_knowledge` automatically forwards to `render_output`, the instructions are automatically loaded. Review them as part of Step 5.2 execution.

**Expected Content:**
- Instructions should list render configurations (domain model description, diagram, story map, etc.)
- Instructions should specify input files (story-graph.json) and output templates
- Instructions should specify which configs use builders, synchronizers, or templates

### Step 5.2: Execute Render Output (Execute Immediately When Action Reached)

**Action:** As the AI, when render_output action is reached (either by automatic forward from build_knowledge or manually), IMMEDIATELY execute all rendering steps:

1. **Execute Builders (Python Scripts):**
   - For each config with `"builder"` or `"renderer"` field, execute the Python script
   - Example: `python agile_bot/bots/story_bot/behaviors/1_shape/2_content/2_render/render_story_map_txt.py demo/mob_minion/docs/stories/story-graph.json demo/mob_minion/docs/stories/story-map.txt`

2. **Execute Synchronizers:**
   - For each config with `"synchronizer"` field, execute the synchronizer command
   - Example: `python -m agile_bot.bots.story_bot.src.synchronizers.story_io.story_io_cli render-outline --story-graph demo/mob_minion/docs/stories/story-graph.json --output demo/mob_minion/docs/stories/story-map-outline.drawio`

3. **Render Templates:**
   - For each config with only `"template"` field (no builder/synchronizer), render template directly
   - Load story-graph.json and clarification.json
   - Render domain model description using template
   - Render domain model diagram using template

**CRITICAL:** Do NOT pause after receiving render_output instructions - execute all rendering steps immediately, then pause for validation.

**Validation:**
- `demo/mob_minion/docs/stories/mob-minion-domain-model-description.md` should be created
- `demo/mob_minion/docs/stories/mob-minion-domain-model-diagram.md` should be created
- `demo/mob_minion/docs/stories/story-map.txt` should be created (or similar)
- Verify domain concepts from story-graph.json appear in rendered outputs
- Verify NO OSAP examples appear in domain model description (this was a previous bug)

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 5.3

### Step 5.3: Make a Change to Test Synchronize

**Action:** Make a deliberate change to one of the rendered files:
- Example: Edit `mob-minion-domain-model-description.md` and add a test comment or modify a description
- Or: Edit `story-graph.json` and change a story name slightly

**Validation:**
- Change should be visible in the file
- Note what change was made for next step

### Step 5.4: Test Synchronize (if applicable)

**Action:** If render_output instructions mention synchronize functionality:
- Review synchronize instructions
- Execute synchronize to bring changes back into story-graph.json (if change was made to rendered file)
- OR execute synchronize to update rendered files (if change was made to story-graph.json)

**Validation:**
- If synchronized, verify the change propagated correctly
- Files should be in sync after synchronization

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 5.5

### Step 5.5: Continue to Next Action (Variant-Specific)

<!-- START_VARIANT:CLI_BEHAVIOR -->
**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `validate_rules` action
- Instructions should be returned for validation

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.validate_rules"`
- `completed_actions` should include `render_output`
<!-- END_VARIANT:CLI_BEHAVIOR -->

<!-- START_VARIANT:CLI_ACTION -->
**Command:** `/story_bot-shape validate_rules`

**Expected Behavior:**
- Command should execute `validate_rules` action directly
- Instructions should be returned for validation

**Validation:**
- Instructions should be returned for validation
- Action executed directly
<!-- END_VARIANT:CLI_ACTION -->

<!-- START_VARIANT:MCP_BEHAVIOR -->
**AI Action:** After completing render_output, invoke `story_bot_close_current_action` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_close_current_action` should be called
- Tool should mark render_output as complete
- Tool should transition workflow to `validate_rules` action
- Tool should NOT execute the next action - it only marks complete and transitions

**Validation:**
- MCP tool `story_bot_close_current_action` was called
- `workflow_state.json` should show: `current_action: "story_bot.shape.validate_rules"`
- `completed_actions` should include `render_output`
- No instructions returned (tool only transitions, doesn't execute)

**Next Step:** To actually execute the next action, call the behavior tool again using trigger words (e.g., "I want to continue shaping")
<!-- END_VARIANT:MCP_BEHAVIOR -->

<!-- START_VARIANT:MCP_ACTION -->
**User Input:** "validate rules" or "check against rules" (matches trigger patterns from `base_actions/7_validate_rules/trigger_words.json`)

**AI Action:**
1. Recognize trigger words match action-level patterns ("check.*against.*rule", "validate.*content", "verify.*compliance")
2. Check available MCP tools
3. Invoke `story_bot_shape_validate_rules` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_validate_rules` should be called
- Tool should execute validate_rules action directly
- Instructions should be returned for validation

**Validation:**
- MCP tool `story_bot_shape_validate_rules` was called
- Tool executed validate_rules action
- Instructions should be returned for validation
<!-- END_VARIANT:MCP_ACTION -->

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 6.0

---

## Phase 6: Validate Rules

### Step 6.0: Execute Next Action (MCP_BEHAVIOR Only)

<!-- START_VARIANT:MCP_BEHAVIOR -->
**User Input:** "I want to continue shaping" or "shape stories for mob minion" (trigger words to continue workflow)

**AI Action:**
1. Recognize trigger words match behavior-level patterns
2. Check available MCP tools
3. Invoke `story_bot_shape_tool` MCP tool

**Expected Behavior:**
- MCP tool `story_bot_shape_tool` should be called
- Tool should route to current action (validate_rules after transition)
- Instructions should be returned for validate_rules action

**Validation:**
- MCP tool `story_bot_shape_tool` was called
- Tool returned instructions for validate_rules action
- Instructions are actionable (not just raw rules)
<!-- END_VARIANT:MCP_BEHAVIOR -->

### Step 6.1: Review Validate Rules Instructions

**Action:** Review the instructions returned from validate_rules action

**Expected Content:**
- Instructions should be PRIMARY (actionable steps), not just rules
- Instructions should tell AI to:
  1. Load clarification.json and planning.json
  2. Check content against rules
  3. Generate validation report
  4. **Save report to file at report_path**
- `content_to_validate` should include `report_path` pointing to `validation-report.md`

**Validation:**
- Instructions structure should have:
  - `base_instructions` (primary - list of instruction strings)
  - `validation_rules` (supporting context - list of rules)
  - `content_to_validate.report_path` (path where to save report)
- Instructions should NOT just be raw rules - they should be actionable

### Step 6.2: Execute Validation

**Action:** As the AI, follow the instructions to:
1. Load clarification.json and planning.json
2. Load story-graph.json and rendered outputs
3. Check content against all validation rules
4. Identify violations (naming format, typos, etc.)
5. Generate validation report with:
   - Status (completed with violations / all passed)
   - List of violations found
   - Specific examples from content
   - Suggested corrections
   - Requirements verification
6. **SAVE the report to the file specified in report_path**

**Validation:**
- `demo/mob_minion/docs/stories/validation-report.md` should be created
- Report should contain:
  - Summary section
  - Violations found (if any)
  - Requirements verification
  - Suggested corrections
- Report should be properly formatted markdown
- File should exist at the exact path specified in `content_to_validate.report_path`

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 6.3

### Step 6.3: Verify Workflow Completion

**Action:** Check that validate_rules is the terminal action

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.validate_rules"`
- `completed_actions` should include all actions: initialize_project, gather_context, decide_planning_criteria, build_knowledge, render_output, validate_rules
- No next action should be available (terminal action)

**PAUSE MODE:** After validation, report completion and wait for user confirmation before proceeding to Step 7.1

---

## Phase 7: Final Validation

**Action:** Check that all expected files exist:

**Required Files:**
- `demo/mob_minion/docs/stories/clarification.json`
- `demo/mob_minion/docs/stories/planning.json`
- `demo/mob_minion/docs/stories/story-graph.json`
- `demo/mob_minion/docs/stories/mob-minion-domain-model-description.md`
- `demo/mob_minion/docs/stories/mob-minion-domain-model-diagram.md`
- `demo/mob_minion/docs/stories/validation-report.md`
- `demo/mob_minion/workflow_state.json`
- `agile_bot/bots/story_bot/current_project.json`

**Validation:**
- All files should exist
- All files should have content (not empty)
- Files should be properly formatted (JSON should be valid, Markdown should be readable)

### Step 7.2: Verify Workflow State

**Action:** Check workflow_state.json

**Validation:**
- `current_behavior` should be `"story_bot.shape"`
- `current_action` should be `"story_bot.shape.validate_rules"`
- `completed_actions` should contain all 6 actions in order
- Each completed action should have a timestamp

### Step 7.3: Verify Content Quality

**Action:** Spot-check content quality:

**Story-Graph Validation:**
- Should have at least one epic (e.g., "Manage Mobs")
- Epics should have domain_concepts
- Stories should use verb-noun format
- Sequential order should be present

**Domain Model Validation:**
- Domain concepts should match clarification.json
- Descriptions should use ubiquitous language
- NO OSAP examples should appear

**Validation Report Validation:**
- Should list violations found (if any)
- Should reference clarification.json and planning.json
- Should provide specific corrections

**CRITICAL: PHASE 7 IS THE END OF THE WORKFLOW**
- **After Phase 7 is complete, the shaping workflow is DONE**
- **If user says "continue" after Phase 7, respond with "Done" - do NOT proceed to Phase 8 or any other steps**
- **Done means done - the workflow ends here**

---

## Phase 8: Test Edge Cases (OPTIONAL - Only if explicitly requested)

**NOTE: Phase 7 is the end of the main shaping workflow. Phase 8 is optional edge case testing. If the user says "continue" after Phase 7 is complete, respond with "Done" - do NOT automatically proceed to Phase 8.**

### Step 8.1: Test Workflow Resume After Interruption

**Action:** 
1. Note the current workflow state
2. Simulate an interruption (don't actually interrupt, just verify the state would allow resume)
3. Verify that running the entry point again would resume at the correct action

**Validation:**
- Workflow state should be sufficient to resume
- Current action should be clear from workflow_state.json
- Entry point (CLI command or MCP tool) should correctly resume workflow

### Step 8.2: Test Activity Logging

**Action:** Check activity_log.json (if it exists)

**Validation:**
- Should have entries for each action executed
- Entries should have action_state, timestamp, status
- Completion entries should have outputs

---

## Success Criteria

The workflow test is successful if:

1. ✅ All phases completed without errors
2. ✅ All required files created in correct locations
3. ✅ Workflow state properly maintained throughout
4. ✅ Instructions are actionable (not just raw rules) at each step
5. ✅ Validation report is saved to file
6. ✅ Content quality is acceptable (domain concepts present, stories follow format)
7. ✅ Synchronize functionality works (if tested)
8. ✅ Workflow can be resumed from any point
9. ✅ Variant-specific entry points work correctly (CLI vs MCP, behavior vs action level)

---

## Final Report Format (Straight-Through Mode Only)

When running in Straight-Through mode, provide a comprehensive report at the end with:

### Executive Summary
- Total phases completed: X/7
- Total steps completed: X
- Variant tested: {{VARIANT}}
- Overall status: Success / Partial Success / Failed
- Total execution time: [if tracked]

### Phase-by-Phase Results

For each phase (0-7):
- **Phase X: [Name]**
  - Status: ✅ Completed / ⚠️ Partial / ❌ Failed
  - Steps completed: X/Y
  - Files created: [list]
  - Validation results: [pass/fail for each check]
  - Issues encountered: [if any]
  - Variant-specific notes: [if applicable]

### Files Created

Complete list of all files created with paths:
- `demo/mob_minion/docs/stories/clarification.json` - ✅ Created, validated
- `demo/mob_minion/docs/stories/planning.json` - ✅ Created, validated
- [etc.]

### Validation Summary

- Total validation checks: X
- Passed: X
- Failed: X
- Issues: [list of any failures]

### Workflow State

Final state of `workflow_state.json`:
- Current behavior: [value]
- Current action: [value]
- Completed actions: [list]
- Timestamps: [if relevant]

### Variant-Specific Results

- Entry points tested: [list]
- MCP tools invoked: [list] (if MCP variant)
- Trigger words matched: [list] (if MCP variant)
- CLI commands executed: [list] (if CLI variant)

### Recommendations

- Any issues that need attention
- Suggestions for improvement
- Next steps if workflow needs to be rerun

---

## Notes for AI Executing This Test

- **Follow instructions sequentially** - each phase builds on the previous
- **Validate after each step** - don't proceed if validation fails
- **Simulate human-in-the-loop** - when instructions say "present to user" or "ask user", simulate providing reasonable answers based on input.txt
- **Check file contents** - don't just check files exist, verify they have correct content
- **Report issues** - if any step fails, document what failed and why
- **Use commands/tools exactly as specified** - follow variant-specific instructions

**CRITICAL: WHEN WORKFLOW IS DONE, SAY "DONE"**
- **When Phase 7 (Final Validation) is complete, the workflow is DONE**
- **If user says "continue" after workflow is complete, respond with "Done" - do NOT look for additional steps or phases**
- **Do NOT try to find "next steps" or "Phase 8" or additional validation when the workflow is complete**
- **Done means done - stop and report completion, do not continue**
- **The shaping workflow ends at Phase 7 - validate_rules is the terminal action**

**CRITICAL: NO WORKAROUNDS OR FIXES**
- **DO NOT create temporary scripts, wrappers, or workarounds** when commands fail
- **DO NOT fix system bugs** - this is a test of existing functionality, not a development session
- **If a command fails:**
  1. Report the exact error message
  2. Report what command was attempted
  3. Report what the expected behavior was
  4. **STOP and wait for user direction**
- **The goal is to test the system as-is** - creating workarounds defeats the purpose of the test
- **If something doesn't work, that's valuable test information** - document it and stop

### Variant-Specific Instructions

**For CLI Variants:**
- Use exact CLI commands as specified
- Verify commands execute correctly
- Check that workflow state updates appropriately

**For MCP Variants:**
- **CRITICAL:** Before invoking MCP tools, check available MCP tools first
- Recognize trigger words from the trigger word patterns listed above
- Invoke the correct MCP tool based on trigger words
- Verify MCP tool was called and returned expected results
- **For MCP_BEHAVIOR:** The flow is:
  1. Execute action (via behavior tool with trigger words like "shape stories for mob minion" or "I want to continue shaping")
  2. Complete the action work (follow instructions, create files, etc.)
  3. Call `story_bot_close_current_action` to mark action complete and transition to next action (this does NOT execute the next action)
  4. Call behavior tool again with trigger words to actually execute the next action
  5. Repeat steps 2-4
- **For MCP_ACTION:** Use specific action tools for each phase (each action is executed directly via its action tool)

### Mode-Specific Behavior

**Straight-Through Mode:**
- Execute all steps without pausing
- Collect validation results as you go
- At the end, provide comprehensive report covering all phases
- Report should include: summary, files created, validation results, any issues, final state, variant-specific results

**Pause Mode:**
- After EACH step marked with "PAUSE MODE", you MUST:
  1. Report step completion with the format shown above
  2. Show what was created/changed
  3. Show validation results
  4. Explicitly state you are waiting for user confirmation
  5. DO NOT proceed until user explicitly confirms (e.g., "proceed", "continue", "next", "yes")
- User may ask questions or request changes between steps - handle those before proceeding

---

## Command Reference

### CLI Commands
- `/story_bot-shape @demo/mob_minion/input.txt` - Start shape workflow with input file (CLI_BEHAVIOR)
- `/story_bot-shape initialize_project @demo/mob_minion/input.txt` - Execute specific action (CLI_ACTION)
- `/story_bot-shape` - Resume shape workflow (uses current project from state)
- `/story_bot-continue` - Close current action and continue to next (CLI_BEHAVIOR)
- `python agile_bot/bots/story_bot/src/story_bot_cli.py shape` - Direct CLI invocation
- `python agile_bot/bots/story_bot/src/story_bot_cli.py --close` - Close current action

### MCP Tools
- `story_bot_tool` - Bot-level tool (routes to current behavior/action)
- `story_bot_close_current_action` - Close current action and transition (MCP_BEHAVIOR)
- `story_bot_shape_tool` - Behavior-level tool (routes to current action in shape) (MCP_BEHAVIOR)
- `story_bot_shape_initialize_project` - Action-level tool (MCP_ACTION)
- `story_bot_shape_gather_context` - Action-level tool (MCP_ACTION)
- `story_bot_shape_decide_planning` - Action-level tool (MCP_ACTION)
- `story_bot_shape_build_knowledge` - Action-level tool (MCP_ACTION)
- `story_bot_shape_render_output` - Action-level tool (MCP_ACTION)
- `story_bot_shape_validate_rules` - Action-level tool (MCP_ACTION)

---

**End of Instructions**
