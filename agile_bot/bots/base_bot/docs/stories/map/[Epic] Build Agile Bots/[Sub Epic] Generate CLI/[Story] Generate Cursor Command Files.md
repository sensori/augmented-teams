# [Story] Generate Cursor Command Files

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Build Agile Bots  
**Sub Epic:** Generate CLI
**User:** MCP Server Generator  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Generate Cursor Command Files functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Human calls generate_cursor_commands(commands_dir, cli_script_path)**
- **THEN CLI creates .cursor/commands/ directory if it doesn't exist**
- **AND CLI creates <bot-name>.md command file that invokes CLI with bot name (routes to current behavior/action)**
- **AND CLI creates <bot-name>-<behavior>.md command file for each behavior in bot that invokes CLI with bot name and behavior (auto-forwards to current action)**
- **AND CLI creates <bot-name>-<behavior>-<action>.md command file for each action in each behavior that invokes CLI with bot name, behavior, and action**
- **AND CLI creates <bot-name>-close.md command file that invokes CLI with bot name and --close parameter**
- **AND Each command file contains simple wrapper command that calls CLI script**
- **AND Bot name, behavior, and action are hardcoded in command files (no parameters needed)**
- **AND CLI removes obsolete command files for behaviors/actions that no longer exist in bot**
- **AND CLI returns dict mapping command names (e.g., story_bot, story_bot-exploration, story_bot-exploration-gather_context, story_bot-close) to file paths**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Generate cursor command files (happy_path)

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


### Scenario: Generate cursor commands creates directory if missing (edge_case)

**Steps:**
```gherkin
Given: CLI instance is initialized
And: commands directory does NOT exist
When: Human calls generate_cursor_commands()
Then: CLI creates .cursor/commands directory
And: CLI creates all command files
```


### Scenario: Generate cursor commands removes obsolete files when behavior removed (edge_case)

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


