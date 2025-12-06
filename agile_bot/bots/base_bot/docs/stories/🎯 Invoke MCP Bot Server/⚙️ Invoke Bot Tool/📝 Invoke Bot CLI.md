# 📝 Invoke Bot CLI

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Human  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Human invokes Bot CLI so that bot tools and behaviors can be executed through command-line interface, providing an alternative to MCP protocol.

## Acceptance Criteria

- **WHEN** Human executes CLI command with bot name only (e.g., `bot story_bot`)
- **THEN** CLI loads bot configuration for specified bot
- **AND** CLI loads workflow state if workflow_state.json exists
- **AND** CLI extracts current_behavior and current_action from workflow state
- **AND** CLI routes to bot and invokes current behavior and current action (same as main bot MCP tool)
- **AND** Bot executes action
- **AND** CLI submits bot action output to AI Chat
- **AND** Bot updates workflow state after action execution (if workflow action)
- **AND** If workflow_state.json doesn't exist, CLI defaults to first behavior's first action

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists at "<bot_config_path>"
And workspace root is set to "<workspace_root>"
```

## Scenario Outlines

### Scenario Outline: Invoke bot CLI with workflow state (happy_path)

**Steps:**
```gherkin
Given workflow state contains current_behavior="<current_behavior>"
And workflow state contains current_action="<current_action>"
And workflow_state.json exists at "<workspace_root>/workflow_state.json"
When Human executes CLI command "./<bot_name>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI loads workflow state from "<workspace_root>/workflow_state.json"
And CLI extracts current_behavior="<current_behavior>" from workflow state
And CLI extracts current_action="<current_action>" from workflow state
And CLI routes to bot and invokes current behavior and current action
And Bot executes action "<current_action>"
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
And Bot updates workflow state after action execution
```

**Examples:**
| bot_config_path | workspace_root | current_behavior | current_action | bot_name | expected_status |
|-----------------|----------------|------------------|----------------|----------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | story_bot.exploration | story_bot.exploration.gather_context | story_bot | success |
| agile_bot/bots/code_bot/config/bot_config.json | c:/dev/augmented-teams | code_bot.shape | code_bot.shape.build_knowledge | code_bot | success |

### Scenario Outline: Invoke bot CLI without workflow state (edge_case)

**Steps:**
```gherkin
Given workflow_state.json does NOT exist at "<workspace_root>/workflow_state.json"
When Human executes CLI command "./<bot_name>"
Then CLI loads bot configuration from "<bot_config_path>"
And CLI detects workflow_state.json does not exist
And CLI defaults to first behavior "<first_behavior>"
And CLI defaults to first action "<first_action>"
And CLI routes to bot and invokes "<first_behavior>" and "<first_action>"
And Bot executes action "<first_action>"
And CLI returns result with status="<expected_status>"
And Action is NOT marked as completed (human must close action separately)
```

**Examples:**
| bot_config_path | workspace_root | bot_name | first_behavior | first_action | expected_status |
|-----------------|----------------|----------|----------------|--------------|-----------------|
| agile_bot/bots/story_bot/config/bot_config.json | c:/dev/augmented-teams | story_bot | story_bot.exploration | story_bot.exploration.initialize_project | success |
| agile_bot/bots/code_bot/config/bot_config.json | c:/dev/augmented-teams | code_bot | code_bot.shape | code_bot.shape.initialize_project | success |

### Scenario Outline: Invoke bot CLI with invalid bot name (error_case)

**Steps:**
```gherkin
Given workspace root is set to "<workspace_root>"
And bot configuration does NOT exist at "<bot_config_path>"
When Human executes CLI command "./<bot_name>"
Then CLI attempts to load bot configuration from "<bot_config_path>"
And CLI detects bot configuration does not exist
And CLI returns error message "<error_message>"
And CLI exits with exit code 1
```

**Examples:**
| workspace_root | bot_config_path | bot_name | error_message |
|----------------|-----------------|----------|---------------|
| c:/dev/augmented-teams | agile_bot/bots/invalid_bot/config/bot_config.json | invalid_bot | Bot 'invalid_bot' not found in configuration |
| c:/dev/augmented-teams | agile_bot/bots/missing_bot/config/bot_config.json | missing_bot | Bot 'missing_bot' not found in configuration |

## Source Material

**Generated from:** Story "Invoke Bot CLI" in CLI Increment  
**Date:** 2025-12-05  
**Context:** CLI provides terminal-based alternative to MCP protocol for invoking bot tools and behaviors

