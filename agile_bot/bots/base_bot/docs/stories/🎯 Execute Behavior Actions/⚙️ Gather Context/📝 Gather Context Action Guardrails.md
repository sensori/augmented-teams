# 📝 Gather Context Action Guardrails

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Gather Context

**User:** Bot Behavior  
**Sequential Order:** 2.5  
**Story Type:** system  
**Test File:** test_gather_context_action.py

## Story Description

Tests that gather_context action properly injects guardrails (key_questions and evidence) from behavior folder. The action should load guardrails from `behavior/guardrails/required_context/` and inject them into instructions, replacing placeholders with actual content.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** gather_context action executes
- **AND** behavior folder exists with guardrails/required_context/key_questions.json
- **AND** behavior folder exists with guardrails/required_context/evidence.json
- **THEN** instructions should contain actual questions (not {{key_questions}} placeholder)
- **AND** instructions should contain actual evidence (not {{evidence}} placeholder)
- **WHEN** guardrails don't exist
- **THEN** gather_context should not fail
- **AND** action should execute with base instructions only

## Scenarios

### Scenario: Gather context injects guardrails from behavior folder

**Test Method:** `test_gather_context_injects_guardrails_from_behavior_folder`

```gherkin
GIVEN: behavior folder: 1_shape (with number prefix)
AND: guardrails/required_context/key_questions.json exists
AND: guardrails/required_context/evidence.json exists
WHEN: gather_context action executes
THEN: instructions should contain actual questions (not {{key_questions}} placeholder)
AND: instructions should contain actual evidence (not {{evidence}} placeholder)
AND: guardrails section includes key_questions with actual data
AND: guardrails section includes evidence with actual data
```

### Scenario: Gather context handles missing guardrails gracefully

**Test Method:** `test_gather_context_handles_missing_guardrails_gracefully`

```gherkin
GIVEN: behavior folder exists but no guardrails
WHEN: gather_context action executes
THEN: action should succeed without guardrails
AND: instructions contain base instructions only
AND: no error is raised
```
