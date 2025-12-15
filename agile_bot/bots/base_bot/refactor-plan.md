# Refactoring Plan: Align Code with Class-Level Object Model

Overall guidance.
 I really don't want you to be holding on to legacy code for backwards compatibility that's going to screw up this refactor completely. Eliminate all old code so that we are only using the new code. Everything will be a fix forward.

 All tests need to satisfy the rules in the story-write-tests Validate_rules. 
 Specifically, we need to be matching the given-when-then story-epic/sub-epic structure of the current tests.

## Overview
This plan refactors the codebase to match the class-level object model, addressing SRP violations, size violations, and structural mismatches.

## Phase 1: Foundation - Config and Workspace Classes

### 1.1 Create BotConfig Class


## Phase 2: Bot and Behaviors Collection

### 2.1 Create Behaviors Collection Class
**File:** `src/bot/behaviors.py`
- **Responsibilities:**
  - Manage collection of Behavior objects
  - Track `current: Behavior` (persisted to behavior_action_state.json)
  - Methods: `find_by_name()`, `next()`, `iterate()`, `check_exists()`, `navigate_to()`, `close_current()`, `execute_current()`
  - State persistence: `save_state()`, `load_state()`
- **Instantiated with:** BotConfig
- **Dependencies:** Behavior, BotConfig
- **Impact:** High - new collection class, refactor Bot

### 2.2 Refactor Bot Class
**File:** `src/bot/bot.py`
- **Remove:** Direct behavior management
- **Add:** `behaviors: Behaviors` property (instantiate Behaviors collection)
- **Add:** `rules: Rules` property (instantiate Rules collection - Phase 3)
- **Keep:** `bot_directory`, `workspace_directory` properties
- **Method:** `execute()` delegates to `behaviors.execute_current()`
- **Dependencies:** BotConfig, Behaviors, Rules
- **Impact:** High - major refactor

### 2.3 Create BehaviorConfig Class
**File:** `src/bot/behavior_config.py`
- Extract config loading from Behavior
- Properties: `behavior_name`, `description`, `goal`, `inputs`, `outputs`, `base_actions_path`, `instructions`, `trigger_words`, `actions`
- Instantiated with: Behavior, BotPaths
- **Dependencies:** BotPaths
- **Impact:** Medium - extract from Behavior

### 2.4 Refactor Behavior Class
**File:** `src/bot/bot.py` (split Behavior)
- **Remove:** Config loading, workflow management, rules loading
- **Add:** Instantiate collaborators: `Guardrails`, `Content`, `Rules`, `Actions`, `TriggerWords`
- **Properties:** `folder`, `guardrails`, `content`, `rules`, `actions`
- **Properties:** `description`, `goal`, `inputs`, `outputs` (from BehaviorConfig)
- **Method:** `matches_trigger()` (delegates to TriggerWords)
- **Dependencies:** BehaviorConfig, Guardrails, Content, Rules, Actions, TriggerWords
- **Impact:** High - major split

## Phase 3: Actions Collection and Action Classes

### 3.1 Create Actions Collection Class
**File:** `src/bot/actions.py`
- **Responsibilities:**
  - Manage collection of Action objects
  - Track `current: Action` (persisted to behavior_action_state.json)
  - Methods: `find_by_name()`, `find_by_order()`, `next()`, `iterate()`, `navigate_to()`, `close_current()`, `execute_current()`
  - State persistence: `save_state()`, `load_state()`
- **Instantiated with:** Behavior, BaseActionsConfig, BehaviorConfig
- **Dependencies:** Action, BaseActionConfig, BehaviorConfig
- **Impact:** High - new collection class

### 3.2 Create BaseActionConfig Class
**File:** `src/bot/base_action_config.py`
- Extract action config loading
- Properties: `order`, `next_action`, `custom_class`, `instructions`
- Instantiated with: Actions, Workspace
- **Dependencies:** Workspace
- **Impact:** Medium - extract from existing code

### 3.3 Create Action Class
**File:** `src/bot/action.py`
- **Responsibilities:**
  - Represent single action in workflow
  - Properties: `instructions`, `action_class`, `order`
  - Method: `execute()` (delegates to action class)
