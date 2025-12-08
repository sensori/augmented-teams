# [Story] Complete Validate Rules Action

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Validate Knowledge & Content Against Rules
**User:** Bot Behavior  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Complete Validate Rules Action functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN ValidateRulesAction completes execution**
- **THEN Action returns instructions with base_instructions (primary) and validation_rules (supporting context)**
- **AND Action returns content_to_validate information (project location, rendered outputs, clarification.json, planning.json, report_path)**
- **THEN Action presents validation results to user**
- **AND Action instructions include report_path where validation report should be saved (validation-report.md in docs/stories/)**
- **WHEN AI generates validation report**
- **THEN AI saves validation report to file at report_path location**
- **WHEN Human says action is done**
- **THEN ValidateRulesAction saves Workflow State (per "Saves Behavior State" story)**
- **AND validate_rules is terminal action (next_action: null, workflow completes)**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: validate_rules marks workflow as complete

**Steps:**
```gherkin
Given validate_rules action is complete
And validate_rules is terminal action (next_action=null)
When validate_rules finalizes
Then Workflow is marked as complete (no next action)
```


### Scenario: validate_rules does NOT inject next action instructions

**Steps:**
```gherkin
Given validate_rules action is complete
And validate_rules is terminal action
When validate_rules finalizes
Then No next action instructions injected
```


### Scenario: Workflow state shows all actions completed

**Steps:**
```gherkin
Given validate_rules completes as final action
When Action tracks completion
Then Activity log records the completion
```


### Scenario: Activity log records full workflow completion

**Steps:**
```gherkin
Given validate_rules completes at timestamp
When Activity logger records completion
Then Activity log shows validate_rules completed and workflow finished
```


