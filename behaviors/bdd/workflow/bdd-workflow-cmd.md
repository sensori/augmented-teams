### Command: `bdd-workflow-cmd.md`

**Purpose:** Guide developers through true BDD (Test-Driven Development) with the Red-Green-Refactor cycle for BDD tests.

**Usage:**
* `\BDD-workflow` — Start BDD workflow on current file (auto-creates test file if needed)
* `\BDD-workflow --scope describe` — Work on current describe block
* `\BDD-workflow --scope next:3` — Work on next 3 test signatures
* `\BDD-workflow --scope next:1` — Work on next single test
* `\BDD-workflow --scope all` — Work on all test signatures in file
* `\BDD-workflow --stage scaffold` — Build domain scaffolding only
* `\BDD-workflow --stage signatures` — Build test signatures only
* `\BDD-workflow --stage red` — Jump to RED stage (write failing test)
* `\BDD-workflow --stage green` — Jump to GREEN stage (implement code)
* `\BDD-workflow --stage refactor` — Jump to REFACTOR stage (suggest improvements)
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

### Stage 0: Domain Scaffolding

**Purpose:** Create natural language describe block hierarchy from domain map

1. **AI Agent** reads domain map for the module
2. **AI Agent** creates describe blocks following behavioral lifecycle patterns
3. **AI Agent** nests describe blocks using linking words ("that is", "that has", "whose")
4. **AI Agent** validates against domain scaffold rules
5. **Human** reviews and approves hierarchy

### Stage 1: Signatures

#### 1.1: Create Test File (if needed)
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

#### 1.2: Build Test Signatures

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
6. **Stage 1 Complete** - Ready for Stage 2 (RED)

**Key:** Samples teach patterns (small batches). Expand applies patterns (all at once).

### Stage 2: RED - Write Failing Test

**STEP 0: State Enforcement (MANDATORY - Code runs FIRST)**
1. **Code** `check_can_start_run(run_state)` - Enforces previous run is complete
2. **IF previous run NOT complete**: 
   - **Code** displays error with current run status
   - **Code** STOPS execution - AI CANNOT proceed
   - **Human** must complete previous run (validate/approve/abandon) before continuing
3. **IF can proceed**: Continue to Sample Steps

**Sample Steps (sample_1, sample_2, sample_N) - Pattern Learning:**
1. **Code** `load_rule_examples()` loads BDD rules and RED phase examples
2. **Code** `start_run(StepType.RED_BATCH)` - Creates new run, status = STARTED
3. **AI Agent** implements ONE batch of tests (~18 tests) in failing state
4. **AI Agent** writes proper arrange/act/assert, helpers, mocking following § 2-5
5. **Code** identifies code under test and comments it out (if exists)
6. **Code** `run_tests()` runs tests and verifies failures for RIGHT reason (not defined, not syntax errors)
7. **MANDATORY - Validation with § 3 Detection**:
   - **AI Agent** runs `/bdd-validate` on batch
   - **Code** (via validate command) performs static checks
   - **Code** OUTPUTS suspected § 3 violations to chat:
     * Duplicate Arrange in 3+ sibling it() blocks
     * Identical beforeEach() in sibling describes
     * Repeated mock objects across tests
     * Repeated global.* assignments
   - **AI Agent** REVIEWS each suspected violation
   - **AI Agent** REPORTS violations to Human with:
     * Line numbers and code snippets
     * Severity assessment (HIGH/MEDIUM/LOW)
     * Suggested fixes (DO examples)
   - **Human** DECIDES which violations to fix
   - **AI Agent** FIXES violations per human direction
   - **AI Agent** RE-RUNS `/bdd-validate` if fixes were made
8. **Code** `record_ai_verification()` - Updates run status to AI_VERIFIED
9. **Human** reviews tests and chooses:
   - **Proceed** → Move to next sample batch
   - **Expand** → Skip remaining samples, go to expand step
   - **Reject** → AI fixes issues, back to step 3
10. **IF Human chose Proceed**: 
   - **Code** `record_human_approval()` - Updates status to HUMAN_APPROVED
   - **Code** `complete_run()` - Marks run COMPLETED
   - Repeat for next sample batch
11. **IF Human chose Expand**: Go to Expand Step
12. **AI Agent** LEARNS patterns from violations fixed

