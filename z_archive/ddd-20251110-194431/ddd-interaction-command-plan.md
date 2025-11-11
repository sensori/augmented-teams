# DDD Interaction Command Implementation Plan

## Prerequisites: Create Initial Infrastructure

**IMPORTANT**: Before proceeding with implementation, you must first create the initial infrastructure scaffolding:

1. **Generate Initial Infrastructure**:
   - Run `/code-agent-command-generate ddd ddd-interaction "Document domain interactions and business flows" "Domain interactions file"` to create the initial command files
   - This will generate the basic command structure files (`ddd-interaction-cmd.md`, `ddd-interaction-generate-cmd.md`, `ddd-interaction-validate-cmd.md`)

2. **Validate Initial Infrastructure**:
   - Run `/code-agent-command-validate ddd ddd-interaction` to validate the generated files
   - Fix any validation errors before proceeding

3. **CRITICAL: Follow Test-Driven Development Workflow**:
   - **DO NOT** jump directly to implementing the command files and runners
   - **INSTEAD**, follow the TDD workflow: **Scaffold → Signature → Write Tests → Write Code**
   - The plan below provides context and analysis, but implementation must follow the TDD phases

## AI Analysis Required

### 1. Command Architecture

**Command Classes Needed:**
- `DDDCommand(Command)` - Base command class (shared with structure command)
- `DDDInteractionCommand(DDDCommand)` - Implements domain interaction documentation logic
- `CodeAugmentedDDDInteractionCommand(CodeAugmentedCommand)` - Wraps DDDInteractionCommand with heuristic validation

**Wrapping Pattern:**
`CodeAugmentedDDDInteractionCommand → DDDInteractionCommand → Command`

### 2. Algorithms and Logic

**Generation Algorithm:**
1. Discover domain map file (input - created by ddd-structure command)
2. Read domain map to understand domain concepts
3. Read source code to understand how concepts interact
4. Apply §11 DDD principles:
   - Maintain domain abstraction level (§11.1)
   - Use scenario structure for flows (§11.2)
   - Describe transformations (§11.3)
   - Describe lookups (§11.4)
   - State business rules clearly (§11.5)
   - Show cross-domain reuse (§11.6)
5. Generate scenario-based interaction flows
6. Save to `<name>-domain-interactions.txt` (same folder as domain map)

**Heuristic Logic Required:**
- `AbstractionLevelHeuristic` (§11.1) - Detects implementation details (field names, code syntax, API parameters)
- `ScenarioStructureHeuristic` (§11.2) - Validates proper scenario format (TRIGGER, ACTORS, FLOW, RULES, RESULT)
- `TransformationHeuristic` (§11.3) - Detects constructor calls instead of business transformations
- `LookupHeuristic` (§11.4) - Detects database queries instead of business lookups
- `BusinessRulesHeuristic` (§11.5) - Detects code conditionals instead of domain rules
- `CrossDomainHeuristic` (§11.6) - Detects code reuse details instead of domain reuse

### 3. Command Relationships

**Relationship to other DDD commands:**
- `ddd-structure` creates domain maps (prerequisite)
- `ddd-interaction` uses domain maps as input
- Interaction command requires domain map to exist

### 4. Implementation Details

**Helper Methods:**
- `_discover_domain_map()` - Find domain map file in directory
- `_parse_domain_map()` - Parse domain map to extract concepts
- `_analyze_source_code()` - Analyze code to understand interactions
- `_identify_scenarios()` - Identify business scenarios
- `_document_flow()` - Document scenario flow
- `_generate_interactions()` - Create interaction flows output

**File Structures:**
- Input: Domain map file + source code directory
- Output: `<name>-domain-interactions.txt` (scenario-based flows)

## Files to Create

### 1. Command Definition Files
- `behaviors/ddd/interaction/ddd-interaction-cmd.md` - Main command
- `behaviors/ddd/interaction/ddd-interaction-generate-cmd.md` - Generate delegate
- `behaviors/ddd/interaction/ddd-interaction-validate-cmd.md` - Validate delegate

### 2. Runner Implementation
- Add to `behaviors/ddd/ddd_runner.py`:
  - `DDDInteractionCommand` class (inner command with business logic)
  - `CodeAugmentedDDDInteractionCommand` class (wrapper with heuristics)
  - 6 heuristic classes (one per §11 subsection)
  - CLI handlers: execute-interaction, generate-interaction, validate-interaction

### 3. Test Implementation
- Add to `behaviors/ddd/ddd_runner_test.py`:
  - Test signatures for DDDInteractionCommand
  - Test generation returns prompts
  - Test discovers domain map
  - Test validation uses heuristics
  - Test heuristics detect abstraction violations
  - Mock file operations only

## Implementation Approach & Best Practices

**Follow BDD and Clean Code principles:**
- Mocking: Only mock file I/O operations
- Base Class Reuse: Extend DDDCommand base class
- Clean Code: Use parameter objects, decompose methods
- BDD Compliance: Follow BDD test structure
- Test Strategy: Test observable behavior

## Testing Strategy: Test-Driven Development Workflow

### Phase 0: Domain Scaffold

1. **Extend Domain Scaffold**: `behaviors/ddd/docs/ddd_runner.domain.scaffold.txt`
   - Add DDDInteractionCommand behavioral descriptions
   - "should discover domain map file", "should maintain domain abstraction", "should document business flows"

2. **Validate Scaffold**: Ensure proper integration

### Phase 1: Signature

3. **Add Signatures**: Extend `ddd_runner_test.py` with interaction command signatures
   ```python
   with description("DDDInteractionCommand"):
       with context("generating domain interactions"):
           with it("should discover domain map file"):
               # BDD: SIGNATURE
               pass
           with it("should maintain domain abstraction level"):
               # BDD: SIGNATURE
               pass
   ```

4. **Validate Signatures**: Run `/bdd-validate`

### Phase 2: Write Tests

5. **Implement Test Bodies**: Write full test implementations
   - Mock file operations
   - Test domain map discovery
   - Test scenario generation
   - Test heuristics detect implementation details
   - Extract helpers for test data

6. **Validate Tests**: Run `/bdd-validate` and `/clean-code-validate`

### Phase 3: Write Code

7. **Implement Command Classes**: Make tests pass
   - Implement `DDDInteractionCommand` class
   - Implement 6 heuristic classes
   - Implement `CodeAugmentedDDDInteractionCommand` wrapper
   - Add CLI handlers

8. **Validate Code**: Run `/clean-code-validate` and `/bdd-validate`

## Success Criteria

- ✅ Command generates interaction flows following §11 principles
- ✅ Discovers domain map as input
- ✅ Maintains domain abstraction level
- ✅ Validation uses 6 heuristics to detect violations
- ✅ Works standalone via `/ddd-interaction`
- ✅ CLI testing successful
- ✅ All tests pass (TDD workflow complete)

## Key Insights

1. **Requires Domain Map**: Must discover domain map file created by ddd-structure
2. **Abstraction Level Critical**: Must avoid implementation details leaking into flows
3. **Scenario-Based**: Output organized by business scenarios, not code structure
4. **6 Heuristics**: One per §11 subsection for validation
5. **Language-Agnostic**: Domain interaction analysis applies to all languages
6. **Test Observable Behavior**: Test prompts and file generation, not internal logic

