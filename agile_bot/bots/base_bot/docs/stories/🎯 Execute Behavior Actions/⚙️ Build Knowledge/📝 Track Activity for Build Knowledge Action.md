# 📝 Track Activity for Build Knowledge Action

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Build Knowledge

**User:** Behavior  
**Sequential Order:** 3  
**Story Type:** user

**Test File:** test_build_knowledge.py  
**Test Class:** TestTrackActivityForBuildKnowledgeAction

## Story Description

When Build Knowledge Action executes, the action creates activity entries with timestamps, action name, and behavior name. These entries are appended to the activity log at the project area, providing a record of when knowledge building activities occur and what inputs/outputs they process.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** BuildKnowledgeAction executes
- **THEN** Action creates activity entry with timestamp, action name, behavior name
- **AND** Activity entry appended to {project_area}/activity_log.json

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Build Knowledge Action is initialized with bot_name and behavior
And project_area is available
And activity log exists or will be created
```

## Scenarios

### Scenario: Track activity when build_knowledge action starts

**Test Method:** `test_track_activity_when_build_knowledge_action_starts`

**Steps:**
```gherkin
Given behavior is 'scenarios'
And action is 'build_knowledge'
When build_knowledge action starts execution
Then Activity logger creates entry with:
  - timestamp=[start timestamp]
  - action_state='story_bot.scenarios.build_knowledge'
  - inputs={criteria_count: 4, assumptions_count: 2, context_file_path: "planning.json"}
And Entry is appended to activity log at project_area/
And Activity log records action initiation
```

### Scenario: Track activity when build_knowledge action completes

**Test Method:** `test_track_activity_when_build_knowledge_action_completes`

**Steps:**
```gherkin
Given build_knowledge action started at timestamp='2025-12-03T10:30:00Z'
And activity log has entry for build_knowledge
When build_knowledge action finishes execution at timestamp='2025-12-03T10:50:00Z'
Then Activity logger creates completion entry with:
  - action_state='story_bot.scenarios.build_knowledge'
  - outputs={concepts_count: 15, relationships_count: 30, rules_count: 8, file_path: "knowledge_graph.json"}
  - duration=1200 (seconds: 20 minutes)
And Entry is appended to activity log
And Activity log shows complete execution record with duration
```

### Scenario: Track knowledge building inputs from previous actions

**Steps:**
```gherkin
Given gather_context outputs are available in clarifications.json
And decide_planning_criteria outputs are available in planning.json  
And behavior is 'scenarios'
When build_knowledge action starts
Then Activity logger captures inputs including:
  - context_from="gather_context and decide_planning_criteria"
  - questions_count=5
  - criteria_count=4
  - assumptions_count=2
And Inputs show connection to previous actions
And Activity log traces workflow dependencies
```

### Scenario: Track knowledge graph outputs

**Steps:**
```gherkin
Given build_knowledge action is complete
And Knowledge graph contains: 15 concepts, 30 relationships, 8 rules
When Activity logger records completion
Then Activity logger captures outputs including:
  - concepts_count=15
  - relationships_count=30
  - rules_count=8
  - file_path="knowledge_graph.json"
  - summary="Built domain knowledge graph for increment 3"
And Outputs capture counts and file paths, not full graph content
And Activity log shows metrics of what knowledge artifacts were produced
```

### Scenario: Activity log maintains sequence through build_knowledge

**Steps:**
```gherkin
Given activity log contains entries for:
  - gather_context (completed at 10:05:30)
  - decide_planning_criteria (completed at 10:25:00)
And build_knowledge completes at 10:50:00
When Activity logger appends build_knowledge entry
Then Activity log shows chronological sequence:
  1. gather_context (10:00:00 - 10:05:30)
  2. decide_planning_criteria (10:15:00 - 10:25:00)
  3. build_knowledge (10:30:00 - 10:50:00)
And Activity log demonstrates workflow progression through knowledge building
```

## Test Details

- **Test File:** `test_build_knowledge.py`
- **Test Class:** `TestTrackActivityForBuildKnowledgeAction`
- **Test Methods:**
  - `test_track_activity_when_build_knowledge_action_starts` - Tests activity tracking when action starts
  - `test_track_activity_when_build_knowledge_action_completes` - Tests activity tracking when action completes

## Implementation Notes

The Build Knowledge Action tracks activity by:
1. Creating activity entries when the action starts execution
2. Capturing inputs from previous actions (gather_context, decide_planning_criteria)
3. Recording outputs including knowledge graph metrics (concepts, relationships, rules counts)
4. Appending entries to the activity log at the project area
5. Maintaining chronological sequence of workflow activities

Activity entries include:
- Timestamps for start and completion
- Action state (full path: bot_name.behavior.action)
- Inputs (criteria count, assumptions count, context file paths)
- Outputs (knowledge graph metrics, file paths)
- Duration (calculated from start to completion timestamps)

The activity log provides a traceable record of the knowledge building process, showing dependencies between actions and metrics of what was produced.
