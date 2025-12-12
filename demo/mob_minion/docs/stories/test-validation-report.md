# Validation Report - 7 Tests

**Generated:** 2025-12-11 23:38:46
**Project:** mob_minion
**Behavior:** 7_tests
**Action:** validate_rules

## Summary

Validated story map and domain model against **36 validation rules**.

## Content Validated

- **Clarification:** `clarification.json`
- **Rendered Outputs:**
  - `mob-minion-domain-model-description.md`
  - `mob-minion-domain-model-diagram.md`
  - `story-graph.json`

## Validation Rules Checked

### Rule: Maintain Verb Noun Consistency
**Description:** Maintain verb-noun consistency from epic to feature to story to scenario

### Rule: Map Sequential Spine Vs Optional Paths
**Description:** When mapping stories, carefully distinguish between sequential spine (essential path) and optional paths, alternate routes, or additional functionality that is not strictly essential. Sequential stories form the mandatory flow; optional stories are alternatives, enhancements, or non-essential features.

### Rule: Stories Developed And Tested In Days
**Description:** Write stories that can be developed and tested in a matter of days

### Rule: Story Names Must Follow Verb Noun Format
**Description:** CRITICAL: Story names MUST follow Verb-Noun format (e.g., 'Move To Mob Leaders Turn', 'Determines Target from Strategy', 'Initiate Mob Attack'), and include italicized description showing component interactions (e.g., '*Combat Tracker moves to any mob member's turn, auto moves to mob leader's turn*'). The story name should be concise and action-oriented, while the description shows the component-to-component interactions.

### Rule: Use Active Behavioral Language
**Description:** Use active behavioral language with action verbs. Describe behaviors, not tasks or capabilities.

### Rule: Use Verb Noun Format For Story Elements
**Description:** Use verb-noun format for all story elements (epic names, feature names, story titles)

### Rule: Bug Fix Test First
**Description:** When production code breaks, ALWAYS follow the test-first workflow: write/modify failing test, verify failure, fix code, verify success, then test in production. Never fix bugs directly without a failing test first.

### Rule: Business Readable Test Names
**Description:** Test names must read like plain English business language. Use domain language stakeholders understand, not technical jargon. Test names should read naturally when spoken aloud. Describe WHAT happens (behavior), not HOW it works (implementation). Combines BDD Rule 1 (Business Readable Language) with pytest orchestrator pattern.

### Rule: Call Production Code Directly
**Description:** Call production code directly - tests drive production code creation through RED-GREEN-REFACTOR. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries (file I/O, network, APIs) when necessary. Separate business logic from side effects.

### Rule: Consistent Vocabulary
**Description:** Use ONE word per concept across entire test suite. Pick consistent vocabulary for common operations: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Inconsistent vocabulary confuses readers and makes codebase harder to navigate. From Clean Code Rule 2.2 and BDD Rule 1.

### Rule: Cover All Behavior Paths
**Description:** Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent and can run in any order. From BDD Rule 3 (Comprehensive and Brief Coverage).

### Rule: Create Parameterized Tests For Scenarios
**Description:** If scenarios have tests in stories (Examples tables with multiple test cases), then create parameterized tests using @pytest.mark.parametrize. Each row in the Examples table becomes a test case. Don't write single test methods that only test one example - iterate over all examples from the scenario file.

### Rule: Define Fixtures In Test File
**Description:** Define fixtures in the test file, not in separate conftest.py. Use pytest fixtures for shared setup. Truly reusable fixtures (file operations, location helpers) belong in agents/base/src/conftest.py.

### Rule: Design Api Through Failing Tests
**Description:** Write tests against the REAL expected API (not dummy variables or placeholders) BEFORE implementing code. Tests MUST fail initially because the API doesn't exist yet. This failure reveals the complete API design including parameter objects, config setup, dependencies, and return values. Set up real test data (files, directories, objects) and call the real API. Only mock I/O boundaries (file access, network, database) and only when explicitly necessary. The failing test serves as executable API documentation.

### Rule: Helpers Inline Not Shared
**Description:** Helper functions must be inline in test file, not in separate shared helper file

### Rule: Helper Extraction And Reuse
**Description:** Extract duplicate test setup to reusable helper functions and factory functions. Keep test bodies focused on specific behavior being tested. Balance shared context with test-specific setup. Avoid duplication through helper extraction. From BDD Rules 8.3 (Helper Extraction) and 4 (Balance Context Sharing with Localization).

