# 📝 Discovers Scanners

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Validate Knowledge & Content Against Rules  
**Feature:** Code Scanner  
**Story:** Discovers Scanners

## Story Description

System discovers scanners from rule.json files, extracts metadata, and registers them in a catalog organized by behavior name.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** scanner discovery is executed for rule files, **then** scanners are discovered from rule files containing scanner properties
- **When** scanner class path is found in rule file, **then** scanner class is located and validated
- **When** scanner metadata is extracted, **then** metadata includes rule_name, description, and behavior_name
- **When** scanners are registered, **then** scanners are organized in catalog grouped by behavior_name
- **When** rule file is malformed, **then** error is logged and valid scanners are still registered
- **When** scanner class is not found, **then** error is logged and scanner is not registered
- **When** rule file is missing scanner property, **then** error is logged and scanner is not registered

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='test_story_bot'
And Project has finished generating knowledge graph
And Behavior is "<behavior_name>"
And Common rules directory exists at 'agile_bot/bots/test_story_bot/rules/'
And Behavior rules directory exists at 'agile_bot/bots/test_story_bot/behaviors/<behavior_number>_<behavior_name>/3_rules/'
```

## Scenarios

### Scenario Outline: Scanner discovery extracts metadata and registers scanners (happy_path)

**Steps:**
```gherkin
Given Rule files exist at "<rule_file_paths>"
And Rule files contain "<rule_file_content>"
When Scanner discovery is executed for rule files at "<rule_file_paths>"
Then Scanners are discovered: "<registered_scanners>"
And Scanner class found status is "<scanner_class_found>"
And Scanner metadata is extracted from rule file with content "<rule_file_content>"
And Scanner metadata is "<scanner_metadata>"
And Scanners "<registered_scanners>" are registered in catalog for behaviors "<behaviors>"
And Catalog structure is "<catalog_structure>"
And Catalog size is "<catalog_size>"
```

**Examples:**

| rule_file_paths | rule_file_content | registered_scanners | scanner_class_found | scanner_metadata | behaviors | catalog_structure | catalog_size |
|----------------------------|----------------------------------------------|---------------------------|---------------------|-------------------|-----------|-------------------|---------------|
| agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/use_active_behavioral_language.json<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/apply_exhaustive_decomposition.json | use_verb_noun_format_for_story_elements.json: {"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Use verb-noun format", "do": {...}}<br>use_active_behavioral_language.json: {"scanner": "agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner", "description": "Use active behavioral language", "do": {...}}<br>apply_exhaustive_decomposition.json: {"scanner": "agile_bot.bots.story_bot.scanners.exhaustive_decomposition_scanner.ExhaustiveDecompositionScanner", "description": "Apply exhaustive decomposition", "do": {...}} | 3 scanners: VerbNounScanner, ActiveLanguageScanner, ExhaustiveDecompositionScanner | VerbNounScanner: Yes - found at agile_bot/bots/story_bot/scanners/verb_noun_scanner.py<br>ActiveLanguageScanner: Yes - found<br>ExhaustiveDecompositionScanner: Yes - found | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common"<br>rule_name="use_active_behavioral_language", description="Use active behavioral language", behavior_name="shape"<br>rule_name="apply_exhaustive_decomposition", description="Apply exhaustive decomposition", behavior_name="discovery" | common, shape, discovery | Catalog with 3 entries grouped by behavior_name | 3 scanners registered |
| agile_bot/bots/test_story_bot/rules/use_verb_noun_format_for_story_elements.json<br>agile_bot/bots/test_story_bot/rules/use_active_behavioral_language.json<br>(No behavior directories exist) | use_verb_noun_format_for_story_elements.json: {"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Use verb-noun format", "do": {...}}<br>use_active_behavioral_language.json: {"scanner": "agile_bot.bots.story_bot.scanners.active_language_scanner.ActiveLanguageScanner", "description": "Use active behavioral language", "do": {...}} | 2 scanners: VerbNounScanner, ActiveLanguageScanner | VerbNounScanner: Yes - found<br>ActiveLanguageScanner: Yes - found | rule_name="use_verb_noun_format_for_story_elements", description="Use verb-noun format", behavior_name="common"<br>rule_name="use_active_behavioral_language", description="Use active behavioral language", behavior_name="common" | common | Catalog with 2 entries grouped by behavior_name | 2 scanners registered |
| agile_bot/bots/test_story_bot/rules/ (directory exists but empty) | No rule files in directory | 0 scanners discovered | N/A - no rule files | N/A - no metadata | common | Empty catalog | 0 scanners registered |
| agile_bot/bots/test_story_bot/rules/ (directory does not exist) | N/A | Error: Directory not found | N/A - directory doesn't exist | N/A - no metadata | common | Empty catalog | 0 scanners registered |
| agile_bot/bots/test_story_bot/rules/invalid.json (malformed JSON)<br>agile_bot/bots/test_story_bot/rules/valid.json | invalid.json: {"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "..." (missing closing brace)<br>valid.json: {"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Valid rule", "do": {...}} | 1 scanner: VerbNounScanner + 1 error | VerbNounScanner: Yes - found<br>Error: "Rule file parse failure: agile_bot/bots/test_story_bot/rules/invalid.json, line 1: Expecting ',' delimiter or '}'" | rule_name="use_verb_noun_format_for_story_elements", description="Valid rule", behavior_name="common"<br>Error: Invalid rule structure for invalid.json | common | Catalog with 1 entry | 1 scanner registered, 1 error logged |
| agile_bot/bots/test_story_bot/rules/rule.json<br>agile_bot/bots/test_story_bot/rules/readme.txt (non-JSON) | rule.json: {"scanner": "agile_bot.bots.story_bot.scanners.rule_scanner.RuleScanner", "description": "Rule", "do": {...}}<br>readme.txt: This is a readme file (not JSON) | 1 scanner: RuleScanner | RuleScanner: Yes - found<br>Non-JSON file ignored | rule_name="rule", description="Rule", behavior_name="common" | common | Catalog with 1 entry | 1 scanner registered |
| agile_bot/bots/test_story_bot/rules/missing_scanner.json<br>agile_bot/bots/story_bot/scanners/verb_noun_scanner.py (does not exist) | missing_scanner.json: {"scanner": "agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner", "description": "Rule", "do": {...}} | 1 scanner: VerbNounScanner + 1 error | VerbNounScanner: No - not found at agile_bot/bots/story_bot/scanners/verb_noun_scanner.py<br>Error: "Scanner class not found: agile_bot.bots.story_bot.scanners.verb_noun_scanner.VerbNounScanner" | rule_name="missing_scanner", description="Rule", behavior_name="common" | common | Catalog with 0 entries (scanner not registered due to class not found) | 0 scanners registered, 1 error logged |
| agile_bot/bots/test_story_bot/rules/invalid_scanner_path.json | invalid_scanner_path.json: {"scanner": "invalid.module.path.InvalidScanner", "description": "Rule", "do": {...}} | 1 scanner: InvalidScanner + 1 error | InvalidScanner: No - cannot be imported<br>Error: "Scanner class import failure: ModuleNotFoundError: No module named 'invalid.module.path'" | rule_name="invalid_scanner_path", description="Rule", behavior_name="common" | common | Catalog with 0 entries (scanner not registered due to import failure) | 0 scanners registered, 1 error logged |
| agile_bot/bots/test_story_bot/rules/no_scanner_property.json | no_scanner_property.json: {"description": "Rule without scanner property", "do": {...}} (missing scanner property) | 1 scanner discovered + 1 error | Scanner: No - missing `scanner` property<br>Error: "Rule file missing required 'scanner' property: agile_bot/bots/test_story_bot/rules/no_scanner_property.json" | Error: Invalid rule structure, behavior_name="common" | common | Catalog with 0 entries (scanner not registered due to missing property) | 0 scanners registered, 1 error logged |
| agile_bot/bots/test_story_bot/rules/ (1000+ rule files)<br>agile_bot/bots/test_story_bot/behaviors/*/3_rules/ (1000+ rule files total) | Multiple rule files with scanner properties | All scanners discovered | All scanner classes found, discovery completes without timeout | Metadata extracted for all scanners | all | Catalog with all entries grouped by behavior_name | All scanners registered, organized by behavior_name |
| agile_bot/bots/test_story_bot/rules/ (7 rule files)<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (25 rule files)<br>agile_bot/bots/test_story_bot/behaviors/4_discovery/3_rules/ (5 rule files)<br>agile_bot/bots/test_story_bot/behaviors/5_exploration/3_rules/ (8 rule files)<br>agile_bot/bots/test_story_bot/behaviors/6_scenarios/3_rules/ (9 rule files)<br>agile_bot/bots/test_story_bot/behaviors/7_tests/3_rules/ (30 rule files)<br>agile_bot/bots/test_story_bot/behaviors/8_code/3_rules/ (43 rule files) | Multiple rule files with scanner properties across all behaviors | 50 scanners: 7 common (VerbNounScanner, ActiveLanguageScanner, ...), 25 shape (StorySizingScanner, BehavioralJourneyScanner, ...), 5 discovery (ExhaustiveDecompositionScanner, ...), 8 exploration, 9 scenarios, 30 tests, 43 code | All scanner classes found | Metadata extracted for all scanners across all behaviors | all | Catalog with 50 entries grouped by behavior_name | 50 scanners registered, organized by behavior_name |
| (no rule directories exist or all empty) | N/A | 0 scanners | N/A - no rule files | N/A - no metadata | none | Empty catalog | 0 scanners registered |
| agile_bot/bots/test_story_bot/rules/ (7 rule files)<br>agile_bot/bots/test_story_bot/behaviors/1_shape/3_rules/ (25 rule files, some with missing scanner classes) | Common rules: Multiple rule files with scanner properties<br>Shape rules: Some rule files reference scanner classes that don't exist | Scanners from common behavior + partial from shape behavior | Common scanners: All found<br>Shape scanners: Some not found (scanner class not found errors) | Metadata extracted for common scanners, errors logged for shape scanners | all | Partial catalog: common scanners registered, shape scanners excluded | Failed scanners excluded, errors logged, common behavior still registered |









