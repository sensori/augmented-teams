# AI-Based Code Rules Analysis: Test Files Cross-File Violations

**Analysis Date:** 2025-01-XX  
**Scope:** All test files in `agile_bot/bots/base_bot/test/`  
**Focus:** Cross-file violations that worsen when considering the entire codebase together  
**Rules Analyzed:** All rules from `agile_bot/bots/story_bot/behaviors/8_code/3_rules/`

---

## Executive Summary

When analyzing the test codebase as a **whole system** rather than individual files, several critical violations emerge that are **worse** than what single-file scanners detect:

1. **Massive Duplication** - Same helper functions duplicated across 7+ files
2. **File Size Violations** - One file exceeds 3,000 lines (6x the recommended limit)
3. **Incomplete Refactoring** - Multiple patterns coexist (old vs new formats)
4. **Poor Abstraction Levels** - Test setup mixed with test logic throughout
5. **Naming Inconsistencies** - Same concepts named differently across files
6. **Concern Separation** - Test infrastructure mixed with test assertions

**Key Finding:** The codebase violates the "refactor completely, not partially" rule - multiple incompatible patterns exist simultaneously, creating confusion and maintenance burden.

---

## 1. ELIMINATE DUPLICATION - CRITICAL VIOLATION

### Cross-File Duplication Patterns

#### Pattern 1: `create_bot_config` / `create_bot_config_file` (7 files)

**Violation Severity:** 🔴 **CRITICAL** - Same logic duplicated 7 times with variations

**Files Affected:**
1. `test_helpers.py` (line 54-59)
2. `test_base_action.py` (line 20-30)
3. `test_init_project.py` (line 25-30)
4. `test_generate_bot_server_and_tools.py` (line 23-29)
5. `test_invoke_bot_tool.py` (line 27-36)
6. `test_bot_execute_behavior.py` (line 17-26)
7. `conftest.py` (line 91-97) ✅ **This is the canonical version**

**Cross-File Impact:**
- **7 implementations** of essentially the same function
- **3 different parameter patterns** (bot_directory vs workspace, bot_name handling)
- **2 different path construction methods** (direct vs helper-based)
- **Maintenance burden:** Changes to bot config structure require updates in 7 places

**Rule Violation:** "Every piece of knowledge should have a single, authoritative representation (DRY principle)"

**Recommendation:** All files should use `conftest.py`'s `create_bot_config_file()`. The variations are unnecessary and create confusion.

---

#### Pattern 2: `create_workflow_state` Variations (6+ files)

**Violation Severity:** 🔴 **CRITICAL** - Same concept implemented 6+ times with incompatible formats

**Files Affected:**
1. `test_helpers.py` (line 68-83) - Uses helper function
2. `test_invoke_bot_tool.py` (line 57-67) - Direct implementation, hardcoded timestamp
3. `test_validate_knowledge_and_content_against_rules.py` (line 33-42) - `create_workflow_state_local()`, hardcoded behavior
4. `test_workflow_action_sequence.py` (line 18-33) - Wrapper function
5. `test_close_current_action.py` (line 24-38) - Wrapper function
6. `conftest.py` (line 99-114) ✅ **This is the canonical version**

**Cross-File Impact:**
- **6+ implementations** creating workflow state files
- **3 different formats:**
  - `bot_name.behavior` format (conftest.py)
  - `bot_name.behavior.action` format (some tests)
  - Hardcoded `'story_bot.exploration'` (test_validate_knowledge_and_content_against_rules.py)
