# 📝 System Validates Action Type

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** System
**Sequential Order:** 2
**Story Type:** system

## Story Description

System Validates Action Type functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action type is selected
  **then** system validates action type is valid for mob
  **and** system checks action type is available in Foundry VTT combat system

- **When** action type is invalid
  **then** system shows error message and clears action selection

- **When** action type is not available in Foundry VTT
  **then** system shows error message indicating action is not available

## Scenarios

### Scenario: System validates action type successfully (happy_path)

**Steps:**
```gherkin
Given action type is selected
And Foundry VTT combat system is available
When system validates action type
Then system validates action type is valid for mob
And system checks action type is available in Foundry VTT combat system
```


### Scenario: Action type is invalid (error_case)

**Steps:**
```gherkin
Given action type is selected
And action type is invalid for mob
When system validates action type
Then system shows error message
And system clears action selection
```


### Scenario: Action type is not available in Foundry VTT (error_case)

**Steps:**
```gherkin
Given action type is selected
And action type is not available in Foundry VTT combat system
When system validates action type
Then system shows error message indicating action is not available
```

