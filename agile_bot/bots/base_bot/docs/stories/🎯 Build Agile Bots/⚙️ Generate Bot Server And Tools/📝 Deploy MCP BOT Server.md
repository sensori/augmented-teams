# 📝 Deploy MCP BOT Server

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** System  
**Sequential Order:** 3  
**Story Type:** system

## Story Description

System deploys generated MCP Server so that tools are available to AI Chat for invocation.

## Acceptance Criteria

### AC 1: Deploy and Publish Tool Catalog

- **WHEN** MCP Server code generated and all tools generated
- **THEN** Generator deploys/starts generated MCP Server
- **AND** Server initializes in separate thread
- **AND** Server registers itself with MCP Protocol Handler using unique server name
- **AND** Server publishes tool catalog to AI Chat containing all generated BaseBehavioralActionTools
- **AND** Each tool entry in catalog includes:
  - Unique tool name: `{bot_name}_{behavior}_{action}`
  - Description from instructions.json
  - Trigger patterns from trigger_words.json (for AI Chat to match against user input)
  - Parameters (behavior name, action name, optional user input)
- **AND** AI Chat can discover tools by trigger word pattern matching
- **AND** Server endpoint accessible to AI Chat client

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server code has been generated for test_bot
And all Behavior Action Tools have been generated for test_bot
And MCP Protocol Handler is running
```

## Scenarios

### Scenario: Generator deploys test_bot MCP Server successfully

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has 4 behaviors with 6 actions each (24 tools total)
And MCP Server has been generated
And MCP Protocol Handler is running
When Generator deploys MCP Server
Then Server initializes in separate thread with unique thread ID
And Server registers with MCP Protocol Handler using server name 'test_bot_server'
And Server publishes tool catalog with 24 tools to AI Chat
And Server is accessible at exact path: agile_bot/bots/test_bot/src/test_bot_server.py
And each tool entry includes tool name, description, trigger patterns, and parameters
And AI Chat can discover tools by matching user input against trigger patterns
```

### Scenario: Server publishes tool catalog with complete metadata

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape' with action 'gather_context'
And action has trigger patterns: ["shape.*story", "start.*mapping", "story.*discovery"]
And MCP Server has initialized in separate thread
When Server publishes tool catalog to AI Chat
Then catalog entry for 'test_bot_shape_gather_context' includes tool name 'test_bot_shape_gather_context'
And catalog entry includes description loaded from exact path: agile_bot/bots/test_bot/behaviors/shape/gather_context/instructions.json
And catalog entry includes trigger patterns: ["shape.*story", "start.*mapping", "story.*discovery"]
And catalog entry includes parameters: behavior_name='shape', action_name='gather_context', user_input=(optional)
And AI Chat receives complete tool catalog via MCP Protocol Handler
```

### Scenario: Generator fails to deploy when MCP Protocol Handler is not running

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And MCP Server has been generated
And MCP Protocol Handler is NOT running
When Generator attempts to deploy MCP Server
Then Generator raises ConnectionError with message 'MCP Protocol Handler not accessible'
And Server at exact path agile_bot/bots/test_bot/src/test_bot_server.py does not initialize
And Tool catalog is not published
```

### Scenario: Server handles initialization failure in separate thread

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And MCP Server has been generated
And Bot Config is missing (file moved or deleted)
When Generator deploys MCP Server
Then Server thread starts but fails during initialization
And Server logs error 'Bot Config not found during initialization at agile_bot/bots/test_bot/config/bot_config.json'
And Server does not register with MCP Protocol Handler
And Tool catalog is not published
And Generator receives initialization failure notification
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on MCP Server deployment, thread initialization, and tool catalog publishing.

