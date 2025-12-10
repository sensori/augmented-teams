# 📝 Invoke Bot CLI

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke CLI
**User:** Human
**Sequential Order:** 1
**Story Type:** user

## Story Description

Invoke Bot CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Human executes CLI command with bot name only (e.g., bot story_bot)

  **then** CLI loads bot configuration for specified bot

  **and** CLI loads workflow state if workflow_state.json exists

  **and** CLI extracts current_behavior and current_action from workflow state

  **and** CLI routes to bot and invokes current behavior and current action (same as main bot MCP tool)

  **and** Bot executes action

  **and** CLI submits bot action output to AI Chat

  **and** Bot updates workflow state after action execution (if workflow action)

  **and** If workflow_state.json doesn't exist, CLI defaults to first behavior's first action

## Scenarios

### Scenario: Invoke bot CLI with workflow state (happy_path)

**Steps:**
```gherkin
Given workflow state contains current_behavior="story_bot.exploration"
And workflow state contains current_action="story_bot.exploration.gather_context"
And workflow_state.json exists
When Human executes CLI command "./story_bot"
Then CLI loads bot configuration
And CLI loads workflow state
And CLI routes to bot and invokes current behavior and current action
And Bot executes action
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot CLI without workflow state (happy_path)

**Steps:**
```gherkin
Given workflow_state.json does NOT exist
When Human executes CLI command "./story_bot"
Then CLI loads bot configuration
And CLI detects workflow_state.json does not exist
And CLI defaults to first behavior "story_bot.exploration"
And CLI defaults to first action "story_bot.exploration.initialize_project"
And CLI routes to bot and invokes first behavior and first action
And Bot executes action
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot CLI with invalid bot name (happy_path)

**Steps:**
```gherkin
Given bot configuration does NOT exist at specified path
When Human executes CLI command "./invalid_bot"
Then CLI attempts to load bot configuration
And CLI detects bot configuration does not exist
And CLI returns error message
And CLI exits with exit code 1
```

