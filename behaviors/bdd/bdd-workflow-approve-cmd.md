### Command: `bdd-workflow-approve-cmd.md`

**Purpose:** Human approval or rejection of AI work after validation.

**Rule:**
* `\bdd-workflow-rule` — Enforces human approval step in workflow

**AI Usage:**
* AI Agent waits for human approval before proceeding to next phase
* AI Agent interprets approval/rejection feedback

**Code Usage:**
* Code updates run state to `human_approved` or `started` (if rejected)
* Code records feedback and timestamps
* Code blocks workflow progression until approved

**Usage:**
* `\bdd-approve` — Approve current run and proceed
* `\bdd-approve <feedback>` — Approve with feedback
* `\bdd-reject <reason>` — Reject and send back to AI

**When to Use:**
* After AI has run `/bdd-validate` and work passed
* When reviewing test signatures, implementations, or refactorings
* To provide feedback on AI's work

**Workflow Position:**
```
AI Work → AI Validate → [YOU ARE HERE] → Next Step
                       Human Approve/Reject
```

**Examples:**

Approve with no feedback:
```bash
python behaviors/bdd/bdd-workflow-approve-cmd.py demo/mm3e-animations/mm3e-effects-section.test.mjs
```

Approve with feedback:
```bash
python behaviors/bdd/bdd-workflow-approve-cmd.py test.mjs "Good work, proceed"
```

Reject and request fixes:
```bash
python behaviors/bdd/bdd-workflow-approve-cmd.py test.mjs --reject "Fix test naming to be more behavioral"
```

**What Happens:**

**On Approval:**
1. Records human approval timestamp
2. Records optional feedback
3. Marks run as COMPLETED
4. Unlocks workflow to proceed to next step

**On Rejection:**
1. Records rejection reason
2. Resets run to STARTED status
3. Clears AI verification
4. AI must fix issues and re-validate

**Output Example:**

```
=== Approving Run: sample_1_20241104_143000 ===
Step: sample_1
Status: ai_verified

✅ Run approved and completed
Feedback: Looks good, proceed

🎯 Ready to proceed to next step
```

**Error Cases:**

No active run:
```
❌ No active run to approve
```

Run not AI verified:
```
❌ Cannot approve - run not AI verified
Current status: started
AI must run /bdd-validate first
```

**Implementation:**
* `approve_run(test_file, feedback)` — Approve and complete run
* `reject_run(test_file, feedback)` — Reject and reset to STARTED
* Uses `BDDRunState.record_human_approval()` and `complete_run()`

**Related Commands:**
* `\bdd-workflow` — Start workflow
* `\bdd-validate` — AI validation (must happen before approval)
* `\bdd-status` — Check current status


