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

1. The function loads the feature's configuration file (`<feature>.json` or `code-agent-behavior.json`)
2. The function checks if `isHierarchical` flag is set to `true`
   - If `false` or missing, skip hierarchical validation (not an error, just different pattern)
3. The function runs base structure validation first:
   - Import and call `behavior_structure("validate", feature_name)`
   - Report base structure issues
4. The function validates the `hierarchy` configuration section:
   - Verify `baseRule` is declared
   - Verify `specializedRules` array exists and contains file names
   - Verify `referenceFiles` array exists and contains file names
5. The function validates all declared files exist:
   - Check base rule file exists
   - Check each specialized rule file exists
   - Check each reference file exists
   - Report missing files as errors (prevents misclassification)
6. The function validates cross-references:
   - Base rule mentions specialized rules (warning if missing)
   - Each specialized rule references base rule (error if missing)
   - Each specialized rule starts with `**When**` pattern (warning if missing)
7. The function validates reference material links:
   - Extract framework from reference file name
   - Find corresponding specialized rule
   - Check specialized rule mentions reference file
   - Report missing links as errors
8. The function validates conceptual alignment (optional, advanced):
   - Check principle numbering matches across files
   - Verify same section numbers exist in base and specialized rules
   - Check DO/DON'T example complexity is similar (±3 lines)
9. The function outputs a detailed validation report:
   - Summary of base validation results
   - Count of hierarchical issues found
   - Count of warnings
   - List of specific issues and warnings
10. The function returns validation results object:
    - `base`: Base validation results
    - `hierarchical`: Boolean indicating if feature uses hierarchical pattern
    - `specialized_issues`: Count of hierarchical issues
    - `warnings`: Count of warnings
    - `issues_list`: Detailed issue descriptions
    - `warnings_list`: Detailed warning descriptions
    - `total_issues`: Combined issue count
11. The function exits with error code 1 if issues found (for CI/CD integration)

**Integration:**

- Generic validation handles all common hierarchical checks
- Features can create feature-specific validation commands for additional domain-specific checks
- Feature-specific commands should call generic validation first, then add custom checks
- Validation can run automatically via watchers, pre-commit hooks, or CI/CD pipelines
- Results integrate with sync and index processes

