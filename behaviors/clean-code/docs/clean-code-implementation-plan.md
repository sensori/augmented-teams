# Clean-Code Command Implementation Plan

## Overview

Implement the `clean-code` command using the new code-agent structure with plan, generate, and validate actions. This is a complete command that generates clean code - planning the creation, generating the code, and validating it follows clean code principles.

## Files to Create/Modify

### 1. Create Command Files at Feature Root

**Location:** `behaviors/clean-code/`

Since this is a single-command feature, command files go at feature root (no subdirectory):
- `clean-code-cmd.md` - Main command with plan, generate, validate actions
- `clean-code-plan-cmd.md` - Delegates to plan action (generates implementation plan for applying clean code to a context)
- `clean-code-generate-cmd.md` - Delegates to generate action (performs the  code generation)
- `clean-code-validate-cmd.md` - Delegates to validate action 
### 2. Update Runner Implementation

**File:** `behaviors/clean-code/clean-code_runner.py`

Currently has minimal boilerplate (22 lines). Needs to be expanded with:

**Add Classes:**
- `CommandConfig` - Dataclass for parameters (file_path, language)
- `CleanCodeCommand(CodeAgentCommand)` - Inner command class with business logic
  - `plan()` - Plans creation of clean code based on context, saves plan to `docs/{name}-clean-code-plan.md`
  - `generate()` - Generates clean code (new or updates existing) according to context
  - `validate()` - Validates clean code using violations against clean code principles
  - Helper methods from archive: `detect_language()`, `load_rule_file()`, `perform_static_analysis()`, `CleanCodeRuleParser`
- `CodeAugmentedCleanCodeCommand(CodeAugmentedCommand)` - Outer wrapper for CLI integration
  - `handle_cli()` - Parse arguments (file_path, language)

**Port Logic from Archive:**
From `z_archive/clean-code/clean-code-runner.py`:
- `CleanCodeRuleParser` class (lines 78-180) - Parses rule files into checklists
- `detect_language()` function (lines 28-40) - Detects Python/JavaScript
- `load_rule_file()` function (lines 47-71) - Loads language-specific rules
- Static analysis functions for violations detection


**Key Adaptations:**
- Use `Content(file_path=...)` pattern from common_command_runner
- Replace print statements with structured return from generate()
- Support both Python and JavaScript via specialized rules
- Add plan() method for generating implementation roadmap

### 3. Create Main Command File

**File:** `behaviors/clean-code/clean-code-validate-cmd.md`

Structure based on archive `clean-code-validate-cmd.md` but adapted to include plan action:

**Sections:**
- Purpose: Validate code against clean code principles
- Rule reference: `clean-code-rule.mdc`
- Runner: CLI commands for plan/execute/generate/validate
- Action 0 PLAN: Generate implementation plan for applying clean code to context
- Action 1 GENERATE: Run validation, detect violations, output report
- Action 2 GENERATE FEEDBACK: User reviews violations
- Action 3 VALIDATE: Verify validation ran correctly
- Action 4 VALIDATE FEEDBACK: User decides to fix or iterate

**Key Content from Archive:**
- Steps 1-14 from archive describe the validation workflow
- Rule file references (base + specialized)
- Output format specifications
- --fix flag behavior

### 4. Create Delegate Command Files

**File:** `behaviors/clean-code/clean-code-validate-plan-cmd.md`

Simple delegate that invokes the plan action of main command to generate implementation roadmap.

**File:** `behaviors/clean-code/clean-code-validate-generate-cmd.md`

Simple delegate that invokes the generate action of main command.

**File:** `behaviors/clean-code/clean-code-validate-validate-cmd.md`

Simple delegate that invokes the validate action of main command.

### 5. Create Specialized Rules

**This feature uses specialized rules extending the base rule for Python and JavaScript.**

