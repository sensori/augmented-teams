# 📝 Invoke Bot Behavior Action CLI

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Human  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Human invokes Bot Behavior Action CLI so that specific bot behavior actions can be executed through command-line interface, with support for passing parameters to actions.

## Acceptance Criteria

- **WHEN** Human executes CLI command with bot name, behavior name, and action name (e.g., `bot story_bot exploration gather_context`)
- **THEN** CLI loads bot configuration and validates behavior and action exist
- **AND** CLI loads workflow state if it exists
- **AND** CLI routes to bot and specified behavior action (same as specific action MCP tool)
- **AND** Bot executes action
- **AND** CLI submits bot action output to AI Chat
- **AND** Bot updates workflow state after action execution (if workflow action)
- **AND** CLI supports passing additional parameters/arguments to bot actions
- **AND** CLI provides error messages for invalid bot/behavior/action combinations

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists at "<bot_config_path>"
And workspace root is set to "<workspace_root>"
And behavior "<behavior_name>" exists in bot configuration
And action "<action_name>" exists in behavior "<behavior_name>"
```

## Scenario Outlines

### Scenario Outline: Invoke bot behavior action CLI with parameters (happy_path)

**Steps:**
```gherkin
When Human executes CLI command "./<bot_name> <behavior_name> <action_name> --<param_name>=<param_value>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<behavior_name>" exists
And CLI validates action "<action_name>" exists
And CLI loads workflow state if it exists
And CLI routes to bot and specified behavior "<behavior_name>" and action "<action_name>"
And CLI passes parameter "<param_name>"="<param_value>" to action
And Bot executes action "<action_name>" with parameters
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
And Bot updates workflow state after action execution
```

**Examples:**
| bot_config_path | workspace_root | behavior_name | action_name | bot_name | param_name | param_value | expected_status |
|-----------------|----------------|---------------|-------------|----------|------------|-------------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | exploration | gather_context | story_bot | increment_file | increment-cli-exploration.txt | success |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | shape | build_knowledge | story_bot | context_file | clarification.json | success |

### Scenario Outline: Invoke bot behavior action CLI without parameters (happy_path)

**Steps:**
```gherkin
When Human executes CLI command "./<bot_name> <behavior_name> <action_name>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<behavior_name>" exists
And CLI validates action "<action_name>" exists
And CLI loads workflow state if it exists
And CLI routes to bot and specified behavior "<behavior_name>" and action "<action_name>"
And Bot executes action "<action_name>" without parameters
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
And Bot updates workflow state after action execution
```

**Examples:**
| bot_config_path | workspace_root | behavior_name | action_name | bot_name | expected_status |
|-----------------|----------------|---------------|-------------|----------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | exploration | gather_context | story_bot | success |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | shape | build_knowledge | story_bot | success |

### Scenario Outline: Invoke bot behavior action CLI with invalid action (error_case)

**Steps:**
```gherkin
Given action "<invalid_action>" does NOT exist in behavior "<behavior_name>"
When Human executes CLI command "./<bot_name> <behavior_name> <invalid_action>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<behavior_name>" exists
And CLI validates action "<invalid_action>" does not exist
And CLI returns error message "<error_message>"
And CLI exits with exit code 1
```

**Examples:**
| bot_config_path | workspace_root | behavior_name | invalid_action | bot_name | error_message |
|-----------------|----------------|---------------|----------------|----------|---------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | exploration | invalid_action | story_bot | Action 'invalid_action' not found in behavior 'exploration' |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | shape | nonexistent | story_bot | Action 'nonexistent' not found in behavior 'shape' |

## Source Material

**Generated from:** Story "Invoke Bot Behavior Action CLI" in CLI Increment  
**Date:** 2025-12-05  
**Context:** CLI provides terminal-based alternative to MCP protocol for invoking specific bot behavior actions

