# 📝 Invoke Bot Behavior Action CLI

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke CLI
**User:** Human
**Sequential Order:** 3
**Story Type:** user

## Story Description

Invoke Bot Behavior Action CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Human executes CLI command with bot name, behavior name, and action name (e.g., bot story_bot exploration gather_context)

  **then** CLI loads bot configuration and validates behavior and action exist

  **and** CLI loads workflow state if it exists

  **and** CLI routes to bot and specified behavior action (same as specific action MCP tool)

  **and** Bot executes action

  **and** CLI submits bot action output to AI Chat

  **and** Bot updates workflow state after action execution (if workflow action)

  **and** CLI supports passing additional parameters/arguments to bot actions

  **and** CLI provides error messages for invalid bot/behavior/action combinations

## Scenarios

### Scenario: Invoke bot behavior action CLI with parameters (happy_path)

**Steps:**
```gherkin
When Human executes CLI command "./story_bot exploration gather_context --increment_file=increment-cli-exploration.txt"
Then CLI loads bot configuration
And CLI validates behavior "exploration" exists
And CLI validates action "gather_context" exists
And CLI loads workflow state if it exists
And CLI routes to bot and specified behavior "exploration" and action "gather_context"
And CLI passes parameter "increment_file"="increment-cli-exploration.txt" to action
And Bot executes action "gather_context" with parameters
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot behavior action CLI without parameters (happy_path)

**Steps:**
```gherkin
When Human executes CLI command "./story_bot exploration gather_context"
Then CLI loads bot configuration
And CLI validates behavior "exploration" exists
And CLI validates action "gather_context" exists
And CLI loads workflow state if it exists
And CLI routes to bot and specified behavior "exploration" and action "gather_context"
And Bot executes action "gather_context" without parameters
And CLI returns result with status="success"
And Action is NOT marked as completed (human must close action separately)
```


### Scenario: Invoke bot behavior action CLI with invalid action (happy_path)

**Steps:**
```gherkin
Given action "invalid_action" does NOT exist in behavior "exploration"
When Human executes CLI command "./story_bot exploration invalid_action"
Then CLI loads bot configuration
And CLI validates behavior "exploration" exists
And CLI validates action "invalid_action" does not exist
And CLI returns error message
And CLI exits with exit code 1
```

