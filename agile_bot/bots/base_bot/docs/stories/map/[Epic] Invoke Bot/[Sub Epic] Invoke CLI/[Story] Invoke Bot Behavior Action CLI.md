# [Story] Invoke Bot Behavior Action CLI

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Invoke CLI
**User:** Human  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Invoke Bot Behavior Action CLI functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Human executes CLI command with bot name, behavior name, and action name (e.g., bot story_bot exploration gather_context)**
- **THEN CLI loads bot configuration and validates behavior and action exist**
- **AND CLI loads workflow state if it exists**
- **AND CLI routes to bot and specified behavior action (same as specific action MCP tool)**
- **AND Bot executes action**
- **AND CLI submits bot action output to AI Chat**
- **AND Bot updates workflow state after action execution (if workflow action)**
- **AND CLI supports passing additional parameters/arguments to bot actions**
- **AND CLI provides error messages for invalid bot/behavior/action combinations**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Invoke bot behavior action CLI with parameters

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


### Scenario: Invoke bot behavior action CLI without parameters

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


### Scenario: Invoke bot behavior action CLI with invalid action

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


