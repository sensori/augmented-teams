# 📝 Generate MCP Bot Server

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** MCP Server Generator  
**Sequential Order:** 1  
**Story Type:** system

## Story Description

MCP Server Generator generates unique MCP Bot Server instance so that bot behaviors can be accessed as MCP tools.

## Acceptance Criteria

- **WHEN** MCP Server Generator receives Bot Config
- **THEN** Generator generates unique MCP Server instance with **Unique server name** from bot name (e.g., "story_bot_server", "bdd_bot_server")
  - THAT leverages **Server initialization code** to start in separate thread
- **AND** Generated server includes Bot Config reference
- **AND** Generated server leverages Specific Bot instantiation code

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Bot Server Generator is initialized
And base MCP server template code exists in base_bot/src/base_mcp_server.py
And base bot class exists in base_bot/src/base_bot.py
```

## Scenarios

### Scenario: Generator creates MCP server for test_bot

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has behaviors configured as ['shape', 'discovery', 'exploration', 'specification']
And Bot Config exists at bot_config.json
When MCP Server Generator receives Bot Config
Then Generator creates MCP Server instance with unique server name 'test_bot_server'
And Generated server includes reference to Bot Config at exact path: agile_bot/bots/test_bot/config/bot_config.json
And Generated server includes Specific Bot instantiation code that loads test_bot.py
And Generated server is saved to exact path: agile_bot/bots/test_bot/src/test_bot_server.py
```

### Scenario: Generator fails when Bot Config is missing

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And Bot Config does NOT exist at bot_config.json
When MCP Server Generator attempts to receive Bot Config
Then Generator raises FileNotFoundError with message 'Bot Config not found at agile_bot/bots/test_bot/config/bot_config.json'
And Generator does not create MCP Server instance
```

### Scenario: Generator fails when Bot Config is malformed

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And Bot Config exists at bot_config.json
And Bot Config has invalid JSON syntax
When MCP Server Generator attempts to receive Bot Config
Then Generator raises JSONDecodeError with message 'Malformed Bot Config at agile_bot/bots/test_bot/config/bot_config.json'
And Generator does not create MCP Server instance
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on MCP Bot Server generation. Minimal path plus alternates approach covering happy path and key error cases.

