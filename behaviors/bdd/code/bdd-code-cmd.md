---
execution:
  registry_key: bdd-code
  python_import: behaviors.bdd.bdd_runner.CodeCommand
  cli_runner: behaviors/bdd/bdd_runner.py
  actions:
    generate:
      cli: generate-code
      method: generate
    validate:
      cli: validate-code
      method: validate
    correct:
      cli: correct-code
      method: correct
  working_directory: workspace_root
---

### Command: `/bdd-code`

**[Purpose]:** Implement production code to make tests pass following BDD minimalism principles. This command writes complete, functional code that tests demand - no placeholders, no stubs, no extra features. Minimalism means simple and straightforward, not incomplete.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 9: Code Implementation Phase (minimalism, YAGNI, make tests pass, avoid over-engineering, check regressions)
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific examples:
  - Section 8: Code Implementation Phase Examples

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] 3 --no-guard` — Execute Phase 3 (Write Code) via workflow
* CLI: `python behaviors/bdd/bdd-runner.py run [test-file] [framework]` — Run tests after code implementation
* CLI: `python behaviors/bdd/bdd-runner.py correct-code [test-file]` — Correct production code based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-code` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-code-generate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-code", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references rule files to understand how to implement production code:
   - `/bdd-rule.mdc` Section 9 for base code implementation principles (minimalism, YAGNI)
   - `/bdd-mamba-rule.mdc` Section 8 for framework-specific examples

4. **Runner** (`BDDWorkflow.Phase3.generate()`) implements production code:
   - Identifies failing tests (tests calling non-existent production code)
   - Implements complete, functional code to make tests pass (see Section 9 of base rule)
   - **CRITICAL**: Code must be fully functional, not placeholders or stubs
   - Uses simple data structures before classes (§ 9.3) - but still complete and functional
   - Avoids over-factoring for reuse - but implements complete functionality
   - Avoids adding untested features (§ 9.1)
   - Updates production code files

5. **Runner** which displays list of updated files with relative paths

6. **AI Agent** presents generation results to user:
   - Updated production code files
   - Tests that should now pass
   - Next step after human feedback (regenerate, proceed to validation, run tests)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews implemented code and adds/edits content:
   - Reviews minimalism (§ 9.1 - only what tests demand)
   - Verifies simple data structures used (§ 9.3)
   - Confirms no untested features added
   - Runs tests to verify they pass
   - Edits implementations if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/bdd-code` again, or explicit `/bdd-code-validate`)

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-code", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`BDDWorkflow.Phase3.validate()`) validates if production code follows the principles:
   - **Primary Check**: Tests pass (run tests and verify)
   - **Secondary Check**: Code minimalism (no extra features per § 9.1, simple structures per § 9.3)
   - **Tertiary Check**: No regressions (§ 9.4 - all tests still pass)
   - Uses heuristics to detect violations

4. **Runner** which displays validation report with violations (if any) and test results

5. **AI Agent** presents validation results:
   - Test results (pass/fail counts)
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, continue iteration, or workflow complete)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** continues code implementation for remaining failing tests (if not complete)
3. **User** completes workflow if all tests pass and validation passes (refactoring happens through validation at every phase)

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/bdd-code-correct [test-file] [chat-context]` when production code has validation errors or needs updates based on chat context

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-code", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references rule files to understand how to correct production code based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - BDD principles from Section 9 (minimalism, YAGNI) and framework-specific Section 8

4. **AI Agent** corrects the production code:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures code follows BDD principles (minimalism, only what tests demand)
   - Updates production code files directly

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated production code file paths
   - Next steps (re-validate, run tests, workflow complete)

**ACTION 6: RUN**
**Steps:**
1. **User** invokes test execution via `/bdd-run [test-file] [framework]` to run tests after code implementation

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-code", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`BDDWorkflow.run_tests()`) executes tests:
   - **Mamba/Python**: Runs `python -m mamba.cli [test-file]` from test file's directory
   - **Jest/JavaScript**: Runs `npm test -- [test-file]` from project root
   - Captures stdout, stderr, and return code
   - Parses test results (pass/fail counts)

4. **Runner** which displays test execution results:
   - Test output (stdout + stderr)
   - Pass/fail counts
   - Success/failure status

5. **AI Agent** presents execution results to user:
   - Test results summary
   - Pass/fail counts
   - Next steps (fix failing tests, continue code implementation, workflow complete if all tests pass)
