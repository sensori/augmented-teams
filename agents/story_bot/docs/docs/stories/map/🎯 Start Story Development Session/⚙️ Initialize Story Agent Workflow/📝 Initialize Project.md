# 📝 Initialize Project

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../initialize-workflow-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Initialize Story Agent Workflow

## Story Description

Agent creates Project instance and delegates project area determination to Project. Project determines project_area for new project, presents to user for confirmation, saves to agent_state.json, and completes initialization

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When Agent creates Project for new project, then Agent instantiates Project with agent_name='stories' and optional project_area parameter, and delegates project area determination to Project
- When Project initializes for new project, then Project determines project_area (defaults to current folder name since no state files exist), and presents determined project_area to user for confirmation
- When user confirms or suggests new project area, then Project updates project_area if user suggested different value, saves project_area to agent_state.json in project area, creates necessary directory structure, and completes initialization

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And no agent_state.json files exist in current directory or subdirectories
  [🔗](../../../../../../src/stories_acceptance_tests.py#L421)
```

## Scenarios

### Scenario Outline: Project initializes with default project area

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And no agent_state.json exists in "<test_working_dir>" or subdirectories
When Agent creates Project for new project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L430)
Then Agent instantiates Project with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L438)
And Agent initializes Project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
When Project initializes
  [🔗](../../../../../../src/stories_acceptance_tests.py#L452)
Then Project determines project_area defaults to "<expected_default_project_area>"
And Project presents determined project_area to user for confirmation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L464)
When user confirms project area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L470)
Then Project saves project_area to "<expected_default_project_area>/docs/agent_state.json"
When user suggests different project area "<user_suggested_area>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L518)
Then Project updates project_area to "<user_suggested_area>"
When project area is saved
Then Project creates necessary directory structure at "<final_project_area>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L485)
And Project completes initialization
  [🔗](../../../../../../src/stories_acceptance_tests.py#L493)
```

**Examples:**
| test_working_dir | expected_default_project_area | user_suggested_area | final_project_area |
|------------------|------------------------------|---------------------|-------------------|
| test_data/working_dirs/my-project | test_data/working_dirs/my-project | test_data/projects/my-story-project | test_data/projects/my-story-project |
| test_data/working_dirs/story-dev | test_data/working_dirs/story-dev | test_data/projects/story-dev | test_data/projects/story-dev |

### Scenario Outline: Project area determination with invalid folder name

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And current working directory has invalid condition "<invalid_condition>"
When Project initializes for new project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L452)
And Project attempts to determine project_area from current folder name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L549)
Then Project detects invalid condition "<invalid_condition>"
And Project handles invalid folder name gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L555)
And Project does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L561)
And Project presents error to user or uses safe default "<safe_default>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L567)
And user can provide valid project area "<valid_project_area>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L573)
```

**Examples:**
| test_working_dir | invalid_condition | safe_default | valid_project_area |
|-----------------|-------------------|--------------|-------------------|
| test_data/working_dirs/invalid-chars-<> | invalid_characters | test_data/projects/story-project | test_data/projects/story-project |
| test_data/working_dirs/ | empty_folder_name | test_data/projects/story-project | test_data/projects/story-project |
| test_data/working_dirs/very-long-name-that-exceeds-maximum-path-length-limits | too_long | test_data/projects/story-project | test_data/projects/story-project |

### Scenario: Project fails to save agent_state.json due to permissions

**Steps:**
```gherkin
Given Project has determined project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L579)
And user has confirmed project area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L585)
And project area directory has read-only permissions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L591)
When Project attempts to save project_area to agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L598)
Then Project handles file write permission error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L610)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And appropriate error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1186)
And Project does not complete initialization until file can be written
  [🔗](../../../../../../src/stories_acceptance_tests.py#L622)
```

### Scenario: Project fails to create directory structure

**Steps:**
```gherkin
Given Project has determined project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L579)
And user has confirmed project area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L585)
And project area path is on read-only filesystem
  [🔗](../../../../../../src/stories_acceptance_tests.py#L628)
When Project attempts to create necessary directory structure
  [🔗](../../../../../../src/stories_acceptance_tests.py#L634)
Then Project handles directory creation error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L644)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And appropriate error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1186)
And Project does not complete initialization until directories can be created
  [🔗](../../../../../../src/stories_acceptance_tests.py#L650)
```

### Scenario: Project area already exists with conflicting state

**Steps:**
```gherkin
Given Project has determined project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L579)
And project area directory already exists
  [🔗](../../../../../../src/stories_acceptance_tests.py#L656)
And project area contains agent_state.json with different agent_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L662)
When Project attempts to save project_area to agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L598)
Then Project detects conflicting state file
  [🔗](../../../../../../src/stories_acceptance_tests.py#L671)
And Project handles conflict gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L677)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And Project presents conflict to user for resolution
  [🔗](../../../../../../src/stories_acceptance_tests.py#L683)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

