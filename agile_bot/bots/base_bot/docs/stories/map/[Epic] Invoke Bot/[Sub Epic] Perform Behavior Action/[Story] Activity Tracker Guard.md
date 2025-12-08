# [Story] Activity Tracker Guard

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Perform Behavior Action
**User:** Bot Behavior  
**Sequential Order:** 4  
**Story Type:** user

## Story Description

Activity Tracker Guard functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** GIVEN: current_project.json does NOT exist
- **WHEN: ActivityTracker.track_start() is called**
- **THEN: activity_log.json is NOT created**
- **WHEN** GIVEN: current_project.json exists
- **WHEN: ActivityTracker.track_start() is called**
- **THEN: activity_log.json IS created**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Activity not tracked when current_project missing

**Steps:**
```gherkin
GIVEN: current_project.json does NOT exist
WHEN: ActivityTracker.track_start() is called
THEN: activity_log.json is NOT created
```


### Scenario: Activity tracked when current_project exists

**Steps:**
```gherkin
GIVEN: current_project.json exists
WHEN: ActivityTracker.track_start() is called
THEN: activity_log.json IS created
```


