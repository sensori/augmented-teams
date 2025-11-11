### Command: `/bdd-code`

**[Purpose]:** Implement production code to make tests pass following BDD minimalism principles. This command writes only the code that tests demand - no extra features.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 9: Code Implementation Phase (minimalism, YAGNI, make tests pass, avoid over-engineering, check regressions)
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific examples:
  - Section 8: Code Implementation Phase Examples

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] 3 --no-guard` — Execute Phase 3 (Write Code) via workflow

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-code` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-code-generate`

2. **AI Agent** (using `BDDWorkflow.Phase3.generate()`) determines the test file path (from user input or context)

3. **AI Agent** references rule files to understand how to implement production code:
   - `/bdd-rule.mdc` Section 9 for base code implementation principles (minimalism, YAGNI)
   - `/bdd-mamba-rule.mdc` Section 8 for framework-specific examples

4. **Runner** (`BDDWorkflow.Phase3.generate()`) implements production code:
   - Identifies failing tests (tests calling non-existent production code)
   - Implements minimal code to make tests pass (see Section 9 of base rule)
   - Uses simple data structures before classes (§ 9.3)
   - Avoids adding untested features (§ 9.1)
   - Updates production code files

5. **Runner** displays list of updated files with relative paths

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

2. **AI Agent** references rule files to validate production code:
   - `/bdd-rule.mdc` Section 9 for code implementation principles
   - `/bdd-mamba-rule.mdc` Section 8 for framework-specific patterns

3. **Runner** (`BDDWorkflow.Phase3.validate()`) validates if production code follows the principles:
   - **Primary Check**: Tests pass (run tests and verify)
   - **Secondary Check**: Code minimalism (no extra features per § 9.1, simple structures per § 9.3)
   - **Tertiary Check**: No regressions (§ 9.4 - all tests still pass)
   - Uses heuristics to detect violations

4. **Runner** displays validation report with violations (if any) and test results

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
