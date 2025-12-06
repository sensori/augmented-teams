# Create {command_name} Command

## Prerequisites: Create Initial Infrastructure

**IMPORTANT**: Before proceeding with implementation, you must first create the initial infrastructure scaffolding:

1. **Generate Initial Infrastructure**:
   - Run `/code-agent-command-generate {feature_name} {command_name} "{command_purpose}" "{target_entity}"` to create the initial command files
   - This will generate the basic command structure files (`{command_name}-cmd.md`, `{command_name}-generate-cmd.md`, `{command_name}-validate-cmd.md`)
   - This is normal scaffolding - it creates the basic file structure

2. **Validate Initial Infrastructure**:
   - Run `/code-agent-command-validate {feature_name} {command_name}` to validate the generated files
   - Fix any validation errors before proceeding

3. **CRITICAL: Follow Test-Driven Development Workflow**:
   - **DO NOT** jump directly to implementing the command files and runners according to the plan below
   - **INSTEAD**, follow the TDD workflow: **Scaffold → Signature → Implementation (RED → GREEN)**
   - The plan below provides context and analysis, but implementation must follow the TDD phases described in the "Testing Strategy" section
   - Refer to BDD rules files (bdd-domain-scaffold-rule.mdc, bdd-domain-fluency-rule.mdc, bdd-mamba-rule.mdc) for what constitutes a valid scaffold, valid signature, etc.

## AI Analysis Required

**CRITICAL: Workflow Command Detection**

**If this is a workflow-related command (purpose contains "workflow", "phase", "stage", "scaffold", "signature", "red", "green", "refactor", or command name indicates workflow):**

**You MUST plan for BOTH command categories:**

1. **Phase-Specific Commands** (if this is a phase-specific command):
   - Main command: `/{feature_name}-{command_name}` (e.g., `/bdd-scaffold`)
   - Generate delegate: `/{feature_name}-{command_name}-generate`
   - Validate delegate: `/{feature_name}-{command_name}-validate`
   - Files: `{command_name}-cmd.md`, `{command_name}-generate-cmd.md`, `{command_name}-validate-cmd.md`
   - Purpose: Execute specific workflow phase/state

