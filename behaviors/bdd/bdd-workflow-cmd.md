### Command: `bdd-workflow-cmd.md`

**Purpose:** Guide developers through true BDD (Test-Driven Development) with the Red-Green-Refactor cycle for BDD tests.

**Usage:**
* `\BDD-workflow` — Start BDD workflow on current file (auto-creates test file if needed)
* `\BDD-workflow --scope describe` — Work on current describe block
* `\BDD-workflow --scope next:3` — Work on next 3 test signatures
* `\BDD-workflow --scope next:1` — Work on next single test
* `\BDD-workflow --scope all` — Work on all test signatures in file
* `\BDD-workflow --phase signatures` — Build test signatures only
* `\BDD-workflow --phase red` — Jump to RED phase (write failing test)
* `\BDD-workflow --phase green` — Jump to GREEN phase (implement code)
* `\BDD-workflow --phase refactor` — Jump to REFACTOR phase (suggest improvements)
* `python behaviors/bdd/bdd-workflow-runner.py <file-path> [options]` — Run from command line

**Note:** Can be invoked on either test files or production files. If invoked on a production file, automatically creates corresponding test file.

**Rule:**
* `\bdd-workflow-rule` — Core BDD workflow (Red-Green-Refactor cycle)
* `\bdd-rule` — BDD principles (referenced throughout TDD cycle)
* `\bdd-jest-rule` — Jest-specific patterns
* `\bdd-mamba-rule` — Mamba-specific patterns

**Valid Files** (same as BDD behavior rules):
* **Jest**: `["**/*.test.js", "**/*.spec.js", "**/*.test.ts", "**/*.spec.ts", "**/*.test.jsx", "**/*.spec.jsx", "**/*.test.tsx", "**/*.spec.tsx", "**/*.test.mjs", "**/*.spec.mjs"]`
* **Mamba**: `["**/*_test.py", "**/test_*.py", "**/*_spec.py", "**/spec_*.py", "**/*_test.pyi", "**/test_*.pyi", "**/*_spec.pyi", "**/spec_*.pyi"]`

**Implementation:**
* `bdd_workflow()` in `behaviors/bdd/bdd-workflow-runner.py` — Main orchestrator
* `detect_framework_from_file()` — Detect Jest vs Mamba from file path
* `parse_test_structure()` — Extract test signatures and implementation status
* `determine_test_scope()` — Filter tests by scope option
* `run_tests()` — Execute tests and capture results
* `identify_code_relationships()` — Find related code under test and test files

**AI Usage:**
* AI Agent creates test signatures during Phase 0 (SIGNATURES)
* AI Agent validates tests with `/bdd-validate` after EVERY phase
* AI Agent fixes ALL BDD violations before proceeding
* AI Agent implements test code during Phase 1 (RED)
* AI Agent implements production code during Phase 2 (GREEN)  
* AI Agent suggests refactorings during Phase 3a (REFACTOR)
* AI Agent implements approved refactorings during Phase 3b (IMPLEMENT)

**Code Usage:**
* Code parses test file structure and detects implementation status
* Code runs tests and captures pass/fail results
* Code tracks workflow state across sessions
* Code identifies code relationships and impacts

**Steps:**

1. **User** invokes `\bdd-workflow` on file (with optional scope and phase flags)
2. **Code** `bdd_workflow()` checks if file is a test file (matches glob patterns)
3. **IF NOT a test file**: 
   - **Code** `detect_framework_from_file()` detects framework from file extension (.mjs → Jest, .py → Mamba)
   - **Code** `generate_test_file_path()` creates corresponding test file path (e.g., `foo.mjs` → `foo.test.mjs`)
   - **Code** checks if test file already exists
   - **IF test file does NOT exist**: 
     - **Code** presents production file and proposed test file path to AI Agent
     - **AI Agent** creates initial test file structure with imports and basic describe block
     - **Code** saves new test file
   - **Code** switches context to the newly created/found test file
4. **Code** `detect_framework_from_file()` detects framework from file path (Jest vs Mamba)
5. **Code** `BDDRunState()` loads or initializes workflow state from `.bdd-workflow/<filename>.run-state.json`
6. **Code** `parse_test_structure()` parses test file into describe/it blocks with implementation status
7. **Code** `determine_test_scope()` filters tests based on scope option (describe block, next N, all, line number)
8. **Code** identifies current phase from state or user-provided phase flag
9. **Code** presents test structure, scope, and workflow data to AI Agent

