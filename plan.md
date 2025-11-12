# Clean Code Behavior Refactoring Plan
_Created: 11/12/2025_

## Goal
Refactor the recovered clean-code runner to follow the modern code-agent behavior pattern with proper command/action structure, specialized rules, and common runner integration.

## Current State
- Recovered `clean-code_runner.RECOVERED.py` with functional validation and refactoring logic
- Has static analysis + AI review prompts
- Uses old pattern (direct CLI with validate/refactor commands)
- Missing specialized rule files

## Target Structure

### 1. Command & Actions
**Command:** `/clean-code`
**Actions:** generate, validate, correct

```
/clean-code                    # Run full workflow (generate → validate → correct)
/clean-code --action generate  # Generate clean code analysis
/clean-code --action validate  # Validate generated analysis against rules
/clean-code --action correct   # Apply corrections based on validation
```

### 2. File Organization (Flat Structure)
```
behaviors/clean-code/
├── behavior.json                          # Behavior metadata
├── clean-code-rule.mdc                    # Base clean code rule (exists)
├── clean-code-python-rule.mdc            # Python-specific rules (recover from git)
├── clean-code-js-rule.mdc                # JS/TS-specific rules (recover from git)
├── clean-code-cmd.md                     # Command plan (create new)
├── clean-code-runner.py                  # Main runner (refactor RECOVERED version)
├── clean-code_runner_test.py            # Tests (create new)
└── templates/
    ├── clean-code-generate.mdc           # Generate action template
    ├── clean-code-validate.mdc           # Validate action template
    └── clean-code-correct.mdc            # Correct action template
```

### 3. Architecture Pattern

#### Runner Structure (following BDD/stories pattern)
```python
# clean-code-runner.py

from behaviors.common.code_runner import CodeAugmentedCommand

class CleanCodeCommand(CodeAugmentedCommand):
    """
    Clean code validation and improvement command.
    
    Actions:
    - generate: Analyze code and generate violations report
    - validate: Validate generated report against rules
    - correct: Apply fixes based on validated violations
    """
    
    def __init__(self):
        super().__init__(
            behavior_name="clean-code",
            command_name="clean-code",
            actions=["generate", "validate", "correct"]
        )
    
    def get_heuristics(self) -> List[Callable]:
        """Static analysis checks as heuristics"""
        return [
            check_deep_nesting,
            check_magic_numbers,
            check_single_letter_vars,
            check_commented_code,
            check_large_functions,
            check_too_many_parameters,
            check_large_classes
        ]
    
    def detect_language(self, file_path: str) -> str:
        """Detect Python vs JavaScript"""
        # ... existing logic
    
    def load_specialized_rule(self, language: str) -> dict:
        """Load language-specific rule file"""
        # ... existing logic
    
    def extract_code_structure(self, file_path: str) -> dict:
        """Extract functions, classes, metrics"""
        # ... existing logic from RECOVERED
```

#### Heuristics (from static analysis)
Convert existing `perform_static_analysis()` checks into individual heuristic functions:
- `check_deep_nesting()` - Detect nesting depth > 3
- `check_magic_numbers()` - Find unexplained numeric literals
- `check_single_letter_vars()` - Find non-loop single-letter variables
- `check_commented_code()` - Detect commented code blocks
- `check_large_functions()` - Functions > 20 lines
- `check_too_many_parameters()` - Functions with > 3 params
- `check_large_classes()` - Classes > 200 lines

Each heuristic returns violations with severity (critical/important/suggested)

### 4. Templates

#### generate template (clean-code-generate.mdc)
```markdown
# Clean Code Analysis Generation

## Context
File: {{file_path}}
Language: {{language}}
Rule: {{rule_file}}

## Code Structure
{{code_structure}}

## Heuristic Violations (Pre-detected)
{{heuristic_violations}}

## Task
Analyze the code against all clean code principles in the rule file.

### For each function and class:
1. Compare against DO/DON'T examples
2. Check for violations of clean code principles
3. Look beyond heuristics for deeper issues:
   - Single Responsibility violations
   - Side effects mixed with logic
   - Poor encapsulation
   - Duplication
   - Unclear naming

### Generate violations report:
```json
{
  "file": "{{file_path}}",
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
  }
}
```
```

