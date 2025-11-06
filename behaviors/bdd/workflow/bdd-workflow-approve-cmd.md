### Command: `bdd-workflow-approve-cmd.md`

**Purpose:** Human approval or rejection of AI work after validation.

**Rule:**
* `\bdd-workflow-rule` — Enforces human approval step in workflow

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

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> approve [feedback]` — Approves or rejects AI work after validation

**Steps:**
1. **User** invokes command via `\bdd-approve [feedback]` or `\bdd-reject <reason>`
2. **Code** function `get_current_run_state(file_path)` — loads run state, returns current run details or None
3. **Code** validates run is in 'ai_verified' status (rejects if not verified)
4. **If approving:**
   - **Code** function `approve_run(run_id, feedback)` — marks run as 'completed', records approval timestamp and feedback, returns success
5. **If rejecting:**
   - **Code** function `reject_run(run_id, reason)` — resets status to 'started', clears ai_verified timestamp, records rejection reason, returns success
6. **Code** displays appropriate confirmation and next action message

**Related Commands:**
* `\bdd-workflow` — Start workflow
* `\bdd-validate` — AI validation (must happen before approval)
* `\bdd-status` — Check current status


3. **Code** validates run is in 'ai_verified' status (rejects if not verified)
4. **If approving:**
   - **Code** function `approve_run(run_id, feedback)` — marks run as 'completed', records approval timestamp and feedback, returns success
5. **If rejecting:**
   - **Code** function `reject_run(run_id, reason)` — resets status to 'started', clears ai_verified timestamp, records rejection reason, returns success
6. **Code** displays appropriate confirmation and next action message

**Related Commands:**
* `\bdd-workflow` — Start workflow
* `\bdd-validate` — AI validation (must happen before approval)
* `\bdd-status` — Check current status