### Phase 0: Build Signatures

#### 0.1: Create Test File (if needed)
1. **IF test file does NOT exist** (invoked on production file):
   - **AI Agent** analyzes production file structure (classes, functions, modules)
   - **AI Agent** determines appropriate test file name (e.g., `foo.mjs` → `foo.test.mjs`)
   - **AI Agent** creates test file with:
     - Proper imports from production file
     - Framework-specific setup (Jest: `describe`, Mamba: `with describe`)
     - Top-level describe block matching module/class name
     - Empty body ready for test signatures
   - **AI Agent** saves new test file
   - **Code** confirms test file creation and switches context

#### 0.2: Build Test Signatures

**Sample Steps (sample_1, sample_2, sample_N) - Pattern Learning:**
1. **Code** `load_rule_examples(test_file_path)` loads rule file and presents DO/DON'T examples from all sections (§ 1-5) to AI Agent
2. **AI Agent** creates ONE complete behavioral example (one describe block with ~18 tests) aligning to the rules and DO/DON'T examples
3. **AI Agent** writes test signatures following examples (fluent language, proper nesting)
4. **Human** reviews test and chooses:
   - **Proceed** → Move to next sample or expand
   - **Expand** → Skip remaining samples, go to expand step
   - **Validate** → Run `/bdd-validate` to check for violations and fix them
6. **IF Human chose Validate:** 
   - **AI Agent** runs `/bdd-validate`
   - **AI Agent** fixes ALL violations
   - **AI Agent** re-validates until ZERO violations
   - **AI Agent** LEARNS patterns from violations fixed
   - **Human** reviews fixes, then proceeds to next sample or expand

**Expand Step (expand) - Full Coverage:**
1. **AI Agent** creates ALL remaining test signatures in ONE batch, applying learned patterns
2. **AI Agent** ensures comprehensive coverage: all settings, hooks, edge cases, failures
3. **MANDATORY**: **AI Agent** runs `/bdd-validate` on complete set (NO EXCEPTIONS)
4. **MANDATORY**: **AI Agent** fixes ALL violations - MUST achieve zero violations
5. **Workflow** auto-approves and completes expand run
6. **Phase 0 Complete** - Ready for Phase 1 (RED)

**Key:** Samples teach patterns (small batches). Expand applies patterns (all at once).

### Phase 1: RED - Write Failing Test

1. **AI Agent** implements ALL test signatures in scope following `bdd-rule.mdc` § 2-5
2. **AI Agent** writes proper arrange/act/assert, helpers, mocking
3. **MANDATORY**: **AI Agent** runs `/bdd-validate` on all tests (NO EXCEPTIONS)
4. **MANDATORY**: **AI Agent** fixes ALL violations - MUST achieve zero violations
5. **Code** identifies code under test and comments it out (if exists)
6. **Code** `run_tests()` runs all tests and captures failure output
7. **Code** verifies failures are for RIGHT reason (not defined, not syntax errors)
8. **AI Agent** confirms tests fail for correct reasons
9. **Workflow** auto-approves and completes RED phase
10. **Ready for Phase 2 (GREEN)**

### Phase 2: GREEN - Implement Minimal Code

1. **AI Agent** uncomments/writes minimal code under test to make ALL tests pass
2. **AI Agent** resists adding features no test demands
3. **Code** `run_tests()` runs all tests to verify they pass
4. **Code** checks for regressions in existing tests
5. **AI Agent** verifies all tests pass with no regressions
6. **MANDATORY**: **AI Agent** runs `/bdd-validate` on tests (NO EXCEPTIONS)
7. **MANDATORY**: **AI Agent** fixes ALL violations - MUST achieve zero violations
8. **Workflow** auto-approves and completes GREEN phase
9. **Ready for Phase 3 (REFACTOR) or finish**

### Phase 3: REFACTOR - Improve Code Quality

1. **Code** `identify_code_relationships()` finds code under test and related test files
2. **AI Agent** runs `/bdd-validate` to ensure tests follow BDD principles (NO EXCEPTIONS)
3. **AI Agent** fixes ALL violations before refactoring (MUST achieve zero violations)
4. **AI Agent** identifies all code smells in code under test (duplication, long methods, magic values, poor names)
5. **AI Agent** suggests refactorings with WHAT to change, WHY, and trade-offs
6. **User** reviews and approves refactorings
7. **AI Agent** implements ALL approved refactorings to code under test
8. **Code** `run_tests()` verifies all tests still pass
9. **AI Agent** runs `/bdd-validate` to ensure BDD quality maintained
10. **AI Agent** fixes any violations
11. **Workflow** auto-approves and completes REFACTOR phase
12. **User** (optional) commits changes

