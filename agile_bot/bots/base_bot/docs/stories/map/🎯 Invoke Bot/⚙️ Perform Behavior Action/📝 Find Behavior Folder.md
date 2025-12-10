# 📝 Find Behavior Folder

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Perform Behavior Action
**User:** Bot Behavior
**Sequential Order:** 7
**Story Type:** user

## Story Description

Find Behavior Folder functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** : find_behavior_folder is called with behavior name

  **then** : Returns path to behavior folder with number prefix if it exists

  **and** : Handles various behavior folder naming patterns

## Scenarios

### Scenario: Find behavior folder with number prefix (happy_path)

**Steps:**
```gherkin
GIVEN: Behavior folder exists with number prefix (8_tests)
WHEN: find_behavior_folder is called with behavior name without prefix (tests)
THEN: Returns path to numbered folder (8_tests)
```


### Scenario: Find shape folder with number prefix (happy_path)

**Steps:**
```gherkin
GIVEN: Behavior folder exists as 1_shape
WHEN: find_behavior_folder is called with 'shape'
THEN: Returns path to 1_shape folder
```


### Scenario: Raises error when behavior folder not found (happy_path)

**Steps:**
```gherkin
GIVEN: Behavior folder does NOT exist
WHEN: find_behavior_folder is called
THEN: Raises appropriate error
```