#### validate template (clean-code-validate.mdc)
```markdown
# Clean Code Violations Validation

## Context
Generated violations report for: {{file_path}}

## Rule File
{{rule_content}}

## Generated Violations
{{generated_violations}}

## Task
Validate each violation in the generated report:

### Check each violation:
1. Is the violation correctly identified?
2. Does it truly violate the stated principle?
3. Is the severity appropriate?
4. Is the suggestion actionable?

### Look for:
- False positives (not actually violations)
- Incorrect principle attribution
- Missing context
- Overly aggressive or too lenient severity

### Output:
```json
{
  "valid_violations": [...],
  "invalid_violations": [...],
  "corrections_needed": [
    {
      "line": 42,
      "issue": "Severity too high",
      "correction": "Change from critical to important"
    }
  ]
}
```
```

#### correct template (clean-code-correct.mdc)
```markdown
# Clean Code Violations Correction

## Context
Validated violations for: {{file_path}}

## Validated Violations
{{validated_violations}}

## Task
Apply corrections to the violations report based on validation feedback.

### Process:
1. Remove invalid violations
2. Adjust severities as indicated
3. Improve suggestions where needed
4. Ensure all principles are correctly attributed

### Output final validated report:
```json
{
  "file": "{{file_path}}",
  "violations": [...],
  "summary": {...}
}
```
```

### 5. Command Plan (clean-code-cmd.md)

```markdown
# Clean Code Command Plan

## Command
`/clean-code`

## Purpose
Validate code quality against clean code principles and suggest improvements.

## Target Files
- Python: .py, .pyi
- JavaScript/TypeScript: .js, .mjs, .ts, .tsx, .jsx

## Actions

### generate
1. Detect language from file extension
2. Load specialized rule file (clean-code-python-rule.mdc or clean-code-js-rule.mdc)
3. Extract code structure (functions, classes with metrics)
4. Run heuristics (static analysis)
5. Present code + rules + heuristics to AI
6. Generate violations report (JSON)

### validate
1. Load generated violations report
2. Load rule file for reference
3. Present to AI for validation
4. Check each violation for accuracy
5. Generate validation report with corrections

### correct
1. Load validated violations + correction suggestions
2. Apply corrections to violations report
3. Output final clean violations report

## Outputs
- `{file_stem}-clean-code-violations.json` - Final violations report
- `{file_stem}-clean-code-analysis.md` - Human-readable analysis

## Integration
- Uses CodeAugmentedCommand base class
- Follows code-agent behavior pattern
- Respects specialized rule pattern
```

## Implementation Steps

### Phase 1: File Recovery & Setup
1. ✅ Recover `clean-code-python-rule.mdc` from git history
2. ✅ Recover `clean-code-js-rule.mdc` from git history
3. ✅ Create `clean-code-cmd.md` command plan
4. ✅ Create template directory structure

### Phase 2: Templates
5. Create `templates/clean-code-generate.mdc`
6. Create `templates/clean-code-validate.mdc`
7. Create `templates/clean-code-correct.mdc`

### Phase 3: Runner Refactoring
8. Refactor `clean-code_runner.RECOVERED.py` → `clean-code-runner.py`
   - Inherit from `CodeAugmentedCommand`
   - Implement action methods (generate, validate, correct)
   - Convert static analysis to heuristics
   - Keep existing extraction logic (functions, classes, metrics)
   - Update to use template system

### Phase 4: Testing
9. Create `clean-code_runner_test.py`
   - Test language detection
   - Test rule loading (specialized rules)
   - Test code structure extraction
   - Test each heuristic
   - Test full generate/validate/correct workflow

### Phase 5: Integration
10. Update `behavior.json` if needed
11. Ensure command registration works
12. Test end-to-end with `/clean-code` command
13. Verify specialized rules load correctly for Python vs JS

## Key Decisions

1. **Command name:** `/clean-code` (singular command, not /clean-code-validate)
2. **Actions:** generate, validate, correct (standard pattern)
3. **Specialized rules:** Recover from git history, follow specialization pattern
4. **Heuristics:** Convert static analysis checks to individual heuristic functions
5. **Architecture:** Use CodeAugmentedCommand base class from common.code_runner
6. **File structure:** Flat (only one command)
7. **Outputs:** JSON violations report + markdown analysis

## Success Criteria

- [ ] Runner follows CodeAugmentedCommand pattern
- [ ] All three actions implemented (generate, validate, correct)
- [ ] Specialized rules load correctly based on language
- [ ] Heuristics detect violations automatically
- [ ] AI validation improves accuracy beyond heuristics
- [ ] Templates guide AI through each action
- [ ] Tests cover core functionality
- [ ] `/clean-code` command works end-to-end
- [ ] Matches code-agent behavior standards

## Notes
- Keep all the valuable logic from RECOVERED runner (extraction, detection, analysis)
- Static analysis becomes heuristics (pre-validation checks)
- AI validation goes deeper than heuristics (semantic issues)
- Correction step refines the violations report
- Specialized rules essential for language-specific patterns