### Repeat Cycle

1. **Code** identifies next unimplemented test in scope
2. **Repeat** Phase 1 through Phase 3 until all tests in scope are implemented
3. **Code** `BDDRunState.complete_run()` updates state to completed
4. **User** decides next action: expand scope, start new feature, or finish session

---
REFACTORING SUGGESTIONS for UserService.authenticate():


## Workflow States

The command tracks workflow state in the test file as comments:

```javascript
// BDD-WORKFLOW-STATE: phase=red, scope=describe, test=2/5
describe('user authentication', () => {
  it('should return token when credentials are valid', () => {
    // BDD: IMPLEMENTED (GREEN)
    // ...
  });
  
  it('should throw error when credentials are invalid', () => {
    // BDD: NEXT (RED)
    // TODO: implement
  });
});
```

State markers:
* `BDD: SIGNATURE` — Test signature created, not implemented
* `BDD: RED` — Test written, currently failing
* `BDD: GREEN` — Test passing, code implemented
* `BDD: REFACTOR` — Ready for refactoring suggestions
* `BDD: NEXT` — Next test to implement

---


## Command Options

### Scope Options

* `--scope describe` (default) — Work on all tests in current describe block
* `--scope next:N` — Work on next N tests (e.g., `next:1`, `next:3`)
* `--scope all` — Work on all test signatures in file
* `--scope line:N` — Work on test at specific line number

### Phase Options

* `--phase signatures` — Only create test signatures
* `--phase red` — Jump to RED phase (skip signatures)
* `--phase green` — Jump to GREEN phase (assumes tests are failing)
* `--phase refactor` — Jump to REFACTOR phase (assumes tests passing)

### Mode Options

* `--auto` — Automatic mode (proceed through phases without prompting)
* `--interactive` (default) — Prompt for approval at each phase
* `--suggest-only` — Only suggest refactorings, don't implement

### Example Usage

```bash
# Start BDD workflow on current file (auto-creates test file if needed)
\BDD-workflow

# Start BDD workflow on production file (creates UserService.test.js)
# Open UserService.js, then:
\BDD-workflow --scope all --phase signatures

# Work on next 3 tests in auto mode
\BDD-workflow --scope next:3 --auto

# Just build test signatures for entire file
\BDD-workflow --scope all --phase signatures

# Jump to refactor phase for current test
\BDD-workflow --phase refactor

# Command line usage on test file
python behaviors/bdd/bdd-workflow-runner.py src/auth/AuthService.test.js --scope describe

# Command line usage on production file (auto-creates test file)
python behaviors/bdd/bdd-workflow-runner.py src/auth/AuthService.js --scope all

# Interactive with thorough refactoring suggestions
python behaviors/bdd/bdd-workflow-runner.py src/auth/AuthService.test.js --interactive --suggest-only
```

---

## Integration

This command integrates with:
* **BDD Validation** (`\bdd-validate`) — MANDATORY validation after every phase to ensure tests follow BDD principles
* **CRITICAL**: AI Agent MUST run `/bdd-validate` and fix ALL violations before proceeding to next phase


## Implementation

**Files:**
* `behaviors/bdd/bdd-workflow-runner.py` — Main command implementation
* `behaviors/bdd/bdd-workflow-rule.mdc` — Core BDD workflow rule
* `behaviors/bdd/bdd-workflow-jest-rule.mdc` — Jest-specific patterns
* `behaviors/bdd/bdd-workflow-mamba-rule.mdc` — Mamba-specific patterns

**Division of Labor:**
* **Code**: File parsing, test running, state tracking, result capture
* **AI Agent**: Test writing, code implementation, refactoring suggestions
* **AI Agent (MANDATORY)**: Run `/bdd-validate` after EVERY phase, fix ALL violations before proceeding

**State Management:**
* Separate state file (`.bdd-workflow/<filename>.run-state.json`) tracks overall workflow state
* State persists across sessions for long workflows
* Tracks run ID, step type, status, timestamps, and validation results

#   T e s t   c h a n g e 
 
 