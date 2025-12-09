# [Story] Generate BOT CLI code

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Build Agile Bots  
**Sub Epic:** Generate CLI
**User:** MCP Server Generator  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Generate BOT CLI code functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN MCP Server Generator processes Bot Config**
- **THEN Generator creates CLI command wrapper structure for bot invocation**
- **AND Generator generates CLI entry point script (e.g., bot_cli.py and bot shell script)**
- **AND CLI code includes argument parsing for behavior and action parameters**
- **AND CLI code includes help/usage documentation generation**
- **AND CLI code supports listing available bots, behaviors, and actions**
- **AND Generated CLI code integrates with existing bot instantiation logic**
- **AND CLI code follows same routing logic as MCP tools for consistency**
- **AND Generator updates bot registry at agile_bot/bots/registry.json**
- **AND Registry entry includes bot name, bot-level trigger patterns, and CLI path**
- **AND Generator loads trigger patterns from bot's trigger_words.json file**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Generate BOT CLI code

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