### Rule: Match Specification Scenarios
**Description:** CRITICAL: Test docstrings and assertions must match specification scenarios exactly. Test names and docstrings describe the behavior from specification. Assertions verify exactly what the scenario states - no more, no less. Use exact variable names and terminology from specification.

### Rule: Mock Only Boundaries
**Description:** Mock ONLY at architectural boundaries: external APIs, network calls, uncontrollable services. DON'T mock internal business logic, classes under test, or file operations (use temp files). Mocking internal code defeats the purpose of tests. From BDD Rule 8.2 (Proper Mocking).

### Rule: No Fallbacks In Tests
**Description:** Tests must fail if a fallback or default branch is executed. Every assertion should cover the explicitly intended path so that regressions do not hide behind fallback/default handling.

### Rule: Production Code Api Design
**Description:** PRODUCTION CODE RULE: Object-oriented API design principles from BDD. Objects initialize automatically, manage their own state (ask don't tell), use properties over methods when appropriate, and provide simple direct verb names. From BDD Rules 11.1-11.4.

*... and 16 more rules*

## Violations Found

**Total Violations:** 71

### Maintain Verb Noun Consistency: 3 violation(s)

- 🔴 **ERROR** - `epics[0].sub_epics[0].story_groups[0].stories[2].name`: Story name "Display Mob Creation Confirmation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[2].story_groups[0].stories[0].name`: Story name "Display Available Strategies" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[4].story_groups[0].stories[2].name`: Story name "Configure Spawned Mob" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")

### Map Sequential Spine Vs Optional Paths: 7 violation(s)

- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements

### Stories Developed And Tested In Days: 22 violation(s)

