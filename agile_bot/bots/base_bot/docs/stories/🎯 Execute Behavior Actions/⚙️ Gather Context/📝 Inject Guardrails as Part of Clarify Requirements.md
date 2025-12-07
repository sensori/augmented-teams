# 📝 Inject Guardrails as Part of Clarify Requirements

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Gather Context

**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** system

**Test File:** test_gather_context.py  
**Test Class:** TestInjectGuardrailsAsPartOfClarifyRequirements

## Story Description

When the MCP Specific Behavior Action Tool invokes Gather Context Action, the action checks for guardrails in the behavior's guardrails folder and injects them into the clarify requirements section if they exist.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Gather Context Action
- **THEN** Action checks for guardrails in behavior/guardrails/required_context/
- **WHEN** guardrails exist, **THEN** Action loads key_questions.json and evidence.json
- **AND** Action injects guardrails into clarify requirements section

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Gather Context Action is initialized with bot_name and behavior
And behavior folder structure exists
```

## Scenarios

### Scenario: Action injects guardrails when they exist

**Test Method:** `test_action_injects_questions_and_evidence`

**Steps:**
```gherkin
Given behavior folder exists with guardrails in behavior/guardrails/required_context/
And key_questions.json exists
And evidence.json exists
When Gather Context Action executes
Then Action checks for guardrails in behavior/guardrails/required_context/
And Action loads key_questions.json
And Action loads evidence.json
And Action injects guardrails into clarify requirements section
```

### Scenario: Action continues when guardrails do not exist

**Test Method:** `test_action_uses_base_instructions_when_guardrails_missing`

**Steps:**
```gherkin
Given behavior folder exists without guardrails in behavior/guardrails/required_context/
When Gather Context Action executes
Then Action checks for guardrails
And Action continues execution without guardrails
```

### Scenario: Action handles malformed guardrails json

**Test Method:** `test_action_handles_malformed_guardrails_json`

**Steps:**
```gherkin
Given behavior folder exists with guardrails in behavior/guardrails/required_context/
And key_questions.json contains invalid JSON
When Gather Context Action attempts to load guardrails
Then Action raises JSONDecodeError
```

## Implementation Notes

The Gather Context Action checks for guardrails in `behavior/guardrails/required_context/` and loads:
- `key_questions.json` - Contains key questions to guide context gathering
- `evidence.json` - Contains evidence requirements

These guardrails are then injected into the clarify requirements section of the instructions provided to the AI.
