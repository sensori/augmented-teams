### Command: `bdd-red-verify-cmd.md`

**Purpose:** Verify RED phase tests follow BDD principles

**Usage:**
* `\bdd-red-verify` — Verify current RED work
* `python behaviors/bdd/bdd-runner.py workflow <file> red-verify` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD validation

**Validation Requirements:**

**MANDATORY:** Run `/bdd-validate` and report violations

AI should confirm:
1. ✓ Ran `/bdd-validate` on test file
2. ✓ Reviewed suspected § 3 violations (duplicate code)
3. ✓ Reported violations to Human
4. ✓ Fixed violations per Human direction
5. ✓ Tests FAIL for right reason (code not implemented, not syntax errors)

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> red-verify` — Verify RED tests (Stage 2 verification)

**Steps:**
1. **User** invokes command via `\bdd-red-verify`
2. **AI Agent** runs tests to confirm they FAIL for the right reason (not syntax errors)
3. **AI Agent** runs `\bdd-validate` command on test file
4. **AI Agent** analyzes validation results for § 3 (Context Sharing - duplicate code) violations
5. **AI Agent** reports test status and violations to Human
6. **User** reviews and provides direction
7. **AI Agent** fixes violations per Human feedback
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve RED phase
* Then `/bdd-green` — Implement code


2. **AI Agent** runs tests to confirm they FAIL for the right reason (not syntax errors)
3. **AI Agent** runs `\bdd-validate` command on test file
4. **AI Agent** analyzes validation results for § 3 (Context Sharing - duplicate code) violations
5. **AI Agent** reports test status and violations to Human
6. **User** reviews and provides direction
7. **AI Agent** fixes violations per Human feedback
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
* `/bdd-workflow-approve` — Approve RED phase
* Then `/bdd-green` — Implement code

