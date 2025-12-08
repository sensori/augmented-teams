# [Story] Proceed To Decide Planning

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Gather Context
**User:** Bot Behavior  
**Sequential Order:** 5  
**Story Type:** user

## Story Description

Proceed To Decide Planning functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN GatherContextAction completes execution**
- **AND Human says action is done**
- **THEN GatherContextAction saves Workflow State (per "Saves Behavior State" story)**
- **AND Workflow injects next action instructions (per "Inject Next Behavior-Action" story)**
- **AND Workflow proceeds to decide_planning_criteria**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Seamless transition from gather_context to decide_planning_criteria

**Steps:**
```gherkin
Given behavior is 'discovery'
And gather_context action is complete
And Human confirms "done" or "proceed"
When gather_context action finalizes
Then Action saves Workflow State with:
  - current_behavior='story_bot.discovery'
  - current_action='story_bot.discovery.gather_context'
  - timestamp=[completion time]
And Action loads gather_context/action configuration
And Action reads next_action='decide_planning_criteria'
And Action injects AI instructions: "When done, proceed to decide_planning_criteria"
And AI invokes decide_planning_criteria tool
And Workflow transitions seamlessly to next action
```


### Scenario: User must confirm before transition

**Steps:**
```gherkin
Given gather_context action is complete
And Human has NOT yet confirmed completion
When gather_context action waits for human feedback
Then Action does NOT save workflow state as completed
And Action does NOT inject next action instructions
And Action does NOT proceed to decide_planning_criteria
And AI waits for human to say "done" before transitioning
```


### Scenario: Workflow state captures gather_context completion

**Steps:**
```gherkin
Given gather_context action completes at timestamp='2025-12-03T10:05:30Z'
And Human confirms "done"
When Action saves workflow state
Then workflow state is updated with:
  - current_action='story_bot.exploration.gather_context'
  - timestamp='2025-12-03T10:05:30Z'
And completed_actions list includes: {action_state: 'story_bot.exploration.gather_context', timestamp: '2025-12-03T10:05:30Z'}
And State persists to project_area/workflow state
And If workflow is interrupted after this point, gather_context is marked as completed
```


### Scenario: Workflow resumes at decide_planning_criteria after interruption

**Steps:**
```gherkin
Given gather_context is completed and chat was interrupted
When user reopens chat and invokes bot tool
Then Router forwards to decide_planning_criteria action
```


