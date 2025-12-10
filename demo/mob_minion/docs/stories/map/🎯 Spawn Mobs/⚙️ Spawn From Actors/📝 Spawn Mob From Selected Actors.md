# 📝 Spawn Mob From Selected Actors

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Spawn Mobs
**Feature:** Spawn From Actors
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Spawn Mob From Selected Actors functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master spawns mob from selected actors (happy_path)

**Steps:**
```gherkin
Given Game Master has selected one or more actor tokens
And Foundry VTT scene is available
When Game Master confirms spawning mob from selected actors
Then system creates mob from selected actors
And system creates Mob domain object with selected actors as minions
And system groups actors into mob
```


### Scenario: Game Master selects zero actors (error_case)

**Steps:**
```gherkin
Given Game Master has selected zero actor tokens
When Game Master attempts to spawn mob from selected actors
Then system shows error message indicating at least one actor must be selected
```

