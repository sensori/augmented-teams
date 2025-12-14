# Orphaned Story Matches - Increments to Epics

## Increment 1: Simplest MCP - Orphaned Stories

### Potential Matches:

1. **"Speaks Trigger Words For Bot Tool"** (orphaned)
   → **"Detect Trigger Words Through Extension"** (in epics, not in increments)
   - Match: Both about trigger words detection

2. **"Injects Instructions"** (orphaned)
   → **"Provide Behavior Action Instructions"** (in epics, not in increments)
   → **"Behavior Action Instructions"** (in epics, not in increments)
   - Match: Both about providing/injecting instructions

3. **"Folllows Injected Instructions"** (orphaned)
   → No direct match, but conceptually related to following instructions

4. **"Injects Gather Context Instructions"** (orphaned)
   → **"Track Activity for Gather Context Action"** (in epics, not in increments)
   - Match: Both related to Gather Context action

5. **"Inject Common Bot Rules Instructions"** (orphaned)
   → **"Inject Validation Rules for Validate Rules Action"** (in epics, not in increments)
   - Match: Both about injecting rules/instructions

6. **"Inject Behavior Specific Rules Instructions"** (orphaned)
   → **"Inject Validation Rules for Validate Rules Action"** (in epics, not in increments)
   - Match: Both about injecting rules

7. **"Validate Content vs Injected Diagnostics and Rules"** (orphaned)
   → **"Complete Validate Rules Action"** (in epics, not in increments)
   → **"Run Diagnostics + inject Results"** (in epics, not in increments)
   - Match: Both about validation and diagnostics

8. **"Track Activity for Correct-Bot Action"** (orphaned)
   → **"Track Activity for Gather Context Action"** (in epics, not in increments)
   → **"Track Activity for Planning Action"** (in epics, not in increments)
   → **"Track Activity for Build Knowledge Action"** (in epics, not in increments)
   → **"Track Activity for Render Output Action"** (in epics, not in increments)
   → **"Track Activity for Validate Rules Action"** (in epics, in increments)
   - Match: Pattern matches other "Track Activity" stories

9. **"Route To Behavior Action"** (orphaned)
   → **"Bot Tool Invocation"** (in epics, not in increments)
   - Match: Both about routing/invoking actions

10. **"Forward To Behavior Action"** (orphaned)
    → **"Forward To Current Behavior and Current Action"** (in epics, in increments)
    → **"Forward To Current Action"** (in epics, not in increments)
    - Match: Very similar naming

11. **"Invoke Action In Behavior"** (orphaned)
    → **"Bot Tool Invocation"** (in epics, not in increments)
    - Match: Both about invoking actions

---

## Increment 2: Workflow - Orphaned Stories

1. **"Generate Bot Tools"** (orphaned)
   → **"Generate MCP Bot Server"** (in epics, in increments)
   → **"Generate Behavior Action Tools"** (in epics, in increments)
   → **"Generate BOT CLI code"** (in epics, not in increments)
   → **"Generate Cursor Command Files"** (in epics, not in increments)
   - Match: Pattern matches other "Generate" stories

2. **"Generate Behavior Tools"** (orphaned)
   → **"Generate Behavior Action Tools"** (in epics, in increments)
   - Match: Very similar name

3. **"Route To MCP Behavior Tool"** (orphaned)
   → **"Bot Tool Invocation"** (in epics, not in increments)
   - Match: Both about routing/invoking tools

4. **"Forward To Behavior and Current Action"** (orphaned)
   → **"Forward To Current Behavior and Current Action"** (in epics, in increments)
   → **"Forward To Current Action"** (in epics, not in increments)
   - Match: Very similar name

5. **"Inject Next behavor-Action to Instructions"** (orphaned)
   → **"Inject Planning Criteria Into Instructions"** (in epics, not in increments)
   → **"Inject Knowledge Graph Template and Builder Instructions"** (in epics, not in increments)
   → **"Inject Template Instructions"** (in epics, not in increments)
   → **"Inject Synchronizer Instructions"** (in epics, not in increments)
   → **"Load+ Inject Content Into Instructions"** (in epics, not in increments)
   - Match: Pattern matches other "Inject...Into Instructions" stories

6. **"Saves Behavior State"** (orphaned)
   → **"Save Knowledge Graph"** (in epics, not in increments)
   → **"Save Content"** (in epics, in increments)
   → **"Save Final Assumptions and Decisions"** (in epics, not in increments)
   - Match: Pattern matches other "Save" stories

7. **"Call Correct-Bot Action Tool"** (orphaned)
   → **"Bot Tool Invocation"** (in epics, not in increments)
   - Match: Both about calling/invoking tools

8. **"Submit Content to Tool for Saving"** (orphaned)
   → **"Save Through MCP"** (in epics, not in increments)
   → **"Save Through CLI"** (in epics, not in increments)
   - Match: Both about saving content

---

## Increment 3: Inject Content - Orphaned Stories

1. **"Route To MCP BotTool"** (orphaned)
   → **"Bot Tool Invocation"** (in epics, not in increments)
   - Match: Both about routing/invoking tools

2. **"InjectsContent Into Instructions"** (orphaned)
   → **"Load+ Inject Content Into Instructions"** (in epics, not in increments)
   - Match: Very similar name (typo difference: "InjectsContent" vs "Inject Content")

3. **"Follows Enriched Instructions"** (orphaned)
   → No direct match, but conceptually related to following instructions

4. **"Inject Load Bot and Rules In Instructions"** (orphaned)
   → **"Load + Inject  Guardrails"** (in epics, not in increments)
   → **"Load + Inject Knolwedge Graph"** (in epics, not in increments)
   → **"Load+ Inject Content Into Instructions"** (in epics, not in increments)
   - Match: Pattern matches other "Load + Inject" stories

