# [Story] Proceed To Render Output

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Build Knowledge
**User:** Bot Behavior  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Proceed To Render Output functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN BuildKnowledgeAction completes execution**
- **THEN BuildKnowledgeAction saves Workflow State (per "Saves Behavior State" story)**
- **AND BuildKnowledgeAction submits content for saving**
- **AND Workflow automatically proceeds to render_output (auto_progress: true, no human confirmation needed)**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Proceed To Render Output

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

