# 📝 Track Activity for Strategy Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Decide Strategy Criteria Action
**User:** Bot Behavior
**Sequential Order:** 2
**Story Type:** user

## Story Description

Track Activity for Strategy Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** StrategyAction executes

  **then** Action creates activity entry with timestamp, action name, behavior name

  **and** Activity entry appended to {project_area}/activity_log.json

## Scenarios

### Scenario: Track activity when strategy action starts (happy_path)

**Steps:**
```gherkin
Given behavior is 'exploration'
And action is 'decide_strategy'
When decide_strategy action starts execution
Then Activity logger creates entry with:
- timestamp=[start timestamp]
- action_state='story_bot.exploration.decide_strategy'
- inputs={questions_count: 5, evidence_count: 3, context_file_path: "clarifications.json"}
And Entry is appended to activity log at project_area/
And Activity log records action initiation
```


### Scenario: Track activity when strategy action completes (happy_path)

**Steps:**
```gherkin
Given decide_strategy action started at timestamp='2025-12-03T10:15:00Z'
And activity log has entry for decide_strategy
When decide_strategy action finishes execution at timestamp='2025-12-03T10:25:00Z'
Then Activity logger creates completion entry with:
- action_state='story_bot.exploration.decide_strategy'
- outputs={criteria_count: 4, assumptions_count: 2, decisions_count: 3, file_path: "strategy.json"}
- duration=600 (seconds: 10 minutes)
And Entry is appended to activity log
And Activity log shows complete execution record with duration
```

