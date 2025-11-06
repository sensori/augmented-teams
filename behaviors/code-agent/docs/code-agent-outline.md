# Code Agent Behavior Feature Outline

## Overview
This Behavior Feature contains behaviors for managing AI behavior files themselves - the behaviors that govern how behaviors are structured, validated, indexed, synced, and maintained. These behaviors enable the self-managing behavior system.

## Main Behaviors

**Behavior Consistency** - When behaviors are changed, deleted, updated, or created, validate for inconsistencies, overlapping behaviors, or inconsistent guidance, and surface potential contradictions or redundancies for review.

**Behavior Index** - Maintain a searchable index of all AI behaviors across features, tracking file locations, purposes, and modification timestamps. The index enables discovery and consistency checking.

**Behavior Specialization** - Validate hierarchical behavior patterns with base rules and specialized implementations (e.g., framework-specific variations like Jest vs Mamba for BDD testing).

**Behavior Structure** - Validate, fix, and create AI behaviors following structure and naming conventions. Ensures all behaviors follow consistent patterns for modularity, consistency, and discoverability.

**Behavior Suggest** - Analyze conversation patterns and suggest creating new behaviors when repetitive tasks are detected, helping users create reusable behavior definitions.

**Behavior Sync** - Keep AI behaviors up to date by syncing files from features marked with `behavior.json` (deployed: true) to `.cursor/` directories, merging MCP configs and tasks.json files.

## Implementation

**Consolidated Runner:** All code-agent behaviors are implemented in a single consolidated runner file (`code-agent-runner.py`) that provides:
- `behavior_structure()` - Structure validation, fixing, and scaffolding
- `behavior_sync()` - Sync behaviors to deployed locations
- `behavior_consistency()` - Semantic analysis for overlaps and contradictions
- `behavior_index()` - Maintain behavior indexes
- `validate_hierarchical_behavior()` - Specialization pattern validation
- Common utilities: `find_deployed_behaviors()`, `require_command_invocation()`

## Tools

**Runner:** `code-agent-runner.py` - Single consolidated Python runner implementing all code-agent commands

**Orchestrator:** Task configs (`code-agent-tasks.json`) merged into `.vscode/tasks.json` for background processes

**MCP:** MCP configs (`*-mcp.json`) synced to `.cursor/mcp/` and merged when multiple configs exist

## Related Features
This feature manages itself and the entire lifecycle of all other behavior features.
