### Command: `bdd-green-verify-cmd.md`

**Purpose:** Verify GREEN phase implementation

**Usage:**
* `\bdd-green-verify` — Verify current GREEN work
* `python behaviors/bdd/bdd-runner.py workflow <file> green-verify` — Run from command line

**Rule:**
`\bdd-jest-rule` or `\bdd-mamba-rule` — Framework-specific BDD validation

**Validation Requirements:**

**MANDATORY:**
1. Run tests - confirm they PASS
2. Run `/bdd-validate` - report violations
3. Check for regressions in existing tests

AI should confirm:
1. ✓ All tests pass
2. ✓ No regressions in existing tests
3. ✓ Ran `/bdd-validate` 
4. ✓ Reported and fixed violations per Human direction

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> green-verify` — Verify GREEN implementation (Stage 3 verification)

**Steps:**
1. **User** invokes command via `\bdd-green-verify`
2. **AI Agent** runs tests to confirm they all PASS
3. **AI Agent** checks for regressions in existing tests
4. **AI Agent** runs `\bdd-validate` command on test file
5. **AI Agent** reports test results and any violations to Human
6. **User** reviews implementation and provides direction
7. **AI Agent** fixes violations per Human feedback
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve GREEN phase
* Then `/bdd-refactor` — Clean up code



**Steps:**
1. **User** invokes command via `\bdd-green-verify`
2. **AI Agent** runs tests to confirm they all PASS
3. **AI Agent** checks for regressions in existing tests
4. **AI Agent** runs `\bdd-validate` command on test file
5. **AI Agent** reports test results and any violations to Human
6. **User** reviews implementation and provides direction
7. **AI Agent** fixes violations per Human feedback
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve GREEN phase
* Then `/bdd-refactor` — Clean up code

