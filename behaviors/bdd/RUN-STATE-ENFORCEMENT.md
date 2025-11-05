# BDD Workflow RUN State Enforcement

## Problem
The BDD workflow previously relied on AI discipline to:
- Remember to run `/bdd-validate` after every step
- Stop and wait for human approval
- Not skip steps

**This doesn't work reliably** - AI can forget or skip steps.

## Solution
**Code-enforced state machine** that blocks progression until requirements met.

## RUN Lifecycle

```
STARTED → AI_VERIFIED → HUMAN_APPROVED → COMPLETED
```

A **RUN** is a single workflow step (e.g., Sample 1, Sample 2, RED batch, etc.)

### State Transitions

1. **STARTED**: Work begins
   - AI creates test signatures or implementation
   - **Cannot proceed until**: AI runs `/bdd-validate`

2. **AI_VERIFIED**: AI verified the work
   - Code records validation results
   - **Cannot proceed until**: Human reviews and approves

3. **HUMAN_APPROVED**: Human approved
   - Human typed "proceed" or approved via command
   - **Cannot proceed until**: Run marked complete

4. **COMPLETED**: Run finished
   - Ready to start next run
   - Previous run state cleared

## Implementation

### Files

1. **`bdd-workflow-run-state.py`** - RUN state machine
   - `BDDRunState` class tracks runs
   - `RunStatus` enum defines lifecycle
   - `StepType` enum defines step types

2. **`bdd-workflow-runner.py`** - Integrated enforcement
   - `check_can_start_run()` - Blocks if previous run incomplete
   - `record_validation_results()` - Records AI verification
   - `wait_for_human_approval()` - Blocks until human approves

### Usage Pattern

```python
from bdd_workflow_run_state import BDDRunState, StepType

# Initialize
run_state = BDDRunState("path/to/test.mjs")

# Check if can start new run
run_state.enforce_can_proceed()  # Raises RuntimeError if blocked

# Start new run
run_id = run_state.start_run(
    StepType.SAMPLE_1,
    context={"describe": "base effect section", "test_count": 7}
)

# ... AI does work ...

# AI MUST run /bdd-validate and record results
run_state.record_ai_verification(
    run_id,
    validation_results={"passed": True, "output": "..."}
)

# Human reviews and approves
run_state.record_human_approval(
    run_id,
    approved=True,
    feedback="Looks good, proceed"
)

# Mark complete
run_state.complete_run(run_id)

# Now can start next run
```

### Error Handling

If you try to start a new run without completing the previous one:

```
❌ CANNOT START NEW RUN
============================================================
Previous run sample_1_20241104_143000 not complete.
Status: ai_verified
Complete or abandon previous run before starting new one.

To fix:
1. If AI hasn't verified: Run /bdd-validate
2. If AI verified: Type 'proceed' to approve
3. If stuck: Call abandon_run() to reset
============================================================
```

## StepTypes

```python
class StepType(Enum):
    SAMPLE_1 = "sample_1"                        # First sample (Phase 0)
    SAMPLE_2 = "sample_2"                        # Second sample (Phase 0)
    EXPAND = "expand"                            # Expand to full scope (Phase 0)
    RED_BATCH = "red_batch"                      # RED phase batch
    GREEN_BATCH = "green_batch"                  # GREEN phase batch
    REFACTOR_SUGGEST = "refactor_suggest"        # REFACTOR suggest
    REFACTOR_IMPLEMENT = "refactor_implement"    # REFACTOR implement
```

## Benefits

✅ **Enforced discipline** - Cannot bypass steps  
✅ **Clear audit trail** - Know exactly what was verified when  
✅ **Human-in-the-loop** - Must explicitly approve  
✅ **AI accountability** - Must run validation before proceeding  
✅ **Error recovery** - Can abandon stuck runs  

## State Files

State stored in `.bdd-workflow/<filename>.run-state.json`:

```json
{
  "runs": [
    {
      "run_id": "sample_1_20241104_143000",
      "step_type": "sample_1",
      "status": "completed",
      "started_at": "2024-11-04T14:30:00",
      "ai_verified_at": "2024-11-04T14:31:00",
      "human_approved_at": "2024-11-04T14:32:00",
      "completed_at": "2024-11-04T14:32:30",
      "validation_results": {
        "passed": true,
        "output": "..."
      },
      "human_feedback": "Looks good"
    }
  ],
  "current_run_id": null,
  "phase": "signatures",
  "scope": "describe"
}
```

## Integration with BDD Workflow

The main `bdd_workflow()` function now:

1. **Checks run state** before starting
2. **Blocks** if previous run incomplete
3. **Returns error** with status summary

```python
# Step 3a: CHECK RUN STATE - Can we proceed?
try:
    check_can_start_run(run_state)
except RuntimeError:
    return {
        "error": "Cannot proceed - previous run not complete",
        "run_status": run_state.get_status_summary()
    }
```

## Commands Updated

- **`bdd-workflow-cmd.md`** - Documents RUN enforcement
- **`bdd-workflow-runner.py`** - Implements enforcement
- **`bdd-workflow-run-state.py`** - New state machine module

## Next Steps

1. Update command runner to use run state
2. Add commands for:
   - `record-validation` - Record AI verification
   - `approve` - Human approval
   - `reject` - Send back for fixes
   - `abandon-run` - Error recovery
3. Integrate with Cursor command interface


