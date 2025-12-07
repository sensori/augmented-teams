# 📝 Store Context Files

**Navigation:** [📋 Story Map](story-map-outline.drawio) | [⚙️ Feature Overview](../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Init Project

**User:** Bot-Behavior  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Initialize Project Action creates a standardized `context/` folder at `{project_area}/docs/context/` immediately after project area is confirmed. All original context providers, input files, prompts, and source material are stored in this folder. Generated files (clarification.json, planning.json) are stored in `{project_area}/docs/stories/` along with other generated artifacts.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** initialize_project action confirms project area location
- **THEN** initialize_project creates `{project_area}/docs/context/` folder
- **WHEN** user provides input file via `@input.txt` or similar
- **THEN** initialize_project copies input file to `{project_area}/docs/context/input.txt`
- **WHEN** user provides context in conversation
- **THEN** initialize_project saves context to `{project_area}/docs/context/initial-context.md` or similar
- **WHEN** gather_context action stores clarification data
- **THEN** gather_context saves to `{project_area}/docs/stories/clarification.json` (in docs_path, NOT in context folder)
- **WHEN** decide_planning_criteria action stores planning decisions
- **THEN** decide_planning_criteria saves to `{project_area}/docs/stories/planning.json` (in docs_path, NOT in context folder)
- **WHEN** build_knowledge action loads context
- **THEN** build_knowledge loads original input from `{project_area}/docs/context/` folder (input.txt)
- **AND** build_knowledge loads generated files from `{project_area}/docs/stories/` folder (clarification.json, planning.json)
- **WHEN** render_output action loads context
- **THEN** render_output loads original input from `{project_area}/docs/context/` folder (input.txt)
- **AND** render_output loads generated files from `{project_area}/docs/stories/` folder (clarification.json, planning.json)
- **WHEN** any action needs original context files
- **THEN** action references `{project_area}/docs/context/` folder for original input files
- **WHEN** any action needs generated context files
- **THEN** action references `{project_area}/docs/stories/` folder for generated files (clarification.json, planning.json)

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given workspace root exists
And project area location is confirmed
And initialize_project action has executed
```

## Scenarios

### Scenario: Initialize project creates context folder

**Steps:**
```gherkin
Given user confirms project area location
When initialize_project action completes
Then {project_area}/docs/context/ folder exists
And context folder is empty (ready for original context files)
```

### Scenario: Initialize project copies input file to context folder

**Steps:**
```gherkin
Given user provides input file via @input.txt command
And input file exists at original location
When initialize_project action executes
Then initialize_project copies input file to {project_area}/docs/context/input.txt
And original input file remains at original location (copy, not move)
And {project_area}/docs/context/input.txt exists and contains original content
```

### Scenario: Initialize project saves conversation context to context folder

**Steps:**
```gherkin
Given user provides context in conversation (not via file)
When initialize_project action executes
Then initialize_project saves conversation context to {project_area}/docs/context/initial-context.md
And initial-context.md contains the conversation context provided by user
```

### Scenario: Gather context saves clarification to docs/stories folder

**Steps:**
```gherkin
Given context folder exists at {project_area}/docs/context/
And gather_context action has collected key questions and evidence
When gather_context action stores clarification data
Then gather_context saves to {project_area}/docs/stories/clarification.json
And clarification.json is saved in docs_path (NOT in context folder)
And clarification.json contains behavior-specific key_questions and evidence structure
```

### Scenario: Decide planning criteria saves planning to docs/stories folder

**Steps:**
```gherkin
Given context folder exists at {project_area}/docs/context/
And decide_planning_criteria action has collected assumptions and decisions
When decide_planning_criteria action stores planning data
Then decide_planning_criteria saves to {project_area}/docs/stories/planning.json
And planning.json is saved in docs_path (NOT in context folder)
And planning.json contains behavior-specific assumptions_made and decisions_made structure
```

### Scenario: Build knowledge loads context from correct locations

**Steps:**
```gherkin
Given context folder exists with input.txt
And clarification.json and planning.json exist in docs/stories/
When build_knowledge action executes
Then build_knowledge loads {project_area}/docs/stories/clarification.json
And build_knowledge loads {project_area}/docs/stories/planning.json
And build_knowledge loads {project_area}/docs/context/input.txt
And build_knowledge incorporates all context into generated content
```

### Scenario: Render output loads context from correct locations

**Steps:**
```gherkin
Given context folder exists with input.txt
And clarification.json and planning.json exist in docs/stories/
When render_output action executes
Then render_output loads {project_area}/docs/stories/clarification.json
And render_output loads {project_area}/docs/stories/planning.json
And render_output loads {project_area}/docs/context/input.txt
And render_output reflects context in all rendered artifacts
```

### Scenario: Context folder is universal across all bots and behaviors

**Steps:**
```gherkin
Given any bot (story_bot, base_bot, etc.) initializes project
When initialize_project action executes
Then context folder is created at {project_area}/docs/context/
And context folder structure is identical regardless of bot or behavior
And all actions reference context folder using same path pattern (docs/context/ for original input, docs/stories/ for generated files)
```

### Scenario: Context folder handles missing files gracefully

**Steps:**
```gherkin
Given context folder exists at {project_area}/docs/context/
And some context files are missing (e.g., input.txt not provided)
When action attempts to load context files
Then action checks for file existence before loading
And action handles missing files gracefully (skips or uses defaults)
And action does NOT fail if optional context files are missing
```

