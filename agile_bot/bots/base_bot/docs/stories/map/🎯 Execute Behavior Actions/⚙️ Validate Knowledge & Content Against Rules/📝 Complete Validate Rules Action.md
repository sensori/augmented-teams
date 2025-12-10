# 📝 Complete Validate Rules Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Validate Knowledge & Content Against Rules
**User:** Bot Behavior
**Sequential Order:** 3
**Story Type:** user

## Story Description

Complete Validate Rules Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** ValidateRulesAction completes execution

  **then** Action returns instructions with base_instructions (primary) and validation_rules (supporting context)

  **and** Action returns content_to_validate information (project location, rendered outputs, clarification.json, planning.json, report_path)

  **then** Action presents validation results to user

  **and** Action instructions include report_path where validation report should be saved (validation-report.md in docs/stories/)

- **When** AI generates validation report

  **then** AI saves validation report to file at report_path location

- **When** Human says action is done

  **then** ValidateRulesAction saves Workflow State (per "Saves Behavior State" story)

  **and** validate_rules is terminal action (next_action: null, workflow completes)

## Scenarios

### Scenario: validate_rules marks workflow as complete (happy_path)

**Steps:**
```gherkin
Given validate_rules action is complete
And validate_rules is terminal action (next_action=null)
When validate_rules finalizes
Then Workflow is marked as complete (no next action)
```


### Scenario: validate_rules does NOT inject next action instructions (happy_path)

**Steps:**
```gherkin
Given validate_rules action is complete
And validate_rules is terminal action
When validate_rules finalizes
Then No next action instructions injected
```


### Scenario: Workflow state shows all actions completed (happy_path)

**Steps:**
```gherkin
Given validate_rules completes as final action
When Action tracks completion
Then Activity log records the completion
```


### Scenario: Activity log records full workflow completion (happy_path)

**Steps:**
```gherkin
Given validate_rules completes at timestamp
When Activity logger records completion
Then Activity log shows validate_rules completed and workflow finished
```

