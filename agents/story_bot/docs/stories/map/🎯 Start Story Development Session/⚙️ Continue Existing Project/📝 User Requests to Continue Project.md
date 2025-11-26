# 📝 User Requests to Continue Project

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

User requests to continue working on an existing project in Cursor/VS Code chat, either by explicitly asking to continue or by referencing the project area

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When user requests to continue working on an existing project in Cursor/VS Code chat (e.g., "continue project", "resume work", "pick up where I left off", or by referencing project area), then AI Chat receives and processes the request
- When AI Chat processes continue request, then AI Chat identifies continuation keywords (e.g., "continue", "resume", "existing project", project area references) and determines Story Agent is needed

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Cursor/VS Code chat window is open
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And user has an existing project with agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Scenarios

### Scenario Outline: User requests to continue existing project

**Steps:**
```gherkin
Given user has typed request message "<request_message>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat receives and processes the request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L703)
Then AI Chat identifies continuation keywords: "<detected_keywords>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L709)
And AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
```

**Examples:**
| request_message | detected_keywords |
|----------------|-------------------|
| continue project | continue,project |
| resume work | resume,work |
| pick up where I left off | pick up,left off |
| continue working on my-story-project | continue,my-story-project |
| resume my-story-project | resume,my-story-project |

### Scenario Outline: User references project area directly

**Steps:**
```gherkin
Given user has typed request message referencing project area "<project_area_reference>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L851)
When AI Chat receives and processes the request
  [🔗](../../../../../../src/stories_acceptance_tests.py#L703)
Then AI Chat identifies project area reference: "<project_area_reference>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L709)
And AI Chat determines Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L721)
```

**Examples:**
| project_area_reference |
|------------------------|
| test_data/projects/my-story-project |
| my-story-project |
| ../projects/story-dev |
| C:\dev\my-story-project |

### Scenario: User request without continuation keywords

**Steps:**
```gherkin
Given user has typed request message without continuation keywords
  [🔗](../../../../../../src/stories_acceptance_tests.py#L820)
When AI Chat processes user message
  [🔗](../../../../../../src/stories_acceptance_tests.py#L826)
Then AI Chat does not identify continuation keywords
  [🔗](../../../../../../src/stories_acceptance_tests.py#L832)
And AI Chat does not determine Story Agent is needed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L839)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And AI Chat handles request through default flow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L845)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

