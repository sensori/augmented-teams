# 📝 Activity Tracker Guard

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Perform Behavior Action
**User:** Bot Behavior
**Sequential Order:** 4
**Story Type:** user

## Story Description

Activity Tracker Guard functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** : ActivityTracker.track_start() is called

  **then** : activity_log.json is NOT created

- **When** : ActivityTracker.track_start() is called

  **then** : activity_log.json IS created

## Scenarios

### Scenario: Activity not tracked when current_project missing (happy_path)

**Steps:**
```gherkin
GIVEN: current_project.json does NOT exist
WHEN: ActivityTracker.track_start() is called
THEN: activity_log.json is NOT created
```


### Scenario: Activity tracked when current_project exists (happy_path)

**Steps:**
```gherkin
GIVEN: current_project.json exists
WHEN: ActivityTracker.track_start() is called
THEN: activity_log.json IS created
```

