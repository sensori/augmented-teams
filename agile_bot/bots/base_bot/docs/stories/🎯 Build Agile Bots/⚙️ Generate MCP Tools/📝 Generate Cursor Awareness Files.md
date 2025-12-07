# 📝 Generate Cursor Awareness Files

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** MCP Server Generator  
**Sequential Order:** 4  
**Story Type:** system

**Test File:** test_generate_bot_server_and_tools.py  
**Test Class:** TestGenerateAwarenessFilesIntegration  
**Test Methods:** 
- test_full_awareness_generation_workflow

## Story Description

MCP Server Generator creates Cursor awareness files that instruct the AI to check MCP tools FIRST before manual file operations. The generator creates bot-specific workspace rules files with trigger word patterns mapped to MCP tool types, enabling the AI to recognize when to use MCP tools based on user intent.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** MCP Generator runs for a bot
- **THEN** Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
- **AND** File includes trigger word patterns mapped to MCP tool types
- **WHEN** workspace rules file is generated
- **THEN** Rules instruct AI to check MCP tools FIRST before manual file operations
- **AND** Rules include pattern: hear trigger word → check available tools → invoke tool OR inform user
- **WHEN** Generator creates memory about tool awareness
- **THEN** Memory created via update_memory API
- **AND** Memory persists pattern for AI to check MCP tools when hearing workflow trigger words
- **AND** Memory includes handling for ask mode vs agent mode

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server Generator is initialized
And Bot config exists with behaviors
And Trigger words files exist for behaviors
```

## Scenarios

### Scenario: Full awareness generation workflow

**Steps:**
```gherkin
Given MCP Server Generator initialized
When generate_awareness_files() called
Then Bot-specific rules file is created
And Rules file has all required sections
And File includes bot name
And File includes Priority: Check MCP Tools First
```

**Test Method:** `test_full_awareness_generation_workflow`

**Test Details:**
- Creates MCP Server Generator instance
- Calls `generate_awareness_files()` method
- Verifies that bot-specific rules file is created at `.cursor/rules/mcp-<bot-name>-awareness.mdc`
- Verifies that rules file contains bot name
- Verifies that rules file includes priority section
- Verifies that rules file includes bot identification

## Test Details

- **Test File:** `test_generate_bot_server_and_tools.py`
- **Test Class:** `TestGenerateAwarenessFilesIntegration`
- **Test Methods:**
  - `test_full_awareness_generation_workflow` - Integration test for complete awareness file generation workflow

## Implementation Notes

The MCP Server Generator uses the `generate_awareness_files()` method to:
1. Create `.cursor/rules/` directory if it doesn't exist
2. Generate bot-specific awareness file with naming pattern: `mcp-<bot-name>-awareness.mdc`
3. Include trigger word patterns from behavior trigger_words.json files
4. Map trigger patterns to tool naming conventions
5. Include bot goal and behavior descriptions from instructions.json
6. Provide clear instructions for AI to check MCP tools first

The awareness file enables the AI to recognize when user requests match trigger patterns and automatically check for and invoke appropriate MCP tools instead of performing manual file operations.
