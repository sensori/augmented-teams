# Code Scanner Stories - Testing Tables

## Overview
This document defines testing tables for Code Scanner stories that will be used to test each story against all rules in isolation. Each table uses parameterized backgrounds and robust example tables to cover happy paths, edge cases, and error cases.

## Behavior-to-Rule Mapping

Rules are organized by behavior. Each rule belongs to one behavior. **The directory structure is fixed and will never change:**

### Fixed Directory Structure

- **Common Rules Path** (fixed, never changes):
  - `agile_bot/bots/test_story_bot/rules/`

- **Behavior Rules Path** (fixed pattern, never changes):
  - `agile_bot/bots/test_story_bot/behaviors/{behavior_number}_{behavior_name}/3_rules/`
  - Example: `agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/`
  - Example: `agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/`

### Rules by Behavior

- **common**: Rules that apply across all behaviors (~7 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/rules/`
  - Examples: `use_verb_noun_format_for_story_elements.json`, `use_active_behavioral_language.json`

- **shape**: Rules specific to the shape behavior (~25 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/`
  - Examples: `use_active_behavioral_language.json`, `size_stories_3_to_12_days.json`, `enforce_behavioral_journey_flow.json`

- **discovery**: Rules specific to the discovery behavior (~5 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/`
  - Examples: `apply_exhaustive_decomposition.json`, `ensure_vertical_slices.json`

- **exploration**: Rules specific to the exploration behavior (~8 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/5_exploration/3_rules/`
  - Examples: `behavioral_ac_at_story_level.json`

- **scenarios**: Rules specific to the scenarios behavior (~9 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/`
  - Examples: `use_background_for_common_setup.json`, `given_uses_state_language.json`

- **tests**: Rules specific to the tests behavior (~30 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/`
  - Examples: `use_exact_variable_names.json`, `use_arrange_act_assert.json`, `mock_only_boundaries.json`

- **code**: Rules specific to the code behavior (~43 rules)
  - **Fixed Path**: `agile_bot/bots/test_story_bot/behaviors/8_code/3_rules/`
  - Examples: `production_code_api_design.json`, `production_code_single_responsibility.json`

**Total**: ~127 rules across all behaviors

**Note**: The structure `behaviors/{number}_{name}/3_rules/` is fixed and will never change.

## Stories Under Test
1. "proactively Validate knowledge against rules"
2. "Discovers Scanners"
3. "Run Scanners against Knowledge Graph"
4. "Reports Violations"

(Excluding "Run AST Scanners against Knowledge Graph (OUT OF SCOPE)")

---

## Common Background

The following background applies to ALL stories and scenarios:

```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
And Behavior is '{behavior_name}'
And Common rules directory exists at 'agile_bot/bots/test_story_bot/rules/'
And Behavior rules directory exists at 'agile_bot/bots/test_story_bot/behaviors/{behavior_number}_{behavior_name}/3_rules/'
```

---

## Story 1: "proactively Validate knowledge against rules"

### Scenario
```gherkin
Given Action is 'build_knowledge'
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Behavior has validation rules '{validation_rules}'
And Validation rules have code scanners '{code_scanners}'
And Code scanners are stubbed to return '{code_scanner_output}'
When Build knowledge action forwards to validate_action_bot with knowledge graph at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
Then Validate action bot runs stubbed code scanners '{code_scanners}' against knowledge graph
And Stubbed scanners return '{code_scanner_output}'
And Validation report is generated with '{code_scanner_output}'
And Enhanced instructions are returned to build_knowledge action
And Enhanced instructions contain '{enhanced_instructions}'
```

### Testing Table: Instruction Generation and Forwarding

| Test ID | Behavior | Validation Rules | Code Scanners (Stubbed) | Code Scanner Output (JSON) | Enhanced Instructions (Full Text) |
|---------|----------|-----------------|------------------------|---------------------------|----------------------------------|
| T1.1 | shape | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json | VerbNounScanner, ActiveLanguageScanner | ```json<br>{<br>  "violations": [<br>    {<br>      "rule_name": "use_verb_noun_format_for_story_elements",<br>      "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json",<br>      "violation_message": "Epic name uses noun-only format instead of verb-noun",<br>      "line_number": 2,<br>      "location": "epics[0].name",<br>      "severity": "error"<br>    }<br>  ],<br>  "scanners_executed": 2,<br>  "scanners_passed": 1,<br>  "scanners_failed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Report<br><br>Code scanners executed: 2<br>Violations detected: 1<br><br>### Violations:<br><br>- **Rule**: use_verb_noun_format_for_story_elements<br>  - **Location**: Line 2 (epics[0].name)<br>  - **Issue**: Epic name 'Order Management' uses noun-only format instead of verb-noun<br>  - **Fix**: Change to verb-noun format like 'Places Order' or 'Manages Orders'<br><br>Please review sections indicated by scanner violations against appropriate rules and make necessary edit, then run against all rules and make final edits before considering the knowledge generation action to be complete." |
| T1.2 | shape | use_verb_noun_format_for_story_elements.json, size_stories_3_to_12_days.json | VerbNounScanner, StorySizingScanner | ```json<br>{<br>  "violations": [<br>    {<br>      "rule_name": "size_stories_3_to_12_days",<br>      "rule_file": "agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json",<br>      "violation_message": "Story sizing '15 days' is outside 3-12 day range",<br>      "line_number": 4,<br>      "location": "epics[0].features[0].stories[0].sizing",<br>      "severity": "error"<br>    }<br>  ],<br>  "scanners_executed": 2,<br>  "scanners_passed": 1,<br>  "scanners_failed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Report<br><br>Code scanners executed: 2<br>Violations detected: 1<br><br>### Violations:<br><br>- **Rule**: size_stories_3_to_12_days<br>  - **Location**: Line 4 (epics[0].features[0].stories[0].sizing)<br>  - **Issue**: Story sizing '15 days' is outside 3-12 day range<br>  - **Fix**: Adjust sizing to be between 3 and 12 days<br><br>Please review sections indicated by scanner violations against appropriate rules and make necessary edit, then run against all rules and make final edits before considering the knowledge generation action to be complete." |
| T1.3 | discovery | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json | VerbNounScanner (2 instances), ActiveLanguageScanner | ```json<br>{<br>  "violations": [],<br>  "scanners_executed": 3,<br>  "scanners_passed": 3,<br>  "scanners_failed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Report<br><br>Code scanners executed: 3<br>Violations detected: 0<br><br>All scanners validated successfully:<br>- use_verb_noun_format_for_story_elements scanner 1: PASSED<br>- use_verb_noun_format_for_story_elements scanner 2: PASSED<br>- use_active_behavioral_language scanner: PASSED<br><br>No violations found from code scanner. please run against rules directly and make any edits based on findings before completing build knowledge action" |
| T1.4 | exploration | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json | VerbNounScanner, ActiveLanguageScanner | ```json<br>{<br>  "violations": [],<br>  "scanners_executed": 2,<br>  "scanners_passed": 2,<br>  "scanners_failed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Report<br><br>Code scanners executed: 2<br>Violations detected: 0<br><br>All scanners validated successfully:<br>- use_verb_noun_format_for_story_elements scanner: PASSED<br>- use_active_behavioral_language scanner: PASSED<br><br>No violations found. Empty knowledge graph is valid from a code scanner perspective please validate using rules directly." |
| T1.5 | scenarios | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json | VerbNounScanner, ActiveLanguageScanner | ```json<br>{<br>  "error": "Knowledge graph file not found",<br>  "path": "agile_bot/bots/test_story_bot/docs/stories/story-graph.json",<br>  "scanners_executed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Error<br><br>Unable to validate knowledge graph.<br><br>**Error**: Knowledge graph file not found<br>**Path**: agile_bot/bots/test_story_bot/docs/stories/story-graph.json<br><br>Please ensure the knowledge graph file exists before proceeding." |
| T1.6 | tests | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json | VerbNounScanner, ActiveLanguageScanner | ```json<br>{<br>  "error": "validate_action_bot unavailable",<br>  "message": "Service not responding",<br>  "scanners_executed": 0<br>}<br>``` | **Original Instructions:**<br>"Build knowledge graph for the current behavior..."<br><br>**Enhanced Instructions (appended):**<br><br>"## Validation Error<br><br>Unable to forward to validate_action_bot.<br><br>**Error**: validate_action_bot unavailable<br>**Message**: Service not responding<br><br>Please check that validate_action_bot is available and try again." |


---

## Story 2: "Discovers Scanners"

### Scenario
```gherkin
Given Rule files exist at '{rule_file_paths}'
And Rule files contain '{rule_file_content}'
When Scanner discovery is executed for rule files at '{rule_file_paths}'
Then Scanners are discovered: '{registered_scanners}'
And Scanner class found status is '{scanner_class_found}'
And Scanner metadata is extracted from rule file with content '{rule_file_content}'
And Scanner metadata is '{scanner_metadata}'
And Scanners '{registered_scanners}' are registered in catalog for behaviors '{behaviors}'
And Catalog structure is '{catalog_structure}'
And Catalog size is '{catalog_size}'
```

### Testing Table: Scanner Discovery, Metadata Extraction, and Registration

| Test ID | Behavior | Rule File Paths | Rule File Content | Scanners Discovered | Scanner Class Found | Scanner Metadata | Catalog Structure | Catalog Size |
|---------|----------|----------------------------|----------------------------------------------|---------------------------|---------------------|-------------------|-------------------|---------------|
| T2.1 | all | agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/apply_exhaustive_decomposition.json | use_verb_noun_format_for_story_elements.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Use verb-noun format", "do": {...}}`<br>use_active_behavioral_language.json: `{"scanner": "agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner", "description": "Use active behavioral language", "do": {...}}`<br>apply_exhaustive_decomposition.json: `{"scanner": "agile_bot.bots.story_bot.scanners.exhaustive_decomposition_scanner.ExhaustiveDecompositionScanner", "description": "Apply exhaustive decomposition", "do": {...}}` | 3 scanners: VerbNounScanner, ActiveLanguageScanner, ExhaustiveDecompositionScanner | VerbNounScanner: Yes - found at agile_bot/bots/story_bot/scanners/verb_noun_scanner.py<br>ActiveLanguageScanner: Yes - found<br>ExhaustiveDecompositionScanner: Yes - found | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common"<br>rule_name="use_active_behavioral_language", description="Use active behavioral language", behavior_name="shape"<br>rule_name="apply_exhaustive_decomposition", description="Apply exhaustive decomposition", behavior_name="discovery" | Catalog with 3 entries grouped by behavior_name | 3 scanners registered |
| T2.2 | common | agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json<br>agile_bot/bots/test_story_bot/rules/use_active_behavioral_language.json<br>(No behavior directories exist) | use_verb_noun_format_for_story_elements.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Use verb-noun format", "do": {...}}`<br>use_active_behavioral_language.json: `{"scanner": "agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner", "description": "Use active behavioral language", "do": {...}}` | 2 scanners: VerbNounScanner, ActiveLanguageScanner | VerbNounScanner: Yes - found<br>ActiveLanguageScanner: Yes - found | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common"<br>rule_name="use_active_behavioral_language", description="Use active behavioral language", behavior_name="common" | Catalog with 2 entries grouped by behavior_name | 2 scanners registered |
| T2.3 | common | agile_bot/bots/test_story_bot/rules/ (directory exists but empty) | No rule files in directory | 0 scanners discovered | N/A - no rule files | N/A - no metadata | Empty catalog | 0 scanners registered |
| T2.4 | common | agile_bot/bots/test_story_bot/rules/ (directory does not exist) | N/A | Error: Directory not found | N/A - directory doesn't exist | N/A - no metadata | Empty catalog | 0 scanners registered |
| T2.5 | common | agile_bot/bots/test_story_bot/rules/invalid.json (malformed JSON)<br>agile_bot/bots/test_story_bot/rules/valid.json | invalid.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "..."` (missing closing brace)<br>valid.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Valid rule", "do": {...}}` | 1 scanner: VerbNounScanner + 1 error | VerbNounScanner: Yes - found<br>Error: "Rule file parse failure: agile_bot/bots/test_story_bot/rules/invalid.json, line 1: Expecting ',' delimiter or '}'" | rule_name="use_verb_noun_format_for_story_elements", description="Valid rule", behavior_name="common"<br>Error: Invalid rule structure for invalid.json | Catalog with 1 entry | 1 scanner registered, 1 error logged |
| T2.6 | common | agile_bot/bots/test_story_bot/rules/rule.json<br>agile_bot/bots/test_story_bot/rules/readme.txt (non-JSON) | rule.json: `{"scanner": "agile_bot.bots.story_bot.scanners.rule_scanner.RuleScanner", "description": "Rule", "do": {...}}`<br>readme.txt: `This is a readme file` (not JSON) | 1 scanner: RuleScanner | RuleScanner: Yes - found<br>Non-JSON file ignored | rule_name="rule", description="Rule", behavior_name="common" | Catalog with 1 entry | 1 scanner registered |
| T2.7 | shape | agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (directory does not exist) | use_verb_noun_format_for_story_elements.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Use verb-noun format", "do": {...}}` | 1 scanner: VerbNounScanner + 1 error | VerbNounScanner: Yes - found<br>Error: "Behavior rules directory not found: agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/" | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common" | Catalog with 1 entry | 1 scanner registered, 1 error logged |
| T2.8 | all | agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/invalid.json (malformed)<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/valid.json | invalid.json: `{"scanner": "agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner", "description": "..."` (missing closing brace)<br>valid.json: `{"scanner": "agile_bot.bots.story_bot.scanners.exhaustive_decomposition_scanner.ExhaustiveDecompositionScanner", "description": "Valid rule", "do": {...}}` | 1 scanner: ExhaustiveDecompositionScanner + 1 error | ExhaustiveDecompositionScanner: Yes - found<br>Error: "Rule file parse failure: agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/invalid.json, line 1: Expecting ',' delimiter or '}'" | rule_name="apply_exhaustive_decomposition", description="Valid rule", behavior_name="discovery"<br>Error: Invalid rule structure for invalid.json | Catalog with 1 entry | 1 scanner registered, 1 error logged |
| T2.9 | common | agile_bot/bots/test_story_bot/rules/missing_scanner.json<br>agile_bot/bots/story_bot/scanners/verb_noun_scanner.py (does not exist) | missing_scanner.json: `{"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Rule", "do": {...}}` | 1 scanner: VerbNounScanner + 1 error | VerbNounScanner: No - not found at agile_bot/bots/story_bot/scanners/verb_noun_scanner.py<br>Error: "Scanner class not found: agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner" | rule_name="missing_scanner", description="Rule", behavior_name="common" | Catalog with 0 entries (scanner not registered due to class not found) | 0 scanners registered, 1 error logged |
| T2.10 | common | agile_bot/bots/test_story_bot/rules/invalid_scanner_path.json | invalid_scanner_path.json: `{"scanner": "invalid.module.path.InvalidScanner", "description": "Rule", "do": {...}}` | 1 scanner: InvalidScanner + 1 error | InvalidScanner: No - cannot be imported<br>Error: "Scanner class import failure: ModuleNotFoundError: No module named 'invalid.module.path'" | rule_name="invalid_scanner_path", description="Rule", behavior_name="common" | Catalog with 0 entries (scanner not registered due to import failure) | 0 scanners registered, 1 error logged |
| T2.11 | common | agile_bot/bots/test_story_bot/rules/no_scanner_property.json | no_scanner_property.json: `{"description": "Rule without scanner property", "do": {...}}` (missing scanner property) | 1 scanner discovered + 1 error | Scanner: No - missing `scanner` property<br>Error: "Rule file missing required 'scanner' property: agile_bot/bots/test_story_bot/rules/no_scanner_property.json" | Error: Invalid rule structure, behavior_name="common" | Catalog with 0 entries (scanner not registered due to missing property) | 0 scanners registered, 1 error logged |
| T2.12 | all | agile_bot/bots/test_story_bot/rules/ (1000+ rule files)<br>agile_bot/bots/test_story_bot/behaviors/*/3_rules/ (1000+ rule files total) | Multiple rule files with scanner properties | All scanners discovered | All scanner classes found, discovery completes without timeout | Metadata extracted for all scanners | Catalog with all entries grouped by behavior_name | All scanners registered, organized by behavior_name |
| T2.13 | common | agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json | use_verb_noun_format_for_story_elements.json: `{"scanner": "...", "description": "Use verb-noun format", "do": {"examples": [...]}, "dont": {"examples": [...]}}` | 1 scanner: VerbNounScanner | VerbNounScanner: Yes - found | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common" | Catalog with 1 entry | 1 scanner registered |
| T2.14 | shape | agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json | use_active_behavioral_language.json: `{"scanner": "...", "do": {...}}` (missing description field) | 1 scanner: ActiveLanguageScanner | ActiveLanguageScanner: Yes - found | rule_name="use_active_behavioral_language", description=null, behavior_name="shape" | Catalog with 1 entry | 1 scanner registered |
| T2.15 | scenarios | agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json | use_background_for_common_setup.json: `{"scanner": "...", "description": "Use background for common setup"}` (missing do/dont examples) | 1 scanner: BackgroundSetupScanner | BackgroundSetupScanner: Yes - found | rule_name="use_background_for_common_setup", description="Use background for common setup", behavior_name="scenarios" | Catalog with 1 entry | 1 scanner registered |
| T2.16 | tests | agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/use_exact_variable_names.json | use_exact_variable_names.json: `{"scanner": "..."` (malformed JSON, missing closing brace) | 1 scanner discovered + 1 error | Error: "Rule file parse failure" | Error: Invalid rule structure, behavior_name="tests" | Catalog with 0 entries | 0 scanners registered, 1 error logged |
| T2.17 | exploration | agile_bot/bots/test_story_bot/behaviors/5_exploration/3_rules/behavioral_ac_at_story_level.json | behavioral_ac_at_story_level.json: `{"scanner": "...", "description": "", "do": {}, "dont": {}}` (empty content) | 1 scanner: BehavioralACScanner | BehavioralACScanner: Yes - found | rule_name="behavioral_ac_at_story_level", description="", behavior_name="exploration" | Catalog with 1 entry | 1 scanner registered |
| T2.18 | code | agile_bot/bots/test_story_bot/behaviors/8_code/3_rules/production_code_api_design.json | production_code_api_design.json: `{"scanner": "...", "description": "...", "behavior": "code", "do": {...}}` | 1 scanner: APIDesignScanner | APIDesignScanner: Yes - found | rule_name="production_code_api_design", behavior_name="code", description="..." | Catalog with 1 entry | 1 scanner registered |
| T2.19 | discovery | agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/apply_exhaustive_decomposition.json | apply_exhaustive_decomposition.json: `{"scanner": "...", "description": "...", "do": {...}}` (in discovery/3_rules directory) | 1 scanner: ExhaustiveDecompositionScanner | ExhaustiveDecompositionScanner: Yes - found | rule_name="apply_exhaustive_decomposition", behavior_name="discovery" (from path), description="..." | Catalog with 1 entry | 1 scanner registered |
| T2.20 | all | agile_bot/bots/test_story_bot/rules/ (7 rule files)<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (25 rule files)<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/ (5 rule files)<br>agile_bot/bots/test_story_bot/behaviors/5_exploration/3_rules/ (8 rule files)<br>agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/ (9 rule files)<br>agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/ (30 rule files)<br>agile_bot/bots/test_story_bot/behaviors/8_code/3_rules/ (43 rule files) | Multiple rule files with scanner properties across all behaviors | 50 scanners: 7 common (VerbNounScanner, ActiveLanguageScanner, ...), 25 shape (StorySizingScanner, BehavioralJourneyScanner, ...), 5 discovery (ExhaustiveDecompositionScanner, ...), 8 exploration, 9 scenarios, 30 tests, 43 code | All scanner classes found | Metadata extracted for all scanners across all behaviors | Catalog with 50 entries grouped by behavior_name | 50 scanners registered, organized by behavior_name |
| T2.21 | none | (no rule directories exist or all empty) | N/A | 0 scanners | N/A - no rule files | N/A - no metadata | Empty catalog | 0 scanners registered |
| T2.22 | all | agile_bot/bots/test_story_bot/rules/use_active_behavioral_language.json<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json | use_active_behavioral_language.json (common): `{"scanner": "...", "description": "Use active behavioral language", "do": {...}}`<br>use_active_behavioral_language.json (shape): `{"scanner": "...", "description": "Use active behavioral language", "do": {...}}` | 2 scanners: ActiveLanguageScanner (common), ActiveLanguageScanner (shape) | Both scanner classes found | rule_name="use_active_behavioral_language", behavior_name="common"<br>rule_name="use_active_behavioral_language", behavior_name="shape" | Catalog with unique rule names per behavior: common.use_active_behavioral_language, shape.use_active_behavioral_language | Duplicates handled (behavior-specific, both registered with behavior prefix) |
| T2.23 | all | agile_bot/bots/test_story_bot/rules/ (7 rule files)<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (25 rule files)<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/ (5 rule files)<br>agile_bot/bots/test_story_bot/behaviors/5_exploration/3_rules/ (8 rule files)<br>agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/ (9 rule files)<br>agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/ (30 rule files)<br>agile_bot/bots/test_story_bot/behaviors/8_code/3_rules/ (43 rule files) | Multiple rule files with scanner properties from all 7 behaviors | Scanners from all 7 behaviors | All scanner classes found | Metadata extracted for all scanners | Catalog grouped by behavior_name | Catalog organized by behavior_name: common (7), shape (25), discovery (5), exploration (8), scenarios (9), tests (30), code (43) |
| T2.24 | all | agile_bot/bots/test_story_bot/rules/ (7 rule files)<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (25 rule files, some with missing scanner classes) | Common rules: Multiple rule files with scanner properties<br>Shape rules: Some rule files reference scanner classes that don't exist | Scanners from common behavior + partial from shape behavior | Common scanners: All found<br>Shape scanners: Some not found (scanner class not found errors) | Metadata extracted for common scanners, errors logged for shape scanners | Partial catalog: common scanners registered, shape scanners excluded | Failed scanners excluded, errors logged, common behavior still registered |

---

## Story 3: "Run Scanners against Knowledge Graph"


Background
Given Scanners are discovered and registered for {behavior} and {rule file}:
  - Common rules: 'agile_bot/bots/test_story_bot/rules/'
  - Behavior rules: 'agile_bot/bots/test_story_bot/behaviors/{behavior_number}_{behavior_name}/3_rules/'
and Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'

### Scenario
```gherkin
Given Knowledge graph contains '{knowledge_graph_problems}'
And Rule file is '{rule_file}'
When Scanners are executed against knowledge graph containing '{knowledge_graph_problems}'
Then Violations are detected at '{expected_violation_line}'
And Violation details are '{expected_violation_details}'
And Report format is '{expected_report_format}'
And Report structure is '{expected_report_structure}'
```

### Testing Table: Rule Detection and Violation Reporting

| Test ID | Behavior | Rule File | Knowledge Graph with Problems | Expected Violation Line | Expected Violation Details | Expected Report Format | Expected Report Structure |
|---------|----------|-----------|------------------------|----------------------|---------------------------|----------------------|------------------------|
| T3.1 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Order Management"}]}` | line 2 (epics[0].name) | violation_message: "Epic name uses noun-only format instead of verb-noun", location: "epics[0].name" | JSON report | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format instead of verb-noun", "line_number": 2, "location": "epics[0].name", "severity": "error"}]}` |
| T3.2 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order"}]}]}]}` | None (0 violations) | No violations - correct verb-noun format | JSON report | `{"violations": []}` |
| T3.2a | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]}` | line 4 (epics[0].features[0].stories[0].name) | violation_message: "Story name contains actor 'Customer' - actors should not be in story names", location: "epics[0].features[0].stories[0].name" | JSON report | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Story name contains actor 'Customer' - actors should not be in story names", "line_number": 4, "location": "epics[0].features[0].stories[0].name", "severity": "error"}]}` |
| T3.3 | shape | use_active_behavioral_language.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Payment Processing"}]}]}` | line 3 (epics[0].features[0].name) | violation_message: "Feature uses capability noun 'Processing' instead of behavioral language", location: "epics[0].features[0].name" | JSON report | `{"violations": [{"rule_name": "use_active_behavioral_language", "rule_file": "agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json", "violation_message": "Feature uses capability noun 'Processing' instead of behavioral language", "line_number": 3, "location": "epics[0].features[0].name", "severity": "error"}]}` |
| T3.4 | shape | size_stories_3_to_12_days.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]}` | line 4 (epics[0].features[0].stories[0].sizing) | violation_message: "Story sizing '15 days' is outside 3-12 day range", location: "epics[0].features[0].stories[0].sizing" | JSON report | `{"violations": [{"rule_name": "size_stories_3_to_12_days", "rule_file": "agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/size_stories_3_to_12_days.json", "violation_message": "Story sizing '15 days' is outside 3-12 day range", "line_number": 4, "location": "epics[0].features[0].stories[0].sizing", "severity": "error"}]}` |
| T3.5 | scenarios | use_background_for_common_setup.json | `{"scenarios": [{"background": {"steps": ["Given test project area is set up at test_data/projects/valid-project"]}}]}` | line 2 (background.steps[0]) | violation_message: "Background contains scenario-specific setup - should only contain steps true for ALL scenarios", location: "background.steps[0]" | JSON report | `{"violations": [{"rule_name": "use_background_for_common_setup", "rule_file": "agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/use_background_for_common_setup.json", "violation_message": "Background contains scenario-specific setup - should only contain steps true for ALL scenarios", "line_number": 2, "location": "background.steps[0]", "severity": "error"}]}` |
| T3.6 | tests | use_exact_variable_names.json | `{"test_code": "name = 'story_bot'"}` | line 2 (test code) | violation_message: "Variable name 'name' doesn't match specification 'agent_name'", location: "test_code", code_snippet: "name = 'story_bot'" | JSON report | `{"violations": [{"rule_name": "use_exact_variable_names", "rule_file": "agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/use_exact_variable_names.json", "violation_message": "Variable name 'name' doesn't match specification 'agent_name'", "line_number": 2, "location": "test_code", "code_snippet": "name = 'story_bot'", "severity": "error"}]}` |
| T3.7 | multiple | use_verb_noun_format_for_story_elements.json, use_active_behavioral_language.json, size_stories_3_to_12_days.json | `{"epics": [{"name": "Order Management", "features": [{"name": "Payment Processing", "stories": [{"name": "Customer places order", "sizing": "15 days"}]}]}]}` | Multiple lines: 2, 3, 4, 5 | 4 violations: epic noun-only (line 2), feature capability noun (line 3), story actor in name (line 4), story sizing (line 5) | JSON report with array | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 2, ...}, {"rule_name": "use_active_behavioral_language", "line_number": 3, ...}, {"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 4, ...}, {"rule_name": "size_stories_3_to_12_days", "line_number": 5, ...}]}` - 4 entries, each with exact line_number |
| T3.8 | common | use_verb_noun_format_for_story_elements.json | `{}` | None (0 violations) | Empty graph is valid - no violations | JSON report | `{"violations": []}` |
| T3.9 | shape | use_active_behavioral_language.json | `{"epics": [{"name": "Places Order"` | Error at parse | Error: JSON parse failure at line 1, message: "Expecting ',' delimiter or '}'" | Error report | `{"error": "JSON parse failure", "message": "Expecting ',' delimiter or '}'", "line": 1}` |
| T3.10 | common | use_verb_noun_format_for_story_elements.json | (file does not exist) | Error | Error: Knowledge graph file not found | Error report | `{"error": "Knowledge graph file not found", "path": "agile_bot/bots/test_story_bot/docs/stories/story-graph.json"}` |
| T3.11 | common | use_verb_noun_format_for_story_elements.json | (rule file malformed: `{"description": "..."`) | Error at rule load | Error: Rule file parse failure, message: "Expecting ',' delimiter or '}'" | Error report | `{"error": "Rule file parse failure", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "message": "Expecting ',' delimiter or '}'"}` |
| T3.12 | all | All rule files (all behaviors) | `{"epics": [{"name": "Order Management"}, {"name": "Payment Processing"}, ...], "features": [...], "stories": [...]}` (large structure with 50+ violations) | Multiple lines (50+) | 50+ violations reported, each with exact line_number and location | JSON report | `{"violations": [...]}` - array with all entries, each with exact line_number, pagination if needed |
| T3.13 | shape | use_active_behavioral_language.json | (file does not exist) | Error | Error: Knowledge graph file not found | Error report | `{"error": "Knowledge graph file not found", "path": "agile_bot/bots/test_story_bot/docs/stories/story-graph.json"}` |
| T3.14 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "epic_ref": "epics[0]"}]}]}` | Error at validation | Error: Circular reference detected in knowledge graph structure | Error report | `{"error": "Circular reference detected", "location": "epics[0].features[0].epic_ref"}` |
| T3.15 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": null}]}` | line 2 (epics[0].name) | violation_message: "Epic name is null", location: null (invalid) | JSON report | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "line_number": 2, "location": null, "violation_message": "Epic name is null"}]}` - violation with null/empty location fields |

### Scenario
```gherkin
Given Knowledge graph contains '{knowledge_graph_problems}'
And Scanner '{scanner}' is selected for execution
When Single scanner '{scanner}' is executed against knowledge graph containing '{knowledge_graph_problems}'
Then Violation line is '{expected_violation_line}'
And Violation details are '{expected_violation_details}'
```

### Testing Table: Single Scanner Execution

| Test ID | Behavior | Scanner | Knowledge Graph with Problems | Expected Violation Line | Expected Violation Details |
|---------|----------|---------|------------------------|------------------------|---------------------------|
| T3.16 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Order Management"}]}` | line 2 (epics[0].name) | line_number: 2, location: "epics[0].name", message: "Epic name uses noun-only format instead of verb-noun" |
| T3.17 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order"}]}]}]}` | None (0 violations) | No violations - correct verb-noun format |
| T3.17a | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]}` | line 4 (epics[0].features[0].stories[0].name) | line_number: 4, location: "epics[0].features[0].stories[0].name", message: "Story name contains actor 'Customer' - actors should not be in story names" |
| T3.18 | shape | use_active_behavioral_language.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Payment Processing"}]}]}` | line 3 (epics[0].features[0].name) | line_number: 3, location: "epics[0].features[0].name", message: "Feature uses capability noun 'Processing' instead of behavioral language" |
| T3.19 | shape | size_stories_3_to_12_days.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]}` | line 4 (epics[0].features[0].stories[0].sizing) | line_number: 4, location: "epics[0].features[0].stories[0].sizing", message: "Story sizing '15 days' is outside 3-12 day range" |
| T3.20 | scenarios | use_background_for_common_setup.json | `{"scenarios": [{"background": {"steps": ["Given test project area is set up at test_data/projects/valid-project"]}}]}` | line 2 (background.steps[0]) | line_number: 2, location: "background.steps[0]", message: "Background contains scenario-specific setup - should only contain steps true for ALL scenarios" |
| T3.21 | tests | use_exact_variable_names.json | `{"test_code": "name = 'story_bot'"}` | line 2 (test code) | line_number: 2, location: "test_code", message: "Variable name 'name' doesn't match specification 'agent_name'", code_snippet: "name = 'story_bot'" |
| T3.22 | common | use_verb_noun_format_for_story_elements.json | `{}` | None (0 violations) | Empty graph is valid - no violations |
| T3.23 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...]}` (large structure with 1000+ stories) | Multiple lines (all violations detected) | All violations detected with exact line numbers, violations array contains all matches |
| T3.24 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order"` | Error at parse | Error: JSON parse failure, message: "Expecting ',' delimiter or '}'", scanner doesn't crash |
| T3.25 | common | use_verb_noun_format_for_story_elements.json | (file does not exist) | Error | Error: Knowledge graph file not found at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json' |
| T3.26 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "epic_ref": "epics[0]"}]}]}` | Error at validation | Error: Circular reference detected in knowledge graph structure |
| T3.27 | common | use_verb_noun_format_for_story_elements.json | `{"epics": [{"name": "Order Management", "features": [{"name": null}]}]}` | line 2 (epics[0].name) | Partial violations: Valid violation detected at line 2 (epic noun-only), errors logged for invalid feature name |

### Scenario
```gherkin
Given Scanners are discovered and registered
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Knowledge graph contains '{knowledge_graph_problems}'
And Multiple scanners '{scanners}' are selected for execution
When Multiple scanners '{scanners}' are executed against knowledge graph containing '{knowledge_graph_problems}'
Then Violations per scanner are '{expected_violations_per_scanner}'
And Total violations are '{expected_total_violations}'
```

### Testing Table: Multiple Scanner Execution

| Test ID | Behaviors | Scanners | Knowledge Graph with Problems | Expected Violations Per Scanner | Expected Total Violations |
|---------|-----------|----------|------------------------|--------------------------------|---------------------------|
| T3.28 | common | All common rules (7 scanners: VerbNounScanner, ActiveLanguageScanner, ...) | `{"epics": [{"name": "Order Management", "features": [{"name": "Validates Payment", "stories": [{"name": "Customer places order"}]}]}]}` | 3 scanners report violations (VerbNounScanner: line 2, VerbNounScanner: line 4, ActiveLanguageScanner: line 2), 4 report none | 3 violations total with exact line numbers |
| T3.29 | shape | All shape behavior rules (25 scanners: StorySizingScanner, BehavioralJourneyScanner, ...) | `{"epics": [{"name": "Order Management", "features": [{"name": "Payment Processing", "stories": [{"name": "Place Order", "sizing": "15 days"}]}]}]}` | 5 scanners report violations (VerbNounScanner: line 2, ActiveLanguageScanner: line 3, StorySizingScanner: line 5, ...), 20 report none | 5 violations total with exact line numbers |
| T3.30 | all | All behavior rules (50+ scanners across all behaviors) | `{"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...], "scenarios": [...], "tests": [...]}` (large structure with multiple violations) | 10 scanners report violations (various lines), 40+ report none | 10 violations total, each with exact line_number |
| T3.31 | all | All scanners (all behaviors) | `{"epics": [{"name": "Places Order", "features": [{"name": "Validates Payment", "stories": [{"name": "Submits payment", "sizing": "5 days"}]}]}]}` | All scanners report 0 violations | 0 violations total |
| T3.32 | all | All scanners (all behaviors) | `{"epics": [{"name": "Order Management"}, ...], "features": [...], "stories": [...], "scenarios": [...], "tests": [...]}` (large structure with violations across all rule types) | All scanners report violations (many lines) | 50+ violations total, each with exact line_number |
| T3.33 | all | All scanners (all behaviors) | `{"epics": [{"name": "Places Order"` | All scanners report parse error | Error: JSON parse failure at line 1 |
| T3.34 | all | All scanners (all behaviors) | `{}` | All scanners report 0 violations | 0 violations total |

### Scenario
```gherkin
Given Scanners are discovered and registered
And Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Knowledge graph contains '{knowledge_graph_problems}'
And Scanner execution order is '{scanner_execution_order}'
And Scanner failure behavior is '{scanner_failure_behavior}'
When Scanners execute in '{scanner_execution_order}' order against knowledge graph containing '{knowledge_graph_problems}'
Then Result is '{expected_result}'
```

### Testing Table: Scanner Execution Order and Isolation

| Test ID | Behavior | Scanner Execution Order | Knowledge Graph with Problems | Scanner Failure Behavior | Expected Result |
|---------|----------|------------------------|------------------------|-------------------------|----------------|
| T3.35 | common | Sequential execution | `{"epics": [{"name": "Order Management"}]}` | Scanner 1 (VerbNounScanner) throws exception, Scanner 2 (ActiveLanguageScanner) succeeds | Scanner 1 error logged with exception details, Scanner 2 executes and reports violation at line 2 |
| T3.36 | common | Parallel execution | `{"epics": [{"name": "Order Management"}]}` | Scanner 1 (VerbNounScanner) fails, Scanner 2 (ActiveLanguageScanner) succeeds | Both results reported: Scanner 1 error logged, Scanner 2 reports violation at line 2, errors isolated |
| T3.37 | shape | Sequential execution | `{"epics": [{"name": "Order Management"}]}` | All scanners succeed | All scanners execute in order, violations reported with line numbers |
| T3.38 | discovery | Sequential execution | `{"epics": [...], "features": [...], "stories": [...]}` (large structure with 1000+ stories) | Scanner 1 (VerbNounScanner) timeout after 30s | Timeout error reported with scanner name, next scanner continues execution |
| T3.39 | exploration | Parallel execution | `{"epics": [...], "features": [...], "stories": [...]}` (large structure with 1000+ stories) | Scanner 1 (VerbNounScanner) memory error | Error isolated with scanner name, other scanners complete and report violations |

---

## Story 4: "Reports Violations"

### Scenario
```gherkin
Given Scanners have executed against knowledge graph
And Violations have been detected: '{violations_data}'
And Report format is '{report_format}'
When Violation report is generated with violations '{violations_data}' and format '{report_format}'
Then Report structure is '{expected_report_structure}'
```

### Testing Table: Violation Report Generation

| Test ID | Behavior | Violations Data | Report Format | Expected Report Structure |
|---------|----------|----------------|---------------|--------------------------|
| T4.1 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | JSON | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "error", "timestamp": "..."}]}` |
| T4.2 | multiple | 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | JSON | `{"violations": [...]}` - Array of 5 violation objects, each with exact line_number |
| T4.3 | common | No violations detected (empty array) | JSON | `{"violations": []}` |
| T4.4 | all | 100+ violations: multiple epics with noun-only names (lines 2, 10, 25, ...), features with capability nouns (lines 3, 11, 26, ...), stories with actors in names (lines 4, 12, 27, ...) | JSON | `{"violations": [...]}` - Array with all entries, each with exact line_number, pagination if needed |
| T4.5 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | CHECKLIST | `- [ ] Line 2 (epics[0].name): Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order"` |
| T4.6 | multiple | 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | CHECKLIST | Checklist with 5 items, each showing line_number and fix suggestion |
| T4.7 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", violation_message="Epic name uses noun-only format" | DETAILED | All fields + code_snippet showing line 2 + context + examples from rule file |
| T4.8 | multiple | 5 violations: Epic "Order Management" (line 2), Feature "Payment Processing" (line 3), Story "Customer places order" (line 4), Story sizing "15 days" (line 5), Background step (line 6) | DETAILED | Each violation with full details including exact line_number, code_snippet, context |
| T4.9 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, severity="error" | SUMMARY | `{"violation_count": 1, "rule_count": 1, "severity_breakdown": {"error": 1}}` |
| T4.10 | multiple | 5 violations from 3 rules: Epic "Order Management" (use_verb_noun_format, line 2), Feature "Payment Processing" (use_active_behavioral_language, line 3), Story "Customer places order" (use_verb_noun_format, line 4), Story sizing "15 days" (size_stories_3_to_12_days, line 5), Background step (use_background_for_common_setup, line 6) | SUMMARY | `{"violation_count": 5, "rule_count": 3, "severity_breakdown": {...}}` - Total count, grouped by rule, severity summary |
| T4.11 | common | No violations detected (empty array) | All formats | Format-appropriate empty structure (empty array, empty checklist, etc.) |
| T4.12 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | JSON | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "error"}]}` |
| T4.13 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="warning" | JSON | `{"violations": [{"rule_name": "use_verb_noun_format_for_story_elements", "rule_file": "agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json", "violation_message": "Epic name uses noun-only format", "line_number": 2, "location": "epics[0].name", "severity": "warning"}]}` |
| T4.14 | multiple | 5 violations with mixed severities: Epic "Order Management" (severity="error", line 2), Feature "Payment Processing" (severity="error", line 3), Story "Customer places order" (severity="warning", line 4), Story sizing "15 days" (severity="error", line 5), Background step (severity="info", line 6) | JSON | `{"violations": [{"severity": "error", "line_number": 2, ...}, {"severity": "error", "line_number": 3, ...}, {"severity": "warning", "line_number": 4, ...}, {"severity": "error", "line_number": 5, ...}, {"severity": "info", "line_number": 6, ...}]}` - All violations include severity field |
| T4.15 | multiple | 5 violations with mixed severities: Epic "Order Management" (severity="error", line 2), Feature "Payment Processing" (severity="error", line 3), Story "Customer places order" (severity="warning", line 4), Story sizing "15 days" (severity="error", line 5), Background step (severity="info", line 6) | SUMMARY | `{"violation_count": 5, "rule_count": 3, "severity_breakdown": {"error": 3, "warning": 1, "info": 1}}` - Severity breakdown shows counts per severity level |
| T4.16 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | CHECKLIST | `- [ ] Line 2 (epics[0].name) [ERROR]: Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order"` - Severity shown in checklist item |
| T4.17 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="warning" | CHECKLIST | `- [ ] Line 2 (epics[0].name) [WARNING]: Epic name uses noun-only format\n  Fix: Use verb-noun format like "Places Order"` - Warning severity shown in checklist item |
| T4.18 | common | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | DETAILED | All fields + severity="error" prominently displayed + code_snippet showing line 2 + context + examples from rule file |

### Scenario
```gherkin
Given Scanners have executed against knowledge graph
And Violations have been detected: '{violations_data}'
And Violations are from behaviors '{behaviors}'
When Violations are grouped and organized with violations '{violations_data}' from behaviors '{behaviors}'
Then Grouping is '{expected_grouping}'
And Organization is '{expected_organization}'
```

### Testing Table: Violation Grouping and Organization

| Test ID | Behaviors | Violations Data | Expected Grouping | Expected Organization |
|---------|-----------|----------------|------------------|---------------------|
| T4.19 | common, shape, scenarios | Epic "Order Management" violation (common, use_verb_noun_format, line 2), Feature "Payment Processing" violation (shape, use_active_behavioral_language, line 3), Background step violation (scenarios, use_background_for_common_setup, line 4) | Grouped by rule_name, then by behavior_name | 3 groups organized by behavior: common (use_verb_noun_format, line 2), shape (use_active_behavioral_language, line 3), scenarios (use_background_for_common_setup, line 4), violations within each group |
| T4.20 | shape | 10 violations from rule "use_active_behavioral_language": Feature "Payment Processing" (line 2), Feature "Order Management" (line 3), ... (lines 2-11) | Single group | All violations in one group, behavior_name=shape, each with exact line_number |
| T4.21 | all | Violations from all 7 behaviors: Epic "Order Management" (common, line 2), Feature "Payment Processing" (shape, line 3), Epic "Explores Domain" (discovery, line 4), ... | Grouped by behavior_name, then by rule_name | Groups organized by behavior: common (line 2), shape (line 3), discovery (line 4), exploration, scenarios, tests, code, each violation with line_number |
| T4.22 | common, shape | Epic "Order Management" violation (common, use_verb_noun_format, location="epics[0].name", line 2), Epic "Order Management" violation (shape, use_active_behavioral_language, location="epics[0].name", line 2) | Grouped by location, then by behavior_name | Violations at same location (epics[0].name, line 2) grouped, behavior_name preserved |
| T4.23 | common, shape | Epic "Order Management" violation (common, use_verb_noun_format, severity="error", line 2), Feature "Payment Processing" violation (shape, use_active_behavioral_language, severity="warning", line 3) | Grouped by severity, then by behavior_name | Violations organized by severity level, behavior_name preserved, each with line_number |

### Scenario
```gherkin
Given Scanners have executed against knowledge graph
And Violations have been detected: '{violations_data}'
And Report format is '{report_format}'
And Output destination is '{output_destination}'
When Report is generated with format '{report_format}' and violations '{violations_data}' and written to '{output_destination}'
Then Output is '{expected_output}'
```

### Testing Table: Report Output and Persistence

| Test ID | Behavior | Report Format | Violations Data | Output Destination | Expected Output |
|---------|----------|--------------|----------------|-------------------|----------------|
| T4.24 | common | JSON | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | File: validation_report.json | JSON file written with violations including line_number and severity, file exists at output path |
| T4.25 | common | CHECKLIST | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | File: validation_report.md | Markdown file written with checklist items showing line numbers and severity, file exists at output path |
| T4.26 | common | DETAILED | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | File: validation_report.txt | Text file written with detailed violations including line_number, severity, and code snippets, file exists at output path |
| T4.27 | common | JSON | Epic "Order Management" violation: rule_name="use_verb_noun_format_for_story_elements", line_number=2, location="epics[0].name", severity="error" | Console output | JSON printed to console with violations including line_number and severity, no file written |
| T4.28 | shape | JSON | `[{"rule_name": "...", "line_number": 2, "severity": "error", ...}]` | File: validation_report.json (write fails) | Error reported with file path, report still generated in memory |
| T4.29 | discovery | JSON | `[{"rule_name": "...", "line_number": 2, "severity": "warning", ...}]` | File: validation_report.json (exists) | File overwritten with new violations or error if overwrite disabled |
| T4.30 | exploration | JSON | `[{"rule_name": "...", "line_number": 2, "severity": "info", ...}]` | File: nonexistent_dir/validation_report.json | Directory created or error if permissions insufficient |
| T4.31 | scenarios | JSON | `[{"rule_name": "...", "line_number": 2, "severity": "error", ...}]` | File: validation_report.json (disk full) | Error reported: "Insufficient disk space" |

---

## Common Testing Patterns Across All Stories

### Parameterized Background Patterns

#### Pattern 1: Basic Agent Setup
```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
```

#### Pattern 2: Behavior-Specific Setup
```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
And Behavior is '{behavior_name}'
```

#### Pattern 3: Rules Directory Setup
```gherkin
Given Common rules directory exists at 'agile_bot/bots/test_story_bot/rules/'
And Behavior rules directory exists at 'agile_bot/bots/test_story_bot/behaviors/{behavior_number}_{behavior_name}/3_rules/'
And Common rules directory contains '{common_rule_count}' rule files
And Behavior rules directory contains '{behavior_rule_count}' rule files
```

#### Pattern 4: Knowledge Graph Setup
```gherkin
Given Knowledge graph exists at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json'
And Knowledge graph contains '{concept_count}' concepts
And Knowledge graph contains '{relationship_count}' relationships
```

### Example Table Patterns

#### Pattern 1: Rule Testing Table
| Behavior | Rule Name | Rule File | Knowledge Graph State | Expected Violations | Expected Message Contains |
|----------|-----------|-----------|---------------------|-------------------|-------------------------|
| common | Verb-Noun Format | use_verb_noun_format_for_story_elements.json | Epic "Order Management" | 1 | "noun-only format" |
| common | Actor in Name | use_verb_noun_format_for_story_elements.json | Story "Customer places order" | 1 | "contains actor" |
| shape | Active Language | use_active_behavioral_language.json | Feature "Payment Processing" | 1 | "capability noun" |
| shape | Story Sizing | size_stories_3_to_12_days.json | Story sizing="15 days" | 1 | "outside 3-12 day range" |
| scenarios | Background Setup | use_background_for_common_setup.json | Background with scenario-specific Given | 1 | "scenario-specific setup" |
| tests | Variable Names | use_exact_variable_names.json | Test with variable name mismatch | 1 | "doesn't match specification" |
| exploration | AC Format | behavioral_ac_at_story_level.json | AC split across multiple strings | 1 | "single string" |
| discovery | Exhaustive Decomposition | apply_exhaustive_decomposition.json | Missing sub-epics | 1 | "exhaustive decomposition" |
| code | Production Code API | production_code_api_design.json | API doesn't match tests | 1 | "API design" |

#### Pattern 2: Error Case Testing Table
| Error Type | Error Condition | Expected Error Message | Expected Behavior |
|------------|----------------|----------------------|-------------------|
| File Not Found | Knowledge graph at 'agile_bot/bots/test_story_bot/docs/stories/story-graph.json' doesn't exist | "Knowledge graph file not found" | Error reported, no crash |
| Invalid JSON | Knowledge graph has malformed JSON | "JSON parse failure" | Error reported, no crash |
| Permission Denied | Rules directory not readable | "Permission denied" | Error reported, no crash |
| Circular Reference | Knowledge graph has circular refs | "Circular reference detected" | Error reported, no crash |

#### Pattern 3: Edge Case Testing Table
| Edge Case | Example Content | Expected Behavior |
|-----------|----------------|------------------|
| Empty Graph | `{}` | 0 violations, no errors |
| Large Graph | JSON with 1000+ epics/features/stories | All violations detected with exact line numbers |
| Many Rules | 100+ rule files across all behaviors | All scanners discovered from fixed paths |
| Many Violations | Graph with violations at lines 2, 5, 10, 15, ... (100+) | All violations reported, each with exact line_number |

### Test Data Fixtures

#### Fixture 1: Valid Knowledge Graph
```json
{
  "epics": [
    {
      "name": "Places Order",
      "features": [
        {
          "name": "Validates Payment",
          "stories": [
            {
              "name": "Submits payment",
              "sizing": "5 days"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Fixture 2: Invalid Knowledge Graph (Violates Verb-Noun)
```json
{
  "epics": [
    {
      "name": "Order Management",
      "features": [
        {
          "name": "Payment Processing",
          "stories": [
            {
              "name": "Ordering",
              "sizing": "15 days"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Fixture 3: Empty Knowledge Graph
```json
{}
```

#### Fixture 4: Malformed Knowledge Graph
```json
{
  "epics": [
    {
      "name": "Places Order",
      "features": [
        {
          "name": "Validates Payment",
          "stories": [
            {
              "name": "Submits payment",
              "sizing": "5 days"
            }
          ]
        }
      ]
    }
  ]
  // Missing closing brace
```

---

## Testing Strategy Summary

### For Each Story:
1. **Happy Path Tests**: Test normal operation with valid inputs
2. **Edge Case Tests**: Test boundary conditions, empty inputs, large inputs
3. **Error Case Tests**: Test error handling, invalid inputs, missing files
4. **Rule Isolation Tests**: Test each rule in isolation against the story
5. **Integration Tests**: Test multiple rules together, multiple scanners together

### For Each Rule:
1. **Violation Detection Test**: Rule detects violations in bad content
2. **No Violation Test**: Rule correctly identifies valid content
3. **Scanner Discovery Test**: Rule scanner is discovered and registered
4. **Report Generation Test**: Violations from rule are properly reported
5. **Error Handling Test**: Rule handles errors gracefully

### Common Test Scenarios:
- Empty inputs (empty graph, empty rules directory)
- Large inputs (1000+ concepts, 100+ rules)
- Invalid inputs (malformed JSON, missing files)
- Multiple violations (many violations, violations from multiple rules)
- Error conditions (permission denied, file not found, parse errors)

---

## Next Steps

1. Implement test fixtures based on these tables
2. Create parameterized test functions using these tables
3. Implement code scanners for each rule
4. Create violation report generators
5. Build test execution framework that runs all table rows

