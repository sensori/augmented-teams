### Command: `/bdd-test-run`

**Purpose:** Run tests for test phase to verify test implementations execute correctly (tests should fail if production code not yet written). Delegates to main command with explicit run action.

**Usage:**
* `/bdd-test-run [test-file]` — Run tests for test phase (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the run action in `/bdd-test`

