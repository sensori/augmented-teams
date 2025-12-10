# 📝 Reports Violations

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Validate Knowledge & Content Against Rules  
**Feature:** Code Scanner  
**Story:** Reports Violations

## Story Description

System generates violation reports in multiple formats (JSON, CHECKLIST, DETAILED, SUMMARY) with violations organized by behavior, rule, location, and severity.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** violation report is generated, **then** report is generated in requested format
- **When** violations are grouped, **then** violations are organized by behavior_name, rule_name, location, or severity
- **When** report is written to file, **then** file is created at specified output destination

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
And Behavior is "<behavior_name>"
And Common rules directory exists at 'agile_bot/bots/test_story_bot/rules/'
And Behavior rules directory exists at 'agile_bot/bots/test_story_bot/behaviors/<behavior_number>_<behavior_name>/3_rules/'
And Scanners have executed against knowledge graph
```

## Scenarios

### Scenario Outline: Violation report generation in different formats (happy_path)

**Steps:**
```gherkin
Given Violations have been detected: "<violations_data>"
And Report format is "<report_format>"
When Violation report is generated with violations "<violations_data>" and format "<report_format>"
Then Report structure is "<expected_report_structure>"
```

**Examples:**

| violations_data | report_format | expected_report_structure |
|----------------|---------------|--------------------------|
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | JSON | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "error", "timestamp": "..."}]} |
| 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | JSON | {"violations": [...]} - Array of 5 violation objects, each with exact line_number |
| No violations detected (empty array) | JSON | {"violations": []} |
| 100+ violations: multiple epics with noun-only names (lines 2, 10, 25, ...), features with capability nouns (lines 3, 11, 26, ...), stories with actors in names (lines 4, 12, 27, ...) | JSON | {"violations": [...]} - Array with all entries, each with exact line_number, pagination if needed |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | CHECKLIST | - [ ] Line 2 (epics[0].name): Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order" |
| 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | CHECKLIST | Checklist with 5 items, each showing line_number and fix suggestion |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | DETAILED | All fields + code_snippet showing line 2 + context + examples from rule file |
| 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | DETAILED | Each violation with full details including exact line_number, code_snippet, context |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, severity="error" | SUMMARY | {"violation_count": 1, "rule_count": 1, "severity_breakdown": {"error": 1}} |
| 5 violations from 3 rules: Epic "Order Management" (use_verb_noun_format, line 2), Feature "Payment Processing" (use_active_behavioral_language, line 3), Story "Customer places order" (use_verb_noun_format, line 4), Story sizing "15 days" (size_stories_3_to_12_days, line 5), Background step (use_background_for_common_setup, line 6) | SUMMARY | {"violation_count": 5, "rule_count": 3, "severity_breakdown": {...}} - Total count, grouped by rule, severity summary |
| No violations detected (empty array) | All formats | Format-appropriate empty structure (empty array, empty checklist, etc.) |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | JSON | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "error"}]} |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="warning" | JSON | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "warning"}]} |
| 5 violations with mixed severities: Epic "Order Management" (severity="error", line 2), Feature "Payment Processing" (severity="error", line 3), Story "Customer places order" (severity="warning", line 4), Story sizing "15 days" (severity="error", line 5), Background step (severity="info", line 6) | JSON | {"violations": [{"severity": "error", "line_number": 2, ...}, {"severity": "error", "line_number": 3, ...}, {"severity": "warning", "line_number": 4, ...}, {"severity": "error", "line_number": 5, ...}, {"severity": "info", "line_number": 6, ...}]} - All violations include severity field |
| 5 violations with mixed severities: Epic "Order Management" (severity="error", line 2), Feature "Payment Processing" (severity="error", line 3), Story "Customer places order" (severity="warning", line 4), Story sizing "15 days" (severity="error", line 5), Background step (severity="info", line 6) | SUMMARY | {"violation_count": 5, "rule_count": 3, "severity_breakdown": {"error": 3, "warning": 1, "info": 1}} - Severity breakdown shows counts per severity level |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | CHECKLIST | - [ ] Line 2 (epics[0].name) [ERROR]: Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order" - Severity shown in checklist item |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="warning" | CHECKLIST | - [ ] Line 2 (epics[0].name) [WARNING]: Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order" - Warning severity shown in checklist item |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | DETAILED | All fields + severity="error" prominently displayed + code_snippet showing line 2 + context + examples from rule file |

### Scenario Outline: Violation grouping and organization (happy_path)

**Steps:**
```gherkin
Given Violations have been detected: "<violations_data>"
And Violations are from behaviors "<behaviors>"
When Violations are grouped and organized with violations "<violations_data>" from behaviors "<behaviors>"
Then Grouping is "<expected_grouping>"
And Organization is "<expected_organization>"
```

**Examples:**

| violations_data | behaviors | expected_grouping | expected_organization |
|----------------|-----------|------------------|---------------------|
| Epic "Order Management" violation (common, use_verb_noun_format, line 2), Feature "Payment Processing" violation (shape, use_active_behavioral_language, line 3), Background step violation (scenarios, use_background_for_common_setup, line 4) | common, shape, scenarios | Grouped by rule_name, then by behavior_name | 3 groups organized by behavior: common (use_verb_noun_format, line 2), shape (use_active_behavioral_language, line 3), scenarios (use_background_for_common_setup, line 4), violations within each group |
| 10 violations from rule "use_active_behavioral_language": Feature "Payment Processing" (line 2), Feature "Order Management" (line 3), ... (lines 2-11) | shape | Single group | All violations in one group, behavior_name=shape, each with exact line_number |
| Violations from all 7 behaviors: Epic "Order Management" (common, line 2), Feature "Payment Processing" (shape, line 3), Epic "Explores Domain" (discovery, line 4), ... | all | Grouped by behavior_name, then by rule_name | Groups organized by behavior: common (line 2), shape (line 3), discovery (line 4), exploration, scenarios, tests, code, each violation with line_number |
| Epic "Order Management" violation (common, use_verb_noun_format, location="epics[0].name", line 2), Epic "Order Management" violation (shape, use_active_behavioral_language, location="epics[0].name", line 2) | common, shape | Grouped by location, then by behavior_name | Violations at same location (epics[0].name, line 2) grouped, behavior_name preserved |
| Epic "Order Management" violation (common, use_verb_noun_format, severity="error", line 2), Feature "Payment Processing" violation (shape, use_active_behavioral_language, severity="warning", line 3) | common, shape | Grouped by severity, then by behavior_name | Violations organized by severity level, behavior_name preserved, each with line_number |

### Scenario Outline: Report output and persistence (happy_path)

**Steps:**
```gherkin
Given Violations have been detected: "<violations_data>"
And Report format is "<report_format>"
And Output destination is "<output_destination>"
When Report is generated with format "<report_format>" and violations "<violations_data>" and written to "<output_destination>"
Then Output is "<expected_output>"
```

**Examples:**

| violations_data | report_format | output_destination | expected_output |
|----------------|--------------|-------------------|----------------|
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | JSON | File: validation_report.json | JSON file written with violations including line_number and severity, file exists at output path |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | CHECKLIST | File: validation_report.md | Markdown file written with checklist items showing line numbers and severity, file exists at output path |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | DETAILED | File: validation_report.txt | Text file written with detailed violations including line_number, severity, and code snippets, file exists at output path |
| Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | JSON | Console output | JSON printed to console with violations including line_number and severity, no file written |
| [{"rule_name": "...", "line_number": 2, "severity": "error", ...}] | JSON | File: validation_report.json (write fails) | Error reported with file path, report still generated in memory |
| [{"rule_name": "...", "line_number": 2, "severity": "warning", ...}] | JSON | File: validation_report.json (exists) | File overwritten with new violations or error if overwrite disabled |
| [{"rule_name": "...", "line_number": 2, "severity": "info", ...}] | JSON | File: nonexistent_dir/validation_report.json | Directory created or error if permissions insufficient |
| [{"rule_name": "...", "line_number": 2, "severity": "error", ...}] | JSON | File: validation_report.json (disk full) | Error reported: "Insufficient disk space" |

