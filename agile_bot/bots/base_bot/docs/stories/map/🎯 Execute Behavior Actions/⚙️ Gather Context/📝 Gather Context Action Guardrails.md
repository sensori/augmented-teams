# 📝 Gather Context Action Guardrails

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Gather Context
**User:** Bot Behavior
**Sequential Order:** 1
**Story Type:** user

## Story Description

Gather Context Action Guardrails functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** gather_context action executes

  **and** behavior folder exists with guardrails/required_context/key_questions.json

  **and** behavior folder exists with guardrails/required_context/evidence.json

  **then** instructions should contain actual questions (not {{key_questions}} placeholder)

  **and** instructions should contain actual evidence (not {{evidence}} placeholder)

- **When** guardrails don't exist

  **then** gather_context should not fail

  **and** action should execute with base instructions only

## Scenarios

### Scenario: Gather context injects guardrails from behavior folder (happy_path)

**Steps:**
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


### Scenario: Gather context handles missing guardrails gracefully (happy_path)

**Steps:**
```gherkin
GIVEN: behavior folder exists but no guardrails
WHEN: gather_context action executes
THEN: action should succeed without guardrails
AND: instructions contain base instructions only
AND: no error is raised
```

