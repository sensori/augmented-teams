# BDD Workflow Command Implementation Plan

## Overview
Create a `/bdd-workflow` command that orchestrates all BDD phases (Domain Scaffold, Signatures, Write Tests, Write Code). This is a **VERY LIGHTWEIGHT orchestrator** that simply delegates to phase-specific commands and manages workflow state. It does NOT contain complex logic or duplicate phase command functionality.

## Key Requirements

1. **Workflow Orchestrator Only**: This command orchestrates phases, does NOT implement phase logic
2. **Delegates to Phase Commands**: Routes to `/bdd-scaffold`, `/bdd-signature`, `/bdd-test`, `/bdd-code`
3. **State Management**: Tracks current phase, completed phases, workflow progress
4. **Phase Navigation**: Supports approve, jump-to, restart, status operations
5. **Uses Common Workflow Infrastructure**: Leverages existing `Workflow` and `WorkflowPhaseCommand` classes from common runner

## Investigation Results

### 1. Workflow Orchestrator Pattern - FINDINGS

**Current State:**
- `Workflow` class exists in `common_command_runner.py` - provides state management
- `WorkflowPhaseCommand` exists - wraps phase commands with workflow state
- `BDDWorkflow` class (lines 1029-1092) **FULLY IMPLEMENTED** - creates all 4 phases
- `BDDWorkflowPhaseCommand` (lines 1208+) wraps `WorkflowPhaseCommand` with BDD-specific logic
- CLI handler exists: `bdd_workflow()` function

**Analysis:**
- Workflow orchestrator is **NOT** a complex command class
- It's a **lightweight dispatcher** that:
  - Identifies current phase from state
  - Routes to appropriate phase-specific command
  - Manages workflow state (phase transitions)
  - Provides workflow operations (approve, jump-to, status, restart)

**Decision:** ✅ **Workflow Command is Lightweight Orchestrator**
- Command file describes workflow operations
- References existing `BDDWorkflow` class
- Does NOT contain complex logic
- Simply explains how to use workflow commands

### 2. Workflow State and Operations - FINDINGS

**Current State:**
- `BDDWorkflow` already manages 4 phases
- Workflow state tracked via `WorkflowPhaseCommand`
- Operations available (from common runner):
  - **generate**: Execute current phase generation
  - **validate**: Execute current phase validation
  - **approve**: Approve current phase and move to next
  - **jump-to**: Jump to specific phase
  - **status**: Show current workflow state
  - **restart**: Restart workflow from beginning

**Decision:** ✅ **Document Workflow Operations in Command File**
- List all 4 phases
- Explain each workflow operation
- Show how to navigate between phases
- Reference phase-specific commands for details

### 3. Command Structure - FINDINGS

**Current State:**
- Workflow orchestrator commands already partially exist
- CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] [phase] --no-guard`
- Infrastructure fully implemented

**Decision:** ✅ **Create Command Files That Document Workflow Usage**
- Main command: `bdd-workflow-cmd.md`
- Generate delegate: `bdd-workflow-generate-cmd.md` (executes current phase generate)
- Validate delegate: `bdd-workflow-validate-cmd.md` (executes current phase validate)
- NO complex logic - just documentation of how to use workflow

## Implementation Plan

### Phase 1: Create Workflow Command Files

**Workflow Orchestrator Command Files:**
- `behaviors/bdd/workflow/bdd-workflow-cmd.md` - Main workflow orchestrator
- `behaviors/bdd/workflow/bdd-workflow-generate-cmd.md` - Generate delegate
- `behaviors/bdd/workflow/bdd-workflow-validate-cmd.md` - Validate delegate

**Command Content Requirements:**

**Main Command (`bdd-workflow-cmd.md`):**
- **Purpose**: Orchestrate BDD workflow phases (Domain Scaffold → Signatures → Write Tests → Write Code)
- **Phases**: List all 4 phases with descriptions
  - Phase 0: Domain Scaffolding - Generate plain English hierarchy from domain maps
  - Phase 1: Build Test Signatures - Convert scaffold to code structure with empty bodies
  - Phase 2: Write Tests - Implement tests with Arrange-Act-Assert
  - Phase 3: Write Code - Implement production code to make tests pass
- **Operations**:
  - `generate` - Execute current phase generation
  - `validate` - Execute current phase validation
  - `approve` - Approve current phase and advance to next
  - `jump-to` - Jump to specific phase
  - `status` - Show current workflow state
- **Phase-Specific Commands**: Link to `/bdd-scaffold`, `/bdd-signature`, `/bdd-test`, `/bdd-code`
- **Runner**: Reference existing `BDDWorkflow` class
- **CLI**: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] [phase] --no-guard`