**Files to create:**
- `behaviors/clean-code/rules/clean-code-python-rule.mdc` - Python-specific patterns
- `behaviors/clean-code/rules/clean-code-js-rule.mdc` - JavaScript-specific patterns
- `behaviors/clean-code/rules/clean-code-python-rule.py` - Custom rule class (if needed for complex validation logic)
- `behaviors/clean-code/rules/clean-code-js-rule.py` - Custom rule class (if needed)

**Requirements per `/code-agent-rule-cmd`:**
- Use `specialized_rule_template.mdc` template
- Reference base rule (`clean-code-rule.mdc`) directly (no specializing rule for clean-code)
- Include framework-specific globs in frontmatter:
  - Python: `["**/*.py", "**/*.pyi"]`
  - JavaScript: `["**/*.js", "**/*.mjs", "**/*.ts", "**/*.tsx", "**/*.jsx"]`
- Include framework-specific code examples for each principle
- Each principle needs **heuristics** for automated validation
- May need custom rule class extending `SpecializedRule` if complex validation logic required

**Creating Specialized Rules (Step-by-Step):**

**Step 5.1: Generate rule files using code-agent-rule command**

Run `/code-agent-rule` for each specialized rule:
```bash
# Python specialized rule
python behaviors/code-agent/code_agent_runner.py generate-rule clean-code clean-code-python "Python-specific clean code patterns" specialized clean-code-rule

# JavaScript specialized rule  
python behaviors/code-agent/code_agent_runner.py generate-rule clean-code clean-code-js "JavaScript-specific clean code patterns" specialized clean-code-rule
```

This creates template files at:
- `behaviors/clean-code/rules/clean-code-python-rule.mdc`
- `behaviors/clean-code/rules/clean-code-js-rule.mdc`

**Step 5.2: Populate specialized rules with content from archive**

Copy content from archive and adapt:
- Source: `z_archive/clean-code/clean-code-python-rule.mdc`
- Source: `z_archive/clean-code/clean-code-js-rule.mdc`
- Ensure each rule follows `specialized_rule_template.mdc` structure
- Keep all 10 principle sections (Functions, Naming, Code Structure, Error Handling, State Management, Classes, Comments, Formatting, Testing, Boundaries)

**Step 5.3: Add code examples to EACH principle**

