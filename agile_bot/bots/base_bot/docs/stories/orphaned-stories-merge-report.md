# Orphaned Stories Merge Report

**Generated:** Analysis of stories in epics section that are NOT assigned to any increment

**Total Orphaned Stories:** 28

## Summary

This report identifies 28 stories that exist in the epics section but are not assigned to any increment. Recommendations are provided for which increment each story should be assigned to based on logical grouping and feature context.

---

## Proposed Increment Assignments

### Increment 1: "Simplest MCP" (Priority 1)
**Current Stories:** 4  
**Proposed Additions:** 1

#### Add to Increment 1:
- **Restart MCP Server To Load Code Changes** (Build Agile Bots | Generate MCP Tools)
  - *Rationale: Related to MCP server deployment and code loading*

---

### Increment 2: "Workflow" (Priority 2)
**Current Stories:** 12  
**Proposed Additions:** 11

#### Add to Increment 2:
- **Initialize Project Creates Context Folder** (Invoke Bot | Init Project)
  - *Rationale: Core initialization workflow functionality*
- **Input File Copied To Context Folder** (Invoke Bot | Init Project)
  - *Rationale: Part of project initialization workflow*
- **Guards Prevent Writes Without Project** (Invoke Bot | Init Project)
  - *Rationale: Safety guard for workflow*
- **Invoke Bot Tool** (Invoke Bot | Invoke MCP)
  - *Rationale: Core MCP invocation for workflow*
- **Load And Merge Behavior Action Instructions** (Invoke Bot | Invoke MCP)
  - *Rationale: Required for workflow execution*
- **Forward To Current Behavior and Current Action** (Invoke Bot | Invoke MCP)
  - *Rationale: Workflow routing*
- **Forward To Current Action** (Invoke Bot | Invoke MCP)
  - *Rationale: Workflow routing*
- **Inject Planning Criteria Into Instructions** (Execute Behavior Actions | Decide Planning Criteria Action)
  - *Rationale: Part of planning workflow*
- **Track Activity for Planning Action** (Execute Behavior Actions | Decide Planning Criteria Action)
  - *Rationale: Activity tracking in workflow*
- **Proceed To Build Knowledge** (Execute Behavior Actions | Decide Planning Criteria Action)
  - *Rationale: Workflow progression*
- **Proceed To Validate Rules** (Execute Behavior Actions | Render Output)
  - *Rationale: Workflow progression after render*

---

### Increment 3: "Save Content" (Priority 3)
**Current Stories:** 0 (Empty)  
**Proposed Additions:** 2

#### Add to Increment 3:
- **Gather Context Action Guardrails** (Execute Behavior Actions | Gather Context)
  - *Rationale: Guardrails for content gathering*
- **Saves Answers and Evidence** (Execute Behavior Actions | Gather Context)
  - *Rationale: Content saving functionality*

---

### Increment 4: "Later" (Priority 4)
**Current Stories:** 0 (Empty)  
**Proposed Additions:** 14

#### Add to Increment 4:
- **Generate BOT CLI code** (Build Agile Bots | Generate CLI)
  - *Rationale: CLI generation - deferred feature*
- **Generate Cursor Command Files** (Build Agile Bots | Generate CLI)
  - *Rationale: CLI generation - deferred feature*
- **Invoke Bot CLI** (Invoke Bot | Invoke CLI)
  - *Rationale: CLI invocation - deferred feature*
- **Invoke Bot Behavior CLI** (Invoke Bot | Invoke CLI)
  - *Rationale: CLI invocation - deferred feature*
- **Invoke Bot Behavior Action CLI** (Invoke Bot | Invoke CLI)
  - *Rationale: CLI invocation - deferred feature*
- **Get Help for Command Line Functions** (Invoke Bot | Invoke CLI)
  - *Rationale: CLI help - deferred feature*
- **Detect Trigger Words Through Extension** (Invoke Bot | Invoke CLI)
  - *Rationale: Extension integration - deferred feature*
- **Close Current Action** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Action management - deferred feature*
- **Complete Workflow Integration** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Workflow integration - deferred feature*
- **Provide Behavior Action Instructions** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Action instructions - deferred feature*
- **Activity Tracker Guard** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Guard functionality - deferred feature*
- **Workflow Guard** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Guard functionality - deferred feature*
- **Activity Tracking Location** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Tracking location - deferred feature*
- **Find Behavior Folder** (Invoke Bot | Perform Behavior Action)
  - *Rationale: Folder discovery - deferred feature*

---

## Increment Summary After Merge

| Increment | Current Stories | Proposed Additions | Total After Merge |
|-----------|----------------|-------------------|-------------------|
| Simplest MCP (1) | 4 | 1 | 5 |
| Workflow (2) | 12 | 11 | 23 |
| Save Content (3) | 0 | 2 | 2 |
| Later (4) | 0 | 14 | 14 |
| Inject / Store Content (5) | 12 | 0 | 12 |
| Code Scanner (6) | 13 | 0 | 13 |
| **TOTAL** | **41** | **28** | **69** |

---

## Stories by Epic/Feature Context

### Build Agile Bots
- **Generate MCP Tools:** 1 orphaned (Restart MCP Server To Load Code Changes)
- **Generate CLI:** 2 orphaned (Generate BOT CLI code, Generate Cursor Command Files)

### Invoke Bot
- **Init Project:** 3 orphaned (Initialize Project Creates Context Folder, Input File Copied To Context Folder, Guards Prevent Writes Without Project)
- **Invoke MCP:** 4 orphaned (Invoke Bot Tool, Load And Merge Behavior Action Instructions, Forward To Current Behavior and Current Action, Forward To Current Action)
- **Invoke CLI:** 5 orphaned (Invoke Bot CLI, Invoke Bot Behavior CLI, Invoke Bot Behavior Action CLI, Get Help for Command Line Functions, Detect Trigger Words Through Extension)
- **Perform Behavior Action:** 7 orphaned (Close Current Action, Complete Workflow Integration, Provide Behavior Action Instructions, Activity Tracker Guard, Workflow Guard, Activity Tracking Location, Find Behavior Folder)

### Execute Behavior Actions
- **Gather Context:** 2 orphaned (Gather Context Action Guardrails, Saves Answers and Evidence)
- **Decide Planning Criteria Action:** 3 orphaned (Inject Planning Criteria Into Instructions, Track Activity for Planning Action, Proceed To Build Knowledge)
- **Render Output:** 1 orphaned (Proceed To Validate Rules)

---

## Recommendations

1. **Increment 2 (Workflow)** should receive the most additions (11 stories) as it contains core workflow functionality
2. **Increment 4 (Later)** should receive CLI and advanced features (14 stories) that can be deferred
3. **Increment 3 (Save Content)** should receive content-related guardrails and saving functionality (2 stories)
4. **Increment 1 (Simplest MCP)** should receive the MCP server restart story (1 story)

---

## Next Steps

1. Review proposed assignments
2. Adjust assignments based on priority and dependencies
3. Update `story-graph.json` increments section with approved assignments
4. Regenerate DrawIO diagram to visualize changes
5. Verify no duplicate story assignments



