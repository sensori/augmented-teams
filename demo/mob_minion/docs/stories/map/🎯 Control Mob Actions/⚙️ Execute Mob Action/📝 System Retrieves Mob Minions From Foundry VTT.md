# 📝 System Retrieves Mob Minions From Foundry VTT

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** System
**Sequential Order:** 4
**Story Type:** system

## Story Description

System Retrieves Mob Minions From Foundry VTT functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action execution is confirmed
  **then** system queries Foundry VTT API for all minion tokens in mob
  **and** system retrieves actor ID and position for each minion

- **When** Foundry VTT API returns invalid minion data
  **then** system shows error message and excludes invalid minions from action execution

- **When** Foundry VTT API is unavailable
  **then** system shows error message indicating connection failure

## Scenarios

### Scenario: System retrieves minion data successfully (happy_path)

**Steps:**
```gherkin
Given action execution is confirmed
And Foundry VTT API is available
When system queries Foundry VTT API for all minion tokens in mob
Then system retrieves actor ID and position for each minion
```


### Scenario: Foundry VTT API returns invalid minion data (error_case)

**Steps:**
```gherkin
Given action execution is confirmed
And Foundry VTT API is available
When Foundry VTT API returns invalid minion data
Then system shows error message
And system excludes invalid minions from action execution
```


### Scenario: Foundry VTT API is unavailable (error_case)

**Steps:**
```gherkin
Given action execution is confirmed
And Foundry VTT API is unavailable
When system attempts to query Foundry VTT API
Then system shows error message indicating connection failure
```