- **Inconsistent timestamp handling** (some include, some don't, different formats)
- **Different parameter names** (`workspace_dir` vs `workspace`)

**Rule Violation:** "Extract repeated logic into reusable functions" and "Apply DRY principle to both code and data"

**Recommendation:** Standardize on `conftest.py`'s `create_workflow_state_file()` with optional parameters for variations.

---

#### Pattern 3: `create_actions_workflow_json` (2 files, incompatible formats)

**Violation Severity:** 🟡 **HIGH** - Two incompatible implementations

**Files Affected:**
1. `test_helpers.py` (line 201-280+) - **New format** with `instructions` array per action
2. `test_bot_execute_behavior.py` (line 29-58+) - **Old format** with `actions_workflow` structure

**Cross-File Impact:**
- **Incompatible data structures** - Tests using one format won't work with code expecting the other
- **Confusion about which format is correct** - No clear migration path
- **Violates "refactor completely, not partially" rule**

**Rule Violation:** "When refactoring, replace old code completely - don't try to support both legacy and new patterns"

**Recommendation:** Choose one format (prefer `test_helpers.py` new format), update all tests, delete old format.

---

#### Pattern 4: `MockBot` Class (2 identical instances)

**Violation Severity:** 🟡 **MEDIUM** - Same class defined twice in one file

**Location:** `test_build_knowledge.py`
- Line 767-769
- Line 806-808

**Cross-File Impact:**
- Could be extracted to shared fixture/helper
- Currently only in one file, but pattern suggests it might be needed elsewhere

**Recommendation:** Extract to `conftest.py` or `test_helpers.py` as a fixture or factory function.

---

## 2. KEEP FUNCTIONS SMALL FOCUSED - VIOLATION

### Large Test Functions Across Files

**Violation Severity:** 🟡 **HIGH** - Multiple test functions exceed 20-30 line guideline

**Cross-File Pattern:**
- Test functions mixing **setup**, **execution**, and **assertions** in single functions
- Many test functions are 50-100+ lines
- Complex test setup not extracted to helpers

**Example Pattern Found:**
```python
def test_something(self, bot_directory, workspace_directory):
    # 10 lines of setup
    bot_dir = tmp_path / "test_bot"
    bot_dir.mkdir()
    docs_dir = bot_dir / "docs" / "stories"
    docs_dir.mkdir(parents=True)
    story_graph = {...}  # 20 lines of test data
    story_graph_path.write_text(...)
    # 10 lines of execution
    # 10 lines of assertions
```

**Rule Violation:** "Keep functions under 20 lines when possible" and "Extract complex logic into named helper functions"

**Cross-File Impact:**
- Test readability suffers when setup is verbose
- Test maintenance harder when logic is embedded
- Similar setup patterns duplicated across files

**Recommendation:** Extract test setup to helper functions/fixtures. Use builder pattern for complex test data.

---

## 3. KEEP CLASSES SINGLE RESPONSIBILITY - VIOLATION

### Test Classes with Multiple Responsibilities

**Violation Severity:** 🟡 **MEDIUM** - Some test classes mix concerns

**Cross-File Pattern:**
- Test classes that both **set up test infrastructure** AND **run test assertions**
- Helper classes that both **create test data** AND **verify test results**

**Example:** `TriggerTestSetup` in `test_invoke_bot_cli.py`
- Sets up bot configuration
- Creates trigger words
- Creates workflow state
- Could be split into: `BotSetupHelper`, `TriggerWordHelper`, `WorkflowStateHelper`

**Rule Violation:** "Each class should have one reason to change"

**Recommendation:** Split helper classes by responsibility. Use composition to combine helpers.

---

## 4. MAINTAIN VERTICAL DENSITY - VIOLATION

### File Size Violations

**Violation Severity:** 🔴 **CRITICAL** - One file exceeds recommended size by 6x

**File:** `test_validate_knowledge_and_content_against_rules.py`
- **3,160 lines** (recommended: <500 lines)
- **46 test functions**
- **36 classes/functions defined**

**Cross-File Impact:**
- File is **6x larger** than recommended
- Hard to navigate and understand
- Related code scattered throughout file
- Violates "keep files under 500 lines when possible"

**Rule Violation:** "Keep files under 500 lines when possible"

**Recommendation:** Split into multiple files:
- `test_validate_rules_activity.py` (activity tracking tests)
- `test_validate_rules_scanners.py` (scanner discovery tests)
- `test_validate_rules_violations.py` (violation reporting tests)
- `test_validate_rules_scope.py` (scope filtering tests)
- `test_validate_rules_exceptions.py` (exception handling tests)

---

### Other Large Files

**Files exceeding 500 lines:**
- `test_generate_bot_server_and_tools.py` - 978 lines (2x limit)
- `test_build_knowledge.py` - 782 lines (1.5x limit)
- `test_workflow_action_sequence.py` - 596 lines (slightly over)

**Recommendation:** Review and split these files as well.

---

## 5. REFACTOR COMPLETELY NOT PARTIALLY - CRITICAL VIOLATION

### Multiple Incompatible Patterns Coexisting

**Violation Severity:** 🔴 **CRITICAL** - Codebase violates this rule extensively

**Pattern 1: Workflow State Creation**
- **Old pattern:** Direct JSON file creation with hardcoded values
- **New pattern:** Factory function in `conftest.py` with structured format
- **Current state:** Both patterns exist simultaneously

**Pattern 2: Behavior JSON Creation**
- **Old pattern:** `actions_workflow` structure with separate key
- **New pattern:** `instructions` array per action in actions list
- **Current state:** Both formats exist, tests use different ones

**Pattern 3: Bot Config Creation**
- **Old pattern:** Direct path construction in each test file
- **New pattern:** Factory function in `conftest.py`
- **Current state:** 7 different implementations coexist

**Rule Violation:** "When refactoring, replace old code completely - don't try to support both legacy and new patterns"

**Cross-File Impact:**
- **Confusion:** Developers don't know which pattern to use
- **Inconsistency:** Tests behave differently depending on which pattern they use
- **Maintenance burden:** Two code paths to maintain
- **Technical debt:** Refactoring never completed

**Recommendation:** 
1. **Choose canonical pattern** for each concept
2. **Update all files** to use canonical pattern
3. **Delete old implementations** completely
4. **Update tests** to verify new pattern works

---

## 6. USE INTENTION REVEALING NAMES - VIOLATION

### Naming Inconsistencies Across Files

**Violation Severity:** 🟡 **MEDIUM** - Same concepts named differently

**Pattern 1: Workflow State Functions**
- `create_workflow_state()` - in test_helpers.py
- `create_workflow_state_file()` - in conftest.py
- `create_workflow_state_local()` - in test_validate_knowledge_and_content_against_rules.py
- `create_test_workflow()` - in test_close_current_action.py

**All do similar things but names don't reveal they're related!**

**Pattern 2: Bot Config Functions**
- `create_bot_config()` - in 4 files
- `create_bot_config_file()` - in 3 files

**Pattern 3: Test Setup Functions**
- `bootstrap_env()` - in test_helpers.py and conftest.py
- `setup_bot()` - in TriggerTestSetup class
- Various inline setup code

**Rule Violation:** "Names should clearly communicate purpose and usage" and "Use names that answer 'why does this exist?'"

**Cross-File Impact:**
- **Search difficulty:** Can't find all related functions easily
- **Confusion:** Similar names for different things, different names for same things
- **Maintenance:** Hard to know which function to use

**Recommendation:** 
- Standardize naming: `create_workflow_state_file()` (canonical)
- Use consistent prefixes: `create_*` for factories, `setup_*` for initialization
- Document naming conventions

---

## 7. SEPARATE CONCERNS - VIOLATION

### Mixed Concerns in Test Files

**Violation Severity:** 🟡 **MEDIUM** - Test infrastructure mixed with test logic

**Cross-File Pattern:**
- **Test setup code** (file system operations, JSON creation) mixed with **test assertions**
- **Helper functions** defined inline in test files instead of shared modules
- **Test data creation** embedded in test functions instead of builders/factories

**Example Pattern:**
```python
def test_something(self, tmp_path):
    # Infrastructure concern: Create file structure
    bot_dir = tmp_path / "test_bot"
    bot_dir.mkdir()
    config_dir = bot_dir / "config"
    config_dir.mkdir()
    config_file = config_dir / "bot_config.json"
    config_file.write_text(json.dumps({...}), encoding='utf-8')
    
    # Business logic concern: Test behavior
    bot = Bot(...)
    result = bot.doSomething()
    
    # Assertion concern: Verify results
    assert result == expected
```

**Rule Violation:** "Keep pure calculations separate from I/O" and "Isolate business logic from infrastructure"

**Cross-File Impact:**
- **Test readability:** Hard to see what's being tested vs what's setup
- **Reusability:** Setup code duplicated instead of reused
- **Maintainability:** Changes to infrastructure require updating many test functions

**Recommendation:**
- Extract all file system operations to fixtures/factories
- Use builder pattern for complex test data
- Keep test functions focused on: Given/When/Then structure

---

## 8. MAINTAIN ABSTRACTION LEVELS - VIOLATION

### Mixed Abstraction Levels in Tests

**Violation Severity:** 🟡 **MEDIUM** - High-level test logic mixed with low-level file operations

**Cross-File Pattern:**
- Test functions jump between:
  - **High-level:** "Test that validation works"
  - **Low-level:** `Path(...).mkdir(parents=True)`, `write_text(json.dumps(...))`
  - **High-level:** Assertions about business logic

**Rule Violation:** "Code should flow from high-level concepts down to details" and "Don't mix low-level details with high-level concepts"

**Cross-File Impact:**
- **Readability:** Hard to understand test intent when buried in file operations
- **Maintenance:** Low-level details scattered throughout tests
- **Reusability:** Can't reuse high-level test patterns because they're coupled to low-level details

**Recommendation:**
- Use fixtures for all file system setup
- Create high-level test helpers: `setup_bot_with_behaviors()`, `create_workflow_at_action()`
- Keep test functions at high abstraction level

---

## 9. KEEP CLASSES SMALL COMPACT - VIOLATION

### Large Test Classes

**Violation Severity:** 🟡 **MEDIUM** - Some test classes are too large

**Example:** `TestValidateKnowledgeAndContentAgainstRules` classes in `test_validate_knowledge_and_content_against_rules.py`
- Multiple test classes in one file
- Each class has many test methods
- Related but could be split by story/epic

**Rule Violation:** "Keep classes cohesive" and "Focus on single responsibility"

**Recommendation:** Split large test classes by story/epic into separate files.

---

## Summary: Cross-File Violations That Get Worse

### When Considering the Entire Codebase Together:

1. **Duplication is SYSTEMIC** - Not just a few functions, but entire patterns duplicated across 7+ files
2. **Incomplete Refactoring is PERVASIVE** - Multiple incompatible patterns coexist throughout
3. **File Size Violations are EXTREME** - One file is 6x the recommended size
4. **Naming Inconsistencies CREATE CONFUSION** - Same concepts have different names, making codebase hard to navigate
5. **Concern Separation is POOR** - Infrastructure code mixed with test logic throughout

### Key Insight:

**Single-file scanners miss these violations** because they only see one file at a time. When you look at the **entire codebase together**, the violations compound:

- **7 duplicate implementations** × **maintenance burden** = **7x the work**
- **2 incompatible formats** × **confusion** = **tests that break unpredictably**
- **3,160 line file** × **navigation difficulty** = **harder to maintain**

### Priority Actions:

1. **🔴 CRITICAL:** Eliminate duplication - Consolidate all `create_bot_config` and `create_workflow_state` functions
2. **🔴 CRITICAL:** Complete refactoring - Choose one format for behavior JSON, update all files, delete old format
3. **🔴 CRITICAL:** Split large file - Break `test_validate_knowledge_and_content_against_rules.py` into 5+ files
4. **🟡 HIGH:** Standardize naming - Use consistent names for similar functions across files
5. **🟡 HIGH:** Extract test setup - Move all file system operations to fixtures/helpers

---

## Recommendations by Rule

### eliminate_duplication.json
- ✅ Extract all duplicate helper functions to `conftest.py` or `test_helpers.py`
- ✅ Update all test files to use canonical implementations
- ✅ Delete duplicate implementations

### refactor_completely_not_partially.json
- ✅ Choose canonical format for behavior JSON (prefer new format)
- ✅ Update all tests to use canonical format
- ✅ Delete old format implementations
- ✅ Update all `create_workflow_state` calls to use `conftest.py` version

### keep_functions_small_focused.json
- ✅ Extract test setup to helper functions
- ✅ Use builder pattern for complex test data
- ✅ Keep test functions under 30 lines

### maintain_vertical_density.json
- ✅ Split `test_validate_knowledge_and_content_against_rules.py` into 5+ files
- ✅ Review and split other files over 500 lines

### use_intention_revealing_names.json
- ✅ Standardize function names across files
- ✅ Document naming conventions
- ✅ Use consistent prefixes (`create_*`, `setup_*`, `verify_*`)

### separate_concerns.json
- ✅ Extract all file system operations to fixtures
- ✅ Use high-level test helpers
- ✅ Keep test functions focused on Given/When/Then

### maintain_abstraction_levels.json
- ✅ Use fixtures for all setup
- ✅ Create high-level test helpers
- ✅ Keep test functions at high abstraction level

---

## Files Requiring Immediate Attention

### High Priority (Critical Violations):
1. `test_validate_knowledge_and_content_against_rules.py` - Split into 5+ files
2. `test_generate_bot_server_and_tools.py` - Remove duplicate `create_bot_config`
3. `test_invoke_bot_tool.py` - Replace `create_bot_config_file` and `create_workflow_state` with conftest versions
4. `test_bot_execute_behavior.py` - Replace `create_actions_workflow_json` with test_helpers version
5. `test_build_knowledge.py` - Extract `MockBot` to shared helper

### Medium Priority:
6. `test_base_action.py` - Replace `create_bot_config` with conftest version
7. `test_init_project.py` - Replace `create_bot_config` with conftest version
8. `test_validate_knowledge_and_content_against_rules.py` - Replace `create_workflow_state_local` with conftest version
9. All files - Extract test setup to helpers/fixtures

---

## Conclusion

The test codebase violates multiple clean code rules **more severely when considered as a whole** than individual file scanners detect. The primary issues are:

1. **Systemic duplication** across 7+ files
2. **Incomplete refactoring** leaving multiple incompatible patterns
3. **Extreme file size violations** (6x recommended limit)
4. **Naming inconsistencies** creating navigation difficulties
5. **Poor concern separation** mixing infrastructure with test logic

**Action Required:** Comprehensive refactoring to eliminate duplication, complete partial refactorings, and improve code organization.




