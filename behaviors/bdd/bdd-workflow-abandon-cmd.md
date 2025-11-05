### Command: `bdd-workflow-abandon-cmd.md`

**Purpose:** Abandon a stuck or errored run to allow starting fresh.

**Rule:**
* `\bdd-workflow-rule` — Allows resetting workflow when stuck

**AI Usage:**
* AI Agent determines when a run should be abandoned (errors, wrong phase, etc.)
* AI Agent provides reason for abandonment

**Code Usage:**
* Code marks current run as `abandoned`
* Code records abandonment reason and timestamp
* Code allows new run to be started

**Usage:**
* `\bdd-abandon <reason>` — Abandon current run with reason

**When to Use:**
* Run is stuck in wrong state
* Started wrong phase or step
* Validation failed and need to start over
* Error occurred and can't recover

**⚠️ Warning:** This abandons current work. Use only when necessary.

**Examples:**

```bash
# Abandon with reason
python behaviors/bdd/bdd-workflow-abandon-cmd.py test.mjs "Started wrong phase"

# Or use command
\bdd-abandon "Need to restart from scratch"
```

**What Happens:**

1. Shows current run details
2. Asks for confirmation
3. Marks run as `abandoned`
4. Records reason in audit trail
5. Clears current_run_id
6. Allows starting fresh

**Output Example:**

```
=== Abandoning Run: sample_1_20241104_143000 ===
Step: sample_1
Status: ai_verified
Reason: Started wrong phase

⚠️  This will abandon the current run and allow starting fresh.
Continue? (y/n): y

✅ Run abandoned
Ready to start new run
```

**After Abandoning:**

The run is marked `abandoned` in history but work is NOT deleted:
- Test file remains unchanged
- You can review what was done
- Audit trail preserved
- Can start new run

**Check Status After:**

```bash
python behaviors/bdd/bdd-workflow-status-cmd.py test.mjs
```

You should see:
```
✅ No active run - ready to start new work
✅ Can proceed: True
```

**Common Reasons to Abandon:**

* `"Started wrong phase"` - Jumped to wrong step
* `"Validation stuck"` - Can't get validation to pass
* `"Need to refactor approach"` - Want to try different approach
* `"Scope changed"` - Requirements changed mid-run
* `"Testing different strategy"` - Experimenting

**Alternative: Reject Instead**

If AI work just needs fixes (not complete restart):
```bash
\bdd-reject "Fix test naming to be more behavioral"
```

Rejection sends work back to AI but keeps run active.

**Implementation:**
* `abandon_run(test_file, reason)` — Abandon with confirmation
* Uses `BDDRunState.abandon_run()`
* Requires explicit confirmation
* Records in audit trail

**Related Commands:**
* `\bdd-status` — Check if stuck
* `\bdd-reject` — Send back for fixes (less drastic)
* `\bdd-workflow` — Start new run after abandoning

