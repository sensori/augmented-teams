# 📝 AI Chat Invokes Story Agent MCP

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

AI Chat determines Story Agent is needed for continuation, selects appropriate MCP tool (agent_get_state for checking current state, agent_get_instructions for getting workflow instructions), and invokes Story Agent MCP Server

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When AI Chat determines Story Agent is needed for continuation, then AI Chat selects appropriate MCP tool (agent_get_state for checking current state, agent_get_instructions for getting workflow instructions) and prepares tool call with agent_name='stories'
- When AI Chat prepares MCP tool call, then AI Chat invokes Story Agent MCP Server via selected tool and MCP Server receives tool call with agent_name parameter

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given user has typed request message with continuation keywords
  [🔗](../../../../../../src/stories_acceptance_tests.py#L696)
And AI Chat has determined Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
```

## Scenarios

### Scenario Outline: AI Chat selects agent_get_state tool for continuation

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat determines Story Agent is needed for continuation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat needs to check current agent state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L764)
Then AI Chat selects agent_get_state tool
  [🔗](../../../../../../src/stories_acceptance_tests.py#L770)
And AI Chat prepares tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L733)
When AI Chat invokes Story Agent MCP Server via agent_get_state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L776)
Then MCP Server receives tool call with agent_name parameter 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L783)
```

**Examples:**
| request_message |
|----------------|
| continue project |
| resume work |
| check project status |
| what is the current workflow state |

### Scenario Outline: AI Chat selects agent_get_instructions tool for continuation

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat determines Story Agent is needed for continuation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat needs to get workflow instructions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L795)
Then AI Chat selects agent_get_instructions tool
  [🔗](../../../../../../src/stories_acceptance_tests.py#L801)
And AI Chat prepares tool call with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L733)
When AI Chat invokes Story Agent MCP Server via agent_get_instructions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L807)
Then MCP Server receives tool call with agent_name parameter 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L814)
```

**Examples:**
| request_message |
|----------------|
| continue from where I left off |
| resume workflow |
| pick up where I left off |
| continue working |

### Scenario: AI Chat handles MCP Server unavailable during continuation

**Steps:**
```gherkin
Given user has typed request message 'continue project'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
And MCP Server is not available or not responding
  [🔗](../../../../../../src/stories_acceptance_tests.py#L857)
When AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
And AI Chat attempts to invoke MCP Server
  [🔗](../../../../../../src/stories_acceptance_tests.py#L863)
Then system handles MCP Server unavailability gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L878)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And user receives appropriate error message
  [🔗](../../../../../../src/stories_acceptance_tests.py#L884)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

