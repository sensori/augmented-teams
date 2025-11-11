### Command: `/bdd-signature-run`

**Purpose:** Run tests for signature phase to verify test signatures are syntactically correct (tests should fail with "not implemented" or similar). Delegates to main command with explicit run action.

**Usage:**
* `/bdd-signature-run [test-file]` — Run tests for signature phase (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the run action in `/bdd-signature`

