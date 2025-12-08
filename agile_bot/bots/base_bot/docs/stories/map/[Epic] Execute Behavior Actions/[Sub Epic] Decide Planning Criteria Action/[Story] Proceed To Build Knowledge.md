# [Story] Proceed To Build Knowledge

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Decide Planning Criteria Action
**User:** Bot Behavior  
**Sequential Order:** 4  
**Story Type:** user

## Story Description

Proceed To Build Knowledge functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN PlanningAction completes execution**
- **WHEN Human says action is done**
- **THEN PlanningAction saves Workflow State (per "Saves Behavior State" story)**
- **AND Workflow injects next action instructions (per "Inject Next Behavior-Action" story)**
- **AND Workflow proceeds to build_knowledge**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Seamless transition from planning to build_knowledge

**Steps:**
```gherkin
Given behavior is 'discovery'
And decide_planning_criteria action is complete
And Human confirms "done" or "proceed"
When decide_planning_criteria action finalizes
Then Action saves Workflow State with:
  - current_behavior='story_bot.discovery'
  - current_action='story_bot.discovery.decide_planning_criteria'
  - timestamp=[completion time]
And Action loads decide_planning_criteria/action configuration
And Action reads next_action='build_knowledge'
And Action injects AI instructions: "When done, proceed to build_knowledge"
And AI invokes build_knowledge tool
And Workflow transitions seamlessly to next action
```


### Scenario: User must confirm before transition

**Steps:**
```gherkin
Given decide_planning_criteria action is complete
And Human has NOT yet confirmed completion
When decide_planning_criteria action waits for human feedback
Then Action does NOT save workflow state as completed
And Action does NOT inject next action instructions
And Action does NOT proceed to build_knowledge
And AI waits for human to say "done" before transitioning
```


### Scenario: Workflow state captures planning completion

**Steps:**
```gherkin
Given decide_planning_criteria action completes at timestamp='2025-12-03T10:25:00Z'
And Human confirms "done"
When Action saves workflow state
Then workflow state is updated with:
  - current_action='story_bot.exploration.decide_planning_criteria'
  - timestamp='2025-12-03T10:25:00Z'
And completed_actions list includes: {action_state: 'story_bot.exploration.decide_planning_criteria', timestamp: '2025-12-03T10:25:00Z'}
And State persists to project_area/workflow state
And If workflow is interrupted after this point, planning is marked as completed
```


