# 📝 Generate Cursor Command Files

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Human  
**Sequential Order:** 5  
**Story Type:** user

## Story Description

Human generates cursor command files so that bot CLI can be invoked from Cursor IDE command palette, providing convenient shortcuts for bot, behavior, behavior action, and close commands.

## Acceptance Criteria

- **WHEN** Human calls `generate_cursor_commands(commands_dir, cli_script_path)`
- **THEN** CLI creates `.cursor/commands/` directory if it doesn't exist
- **AND** CLI creates `<bot-name>.md` command file that invokes CLI with bot name (routes to current behavior/action)
- **AND** CLI creates `<bot-name>-<behavior>.md` command file for each behavior in bot that invokes CLI with bot name and behavior (auto-forwards to current action)
- **AND** CLI creates `<bot-name>-<behavior>-<action>.md` command file for each action in each behavior that invokes CLI with bot name, behavior, and action
- **AND** CLI creates `<bot-name>-close.md` command file that invokes CLI with bot name and --close parameter
- **AND** Each command file contains simple wrapper command that calls CLI script
- **AND** Bot name, behavior, and action are hardcoded in command files (no parameters needed)
- **AND** CLI removes obsolete command files for behaviors/actions that no longer exist in bot
- **AND** CLI returns dict mapping command names (e.g., `story_bot`, `story_bot-exploration`, `story_bot-exploration-gather_context`, `story_bot-close`) to file paths

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given CLI instance is initialized with bot_name="<bot_name>"
And bot has behaviors="<behaviors>"
And bot has actions="<actions>" for behavior "<behavior>"
And commands directory path is "<commands_dir>"
And CLI script path is "<cli_script_path>"
```

## Scenario Outlines

### Scenario Outline: Generate cursor command files (happy_path)

**Steps:**
```gherkin
Given CLI instance is initialized with bot_name="<bot_name>"
And bot has behavior "<behavior>"
And bot has action "<action>" in behavior "<behavior>"
And commands directory path is "<commands_dir>"
And CLI script path is "<cli_script_path>"
When Human calls generate_cursor_commands(commands_dir, cli_script_path)
Then CLI creates .cursor/commands directory
And CLI creates bot command file at "<commands_dir>/<bot_name>.md"
And CLI creates behavior command file at "<commands_dir>/<bot_name>-<behavior>.md"
And CLI creates action command file at "<commands_dir>/<bot_name>-<behavior>-<action>.md"
And CLI creates close command file at "<commands_dir>/<bot_name>-close.md"
And bot command file contains "<cli_script_path> <bot_name>"
And behavior command file contains "<cli_script_path> <bot_name> <behavior>"
And action command file contains "<cli_script_path> <bot_name> <behavior> <action>"
And close command file contains "<cli_script_path> <bot_name> --close"
And CLI returns dict with key "<bot_name>" mapping to bot command file path
And CLI returns dict with key "<bot_name>-<behavior>" mapping to behavior command file path
And CLI returns dict with key "<bot_name>-<behavior>-<action>" mapping to action command file path
And CLI returns dict with key "<bot_name>-close" mapping to close command file path
```

**Examples:**
| commands_dir | cli_script_path | bot_name | behavior | action |
|--------------|-----------------|----------|----------|--------|
| .cursor/commands | agile_bot/bots/story_bot/story_bot | story_bot | exploration | gather_context |
| .cursor/commands | agile_bot/bots/code_bot/code_bot | code_bot | shape | build_knowledge |
| .cursor/commands | agile_bot/bots/story_bot/story_bot | story_bot | exploration | build_knowledge |

### Scenario Outline: Generate cursor commands removes obsolete files when behavior removed (edge_case)

**Steps:**
```gherkin
Given CLI instance is initialized with bot_name="<bot_name>"
And bot previously had behavior "<removed_behavior>"
And obsolete command file exists at "<commands_dir>/<bot_name>-<removed_behavior>.md"
And obsolete action command file exists at "<commands_dir>/<bot_name>-<removed_behavior>-<removed_action>.md"
And bot no longer has behavior "<removed_behavior>"
And commands directory path is "<commands_dir>"
And CLI script path is "<cli_script_path>"
When Human calls generate_cursor_commands(commands_dir, cli_script_path)
Then CLI creates new command files for current behaviors and actions
And CLI removes obsolete command file "<commands_dir>/<bot_name>-<removed_behavior>.md"
And CLI removes obsolete action command file "<commands_dir>/<bot_name>-<removed_behavior>-<removed_action>.md"
And Obsolete command files no longer exist
```

**Examples:**
| commands_dir | cli_script_path | bot_name | removed_behavior | removed_action |
|--------------|------------------|----------|------------------|----------------|
| .cursor/commands | agile_bot/bots/story_bot/story_bot | story_bot | old_behavior | old_action |
| .cursor/commands | agile_bot/bots/code_bot/code_bot | code_bot | deprecated_behavior | deprecated_action |

### Scenario Outline: Generate cursor commands creates directory if missing (edge_case)

**Steps:**
```gherkin
Given CLI instance is initialized with bot_name="<bot_name>"
And bot has behaviors="<behaviors>"
And commands directory does NOT exist at "<commands_dir>"
And CLI script path is "<cli_script_path>"
When Human calls generate_cursor_commands(commands_dir, cli_script_path)
Then CLI creates .cursor/commands directory
And CLI creates bot command file at "<commands_dir>/<bot_name>.md"
And CLI creates behavior command file for each behavior in "<behaviors>"
And CLI creates action command file for each action in each behavior
And CLI creates close command file at "<commands_dir>/<bot_name>-close.md"
And All command files contain correct CLI invocations with hardcoded bot name, behaviors, and actions
```

**Examples:**
| commands_dir | cli_script_path | bot_name | behaviors |
|--------------|------------------|----------|-----------|
| .cursor/commands | agile_bot/bots/story_bot/story_bot | story_bot | exploration,discovery |
| .cursor/commands | agile_bot/bots/code_bot/code_bot | code_bot | shape,arrange |

## Source Material

**Generated from:** Story "Generate Cursor Command Files" in CLI Increment  
**Date:** 2025-01-27  
**Context:** Cursor command files provide convenient shortcuts for invoking bot CLI from Cursor IDE command palette

