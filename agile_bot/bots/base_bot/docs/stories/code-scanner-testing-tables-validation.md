# Code Scanner Testing Tables - Validation Report

## Validation Against Three Rules

This report validates `code-scanner-testing-tables.md` against:
1. `use_domain_rich_language_in_testing_tables.json`
2. `map_table_columns_to_scenario_parameters.json`
3. `specify_constants_and_stub_values.json`

---

## Rule 1: Use Domain-Rich Language in Testing Tables

### ✅ PASSES

**Story 3 - Knowledge Graph Problems Column:**
- ✅ Uses domain-rich language: "Epic 'Order Management' (noun-only, violates verb-noun rule)"
- ✅ Describes actual problems explicitly
- ✅ Ties back to story graph structure
- ✅ Uses domain terminology (verb-noun format, behavioral language, sizing range)

**Story 4 - Violations Data Column:**
- ✅ Uses concrete examples: "Epic 'Order Management' violation: rule_name='use_verb_noun_format_for_story_elements', line_number=2"
- ✅ Provides actual violation details with context
- ✅ Not generic or abstract

**Real Data Examples:**
- ✅ Enhanced Instructions column shows full text, not just descriptions
- ✅ Code Scanner Output shows complete JSON structures
- ✅ Violation details include actual messages, line numbers, locations

### ⚠️ MINOR ISSUES

**Story 1 - Enhanced Instructions:**
- ✅ Good: Shows full text of enhanced instructions
- ✅ Good: Includes actual violation details
- ⚠️ Note: References "Epic name 'Order Management'" in instructions but this is appropriate since it's showing what the actual output would contain

---

## Rule 2: Map Table Columns to Scenario Parameters

### ✅ PASSES

**Story 1:**
- ✅ Background parameter `{behavior_name}` → Missing "Behavior" column ❌ **VIOLATION**
- ✅ Background parameter `{validation_rules}` → "Validation Rules" column ✅
- ✅ Background parameter `{code_scanners}` → "Code Scanners (Stubbed)" column ✅
- ✅ Background parameter `{code_scanner_output}` → "Code Scanner Output (JSON)" column ✅
- ✅ When/Then parameter `{enhanced_instructions}` → "Enhanced Instructions (Full Text)" column ✅

**Story 2:**
- ✅ Background parameter `{behavior_name}` → Missing "Behavior" column ❌ **VIOLATION**
- ✅ Background parameter `{rule_file_paths}` → "Rule File Paths" column ✅
- ✅ Background parameter `{rule_file_content}` → "Rule File Content (scanner property)" column ✅
- ✅ Background parameter `{discovery_pattern}` → Missing column ❌ **VIOLATION**
- ✅ When/Then parameter `{actual_scanners_discovered}` → "Actual Scanners Discovered" column ✅
- ✅ When/Then parameter `{scanner_class_found}` → "Scanner Class Found?" column ✅

**Story 2 - Scanner Metadata Extraction:**
- ✅ Background parameter `{behavior_name}` → "Behavior" column ✅
- ✅ Background parameter `{rule_file_content}` → "Rule File Content" column ✅
- ✅ When/Then parameter `{expected_scanner_metadata}` → "Expected Scanner Metadata" column ✅

**Story 2 - Scanner Registration:**
- ✅ When/Then parameter `{scanners_discovered}` → "Scanners Discovered" column ✅
- ✅ When/Then parameter `{behaviors}` → "Behaviors" column ✅
- ✅ When/Then parameter `{expected_catalog_structure}` → "Expected Catalog Structure" column ✅
- ✅ When/Then parameter `{expected_catalog_size}` → "Expected Catalog Size" column ✅

**Story 3:**
- ✅ Background parameter `{behavior_name}` → "Behavior" column ✅
- ✅ Background parameter `{knowledge_graph_problems}` → "Knowledge Graph Problems" column ✅
- ✅ Background parameter `{rule_file}` → "Rule File" column ✅
- ✅ Background parameter `{scanner_name}` → Missing, but "Scanner" column exists in some tables ✅
- ✅ Background parameter `{scanner_config}` → Missing column ❌ **VIOLATION** (only in Scanner Configuration table)
- ✅ When/Then parameter `{expected_violation_line}` → "Expected Violation Line" column ✅
- ✅ When/Then parameter `{expected_violation_details}` → "Expected Violation Details" column ✅
- ✅ When/Then parameter `{expected_report_format}` → "Expected Report Format" column ✅
- ✅ When/Then parameter `{expected_report_structure}` → "Expected Report Structure" column ✅

