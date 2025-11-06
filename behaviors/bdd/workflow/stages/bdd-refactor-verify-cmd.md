### Command: `bdd-refactor-verify-cmd.md`

**Purpose:** Verify REFACTOR phase improvements

**Usage:**
* `\bdd-refactor-verify` — Verify current REFACTOR work
* `python behaviors/bdd/bdd-runner.py workflow <file> refactor-verify` — Run from command line

**Rule:**
`\bdd-jest-rule` or `\bdd-mamba-rule` — Framework-specific BDD validation

**Validation Requirements:**

**MANDATORY:**
1. Run tests - confirm they still PASS
2. Run `/bdd-validate` - report violations
3. Confirm code quality improved

AI should confirm:
1. ✓ All tests still pass after refactoring
2. ✓ No regressions
3. ✓ Ran `/bdd-validate`
4. ✓ Code smells addressed

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> refactor-verify` — Verify REFACTOR improvements (Stage 4 verification)

**Steps:**
1. **User** invokes command via `\bdd-refactor-verify`
2. **AI Agent** runs tests to confirm they still PASS after refactoring
3. **AI Agent** checks for regressions
4. **AI Agent** confirms code quality improvements were made
5. **AI Agent** runs `\bdd-validate` command on test file
6. **AI Agent** reports test results, quality improvements, and violations to Human
7. **User** reviews refactorings and provides direction
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve REFACTOR phase
* Cycle complete!



**Steps:**
1. **User** invokes command via `\bdd-refactor-verify`
2. **AI Agent** runs tests to confirm they still PASS after refactoring
3. **AI Agent** checks for regressions
4. **AI Agent** confirms code quality improvements were made
5. **AI Agent** runs `\bdd-validate` command on test file
6. **AI Agent** reports test results, quality improvements, and violations to Human
7. **User** reviews refactorings and provides direction
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve REFACTOR phase
* Cycle complete!

