# 📝 Generate Behavior Action Tools

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** MCP Server Generator  
**Sequential Order:** 2  
**Story Type:** system

**Test File:** test_generate_bot_server_and_tools.py  
**Test Class:** TestGenerateBehaviorActionTools

## Story Description

MCP Server Generator processes Bot Config and creates tool code for each (behavior, action) pair. The generator enumerates all behaviors and actions from Bot Config, and for each pair generates tool code with unique name, trigger words, and forwarding logic. A tool catalog is prepared with all generated tool instances.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Generator processes Bot Config
- **THEN** Generator creates tool code for each (behavior, action) pair
- **AND** Enumerates all behaviors and actions from Bot Config
- **AND** For each pair, generates tool code with unique name, trigger words, forwarding logic
- **AND** Tool catalog prepared with all generated tool instances

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server Generator has Bot Config
And Bot Config contains behaviors and actions
```

## Scenarios

### Scenario: Generate behavior action tools

**Test Method:** `test_generator_creates_behavior_action_tools`

**Steps:**
```gherkin
Given MCP Server Generator processes Bot Config
When Generator creates tool code
Then Generator enumerates all behaviors and actions from Bot Config
And Generator creates tool code for each (behavior, action) pair
And Each tool has unique name, trigger words, and forwarding logic
And Tool catalog is prepared with all generated tool instances
```

