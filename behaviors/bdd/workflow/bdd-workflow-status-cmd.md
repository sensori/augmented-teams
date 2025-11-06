### Command: `bdd-workflow-status-cmd.md`

**Purpose:** Check current workflow status and what's needed to proceed.

**Rule:**
* `\bdd-workflow-rule` — Follows BDD workflow state management

**Usage:**
* `\bdd-status` — Show current run status and history

**When to Use:**
* Check if you can start new work
* See what action is needed (AI validate? Human approve?)
* Review recent run history
* Debug stuck workflows

**Output Example:**

```
============================================================
BDD WORKFLOW STATUS
============================================================

File: demo/mm3e-animations/mm3e-effects-section.test.mjs
Total runs: 3
Completed: 2

📍 CURRENT RUN
  ID: sample_1_20241104_143000
  Step: sample_1
  Status: ai_verified
  Started: 2024-11-04T14:30:00
  AI Verified: 2024-11-04T14:31:00

  Validation: ✅ PASSED

⚠️ Can proceed: False
Next action: Human must review and approve before proceeding

📜 RECENT RUNS (last 5):
  ✅ sample_1              | completed       | sample_1_20241104_140000
  ✅ sample_2              | completed       | sample_2_20241104_141000
  🔍 expand                | ai_verified     | expand_20241104_143000
============================================================
```

**Status Icons:**
* ✅ `completed` - Run finished successfully
* 🔍 `ai_verified` - AI validated, waiting for human
* 👍 `human_approved` - Human approved, needs completion
* 🚧 `started` - Work in progress, not validated
* ❌ `abandoned` - Run abandoned/errored

**What You Learn:**
1. **Can proceed?** - Whether you can start new work
2. **Next action** - What's blocking (AI validate? Human approve?)
3. **Current run details** - ID, step type, timestamps
4. **Validation results** - Whether BDD validation passed
5. **Recent history** - Last 5 runs with status

**Examples:**

```bash
# Check status
python behaviors/bdd/bdd-workflow-status-cmd.py demo/mm3e-animations/mm3e-effects-section.test.mjs

# Or use command
\bdd-status
```

**Common Scenarios:**

**No active run (ready to work):**
```
✅ No active run - ready to start new work
✅ Can proceed: True
Next action: No active run, can start new one
```

**AI hasn't validated:**
```
⚠️ Can proceed: False
Next action: AI must verify (run /bdd-validate) before proceeding
```

**Waiting for human approval:**
```
⚠️ Can proceed: False
Next action: Human must review and approve before proceeding
```

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> status` — Displays current workflow state and history

**Steps:**
1. **User** invokes command via `\bdd-status`
2. **Code** function `get_run_state(file_path)` — loads complete run state file, returns {runs: [], current_run_id, phase, scope} or empty state
3. **Code** function `get_current_run(state)` — extracts current run from state using current_run_id, returns run details or None
4. **Code** function `calculate_can_proceed(current_run)` — checks if status is 'completed' or no active run, returns boolean
5. **Code** function `determine_next_action(current_run)` — analyzes status to determine what's blocking, returns action message string
6. **Code** function `format_run_history(runs, limit=5)` — formats last N runs with status icons, returns formatted strings
7. **Code** displays complete status report with current run details, can_proceed flag, next action, and recent history

**Related Commands:**
* `\bdd-workflow` — Start workflow
* `\bdd-approve` — Approve current run
* `\bdd-abandon` — Abandon stuck run


3. **Code** function `get_current_run(state)` — extracts current run from state using current_run_id, returns run details or None
4. **Code** function `calculate_can_proceed(current_run)` — checks if status is 'completed' or no active run, returns boolean
5. **Code** function `determine_next_action(current_run)` — analyzes status to determine what's blocking, returns action message string
6. **Code** function `format_run_history(runs, limit=5)` — formats last N runs with status icons, returns formatted strings
7. **Code** displays complete status report with current run details, can_proceed flag, next action, and recent history

**Related Commands:**
* `\bdd-workflow` — Start workflow
* `\bdd-approve` — Approve current run
* `\bdd-abandon` — Abandon stuck run