- **Instantiated with:** Actions, BaseActionConfig, BehaviorConfig
- **Dependencies:** BaseActionConfig, BehaviorConfig
- **Impact:** Medium - extract from Behavior

### 3.4 Refactor BaseAction
**File:** `src/bot/base_action.py`
- **Update:** Constructor to accept Behavior, ActivityTracker
- **Keep:** `execute()`, `do_execute()`, activity tracking
- **Properties:** `workspace_directory`, `base_actions_directory`
- **Dependencies:** Behavior, ActivityTracker
- **Impact:** Low - constructor change

## Phase 4: Rules Collection

### 4.1 Create Rules Collection Class
**File:** `src/bot/rules.py`
- **Responsibilities:**
  - Manage collection of Rule objects
  - Methods: `find_by_name()`, `iterate()`
  - Property: `instructions` (returns Rule)
- **Instantiated with:** Behavior (or BotConfig for common rules)
- **Dependencies:** Rule
- **Impact:** Medium - new collection class

### 4.2 Refactor Rule Class
**File:** `src/bot/validate_rules_action.py`
- **Remove:** Scanner loading logic (extract to ScannerLoader)
- **Keep:** Properties: `description`, `examples`, `scanner`, `instruction`
- **Simplify:** Rule is data object, scanner loaded separately
- **Dependencies:** ScannerLoader (new service)
- **Impact:** Medium - extract scanner loading

### 4.3 Create ScannerLoader Service
**File:** `src/bot/scanner_loader.py`
- Extract scanner loading logic from Rule
- **Dependencies:** None (utility service)
- **Impact:** Low - extract from Rule




## Phase 6: Content Classes

### 6.1 Create Content Class
**File:** `src/bot/content.py`
- **Properties:** `knowledge`, `render_specs`, `synchronizers`, `instructions`
- **Instantiated with:** Behavior
- **Dependencies:** Knowledge, RenderSpec, Synchronizer
- **Impact:** Medium - new class

### 6.2 Create KnowledgeGraphSpec Class
**File:** `src/bot/knowledge_graph_spec.py`
- **Properties:** `output_path`, `output_filename`, `template_filename`
- **Impact:** Low - new class

### 6.3 Create KnowledgeGraphTemplate Class
**File:** `src/bot/knowledge_graph_template.py`
- **Property:** `schema`
- **Impact:** Low - new class

### 6.4 Create StoryGraphTemplate Class
**File:** `src/bot/story_graph_template.py`
- Extends KnowledgeGraphTemplate
- **Impact:** Low - new class

### 6.5 Create KnowledgeGraph Class
**File:** `src/bot/knowledge_graph.py`
- Base class for knowledge graphs
- **Impact:** Low - new class

### 6.6 Refactor StoryMap
**File:** `src/scanners/story_map.py`
- **Add:** `domain_concepts: DomainConcept` property
- **Update:** Constructor to accept Story Graph JSON (not from_bot classmethod)
- **Keep:** `epics()` property
- **Dependencies:** DomainConcept
- **Impact:** Medium - add domain concepts support

### 6.7 Add Domain Concepts to Epic/SubEpic
**File:** `src/scanners/story_map.py`
- **Add:** `domain_concepts: DomainConcept` property to Epic
- **Add:** `domain_concepts: DomainConcept` property to SubEpic
- **Dependencies:** DomainConcept
- **Impact:** Medium - add properties

### 6.8 Create DomainConcept Class
**File:** `src/scanners/domain_concept.py` (or use existing domain_concept_node.py)
- **Properties:** `name`, `description`, `responsibility`, `collaborators`
- **May inherit from:** DomainConcept (self-reference)
- **Dependencies:** DomainResponsibility
- **Impact:** Medium - create/refactor class

### 6.9 Create DomainResponsibility Class
**File:** `src/scanners/domain_responsibility.py`
- **Properties:** `name`, `descriptions`, `collaborates_with`
- **Impact:** Low - new class

