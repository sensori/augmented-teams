---
execution:
  registry_key: bdd-code-run
  python_import: behaviors.bdd.bdd_runner.CodeRunCommand
  cli_runner: behaviors/bdd/bdd_runner.py
  actions:
    generate:
      cli: generate-code-run
      method: generate
    validate:
      cli: validate-code-run
      method: validate
    correct:
      cli: correct-code-run
      method: correct
  working_directory: workspace_root
---

### Command: `/bdd-code-run`

**Purpose:** Run tests for code phase to verify production code passes all tests. Delegates to main command with explicit run action.

**Usage:**
* `/bdd-code-run [test-file]` — Run tests for code phase (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the run action in `/bdd-code`

