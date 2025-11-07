### Command: `/clean-code-validate`

**Purpose:** Validate code against clean code principles, report violations, and optionally apply automated fixes.

**Usage:**
* `/clean-code-validate` — Validate current file, report issues only
* `/clean-code-validate --fix` — Validate and auto-fix safe issues
* `python behaviors/clean-code/clean-code-runner.py validate <file> --cursor` — Run from command line

**When invoked, this command MUST:**
1. Run: `python behaviors/clean-code/clean-code-runner.py validate <file-path> --cursor [--fix]`
2. Parse the outputted validation prompts by section
3. Validate each chunk against clean code checklists
4. Report violations with line numbers and severity
5. If `--fix` flag: Apply safe automated fixes using search_replace tool
6. Report remaining issues requiring manual review

**Rule Files:**
* `clean-code-rule.mdc` — Framework-agnostic clean code principles
* `clean-code-python-rule.mdc` — Python-specific patterns (for .py files)
* `clean-code-js-rule.mdc` — JavaScript-specific patterns (for .js/.ts files)

**Valid Files** (uses same glob patterns as rules):
* **Python**: `["**/*.py", "**/*.pyi"]`
* **JavaScript/TypeScript**: `["**/*.js", "**/*.mjs", "**/*.ts", "**/*.tsx", "**/*.jsx"]`

**Runner:**
python behaviors/clean-code/clean-code-runner.py validate

---

## Steps

1. **User** invokes `/clean-code-validate` or `/clean-code-validate --fix`

2. **Code** function `detect_language()` — detects Python or JavaScript from file extension, returns language

3. **Code** class `CleanCodeRuleParser.get_checklist(language)` — dynamically parses language-specific rule file, extracts:
   - All 10 section headers (## 1. Functions, ## 2. Naming, etc.)
   - Subsection principles (### 1.1, ### 1.2, etc.)
   - DO/DON'T code examples from each subsection
   - Auto-generates validation checks based on subsection titles and DON'T patterns
   - Returns structured rules dict with cached results

4. **Code** function `extract_functions_from_file(file, language)` — parses file structure:
   - Extracts all functions with line numbers, length, param count, nesting depth
   - Identifies potential violations (e.g., > 20 lines, > 3 params, deep nesting)

5. **Code** function `extract_classes_from_file(file, language)` — parses class structure:
   - Extracts all classes with line numbers, length, method count
   - Identifies god objects (> 300 lines, many methods)

6. **Code** function `perform_static_analysis(file, language)` — runs automated checks:
   - Deep nesting detection
   - Magic number detection
   - Single-letter variable detection
   - Commented-out code detection
   - Large function/class detection
   - Too many parameters detection
   - Returns static violations with line numbers and severity

7. **Code** displays full rule file content for AI context:
   - Outputs complete .mdc file with all 10 sections
   - Shows all DO/DON'T examples
   - Provides principles for each subsection

8. **Code** displays code structure with pre-identified issues:
   - Lists functions with length, params, nesting depth
   - Lists classes with length, method count
   - Shows static violations from automated analysis
   - Highlights which sections to review for each violation

9. **AI Agent** validates code against full rule file:
   - Reviews static violations for accuracy
   - Identifies additional violations missed by static analysis
   - Checks for code smells requiring semantic understanding:
     - Hidden side effects in pure functions
     - Misleading names
     - Improper abstraction levels
     - Missing encapsulation
     - Poor error handling
     - Design principle violations

10. **AI Agent** reports violations with:
    - Line numbers
    - Severity (Critical/Important/Suggested)
    - Principle violated (section reference from rules)
    - Suggested fix with before/after preview

11. **AI Agent** categorizes fixes by safety:
    - **✅ Safe Automatable**: Rename variables, extract constants, add type hints, fix bare except
    - **⚠️ Requires Review**: Extract methods, parameter objects, restructure control flow
    - **❌ Manual**: Split classes/modules, change APIs, introduce patterns

12. **Code** outputs fix application prompt (if --fix flag present)

13. **AI Agent** (if --fix) applies safe automated fixes using search_replace:
    - Replace magic numbers with named constants
    - Rename single-letter variables
    - Add type hints (Python)
    - Fix bare except clauses (Python)
    - Remove commented-out code
    - Remove unused imports

14. **AI Agent** reports final summary:
    - Issues found by severity
    - Fixes applied (if --fix)
    - Remaining issues requiring manual review
    - Before/after code quality score

---

## How Checklist Auto-Generation Works

The `CleanCodeRuleParser` dynamically extracts validation checks from the rule `.mdc` files:

**Example from clean-code-python-rule.mdc:**

```markdown
### 1.3 Clear Parameters

Use parameter objects for complex signatures; avoid boolean flags.

**✅ DO:**
\```python
def connect(opts: ConnectionOptions):
    ...
\```

**❌ DON'T:**
\```python
def export_report(data, is_csv: bool):  # DON'T: Boolean flag parameter
    return to_csv(data) if is_csv else to_json(data)
\```
```

**Auto-Generated Check:**
```
□ Does function use boolean flag parameters?
  Keywords to avoid: bool, boolean, flag, is_, has_
  ❌ DON'T: def export_report(data, is_csv: bool)...
  ✅ DO: def export_csv(data): return to_csv(data)...
```

This ensures the command never gets out of sync with the rules!

---

## Output Format

**Validation Report:**
```
Clean Code Validation Report
=============================

File: src/checkout.py (85 lines)

Critical Issues (3):
  Line 15: Function 'checkout' is too large (45 lines)
    → Principle: §1.2 Functions should be small and focused
    → Suggestion: Extract into smaller functions
    
  Line 22: Magic number 1.13
    → Principle: §2.3 Replace magic numbers with named constants
    → Fix: TAX_RATE = 0.13

Important Issues (5):
  Line 8: Parameter count exceeds 3 (has 5 parameters)
    → Principle: §1.3 Prefer parameter objects
    → Suggestion: Use CheckoutRequest data class

Suggested Improvements (7):
  Line 33: Variable name 'd' is unclear
    → Principle: §2.1 Use intention-revealing names
    → Fix: Rename to 'discount_amount'

Summary:
- Critical: 3
- Important: 5  
- Suggested: 7
- Code Quality Score: 65/100
```

**With --fix Applied:**
```
Clean Code Validation & Fix Report
===================================

File: src/checkout.py (85 lines)

✅ Auto-Applied Fixes (5):
  [Line 22] Replaced magic number 1.13 with TAX_RATE constant
  [Line 33] Renamed 'd' to 'discount_amount'
  [Line 45] Renamed 'f' to 'config_file'
  [Line 58] Removed commented-out code block
  [Line 62] Fixed bare except → except (ValueError, KeyError)

⚠️ Manual Review Needed (5):
  1. [Line 15] Extract checkout() into 6 smaller functions
  2. [Line 8] Introduce CheckoutRequest parameter object
  3. [Line 72] Flatten nested conditionals (4 levels deep)
  4. [Line 120] Split OrderProcessor class (god object)
  5. [Line 200] Extract duplicate calculation logic

Summary:
- Applied: 5 fixes
- Remaining: 5 issues (manual review)
- New Code Quality Score: 78/100 (+13)
```