### 6.10 Refactor Story Class
**File:** `src/scanners/story_map.py`
- **Change:** `scenarios: Scenario` (not Scenarios collection - direct list)
- **Add:** `test_file: Test` property
- **Impact:** Low - property change

### 6.11 Create RenderSpec Class
**File:** `src/bot/render_spec.py`
- **Properties:** `input`, `output`, `template`, `synchronizer`, `instructions`
- **Dependencies:** KnowledgeGraph, Template, Synchronizer
- **Impact:** Medium - extract from RenderOutputAction

### 6.12 Create Template Class
**File:** `src/bot/template.py`
- **Property:** `content`
- **Impact:** Low - new class

### 6.13 Create Synchronizer Class
**File:** `src/bot/synchronizer.py`
- Placeholder for now
- **Impact:** Low - new class

### 6.14 Refactor RenderOutputAction
**File:** `src/bot/render_output_action.py`
- **Add:** Properties: `render_specs`, `templates`, `synchronizers`
- **Update:** Use RenderSpec, Template, Synchronizer classes
- **Dependencies:** RenderSpec, Template, Synchronizer
- **Impact:** Medium - refactor to use new classes

### 6.15 Refactor BuildKnowledgeAction
**File:** `src/bot/build_knowledge_action.py`
- **Add:** Properties: `knowledge_graph_spec`, `knowledge_graph_template`, `rules`
- **Update:** Use KnowledgeGraphSpec, KnowledgeGraphTemplate classes
- **Dependencies:** KnowledgeGraphSpec, KnowledgeGraphTemplate, ValidateRulesAction
- **Impact:** Medium - refactor to use new classes

## Phase 7: Validation Classes

### 7.1 Create ValidationContext Class
**File:** `src/bot/validation_context.py`
- **Properties:** `rendered_outputs`, `clarification_file`, `planning_file`, `report_path`
- **Impact:** Low - new class

### 7.2 Create ValidationScope Class
**File:** `src/bot/validation_scope.py`
- **Properties:** `file_paths_scope`, `story_graph_scope`
- **Impact:** Low - new class

### 7.3 Refactor ValidateRulesAction
**File:** `src/bot/validate_rules_action.py`
- **Split into:**
  - `ValidateRulesAction` (orchestrator)
  - `ContentIdentifier` (identify content - already exists)
  - `ScannerExecutor` (execute scanners)
  - `ViolationCollector` (collect violations)
- **Add:** Properties: `rules`, `validation_context`, `validation_scope`
- **Method:** `collect_violations()`, `save_validation_report()`
- **Dependencies:** Rules, ValidationContext, ValidationScope, ScannerExecutor, ViolationCollector
- **Impact:** High - major split

### 7.4 Create ScannerExecutor Service
**File:** `src/bot/scanner_executor.py`
- Extract scanner execution logic from ValidateRulesAction
- **Dependencies:** Scanner, ValidationScope
- **Impact:** Medium - extract from ValidateRulesAction

### 7.5 Create ViolationCollector Service
**File:** `src/bot/violation_collector.py`
- Extract violation collection logic
- **Dependencies:** Violation
- **Impact:** Low - extract from ValidateRulesAction

### 7.6 Refactor Scanner Classes
**Files:** `src/scanners/scanner.py`, `story_scanner.py`, `test_scanner.py`, `code_scanner.py`
- **Add:** `rule: Rule` property
- **Update:** `scan()` method signature: `Scan: ValidationScope -> Violation`
- **Impact:** Low - property and method signature updates

### 7.7 Refactor Violation Class
**File:** `src/scanners/violation.py`
- **Change:** `validates_rule: Rule` (not `rule`)
- **Keep:** `message`, `line_number`, `location`, `severity`
- **Impact:** Low - property rename

### 7.8 Create ValidationReport Class
**File:** `src/bot/validation_report.py`
- **Properties:** `violations`, `validation_context`
- **Impact:** Low - new class

## Phase 8: Base Actions Classes

### 8.1 Create BaseActions Class
**File:** `src/bot/base_actions.py`
- **Responsibilities:**
  - Manage base actions configuration
  - Method: `find_folder()`
  - Property: `instructions_for()` (returns BaseInstructions)
