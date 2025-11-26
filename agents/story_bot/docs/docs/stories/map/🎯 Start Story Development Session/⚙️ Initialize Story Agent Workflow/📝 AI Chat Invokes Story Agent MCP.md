# 📝 AI Chat Invokes Story Agent MCP

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../initialize-workflow-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Initialize Story Agent Workflow

## Story Description

AI Chat detects story shaping request and calls Story Agent MCP Server via agent_get_state or agent_get_instructions tool

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When AI Chat processes user message and attached documents, then AI Chat identifies story shaping keywords (e.g., 'shaping', 'planning', 'story map', 'new project') and determines Story Agent is needed
- When AI Chat determines Story Agent is needed, then AI Chat selects appropriate MCP tool (agent_get_state for checking current state, agent_get_instructions for getting workflow instructions) and prepares tool call with agent_name='stories'
- When AI Chat prepares MCP tool call, then AI Chat invokes Story Agent MCP Server via selected tool and MCP Server receives tool call with agent_name parameter

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Cursor/VS Code chat window is open
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And user has attached documents to chat window
  [🔗](../../../../../../src/stories_acceptance_tests.py#L690)
```

## Scenarios

### Scenario Outline: AI Chat detects story shaping keywords and invokes MCP

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat processes user message and attached documents
  [🔗](../../../../../../src/stories_acceptance_tests.py#L703)
Then AI Chat identifies story shaping keywords: "<detected_keywords>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L709)
And AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
When AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
Then AI Chat selects appropriate MCP tool: "<selected_tool>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L727)
And AI Chat prepares tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L733)
When AI Chat invokes Story Agent MCP Server via selected tool
  [🔗](../../../../../../src/stories_acceptance_tests.py#L739)
Then MCP Server receives tool call with agent_name parameter 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L745)
```

**Examples:**
| request_message | detected_keywords | selected_tool |
|----------------|-------------------|--------------|
| start shaping | shaping | agent_get_instructions |
| plan new project | planning,new project | agent_get_instructions |
| build story map | story map | agent_get_instructions |
| check story status | story | agent_get_state |

### Scenario Outline: AI Chat selects agent_get_state tool

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat processes request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L758)
And AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat needs to check current agent state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L764)
Then AI Chat selects agent_get_state tool
  [🔗](../../../../../../src/stories_acceptance_tests.py#L770)
And AI Chat prepares tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L733)
When AI Chat invokes agent_get_state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L776)
Then MCP Server receives agent_get_state tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L783)
```

**Examples:**
| request_message |
|----------------|
| check story status |
| what is the current workflow state |
| show me the agent state |

### Scenario Outline: AI Chat selects agent_get_instructions tool

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat processes request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L758)
And AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat needs to get workflow instructions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L795)
Then AI Chat selects agent_get_instructions tool
  [🔗](../../../../../../src/stories_acceptance_tests.py#L801)
And AI Chat prepares tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L733)
When AI Chat invokes agent_get_instructions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L807)
Then MCP Server receives agent_get_instructions tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L814)
```

**Examples:**
| request_message |
|----------------|
| plan new project |
| start shaping |
| build story map |
| create story specification |

### Scenario Outline: AI Chat handles ambiguous request without keywords

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat processes user message
  [🔗](../../../../../../src/stories_acceptance_tests.py#L826)
Then AI Chat does not identify story shaping keywords
  [🔗](../../../../../../src/stories_acceptance_tests.py#L832)
And AI Chat does not determine Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L839)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And AI Chat handles request through default flow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L845)
```

**Examples:**
| request_message |
|----------------|
| hello |
| what can you do |
| help me with my code |
| explain this function |

### Scenario Outline: AI Chat handles MCP Server unavailable

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
And MCP Server is not available or not responding due to "<unavailability_reason>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L857)
When AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat attempts to invoke MCP Server
  [🔗](../../../../../../src/stories_acceptance_tests.py#L863)
Then system handles MCP Server unavailability gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L878)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And user receives error message "<expected_error_message>"
```

**Examples:**
| request_message | unavailability_reason | expected_error_message |
|----------------|----------------------|----------------------|
| build story map | server_not_running | "MCP Server is not available. Please check server status." |
| start shaping | connection_timeout | "Could not connect to MCP Server. Connection timed out." |
| plan new project | server_crashed | "MCP Server error. Please restart the server." |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

