# [Story] Gather Context Action Guardrails

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Gather Context
**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Gather Context Action Guardrails functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN gather_context action executes**
- **AND behavior folder exists with guardrails/required_context/key_questions.json**
- **AND behavior folder exists with guardrails/required_context/evidence.json**
- **THEN instructions should contain actual questions (not {{key_questions}} placeholder)**
- **AND instructions should contain actual evidence (not {{evidence}} placeholder)**
- **WHEN guardrails don't exist**
- **THEN gather_context should not fail**
- **AND action should execute with base instructions only**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Gather context injects guardrails from behavior folder

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


### Scenario: Gather context handles missing guardrails gracefully

**Steps:**
```gherkin
GIVEN: behavior folder exists but no guardrails
WHEN: gather_context action executes
THEN: action should succeed without guardrails
AND: instructions contain base instructions only
AND: no error is raised
```


