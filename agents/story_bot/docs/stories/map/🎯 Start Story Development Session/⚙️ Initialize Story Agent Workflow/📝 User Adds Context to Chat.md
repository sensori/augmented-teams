# 📝 User Adds Context to Chat

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../initialize-workflow-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Initialize Story Agent Workflow

## Story Description

User adds documents, models, text descriptions, diagrams to Cursor/VS Code chat window and requests to start shaping/planning/building a new project

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When user selects and attaches documents, models, or diagrams to Cursor/VS Code chat window, then system receives context and stores location/path and purpose of each context item to docs/provide_context.json (not the actual file content)
- When user provides textual description as context in Cursor/VS Code chat window, then system stores the actual text content and purpose to docs/provide_context.json (since there is no file to reference)
- When user types request message in chat window (e.g., 'start shaping', 'plan new project', 'build story map'), then AI Chat receives and processes the request

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Cursor/VS Code chat window is open
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Scenarios

### Scenario Outline: User attaches documents and requests story shaping

**Steps:**
```gherkin
Given user has documents available: "<document_paths>"
When user selects and attaches documents to chat window
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1417)
And user types request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1535)
Then system receives context and stores location/path and purpose of each context item to docs/provide_context.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1429)
And docs/provide_context.json contains context entries: "<expected_context_entries>"
And AI Chat receives and processes the request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1436)
```

**Examples:**
| document_paths | request_message | expected_context_entries |
|----------------|-----------------|-------------------------|
| docs/requirements.md | start shaping | [{"type":"file","path":"docs/requirements.md","purpose":"requirements document"}] |
| models/user-model.json,docs/architecture.md | plan new project | [{"type":"file","path":"models/user-model.json","purpose":"user model"},{"type":"file","path":"docs/architecture.md","purpose":"architecture document"}] |
| diagrams/system-flow.png | build story map | [{"type":"file","path":"diagrams/system-flow.png","purpose":"system flow diagram"}] |
```

### Scenario Outline: User attaches multiple document types

**Steps:**
```gherkin
When user attaches markdown document at "<markdown_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1442)
And user attaches JSON model file at "<json_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1450)
And user types request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1535)
Then system stores location/path and purpose of each attached file to docs/provide_context.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1464)
And docs/provide_context.json contains context entries: "<expected_context_entries>"
And AI Chat receives and processes the request with all context
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1471)
```

**Examples:**
| markdown_path | json_path | request_message | expected_context_entries |
|--------------|-----------|-----------------|-------------------------|
| docs/requirements.md | models/user-model.json | plan new project | [{"type":"file","path":"docs/requirements.md","purpose":"requirements document"},{"type":"file","path":"models/user-model.json","purpose":"user model"}] |
| README.md | config/settings.json | start shaping | [{"type":"file","path":"README.md","purpose":"readme document"},{"type":"file","path":"config/settings.json","purpose":"settings configuration"}] |
```

### Scenario Outline: User provides textual description as context

**Steps:**
```gherkin
When user types textual description "<textual_description>" as context in chat window
And user types request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1535)
Then system stores actual text content and purpose of textual description to docs/provide_context.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1484)
And docs/provide_context.json contains context entry: "<expected_context_entry>"
And AI Chat receives and processes the request with textual context
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1491)
```

**Examples:**
| textual_description | request_message | expected_context_entry |
|---------------------|-----------------|----------------------|
| This is a project to build a task management system | start shaping | {"type":"text","content":"This is a project to build a task management system","purpose":"project description"} |
| We need to support user authentication and file uploads | plan new project | {"type":"text","content":"We need to support user authentication and file uploads","purpose":"feature requirements"} |
```

### Scenario Outline: User attaches empty or invalid files

**Steps:**
```gherkin
When user attempts to attach file "<file_path>" with error condition "<error_condition>"
And user types request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1535)
Then system handles file attachment error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1516)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And system stores only valid context items to docs/provide_context.json
And docs/provide_context.json contains context entries: "<expected_context_entries>"
And AI Chat receives request with available valid context only
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1529)
```

**Examples:**
| file_path | error_condition | request_message | expected_context_entries |
|-----------|----------------|-----------------|-------------------------|
| docs/empty.txt | empty_file | build story map | [] |
| docs/corrupted.json | corrupted_file | start shaping | [] |
| docs/valid.md,docs/empty.txt | empty_file | plan new project | [{"type":"file","path":"docs/valid.md","purpose":"valid document"}] |
```

### Scenario Outline: User types request without attaching documents

**Steps:**
```gherkin
When user types request message "<request_message>" without attaching any documents
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1535)
Then system creates docs/provide_context.json with empty context list
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1542)
And docs/provide_context.json contains context entries: "<expected_context_entries>"
And AI Chat receives and processes the request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1436)
And system proceeds with story shaping workflow using empty context
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1549)
```

**Examples:**
| request_message | expected_context_entries |
|----------------|-------------------------|
| start shaping | [] |
| plan new project | [] |
| build story map | [] |
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

