# 📝 System Validates Range Constraints Using Foundry Movement System

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** System
**Sequential Order:** 7
**Story Type:** system

## Story Description

System Validates Range Constraints Using Foundry Movement System functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** target is selected
  **then** system queries Foundry VTT movement system for range between minion and target
  **and** system compares range to action type range requirements

- **When** range validation succeeds
  **then** system confirms action can proceed
  **and** system stores range validation result

- **When** range validation fails
  **then** system shows error message indicating range constraint violation
  **and** system prevents action execution

## Scenarios

### Scenario: Range validation succeeds (happy_path)

**Steps:**
```gherkin
Given target is selected
And Foundry VTT movement system is available
When system queries Foundry VTT movement system for range between minion and target
Then system compares range to action type range requirements
And system confirms action can proceed
And system stores range validation result
```


### Scenario: Range validation fails (error_case)

**Steps:**
```gherkin
Given target is selected
And Foundry VTT movement system is available
And range exceeds action type range requirements
When system queries Foundry VTT movement system for range between minion and target
And system compares range to action type range requirements
Then system shows error message indicating range constraint violation
And system prevents action execution
```