**Generate Delegate (`bdd-workflow-generate-cmd.md`):**
- Delegates to current phase's generate action
- Very simple - just execute generation for current phase

**Validate Delegate (`bdd-workflow-validate-cmd.md`):**
- Delegates to current phase's validate action
- Very simple - just execute validation for current phase

### Phase 2: Update Rule Files

**NO RULE SECTION NEEDED** - Workflow orchestrator doesn't implement logic, just orchestrates

**Update Commands Section in Rules:**
- Already done - workflow commands listed in base rule and specializing rules

### Phase 3: No Runner Code Needed

**Infrastructure Already Exists:**
- `BDDWorkflow` class - Fully implemented with 4 phases
- `BDDWorkflowPhaseCommand` - Wraps phases with workflow state
- `bdd_workflow()` function - CLI entry point
- All phase commands already integrated

**Command Files Only:**
- Create workflow command documentation files
- No new Python code needed
- Just document how to use existing workflow infrastructure

## Files to Create/Modify

### New Files:
- `behaviors/bdd/workflow/bdd-workflow-cmd.md` - Main workflow orchestrator command
- `behaviors/bdd/workflow/bdd-workflow-generate-cmd.md` - Generate delegate
- `behaviors/bdd/workflow/bdd-workflow-validate-cmd.md` - Validate delegate

### Modified Files:
- NONE - Rules already updated, runner already complete

### Code Changes Needed:
- NONE - Infrastructure fully implemented

## Implementation Steps

### Phase 1: Create Command Files
1. Create `bdd-workflow-cmd.md` - Document workflow orchestration
2. Create `bdd-workflow-generate-cmd.md` - Simple generate delegate
3. Create `bdd-workflow-validate-cmd.md` - Simple validate delegate

### Phase 2: Update Indexes
4. Run index generation to include workflow command files

### Phase 3: CLI Testing
5. Test workflow commands via CLI
6. Verify phase navigation works
7. Verify delegation to phase-specific commands

## Success Criteria ✅

- ✅ Workflow command documents all 4 phases clearly
- ✅ Workflow operations explained (generate, validate, approve, jump-to, status)
- ✅ Command files are lightweight - no complex logic
- ✅ Delegates properly to phase-specific commands
- ✅ CLI testing successful
- ✅ Indexes updated

## Key Insights

1. **Orchestrator is Lightweight**: No complex logic, just delegation and state management
2. **Phase-Specific Commands Do Work**: Workflow just routes to them
3. **Infrastructure Already Exists**: `BDDWorkflow` class fully implemented with 4 phases
4. **No Rules Needed**: Orchestrator doesn't implement logic, so no rules to follow
5. **Simple Command Files**: Just document how to use workflow, don't duplicate phase logic
6. **CLI Already Works**: `bdd_workflow()` function and CLI handler already complete
7. **State Management Handled**: `WorkflowPhaseCommand` and `Workflow` classes manage state
8. **Four Phases Only**: Domain Scaffold, Signatures, Write Tests, Write Code (REFACTOR removed)
9. **Validation is Refactoring**: Each phase validates, so refactoring happens throughout
10. **Template References**: Command describes workflow, references phase commands for details

## Workflow Operations Available

From common runner infrastructure:

1. **generate** - Execute current phase generation
2. **validate** - Execute current phase validation  
3. **approve** - Approve current phase, advance to next
4. **jump-to [phase]** - Jump to specific phase number
5. **status** - Show current phase and progress
6. **restart** - Restart workflow from beginning

All operations managed by existing `Workflow` and `WorkflowPhaseCommand` classes.

## Implementation Status

**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. Create `bdd-workflow-cmd.md` - Main orchestrator command file
2. Create `bdd-workflow-generate-cmd.md` - Generate delegate
3. Create `bdd-workflow-validate-cmd.md` - Validate delegate
4. Update indexes
5. CLI testing


