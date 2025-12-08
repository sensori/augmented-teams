# [Story] Store Context Files

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Init Project
**User:** Bot Behavior  
**Sequential Order:** 1.7  
**Story Type:** user

## Story Description

Store Context Files functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN initialize_project action confirms project area location**
- **THEN initialize_project creates {project_area}/docs/context/ folder and {project_area}/docs/stories/ folder**
- **WHEN user provides input file via @input.txt or similar**
- **THEN initialize_project copies input file to {project_area}/docs/context/input.txt**
- **WHEN user provides context in conversation**
- **THEN initialize_project saves context to {project_area}/docs/context/initial-context.md or similar**
- **WHEN gather_context action stores clarification data**
- **THEN gather_context saves to {project_area}/docs/stories/clarification.json (generated file, NOT in context folder)**
- **WHEN decide_planning_criteria action stores planning decisions**
- **THEN decide_planning_criteria saves to {project_area}/docs/stories/planning.json (generated file, NOT in context folder)**
- **WHEN build_knowledge action loads context**
- **THEN build_knowledge loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)**
- **WHEN render_output action loads context**
- **THEN render_output loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)**
- **WHEN any action needs context files**
- **THEN action references original input from {project_area}/docs/context/ folder and generated files from {project_area}/docs/stories/ folder**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Store Context Files

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

