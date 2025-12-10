# 📝 Track Activity for Gather Context Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Gather Context
**User:** Bot Behavior
**Sequential Order:** 3
**Story Type:** user

## Story Description

Track Activity for Gather Context Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** GatherContextAction executes

  **then** Action creates activity entry with timestamp, action name, behavior name

  **and** Activity entry appended to {project_area}/activity_log.json

## Scenarios

### Scenario: Track activity when gather_context action starts (happy_path)

**Steps:**
```gherkin
Given behavior is 'discovery'
And action is 'gather_context'
When gather_context action starts execution
Then Activity logger creates entry with:
- timestamp=[start timestamp]
- action_state='story_bot.discovery.gather_context'
- inputs={source_files_count: 2, context_type: "exploration"}
And Entry is appended to activity log at project_area/
And Activity log records action initiation
```


### Scenario: Track activity when gather_context action completes (happy_path)

**Steps:**
```gherkin
Given gather_context action started at timestamp='2025-12-03T10:00:00Z'
And activity log has entry for gather_context
When gather_context action finishes execution at timestamp='2025-12-03T10:05:30Z'
Then Activity logger creates completion entry with:
- action_state='story_bot.discovery.gather_context'
- outputs={questions_count: 5, evidence_count: 3, file_path: "clarifications.json"}
- duration=330 (seconds: 5.5 minutes)
And Entry is appended to activity log
And Activity log shows complete execution record with metrics and file path
```


### Scenario: Track multiple gather_context invocations across behaviors (happy_path)

**Steps:**
```gherkin
Given activity log contains entry for story_bot.shape.gather_context completed at 09:00
And activity log contains entry for story_bot.discovery.gather_context completed at 10:00
When both entries are present in activity log
Then activity log contains 2 separate entries:
- Entry 1: action_state='story_bot.shape.gather_context', timestamp='2025-12-03T09:00:00Z'
- Entry 2: action_state='story_bot.discovery.gather_context', timestamp='2025-12-03T10:00:00Z'
And Each entry has its own inputs (metrics/paths), outputs (metrics/paths), and duration
And Activity log distinguishes same action in different behaviors using full path
```