- **Instantiated with:** Bot, BotConfig
- **Dependencies:** BaseActionConfig, BaseInstructions
- **Impact:** Medium - new class

### 8.2 Create BaseInstructions Class
**File:** `src/bot/base_instructions.py`
- **Property:** `instructions`
- **Instantiated with:** BaseActions
- **Dependencies:** Workspace
- **Impact:** Low - new class

## Phase 9: TriggerWords Class

### 9.1 Create TriggerWords Class
**File:** `src/bot/trigger_words.py`
- **Method:** `match_pattern()`
- **Property:** `priority`
- **Instantiated with:** Behavior, BehaviorConfig
- **Dependencies:** BehaviorConfig
- **Impact:** Medium - extract from Behavior

## Phase 10: Instructions Classes

### 10.1 Create Instructions Class
**File:** `src/bot/instructions.py`
- **Properties:** `base_instructions`, `behavior_instructions`
- **Dependencies:** BaseActions, Behavior
- **Impact:** Low - new class

### 10.2 Create MergedInstructions Class
**File:** `src/bot/merged_instructions.py`
- **Properties:** `base_instructions`, `render_instructions`
- **Dependencies:** BaseActions, RenderSpec
- **Impact:** Low - new class

## Phase 11: Utility Classes

### 11.1 Create Docs Class
**File:** `src/bot/docs.py`
- **Properties:** `clarification`, `planning`, `validation_report`
- **Instantiated with:** Behavior
- **Instantiates:** StoryMap
- **Dependencies:** Workspace, StoryMap
- **Impact:** Medium - new class

### 11.2 Create TestFiles Class
**File:** `src/bot/test_files.py`
- **Method:** `discover()`
- **Property:** `resolve_paths()` (uses FilePathResolver)
- **Instantiated with:** Workspace
- **Dependencies:** Workspace, FilePathResolver
- **Impact:** Low - new class

### 11.3 Create CodeFiles Class
**File:** `src/bot/code_files.py`
- **Method:** `discover()`, `filter_by_extension()`
- **Property:** `resolve_paths()` (uses FilePathResolver)
- **Instantiated with:** Workspace
- **Dependencies:** Workspace, FilePathResolver
- **Impact:** Low - new class

### 11.4 Create FilePathResolver Class
**File:** `src/bot/file_path_resolver.py`
- **Methods:** `resolve_file_paths()`, `normalize_paths()`
- **Instantiated with:** Workspace
- **Dependencies:** Workspace
- **Impact:** Low - new class

## Phase 12: Integration and Testing

### 12.1 Update All Action Classes
- Update constructors to match model
- Ensure all properties are exposed
- **Impact:** Medium - update all action classes

### 12.2 Update Workflow Integration
- Update Workflow class to work with Actions collection
- Ensure state persistence works with new structure
- **Impact:** Medium - update workflow

### 12.3 Update Tests
- Update all tests to use new structure
- Add tests for new collection classes
- **Impact:** High - comprehensive test updates

### 12.4 Update CLI/MCP Integration
- Update CLI and MCP code to use new structure
- **Impact:** Medium - update integrations

## Implementation Order Summary

**Priority 1 (Foundation):**
1. BotConfig
2. Workspace (refactor)
3. Behaviors collection
4. Bot refactor

**Priority 2 (Core Structure):**
5. BehaviorConfig
6. Behavior refactor
7. Actions collection
8. Action classes
9. BaseActionConfig

**Priority 3 (Supporting Classes):**
10. Rules collection
11. Rule refactor
12. ScannerLoader
13. Guardrails classes
14. Content classes

**Priority 4 (Validation):**
15. Validation classes
16. ValidateRulesAction split

**Priority 5 (Remaining):**
17. BaseActions classes
18. TriggerWords
19. Instructions classes
20. Utility classes

**Priority 6 (Integration):**
21. Update all integrations
22. Update tests
23. Final verification

## Notes

- Each phase should be completed with tests before moving to next phase
- Maintain backward compatibility where possible during transition
- Use feature flags if needed for gradual rollout
- Document breaking changes clearly
- Update model documentation as code changes