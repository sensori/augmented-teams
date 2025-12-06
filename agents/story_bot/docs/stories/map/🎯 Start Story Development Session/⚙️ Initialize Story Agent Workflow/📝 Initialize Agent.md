# 📝 Initialize Agent

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../initialize-workflow-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Initialize Story Agent Workflow

## Story Description

MCP Server receives tool call from AI Chat and requests Agent instance from AgentStateManager, which creates and initializes Agent with agent_name='stories', sets up configuration file paths

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When MCP Server receives tool call from AI Chat, then MCP Server requests Agent instance from AgentStateManager
- When AgentStateManager receives request for Agent instance, then AgentStateManager checks if Agent instance already exists in cache, and if not found creates new Agent instance
- When AgentStateManager creates new Agent instance, then AgentStateManager instantiates Agent with agent_name='stories', handles any initialization errors, stores instance in cache, and returns the Agent instance
- When Agent initializes, then Agent sets up configuration file paths: base agent configuration at agents/base/agent.json, agent directory at workspace_root/agents, and agent-specific configuration at agents/{agent_name}/agent.json

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Server is initialized and running
  [🔗](../../../../../../src/stories_acceptance_tests.py#L145)
```

## Scenarios

### Scenario: MCP Server requests new Agent instance

**Steps:**
```gherkin
Given MCP Server has received tool call from AI Chat with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L152)
And AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
Then AgentStateManager checks if Agent instance exists in cache
  [🔗](../../../../../../src/stories_acceptance_tests.py#L173)
And AgentStateManager finds no cached instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L180)
When AgentStateManager creates new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L186)
Then AgentStateManager instantiates Agent with agent_name='stories'
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
```

### Scenario: AgentStateManager reuses cached Agent instance

**Steps:**
```gherkin
Given AgentStateManager has cached Agent instance with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L245)
And MCP Server has received tool call from AI Chat with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L152)
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
```

### Scenario Outline: Agent initialization fails due to missing agent-specific config

**Steps:**
```gherkin
Given agents/base/agent.json exists at "<base_config_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L326)
And agents/stories/agent.json file does not exist at "<agent_config_path>"
And AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
And AgentStateManager attempts to create new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L284)
Then Agent sets up base agent configuration path successfully at "<base_config_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L340)
And Agent attempts to set up agent-specific configuration path at "<agent_config_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L347)
Then AgentStateManager handles missing agent config error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L353)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is returned to MCP Server
And error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L313)
```

**Examples:**
| base_config_path | agent_config_path | expected_error_message |
|-----------------|-------------------|----------------------|
| agents/base/agent.json | agents/stories/agent.json | "Error: Could not load Story Agent configuration from agents/stories/agent.json: File not found" |
| test_data/agents/base/agent.json | test_data/agents/stories/agent.json | "Error: Could not load Story Agent configuration from test_data/agents/stories/agent.json: File not found" |
```

### Scenario Outline: Agent initialization with invalid agent_name

**Steps:**
```gherkin
Given MCP Server has received tool call with invalid agent_name "<invalid_agent_name>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L359)
And AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance with invalid agent_name "<invalid_agent_name>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L365)
And AgentStateManager attempts to create new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L284)
Then AgentStateManager handles invalid agent_name error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L377)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is returned to MCP Server
And error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L313)
```

**Examples:**
| invalid_agent_name | expected_error_message |
|-------------------|----------------------|
| invalid_agent | "Error: Agent 'invalid_agent' not found. Available agents: stories, clean_code" |
| nonexistent | "Error: Agent 'nonexistent' not found. Available agents: stories, clean_code" |
| empty_string | "Error: Agent name cannot be empty" |
```

### Scenario Outline: Agent initialization with corrupted config file

**Steps:**
```gherkin
Given agents/base/agent.json exists at "<base_config_path>" but is corrupted or invalid JSON with error "<json_error_type>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L326)
And AgentStateManager cache is empty
  [🔗](../../../../../../src/stories_acceptance_tests.py#L159)
When MCP Server requests Agent instance from AgentStateManager
  [🔗](../../../../../../src/stories_acceptance_tests.py#L167)
And AgentStateManager attempts to create new Agent instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L284)
And Agent attempts to load base configuration from "<base_config_path>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1165)
Then Agent handles JSON parsing error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L397)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is returned to MCP Server
And error is presented to user in chat
  [🔗](../../../../../../src/stories_acceptance_tests.py#L313)
```

**Examples:**
| base_config_path | json_error_type | expected_error_message |
|-----------------|----------------|----------------------|
| agents/base/agent.json | invalid_syntax | "Error: Could not parse base agent configuration from agents/base/agent.json: Invalid JSON syntax at line 5" |
| agents/base/agent.json | missing_brace | "Error: Could not parse base agent configuration from agents/base/agent.json: Expected '}' at end of file" |
| test_data/agents/base/agent.json | invalid_syntax | "Error: Could not parse base agent configuration from test_data/agents/base/agent.json: Invalid JSON syntax at line 3" |
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

