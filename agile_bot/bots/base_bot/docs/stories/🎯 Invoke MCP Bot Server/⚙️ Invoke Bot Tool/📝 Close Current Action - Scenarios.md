# 📝 Close Current Action - Scenarios

## Scenario: Close current action and transition to next

**Given** workflow state is persisted with:
- current_behavior: "story_bot.shape"
- current_action: "story_bot.shape.gather_context"  
- completed_actions: ["story_bot.shape.initialize_project"]

**When** user invokes MCP tool `story_bot_close_current_action`

**Then** workflow saves "story_bot.shape.gather_context" to completed_actions

**And** workflow transitions state machine from "gather_context" to "decide_planning_criteria"

**And** workflow persists updated state to workflow_state.json

**And** MCP tool returns:
```json
{
  "status": "completed",
  "completed_action": "gather_context",
  "next_action": "decide_planning_criteria",
  "message": "Action 'gather_context' marked complete. Transitioned to 'decide_planning_criteria'."
}
```

---

## Scenario: Close final action and transition to next behavior

**Given** workflow state specifies:
- current_behavior: "story_bot.shape"
- current_action: "story_bot.shape.validate_rules"
- validate_rules is the final action in shape behavior
- Next behavior in config: "prioritization"

**When** user invokes `story_bot_close_current_action`

**Then** workflow saves "story_bot.shape.validate_rules" to completed_actions

**And** workflow marks behavior "shape" as complete

**And** workflow transitions to behavior "prioritization"

**And** workflow sets current_action to "story_bot.prioritization.initialize_project" (first action of next behavior)

**And** MCP tool returns:
```json
{
  "status": "completed",
  "completed_action": "validate_rules",
  "completed_behavior": "shape",
  "next_behavior": "prioritization",
  "next_action": "initialize_project",
  "message": "Behavior 'shape' complete. Transitioned to behavior 'prioritization', action 'initialize_project'."
}
```

---

## Scenario: Close action that requires confirmation but wasn't confirmed

**Given** workflow state specifies:
- current_behavior: "story_bot.shape"
- current_action: "story_bot.shape.initialize_project"
- initialize_project was executed but returned requires_confirmation: true
- User has NOT confirmed yet (action not in completed_actions)

**When** user invokes `story_bot_close_current_action`

**Then** MCP tool detects action is not in completed_actions

**And** MCP tool returns error:
```json
{
  "status": "error",
  "error": "Action requires confirmation",
  "current_action": "initialize_project",
  "message": "Action 'initialize_project' requires confirmation. Call the action tool with confirmation parameters first."
}
```

**And** workflow stays at "initialize_project" (does not transition)

**And** action is NOT saved to completed_actions

---

## Scenario: Close works regardless of invocation method

**Given** user previously invoked workflow using ANY of these tools:
- `story_bot_tool` (main bot tool routing to current behavior and action), OR
- `story_bot_shape_tool` (behavior tool routing to current action), OR
- `story_bot_shape_gather_context` (specific action tool)

**And** action has been completed (in completed_actions)

**When** user invokes `story_bot_close_current_action`

**Then** current action is marked complete

**And** workflow transitions to next action (or next behavior if last action)

**And** behavior is identical regardless of which tool was used to invoke the action

---

## Scenario: Close when action already completed (idempotent)

**Given** workflow state shows:
- current_action: "story_bot.shape.gather_context"
- completed_actions includes "story_bot.shape.gather_context" (already complete)

**When** user invokes `story_bot_close_current_action`

**Then** operation completes successfully (idempotent)

**And** gather_context remains in completed_actions (not duplicated)

**And** workflow state remains consistent

---

## Implementation Details

### MCP Tool Signature
```python
@mcp_server.tool(name='story_bot_close_current_action')
async def close_current_action(parameters: dict = None):
    """
    Mark the current action as complete and transition to next action.
    
    Call this after:
    1. Action tool returned instructions
    2. AI followed the instructions
    3. Human reviewed and confirmed completion
    
    Returns:
        status: "completed"
        completed_action: Name of action that was closed
        next_action: Name of next action (or same if at end)
        message: Human-readable status message
    """
```

### Workflow Operations
1. Read workflow_state.json to get current_behavior and current_action
2. Check if action is already in completed_actions (if not → error)
3. Extract action name from "bot.behavior.action" format
4. Call workflow.save_completed_action(action_name)
5. Call workflow.transition_to_next() to move within behavior
6. Check if this was the final action in behavior:
   - If yes: Mark behavior complete, transition to next behavior, initialize at first action
   - If no: Stay in current behavior, move to next action
7. Return status with completed action/behavior and next action/behavior names

### Error Handling
- If no workflow state exists → Return error "No active workflow found"
- If cannot determine current action → Return error "Cannot determine current action"
- If action not in completed_actions → Return error "Action requires confirmation" or "Action not complete"
- If transition fails → Log error, return appropriate message
- If no next behavior exists → Return "All behaviors complete"

### Behavior Transition Logic
- Check if current action is last in states list
- If yes and action is terminal (validate_rules):
  - Look up next behavior from bot config
  - Update workflow_state.json with new current_behavior
  - Set current_action to first action of next behavior
  - Reset or preserve completed_actions as appropriate

## Source Material

**Generated from:** Story "Close Current Action"  
**Date:** 2025-12-04  
**Context:** Detailed scenarios for implementing explicit action completion in bot workflow

