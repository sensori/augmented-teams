# Shaping Workflow End-to-End Test Instructions

**Purpose:** This file contains step-by-step instructions for an AI to execute and validate the entire shaping workflow for the mob_minion project.

**Project Location:** `demo/mob_minion/`

**Important:** This is a TEST workflow. A backup has been created. Follow these instructions exactly to validate the entire shaping process works correctly.

---

## Phase 0: Cleanup and Preparation

### Step 0.1: Delete All Generated Files (Keep Only input.txt)

**Action:** Delete all files and directories EXCEPT `input.txt`:
- Delete: `docs/` directory (and all contents)
- Delete: `workflow_state.json`
- Delete: `activity_log.json`
- Keep: `input.txt` (this is the source material)

**Validation:** 
- Verify only `input.txt` remains in `demo/mob_minion/`
- Verify `docs/` directory does not exist

---

## Phase 1: Initialize Project

### Step 1.1: Run Shape Command

**Command:** `/story_bot-shape @demo/mob_minion/input.txt`

**Expected Behavior:**
- Command should forward to `initialize_project` action
- Instructions should ask to confirm project location

**Validation:**
- Instructions received should specify project location: `demo/mob_minion/`
- Instructions should ask for confirmation

### Step 1.2: Confirm Project Location

**Action:** Follow the instructions to confirm the project location is `demo/mob_minion/`

**Validation:**
- `agile_bot/bots/story_bot/current_project.json` should be created
- File should contain: `{"current_project": "C:\\dev\\augmented-teams\\demo\\mob_minion"}`

### Step 1.3: Continue to Next Action

**Command:** `/story_bot-continue` (or use `--close` flag)

**Expected Behavior:**
- Workflow should transition to `gather_context` action
- Instructions should be returned for gathering context

**Validation:**
- `demo/mob_minion/workflow_state.json` should be created
- State should show: `current_action: "story_bot.shape.gather_context"`
- Instructions should contain key questions to ask

---

## Phase 2: Gather Context

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

### Step 2.3: Continue to Next Action

**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `decide_planning_criteria` action
- Instructions should be returned for planning

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.decide_planning_criteria"`
- `completed_actions` should include `gather_context`

---

## Phase 3: Decide Planning Criteria

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

### Step 3.3: Continue to Next Action

**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `build_knowledge` action
- Instructions should be returned for building knowledge graph

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.build_knowledge"`
- `completed_actions` should include both `gather_context` and `decide_planning_criteria`

---

## Phase 4: Build Knowledge

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

### Step 4.3: Continue to Next Action

**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `render_output` action
- Instructions should be returned for rendering outputs

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.render_output"`
- `completed_actions` should include `build_knowledge`

---

## Phase 5: Render Output

### Step 5.1: Review Render Output Instructions

**Action:** Review the instructions returned from render_output action

**Expected Content:**
- Instructions should list render configurations (domain model description, diagram, story map, etc.)
- Instructions should specify input files (story-graph.json) and output templates

### Step 5.2: Execute Render Output

**Action:** As the AI, follow the instructions to:
- Load story-graph.json
- Render domain model description using template
- Render domain model diagram using template
- Render story map files (markdown, text, drawio)

**Validation:**
- `demo/mob_minion/docs/stories/mob-minion-domain-model-description.md` should be created
- `demo/mob_minion/docs/stories/mob-minion-domain-model-diagram.md` should be created
- `demo/mob_minion/docs/stories/story-map.txt` should be created (or similar)
- Verify domain concepts from story-graph.json appear in rendered outputs
- Verify NO OSAP examples appear in domain model description (this was a previous bug)

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

### Step 5.5: Continue to Next Action

**Command:** `/story_bot-continue`

**Expected Behavior:**
- Workflow should transition to `validate_rules` action
- Instructions should be returned for validation

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.validate_rules"`
- `completed_actions` should include `render_output`

---

## Phase 6: Validate Rules

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

### Step 6.3: Verify Workflow Completion

**Action:** Check that validate_rules is the terminal action

**Validation:**
- `workflow_state.json` should show: `current_action: "story_bot.shape.validate_rules"`
- `completed_actions` should include all actions: initialize_project, gather_context, decide_planning_criteria, build_knowledge, render_output, validate_rules
- No next action should be available (terminal action)

---

## Phase 7: Final Validation

### Step 7.1: Verify All Files Created

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

---

## Phase 8: Test Edge Cases

### Step 8.1: Test Workflow Resume After Interruption

**Action:** 
1. Note the current workflow state
2. Simulate an interruption (don't actually interrupt, just verify the state would allow resume)
3. Verify that running `/story_bot-shape` again would resume at the correct action

**Validation:**
- Workflow state should be sufficient to resume
- Current action should be clear from workflow_state.json

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

---

## Notes for AI Executing This Test

- **Follow instructions sequentially** - each phase builds on the previous
- **Validate after each step** - don't proceed if validation fails
- **Simulate human-in-the-loop** - when instructions say "present to user" or "ask user", simulate providing reasonable answers based on input.txt
- **Check file contents** - don't just check files exist, verify they have correct content
- **Report issues** - if any step fails, document what failed and why
- **Use commands exactly as specified** - `/story_bot-shape`, `/story_bot-continue`, etc.

---

## Command Reference

- `/story_bot-shape @demo/mob_minion/input.txt` - Start shape workflow with input file
- `/story_bot-shape` - Resume shape workflow (uses current project from state)
- `/story_bot-continue` - Close current action and continue to next
- `python agile_bot/bots/story_bot/src/story_bot_cli.py shape` - Direct CLI invocation
- `python agile_bot/bots/story_bot/src/story_bot_cli.py --close` - Close current action

---

**End of Instructions**

