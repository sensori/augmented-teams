# DDD Structure Command Implementation Plan

## Prerequisites: Create Initial Infrastructure

**IMPORTANT**: Before proceeding with implementation, you must first create the initial infrastructure scaffolding:

1. **Generate Initial Infrastructure**:
   - Run `/code-agent-command-generate ddd ddd-structure "Analyze code/text/diagrams to extract domain structure" "Domain map file"` to create the initial command files
   - This will generate the basic command structure files (`ddd-structure-cmd.md`, `ddd-structure-generate-cmd.md`, `ddd-structure-validate-cmd.md`)

2. **Validate Initial Infrastructure**:
   - Run `/code-agent-command-validate ddd ddd-structure` to validate the generated files
   - Fix any validation errors before proceeding

3. **CRITICAL: Follow Test-Driven Development Workflow**:
   - **DO NOT** jump directly to implementing the command files and runners
   - **INSTEAD**, follow the TDD workflow: **Scaffold → Signature → Write Tests → Write Code**
   - The plan below provides context and analysis, but implementation must follow the TDD phases

## AI Analysis Required

### 1. Command Architecture

**Command Classes Needed:**
- `DDDCommand(Command)` - Base command class for DDD commands
- `DDDStructureCommand(DDDCommand)` - Implements domain structure extraction logic
- `CodeAugmentedDDDStructureCommand(CodeAugmentedCommand)` - Wraps DDDStructureCommand with heuristic validation

**Wrapping Pattern:**
`CodeAugmentedDDDStructureCommand → DDDStructureCommand → Command`

### 2. Algorithms and Logic

**Generation Algorithm:**
1. Read source file (code, text, diagram, documentation)
2. Parse content to identify domain concepts
3. Apply §1-10 DDD principles:
   - Extract domain concepts using outcome verbs (§1)
   - Integrate system support under domain concepts (§2)
   - Order by user mental model (§3)
   - Organize domain-first (§4)
   - Focus on functional accomplishment (§5)
   - Maximize integration of related concepts (§6)
   - Use nouns for concepts, verbs for behaviors (§7)
   - Assign behaviors to performing concepts (§8)
   - Avoid noun redundancy (§9)
   - Organize by domain concepts, not file structure (§10)
4. Generate hierarchical text output (domain map format)
5. Save to `<name>-domain-map.txt`

**Heuristic Logic Required:**
- `OutcomeVerbsHeuristic` (§1) - Detects communication verbs (showing, displaying, providing)
- `IntegrationHeuristic` (§2) - Detects separated system support sections
- `OrderingHeuristic` (§3) - Detects code structure ordering instead of user mental model
- `DomainFirstHeuristic` (§4) - Detects system concepts before domain concepts
- `FunctionalScopeHeuristic` (§5) - Detects technical framing instead of functional outcomes
- `MaximizeIntegrationHeuristic` (§6) - Detects artificial separation of related concepts
- `NounsVerbsHeuristic` (§7) - Detects verb-based concept names (Animation Resolution)
- `BehaviorAssignmentHeuristic` (§8) - Detects behaviors on wrong concepts
- `NounRedundancyHeuristic` (§9) - Detects domain name collisions
- `DomainOverFileHeuristic` (§10) - Detects file structure organization

### 3. Command Relationships

**Relationship to other DDD commands:**
- `ddd-structure` creates domain maps
- `ddd-interaction` uses domain maps as input
- Structure command is prerequisite for interaction command

### 4. Implementation Details

**Helper Methods:**
- `_parse_source_content()` - Parse code/text to extract concepts
- `_identify_domains()` - Identify major functional domains
- `_extract_concepts()` - Extract concepts within domains
- `_apply_ordering()` - Apply user mental model ordering
- `_generate_domain_map()` - Create hierarchical text output

**File Structures:**
- Input: Any code/text/diagram file
- Output: `<name>-domain-map.txt` (hierarchical text format)

## Files to Create

### 1. Command Definition Files
- `behaviors/ddd/structure/ddd-structure-cmd.md` - Main command
- `behaviors/ddd/structure/ddd-structure-generate-cmd.md` - Generate delegate
- `behaviors/ddd/structure/ddd-structure-validate-cmd.md` - Validate delegate

### 2. Runner Implementation
- Add to `behaviors/ddd/ddd_runner.py`:
  - `DDDCommand` class (base)
  - `DDDStructureCommand` class (inner command with business logic)
  - `CodeAugmentedDDDStructureCommand` class (wrapper with heuristics)
  - 10 heuristic classes (one per rule section)
  - CLI handlers: execute-structure, generate-structure, validate-structure

