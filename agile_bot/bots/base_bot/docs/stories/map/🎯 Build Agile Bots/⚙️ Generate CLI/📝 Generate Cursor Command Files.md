# 📝 Generate Cursor Command Files

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Build Agile Bots
**Feature:** Generate CLI
**User:** MCP Server Generator
**Sequential Order:** 2
**Story Type:** user

## Story Description

Generate Cursor Command Files functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Human calls generate_cursor_commands(commands_dir, cli_script_path)

  **then** CLI creates .cursor/commands/ directory if it doesn't exist

  **and** CLI creates <bot-name>.md command file that invokes CLI with bot name (routes to current behavior/action)

  **and** CLI creates <bot-name>-<behavior>.md command file for each behavior in bot that invokes CLI with bot name and behavior (auto-forwards to current action)

  **and** CLI creates <bot-name>-<behavior>-<action>.md command file for each action in each behavior that invokes CLI with bot name, behavior, and action

  **and** CLI creates <bot-name>-close.md command file that invokes CLI with bot name and --close parameter

  **and** Each command file contains simple wrapper command that calls CLI script

  **and** Bot name, behavior, and action are hardcoded in command files (no parameters needed)

  **and** CLI removes obsolete command files for behaviors/actions that no longer exist in bot

  **and** CLI returns dict mapping command names (e.g., story_bot, story_bot-exploration, story_bot-exploration-gather_context, story_bot-close) to file paths

## Scenarios

### Scenario: Generate cursor command files (happy_path) (happy_path)

**Steps:**
```gherkin
Given: CLI instance is initialized
And: commands directory path is provided
And: CLI script path is provided
When: Human calls generate_cursor_commands()
Then: CLI creates .cursor/commands directory
And: CLI creates bot command file
And: CLI creates bot-behavior command file
And: CLI creates bot-behavior-action command file
And: CLI creates bot-close command file
And: Each command file contains correct CLI invocation
```


### Scenario: Generate cursor commands creates directory if missing (edge_case) (happy_path)

**Steps:**
```gherkin
Given: CLI instance is initialized
And: commands directory does NOT exist
When: Human calls generate_cursor_commands()
Then: CLI creates .cursor/commands directory
And: CLI creates all command files
```


### Scenario: Generate cursor commands removes obsolete files when behavior removed (edge_case) (happy_path)

**Steps:**
```gherkin
Given: CLI instance is initialized
And: Bot previously had behavior "old_behavior"
And: Obsolete command file exists for removed behavior
And: Bot no longer has behavior "old_behavior"
When: Human calls generate_cursor_commands()
Then: CLI creates new command files for current behaviors
And: CLI removes obsolete command files for removed behaviors
```

