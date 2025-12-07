# 📝 Generate BOT CLI code

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** MCP Server Generator  
**Sequential Order:** 1  
**Story Type:** system

## Story Description

MCP Server Generator generates BOT CLI code so that bot tools and behaviors can be invoked through command-line interface, providing an alternative to MCP protocol for terminal-based interaction.

## Acceptance Criteria

- **WHEN** MCP Server Generator processes Bot Config
- **THEN** Generator creates CLI command wrapper structure for bot invocation
- **AND** Generator generates CLI entry point script (e.g., bot_cli.py and bot shell script)
- **AND** CLI code includes argument parsing for behavior and action parameters
- **AND** CLI code includes help/usage documentation generation
- **AND** CLI code supports listing available bots, behaviors, and actions
- **AND** Generated CLI code integrates with existing bot instantiation logic
- **AND** CLI code follows same routing logic as MCP tools for consistency

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server Generator is initialized
And Bot Config exists at bot_config.json
And base bot CLI template code exists in base_bot/src/cli/base_bot_cli.py
And bot instantiation logic exists in base_bot/src/bot/bot.py
```

## Scenario Outlines

### Scenario Outline: Generator creates CLI code for bot (happy_path)

**Steps:**
```gherkin
Given a bot with name "<bot_name>"
And Bot Config exists at "<bot_config_path>"
And bot has behaviors configured as "<behaviors>"
When MCP Server Generator processes Bot Config
Then Generator creates CLI command wrapper structure
And Generator generates CLI entry point script at "<cli_script_path>"
And CLI script includes argument parsing for behavior and action parameters
And CLI script includes help/usage documentation generation
And CLI script supports listing available bots, behaviors, and actions via --list flag
And Generated CLI code integrates with existing bot instantiation logic from base_bot
And CLI code follows same routing logic as MCP tools (workflow state-based auto-forwarding)
And CLI script is executable and can be invoked from command line
```

**Examples:**
| bot_name | bot_config_path | behaviors | cli_script_path |
|----------|-----------------|-----------|-----------------|
| story_bot | agile_bot/bots/story_bot/config/bot_config.json | exploration,shape,discovery | agile_bot/bots/story_bot/story_bot |
| code_bot | agile_bot/bots/code_bot/config/bot_config.json | shape,arrange | agile_bot/bots/code_bot/code_bot |

### Scenario Outline: Generator fails when Bot Config is missing (error_case)

**Steps:**
```gherkin
Given a bot with name "<bot_name>"
And Bot Config does NOT exist at "<bot_config_path>"
When MCP Server Generator attempts to process Bot Config
Then Generator raises FileNotFoundError with message "Bot Config not found at <bot_config_path>"
And Generator does not create CLI code
```

**Examples:**
| bot_name | bot_config_path |
|----------|-----------------|
| missing_bot | agile_bot/bots/missing_bot/config/bot_config.json |
| invalid_bot | agile_bot/bots/invalid_bot/config/bot_config.json |

### Scenario Outline: Generator fails when Bot Config is malformed (error_case)

**Steps:**
```gherkin
Given a bot with name "<bot_name>"
And Bot Config exists at "<bot_config_path>"
And Bot Config has invalid JSON syntax
When MCP Server Generator attempts to process Bot Config
Then Generator raises JSONDecodeError with message "Malformed Bot Config at <bot_config_path>"
And Generator does not create CLI code
```

**Examples:**
| bot_name | bot_config_path |
|----------|-----------------|
| malformed_bot | agile_bot/bots/malformed_bot/config/bot_config.json |
| corrupted_bot | agile_bot/bots/corrupted_bot/config/bot_config.json |

### Scenario Outline: Generator creates CLI with help and list functionality (happy_path)

**Steps:**
```gherkin
Given a bot with name "<bot_name>"
And Bot Config exists at "<bot_config_path>"
And bot has behaviors configured as "<behaviors>"
When MCP Server Generator processes Bot Config
Then Generator creates CLI entry point script
And CLI script supports --help flag that displays usage documentation
And CLI script supports --list flag that displays available bots, behaviors, and actions
And CLI script help includes command structure: "<bot_name> [behavior] [action] [--options]"
And CLI script help includes examples of valid commands
```

**Examples:**
| bot_name | bot_config_path | behaviors |
|----------|-----------------|-----------|
| story_bot | agile_bot/bots/story_bot/config/bot_config.json | exploration,shape |
| code_bot | agile_bot/bots/code_bot/config/bot_config.json | shape,arrange |

### Scenario Outline: Generated CLI integrates with bot instantiation logic (happy_path)

**Steps:**
```gherkin
Given a bot with name "<bot_name>"
And Bot Config exists at "<bot_config_path>"
And base bot instantiation logic exists in base_bot/src/bot/bot.py
When MCP Server Generator processes Bot Config
Then Generated CLI code uses same bot loading logic as MCP server
And Generated CLI code uses same bot initialization logic as MCP server
And Generated CLI code uses same workflow state loading logic as MCP server
And Generated CLI code routes to bot using same patterns as MCP tools
And CLI routing logic matches MCP tool routing logic for consistency
```

**Examples:**
| bot_name | bot_config_path |
|----------|-----------------|
| story_bot | agile_bot/bots/story_bot/config/bot_config.json |
| code_bot | agile_bot/bots/code_bot/config/bot_config.json |

## Source Material

**Generated from:** Story "Generate BOT CLI code" in CLI Increment  
**Date:** 2025-01-27  
**Context:** System story for MCP Server Generator to create CLI code that provides command-line interface alternative to MCP protocol for bot invocation

