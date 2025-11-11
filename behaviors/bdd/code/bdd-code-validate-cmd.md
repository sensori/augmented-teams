### Command: `/bdd-code-validate`

**Purpose:** Validate production code by running tests and checking minimalism principles. Delegates to main command with explicit validate action.

**Usage:**
* `/bdd-code-validate [test-file]` — Validate production code (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the validate action in `/bdd-code`
