# DDD Feature - Domain-Driven Design Analysis

## Purpose
Extract domain structures and document interaction flows from code, text, and diagrams following Domain-Driven Design principles.

## Commands

### `/ddd-structure`
Analyze code/text/diagrams to extract domain structure as hierarchical domain map.

**Input:** Code files, text documents, diagrams, documentation  
**Output:** Domain map file (`<name>-domain-map.txt`)  
**Principles:** Applies §1-10 of ddd-rule.mdc

### `/ddd-interaction`  
Document domain concept interactions and business flows at domain abstraction level.

**Input:** Domain map + source code  
**Output:** Domain interactions file (`<name>-domain-interactions.txt`)  
**Principles:** Applies §11 of ddd-rule.mdc

## Use Cases

1. **Analyze codebase** → Extract domain structure → Understand business logic
2. **Document interactions** → Map business flows → Understand concept relationships
3. **Validate domain models** → Check against DDD principles → Improve design

