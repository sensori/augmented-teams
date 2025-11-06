### Command: `bdd-signature-verify-cmd.md`

**Purpose:** Verify test signatures follow BDD principles (Stage 1 verification)

**Usage:**
* `\bdd-signature-verify` — Verify current signature work
* `python behaviors/bdd/bdd-runner.py workflow <file> signature-verify` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD validation

**When to Run:**
After AI has created "it should..." statements and is ready to lock them in.

**Validation Requirements** (AI must confirm):

**MANDATORY:** Run `/bdd-validate` and report violations

AI should have:
1. Run `/bdd-validate` on test file
2. Reviewed all suspected § 1-5 violations
3. Reported violations to Human with line numbers and severity
4. Fixed violations per Human direction
5. Re-run `/bdd-validate` until 0 violations (or Human accepts remaining)

**What AI Reports:**

```
Validation Summary:

✅ § 1 Business Readable: PASS (or X violations)
✅ § 2 Comprehensive: PENDING (signatures only)
✅ § 3 Context Sharing: PASS (or X violations)  
✅ § 4 All Layers: PENDING (signatures only)
✅ § 5 Front-End: PENDING (signatures only)
✅ Domain Fluency: PASS (from Stage 0)

Total: X violations (or 0 violations - ready for approval)
```

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> signature-verify` — Verify signatures (Stage 1 verification)

**Steps:**
1. **User** invokes command via `\bdd-signature-verify`
2. **AI Agent** runs `\bdd-validate` command on test file
3. **AI Agent** analyzes validation results for § 1 (Business Readable) and § 3 (Context Sharing) violations
4. **AI Agent** reports violations to Human with line numbers and severity
5. **User** reviews violations and provides direction
6. **AI Agent** fixes violations per Human feedback
7. **AI Agent** re-runs `\bdd-validate` until 0 violations or Human accepts remaining
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
After verification:
* `/bdd-workflow-approve` — Human approves, completes Stage 1
* Then ready for `/bdd-red` (Stage 2)


6. **AI Agent** fixes violations per Human feedback
7. **AI Agent** re-runs `\bdd-validate` until 0 violations or Human accepts remaining
8. **Code** function `mark_ai_verified(run_id)` — marks run as 'ai_verified', records timestamp, returns success

**Next Steps:**
After verification:
* `/bdd-workflow-approve` — Human approves, completes Stage 1
* Then ready for `/bdd-red` (Stage 2)

