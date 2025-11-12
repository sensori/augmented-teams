# Clean Code Command Plan

## Command
`/clean-code`

## Purpose
Validate code quality against clean code principles and suggest improvements using static analysis (heuristics) combined with AI-powered deep semantic analysis.

## Target Files
- **Python:** `.py`, `.pyi`
- **JavaScript/TypeScript:** `.js`, `.mjs`, `.ts`, `.tsx`, `.jsx`

## Actions

### generate
**Purpose:** Analyze code and generate violations report

**Steps:**
1. Detect language from file extension (Python vs JavaScript/TypeScript)
2. Load specialized rule file:
   - Python → `clean-code-python-rule.mdc`
   - JavaScript → `clean-code-js-rule.mdc`
3. Extract code structure:
   - Functions (name, line numbers, length, parameter count, nesting depth)
   - Classes (name, line numbers, length, method count)
4. Run heuristics (static analysis pre-checks):
   - Deep nesting detection (>3 levels)
   - Magic numbers
   - Single-letter variables (non-loop)
   - Commented-out code
   - Large functions (>20 lines)
   - Too many parameters (>3)
   - Large classes (>200 lines)
5. Present code + rules + heuristics + structure to AI
6. AI performs deeper semantic analysis beyond heuristics:
   - Single Responsibility violations
   - Side effects mixed with pure logic
   - Poor encapsulation
   - Code duplication patterns
   - Unclear naming
   - Abstraction level mixing
7. Generate violations report (JSON) with:
   - Location (line, function/class name)
   - Severity (critical/important/suggested)
   - Principle violated
   - Specific issue description
   - Actionable suggestion

**Output:** `{file_stem}-clean-code-violations.json`

### validate
**Purpose:** Validate generated violations report for accuracy

**Steps:**
1. Load generated violations report
2. Load rule file for reference
3. Present to AI for validation
4. Check each violation:
   - Is it correctly identified?
   - Does it truly violate the stated principle?
   - Is severity appropriate?
   - Is suggestion actionable?
5. Identify:
   - False positives
   - Incorrect principle attribution
   - Missing context
   - Severity mismatches (too aggressive or too lenient)
6. Generate validation report with corrections needed

**Output:** Validation feedback with corrections list

### correct
**Purpose:** Apply corrections to violations report

**Steps:**
1. Load validated violations + correction suggestions
2. Apply corrections:
   - Remove invalid violations (false positives)
   - Adjust severities as indicated
   - Improve suggestions where needed
   - Ensure correct principle attribution
3. Output final cleaned violations report

**Output:** `{file_stem}-clean-code-violations-final.json`

## Workflow Integration

### Full Workflow
```bash
/clean-code                    # Run all actions: generate → validate → correct
```

### Individual Actions
```bash
/clean-code --action generate  # Generate violations only
/clean-code --action validate  # Validate existing report
/clean-code --action correct   # Apply corrections
```

## Output Files

### Violations Report (JSON)
```json
{
  "file": "path/to/file.py",
  "language": "python",
  "violations": [
    {
      "line": 42,
      "function": "calculate_total",
      "severity": "critical",
      "principle": "1.1 Single Responsibility",
      "issue": "Function both calculates AND persists to database",
      "suggestion": "Extract database persistence to separate function"
    }
  ],
  "summary": {
    "critical": 3,
    "important": 7,
    "suggested": 12,
    "total": 22
  },
  "code_structure": {
    "functions": 15,
    "classes": 3,
    "total_lines": 450
  }
}
```

### Analysis Report (Markdown)
Human-readable markdown report with:
- Summary statistics
- Violations grouped by severity
- Violations grouped by principle
- Code quality score
- Recommendations

## Heuristics (Static Analysis)

The following checks are performed automatically before AI analysis:

1. **Deep Nesting** - Control flow nesting depth
   - Critical: ≥7 levels
   - Important: ≥4 levels
   - Suggested: 3 levels

2. **Magic Numbers** - Unexplained numeric literals (2+ digits)
   - Ignores: version numbers, dates, common patterns

3. **Single-Letter Variables** - Non-loop single-letter names
   - Suggests descriptive names that reveal intent

4. **Commented Code** - Detected code blocks in comments
   - Recommends deletion (it's in git history)

5. **Large Functions** - Function length violations
   - Critical: >50 lines
   - Important: >20 lines

6. **Too Many Parameters** - Parameter count violations
   - Important: >3 parameters
   - Suggests parameter objects or function splitting

7. **Large Classes** - Class length violations
   - Critical: >300 lines
   - Important: >200 lines

## Architecture

### Base Class
Inherits from `CodeAugmentedCommand` (behaviors/common/code_runner.py)

### Language Detection
- File extension-based
- Loads appropriate specialized rule

### Rule Loading
- Base rule: `clean-code-rule.mdc`
- Specialized: `clean-code-python-rule.mdc` or `clean-code-js-rule.mdc`

### Template System
- `clean-code-generate.mdc` - Generation guidance
- `clean-code-validate.mdc` - Validation guidance
- `clean-code-correct.mdc` - Correction guidance

## Usage Examples

### Example 1: Analyze Python file
```bash
/clean-code path/to/module.py
```
Result: Full analysis with violations report

### Example 2: Re-validate existing report
```bash
/clean-code path/to/module.py --action validate
```
Result: Validation feedback on existing violations

### Example 3: JavaScript analysis
```bash
/clean-code src/components/Button.tsx
```
Result: TypeScript/React component analysis with JS-specific rules

## Integration Points

### Code Agent Behavior
- Follows code-agent behavior pattern
- Respects specialized rule pattern
- Uses template-driven AI guidance

### BDD Integration
- Can be used before/after BDD workflow
- Ensures code quality before/after test implementation

### Stories Integration
- Can validate code written during story implementation
- Part of Definition of Done

## Success Criteria

- **Accuracy:** Violations are correctly identified
- **Actionability:** Suggestions are clear and implementable
- **Coverage:** Both heuristics and deep semantic analysis
- **Language-Specific:** Uses appropriate patterns for Python vs JS
- **Non-Intrusive:** Runs without modifying code
- **Iterative:** Validate/correct cycle improves accuracy

## Notes

- **Heuristics First:** Static analysis catches obvious issues fast
- **AI Depth:** Semantic analysis finds deeper architectural issues
- **No Auto-Fix:** Recommendations only, never modifies code
- **Educational:** Teaches clean code principles through examples
- **Specialized Rules:** Language-specific patterns and idioms

