# 📝 Initialize Agent

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

MCP Server receives tool call from AI Chat and requests Agent instance from AgentStateManager, which creates and initializes Agent with agent_name='stories' and optional project_area parameter (may be None if not explicitly provided), sets up configuration file paths

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When MCP Server receives tool call from AI Chat, then MCP Server requests Agent instance from AgentStateManager
- When AgentStateManager receives request for Agent instance, then AgentStateManager checks if Agent instance already exists in cache, and if not found creates new Agent instance
- When AgentStateManager creates new Agent instance, then AgentStateManager instantiates Agent with agent_name='stories' and optional project_area parameter (may be None if not explicitly provided), handles any initialization errors, stores instance in cache, and returns the Agent instance
- When Agent initializes, then Agent sets up configuration file paths: base agent configuration at agents/base/agent.json, agent directory at workspace_root/agents, and agent-specific configuration at agents/{agent_name}/agent.json

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server is initialized and running
  [🔗](../../../../../../src/stories_acceptance_tests.py#L145)
And MCP Server has received tool call from AI Chat with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L152)
```

## Scenarios

### Scenario: MCP Server requests new Agent instance for continuation

**Steps:**
```gherkin
Given AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
Then AgentStateManager checks if Agent instance exists in cache
  [🔗](../../../../../../src/stories_acceptance_tests.py#L173)
And AgentStateManager finds no cached instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L180)
When AgentStateManager creates new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L186)
Then AgentStateManager instantiates Agent with agent_name='stories' and optional project_area parameter
  [🔗](../../../../../../src/stories_acceptance_tests.py#L192)
And AgentStateManager handles any initialization errors
  [🔗](../../../../../../src/stories_acceptance_tests.py#L199)
And AgentStateManager stores instance in cache
  [🔗](../../../../../../src/stories_acceptance_tests.py#L205)
And AgentStateManager returns the Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L212)
When Agent initializes
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
Then Agent sets up base agent configuration path at agents/base/agent.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L224)
And Agent sets up agent directory at workspace_root/agents
  [🔗](../../../../../../src/stories_acceptance_tests.py#L231)
And Agent sets up agent-specific configuration at agents/stories/agent.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L238)
```

### Scenario: AgentStateManager reuses cached Agent instance for continuation

**Steps:**
```gherkin
Given AgentStateManager has cached Agent instance with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L245)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
Then AgentStateManager checks if Agent instance exists in cache
  [🔗](../../../../../../src/stories_acceptance_tests.py#L173)
And AgentStateManager finds cached instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L252)
Then AgentStateManager returns cached Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L258)
And AgentStateManager does not create new instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L264)
And system does not crash from duplicate initialization
  [🔗](../../../../../../src/stories_acceptance_tests.py#L270)
```

### Scenario Outline: Agent initialization fails due to missing base config

**Steps:**
```gherkin
Given agents/base/agent.json file does not exist at "<base_config_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L276)
And AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
And AgentStateManager attempts to create new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L284)
Then AgentStateManager handles initialization error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L295)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is returned to MCP Server
And error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L313)
And AgentStateManager does not store invalid instance in cache
  [🔗](../../../../../../src/stories_acceptance_tests.py#L319)
```

**Examples:**
| base_config_path | expected_error_message |
|-----------------|----------------------|
| agents/base/agent.json | "Error: Could not load base agent configuration from agents/base/agent.json: File not found" |
| test_data/agents/base/agent.json | "Error: Could not load base agent configuration from test_data/agents/base/agent.json: File not found" |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

