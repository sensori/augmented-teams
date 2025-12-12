# 📝 Determine Target From Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Execute Mob Actions
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Determine Target From Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** mob action is initiated

  **then** system uses mob's assigned strategy to determine target

- **When** target is determined

  **then** system selects appropriate enemy based on strategy rules using Foundry combat system

## Scenarios

### Scenario: System determines target using assigned strategy (happy_path)

**Steps:**
```gherkin
Given Foundry VTT session is active
And mob exists with assigned strategy
And combat encounter has <enemy_count> enemies available
And Foundry combat system is active
When mob action is initiated
Then system uses mob's assigned "<strategy_type>" strategy to determine target
When target is determined
Then system selects appropriate enemy based on strategy rules using Foundry combat system
And selected target matches strategy criteria
```

**Examples:**
| enemy_count | strategy_type |
| --- | --- |
| 2 | AttackMostPowerful |
| 3 | AttackWeakest |
| 5 | AttackMostDamaged |


### Scenario: System uses default strategy when no strategy assigned (edge_case)

**Steps:**
```gherkin
Given Foundry VTT session is active
And mob exists without assigned strategy
And combat encounter has enemies available
And Foundry combat system is active
When mob action is initiated
Then system uses default strategy (nearest enemy or first available target)
When target is determined
Then system selects appropriate enemy based on default strategy rules using Foundry combat system
```