**Story 4:**
- ✅ Background parameter `{behavior_name}` → Missing "Behavior" column in some tables ❌ **VIOLATION**
- ✅ Background parameter `{violations_data}` → "Violations Data" column ✅
- ✅ Background parameter `{report_format}` → "Report Format" column ✅
- ✅ When/Then parameter `{expected_report_structure}` → "Expected Report Structure" column ✅

### ❌ VIOLATIONS FOUND

1. **Story 1 - Missing "Behavior" column:**
   - Background has `{behavior_name}` parameter but table doesn't have "Behavior" column
   - **Impact**: Not explicit which behavior is being tested

2. **Story 2 - Missing "Behavior" column (Scanner Discovery table):**
   - Background has `{behavior_name}` parameter but table doesn't have "Behavior" column
   - **Impact**: Not explicit which behavior is being tested

3. **Story 2 - Missing "Discovery Pattern" column:**
   - Background has `{discovery_pattern}` parameter but table doesn't have column
   - **Impact**: Pattern not visible in table

4. **Story 4 - Missing "Behavior" column (some tables):**
   - Background has `{behavior_name}` parameter but some tables don't have "Behavior" column
   - **Impact**: Not explicit which behavior is being tested

---

## Rule 3: Specify Constants and Stub Values

### ✅ PASSES

**Fixed Directory Structures:**
- ✅ Common rules path is constant: `'agile_bot/bots/story_bot/rules/'`
- ✅ Behavior rules path pattern is fixed: `'agile_bot/bots/story_bot/behaviors/{behavior_number}_{behavior_name}/3_rules/'`
- ✅ Knowledge graph path pattern is fixed: `'agile_bot/bots/story_bot/knowledge_graphs/{behavior_name}/story_graph.json'`
- ✅ Constants are explicitly stated, not parameterized

**Stub Values:**
- ✅ Story 1 explicitly states "Code scanners are stubbed to return '{code_scanner_output}'"
- ✅ Column header says "Code Scanners (Stubbed)" to make it explicit
- ✅ Shows actual hardcoded return values in JSON format
- ✅ Makes clear test is NOT validating scanner logic

**Actual Class Names and Paths:**
- ✅ Uses actual scanner class names: VerbNounScanner, ActiveLanguageScanner, etc.
- ✅ Uses actual rule file paths: `agile_bot/bots/story_bot/rules/use_verb_noun_format_for_story_elements.json`
- ✅ Not using placeholders like `{scanner_class}` or `{rule_file}`

**Removed Irrelevant Parameters:**
- ✅ Story 1 correctly removed "Knowledge Graph Content" column (scanners are stubbed, content doesn't matter)
- ✅ Focus is on orchestration, not scanner logic

### ⚠️ MINOR ISSUES

**Story 3 - Scanner Configuration Table:**
- ✅ Has `{scanner_config}` parameter and "Scanner Config" column
- ✅ This is appropriate since it's testing configuration, not stubbing

---

## Summary

### Overall Assessment: ✅ MOSTLY COMPLIANT

**Strengths:**
1. ✅ Excellent use of domain-rich language throughout
2. ✅ Real data examples with concrete violation details
3. ✅ Constants properly specified (fixed paths)
4. ✅ Stub values explicitly marked and described
5. ✅ Irrelevant parameters removed when stubbing

**Issues Found:**
1. ❌ **4 violations** of Rule 2 (Missing parameter columns):
   - Story 1: Missing "Behavior" column
   - Story 2 (Scanner Discovery): Missing "Behavior" column
   - Story 2 (Scanner Discovery): Missing "Discovery Pattern" column
   - Story 4 (some tables): Missing "Behavior" column

### Recommended Fixes

1. **Add "Behavior" column to Story 1 table:**
   ```
   | Test ID | Behavior | Validation Rules | Code Scanners (Stubbed) | ...
   ```

2. **Add "Behavior" column to Story 2 Scanner Discovery table:**
   ```
   | Test ID | Behavior | Rule File Paths | Rule File Content | ...
   ```

3. **Add "Discovery Pattern" column to Story 2 Scanner Discovery table:**
   ```
   | Test ID | Behavior | Discovery Pattern | Rule File Paths | ...
   ```

4. **Add "Behavior" column to Story 4 tables that are missing it:**
   - Violation Report Generation table
   - Report Output and Persistence table (if behavior is relevant)

---

## Conclusion

The testing tables are **well-structured and mostly compliant** with all three rules. The main issues are missing "Behavior" columns in several tables, which violates Rule 2's requirement that all parameters in Background/When/Then must appear as columns. These are easy fixes that will make the tests more explicit and traceable.

