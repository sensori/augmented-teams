---
execution:
  registry_key: bdd-signature-run
  python_import: behaviors.bdd.bdd_runner.SignatureRunCommand
  cli_runner: behaviors/bdd/bdd_runner.py
  actions:
    generate:
      cli: generate-signature-run
      method: generate
    validate:
      cli: validate-signature-run
      method: validate
    correct:
      cli: correct-signature-run
      method: correct
  working_directory: workspace_root
---

### Command: `/bdd-signature-run`

**Purpose:** Run tests for signature phase to verify test signatures are syntactically correct (tests should fail with "not implemented" or similar). Delegates to main command with explicit run action.

**Usage:**
* `/bdd-signature-run [test-file]` — Run tests for signature phase (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the run action in `/bdd-signature`

