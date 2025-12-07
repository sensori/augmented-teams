# 📝 Inject Validation Rules for Validate Rules Action

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Validate Knowledge & Content Against Rules

**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** system

## Story Description

When the MCP Specific Behavior Action Tool invokes Validate Rules Action, the action loads common bot rules from base_bot/rules/ and behavior-specific rules, then merges and injects them into the validation section.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Validate Rules Action
- **THEN** Action loads common bot rules from base_bot/rules/
- **AND** Action loads behavior-specific rules
- **AND** Action merges and injects rules into validation section

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Validate Rules Action is initialized with bot_name and behavior
And base_bot rules folder exists
And behavior folder structure exists
```

## Scenarios

### Scenario: Action injects merged validation rules

**Steps:**
```gherkin
Given base_bot/rules/ contains common bot rules
And behavior folder contains behavior-specific rules
When Validate Rules Action executes
Then Action loads common bot rules from base_bot/rules/
And Action loads behavior-specific rules
And Action merges common and behavior-specific rules
And Action injects merged rules into validation section
```

### Scenario: Action handles missing rules

**Steps:**
```gherkin
Given base_bot/rules/ exists
And behavior folder does not contain behavior-specific rules
When Validate Rules Action executes
Then Action loads common bot rules from base_bot/rules/
And Action uses only common rules
And Action injects rules into validation section
```

## Implementation Notes

The Validate Rules Action loads and merges:
- Common bot rules from `base_bot/rules/` - Rules that apply to all bots
- Behavior-specific rules - Rules specific to the current behavior

The merged rules are then injected into the validation section of the instructions provided to the AI for validating knowledge and content.
