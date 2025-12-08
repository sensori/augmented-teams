# [Story] Track Activity for Planning Action

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Decide Planning Criteria Action
**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Track Activity for Planning Action functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN PlanningAction executes**
- **THEN Action creates activity entry with timestamp, action name, behavior name**
- **AND Activity entry appended to {project_area}/activity_log.json**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Track activity when planning action starts

**Steps:**
```gherkin
Given behavior is 'exploration'
And action is 'decide_planning_criteria'
When decide_planning_criteria action starts execution
Then Activity logger creates entry with:
  - timestamp=[start timestamp]
  - action_state='story_bot.exploration.decide_planning_criteria'
  - inputs={questions_count: 5, evidence_count: 3, context_file_path: "clarifications.json"}
And Entry is appended to activity log at project_area/
And Activity log records action initiation
```


### Scenario: Track activity when planning action completes

**Steps:**
```gherkin
Given decide_planning_criteria action started at timestamp='2025-12-03T10:15:00Z'
And activity log has entry for decide_planning_criteria
When decide_planning_criteria action finishes execution at timestamp='2025-12-03T10:25:00Z'
Then Activity logger creates completion entry with:
  - action_state='story_bot.exploration.decide_planning_criteria'
  - outputs={criteria_count: 4, assumptions_count: 2, decisions_count: 3, file_path: "planning.json"}
  - duration=600 (seconds: 10 minutes)
And Entry is appended to activity log
And Activity log shows complete execution record with duration
```


