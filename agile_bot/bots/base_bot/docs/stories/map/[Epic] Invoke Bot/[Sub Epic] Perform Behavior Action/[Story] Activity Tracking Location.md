# [Story] Activity Tracking Location

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Perform Behavior Action
**User:** Bot Behavior  
**Sequential Order:** 6  
**Story Type:** user

## Story Description

Activity Tracking Location functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN: Activity is tracked during action execution**
- **THEN: Activity is logged to project area, not bot area**
- **AND: Activity log file is created at {project_area}/activity_log.json**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Activity logged to project area not bot area

**Steps:**
```gherkin
GIVEN: Bot is initialized with current_project set
AND: Project area is 'test_project'
WHEN: Action executes and tracks activity
THEN: activity_log.json is created at test_project/activity_log.json
AND: activity_log.json is NOT created at bot area
```