### 3. Test Implementation
- `behaviors/ddd/ddd_runner_test.py`:
  - Test signatures for DDDStructureCommand
  - Test generation returns prompts
  - Test validation uses heuristics
  - Test heuristics detect violations
  - Mock file operations only

## Implementation Approach & Best Practices

**Follow BDD and Clean Code principles:**
- Mocking: Only mock file I/O operations, not internal classes
- Base Class Reuse: Maximize reuse of base classes from common_command_runner
- Clean Code: Use parameter objects, decompose large methods, use guard clauses
- BDD Compliance: Follow BDD test structure and naming
- Test Strategy: Test observable behavior, use helpers, avoid duplication

## Implementation Details

### DDDCommand Class Structure (Base)
```python
class DDDCommand(Command):
    def __init__(self, content: Content, base_rule_file_name: str = 'ddd-rule.mdc'):
        self.rule = BaseRule(base_rule_file_name)
        super().__init__(content, self.rule)
```

### DDDStructureCommand Class Structure
```python
class DDDStructureCommand(DDDCommand):
    def __init__(self, source_file_path: str):
        content = Content(file_path=source_file_path)
        super().__init__(content)
        self.source_file_path = source_file_path
    
    def generate(self) -> str:
        # Returns prompts/instructions for AI to analyze and extract domain structure
        return self._get_generation_instructions()
    
    def validate(self) -> str:
        # Returns validation prompts/instructions for AI
        return self._get_validation_instructions()
```

### CodeAugmentedDDDStructureCommand Class Structure
```python
class CodeAugmentedDDDStructureCommand(CodeAugmentedCommand):
    def __init__(self, source_file_path: str):
        inner_command = DDDStructureCommand(source_file_path)
        base_rule = BaseRule('ddd-rule.mdc')
        super().__init__(inner_command, base_rule)
```

### Heuristic Classes (10 total, one per section)
```python
class OutcomeVerbsHeuristic(CodeHeuristic):
    """Detects communication verbs violating §1"""
    def detect_violations(self, content):
        # Scan for "showing", "displaying", "providing", "enabling"
        # Return violations with line numbers
```

## Testing Strategy: Test-Driven Development Workflow

### Phase 0: Domain Scaffold

1. **Create Domain Scaffold**: `behaviors/ddd/docs/ddd_runner.domain.scaffold.txt`
   - Plain English descriptions of what DDDStructureCommand should do
   - Behavioral focus: "should extract domain concepts", "should apply outcome verbs principle"
   - Represents desired behavior before implementation

2. **Validate Scaffold**: Ensure no duplication, proper integration with existing concepts

### Phase 1: Signature

3. **Convert to Signatures**: Convert scaffold to Mamba test syntax in `ddd_runner_test.py`
   - Empty test bodies marked `# BDD: SIGNATURE`
   - Proper Mamba syntax: `with description()`, `with it()`

4. **Validate Signatures**: Run `/bdd-validate` to ensure proper structure

### Phase 2: Write Tests

5. **Implement Test Bodies**: Write full test implementations
   - Mock file operations (Path.exists, Path.read_text, Path.write_text) with `autospec=True`
   - Test observable behavior (prompts returned, domain map generated)
   - DON'T mock internal classes (use real Command, BaseRule instances)
   - Test heuristics detect principle violations
   - Extract duplicate setup to helpers

6. **Validate Tests**: Run `/bdd-validate` and fix violations

### Phase 3: Write Code

7. **Implement Command Classes**: Make tests pass
   - Implement `DDDCommand` base class
   - Implement `DDDStructureCommand` with generation and validation logic
   - Implement `CodeAugmentedDDDStructureCommand` wrapper
   - Implement 10 heuristic classes
   - Add CLI handlers in `main()`

8. **Validate Code**: Run `/clean-code-validate` and `/bdd-validate`, fix violations

## Success Criteria

- ✅ Command generates domain maps following §1-10 principles
- ✅ Validation uses 10 heuristics to detect violations
- ✅ Works standalone via `/ddd-structure`
- ✅ CLI testing successful
- ✅ All tests pass (TDD workflow complete)
- ✅ Heuristics detect principle violations correctly

## Key Insights

1. **No Incremental Support**: Domain analysis is single-pass (analyze entire file/module at once)
2. **2-Action Workflow**: Simpler than BDD (Generate → Validate, no iterative feedback)
3. **Language-Agnostic**: No specializing rules needed (domain analysis applies to all languages)
4. **10 Heuristics**: One per rule section for comprehensive validation
5. **Base Class Reuse**: Extends Command from common_command_runner
6. **Test Observable Behavior**: Test prompts returned and files generated, not internal logic
7. **Mock Only I/O**: Mock file operations, not business logic classes