**Expand Step (expand) - Full Coverage:**
1. **Code** `check_can_start_run()` - Ensures previous sample runs complete
2. **Code** `start_run(StepType.RED_BATCH)` for expand scope
3. **AI Agent** implements ALL remaining test signatures in scope, applying learned patterns
4. **Code** `run_tests()` verifies all fail for RIGHT reason
5. **MANDATORY - Validation with § 3 Detection**:
   - **AI Agent** runs `/bdd-validate` on all tests (NO EXCEPTIONS)
   - **Code** OUTPUTS suspected § 3 violations with line numbers
   - **AI Agent** REVIEWS each suspected violation
   - **AI Agent** REPORTS violations to Human with severity and suggestions
   - **Human** DECIDES which violations to fix (can defer to refactor phase)
   - **AI Agent** FIXES violations per human direction
   - **AI Agent** RE-RUNS `/bdd-validate` if fixes were made
6. **Code** `record_ai_verification()`
7. **Human** reviews and approves expand run
8. **Code** `record_human_approval()`
9. **Code** `complete_run()` - Marks expand COMPLETED
10. **Stage 2 Complete** - Ready for Stage 3 (GREEN)

**Key:** Small batches teach patterns. Expand applies patterns to full scope.

### Stage 3: GREEN - Implement Minimal Code

**STEP 0: State Enforcement (MANDATORY - Code runs FIRST)**
1. **Code** `check_can_start_run(run_state)` - Enforces previous run is complete
2. **IF previous run NOT complete**: 
   - **Code** displays error with current run status
   - **Code** STOPS execution - AI CANNOT proceed
   - **Human** must complete previous run before continuing
3. **IF can proceed**: Continue to Sample Steps

**Sample Steps (sample_1, sample_2, sample_N) - Pattern Learning:**
1. **Code** `start_run(StepType.GREEN_BATCH)` - Creates new run, status = STARTED
2. **AI Agent** uncomments/writes minimal code for ONE batch of tests (~18 tests)
3. **AI Agent** resists adding features no test demands
4. **Code** `run_tests()` runs batch tests to verify they pass
5. **Code** checks for regressions in existing tests
6. **MANDATORY - Validation with § 3 Detection**:
   - **AI Agent** runs `/bdd-validate` on tests
   - **Code** OUTPUTS suspected § 3 violations with line numbers
   - **AI Agent** REVIEWS each suspected violation
   - **AI Agent** REPORTS violations to Human with severity and suggestions
   - **Human** DECIDES which violations to fix
   - **AI Agent** FIXES violations per human direction
   - **AI Agent** RE-RUNS `/bdd-validate` if fixes were made
7. **Code** `record_ai_verification()` - Updates run status to AI_VERIFIED
9. **Human** reviews implementation and chooses:
   - **Proceed** → Move to next sample batch
   - **Expand** → Skip remaining samples, go to expand step
   - **Reject** → AI fixes issues, back to step 2
10. **IF Human chose Proceed**: 
   - **Code** `record_human_approval()` - Updates status to HUMAN_APPROVED
   - **Code** `complete_run()` - Marks run COMPLETED
   - Repeat for next sample batch
11. **IF Human chose Expand**: Go to Expand Step

**Expand Step (expand) - Full Coverage:**
1. **Code** `check_can_start_run()` - Ensures previous sample runs complete
2. **Code** `start_run(StepType.GREEN_BATCH)` for expand scope
3. **AI Agent** implements ALL remaining code under test in scope
4. **Code** `run_tests()` verifies all tests pass with no regressions
5. **MANDATORY - Validation with § 3 Detection**:
   - **AI Agent** runs `/bdd-validate` on all tests (NO EXCEPTIONS)
   - **Code** OUTPUTS suspected § 3 violations with line numbers
   - **AI Agent** REVIEWS each suspected violation
   - **AI Agent** REPORTS violations to Human with severity and suggestions
   - **Human** DECIDES which violations to fix (can defer to refactor phase)
   - **AI Agent** FIXES violations per human direction
   - **AI Agent** RE-RUNS `/bdd-validate` if fixes were made
6. **Code** `record_ai_verification()`
7. **Human** reviews and approves expand run
8. **Code** `record_human_approval()`
9. **Code** `complete_run()` - Marks expand COMPLETED
10. **Stage 3 Complete** - Ready for Stage 4 (REFACTOR) or finish

**Key:** Small batches verify minimal implementation. Expand completes full scope.

### Stage 4: REFACTOR - Improve Code Quality

**STEP 0: State Enforcement (MANDATORY - Code runs FIRST)**
1. **Code** `check_can_start_run(run_state)` - Enforces previous run is complete
2. **IF previous run NOT complete**: 
   - **Code** displays error with current run status
   - **Code** STOPS execution - AI CANNOT proceed
   - **Human** must complete previous run before continuing
3. **IF can proceed**: Continue to Sample Steps

