# 📝 Activity Logged To Project Area Not Bot Area

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 3  
**Story Type:** system  
**Test File:** test_activity_tracking_for_project_area.py  
**Test Class:** TestActivityTrackingLocation

## Story Description

Activity logs are written to the PROJECT's project_area, not the BOT's project_area. When story_bot is working on base_bot project, activity should be tracked in workspace_root/project_area/, NOT in story_bot/project_area/.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Action tracks activity
- **THEN** Activity log is written to `{project_area}/activity_log.json`
- **AND** Activity log is NOT written to bot directory
- **AND** Activity log location is determined by current_project.json
- **AND** Activity entries include correct action_state with full path

## Scenarios

### Scenario: Activity logged to project_area not bot area

**Test Method:** `test_activity_logged_to_project_area_not_bot_area`

```gherkin
GIVEN: story_bot is working on a project (e.g., base_bot)
AND: current_project.json exists with valid project_area
WHEN: activity is tracked
THEN: activity_log.json is written to workspace_root/
AND NOT: to workspace_root/agile_bot/bots/story_bot/
```

### Scenario: Activity log contains correct entry

**Test Method:** `test_activity_log_contains_correct_entry`

```gherkin
GIVEN: story_bot is working on a project
AND: current_project.json exists with valid project_area
WHEN: activity is tracked
THEN: Activity log has entry
AND: entry includes action_state='story_bot.shape.gather_context'
AND: entry includes timestamp
AND: entry includes status='started'
```
