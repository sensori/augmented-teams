### Command: `/bdd-signature-correct`

**Purpose:** Correct BDD rules based on signature errors and chat context. Delegates to main command with explicit correct action.

**Usage:**
* `/bdd-signature-correct [test-file] [chat-context]` — Correct BDD rules based on errors (AI determines test file and context if not provided)

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py correct-signature [test-file] [chat-context]` — Correct signatures based on errors and chat context

**Steps:**
1. **Code** Execute the correct action in `/bdd-signature`