2. **Workflow Orchestrator Commands** (if workflow orchestrator doesn't exist or needs updating):
   - Main command: `/{feature_name}-workflow` (e.g., `/bdd-workflow`)
   - Generate delegate: `/{feature_name}-workflow-generate`
   - Validate delegate: `/{feature_name}-workflow-validate`
   - Files: `workflow/workflow-cmd.md`, `workflow/workflow-generate-cmd.md`, `workflow/workflow-validate-cmd.md`
   - Purpose: **Lightweight orchestrator** that delegates to appropriate phase-specific commands
   - **CRITICAL**: Workflow orchestrator commands should be VERY LIGHTWEIGHT and VERY SMALL - they simply delegate to the right phase-specific command to do its job. They do NOT contain complex logic or duplicate phase command functionality.

**Determine:**
- Is this a phase-specific command or workflow orchestrator?
- If phase-specific: Plan phase-specific commands AND check if workflow orchestrator needs creation/update
- If workflow orchestrator: Plan orchestrator commands AND identify which phase-specific commands it orchestrates
- Both follow standard pattern: main command + generate delegate + validate delegate
- **Architecture Pattern**: Workflow orchestrator = lightweight dispatcher that delegates to phase commands. Phase commands = full implementation with business logic.

1. **Command Architecture**: 
   - What exact command classes will be needed? (We are not certain - AI must determine based on purpose)
   - What wrapping patterns are appropriate? (CodeAugmentedCommand, IncrementalCommand, WorkflowPhaseCommand, SpecializingRuleCommand, etc.)
   - How should commands be composed and layered?
   - **If workflow command**: What is the relationship between phase-specific and orchestrator commands?

2. **Algorithms and Logic**:
   - What exact algorithms are needed for generation? (We are not certain - AI must determine)
   - **CRITICAL - Heuristic Requirements** (AI MUST analyze):
     * Read feature rule file: `{feature_name}-rule.mdc` (if exists)
     * Identify which principles apply to this command
     * For EACH applicable principle, determine:
       - Does this principle need automated validation? (YES/NO)
       - What patterns should the heuristic detect?
       - What violations should the heuristic report?
     * Plan heuristic classes: `{command_name}{PrincipleAspect}Heuristic`
     * Plan `_get_heuristic_map()` return dictionary: `{principle_number: HeuristicClass}`
     * **IF feature has rule file with applicable principles**: Heuristics are MANDATORY
     * **IF no applicable principles**: Document why heuristics aren't needed
   - What execution flow is needed? (AI must determine)

3. **Command Relationships**:
   - How does this command relate to existing commands in the {feature_name} feature?
   - What patterns from existing commands should be reused?
   - What new patterns need to be established?

4. **Implementation Details**:
   - What helper methods and utilities will be needed?
   - What templates need to be created or modified?
   - What file structures are required?

**The AI should use the command purpose ({command_purpose}) and target entity ({target_entity}) to make these determinations before proceeding with the detailed plan below.**
## Overview
Create `/{feature_name}-{command_name}` command that generates all files needed for a new {target_entity} within the {feature_name} feature, following the same structure and patterns as existing commands. Commands are added to the existing feature runner file and rule file is updated with command references.

**Note**: The specific command classes, algorithms, and implementation details listed below are placeholders. AI must analyze the command purpose and determine the actual requirements.

## Files to Create

### 1. Command Definition Files

**Phase-Specific Commands** (if this is a phase-specific workflow command):
- `behaviors/{feature_name}/{command_name}/{command_name}-cmd.md` - Main phase-specific command definition
- `behaviors/{feature_name}/{command_name}/{command_name}-generate-cmd.md` - Generate delegate (delegates to main command generate action)
- `behaviors/{feature_name}/{command_name}/{command_name}-validate-cmd.md` - Validate delegate (delegates to main command validate action)

**Workflow Orchestrator Commands** (if workflow orchestrator needs to be created/updated):
- `behaviors/{feature_name}/workflow/workflow-cmd.md` - Main workflow orchestrator command definition
- `behaviors/{feature_name}/workflow/workflow-generate-cmd.md` - Generate delegate (delegates to main workflow command generate action)
- `behaviors/{feature_name}/workflow/workflow-validate-cmd.md` - Validate delegate (delegates to main workflow command validate action)

**Note**: If this is NOT a workflow command, only create the phase-specific command files above.

### 2. Templates
- Use existing `behaviors/{feature_name}/command/command_template.md` as base template for generating `{command_name}-cmd.md` files (modify if needed)
- `behaviors/{feature_name}/command/command_class_template.py` - Template for command class to append to existing runner file
- `behaviors/{feature_name}/{feature_name}-rule.mdc` - Base rule file (for reference) with commands section
- `behaviors/{feature_name}/command/rule_command_entry_template.mdc` - Template snippet for adding command reference to "Executing Commands" section

### 3. Runner Implementation
- **AI must determine**: What exact command classes are needed based on analysis above
- **Placeholder examples**: `{CommandClassName}Command` class (may extend CodeAgentCommand or other base classes)
- **Placeholder examples**: Wrapper classes (may use CodeAugmentedCommand, IncrementalCommand, WorkflowPhaseCommand, etc.)
- Add CLI handlers in `main()` function

## Implementation Approach & Best Practices

**IMPORTANT**: When updating this plan, review and incorporate principles from:
- **BDD Rules**: `bdd-rule.mdc`, `bdd-domain-scaffold-rule.mdc`, `bdd-domain-fluency-rule.mdc`, `bdd-mamba-rule.mdc` (or framework-specific rules)
- **Clean Code Rules**: `clean-code-rule.mdc`, `clean-code-js-rule.mdc`, `clean-code-python-rule.mdc` (or language-specific rules)

**Key principles to apply** (see rules for full details):
- Mocking: Only mock file I/O operations, not internal classes
- Base Class Reuse: Maximize reuse of base classes, don't reimplement logic
- Clean Code: Use parameter objects, decompose large methods, use guard clauses, validate early
- BDD Compliance: Follow BDD principles for test structure, naming, and organization
- Test Strategy: Test observable behavior, use helpers, avoid duplication

## Implementation Details

**Note**: The class structures below are examples/placeholders. AI must determine the actual architecture based on the analysis above. Follow the best practices above.

### {CommandClassName}Command Class Structure (Example - AI must determine actual structure)
- **AI must determine**: What base class to extend (CodeAgentCommand, Command, or other)
- **AI must determine**: What methods and logic are needed for generation, validation, execution
- Example pattern: Extends `CodeAgentCommand` (like `FeatureCommand`) - handles template loading and file generation
- **Use Parameter Object**: Create `{CommandClassName}CommandConfig` dataclass instead of many parameters:
  ```python
  @dataclass
  class {CommandClassName}CommandConfig:
      feature_name: Optional[str] = None
      command_name: Optional[str] = None
      command_purpose: Optional[str] = None
      target_entity: Optional[str] = None
  ```
- Content: Points to `behaviors/{feature_name}/{command_name}/` directory (where command files will be created)
- **Method Decomposition**: Large methods should be decomposed:
  - `generate()` → `_generate_files()`, `_update_runner()`, `_update_rule_file()`
  - `validate()` → `_validate_structure()`, `_validate_content()`, `_validate_integration()`
  - Use guard clauses to reduce nesting

### CodeAugmented{CommandClassName}Command Class Structure (MANDATORY Pattern)

**CRITICAL: Heuristic Implementation Steps are REQUIRED for this pattern to work**

1. **Wrapper Pattern**:
   - Extends `CodeAugmentedCommand`
   - Wraps `{CommandClassName}Command` instance
   - Provides CLI integration via `handle_cli()` method

2. **Heuristic Mapping (MANDATORY)**:
   ```python
   def _get_heuristic_map(self):
       """Map principle numbers to heuristic classes
       
       CRITICAL: This method MUST be implemented.
       Return empty dict {} ONLY if:
       - Feature has no rule file, OR
       - Rule file has no applicable principles for this command
       
       Otherwise, map principle numbers to heuristic classes.
       """
       # AI MUST determine based on feature rule file analysis
       return {
           principle_number: HeuristicClass,
           # ... more mappings
       }
   ```

3. **Heuristic Classes (Create for each mapped principle)**:
   ```python
   class {CommandName}{PrincipleAspect}Heuristic(CodeHeuristic):
       def __init__(self):
           super().__init__(detection_pattern="{command_name}_{aspect}")
       
       def scan(self, content):
           """Scan content for violations
           
           Returns: list of (line_number, message) tuples
           """
           violations = []
           # AI MUST determine scanning logic based on principle
           return violations
   ```

**Feature Rule Integration Decision Tree**:
- ✅ Feature has rule file (`{feature_name}-rule.mdc`) → Analyze principles
  - ✅ Principles apply to this command → Create heuristics (MANDATORY)
  - ❌ No principles apply to this command → Document why, empty map OK
- ❌ No rule file exists → Empty map OK (no principles to validate)

### File Generation Logic (AI must determine actual algorithms)
**AI must analyze the command purpose and determine:**
1. **Command Location**: `behaviors/{feature_name}/{command_name}/` (or AI-determined location)
2. **Files Generated** (AI must determine what files are actually needed):
   - `{command_name}-cmd.md` - From existing `command_template.md` with placeholders filled (or AI-determined template)
   - `{command_name}-generate-cmd.md` - Delegates to main command's generate action (or AI-determined structure)
   - `{command_name}-validate-cmd.md` - Delegates to main command's validate action (or AI-determined structure)
   - **AI must determine**: Are there additional files needed? What templates are required?
3. **Runner Updates** (AI must determine the algorithm):
   - Read existing runner file
   - **AI must determine**: How to append/modify command classes (string replacement, AST manipulation, etc.)
   - **AI must determine**: What CLI handlers are needed and how to add them
   - **Decompose**: Break into `_read_runner_file()`, `_append_command_class()`, `_add_cli_handlers()`
4. **Rule File Updates** (AI must determine the algorithm):
   - Read existing rule file
   - **AI must determine**: How to append command reference (string replacement, structured parsing, etc.)
   - Format: `* /{feature_name}-{command_name} — {command_purpose}` (or AI-determined format)
   - **Decompose**: Break into `_read_rule_file()`, `_find_executing_commands_section()`, `_append_command_reference()`
   - **Use guard clauses**: Check if section exists, return early if already added

### Template Placeholders
- `{command_name}` → actual command name: {command_name}
- `{command_purpose}` → purpose description: {command_purpose}
- `{target_entity}` → what command operates on: {target_entity}
- `{rule_name}` → rule file reference: {feature_name}-rule
- `{feature_name}` → parent feature name: {feature_name}
- `{runner_path}` → path to runner file: {feature_name}/{feature_name}_runner.py
- `{command_parameters}` → parameters for the command: [{feature_name}] [{command_name}]
- `{CommandClassName}` → PascalCase command class name: {command_class_name}

### Validation Logic
- Check command directory exists under feature
- Validate all required files exist (`{command_name}-cmd.md`, `{command_name}-generate-cmd.md`, `{command_name}-validate-cmd.md`)
- Validate command.md follows template structure
- Validate runner file has command class added correctly
- Validate CLI handlers added to main() function
- Validate rule file has command reference added to "Executing Commands" section
- Use code heuristics to scan for violations (via CodeAugmentedCommand wrapper)
- **Heuristic Validation** (if feature has rule file):
  * Verify CodeAugmented wrapper class implements `_get_heuristic_map()` method
  * Check that `_get_heuristic_map()` returns non-empty dict if feature has rule file with applicable principles
  * Validate heuristic classes are defined for mapped principles
  * Ensure heuristics extend `CodeHeuristic` base class
  * Verify heuristics implement `scan()` method properly

### CLI Integration
Add to `main()`:
- `execute-{command_name} [{feature_name}] [{command_name}]`
- `generate-{command_name} [{feature_name}] [{command_name}]`
- `validate-{command_name} [{feature_name}] [{command_name}]`

## Key Differences from FeatureCommand
- Creates files in `behaviors/{feature_name}/{command_name}/` instead of `behaviors/{feature_name}/`
- Generates command.md files instead of behavior.json/feature-outline.md
- Updates existing runner file (appends command class) instead of creating new runner
- Updates existing rule file (appends command reference) instead of creating new rule
- References existing rule file instead of creating one
- Uses command-specific templates
- Content points to command subdirectory, not feature root
- Identical class hierarchy: {CommandClassName}Command extends CodeAgentCommand, CodeAugmented{CommandClassName}Command extends CodeAugmentedCommand

## Testing Strategy: Test-Driven Development Workflow

**CRITICAL**: After creating the initial infrastructure (steps 1-2 above), **DO NOT** implement the command files and runners directly. Instead, follow this TDD workflow:

### Phase 0: Domain Scaffold (Create Test Structure First)

**Purpose**: Create a domain scaffold that represents what you want to build - this is a good representation of the command's behavior before implementation.

1. **Create or Extend Domain Scaffold**: `behaviors/{feature_name}/docs/{feature_name}_runner.domain.scaffold.txt`
   
   **Scaffold Creation Process**:
   - If scaffold file exists: Read existing scaffold to understand structure and patterns, then extend it
   - If scaffold file does not exist: Create new scaffold file with appropriate structure
   - Add describe blocks for the command classes that represent the behavior you want to build:
     - Focus on **what the command should do** (behavioral descriptions)
     - Represent the command classes ({CommandClassName}Command, CodeAugmented{CommandClassName}Command) or other command types as behavioral concepts
     - Include tests for generation, validation, and execution behaviors
     - Include tests for rule integration if applicable
   - If existing scaffold exists: Reuse concepts from existing scaffold (CodeAgentCommand, FeatureCommand patterns)
   - Integrate concepts within tests (avoid duplicating CodeAgentCommand tests)
   - Integrate concepts across tests (reference FeatureCommand patterns where applicable, if they exist)
   
   **Scaffold Validation**:
   - Run `/bdd-domain-scaffold-verify` to ensure:
     - No duplication of existing test concepts (if scaffold existed)
     - Proper integration with existing describe blocks (if scaffold existed)
     - Concepts properly nested and related
     - Follows hierarchy and fluency principles
   - Fix any violations before proceeding

### Phase 1: Signature (Convert Scaffold to Test Code Structure)

**Purpose**: Convert the domain scaffold (plain English) into test code structure with empty test bodies.

1. **Convert Scaffold to Signatures**: Convert scaffold to Mamba test syntax with empty test bodies marked `# BDD: SIGNATURE`
   - If `{feature_name}_runner_test.py` exists: Reuse helper functions from existing test file
   - If test file does not exist: Create new test file with appropriate structure
   - Follow existing test structure patterns (if test file exists) or establish new patterns
   - Each describe/it block from scaffold becomes a test signature
   - Test bodies are empty with `# BDD: SIGNATURE` comment
   
2. **Signature Validation**:
   - Run `/bdd-validate-cmd` on signature tests
   - Fix any violations before proceeding

### Phase 2: RED (Implement Failing Tests)

**Purpose**: Implement test bodies with Arrange-Act-Assert logic. Tests should fail initially.

1. **Implement Test Bodies**:
   - If `{feature_name}_runner_test.py` exists: Follow patterns from existing test file:
     - **Mocking Strategy**: Mock ONLY file I/O operations (Path.read_text, Path.write_text, Path.exists, Path.mkdir, open)
     - **DO NOT mock**: Internal classes (BaseRule, Command, etc.) - use real instances
     - **DO NOT mock**: Helper methods or business logic classes - test actual behavior
     - Test observable behavior (prompts returned, files created) not internal implementation
     - Use helper functions for common setup (if they exist)
     - Move duplicate Arrange code to `before.each`
     - Only test logic unique to {CommandClassName}Command (not duplicated from base Command/CodeAgentCommand)
   - If test file does not exist: Establish new test patterns following BDD best practices
   - Mock file operations (Path.exists, Path.mkdir, Path.write_text, Path.read_text) - use `autospec=True` for Path mocks
   - Test that generate() returns prompts (instructions strings)
   - Test that validate() returns prompts with violations
   - Test file content structure (markdown structure) not internal calls
   
2. **RED Validation**:
   - Run `/bdd-validate-cmd` on RED tests
   - Fix any violations before proceeding
   - Verify tests fail as expected (RED state)

### Phase 3: GREEN (Implement Command Files and Runners)

**Purpose**: Implement the actual command files and runners to make tests pass.

1. **Implement Command Classes**:
   - Implement {CommandClassName}Command class in `{feature_name}_runner.py`
   - Implement CodeAugmented{CommandClassName}Command wrapper class
   - Add CLI handlers in `main()` function
   - Follow the patterns and structure determined in the scaffold phase
   
2. **Apply Clean Code Principles** (run `/clean-code-validate-cmd` early and often):
   - Use parameter objects (dataclasses) instead of many parameters
   - Decompose large methods into smaller private methods
   - Use guard clauses to reduce nesting
   - Maximize reuse of base classes - don't reimplement logic
   - Fix violations immediately, don't wait until the end
   
3. **Validate Continuously**:
   - Run `/clean-code-validate-cmd` after each major method implementation
   - Run `/bdd-validate-cmd` to ensure BDD compliance
   - Fix violations as you go
   
2. **GREEN Validation**:
   - Run tests until all pass (GREEN state)
   - Run `/bdd-validate-cmd` on GREEN tests
   - Fix any violations
   - Verify all tests pass

**Key Principle**: The scaffold represents what you want to build. The signature provides the test structure. RED tests define the expected behavior. GREEN implementation makes it work. This ensures you build the right thing, not just build something.

### Integration Testing Workflow
1. **Setup**: Create mock/demo feature first using `/{feature_name}-feature` command
2. **Test Command Creation**: Run `/{feature_name}-{command_name}` to create a test command
3. **Verify Files**: Check all files generated correctly (command.md, generate-cmd.md, validate-cmd.md)
4. **Verify Runner**: Check runner file updated with command class
5. **Verify Rule**: Check rule file updated with command reference
6. **Test CLI**: Test command line execution (execute-{command_name}, generate-{command_name}, validate-{command_name})
7. **Test Full Lifecycle**: Test generate → validate → execute workflow

### Failure Recovery Strategy
When command line tests fail:
1. **RED**: Introduce a test that mimics the failure (reproduces the bug)
2. **Verify RED**: Run test and confirm it fails as expected
3. **Fix Code**: Fix the implementation to address the issue
4. **GREEN**: Run test again until it passes
5. **Iterate**: Repeat until all tests are green
6. **Return to CLI**: Once tests pass, return to command line testing
7. **Repeat**: Continue this cycle until command line works successfully

## Implementation Tasks (TDD Workflow)

**Follow these tasks in order - do not skip ahead to implementation:**

### Phase 0: Domain Scaffold
1. **Analyze Context for Scaffold**:
   - Review command purpose ({command_purpose}) and target entity ({target_entity})
   - Review "AI Analysis Required" section to understand architectural needs
   - Review "Implementation Details" section to understand expected structure
   - Review existing commands in feature (if any) to understand patterns
   - Review feature rule file (`{feature_name}-rule.mdc`) if it exists
   
2. **Create/Extend Domain Scaffold**: 
   - Extend existing `behaviors/{feature_name}/docs/{feature_name}_runner.domain.scaffold.txt` with {CommandClassName}Command and CodeAugmented{CommandClassName}Command sections
   - Ensure scaffold represents what you want to build (behavioral descriptions)
   - Ensure no duplication and proper integration with existing concepts
   
3. **Validate Scaffold**: 
   - Run `/bdd-domain-scaffold-verify` to validate scaffold follows hierarchy principles, no duplication, and proper concept integration
   - Fix violations before proceeding

### Phase 1: Signature
4. **Convert to Signature**: 
   - Convert scaffold to Mamba test syntax with empty test bodies (# BDD: SIGNATURE)
   - Reuse helper functions and patterns from existing `{feature_name}_runner_test.py` if it exists
   
5. **Validate Signature**: 
   - Run `/bdd-validate-cmd` on signature tests, fix violations

### Phase 2: RED
6. **Implement RED Tests**: 
   - Implement RED phase tests following patterns from `{feature_name}_runner_test.py` (mock file ops, test observable behavior, use helpers, avoid duplicating base Command tests)
   - Tests should fail initially (RED state)
   
7. **Validate RED Tests**: 
   - Run `/bdd-validate-cmd` on RED tests, fix violations
   - Verify tests fail as expected

### Phase 3: GREEN
8. **Implement Command Files and Runners**: 
   - Implement {CommandClassName}Command class in `{feature_name}_runner.py`
   - Implement CodeAugmented{CommandClassName}Command wrapper class
   - Add CLI handlers in `main()` function
   - Fix code until all tests pass (GREEN phase)
   
9. **Validate GREEN Tests**: 
   - Run `/bdd-validate-cmd` on GREEN tests, fix violations
   - Verify all tests pass

### Integration Testing
10. **Create Demo Feature**: 
    - Create mock/demo feature using `/{feature_name}-feature` command for integration testing
    
11. **Test Command Creation**: 
    - Test creating a command via CLI, verify files generated, runner updated, rule updated
    
12. **Test CLI Workflow**: 
    - Test CLI execution (execute-{command_name}, generate-{command_name}, validate-{command_name}) and full lifecycle
    
13. **Handle Failures**: 
    - When CLI tests fail: create test that reproduces failure (RED), fix code, verify test passes (GREEN), return to CLI testing

