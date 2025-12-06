---
execution:
  registry_key: bdd-test-run
  python_import: behaviors.bdd.bdd_runner.TestRunCommand
  cli_runner: behaviors/bdd/bdd_runner.py
  actions:
    generate:
      cli: generate-test-run
      method: generate
    validate:
      cli: validate-test-run
      method: validate
    correct:
      cli: correct-test-run
      method: correct
  working_directory: workspace_root
---

### Command: `/bdd-test-run`

**[Purpose]:** Run tests for test phase to verify test implementations execute correctly (tests should fail if production code not yet written). Delegates to main command with explicit run action.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 9: Code Implementation Phase (test execution, verify tests pass)
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific examples:
  - Framework-specific test execution commands and directory requirements

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py run [test-file] [framework]` — Run tests for specified test file and framework

**Usage:**
* `/bdd-test-run [test-file]` — Run tests for test phase (AI determines test file from context if not provided)

**Action 1: RUN**
**Steps:**
1. **User** invokes command via `/bdd-test-run [test-file]`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-test-run", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references rule files to understand framework-specific execution:
   - `/bdd-mamba-rule.mdc` for Python/Mamba execution patterns
   - `/bdd-jest-rule.mdc` for JavaScript/Jest execution patterns

4. **Runner** (`BDDWorkflow.run_tests()`) executes tests:
   - **Mamba/Python**: Runs `python -m mamba.cli [test-file]` from test file's directory
   - **Jest/JavaScript**: Runs `npm test -- [test-file]` from project root
   - Captures stdout, stderr, and return code
   - Parses test results (pass/fail counts)

5. **Runner** which displays test execution results:
   - Test output (stdout + stderr)
   - Pass/fail counts
   - Success/failure status
   - Any errors encountered

6. **AI Agent** presents execution results to user:
   - Test results summary
   - Pass/fail counts
   - Note that test failures are expected at this phase if production code not yet written
   - Next steps (fix failing tests, proceed to code implementation phase, re-run tests)

**Framework-Specific Execution:**

**Mamba/Python:**
- Command: `python -m mamba.cli [test-file]`
- Working Directory: Test file's parent directory (ensures proper Python imports)
- Example: `cd behaviors/character && python -m mamba.cli character-behavior.test.py`

**Jest/JavaScript:**
- Command: `npm test -- [test-file]`
- Working Directory: Project root (where package.json is located)
- Example: `npm test -- behaviors/stories/stories_runner_test.js`

**ACTION 2: RUN FEEDBACK**
**Steps:**
1. **User** reviews test execution results:
   - Checks which tests passed/failed
   - Reviews error messages for failing tests
   - Understands that test failures are expected if production code not yet written
   - Verifies test implementations execute correctly (syntax, structure, mocking)

2. **User** proceeds based on results:
   - If tests execute correctly (even if failing due to missing production code): Proceed to code implementation phase (`/bdd-code`)
   - If tests have syntax/structure errors: Fix test implementations and re-run
   - If all tests pass unexpectedly: Verify production code exists and tests are complete

