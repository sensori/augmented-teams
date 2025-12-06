### Command: `/bdd-signature-generate`

**Purpose:** Generate test signatures (code structure) from scaffolds. Delegates to main command with explicit generate action.

**Usage:**
* `/bdd-signature-generate [test-file]` — Generate test signatures (AI determines test file from context if not provided)

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] 1 --no-guard` — Execute Phase 1 (Build Test Signatures) via workflow

**Steps:**
1. **Code** Execute the generate action in `/bdd-signature`
