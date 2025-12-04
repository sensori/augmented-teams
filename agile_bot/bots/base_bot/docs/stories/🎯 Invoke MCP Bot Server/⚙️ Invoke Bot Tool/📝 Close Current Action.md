# 📝 Close Current Action

## Story

**As a** user of the bot workflow  
**I want to** explicitly mark the current action as complete  
**So that** the workflow transitions to the next action only when I'm ready

## Background

- User has invoked a bot action tool (e.g., `story_bot_shape_gather_context`)
- Action has returned instructions
- AI has followed the instructions (gathered context, answered questions, etc.)
- Human has reviewed the results
- User is ready to move to the next action

## Acceptance Criteria

### Scenario: Close current action and transition to next

**Given** workflow is at action "gather_context"  
**And** action has NOT been marked complete yet  
**When** user invokes `close_current_action` tool  
**Then** action "gather_context" is saved to completed_actions  
**And** workflow transitions to "decide_planning_criteria" (next action)  
**And** response includes completed action and next action names

### Scenario: Close action that requires confirmation but wasn't confirmed

**Given** workflow is at action "initialize_project"  
**And** action requires confirmation (not confirmed yet)  
**When** user invokes `close_current_action` tool  
**Then** tool returns error: "Action requires confirmation"  
**And** workflow stays at "initialize_project" (does not transition)  
**And** response message indicates user must confirm first  
**And** action is NOT saved to completed_actions

### Scenario: Close final action and transition to next behavior

**Given** workflow is at behavior "shape" action "validate_rules" (final action in behavior)  
**When** user invokes `close_current_action` tool  
**Then** action "validate_rules" is saved to completed_actions  
**And** current behavior "shape" is marked complete  
**And** workflow transitions to next behavior "prioritization"  
**And** workflow initializes at first action "initialize_project" of next behavior  
**And** response indicates transition to next behavior

### Scenario: Close action works regardless of how workflow was invoked

**Given** user invoked workflow via ANY tool:
- `story_bot_tool` (main bot tool), OR
- `story_bot_shape_tool` (behavior tool), OR  
- `story_bot_shape_gather_context` (specific action tool)

**When** user invokes `close_current_action` tool  
**Then** current action is marked complete and workflow transitions  
**And** if current action is the last action in behavior, workflow transitions to next behavior  
**And** behavior is the same regardless of invocation method

## Implementation Notes

- Close tool should work at bot level (not behavior-specific)
- Tool name: `{bot_name}_close_current_action` (e.g., `story_bot_close_current_action`)
- Should handle edge cases (already complete, final action, etc.)
- Should return clear status message about what happened

## Out of Scope

- Validation that instructions were followed correctly (that's validate_rules action's job)
- Undoing a close (may be future feature)
- Skipping actions (must complete current before moving to next)
- Manual jumps to different behaviors/actions (covered in "Forward To Behavior and Current Action" story)

## Source Material

**Generated from:** Architectural fix for workflow action completion  
**Date:** 2025-12-04  
**Context:** Fixing the issue where actions were transitioning immediately instead of waiting for explicit completion

