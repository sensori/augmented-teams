# 📝 Spawn Mob From Template

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Spawn Mobs
**Feature:** Spawn From Template
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Spawn Mob From Template functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master spawns mob from template (happy_path)

**Steps:**
```gherkin
Given mob template is selected
And Foundry VTT scene is available
When Game Master confirms spawning mob from template
Then system creates mob from template configuration
And system spawns minion tokens on Foundry VTT scene
And system creates Mob domain object with spawned minions
```


### Scenario: Template spawning fails (error_case)

**Steps:**
```gherkin
Given mob template is selected
And Foundry VTT scene is unavailable or fails
When Game Master attempts to spawn mob from template
Then system shows error message indicating spawning failed
```

