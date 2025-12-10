# 📝 Run Scanners Against Knowledge Graph

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Validate Knowledge & Content Against Rules  
**Feature:** Code Scanner  
**Story:** Run Scanners Against Knowledge Graph

## Story Description

Scanners execute against knowledge graph and detect violations with exact line numbers and locations.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** scanners are executed against knowledge graph, **then** violations are detected at exact line numbers
- **When** violations are detected, **then** violation details include rule_name, location, violation_message, and severity
- **When** multiple scanners execute, **then** violations from all scanners are aggregated

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
And Behavior is "<behavior_name>"
And Common rules directory exists at 'agile_bot/bots/test_story_bot/rules/'
And Behavior rules directory exists at 'agile_bot/bots/test_story_bot/behaviors/<behavior_number>_<behavior_name>/3_rules/'
And Scanners are discovered and registered for <behavior> and <rule_file>:
  - Common rules: 'agile_bot/bots/test_story_bot/rules/'
  - Behavior rules: 'agile_bot/bots/test_story_bot/behaviors/<behavior_number>_<behavior_name>/3_rules/'
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
```

## Scenarios

### Scenario Outline: Scanners detect violations in knowledge graph (happy_path)

**Steps:**
```gherkin
Given Knowledge graph contains "<knowledge_graph_problems>"
And Rule file is "<rule_file>"
When Scanners are executed against knowledge graph containing "<knowledge_graph_problems>"
Then Violations are detected at "<expected_violation_line>"
And Violation details are "<expected_violation_details>"
And Report format is "<expected_report_format>"
And Report structure is "<expected_report_structure>"
```

**Examples:**

| rule_file | knowledge_graph_problems | expected_violation_line | expected_violation_details | expected_report_format | expected_report_structure |
|-----------|------------------------|----------------------|---------------------------|----------------------|------------------------|
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Order Management"}]} | line 2 (epics[0].name) | violation_message: "Epic name uses noun-only format instead of verb-noun", location: "epics[0].name" | JSON report | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format instead of verb-noun", "line_number": 2, "location": "epics[0].name", "severity": "error"}]} |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order"}]}]}]} | None (0 violations) | No violations - correct verb-noun format | JSON report | {"violations": []} |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]} | line 4 (epics[0].features[0].stories[0].name) | violation_message: "Story name contains actor 'Customer' - actors should not be in story names", location: "epics[0].features[0].stories[0].name" | JSON report | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Story name contains actor 'Customer' - actors should not be in story names", "line_number": 4, "location": "epics[0].features[0].stories[0].name", "severity": "error"}]} |
| use_active_behavioral_language.json | {"epics": [{"name": "Places Order", "features": [{"name": "Payment Processing"}]}]} | line 3 (epics[0].features[0].name) | violation_message: "Feature uses capability noun 'Processing' instead of behavioral language", location: "epics[0].features[0].name" | JSON report | {"violations": [{"rule_name": "use_active_behavioral_language", "rule_file": "agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json", "violation_message": "Feature uses capability noun 'Processing' instead of behavioral language", "line_number": 3, "location": "epics[0].features[0].name", "severity": "error"}]} |
| size_stories_3_to_12_days.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]} | line 4 (epics[0].features[0].stories[0].sizing) | violation_message: "Story sizing '15 days' is outside 3-12 day range", location: "epics[0].features[0].stories[0].sizing" | JSON report | {"violations": [{"rule_name": "size_stories_3_to_12_days", "rule_file": "agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json", "violation_message": "Story sizing '15 days' is outside 3-12 day range", "line_number": 4, "location": "epics[0].features[0].stories[0].sizing", "severity": "error"}]} |
| use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json, size_stories_3_to_12_days.json | {"epics": [{"name": "Order Management", "features": [{"name": "Payment Processing", "stories": [{"name": "Customer places order", "sizing": "15 days"}]}]}]} | Multiple lines: 2, 3, 4, 5 | 4 violations: epic noun-only (line 2), feature capability noun (line 3), story actor in name (line 4), story sizing (line 5) | JSON report with array | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 2, ...}, {"rule_name": "use_active_behavioral_language", "line_number": 3, ...}, {"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 4, ...}, {"rule_name": "size_stories_3_to_12_days", "line_number": 5, ...}]} - 4 entries, each with exact line_number |
| use_verb_noun_format_for_story_elements.json | {} | None (0 violations) | Empty graph is valid - no violations | JSON report | {"violations": []} |
| use_active_behavioral_language.json | {"epics": [{"name": "Places Order" | Error at parse | Error: JSON parse failure at line 1, message: "Expecting ',' delimiter or '}'" | Error report | {"error": "JSON parse failure", "message": "Expecting ',' delimiter or '}'", "line": 1} |
| use_verb_noun_format_for_story_elements.json | (file does not exist) | Error | Error: Knowledge graph file not found | Error report | {"error": "Knowledge graph file not found", "path": "agile_bot/bots/test_story_bot/docs/stories/story-graph.json"} |
| All rule files (all behaviors) | {"epics": [{"name": "Order Management"}, {"name": "Payment Processing"}, ...], "features": [...], "stories": [...]} (large structure with 50+ violations) | Multiple lines (50+) | 50+ violations reported, each with exact line_number and location | JSON report | {"violations": [...]} - array with all entries, each with exact line_number, pagination if needed |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "epic_ref": "epics[0]"}]}]} | Error at validation | Error: Circular reference detected in knowledge graph structure | Error report | {"error": "Circular reference detected", "location": "epics[0].features[0].epic_ref"} |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": null}]} | line 2 (epics[0].name) | violation_message: "Epic name is null", location: null (invalid) | JSON report | {"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 2, "location": null, "violation_message": "Epic name is null"}]} - violation with null/empty location fields |

### Scenario Outline: Single scanner execution detects violations (happy_path)

**Steps:**
```gherkin
Given Knowledge graph contains "<knowledge_graph_problems>"
And Scanner "<scanner>" is selected for execution
When Single scanner "<scanner>" is executed against knowledge graph containing "<knowledge_graph_problems>"
Then Violation line is "<expected_violation_line>"
And Violation details are "<expected_violation_details>"
```

**Examples:**

| scanner | knowledge_graph_problems | expected_violation_line | expected_violation_details |
|---------|------------------------|------------------------|---------------------------|
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Order Management"}]} | line 2 (epics[0].name) | line_number: 2, location: "epics[0].name", message: "Epic name uses noun-only format instead of verb-noun" |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order"}]}]}]} | None (0 violations) | No violations - correct verb-noun format |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]} | line 4 (epics[0].features[0].stories[0].name) | line_number: 4, location: "epics[0].features[0].stories[0].name", message: "Story name contains actor 'Customer' - actors should not be in story names" |
| use_active_behavioral_language.json | {"epics": [{"name": "Places Order", "features": [{"name": "Payment Processing"}]}]} | line 3 (epics[0].features[0].name) | line_number: 3, location: "epics[0].features[0].name", message: "Feature uses capability noun 'Processing' instead of behavioral language" |
| size_stories_3_to_12_days.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]} | line 4 (epics[0].features[0].stories[0].sizing) | line_number: 4, location: "epics[0].features[0].stories[0].sizing", message: "Story sizing '15 days' is outside 3-12 day range" |
| use_verb_noun_format_for_story_elements.json | {} | None (0 violations) | Empty graph is valid - no violations |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...]} (large structure with 1000+ stories) | Multiple lines (all violations detected) | All violations detected with exact line numbers, violations array contains all matches |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order" | Error at parse | Error: JSON parse failure, message: "Expecting ',' delimiter or '}'", scanner doesn't crash |
| use_verb_noun_format_for_story_elements.json | (file does not exist) | Error | Error: Knowledge graph file not found at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json' |
| use_verb_noun_format_for_story_elements.json | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "epic_ref": "epics[0]"}]}]} | Error at validation | Error: Circular reference detected in knowledge graph structure |

### Scenario Outline: Multiple scanners execute and aggregate violations (happy_path)

**Steps:**
```gherkin
Given Scanners are discovered and registered
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Knowledge graph contains "<knowledge_graph_problems>"
And Multiple scanners "<scanners>" are selected for execution
When Multiple scanners "<scanners>" are executed against knowledge graph containing "<knowledge_graph_problems>"
Then Violations per scanner are "<expected_violations_per_scanner>"
And Total violations are "<expected_total_violations>"
```

**Examples:**

| scanners | knowledge_graph_problems | expected_violations_per_scanner | expected_total_violations |
|----------|------------------------|--------------------------------|---------------------------|
| All common rules (7 scanners: VerbNounScanner, ActiveLanguageScanner, ...) | {"epics": [{"name": "Order Management", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]} | 3 scanners report violations (VerbNounScanner: line 2, VerbNounScanner: line 4, ActiveLanguageScanner: line 2), 4 report none | 3 violations total with exact line numbers |
| All shape behavior rules (25 scanners: StorySizingScanner, BehavioralJourneyScanner, ...) | {"epics": [{"name": "Order Management", "features": [{"name": "Payment Processing", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]} | 5 scanners report violations (VerbNounScanner: line 2, ActiveLanguageScanner: line 3, StorySizingScanner: line 5, ...), 20 report none | 5 violations total with exact line numbers |
| All behavior rules (50+ scanners across all behaviors) | {"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...], "scenarios": [...], "tests": [...]} (large structure with multiple violations) | 10 scanners report violations (various lines), 40+ report none | 10 violations total, each with exact line_number |
| All scanners (all behaviors) | {"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Submits payment", "sizing": "5 days"}]}]}]} | All scanners report 0 violations | 0 violations total |
| All scanners (all behaviors) | {"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...], "scenarios": [...], "tests": [...]} (large structure with violations across all rule types) | All scanners report violations (many lines) | 50+ violations total, each with exact line_number |
| All scanners (all behaviors) | {"epics": [{"name": "Places Order" | All scanners report parse error | Error: JSON parse failure at line 1 |
| All scanners (all behaviors) | {} | All scanners report 0 violations | 0 violations total |

### Scenario Outline: Scanner execution order and isolation (edge_case)

**Steps:**
```gherkin
Given Scanners are discovered and registered
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Knowledge graph contains "<knowledge_graph_problems>"
And Scanner execution order is "<scanner_execution_order>"
And Scanner failure behavior is "<scanner_failure_behavior>"
When Scanners execute in "<scanner_execution_order>" order against knowledge graph containing "<knowledge_graph_problems>"
Then Result is "<expected_result>"
```

**Examples:**

| scanner_execution_order | knowledge_graph_problems | scanner_failure_behavior | expected_result |
|------------------------|------------------------|-------------------------|----------------|
| Sequential execution | {"epics": [{"name": "Order Management"}]} | Scanner 1 (VerbNounScanner) throws exception, Scanner 2 (ActiveLanguageScanner) succeeds | Scanner 1 error logged with exception details, Scanner 2 executes and reports violation at line 2 |
| Parallel execution | {"epics": [{"name": "Order Management"}]} | Scanner 1 (VerbNounScanner) fails, Scanner 2 (ActiveLanguageScanner) succeeds | Both results reported: Scanner 1 error logged, Scanner 2 reports violation at line 2, errors isolated |
| Sequential execution | {"epics": [{"name": "Order Management"}]} | All scanners succeed | All scanners execute in order, violations reported with line numbers |
| Sequential execution | {"epics": [...], "features": [...], "stories": [...]} (large structure with 1000+ stories) | Scanner 1 (VerbNounScanner) timeout after 30s | Timeout error reported with scanner name, next scanner continues execution |
| Parallel execution | {"epics": [...], "features": [...], "stories": [...]} (large structure with 1000+ stories) | Scanner 1 (VerbNounScanner) memory error | Error isolated with scanner name, other scanners complete and report violations |

