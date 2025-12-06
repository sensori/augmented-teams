### Command: `/bdd-code-correct`

**Purpose:** Correct BDD rules based on production code errors and chat context. Delegates to main command with explicit correct action.

**Usage:**
* `/bdd-code-correct [test-file] [chat-context]` — Correct BDD rules based on errors (AI determines test file and context if not provided)

**Steps:**
1. **Code** Execute the correct action in `/bdd-code`

