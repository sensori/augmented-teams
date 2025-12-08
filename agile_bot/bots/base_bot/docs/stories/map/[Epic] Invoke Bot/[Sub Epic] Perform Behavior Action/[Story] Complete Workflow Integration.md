# [Story] Complete Workflow Integration

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Perform Behavior Action
**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Complete Workflow Integration functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN workflow starts at initialize_project**
- **THEN user can confirm and save to completed_actions**
- **WHEN user forwards to gather_context**
- **THEN workflow executes gather_context and saves state**
- **WHEN user closes gather_context**
- **THEN workflow transitions to decide_planning_criteria**
- **WHEN user jumps to discovery.gather_context (out of order)**
- **THEN state correctly shows discovery.gather_context (not initialize_project)**
- **WHEN user closes discovery action**
- **THEN workflow transitions properly**
- **AND all completed actions tracked across both behaviors**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Complete end-to-end workflow test demonstrating all fixes working together

**Steps:**
```gherkin
Flow:
1. Start at initialize_project
2. Confirm → Saves to completed_actions
3. Forward to gather_context
4. Close gather_context → Transitions to decide_planning_criteria
5. Jump to discovery.gather_context (out of order)
6. Verify state shows discovery.gather_context (not initialize_project)
7. Close and verify proper transition
8. Verify all completed actions tracked across both behaviors
```


