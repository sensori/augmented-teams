# 📝 Invoke Bot Behavior CLI

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke CLI
**User:** Human
**Sequential Order:** 2
**Story Type:** user

## Story Description

Invoke Bot Behavior CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Human executes CLI command with bot name and behavior name (e.g., bot story_bot exploration)

  **then** CLI loads bot configuration and validates behavior exists

  **and** CLI loads workflow state if workflow_state.json exists

  **and** CLI routes to bot and specified behavior

  **and** CLI extracts current_action from workflow state for that behavior

  **and** CLI routes to current action in specified behavior (same as behavior MCP tool)

  **and** Bot executes action

  **and** CLI submits bot action output to AI Chat

  **and** Bot updates workflow state after action execution (if workflow action)

  **and** If workflow_state.json doesn't exist or behavior not in state, CLI defaults to first action of specified behavior

## Scenarios

### Scenario: Invoke bot behavior CLI with workflow state (happy_path)

**Steps:**
```gherkin
Given workflow state contains current_action="story_bot.exploration.gather_context" for behavior "exploration"
And workflow_state.json exists
When Human executes CLI command "./story_bot exploration"
Then CLI loads bot configuration
And CLI validates behavior "exploration" exists
And CLI loads workflow state
And CLI routes to bot and specified behavior "exploration"
And CLI extracts current_action from workflow state
And CLI routes to current action in behavior
And Bot executes action
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot behavior CLI without workflow state (happy_path)

**Steps:**
```gherkin
Given workflow_state.json does NOT exist
When Human executes CLI command "./story_bot exploration"
Then CLI loads bot configuration
And CLI validates behavior "exploration" exists
And CLI detects workflow_state.json does not exist
And CLI defaults to first action "story_bot.exploration.initialize_project" of behavior "exploration"
And CLI routes to bot and behavior "exploration"
And CLI routes to first action
And Bot executes action
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot behavior CLI with invalid behavior (happy_path)

**Steps:**
```gherkin
Given behavior "invalid_behavior" does NOT exist in bot configuration
When Human executes CLI command "./story_bot invalid_behavior"
Then CLI loads bot configuration
And CLI validates behavior "invalid_behavior" does not exist
And CLI returns error message
And CLI exits with exit code 1
```

