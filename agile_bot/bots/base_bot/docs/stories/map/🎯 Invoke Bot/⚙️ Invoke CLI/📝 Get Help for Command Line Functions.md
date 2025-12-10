# 📝 Get Help for Command Line Functions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke CLI
**User:** Human
**Sequential Order:** 4
**Story Type:** user

## Story Description

Get Help for Command Line Functions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Human executes CLI command with --help-cursor flag (e.g., bot story_bot --help-cursor)

  **then** CLI scans all cursor command files for the bot in .cursor/commands/ directory

  **and** CLI loads behavior instructions from behaviors/{behavior_name}/instructions.json for each behavior command

  **and** CLI extracts meaningful descriptions from behavior instructions (description, goal, outputs - top 2-3 lines about outcomes)

  **and** CLI displays formatted list of all cursor commands with command name, description, and parameters

  **and** CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"

  **and** CLI displays usage instructions at bottom

  **and** Output is shown to user (AI agent displays the help output)

- **When** Human executes CLI command with --help flag (e.g., bot story_bot --help)

  **then** CLI loads all behaviors from bot configuration

  **and** CLI loads behavior instructions from behaviors/{behavior_name}/instructions.json for each behavior

  **and** CLI extracts meaningful descriptions from behavior instructions

  **and** CLI loads action instructions from base_actions/{action_name}/instructions.json for each action

  **and** CLI extracts action descriptions from base_actions instructions

  **and** CLI displays formatted list of all behaviors with behavior name, description, and list of actions

  **and** CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"

  **and** CLI displays usage instructions at bottom

  **and** Output is shown to user (AI agent displays the help output)

  **and** CLI handles missing behavior instructions gracefully with fallback descriptions

## Scenarios

### Scenario: Get help for cursor commands (happy_path)

**Steps:**
```gherkin
Given cursor command files exist for bot in '.cursor/commands'
And behavior instructions exist with description, goal, outputs
When Human executes CLI command 'story_bot --help-cursor'
Then CLI scans cursor command files
And CLI loads behavior instructions
And CLI extracts descriptions from behavior instructions
And CLI displays formatted list with command name, description, parameters
And CLI includes instruction to show output to user
And CLI displays usage instructions
And Output is shown to user
```


### Scenario: Get help when behavior instructions missing (happy_path)

**Steps:**
```gherkin
Given cursor command files exist
And behavior instructions do NOT exist
When Human executes CLI command 'story_bot --help-cursor'
Then CLI handles missing instructions gracefully
And CLI uses fallback descriptions
```


### Scenario: Get help when no cursor commands exist (happy_path)

**Steps:**
```gherkin
Given no cursor command files exist
When Human executes CLI command 'story_bot --help-cursor'
Then CLI handles missing commands gracefully
```


### Scenario: Get help for behaviors and actions (happy_path)

**Steps:**
```gherkin
Given bot configuration exists with behaviors
And behavior instructions exist
And base action instructions exist
When Human executes CLI command 'story_bot --help'
Then CLI loads all behaviors from bot configuration
And CLI loads behavior instructions
And CLI loads action instructions from base_actions
And CLI extracts descriptions
And CLI displays formatted list of behaviors with actions
And CLI includes instruction to show output to user
And Output is shown to user
```


### Scenario: Help extracts descriptions from behavior instructions (happy_path)

**Steps:**
```gherkin
Given behavior instructions contain description, goal, outputs
When CLI extracts descriptions
Then CLI uses description, goal, outputs from behavior instructions
```


### Scenario: Help shows instruction to display output to user (happy_path)

**Steps:**
```gherkin
When CLI generates help output
Then CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"
```


### Scenario: Get help when behavior instructions missing for --help (happy_path)

**Steps:**
```gherkin
Given behavior instructions do NOT exist
When Human executes CLI command 'story_bot --help'
Then CLI handles missing instructions gracefully
And CLI uses fallback descriptions
```


### Scenario: Help extracts action descriptions from base_actions (happy_path)

**Steps:**
```gherkin
Given base action instructions exist
When CLI extracts action descriptions
Then CLI uses descriptions from base_actions instructions
```