**Sample Steps (sample_1, sample_2, sample_N) - Pattern Learning:**

**Stage 4a: SUGGEST Refactorings**
1. **Code** `start_run(StepType.REFACTOR_SUGGEST)` - Creates new run, status = STARTED
2. **Code** `identify_code_relationships()` finds code under test and related test files
3. **AI Agent** runs `/bdd-validate` to ensure tests follow BDD principles (NO EXCEPTIONS)
4. **AI Agent** fixes ALL violations before refactoring (MUST achieve zero violations)
5. **AI Agent** identifies code smells in ONE batch of code under test (~1-2 files/classes)
6. **AI Agent** suggests refactorings with WHAT to change, WHY, and trade-offs
7. **Code** `record_ai_verification()` - Updates run status to AI_VERIFIED
8. **Human** reviews suggestions and chooses:
   - **Approve** → Proceed to Stage 4b (implement these refactorings)
   - **Reject** → AI revises suggestions
   - **Skip** → Skip refactoring for this batch
   - **Expand** → Get suggestions for all remaining code
9. **IF Human chose Approve**: 
   - **Code** `record_human_approval()` - Updates status to HUMAN_APPROVED
   - **Code** `complete_run()` - Marks suggest run COMPLETED
   - Proceed to Stage 4b
10. **IF Human chose Expand**: Go to Expand Step

**Stage 4b: IMPLEMENT Refactorings (after 4a approval)**
1. **Code** `check_can_start_run()` - Ensures suggest run complete
2. **Code** `start_run(StepType.REFACTOR_IMPLEMENT)` - Creates new run, status = STARTED
3. **AI Agent** implements ONE approved refactoring at a time
4. **Code** `run_tests()` verifies all tests still pass after each refactoring
5. **AI Agent** stops if any test fails and fixes before continuing
6. **MANDATORY**: **AI Agent** runs `/bdd-validate` after all refactorings
7. **MANDATORY**: **AI Agent** fixes any violations
8. **Code** `record_ai_verification()`
9. **Human** reviews refactored code and chooses:
   - **Proceed** → Move to next sample batch (back to 4a)
   - **Expand** → Implement all remaining refactorings
   - **Reject** → AI reverts or fixes
10. **IF Human chose Proceed**: 
   - **Code** `record_human_approval()` - Updates status to HUMAN_APPROVED
   - **Code** `complete_run()` - Marks implement run COMPLETED
   - Return to Stage 4a for next batch
11. **IF Human chose Expand**: Go to Expand Step

**Expand Step (expand) - Full Coverage:**

**Stage 4a-Expand: Suggest All Refactorings**
1. **Code** `check_can_start_run()` - Ensures previous runs complete
2. **Code** `start_run(StepType.REFACTOR_SUGGEST)` for expand scope
3. **AI Agent** identifies ALL code smells across all code under test
4. **AI Agent** suggests ALL refactorings with priorities and trade-offs
5. **Code** `record_ai_verification()`
6. **Workflow** auto-approves suggestions (human reviews during 4b-expand)
7. **Code** `record_human_approval(approved=True, auto=True)`
8. **Code** `complete_run()` - Marks suggest-expand COMPLETED

**Stage 4b-Expand: Implement All Refactorings**
1. **Code** `start_run(StepType.REFACTOR_IMPLEMENT)` for expand scope
2. **AI Agent** implements ALL approved refactorings one at a time
3. **Code** `run_tests()` after each refactoring
4. **MANDATORY**: **AI Agent** runs `/bdd-validate` on final state (NO EXCEPTIONS)
5. **MANDATORY**: **AI Agent** fixes ALL violations
6. **Code** `record_ai_verification()`
7. **Workflow** auto-approves expand (no human review needed for expand)
8. **Code** `record_human_approval(approved=True, auto=True)`
9. **Code** `complete_run()` - Marks implement-expand COMPLETED
10. **Stage 4 Complete** - User (optional) commits changes

**Key:** Small batches allow focused review. Expand applies all refactorings safely.

### Repeat Cycle

1. **Code** identifies next unimplemented test in scope
2. **Repeat** Stage 2 through Stage 4 until all tests in scope are implemented
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

### Stage Options

* `--stage scaffold` — Stage 0: Domain scaffolding only
* `--stage signatures` — Stage 1: Only create test signatures  
* `--stage red` — Stage 2: Jump to RED (skip scaffolding/signatures)
* `--stage green` — Stage 3: Jump to GREEN (assumes tests are failing)
* `--stage refactor` — Stage 4: Jump to REFACTOR (assumes tests passing)

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