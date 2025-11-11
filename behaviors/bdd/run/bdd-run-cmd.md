### Command: `/bdd-run`

**[Purpose]:** Run tests using framework-specific test runners with proper directory context. This command executes tests for any BDD phase (signature, test, code), ensuring tests run from the correct directory with framework-appropriate commands.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 9: Code Implementation Phase (test execution, verify tests pass)
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific examples:
  - Framework-specific test execution commands and directory requirements

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py run [test-file] [framework]` — Run tests for specified test file and framework

**Action 1: RUN**
**Steps:**
1. **User** invokes command via `/bdd-run [test-file] [framework]` or phase-specific commands (`/bdd-signature-run`, `/bdd-test-run`, `/bdd-code-run`)

2. **AI Agent** (using `BDDWorkflow.run_tests()`) determines:
   - Test file path (from user input or context)
   - Framework (from user input, or auto-detect from test file)
   - Working directory (test file's parent directory for proper imports and context)

3. **AI Agent** references rule files to understand framework-specific execution:
   - `/bdd-mamba-rule.mdc` for Python/Mamba execution patterns
   - `/bdd-jest-rule.mdc` for JavaScript/Jest execution patterns

4. **Runner** (`BDDWorkflow.run_tests()`) executes tests:
   - **Mamba/Python**: Runs `python -m mamba.cli [test-file]` from test file's directory
   - **Jest/JavaScript**: Runs `npm test -- [test-file]` from project root
   - Captures stdout, stderr, and return code
   - Parses test results (pass/fail counts)

5. **Runner** displays test execution results:
   - Test output (stdout + stderr)
   - Pass/fail counts
   - Success/failure status
   - Any errors encountered

6. **AI Agent** presents execution results to user:
   - Test results summary
   - Pass/fail counts
   - Next steps (fix failing tests, proceed to next phase, re-run tests)

**Framework-Specific Execution:**

**Mamba/Python:**
- Command: `python -m mamba.cli [test-file]`
- Working Directory: Test file's parent directory (ensures proper Python imports)
- Example: `cd behaviors/stories && python -m mamba.cli stories_runner_test.py`

**Jest/JavaScript:**
- Command: `npm test -- [test-file]`
- Working Directory: Project root (where package.json is located)
- Example: `npm test -- behaviors/stories/stories_runner_test.js`

**ACTION 2: RUN FEEDBACK**
**Steps:**
1. **User** reviews test execution results:
   - Checks which tests passed/failed
   - Reviews error messages for failing tests
   - Fixes failing tests or production code as needed
   - Re-runs tests to verify fixes

2. **User** proceeds based on results:
   - If all tests pass: Continue to next phase or complete workflow
   - If tests fail: Fix issues and re-run, or proceed to code implementation phase


