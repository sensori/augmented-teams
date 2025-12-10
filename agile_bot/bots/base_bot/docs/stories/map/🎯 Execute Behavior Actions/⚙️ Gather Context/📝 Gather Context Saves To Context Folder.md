# 📝 Gather Context Saves To Context Folder

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Gather Context
**User:** Bot Behavior
**Sequential Order:** 4
**Story Type:** user

## Story Description

Gather Context Saves To Context Folder functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

  **and** : gather_context action has collected key questions and evidence

- **When** : gather_context action stores clarification data

  **then** : gather_context saves to {project_area}/docs/stories/clarification.json

  **and** : clarification.json is NOT saved to {project_area}/docs/context/clarification.json

  **and** : clarification.json contains behavior-specific key_questions and evidence structure

## Scenarios

### Scenario: Gather context saves clarification to docs/stories folder (happy_path)

**Steps:**
```gherkin
GIVEN: context folder exists at {project_area}/docs/context/
AND: gather_context action has collected key questions and evidence
WHEN: gather_context action stores clarification data
THEN: gather_context saves to {project_area}/docs/stories/clarification.json
AND: clarification.json is NOT saved to {project_area}/docs/context/clarification.json
AND: clarification.json contains behavior-specific key_questions and evidence structure
```

