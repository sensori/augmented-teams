### Command: `/bdd-validate`

**Purpose:** Validate actual BDD test files against BDD principles (readable language, comprehensive coverage, proper structure, etc.)

**Usage:**
* `/bdd-validate` — Validate currently open test file
* `/bdd-validate <file-path>` — Validate specific test file

**When invoked, this command MUST:**
1. Run: `python behaviors/bdd/validate/bdd-validate-runner.py <file-path> --cursor`
2. Parse the outputted validation prompts
3. Validate each chunk against the provided checklist
4. Report violations with line numbers
5. Suggest fixes using DO examples

**Rule Files:**
* `bdd-rule.mdc` — Framework-agnostic BDD testing principles
* `bdd-jest-rule.mdc` — Jest-specific BDD patterns
* `bdd-mamba-rule.mdc` — Mamba-specific BDD patterns

**Valid Files** (uses same glob patterns as rules):
* **Jest**: `["**/*.test.js", "**/*.spec.js", "**/*.test.ts", "**/*.spec.ts", "**/*.test.jsx", "**/*.spec.jsx", "**/*.test.tsx", "**/*.spec.tsx", "**/*.test.mjs", "**/*.spec.mjs"]`
* **Mamba**: `["**/*_test.py", "**/test_*.py", "**/*_spec.py", "**/spec_*.py", "**/*_test.pyi", "**/test_*.pyi", "**/*_spec.pyi", "**/spec_*.pyi"]`

---

## Steps

1. **User** invokes `/bdd-validate` or `/bdd-validate <file-path>`

2. **Code** function `detect_framework()` — detects Jest or Mamba from file extension, returns framework

3. **Code** function `parse_bdd_rules(framework)` — loads bdd-jest-rule.mdc or bdd-mamba-rule.mdc, extracts 5 section principles and checklists, returns rules dict

4. **Code** function `extract_test_blocks(file)` — parses test file, extracts all describe/it blocks with line numbers, returns blocks array

5. **Code** function `discover_domain_maps(file)` — finds domain-map.txt and domain-interactions.txt in same directory, returns domain terms

6. **Code** displays all 5 section rules as summary:
   ```
   § 1: Business Readable Language
   § 2: Comprehensive and Brief (Tests observable behavior, not internals)
   § 3: Balance Context Sharing (No duplicate setup)
   § 4: Cover All Layers (Focuses on code under test)
   § 5: Unit Tests Front-End (N/A for backend tests)
   ```

7. **Code** for each section §1-§5:
   - Outputs validation prompts in chunks
   - Each prompt includes: block name, line number, mandatory checklist, DO/DON'T examples

8. **AI Agent** for each chunk validates against checklist:
   - □ § 1: Uses nouns, starts with "should", no jargon?
   - □ § 2: **Tests observable behavior (not helpers/mocks)?**
   - □ § 3: No duplicate setup across siblings?
   - □ § 4: **Focuses on code under test (not dependencies)?**
   - □ § 5: Front-end specific (N/A for backend)

9. **AI Agent** reports violations with line numbers and suggested fixes using DO examples from rules

10. **Code** outputs cross-section validation prompt

11. **AI Agent** checks for systemic issues spanning multiple sections

12. **AI Agent** applies fixes using search_replace tool if violations found