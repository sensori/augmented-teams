# 📝 Store Context Files

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Init Project
**User:** Bot Behavior
**Sequential Order:** 1.7
**Story Type:** user

## Story Description

Store Context Files functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** initialize_project action confirms project area location

  **then** initialize_project creates {project_area}/docs/context/ folder and {project_area}/docs/stories/ folder

- **When** user provides input file via @input.txt or similar

  **then** initialize_project copies input file to {project_area}/docs/context/input.txt

- **When** user provides context in conversation

  **then** initialize_project saves context to {project_area}/docs/context/initial-context.md or similar

- **When** gather_context action stores clarification data

  **then** gather_context saves to {project_area}/docs/stories/clarification.json (generated file, NOT in context folder)

- **When** decide_planning_criteria action stores planning decisions

  **then** decide_planning_criteria saves to {project_area}/docs/stories/planning.json (generated file, NOT in context folder)

- **When** build_knowledge action loads context

  **then** build_knowledge loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)

- **When** render_output action loads context

  **then** render_output loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)

- **When** any action needs context files

  **then** action references original input from {project_area}/docs/context/ folder and generated files from {project_area}/docs/stories/ folder

## Scenarios

### Scenario: Store Context Files (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
