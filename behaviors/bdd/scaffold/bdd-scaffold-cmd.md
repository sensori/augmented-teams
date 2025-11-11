### Command: `/bdd-scaffold`

**[Purpose]:** Generate domain scaffolding (plain English hierarchy) from domain maps following BDD principles. This command ALWAYS creates a plain text file (.txt) with hierarchy structure - NEVER a code file (.py, .js, etc.). The scaffold text file serves as the foundation for test structure generation.

**[Rule]:**
* `/bdd-rule` — Rule file containing BDD principles, specifically:
  - Section 1: Business Readable Language (plain English, domain language, natural sentences)
  - Section 2: Fluency, Hierarchy, and Storytelling (hierarchy patterns, domain map mapping, natural language fluency)
  - Section 7: Principles Especially Important for Scaffolding and Signature Creation (scaffold-specific requirements)

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py execute-scaffold [test-file]` — Execute full workflow (Generate → User Feedback → Validate)
* CLI: `python behaviors/bdd/bdd-runner.py generate-scaffold [test-file]` — Generate scaffold hierarchy only
* CLI: `python behaviors/bdd/bdd-runner.py validate-scaffold [test-file]` — Validate scaffold hierarchy only

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-scaffold` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-scaffold-generate`

2. **AI Agent** (using `BDDScaffoldCommand.generate()`) determines the test file path (from user input or context)

3. **AI Agent** references `/bdd-rule.mdc` Sections 1, 2, and 7 to understand how to generate scaffold hierarchy that follows all BDD principles:
   - Section 1: Use plain English, domain language, natural sentences, NO code syntax
   - Section 2: Preserve domain map hierarchy, use hierarchy patterns (concept lifecycle, state variations, behavioral relationships)
   - Section 7: Plain English only, output format `{test-file-stem}-hierarchy.txt`, temporal progression, complete behaviors

4. **Runner** (`BDDScaffoldCommand.generate()`) generates the scaffold hierarchy:
   - Discovers domain maps AND domain interaction files using `BDDCommand.discover_domain_maps()` to find `*domain-map*.txt`, `*interaction-map*.txt`, and `*domain-interactions*.txt` files in the test file directory
   - Scaffolds entire domain map in one shot (high-level activity, no scoping needed)
   - ALWAYS generates plain text hierarchy file (.txt): `{test-file-stem}.scaffold.txt` or `{test-file-stem}-hierarchy.txt`
   - NEVER generates code files (.py, .js, etc.) - scaffolds are ALWAYS text files
   - Follows domain map → test hierarchy mapping rules (Section 2):
     * Domain Concept → describe block (noun)
     * Domain State → describe block with linking words ("that has been", "that is being")
     * Domain Behavior → it block ("should ...")
     * Domain Sub-Concept → nested describe block (preserve nesting depth)
     * When domain interaction files are present, you can leverage them to enhance:
       - Business Rules → it blocks (each rule becomes a test case)
       - Transformations → function hints for it blocks (transformations tell you what object functions will be)
       - Lookups → behavior descriptions for it blocks (lookup patterns inform what behaviors to test)
   - Preserves domain map hierarchy structure (CRITICAL: DO NOT FLATTEN)
   - When domain interaction files are present, you can leverage them to enhance:
     - Test ordering: Use scenario order to determine test ordering (scenarios provide correct storytelling sequence)
     - Test sequence: Use flow steps to determine test sequence within describe blocks (flow shows order of domain concept interactions)
     - Concept relationships: Use actors to identify concept relationships and co-testing opportunities
   - Uses temporal lifecycle progression (created → played → edited → saved) where applicable
   - Creates complete end-to-end behaviors, not fragmented steps
   - Uses plain English only - NO code syntax (`()`, `=>`, `{}`)

5. **Runner** displays list of generated files with relative paths:
   - `{test-file-stem}.scaffold.txt` or `{test-file-stem}-hierarchy.txt` (ALWAYS a .txt file, NEVER code)

6. **AI Agent** presents generation results to user:
   - Generated hierarchy file path
   - Domain map used (if found)
   - Domain interaction file used (if found)
   - Next step after human feedback (regenerate, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated hierarchy file and adds/edits content:
   - Reviews plain English hierarchy structure
   - Verifies domain map alignment (nesting depth, concepts)
   - Ensures temporal progression follows lifecycle (if applicable)
   - Confirms complete end-to-end behaviors
   - Edits hierarchy if needed to better reflect domain concepts

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/bdd-scaffold` again, or explicit `/bdd-scaffold-validate`)

2. **AI Agent** references `/bdd-rule.mdc` Sections 1, 2, and 7 to validate if scaffold hierarchy follows all BDD principles

3. **Runner** (`BDDScaffoldCommand.validate()`) validates if the scaffold hierarchy follows the principles:
   - **Primary Check**: Domain map alignment (if domain map found):
     * Scaffold nesting depth matches domain map depth
     * Scaffold concepts match domain map concepts
     * Scaffold structure preserves domain map hierarchy
     * No flattening detected
     * When domain interaction files are present: scaffold ordering matches scenario order, scaffold sequence matches flow step order, business rules have corresponding it blocks
   - **Secondary Check**: BDD Section 1 and 7 principles:
     * Plain English only - no code syntax (`()`, `=>`, `{}`) - uses `BDDScaffoldHeuristic` (Section 7)
     * Domain language usage (Section 1)
     * Natural sentence structure (Section 1)
     * Clear subject in every test name (Section 2)
     * Temporal progression follows lifecycle (if applicable) (Section 7)
     * Complete end-to-end behaviors (Section 7)
     * When domain interaction files are present: transformations and lookups inform test descriptions (function hints present)
   - **Fallback**: If domain map not found:
     * Warns user
     * Still validates BDD Section 1 and 7 principles
   - Uses heuristics from `BDDCommand._get_heuristic_map()`:
     * Section 1: `BDDJargonHeuristic` - detects technical jargon
     * Section 7: `BDDScaffoldHeuristic` - detects code syntax, missing subjects, technical function names

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, or proceed if no violations)

**Action 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** proceeds to next phase (signature creation) if validation passes

