### Command: `code-agent-specialization-cmd.md`

**Purpose:** Manage specialized behavior patterns (validate, fix, create base + specialized rules + references)

**Usage:**
* `\specialization validate <feature>` — Validate specialization structure for a specific feature
* `\specialization fix <feature>` — Fix specialization issues automatically
* `\specialization create <feature>` — Scaffold new specialized behavior
* `python behaviors/code-agent/code-agent-runner.py specialization <feature>` — Run from command line

**Rule:**
* `\code-agent-specialization-rule` — Hierarchical specialization patterns for code agent behaviors
* `\code-agent-structure-rule` — Base structure and naming conventions

**Steps:**

1. **User** or **AI Agent** invokes `/code-agent-specialization validate <feature>`
2. **Code** (`validate_hierarchical_behavior(feature)`) loads the feature's configuration file (`<feature>.json` or `behavior.json`)
3. **Code** checks if `isHierarchical` flag is set to `true` (if false/missing, skip hierarchical validation)
4. **Code** runs base structure validation first by calling `Commands.structure("validate", feature_name)` and reports base structure issues
5. **Code** validates the `hierarchy` configuration section:
   - Verify `baseRule` is declared
   - Verify `specializedRules` array exists and contains file names
   - Verify `referenceFiles` array exists and contains file names
6. **Code** validates all declared files exist:
   - Check base rule file exists
   - Check each specialized rule file exists
   - Check each reference file exists
   - Report missing files as errors (prevents misclassification)
7. **Code** validates cross-references:
   - Base rule mentions specialized rules (warning if missing)
   - Each specialized rule references base rule (error if missing)
   - Each specialized rule starts with `**When**` pattern (warning if missing)
8. **Code** validates reference material links:
   - Extract framework from reference file name
   - Find corresponding specialized rule
   - Check specialized rule mentions reference file
   - Report missing links as errors
9. **Code** validates conceptual alignment (optional, advanced):
   - Check principle numbering matches across files
   - Verify same section numbers exist in base and specialized rules
   - Check DO/DON'T example complexity is similar (±3 lines)
10. **Code** outputs a detailed validation report:
    - Summary of base validation results
    - Count of hierarchical issues found
    - Count of warnings
    - List of specific issues and warnings
11. **Code** returns validation results object with base results, hierarchical status, issues, and warnings
12. **Code** exits with error code 1 if issues found (for CI/CD integration)
13. **AI Agent** reviews validation report and presents findings to user

**Integration:**

- Generic validation handles all common hierarchical checks
- Features can create feature-specific validation commands for additional domain-specific checks
- Feature-specific commands should call generic validation first, then add custom checks
- Validation can run automatically via watchers, pre-commit hooks, or CI/CD pipelines
- Results integrate with sync and index processes

