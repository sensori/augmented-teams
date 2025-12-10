# 📝 Activity Tracking Location

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Perform Behavior Action
**User:** Bot Behavior
**Sequential Order:** 6
**Story Type:** user

## Story Description

Activity Tracking Location functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** : Activity is tracked during action execution

  **then** : Activity is logged to project area, not bot area

  **and** : Activity log file is created at {project_area}/activity_log.json

## Scenarios

### Scenario: Activity logged to project area not bot area (happy_path)

**Steps:**
```gherkin
GIVEN: Bot is initialized with current_project set
AND: Project area is 'test_project'
WHEN: Action executes and tracks activity
THEN: activity_log.json is created at test_project/activity_log.json
AND: activity_log.json is NOT created at bot area
```