For each of the 10 principles and their subsections:
- **[DO]** bullet points + code block with clean example
- **[DON'T]** bullet points + code block with violation example
- Source examples: Use code-agent codebase for Python patterns (clean, well-structured code)
- Convert: Translate Python examples to JavaScript for JS rule

**Step 5.4: Add heuristics to EACH principle**

For each principle subsection, add **Heuristics** section:
```markdown
**Heuristics:**
- Function exceeds 20 lines
- Parameter count > 3
- Nesting depth > 3
- Contains magic numbers
```

These heuristics are used by `CleanCodeRuleParser` to automate violation detection.

**Step 5.5: Create custom rule classes (if needed)**

If complex validation logic required beyond static analysis:
```python
# behaviors/clean-code/rules/clean-code-python-rule.py
from common_command_runner import SpecializedRule

class CleanCodePythonRule(SpecializedRule):
    """Custom validation logic for Python clean code"""
    
    def validate_custom(self, code: str) -> List[str]:
        # Custom validation logic specific to Python
        violations = []
        # ... custom checks ...
        return violations
```

**Example Structure per Principle (from specialized rule):**
```markdown
### 1.1 Single Responsibility
Functions should do one thing and do it well.

**[DO]:**
- Keep functions focused on a single task
- Extract multiple concerns into separate functions

```python
def calculate_total(items):
    return sum(item.price for item in items)
```

**[DON'T]:**
- Mix business logic with side effects

```python
def calculate_and_save(items, db):  # DON'T: Multiple responsibilities
    total = sum(item.price for item in items)
    db.save(total)  # Side effect mixed with calculation
    return total
```

**Heuristics:**
- Function does I/O operations (db, file, network)
- Function both calculates and persists data
```

### 6. Update Feature Rule

**File:** `behaviors/clean-code/clean-code-rule.mdc`

Update the **Executing Commands** section (currently line 17) to replace:
```
* `\clean-code-validate` — Validate code quality and optionally apply automated fixes
```

With proper command reference including plan action.

Also update **Commands** section (line 455) with detailed command description.

## Detailed Implementation

### Step 1: Create Main Command File

**File:** `behaviors/clean-code/clean-code-cmd.md`

**Structure:**
```markdown
### Command: `/clean-code`

**[Purpose]:** Generate clean code (new or refactored) following clean code principles

**[Rule]:**
* `clean-code-rule.mdc` — Framework-agnostic clean code principles

**Runner:**
* CLI: `python behaviors/clean-code/clean-code_runner.py execute [requirements]`
* CLI: `python behaviors/clean-code/clean-code_runner.py plan [requirements]`
* CLI: `python behaviors/clean-code/clean-code_runner.py generate [requirements]`
* CLI: `python behaviors/clean-code/clean-code_runner.py validate [file-path]`

**Action 0: PLAN**
**Steps:**
1. **User** invokes plan via `/clean-code-plan [context]`
2. **AI Agent** determines context from user input
3. **Runner** (`CleanCodeCommand.plan()`) plans creation of clean code:
   - Determines what clean code to create based on context
   - Loads appropriate rule file for language
   - Parses rule file into principles checklist
   - Plans code structure following clean code principles
4. **Runner** saves plan to `behaviors/clean-code/docs/{name}-clean-code-plan.md`
5. **AI Agent** presents plan to user

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/clean-code [context]` or `/clean-code-generate`
2. **AI Agent** understands context (new code or update existing)
3. **Runner** (`CleanCodeCommand.generate()`) outputs context and clean code principles
4. **AI Agent** generates clean code according to context:
   - Creates or updates code following all clean code principles
   - Uses intention-revealing names
   - Keeps functions small and focused
   - Proper abstraction levels
   - No code smells
5. **AI Agent** writes generated clean code to files

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated clean code

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/clean-code-validate [file-path]`
2. **Runner** (`CleanCodeCommand.validate()`) validates the clean code:
   - Detects language from file extension
   - Loads appropriate specialized rule file (Python/JavaScript)
   - Performs static analysis
   - Checks code against clean code principles
3. **Runner** identifies violations
4. **AI Agent** presents validation results: violations found, suggested improvements

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results
2. **User** may iterate (regenerate/validate) to improve code quality
```

### Step 2: Create Delegate Command Files

**File:** `behaviors/clean-code/clean-code-plan-cmd.md`
```markdown
### Command: `/clean-code-plan`

**Purpose:** Generate implementation plan for applying clean code. Delegates to main command with explicit plan action.

**Usage:**
* `/clean-code-plan [context]` — Plan creation of clean code based on context

**Steps:**
1. **Code** Execute the plan action in `/clean-code`
```

**File:** `behaviors/clean-code/clean-code-generate-cmd.md`
```markdown
### Command: `/clean-code-generate`

**Purpose:** Generate clean code. Delegates to main command with explicit generate action.

**Usage:**
* `/clean-code-generate [context]` — Generate clean code according to context

**Steps:**
1. **Code** Execute the generate action in `/clean-code`
```

**File:** `behaviors/clean-code/clean-code-validate-cmd.md`
```markdown
### Command: `/clean-code-validate`

**Purpose:** Validate clean code. Delegates to main command with explicit validate action.

**Usage:**
* `/clean-code-validate [file-path]` — Validate clean code using violations

**Steps:**
1. **Code** Execute the validate action in `/clean-code`
```

### Step 3: Implement Runner Classes

**File:** `behaviors/clean-code/clean-code_runner.py`

**Implementation Order:**

1. **Import statements:**
```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
import sys
import re

# Import from common_command_runner
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_command_runner import (
    Command, Content, BaseRule, 
    CodeAugmentedCommand
)
```

2. **CommandConfig dataclass:**
```python
@dataclass
class CommandConfig:
    file_path: Optional[str] = None
    language: Optional[str] = None
```

3. **Port helper functions from archive:**
   - `detect_language(file_path: str) -> Optional[str]`
   - `load_rule_file(language: str) -> Optional[Dict[str, Any]]`

4. **Port CleanCodeRuleParser class from archive** (lines 78-180)
   - Keep all parsing logic intact
   - Update paths to work with new structure

5. **Implement CleanCodeCommand class:**
```python
class CleanCodeCommand(Command):
    def __init__(self, file_path: Optional[str] = None, language: Optional[str] = None):
        config = CommandConfig(file_path, language)
        rule_name = "clean-code-rule.mdc"
        base_rule = BaseRule(rule_name)
        content = Content(file_path=file_path or "")
        
        generate_instructions = "Validate code against clean code principles..."
        validate_instructions = "Verify validation results..."
        
        super().__init__(content, base_rule, validate_instructions, generate_instructions)
        
        self.file_path = file_path
        self.language = language or detect_language(file_path) if file_path else None
        self.parser = CleanCodeRuleParser()
    
    def plan(self) -> str:
        """Generate implementation plan for applying clean code principles"""
        # Analyze file
        # Generate plan content
        # Save to docs/{filename}-clean-code-plan.md
        # Return plan
        pass
    
    def generate(self) -> str:
        """Generate clean code according to context"""
        # Load rule file and parse into checklist
        # Output context and clean code principles
        # AI generates clean code (new or updates existing)
        return super().generate()
    
    def validate(self) -> str:
        """Validate clean code using violations"""
        # Detect language from file extension
        # Load appropriate specialized rule file (python/js)
        # Parse rule file into validation checklist
        # Perform static analysis
        # Check code against clean code principles
        # Report violations
        return super().validate()
```

6. **Implement CodeAugmentedCleanCodeCommand wrapper:**
```python
class CodeAugmentedCleanCodeCommand(CodeAugmentedCommand):
    def __init__(self, file_path: Optional[str] = None, language: Optional[str] = None):
        base_rule = BaseRule("clean-code-rule.mdc")
        clean_code_command = CleanCodeCommand(file_path, language)
        super().__init__(clean_code_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        file_path = args[0] if len(args) > 0 else None
        language = args[1] if len(args) > 1 else None
        
        command = cls(file_path, language)
        
        if action == "execute":
            command.execute()
        elif action == "plan":
            command.plan()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()
```

7. **Add CLI entry point:**
```python
def main():
    if len(sys.argv) < 2:
        print("Usage: python clean-code_runner.py <action> [args]")
        sys.exit(1)
    
    action = sys.argv[1]
    args = sys.argv[2:]
    
    command_handlers = {
        "execute": lambda a: CodeAugmentedCleanCodeCommand.handle_cli("execute", a),
        "plan": lambda a: CodeAugmentedCleanCodeCommand.handle_cli("plan", a),
        "generate": lambda a: CodeAugmentedCleanCodeCommand.handle_cli("generate", a),
        "validate": lambda a: CodeAugmentedCleanCodeCommand.handle_cli("validate", a),
    }
    
    handler = command_handlers.get(action)
    if handler:
        handler(args)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 4: Update Rule File

**File:** `behaviors/clean-code/clean-code-rule.mdc`

Update line 17:
```markdown
**Executing Commands:**
* `\clean-code` — Generate clean code following clean code principles
* `\clean-code-plan` — Plan creation of clean code based on context
* `\clean-code-validate` — Validate clean code using violations
```

Update lines 455-458:
```markdown
## Commands

* `/clean-code` — Generate clean code following clean code principles
  - `/clean-code-plan` — Plan creation of clean code based on context
  - `/clean-code-generate` — Generate clean code according to context
  - `/clean-code-validate` — Validate clean code using violations
```

## Implementation Sequence

**FOLLOW BDD/TDD APPROACH: Red → Green → Refactor**

### Phase 1: RED (Write Failing Tests)

1. **Create test file:** `behaviors/clean-code/clean_code_runner_test.py`
   - Write tests for CleanCodeCommand.plan()
   - Write tests for CleanCodeCommand.generate()
   - Write tests for CleanCodeCommand.validate()
   - Write tests for helper functions (detect_language, load_rule_file, etc.)
   - Write tests for CleanCodeRuleParser
   - **All tests should FAIL initially** (code not implemented yet)

2. **Define test expectations:**
   - Mock specialized rules with example content
   - Mock file I/O operations
   - Assert expected outputs for plan/generate/validate
   - Define what "passing validation" looks like

### Phase 2: GREEN (Implement Minimal Code to Pass Tests)

3. **Create specialized rules FIRST (CRITICAL):**
   - Step 5.1: Run `/code-agent-rule` to generate templates
   - Step 5.2: Populate from archive (copy/adapt content)
   - Step 5.3: Add code examples to ALL 10 principles (DO/DON'T with code blocks)
   - Step 5.4: Add heuristics to ALL principles for automated validation
   - Step 5.5: Create custom rule classes if needed (`.py` files extending `SpecializedRule`)

4. Create main command file `clean-code-cmd.md` at feature root

5. Create three delegate command files (plan, generate, validate)

6. Expand runner `clean-code_runner.py` (minimal implementation to pass tests):
   - Add imports
   - Add CommandConfig
   - Port helper functions from archive
   - Port CleanCodeRuleParser class (reads specialized rules, extracts examples and heuristics)
   - Implement CleanCodeCommand class (minimal to pass tests)
   - Implement CodeAugmentedCleanCodeCommand wrapper
   - Add CLI entry point

7. Update base rule file `clean-code-rule.mdc` with command references

8. **Run tests - should PASS:**
   ```bash
   python behaviors/clean-code/clean_code_runner_test.py
   ```

### Phase 3: REFACTOR (Improve Code Quality)

9. **Refactor runner implementation:**
   - Extract complex methods into smaller functions
   - Improve naming and clarity
   - Add error handling
   - Optimize performance
   - Add docstrings
   - **Re-run tests after each refactoring** to ensure nothing breaks

10. **Integration test:**
    ```bash
    python behaviors/clean-code/clean-code_runner.py plan "Create a user authentication module"
    ```

## Key Design Decisions

**File Organization:**
- No subdirectory for single-command feature - files at feature root
- Follow naming pattern: `{feature-name}-{command-name}-cmd.md`

**Command Structure:**
- Plan action (Action 0) plans creation of clean code
- Generate action (Action 1) generates clean code
- Validate action (Action 3) validates clean code using violations

**Plan Action Purpose:**
- Plans creation of clean code based on context
- Identifies which clean code principles to apply
- Designs code structure
- **Saves plan to:** `behaviors/clean-code/docs/{name}-clean-code-plan.md`
- Returns plan content for AI to present to user

**Specialized Rules:**
- This command uses specialized rules (not just base rule)
- Two specialized rules: `clean-code-python-rule.mdc` and `clean-code-js-rule.mdc`
- Each specialized rule extends base rule with:
  - Framework-specific globs
  - Framework-specific code examples (DO/DON'T with actual code)
  - Framework-specific heuristics for automated validation
- **Must create specialized rules BEFORE implementing command**

**Language Detection:**
- Auto-detect from file extension
- Load appropriate specialized rule (python/js)
- Specialized rules contain examples and heuristics for validation

**Rule Integration:**
- Command loads specialized rules (not base rule directly)
- Parser extracts DO/DON'T code examples from specialized rules
- Parser extracts heuristics from specialized rules for automated validation
- Static analysis uses heuristics to check code

**Examples Source:**
- Use code-agent codebase as source for clean Python examples
- Convert Python examples to JavaScript for JS specialized rule
- Examples should demonstrate real clean code patterns from the codebase

