# 📝 Select Multiple Tokens

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Multiple Tokens functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects multiple minion tokens on Foundry canvas

  **then** Foundry Token API returns array of selected token objects

- **When** Game Master selects zero tokens

  **then** system shows error message indicating at least one token must be selected

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Foundry VTT session is active
And minion tokens exist on Foundry canvas
```

## Scenarios

### Scenario: Game Master selects multiple tokens successfully (happy_path)

**Steps:**
```gherkin
When Game Master selects "<token_count>" minion tokens on Foundry canvas
Then Foundry Token API returns array of "<token_count>" selected token objects
And each token object contains token ID and actor ID
```

**Examples:**
| token_count |
| --- |
| 2 |
| 5 |
| 10 |


### Scenario: Game Master selects zero tokens (error_case)

**Steps:**
```gherkin
When Game Master selects zero tokens
Then system shows error message indicating at least one token must be selected
```

