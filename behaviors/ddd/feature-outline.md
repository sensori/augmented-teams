# DDD Feature

## Purpose
Domain-Driven Design (DDD) analysis tools for extracting domain structures and documenting business flows from code, text, and diagrams.

## Commands

### `/ddd-structure`
Analyzes source files to extract domain structure following 10 core DDD principles:
- Outcome verbs, not communication verbs
- Integrate system support under domain concepts
- Order by user mental model
- Domain-first organization
- Functional accomplishment focus
- Maximize integration
- Nouns for concepts, verbs for behaviors
- Assign behaviors correctly
- Avoid noun redundancy
- Domain concepts over file structure

**Output:** Hierarchical domain map (`<name>-domain-map.txt`)

### `/ddd-interaction`
Documents domain concept interactions and business flows following DDD interaction principles:
- Maintain domain-level abstraction
- Structure scenarios properly
- Business-level transformations
- Business strategy lookups
- Domain logic business rules

**Input:** Domain map + source code
**Output:** Scenario-based interaction flows (`<name>-domain-interactions.txt`)

## Use Cases
1. Analyze existing codebase to extract domain model
2. Document business flows for testing (BDD scaffold/interaction input)
3. Understand domain relationships before refactoring
4. Create business-readable documentation from technical code

