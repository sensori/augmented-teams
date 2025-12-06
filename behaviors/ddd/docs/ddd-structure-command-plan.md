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
   - **DO NOT** jump directly to implementing according to the plan below
   - **INSTEAD**, follow the TDD workflow: **Scaffold → Signature → Write Tests → Write Code**
   - The plan below provides context and analysis, but implementation must follow the TDD phases

## AI Analysis Required

### 1. Command Architecture

**Command Classes Needed:**
- `DDDCommand(Command)` - Base class for DDD commands with shared functionality
- `DDDStructureCommand(DDDCommand)` - Structure analysis specific logic
- `CodeAugmentedDDDStructureCommand(CodeAugmentedCommand)` - Wrapper with heuristic validation

**Wrapping Pattern:**
`CodeAugmentedDDDStructureCommand` → `DDDStructureCommand` → `Command`

**Purpose:** Parse code/text/diagrams and extract domain structure following §1-10 principles

### 2. Algorithms and Logic

**Generation Algorithm:**
1. Read source file (code, text, diagram)
2. Identify functional purpose
3. Extract domain concepts (nouns, entities, services)
4. Apply ordering principles (§3 - user mental model)
5. Apply integration principles (§2, §6 - nest related concepts)
6. Apply naming principles (§1, §7 - outcome verbs, nouns for concepts)
7. Generate hierarchical text output with tabs for nesting
8. Output to `<name>-domain-map.txt`

**Validation Algorithm (Heuristics):**
- §1 Heuristic: Detect communication verbs (showing, displaying, visualizing, providing, enabling)
- §2 Heuristic: Detect separated "SYSTEM SUPPORT" sections
- §3 Heuristic: Detect code-structure ordering (models before domain, technical impl hiding objects)
- §4 Heuristic: Detect system-first organization (Events, UI, Services before domain)
- §5 Heuristic: Detect mechanism/technical framing (system names, technical descriptions)
- §6 Heuristic: Detect artificial separation (related concepts in different sections)
- §7 Heuristic: Detect verb-based concept names (Resolution, Execution, Processing)
- §8 Heuristic: Detect behaviors on wrong concepts (result concepts with actor behaviors)
- §9 Heuristic: Detect noun redundancy (multiple domains with same root noun)
- §10 Heuristic: Detect file structure organization (organized by file types)

### 3. Command Relationships

This is the first command in the DDD feature (new feature). Establishes patterns for:
- Domain analysis workflow (single-pass generation)
- Text-based hierarchical output format
- Heuristic validation pattern (one heuristic per principle)

### 4. Implementation Details

**Helper Methods:**
- `_parse_source()` - Read and parse source file
- `_identify_concepts()` - Extract nouns and domain concepts
- `_apply_ordering()` - Order by user mental model
- `_apply_integration()` - Nest related concepts
- `_generate_output()` - Create hierarchical text format

**No Templates Needed:** Output is freeform hierarchical text based on analysis

## Overview

Create `/ddd-structure` command that analyzes code/text/diagrams to extract domain structure following DDD principles. Command is added to new DDD feature with unified runner.

## Files to Create

### 1. Command Definition Files
- `behaviors/ddd/structure/ddd-structure-cmd.md` - Main command definition
- `behaviors/ddd/structure/ddd-structure-generate-cmd.md` - Generate delegate
- `behaviors/ddd/structure/ddd-structure-validate-cmd.md` - Validate delegate

### 2. Runner Implementation
- `behaviors/ddd/ddd_runner.py` - Unified runner for all DDD commands
  - `DDDCommand` class (base)
  - `DDDStructureCommand` class
  - `CodeAugmentedDDDStructureCommand` class (wrapper)
  - 10 heuristic classes (one per §1-10)
  - CLI handlers

### 3. Test File
- `behaviors/ddd/ddd_runner_test.py` - Mamba tests following TDD

