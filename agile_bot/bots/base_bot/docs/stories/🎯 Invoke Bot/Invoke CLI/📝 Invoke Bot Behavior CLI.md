# 📝 Invoke Bot Behavior CLI

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Human  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Human invokes Bot Behavior CLI so that specific bot behaviors can be executed through command-line interface, routing to current action within that behavior.

## Acceptance Criteria

- **WHEN** Human executes CLI command with bot name and behavior name (e.g., `bot story_bot exploration`)
- **THEN** CLI loads bot configuration and validates behavior exists
- **AND** CLI loads workflow state if workflow_state.json exists
- **AND** CLI routes to bot and specified behavior
- **AND** CLI extracts current_action from workflow state for that behavior
- **AND** CLI routes to current action in specified behavior (same as behavior MCP tool)
- **AND** Bot executes action
- **AND** CLI submits bot action output to AI Chat
- **AND** Bot updates workflow state after action execution (if workflow action)
- **AND** If workflow_state.json doesn't exist or behavior not in state, CLI defaults to first action of specified behavior

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists at "<bot_config_path>"
And workspace root is set to "<workspace_root>"
And behavior "<behavior_name>" exists in bot configuration
```

## Scenario Outlines

### Scenario Outline: Invoke bot behavior CLI with workflow state (happy_path)

**Steps:**
```gherkin
Given workflow state contains current_action="<current_action>" for behavior "<behavior_name>"
And workflow_state.json exists at "<workspace_root>/workflow_state.json"
When Human executes CLI command "./<bot_name> <behavior_name>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<behavior_name>" exists
And CLI loads workflow state from "<workspace_root>/workflow_state.json"
And CLI routes to bot and specified behavior "<behavior_name>"
And CLI extracts current_action="<current_action>" from workflow state
And CLI routes to current action "<current_action>" in behavior "<behavior_name>"
And Bot executes action "<current_action>"
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
And Bot updates workflow state after action execution
```

**Examples:**
| bot_config_path | workspace_root | behavior_name | current_action | bot_name | expected_status |
|-----------------|----------------|---------------|----------------|----------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | exploration | story_bot.exploration.gather_context | story_bot | success |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | shape | story_bot.shape.build_knowledge | story_bot | success |

### Scenario Outline: Invoke bot behavior CLI without workflow state (edge_case)

**Steps:**
```gherkin
Given workflow_state.json does NOT exist at "<workspace_root>/workflow_state.json"
When Human executes CLI command "./<bot_name> <behavior_name>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<behavior_name>" exists
And CLI detects workflow_state.json does not exist
And CLI defaults to first action "<first_action>" of behavior "<behavior_name>"
And CLI routes to bot and behavior "<behavior_name>"
And CLI routes to first action "<first_action>"
And Bot executes action "<first_action>"
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
```

**Examples:**
| bot_config_path | workspace_root | behavior_name | bot_name | first_action | expected_status |
|-----------------|----------------|---------------|----------|--------------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | exploration | story_bot | story_bot.exploration.initialize_project | success |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | shape | story_bot | story_bot.shape.initialize_project | success |

### Scenario Outline: Invoke bot behavior CLI with invalid behavior (error_case)

**Steps:**
```gherkin
Given behavior "<invalid_behavior>" does NOT exist in bot configuration
When Human executes CLI command "./<bot_name> <invalid_behavior>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI validates behavior "<invalid_behavior>" does not exist
And CLI returns error message "<error_message>"
And CLI exits with exit code 1
```

**Examples:**
| bot_config_path | workspace_root | invalid_behavior | bot_name | error_message |
|-----------------|----------------|------------------|----------|---------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | invalid_behavior | story_bot | Behavior 'invalid_behavior' not found in bot configuration |
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | nonexistent | story_bot | Behavior 'nonexistent' not found in bot configuration |

## Source Material

**Generated from:** Story "Invoke Bot Behavior CLI" in CLI Increment  
**Date:** 2025-12-05  
**Context:** CLI provides terminal-based alternative to MCP protocol for invoking bot behaviors