5. **"Read Instructions Injected Structured Content"** (orphaned)
   → **"Load+ Inject Content Into Instructions"** (in epics, not in increments)
   - Match: Both about content in instructions

---

## Increment 4: Save Content - Orphaned Stories

1. **"Persists Content"** (orphaned)
   → **"Save Content"** (in epics, in increments)
   → **"Save Knowledge Graph"** (in epics, not in increments)
   → **"Save Through MCP"** (in epics, not in increments)
   → **"Save Through CLI"** (in epics, not in increments)
   - Match: Pattern matches other "Save" stories

2. **"Submit Content Changes to Tools for Saving"** (orphaned)
   → **"Save Through MCP"** (in epics, not in increments)
   → **"Save Through CLI"** (in epics, not in increments)
   - Match: Both about saving through tools

3. **"Submit Answers and Evidence to Tools for Saving"** (orphaned)
   → **"Saves Answers and Evidence"** (in epics, in increments)
   → **"Save Through MCP"** (in epics, not in increments)
   → **"Save Through CLI"** (in epics, not in increments)
   - Match: Related to saving answers/evidence

4. **"Load + Inject Diagnostics Results, Knowledge, Content Instructions"** (orphaned)
   → **"Run Diagnostics + inject Results"** (in epics, not in increments)
   → **"Load + Inject  Guardrails"** (in epics, not in increments)
   → **"Load + Inject Knolwedge Graph"** (in epics, not in increments)
   → **"Load+ Inject Content Into Instructions"** (in epics, not in increments)
   - Match: Pattern matches other "Load + Inject" stories

5. **"Validate Content Using Injected Diagnostics + Rules"** (orphaned)
   → **"Complete Validate Rules Action"** (in epics, not in increments)
   → **"Run Diagnostics + inject Results"** (in epics, not in increments)
   → **"Inject Validation Rules for Validate Rules Action"** (in epics, not in increments)
   - Match: Both about validation with diagnostics/rules

---

## Stories in Epics NOT in Increments (Potential Replacements)

### Build Agile Bots Epic:
- Store Context Files (in epics, not in increments)
- Stores Activity for Initialize Project Action (in epics, not in increments)
- Restart MCP Server To Load Code Changes (in epics, not in increments)
- Generate BOT CLI code (in epics, not in increments)
- Generate Cursor Command Files (in epics, not in increments)

### Invoke Bot Epic:
- Initialize Project Creates Context Folder (in epics, not in increments)
- Input File Copied To Context Folder (in epics, not in increments)
- Guards Prevent Writes Without Project (in epics, not in increments)
- Bot Tool Invocation (in epics, not in increments)
- Behavior Action Instructions (in epics, not in increments)
- Forward To Current Action (in epics, not in increments)
- Save Through MCP (in epics, not in increments)
- Invoke Bot CLI (in epics, not in increments)
- Invoke Bot Behavior CLI (in epics, not in increments)
- Invoke Bot Behavior Action CLI (in epics, not in increments)
- Get Help for Command Line Functions (in epics, not in increments)
- Detect Trigger Words Through Extension (in epics, not in increments)
- Save Through CLI (in epics, not in increments)
- Close Current Action (in epics, not in increments)
- Complete Workflow Integration (in epics, not in increments)
- Provide Behavior Action Instructions (in epics, not in increments)
- Activity Tracker Guard (in epics, not in increments)
- Workflow Guard (in epics, not in increments)
- Activity Tracking Location (in epics, not in increments)
- Find Behavior Folder (in epics, not in increments)

### Execute Behavior Actions Epic:
- Track Activity for Gather Context Action (in epics, not in increments)
- Proceed To Decide Planning (in epics, not in increments)
- Gather Context Saves To Context Folder (in epics, not in increments)
- Load + Inject  Guardrails (in epics, not in increments)
- Gather Context Action Guardrails (in epics, not in increments)
- Inject Planning Criteria Into Instructions (in epics, not in increments)
- Track Activity for Planning Action (in epics, not in increments)
- Proceed To Build Knowledge (in epics, not in increments)
- Save Final Assumptions and Decisions (in epics, not in increments)
- Inject Knowledge Graph Template and Builder Instructions (in epics, not in increments)
- Track Activity for Build Knowledge Action (in epics, not in increments)
- Proceed To Render Output (in epics, not in increments)
- Load + Inject Knolwedge Graph (in epics, not in increments)
- Save Knowledge Graph (in epics, not in increments)
- Load Render Configurations (in epics, not in increments)
- Inject Template Instructions (in epics, not in increments)
- Inject Synchronizer Instructions (in epics, not in increments)
- Track Activity for Render Output Action (in epics, not in increments)
- Load+ Inject Content Into Instructions (in epics, not in increments)
- Proceed To Validate Rules (in epics, not in increments)
- Complete Validate Rules Action (in epics, not in increments)
- Inject Validation Rules for Validate Rules Action (in epics, not in increments)
- System Discovers Scanners from rule.json (in epics, not in increments)
- System Runs Scanners After Build Knowledge (in epics, not in increments)
- Scanner Detects Violations Using Regex Patterns (in epics, not in increments)
- System Collects Violations from All Scanners (in epics, not in increments)
- System Loads Scanner Classes (in epics, not in increments)
- System Runs Scanners After Render Output (in epics, not in increments)
- Scanner Detects Violations Using AST Parsing (in epics, not in increments)
- System Reports Violations with Location Context (in epics, not in increments)
- System Runs Scanners Before AI Validation (in epics, not in increments)
- Scanner Detects Violations Using File Structure Analysis (in epics, not in increments)
- Run Diagnostics + inject Results (in epics, not in increments)

