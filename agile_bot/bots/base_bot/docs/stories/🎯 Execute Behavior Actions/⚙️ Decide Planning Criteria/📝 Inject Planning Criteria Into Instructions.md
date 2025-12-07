# 📝 Inject Planning Criteria Into Instructions

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Decide Planning Criteria Action

**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** system

**Test File:** test_decide_planning_criteria.py  
**Test Class:** TestInjectPlanningCriteriaIntoInstructions

## Story Description

When the MCP Specific Behavior Action Tool invokes Planning Action, the action checks for guardrails in the behavior's planning guardrails folder and injects them into the planning section if they exist.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Planning Action
- **THEN** Action checks for guardrails in behavior/guardrails/planning/
- **WHEN** guardrails exist, **THEN** Action loads typical_assumptions.json and decision_criteria files
- **AND** Action injects planning guardrails into planning section

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Planning Action is initialized with bot_name and behavior
And behavior folder structure exists
```

## Scenarios

### Scenario: Action injects planning guardrails when they exist

**Test Method:** `test_action_injects_decision_criteria_and_assumptions`

**Steps:**
```gherkin
Given behavior folder exists with guardrails in behavior/guardrails/planning/
And typical_assumptions.json exists
And decision_criteria files exist
When Planning Action executes
Then Action checks for guardrails in behavior/guardrails/planning/
And Action loads typical_assumptions.json
And Action loads decision_criteria files
And Action injects planning guardrails into planning section
```

### Scenario: Action continues when planning guardrails do not exist

**Test Method:** `test_action_uses_base_planning_when_guardrails_missing`

**Steps:**
```gherkin
Given behavior folder exists without guardrails in behavior/guardrails/planning/
When Planning Action executes
Then Action checks for guardrails
And Action continues execution without planning guardrails
```

## Implementation Notes

The Planning Action checks for guardrails in `behavior/guardrails/planning/` and loads:
- `typical_assumptions.json` - Contains typical assumptions for planning
- `decision_criteria` files - Contains decision criteria for planning

These guardrails are then injected into the planning section of the instructions provided to the AI.
