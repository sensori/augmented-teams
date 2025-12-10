# 📝 Query Foundry VTT For Selected Tokens

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** System
**Sequential Order:** 2
**Story Type:** system

## Story Description

Query Foundry VTT For Selected Tokens functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** tokens are selected
  **then** system queries Foundry VTT API for token actor data
  **and** system retrieves actor ID, name, and position for each selected token

- **When** Foundry VTT API returns invalid token data
  **then** system shows error message and excludes invalid tokens from selection

- **When** Foundry VTT API is unavailable
  **then** system shows error message indicating connection failure

## Scenarios

### Scenario: System queries Foundry VTT API successfully (happy_path)

**Steps:**
```gherkin
Given tokens are selected
And Foundry VTT API is available
When system queries Foundry VTT API for token actor data
Then system retrieves actor ID, name, and position for each selected token
```


### Scenario: Foundry VTT API returns invalid token data (error_case)

**Steps:**
```gherkin
Given tokens are selected
And Foundry VTT API is available
When Foundry VTT API returns invalid token data
Then system shows error message
And system excludes invalid tokens from selection
```


### Scenario: Foundry VTT API is unavailable (error_case)

**Steps:**
```gherkin
Given tokens are selected
And Foundry VTT API is unavailable
When system attempts to query Foundry VTT API
Then system shows error message indicating connection failure
```

