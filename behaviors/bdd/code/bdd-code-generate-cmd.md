### Command: `/bdd-code-generate`

**Purpose:** Implement complete, functional production code to make tests pass. Delegates to main command with explicit generate action.

**Usage:**
* `/bdd-code-generate [test-file]` — Implement production code (AI determines test file from context if not provided)

**Steps:**
1. **Code** Execute the generate action in `/bdd-code`

**Implementation Requirements:**
- **Complete and Functional**: Code must be fully implemented, not placeholders or stubs
- **Minimalism**: Simple, straightforward implementation - avoid over-factoring for reuse
- **Test-Driven**: Only implement what tests demand, but implement it completely
- **No Extra Features**: Don't add functionality beyond what tests require
