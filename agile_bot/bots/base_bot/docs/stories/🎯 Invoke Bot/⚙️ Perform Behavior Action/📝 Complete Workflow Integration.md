# 📝 Complete Workflow Integration

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Human  
**Sequential Order:** 4  
**Story Type:** user  
**Test File:** test_complete_workflow_integration.py

## Story Description

End-to-end integration test of the complete workflow demonstrating all features working together:
1. Workflow determines action from current_action (with fallback to completed_actions)
2. Guardrails load with number prefixes
3. Actions save state when called directly
4. Close tool marks complete and transitions
5. Jumping to different behavior-action updates state correctly

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** workflow starts at initialize_project
- **THEN** user can confirm and save to completed_actions
- **WHEN** user forwards to gather_context
- **THEN** workflow executes gather_context and saves state
- **WHEN** user closes gather_context
- **THEN** workflow transitions to decide_planning_criteria
- **WHEN** user jumps to discovery.gather_context (out of order)
- **THEN** state correctly shows discovery.gather_context (not initialize_project)
- **WHEN** user closes discovery action
- **THEN** workflow transitions properly
- **AND** all completed actions tracked across both behaviors

## Scenarios

### Scenario: Complete workflow end-to-end

**Test Method:** `test_complete_workflow_end_to_end`

```gherkin
GIVEN: bot is configured with multiple behaviors (shape, discovery)
AND: base_actions structure exists with next_action transitions
WHEN: Step 1: Initialize project
THEN: initialize_project completed and saved
WHEN: Step 2: Forward (transition from initialize_project)
THEN: forward_to_current_action checked completion and transitioned to gather_context
WHEN: Step 3: Execute gather_context
THEN: Executed gather_context, state saved
WHEN: Step 4: Close gather_context
THEN: gather_context closed, transitioned to decide_planning_criteria
WHEN: Step 5: Jump to discovery.gather_context (out of order)
THEN: Jumped to discovery.gather_context, state correctly shows discovery.gather_context
WHEN: Step 6: Close discovery.gather_context
THEN: discovery.gather_context closed, transitioned to decide_planning_criteria
AND: All completed actions tracked across both behaviors
```
