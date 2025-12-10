# 📝 System Applies Action To Each Minion Via Foundry VTT API

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** System
**Sequential Order:** 5
**Story Type:** system

## Story Description

System Applies Action To Each Minion Via Foundry VTT API functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** minion data is retrieved
  **then** system applies selected action to each minion via Foundry VTT combat API
  **and** system tracks action execution status for each minion

- **When** action application succeeds for minion
  **then** system marks minion as action executed
  **and** system updates minion state in Foundry VTT

- **When** action application fails for minion
  **then** system shows error message for that minion
  **and** system continues with remaining minions

## Scenarios

### Scenario: System applies action to all minions successfully (happy_path)

**Steps:**
```gherkin
Given minion data is retrieved
And Foundry VTT combat API is available
When system applies selected action to each minion via Foundry VTT combat API
Then system tracks action execution status for each minion
And system marks minion as action executed
And system updates minion state in Foundry VTT
```


### Scenario: Action application fails for one minion (error_case)

**Steps:**
```gherkin
Given minion data is retrieved
And Foundry VTT combat API is available
And one minion action application will fail
When system applies selected action to each minion via Foundry VTT combat API
And action application fails for one minion
Then system shows error message for that minion
And system continues with remaining minions
```

