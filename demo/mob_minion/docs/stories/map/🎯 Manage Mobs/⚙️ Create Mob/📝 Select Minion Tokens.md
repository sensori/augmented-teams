# 📝 Select Minion Tokens

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Minion Tokens functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects one or more minion tokens in Foundry VTT
  **then** system highlights selected tokens
  **and** selected tokens are stored in temporary selection state

- **When** Game Master selects zero tokens
  **then** system shows error message indicating at least one token must be selected

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Foundry VTT is running
And Game Master has minion tokens available on the scene
```

## Scenarios

### Scenario: Game Master selects minion tokens (happy_path)

**Steps:**
```gherkin
When Game Master selects one or more minion tokens in Foundry VTT
Then system highlights selected tokens
And selected tokens are stored in temporary selection state
```


### Scenario: Game Master selects zero tokens (error_case)

**Steps:**
```gherkin
When Game Master selects zero tokens
Then system shows error message indicating at least one token must be selected
```

