### Command: `bdd-validate-cmd.md`

**Purpose:** Validate actual BDD test files against BDD principles (readable language, comprehensive coverage, proper structure, etc.)

**Usage:**
* `\bdd-validate` — Validate currently open test file against BDD principles
* `\bdd-validate <file-path>` — Validate specific test file
* `python behaviors/bdd/bdd-validate-runner.py <file-path> --no-guard` — Run validation from command line (testing only)

**Rule:**
* `\bdd-rule` — Framework-agnostic BDD testing principles
* `\bdd-jest-rule` — Jest-specific BDD patterns
* `\bdd-mamba-rule` — Mamba-specific BDD patterns

**Valid Files** (uses same glob patterns as rules):
* **Jest**: `["**/*.test.js", "**/*.spec.js", "**/*.test.ts", "**/*.spec.ts", "**/*.test.jsx", "**/*.spec.jsx", "**/*.test.tsx", "**/*.spec.tsx", "**/*.test.mjs", "**/*.spec.mjs"]`
* **Mamba**: `["**/*_test.py", "**/test_*.py", "**/*_spec.py", "**/spec_*.py", "**/*_test.pyi", "**/test_*.pyi", "**/*_spec.pyi", "**/spec_*.pyi"]`
* **Any test file**: Matches glob patterns from `bdd-rule.mdc` (all of the above)

**Implementation:**
* `bdd_validate_test_file()` in `command-runners/bdd-validate-runner.py` — Extracts and presents rule file and test structure
* **AI Agent (in conversation)** reads rule file and validates test against principles

**AI Usage:**
* AI Agent (in conversation) reads full rule file and validates test against BDD principles
* AI Agent compares test chunks against DO/DON'T examples
* AI Agent identifies violations with line numbers and suggests fixes

**Code Usage:**
* Code detects framework (Jest vs Mamba) from file path
* Code loads appropriate rule file (bdd-jest-rule.mdc or bdd-mamba-rule.mdc)
* Code extracts DO/DON'T examples organized by section
* Code parses test file into describe/it structure chunks
* Code performs static checks (naming patterns, structure issues)
* Code presents extracted data to AI Agent

**Division of Labor:**
* **Code** extracts and presents data in focused chunks:
  - Test file structure (describe/it blocks with line numbers)
  - DO/DON'T examples organized by section (1-5)
  - Reference file examples (if `--thorough` mode)
  - Static issues (missing "should", `_private` calls, etc.)
* **AI Agent** (chat in conversation) analyzes the data:
  - Compares test chunks against DO/DON'T examples
  - Identifies BDD principle violations with line numbers
  - Suggests fixes using DO examples as templates
  - Reports findings to user

**Steps:**

1. **User** invokes validation via `\bdd-validate` (validates open file) or `\bdd-validate <file-path>` with optional `--thorough` flag
2. **Code** detects framework from file path patterns (Jest vs Mamba)
3. **Code** loads appropriate specialized rule file (bdd-jest-rule.mdc or bdd-mamba-rule.mdc)
4. **Code** extracts ALL DO/DON'T examples from rule, organized by section (1-5)
5. **Code** parses test file into describe/it structure chunks (to manage token limits for large files)
6. **Code** (if `--thorough`) loads detailed examples from reference file
7. **Code** performs static checks (naming patterns, structure issues)
8. **Code** presents extracted data to AI Agent:
   - Test chunks with line numbers
   - DO/DON'T examples organized by section
   - Reference examples (if thorough mode)
   - Static issues found
9. **MANDATORY: AI Agent MUST read the rule file** (bdd-jest-rule.mdc or bdd-mamba-rule.mdc):
   - Read § 1-5 to get DO/DON'T examples
   - NO EXCEPTIONS - cannot validate without reading rules
10. **MANDATORY: AI Agent MUST compare test code line-by-line against DO/DON'T examples**:
   - Check EVERY describe/it block against examples
   - Identify violations with specific line numbers
   - Reference which BDD principle was violated (§ 1-5)
   - Suggest fixes using DO examples as templates
11. **MANDATORY: AI Agent MUST fix ALL violations before proceeding**:
   - Apply fixes to test file using search_replace
   - Re-run validation to confirm zero violations
   - CANNOT mark validation complete with violations remaining
12. **User** reviews fixed code

**Note on Data Extraction:** The command chunks large test files by `describe` blocks to stay under token limits while preserving context. The AI Agent then analyzes each chunk against BDD principles and reports violations.

**Example Output:**

```
============================================================
BDD Test Validation: UserService.test.js (Jest)
============================================================

❌ Line 5: describe('getUserById', ...) 
   Violation: Uses action verb instead of noun
   Fix: Use "a user" or "user retrieval" instead of "getUserById"
   Reference: bdd-jest-rule.mdc § 1. Business Readable Language

❌ Line 12: it('returns user', ...)
   Violation: Missing "should" prefix
   Fix: Start with "should return user when ID exists"
   Reference: bdd-jest-rule.mdc § 1. Business Readable Language

⚠️  Line 25: expect(service._validateToken).toHaveBeenCalled()
   Warning: Testing private method
   Suggestion: Test observable behavior, not internals
   Reference: bdd-jest-rule.mdc § 2. Comprehensive and Brief

✅ Line 40: Proper describe nesting (broad → specific)
✅ Line 50: Good use of beforeEach for setup
✅ Line 60: Tests normal and failure paths

============================================================
Validation Summary
============================================================
❌ 2 violations found
⚠️  1 warning
✅ 3 principles followed correctly
```

**Integration:**

This command can be integrated into:
- Pre-commit hooks to validate changes
- CI/CD pipelines for automated checking
- Development workflow as a manual check
- Sync process to validate before deployment

