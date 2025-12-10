# 📝 Assign Mob Name

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 5
**Story Type:** user

## Story Description

Assign Mob Name functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master enters mob name
  **then** system validates name is not empty
  **and** system checks name uniqueness against existing mobs

- **When** mob name is empty
  **then** system shows error message requiring non-empty name

- **When** mob name already exists
  **then** system shows error message indicating name must be unique

- **When** mob name is valid and unique
  **then** system assigns name to Mob object

## Scenarios

### Scenario: Game Master enters valid and unique mob name (happy_path)

**Steps:**
```gherkin
Given Mob domain object is created
And Mob object contains collection of Minion objects
When Game Master enters mob name
Then system validates name is not empty
And system checks name uniqueness against existing mobs
And system assigns name to Mob object
```


### Scenario: Game Master enters empty mob name (error_case)

**Steps:**
```gherkin
Given Mob domain object is created
And Mob object contains collection of Minion objects
When Game Master enters empty mob name
Then system shows error message requiring non-empty name
```


### Scenario: Game Master enters duplicate mob name (error_case)

**Steps:**
```gherkin
Given Mob domain object is created
And Mob object contains collection of Minion objects
And existing mob with same name already exists
When Game Master enters mob name that already exists
Then system shows error message indicating name must be unique
```

