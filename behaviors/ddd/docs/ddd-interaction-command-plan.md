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
   - **DO NOT** jump directly to implementing according to the plan below
   - **INSTEAD**, follow the TDD workflow: **Scaffold → Signature → Write Tests → Write Code**
   - The plan below provides context and analysis, but implementation must follow the TDD phases

## AI Analysis Required

### 1. Command Architecture

**Command Classes Needed:**
- `DDDCommand(Command)` - Base class (shared with structure command)
- `DDDInteractionCommand(DDDCommand)` - Interaction analysis specific logic
- `CodeAugmentedDDDInteractionCommand(CodeAugmentedCommand)` - Wrapper with heuristic validation

**Wrapping Pattern:**
`CodeAugmentedDDDInteractionCommand` → `DDDInteractionCommand` → `DDDCommand` → `Command`

**Purpose:** Document business flows and domain interactions following §11 principles

### 2. Algorithms and Logic

**Generation Algorithm:**
1. Read domain map file (input from ddd-structure command)
2. Read source code for implementation details
3. Identify business scenarios and triggers
4. Extract domain concept interactions
5. Document transformations (Concept A → Concept B)
6. Document lookups and business rules
7. Maintain domain-level abstraction (§11.1 - no implementation details)
8. Generate scenario-based flows
9. Output to `<name>-domain-interactions.txt`

**Validation Algorithm (Heuristics):**
- §11.1 Heuristic: Detect implementation details (field names, code syntax, API parameters)
- §11.2 Heuristic: Detect missing scenario structure (trigger, actors, flow, rules, result)
- §11.3 Heuristic: Detect code-level transformations (constructor calls, field mapping)
- §11.4 Heuristic: Detect implementation-level lookups (queries, filters, null checks)
- §11.5 Heuristic: Detect code conditionals instead of business rules (if/else, boolean logic)

### 3. Command Relationships

**Depends on:** `/ddd-structure` command (domain map is input)

**Workflow:**
1. Run `/ddd-structure` on code → generates domain map
2. Run `/ddd-interaction` on domain map → generates interaction flows

### 4. Implementation Details

**Helper Methods:**
- `_discover_domain_map()` - Find domain map file in same directory
- `_parse_domain_map()` - Extract concepts from domain map
- `_identify_scenarios()` - Identify business scenarios from code
- `_document_flow()` - Create scenario flow documentation
- `_extract_business_rules()` - Extract domain constraints
- `_generate_output()` - Create scenario-based text format

**Input Discovery:**
- Look for `*-domain-map.txt` in same directory as target file
- Use domain map concepts as vocabulary for interaction flows

## Overview

Create `/ddd-interaction` command that documents domain concept interactions and business flows following DDD principles. Builds on domain maps from `/ddd-structure` command.

## Files to Create

### 1. Command Definition Files
- `behaviors/ddd/interaction/ddd-interaction-cmd.md` - Main command definition
- `behaviors/ddd/interaction/ddd-interaction-generate-cmd.md` - Generate delegate
- `behaviors/ddd/interaction/ddd-interaction-validate-cmd.md` - Validate delegate

### 2. Runner Implementation (add to existing ddd_runner.py)
- `DDDInteractionCommand` class
- `CodeAugmentedDDDInteractionCommand` class (wrapper)
- 5 heuristic classes for §11 subsections
- CLI handlers (execute-interaction, generate-interaction, validate-interaction)

### 3. Test File (extend existing ddd_runner_test.py)
- Add test signatures for DDDInteractionCommand
- Add test implementations following Mamba patterns

## Implementation Approach & Best Practices

**Key principles:**
- Mocking: Only mock file I/O operations
- Reuse: Use existing DDDCommand base class
- Clean Code: Parameter objects, method decomposition, guard clauses
- BDD Compliance: Test structure follows BDD principles
- Domain map discovery: Find and parse domain map as input

## Testing Strategy: Test-Driven Development Workflow

### Phase 0: Domain Scaffold

Extend `behaviors/ddd/docs/ddd_runner.domain.scaffold.txt`:

```
DDD Interaction Analysis
  Discovering Domain Maps
    should find domain map in same directory
    should parse domain map concepts
  
  Analyzing Business Flows
    should identify business scenarios from code
    should extract domain concept interactions
    should maintain domain-level abstraction (§11.1)
  
  Documenting Interactions
    should structure scenarios with trigger/actors/flow/rules/result (§11.2)
    should describe transformations at business level (§11.3)
    should describe lookups as business strategy (§11.4)
    should state business rules as domain logic (§11.5)
  
  Generating Output
    should output scenario-based format
    should name file domain-interactions.txt
  
  Validating Output
    should detect implementation details (§11.1 violation)
    should detect missing scenario structure (§11.2 violation)
    should detect code-level transformations (§11.3 violation)
```

### Phase 1: Signature

Add signatures to `ddd_runner_test.py`:

```python
with description("DDDInteractionCommand"):
    with context("generating domain interactions"):
        with it("should discover domain map as input"):
            # BDD: SIGNATURE
            pass
        
        with it("should document business flows"):
            # BDD: SIGNATURE
            pass
        
        with it("should maintain domain abstraction"):
            # BDD: SIGNATURE
            pass
```

### Phase 2: Write Tests

Implement test bodies:
- Mock file operations
- Test domain map discovery
- Test interaction flow generation
- Test heuristics detect §11 violations

### Phase 3: Write Code

Implement to make tests pass:
- `DDDInteractionCommand` class
- Heuristic classes for §11
- CLI handlers
- Domain map parsing logic

## Key Differences from Structure Command

- **Input**: Domain map file (from structure command) + source code
- **Output**: Scenario-based interaction flows (not hierarchical structure)
- **Focus**: Business flows and transformations (not concept extraction)
- **Heuristics**: §11 subsections (abstraction, scenarios, transformations, lookups, rules)
- **Discovery**: Must find domain map file to use as input