## Implementation Approach & Best Practices

**Key principles to apply:**
- Mocking: Only mock file I/O operations, not internal classes
- Base Class Reuse: Maximize reuse of base Command class
- Clean Code: Use parameter objects, decompose methods, guard clauses
- BDD Compliance: Follow BDD principles for test structure
- Test Strategy: Test observable behavior (prompts, files), not internals

## Testing Strategy: Test-Driven Development Workflow

### Phase 0: Domain Scaffold

Create `behaviors/ddd/docs/ddd_runner.domain.scaffold.txt` with plain English descriptions:

```
DDD Structure Analysis
  Analyzing Source Files
    should extract domain concepts from code
    should extract domain concepts from text documents
    should extract domain concepts from diagrams
  
  Applying DDD Principles
    should apply outcome verbs principle (§1)
    should integrate system support under domain concepts (§2)
    should order by user mental model (§3)
    should organize domain-first (§4)
    should focus on functional accomplishment (§5)
    should maximize integration (§6)
    should use nouns for concepts (§7)
    should assign behaviors correctly (§8)
    should avoid noun redundancy (§9)
    should organize by domain concepts (§10)
  
  Generating Output
    should generate hierarchical text format
    should use tabs for nesting
    should output to domain-map.txt file
  
  Validating Output
    should detect communication verbs (§1 violation)
    should detect separated system support (§2 violation)
    should detect code-structure ordering (§3 violation)
```

### Phase 1: Signature

Convert scaffold to Mamba test signatures in `ddd_runner_test.py`:

```python
from mamba import description, context, it, before
from expects import expect, equal, be_true, contain
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

with description("DDDStructureCommand"):
    with context("generating domain structure"):
        with it("should extract domain concepts from code"):
            # BDD: SIGNATURE
            pass
        
        with it("should apply DDD principles"):
            # BDD: SIGNATURE
            pass
        
        with it("should generate hierarchical text output"):
            # BDD: SIGNATURE
            pass
```

### Phase 2: Write Tests

Implement test bodies with Arrange-Act-Assert:
- Mock file operations (Path.read_text, Path.write_text, Path.exists)
- Test that generate() returns prompts/instructions
- Test that validate() detects §1-10 violations using heuristics
- Don't mock DDDCommand, use real instances

### Phase 3: Write Code

Implement to make tests pass:
- `DDDStructureCommand` class
- 10 heuristic classes
- CLI handlers
- File I/O operations

## Implementation Tasks (TDD Workflow)

### Phase 0: Domain Scaffold
1. Create `behaviors/ddd/docs/ddd_runner.domain.scaffold.txt`
2. Validate scaffold follows BDD hierarchy principles

### Phase 1: Signature
3. Convert scaffold to Mamba signatures in `ddd_runner_test.py`
4. Mark with `# BDD: SIGNATURE`

### Phase 2: Write Tests
5. Implement test bodies with mocks and assertions
6. Tests should fail initially

### Phase 3: Write Code
7. Implement `DDDCommand` base class
8. Implement `DDDStructureCommand` class
9. Implement 10 heuristic classes (§1-10)
10. Implement `CodeAugmentedDDDStructureCommand` wrapper
11. Add CLI handlers to `main()`
12. All tests pass

### Integration Testing
13. Create sample code file for testing
14. Run CLI: `python behaviors/ddd/ddd_runner.py generate-structure <file>`
15. Verify domain map generated
16. Run CLI: `python behaviors/ddd/ddd_runner.py validate-structure <domain-map>`
17. Verify validation detects violations

## Key Differences from BDD Commands

- **Simpler workflow**: Generate → Validate (no incremental, no phases)
- **Single-pass analysis**: Analyze entire file/module at once
- **No specializing rules**: Domain analysis is language-agnostic
- **Text output**: Hierarchical text format, not code
- **Heuristic focus**: Validation primarily through heuristics detecting §1-10 violations

