# 📝 Proceed To Render Output

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Build Knowledge
**User:** Bot Behavior
**Sequential Order:** 3
**Story Type:** user

## Story Description

Proceed To Render Output functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** BuildKnowledgeAction completes execution

  **then** BuildKnowledgeAction saves Workflow State (per "Saves Behavior State" story)

  **and** BuildKnowledgeAction submits content for saving

  **and** Workflow automatically proceeds to render_output (auto_progress: true, no human confirmation needed)

## Scenarios

### Scenario: Proceed To Render Output (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