- 🟡 **WARNING** - `epics[0].sub_epics[0].name`: Sub-epic "Create Mob" has 3 3 nested sub-epics/stories (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[0].story_groups[0].stories[0].acceptance_criteria`: Story "Select Multiple Tokens" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[0].story_groups[0].stories[1].acceptance_criteria`: Story "Group Tokens Into Mob" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[0].story_groups[0].stories[2].acceptance_criteria`: Story "Display Mob Creation Confirmation" has 4 4 acceptance criteria (should be 5-9)
- 🔴 **ERROR** - `epics[0].sub_epics[1].name`: Sub-epic "Edit Mob" has 2 2 nested sub-epics/stories (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[1].story_groups[0].stories[0].acceptance_criteria`: Story "Add Tokens To Mob" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[1].story_groups[0].stories[1].acceptance_criteria`: Story "Remove Tokens From Mob" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[0].stories[0].acceptance_criteria`: Story "Display Available Strategies" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[0].stories[1].acceptance_criteria`: Story "Assign Strategy To Mob" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[1].stories[0].acceptance_criteria`: Story "Select Attack Most Powerful Target Strategy" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[1].stories[1].acceptance_criteria`: Story "Select Attack Weakest Target Strategy" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[1].stories[2].acceptance_criteria`: Story "Select Defend Leader Strategy" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[2].story_groups[1].stories[3].acceptance_criteria`: Story "Select Attack Most Damaged Person Strategy" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[3].story_groups[0].stories[0].acceptance_criteria`: Story "Click Mob Token To Command" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[3].story_groups[0].stories[1].acceptance_criteria`: Story "Determine Target From Strategy" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[3].story_groups[0].stories[2].acceptance_criteria`: Story "Execute Attack Action" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[3].story_groups[1].stories[0].acceptance_criteria`: Story "Move To Target For Melee Attack" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[3].story_groups[1].stories[1].acceptance_criteria`: Story "Execute Area Attack" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[4].name`: Sub-epic "Spawn Mob From Template" has 3 3 nested sub-epics/stories (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[4].story_groups[0].stories[0].acceptance_criteria`: Story "Select Mob Template" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[4].story_groups[0].stories[1].acceptance_criteria`: Story "Spawn Mob From Actors" has 4 4 acceptance criteria (should be 5-9)
- 🟡 **WARNING** - `epics[0].sub_epics[4].story_groups[0].stories[2].acceptance_criteria`: Story "Configure Spawned Mob" has 4 4 acceptance criteria (should be 5-9)

### Story Names Must Follow Verb Noun Format: 3 violation(s)

- 🔴 **ERROR** - `epics[0].sub_epics[0].story_groups[0].stories[2].name`: Story name "Display Mob Creation Confirmation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[2].story_groups[0].stories[0].name`: Story name "Display Available Strategies" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[4].story_groups[0].stories[2].name`: Story name "Configure Spawned Mob" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")

### Use Active Behavioral Language: 2 violation(s)

- 🔴 **ERROR** - `epics[0].sub_epics[0].story_groups[0].stories[2].name`: Story name "Display Mob Creation Confirmation" uses capability noun - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")
- 🔴 **ERROR** - `epics[0].sub_epics[3].story_groups[0].stories[2].name`: Story name "Execute Attack Action" uses capability noun - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")

### Use Verb Noun Format For Story Elements: 3 violation(s)

- 🔴 **ERROR** - `epics[0].sub_epics[0].story_groups[0].stories[2].name`: Story name "Display Mob Creation Confirmation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[2].story_groups[0].stories[0].name`: Story name "Display Available Strategies" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - `epics[0].sub_epics[4].story_groups[0].stories[2].name`: Story name "Configure Spawned Mob" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")

### Business Readable Test Names: 1 violation(s)

- 🔴 **ERROR** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test name "test_system_executes_attack_for_all_minions_in_mob" contains technical jargon "execute" - use business-readable domain language instead

### Call Production Code Directly: 1 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Line 210 has commented-out code - call production code directly, even if API doesn't exist yet

### Match Specification Scenarios: 2 violation(s)

- 🔵 **INFO** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Line 157 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Line 178 uses generic variable name "result" - use exact variable names from specification

### Production Code Api Design: 1 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Line 210 has commented-out code - call production code directly, even if API doesn't exist yet

### Tests Must Match Story Graph Exactly: 8 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_selects_multiple_tokens_successfully" is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_groups_tokens_into_mob_successfully" is approximately 42 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_confirms_mob_creation" is approximately 40 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_cancels_mob_creation" is approximately 36 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_game_master_clicks_mob_token_to_command_mob" is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_determines_target_using_assigned_strategy" is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_uses_default_strategy_when_no_strategy_assigned" is approximately 25 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_executes_attack_for_all_minions_in_mob" is approximately 33 lines - should be under 20 lines (extract to helpers)

### Use Class Based Organization: 8 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_selects_multiple_tokens_successfully" is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_groups_tokens_into_mob_successfully" is approximately 42 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_confirms_mob_creation" is approximately 40 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Test method "test_game_master_cancels_mob_creation" is approximately 36 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_game_master_clicks_mob_token_to_command_mob" is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_determines_target_using_assigned_strategy" is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_uses_default_strategy_when_no_strategy_assigned" is approximately 25 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Test method "test_system_executes_attack_for_all_minions_in_mob" is approximately 33 lines - should be under 20 lines (extract to helpers)

### Use Descriptive Function Names: 7 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_execute_mob_actions.py`: Helper function "__init__" contains abbreviations - use full descriptive words

### Use Exact Variable Names: 2 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Variable "result" uses generic name - use exact domain concept name from scenario/AC

### Use Real Implementations: 1 violation(s)

- 🟡 **WARNING** - `C:\dev\augmented-teams\demo\mob_minion\tests\test_create_mob.py`: Line 210 has commented-out code - call production code directly, even if API doesn't exist yet

## Validation Instructions

The following validation steps were performed:

1. **MANDATORY: Before validating any content, you MUST load and review the project's context files:**
2. 1. Load `{project_area}/docs/stories/clarification.json` - Contains key questions and evidence (generated file)
3. 2. Load `{project_area}/docs/stories/planning.json` - Contains assumptions and decisions (generated file)
4. 3. Load `{project_area}/docs/context/input.txt` (or similar) - Original input/source material if needed for validation (original context)
5. 
6. **CRITICAL: File locations:**
7. - **Generated files:** `{project_area}/docs/stories/clarification.json`, `{project_area}/docs/stories/planning.json`
8. - **Original input:** `{project_area}/docs/context/input.txt` and other original context files
9. 
10. These files contain critical requirements, decisions, and context that MUST be checked against during validation.
*... and 232 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\demo\mob_minion\docs\stories\validation-report.md`
