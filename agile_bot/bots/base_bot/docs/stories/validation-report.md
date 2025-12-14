# Validation Report - 7 Write Tests

**Generated:** 2025-12-13 18:33:10
**Project:** base_bot
**Behavior:** 7_write_tests
**Action:** validate_rules

## Summary

Validated story map and domain model against **37 validation rules**.

## Content Validated

- **Planning:** `planning.json`
- **Rendered Outputs:**
  - `build-bot-domain-model-description.md`
  - `build-bot-domain-model-diagram.md`
  - `story-graph.json`
  - `story-map-increments.md`
- **Test Files Scanned:**
  - `test\test_base_action.py`
  - `test\test_bot_behavior_exceptions.py`
  - `test\test_bot_execute_behavior.py`
  - `test\test_build_agile_bots_helpers.py`
  - `test\test_build_knowledge.py`
  - `test\test_cli_exceptions.py`
  - `test\test_close_current_action.py`
  - `test\test_complete_workflow_integration.py`
  - `test\test_decide_planning_criteria.py`
  - `test\test_gather_context.py`
  - `test\test_generate_bot_server_and_tools.py`
  - `test\test_helpers.py`
  - `test\test_init_project.py`
  - `test\test_invoke_bot_cli.py`
  - `test\test_invoke_bot_tool.py`
  - `test\test_mcp_generator_exceptions.py`
  - `test\test_render_output.py`
  - `test\test_restart_mcp_server.py`
  - `test\test_router_exceptions.py`
  - `test\test_utils.py`
  - `test\test_validate_knowledge_and_content_against_rules.py`
  - `test\test_workflow_action_sequence.py`
  - **Total:** 22 test file(s)

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

*... and 17 more rules*

## Violations Found

**Total Violations:** 1391
- **File-by-File Violations:** 1385
- **Cross-File Violations:** 6

### File-by-File Violations (Pass 1)

These violations were detected by scanning each file individually.

#### Maintain Verb Noun Consistency: 23 violation(s)

- 🔴 **ERROR** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[0].name): Sub_epic name "Init Project" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[3].name): Story name "Activity Tracker Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[4].name): Story name "Workflow Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[5].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[5].name): Story name "Activity Tracking Location" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[3].story_groups[1].stories[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[3].story_groups[1].stories[0].name): Story name "Load+ Inject Content Into Instructions" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb-noun pattern (actor prefix) - use verb-noun format without actor (e.g., "Places Order" not "Customer places order")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[3].name): Story name "Scanner Detects Violations Using Regex Patterns" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[8].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[8].name): Story name "Scanner Detects Violations Using AST Parsing" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[12].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[12].name): Story name "Scanner Detects Violations Using File Structure Analysis" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")

#### Map Sequential Spine Vs Optional Paths: 18 violation(s)

- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements

#### Stories Developed And Tested In Days: 5 violation(s)

- 🔴 **ERROR** - [`epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[0].name): Epic "Build Agile Bots" has 2 2 sub-epics/story groups (should be 5-9)
- 🔴 **ERROR** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[0].sub_epics[1].name): Sub-epic "Generate CLI" has 2 2 nested sub-epics/stories (should be 5-9)
- 🟡 **WARNING** - [`epics[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].name): Epic "Invoke Bot" has 4 4 sub-epics/story groups (should be 5-9)
- 🟡 **WARNING** - [`epics[2].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[1].name): Sub-epic "Decide Planning Criteria Action" has 4 4 nested sub-epics/stories (should be 5-9)
- 🔴 **ERROR** - [`epics[2].sub_epics[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].name): Sub-epic "Validate Knowledge & Content Against Rules" has 17 17 nested sub-epics/stories (should be 5-9)

#### Story Names Must Follow Verb Noun Format: 23 violation(s)

- 🔴 **ERROR** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[0].name): Sub_epic name "Init Project" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[3].name): Story name "Activity Tracker Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[4].name): Story name "Workflow Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[5].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[5].name): Story name "Activity Tracking Location" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[3].story_groups[1].stories[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[3].story_groups[1].stories[0].name): Story name "Load+ Inject Content Into Instructions" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb-noun pattern (actor prefix) - use verb-noun format without actor (e.g., "Places Order" not "Customer places order")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[3].name): Story name "Scanner Detects Violations Using Regex Patterns" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[8].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[8].name): Story name "Scanner Detects Violations Using AST Parsing" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[12].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[12].name): Story name "Scanner Detects Violations Using File Structure Analysis" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")

#### Use Verb Noun Format For Story Elements: 23 violation(s)

- 🔴 **ERROR** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[0].name): Sub_epic name "Init Project" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[3].name): Story name "Activity Tracker Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[4].name): Story name "Workflow Guard" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].sub_epics[3].story_groups[0].stories[5].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].story_groups[0].stories[5].name): Story name "Activity Tracking Location" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[3].story_groups[1].stories[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[3].story_groups[1].stories[0].name): Story name "Load+ Inject Content Into Instructions" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb-noun pattern (actor prefix) - use verb-noun format without actor (e.g., "Places Order" not "Customer places order")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[1].name): Story name "System Discovers Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[2].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[2].name): Story name "System Runs Scanners After Build Knowledge" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[3].name): Story name "Scanner Detects Violations Using Regex Patterns" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[4].name): Story name "System Collects Violations from All Scanners" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[6].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[6].name): Story name "System Loads Scanner Classes" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[7].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[7].name): Story name "System Runs Scanners After Render Output" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[8].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[8].name): Story name "Scanner Detects Violations Using AST Parsing" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[9].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[9].name): Story name "System Reports Violations with Location Context" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" contains actor prefix (e.g., "Customer") - use verb-noun format without actor
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[11].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[11].name): Story name "System Runs Scanners Before AI Validation" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[4].story_groups[1].stories[12].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].story_groups[1].stories[12].name): Story name "Scanner Detects Violations Using File Structure Analysis" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")

#### Business Readable Test Names: 61 violation(s)

- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:144): Test name "test_seamless_transition_from_build_knowledge_to_validate_rules" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840): Test name "test_all_template_variables_are_replaced_in_instructions" contains technical jargon "var" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:872): Test name "test_behavior_updates_existing_story_graph_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:951): Test name "test_scenario_default_test_method" contains technical jargon "method" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:966): Test name "test_story_default_test_class" contains technical jargon "class" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:33): Test name "test_cli_raises_exception_when_parameter_description_cannot_be_inferred" contains technical jargon "param" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:233): Test name "test_bot_class_has_close_current_action_method" contains technical jargon "method" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231): Test name "test_save_planning_data_when_parameters_provided" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253): Test name "test_preserve_existing_planning_data_when_saving" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:277): Test name "test_skip_saving_when_no_planning_parameters_provided" contains technical jargon "param" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:454): Test name "test_action_handles_malformed_guardrails_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476): Test name "test_save_clarification_data_when_parameters_provided" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505): Test name "test_preserve_existing_clarification_data_when_saving" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:532): Test name "test_skip_saving_when_no_clarification_parameters_provided" contains technical jargon "param" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:719): Test name "test_generator_fails_when_bot_config_missing" contains technical jargon "config" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:739): Test name "test_generator_fails_when_bot_config_malformed" contains technical jargon "config" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920): Test name "test_server_publishes_tool_catalog_with_metadata" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:973): Test name "test_server_handles_initialization_failure" contains technical jargon "init" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:228): Test name "test_bot_directory_from_environment_variable" contains technical jargon "var" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:242): Test name "test_workspace_directory_from_environment_variable" contains technical jargon "var" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:256): Test name "test_workspace_directory_supports_legacy_working_dir_variable" contains technical jargon "var" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332): Test name "test_entry_point_bootstraps_from_agent_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355): Test name "test_environment_variable_takes_precedence_over_agent_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Test name "test_missing_agent_json_with_preconfig_env_var_works" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419): Test name "test_bot_initializes_with_bootstrapped_directories" contains technical jargon "init" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476): Test name "test_bot_config_loaded_from_bot_directory" contains technical jargon "config" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529): Test name "test_multiple_calls_use_cached_env_vars" contains technical jargon "call" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:62): Test name "test_bot_config" contains technical jargon "config" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241): Test name "test_tool_invokes_behavior_action_when_called" contains technical jargon "invoke" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264): Test name "test_tool_routes_to_correct_behavior_action_method" contains technical jargon "method" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438): Test name "test_action_called_directly_saves_workflow_state" contains technical jargon "call" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:186): Test name "test_seamless_transition_from_validate_rules_to_render_output" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192): Test name "test_render_output_action_executes_successfully" contains technical jargon "execute" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223): Test name "test_all_template_variables_are_replaced_in_instructions" contains technical jargon "var" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268): Test name "test_render_configs_format_includes_all_fields" contains technical jargon "config" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:602): Test name "test_track_activity_when_validate_rules_action_starts" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622): Test name "test_track_activity_when_validate_rules_action_completes" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658): Test name "test_track_multiple_validate_rules_invocations_across_behaviors" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:718): Test name "test_validate_rules_marks_workflow_as_complete" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:735): Test name "test_validate_rules_does_not_inject_next_action_instructions" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:801): Test name "test_workflow_does_not_transition_after_validate_rules" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836): Test name "test_validate_rules_returns_instructions_with_rules_as_context" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948): Test name "test_validate_rules_provides_report_path_for_saving_validation_report" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024): Test name "test_scanner_discovery_extracts_metadata_and_registers_scanners" contains technical jargon "data" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1181): Test name "test_validate_rules_raises_exception_when_story_graph_not_found" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1199): Test name "test_validate_rules_raises_exception_when_story_graph_invalid_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Test name "test_validate_rules_respects_scope" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Test name "test_validate_rules_scope_extraction" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936): Test name "test_validate_rules_with_test_file_scope_parameter" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003): Test name "test_validate_rules_with_test_files_scope_parameter" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073): Test name "test_validate_rules_verifies_test_files_passed_to_scanner" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812): Test name "test_validate_code_files_action_accepts_test_files_parameter" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840): Test name "test_validate_code_files_action_validates_each_file_from_parameters" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Test name "test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2917): Test name "test_validate_code_files_action_works_for_tests_behavior" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946): Test name "test_validate_code_files_action_accepts_code_files_parameter" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2970): Test name "test_validate_code_files_action_works_for_code_behavior" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2989): Test name "test_validate_code_files_action_returns_early_when_no_files_provided" contains technical jargon "validate" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:402): Test name "test_behavior_requires_actions_workflow_json_no_fallback" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Test name "test_behavior_loads_from_actions_workflow_json" contains technical jargon "json" - use business-readable domain language instead
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594): Test name "test_workflow_transitions_built_correctly_from_actions_workflow_json" contains technical jargon "json" - use business-readable domain language instead

#### Call Production Code Directly: 79 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:19): Line 19 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:173): Line 173 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:22): Line 22 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:211): Line 211 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:298): Line 298 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:361): Line 361 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:445): Line 445 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:20): Line 20 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:376): Line 376 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:377): Line 377 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:393): Line 393 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:401): Line 401 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:737): Line 737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:757): Line 757 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:794): Line 794 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:884): Line 884 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:886): Line 886 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:947): Line 947 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:965): Line 965 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1029): Line 1029 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1117): Line 1117 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:183): Line 183 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:229): Line 229 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:251): Line 251 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:293): Line 293 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:43): Line 43 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:41): Line 41 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:52): Line 52 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:63): Line 63 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:69): Line 69 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:82): Line 82 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:93): Line 93 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:101): Line 101 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:153): Line 153 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:243): Line 243 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:265): Line 265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:277): Line 277 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:452): Line 452 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:457): Line 457 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:472): Line 472 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:22): Line 22 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:23): Line 23 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:27): Line 27 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:23): Line 23 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:33): Line 33 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:483): Line 483 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:490): Line 490 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:493): Line 493 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:576): Line 576 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:889): Line 889 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1075): Line 1075 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1082): Line 1082 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1089): Line 1089 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1096): Line 1096 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1110): Line 1110 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1553): Line 1553 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2156): Line 2156 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2265): Line 2265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2272): Line 2272 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2273): Line 2273 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2355): Line 2355 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2363): Line 2363 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2596): Line 2596 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2597): Line 2597 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2713): Line 2713 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2731): Line 2731 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2737): Line 2737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2751): Line 2751 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2758): Line 2758 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2766): Line 2766 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2774): Line 2774 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2776): Line 2776 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:218): Line 218 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:308): Line 308 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:519): Line 519 has commented-out code - call production code directly, even if API doesn't exist yet

#### Helpers Inline Not Shared: 28 violation(s)

- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:11): Line 11 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:14): Line 14 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:11): Line 11 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:36): Line 36 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:16): Line 16 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:218): Line 218 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:17): Line 17 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:18): Line 18 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:15): Line 15 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:17): Line 17 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:12): Line 12 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:13): Line 13 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:103): Line 103 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:113): Line 113 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:133): Line 133 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:190): Line 190 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:21): Line 21 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:22): Line 22 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:22): Line 22 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:23): Line 23 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:12): Line 12 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:31): Line 31 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:21): Line 21 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:422): Line 422 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1046): Line 1046 imports helpers from "agile_bot.bots.base_bot.test.test_build_agile_bots_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1190): Line 1190 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1208): Line 1208 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:12): Line 12 imports helpers from "agile_bot.bots.base_bot.test.test_helpers" - helpers must be inline in test file, not imported from separate helper modules

#### Helper Extraction And Reuse: 2 violation(s)

- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:119): Duplicate code detected: functions then_planning_data_contains_discovery_scope, then_planning_data_contains_discovery_scope have identical bodies - extract to shared function
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:123): Duplicate code detected: functions then_planning_data_contains_shape_drill_down, then_planning_data_contains_shape_drill_down have identical bodies - extract to shared function

#### Match Specification Scenarios: 119 violation(s)

- 🔵 **INFO** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:150): Line 150 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:268): Line 268 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:289): Line 289 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:304): Line 304 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:318): Line 318 uses generic variable name "result" - use exact variable names from specification
- 🟡 **WARNING** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:80): Test method [test_bot_raises_exception_when_behavior_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:80) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:93): Test method [test_behavior_raises_exception_when_actions_workflow_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:93) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:128): Test method [test_track_activity_when_build_knowledge_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:128) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:131): Test method [test_track_activity_when_build_knowledge_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:131) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:144): Test method [test_seamless_transition_from_build_knowledge_to_validate_rules](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:144) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:147): Test method [test_workflow_state_captures_build_knowledge_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:147) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:778): Test method [test_action_injects_knowledge_graph_template](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:778) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:790): Test method [test_action_raises_error_when_template_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:790) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:872): Test method [test_behavior_updates_existing_story_graph_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:872) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:913): Test method [test_story_map_loads_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:913) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:917): Test method [test_epic_has_sub_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:917) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:923): Test method [test_sub_epic_has_story_groups](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:923) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:930): Test method [test_story_group_has_stories](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:930) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:937): Test method [test_story_has_properties](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:937) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:941): Test method [test_story_has_scenarios](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:941) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:946): Test method [test_scenario_has_properties](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:946) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:951): Test method [test_scenario_default_test_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:951) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:956): Test method [test_story_has_scenario_outlines](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:956) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:961): Test method [test_scenario_outline_has_examples](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:961) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:966): Test method [test_story_default_test_class](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:966) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:970): Test method [test_story_map_walk_traverses_all_nodes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:970) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:976): Test method [test_map_location_for_epic](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:976) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:981): Test method [test_map_location_for_sub_epic](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:981) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:986): Test method [test_map_location_for_story](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:986) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:991): Test method [test_scenario_map_location](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:991) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:996): Test method [test_scenario_outline_map_location](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:996) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1001): Test method [test_from_bot_loads_story_graph](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1001) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1010): Test method [test_from_bot_with_path](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1010) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1018): Test method [test_from_bot_raises_when_file_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1018) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:33): Test method [test_cli_raises_exception_when_parameter_description_cannot_be_inferred](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:33) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138): Test method [test_close_current_action_marks_complete_and_transitions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:162): Test method [test_close_action_at_final_action_stays_at_final](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:162) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:180): Test method [test_close_final_action_transitions_to_next_behavior](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:180) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:198): Test method [test_close_action_saves_to_completed_actions_list](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:198) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:213): Test method [test_close_handles_action_already_completed_gracefully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:213) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:233): Test method [test_bot_class_has_close_current_action_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:233) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130): Test method [test_complete_workflow_end_to_end](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🔵 **INFO** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:152): Line 152 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:167): Line 167 uses generic variable name "result" - use exact variable names from specification
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:162): Test method [test_track_activity_when_planning_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:162) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:165): Test method [test_track_activity_when_planning_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:165) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:183): Test method [test_seamless_transition_from_planning_to_build_knowledge](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:183) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:186): Test method [test_workflow_state_captures_planning_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:186) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:197): Test method [test_action_injects_decision_criteria_and_assumptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:197) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:211): Test method [test_action_uses_base_planning_when_guardrails_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:211) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:425): Test method [test_action_injects_questions_and_evidence](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:425) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:441): Test method [test_action_uses_base_instructions_when_guardrails_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:441) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:454): Test method [test_action_handles_malformed_guardrails_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:454) missing docstring - should match specification scenario format
- 🔵 **INFO** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:300): Line 300 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:888): Line 888 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:125): Line 125 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:126): Line 126 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:287): Line 287 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:290): Line 290 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:176): Line 176 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:178): Line 178 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:337): Line 337 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:383): Line 383 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:429): Line 429 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:467): Line 467 uses generic variable name "result" - use exact variable names from specification
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:62): Test method [test_bot_config](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:62) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:259): Line 259 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:288): Line 288 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:348): Line 348 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:369): Line 369 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:393): Line 393 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:413): Line 413 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:433): Line 433 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:473): Line 473 uses generic variable name "result" - use exact variable names from specification
- 🟡 **WARNING** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:13): Test method [test_mcp_generator_raises_exception_when_base_actions_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:13) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:126): Test method [test_track_activity_when_render_output_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:126) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:129): Test method [test_track_activity_when_render_output_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:129) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:140): Test method [test_track_multiple_render_output_invocations_across_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:140) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:186): Test method [test_seamless_transition_from_validate_rules_to_render_output](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:186) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:189): Test method [test_workflow_state_captures_render_output_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:189) missing docstring - should match specification scenario format
- 🟡 **WARNING** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:93): Test method [test_find_mcp_server_processes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:93) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:15): Test method [test_router_raises_exception_when_state_file_does_not_exist](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:15) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:28): Test method [test_router_raises_exception_when_no_completed_actions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:28) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:46): Test method [test_router_raises_exception_when_unknown_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:46) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Test method [test_validate_rules_respects_scope](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Test method [test_validate_rules_scope_extraction](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812): Test method [test_validate_code_files_action_accepts_test_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840): Test method [test_validate_code_files_action_validates_each_file_from_parameters](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Test method [test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2917): Test method [test_validate_code_files_action_works_for_tests_behavior](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2917) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946): Test method [test_validate_code_files_action_accepts_code_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2970): Test method [test_validate_code_files_action_works_for_code_behavior](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2970) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2989): Test method [test_validate_code_files_action_returns_early_when_no_files_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2989) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:730): Line 730 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:874): Line 874 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:973): Line 973 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1857): Line 1857 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1985): Line 1985 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2064): Line 2064 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2138): Line 2138 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2545): Line 2545 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2835): Line 2835 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2861): Line 2861 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2906): Line 2906 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2933): Line 2933 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2965): Line 2965 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2984): Line 2984 uses generic variable name "result" - use exact variable names from specification
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2998): Line 2998 uses generic variable name "result" - use exact variable names from specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:213): Test method [test_workflow_determines_next_action_from_current_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:213) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:229): Test method [test_workflow_starts_at_first_action_when_no_completed_actions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:229) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:241): Test method [test_workflow_uses_current_action_when_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:241) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:257): Test method [test_workflow_falls_back_to_completed_actions_when_current_action_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:257) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:290): Test method [test_workflow_starts_at_first_action_when_no_workflow_state_file_exists](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:290) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:304): Test method [test_workflow_out_of_order_navigation_removes_completed_actions_after_target](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:304) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354): Test method [test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:402): Test method [test_behavior_requires_actions_workflow_json_no_fallback](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:402) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Test method [test_behavior_loads_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474): Test method [test_different_behaviors_can_have_different_action_orders](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594): Test method [test_workflow_transitions_built_correctly_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594) docstring should follow scenario format (GIVEN/WHEN/THEN) to match specification

#### No Fallbacks In Tests: 1 violation(s)

- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:918): Line 918 uses fallback/default value - tests should use explicit test data, not fallbacks

#### Production Code Api Design: 79 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:19): Line 19 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:173): Line 173 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:22): Line 22 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:211): Line 211 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:298): Line 298 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:361): Line 361 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:445): Line 445 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:20): Line 20 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:376): Line 376 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:377): Line 377 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:393): Line 393 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:401): Line 401 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:737): Line 737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:757): Line 757 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:794): Line 794 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:884): Line 884 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:886): Line 886 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:947): Line 947 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:965): Line 965 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1029): Line 1029 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1117): Line 1117 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:183): Line 183 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:229): Line 229 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:251): Line 251 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:293): Line 293 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:43): Line 43 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:41): Line 41 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:52): Line 52 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:63): Line 63 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:69): Line 69 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:82): Line 82 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:93): Line 93 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:101): Line 101 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:153): Line 153 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:243): Line 243 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:265): Line 265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:277): Line 277 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:452): Line 452 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:457): Line 457 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:472): Line 472 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:22): Line 22 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:23): Line 23 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:27): Line 27 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:23): Line 23 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:33): Line 33 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:483): Line 483 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:490): Line 490 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:493): Line 493 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:576): Line 576 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:889): Line 889 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1075): Line 1075 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1082): Line 1082 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1089): Line 1089 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1096): Line 1096 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1110): Line 1110 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1553): Line 1553 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2156): Line 2156 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2265): Line 2265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2272): Line 2272 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2273): Line 2273 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2355): Line 2355 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2363): Line 2363 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2596): Line 2596 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2597): Line 2597 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2713): Line 2713 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2731): Line 2731 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2737): Line 2737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2751): Line 2751 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2758): Line 2758 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2766): Line 2766 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2774): Line 2774 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2776): Line 2776 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:218): Line 218 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:308): Line 308 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:519): Line 519 has commented-out code - call production code directly, even if API doesn't exist yet

#### Production Code Single Responsibility: 54 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:210): Function "then_error_mentions_template_or_knowledge_graph" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:244): Function "given_knowledge_graph_config_and_template_created" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:268): Function "when_build_knowledge_action_loads_and_merges_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:309): Function "when_sub_epic_and_story_group_retrieved" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:476): Function "when_build_knowledge_action_loads_and_injects_all_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:558): Function "given_environment_and_knowledge_graph_setup" appears to have multiple responsibilities - split into separate functions
- 🔵 **INFO** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:898): Class "TestLoadStoryGraphIntoMemory" has 21 methods - consider if it has multiple responsibilities
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800): Function "test_action_loads_and_merges_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:93): Function "when_user_closes_current_action_and_transitions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138): Function "test_close_current_action_marks_complete_and_transitions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:65): Function "when_action_is_closed_and_transitioned" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:107): Function "given_bot_name_and_behaviors_setup" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:117): Function "then_action_result_has_correct_behavior_and_action" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:28): Function "given_planning_assumptions_and_criteria" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:34): Function "given_planning_parameters_with_decisions_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:54): Function "given_discovery_planning_decisions_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:60): Function "given_expected_planning_decisions_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:88): Function "when_action_injects_decision_criteria_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:96): Function "then_instructions_contain_decision_criteria_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:197): Function "test_action_injects_decision_criteria_and_assumptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:64): Function "given_questions_and_evidence_for_guardrails" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:74): Function "given_workflow_states_and_transitions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:88): Function "given_workflow_with_states_and_transitions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:110): Function "given_clarification_parameters_with_questions_and_evidence" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:138): Function "given_discovery_key_questions_and_evidence" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:213): Function "when_action_injects_questions_and_evidence" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:425): Function "test_action_injects_questions_and_evidence" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:29): Function "given_bot_name_and_behaviors_setup" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:35): Function "given_bot_name_and_behavior_setup" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:60): Function "given_bot_config_file_with_working_dir_and_behaviors" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:183): Function "given_behaviors_with_descriptions_and_trigger_words" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:434): Function "then_rules_directory_exists_and_is_directory" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:505): Function "given_bot_goal_and_behavior_descriptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:514): Function "given_behaviors_config_with_descriptions_and_patterns" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038): Function "test_rules_file_includes_bot_goal_and_behavior_descriptions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:92): Function "given_bot_config_and_behavior_exist" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:141): Function "match_and_execute" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312): Function "test_trigger_bot_only_no_behavior_or_action_specified" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350): Function "test_trigger_bot_and_behavior_no_action_specified" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396): Function "test_trigger_bot_behavior_and_action_explicitly" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:127): Function "then_bot_result_has_status_and_behavior_and_action" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:134): Function "then_bot_result_has_behavior_and_action" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:185): Function "given_bot_config_and_behavior_workflow" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297): Function "test_action_loads_and_merges_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:332): Function "test_bot_tool_forwards_to_current_behavior_and_current_action" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:353): Function "test_bot_tool_defaults_to_first_behavior_and_first_action_when_state_missing" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:79): Function "when_render_output_action_loads_and_merges_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:85): Function "when_action_finalizes_and_transitions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:175): Function "when_action_executes_and_returns_result" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:245): Function "then_instructions_file_exists_and_has_content" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:386): Function "then_result_has_violations_or_instructions" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024): Function "test_scanner_discovery_extracts_metadata_and_registers_scanners" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Function "test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files" appears to have multiple responsibilities - split into separate functions
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:68): Function "given_standard_workflow_states_and_transitions" appears to have multiple responsibilities - split into separate functions

#### Production Code Small Functions: 95 violation(s)

- 🟡 **WARNING** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:154): Function "then_base_instructions_include_next_behavior_reminder" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_agile_bots_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_agile_bots_helpers.py:21): Function "create_actions_workflow_json" is 100 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:43): Function "simple_story_graph" is 71 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:244): Function "given_knowledge_graph_config_and_template_created" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:588): Function "given_existing_story_graph_with_mob_epic" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800): Function "test_action_loads_and_merges_instructions" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840): Function "test_all_template_variables_are_replaced_in_instructions" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:42): Function "create_test_workflow" is 34 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138): Function "test_close_current_action_marks_complete_and_transitions" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:30): Function "given_base_actions_exist_with_transitions" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130): Function "test_complete_workflow_end_to_end" is 55 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231): Function "test_save_planning_data_when_parameters_provided" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253): Function "test_preserve_existing_planning_data_when_saving" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:327): Function "test_track_activity_when_gather_context_action_completes" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:393): Function "test_workflow_resumes_at_decide_planning_criteria_after_interruption" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476): Function "test_save_clarification_data_when_parameters_provided" is 28 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505): Function "test_preserve_existing_clarification_data_when_saving" is 26 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:183): Function "given_behaviors_with_descriptions_and_trigger_words" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:399): Function "then_trigger_words_in_behavior_section" is 34 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:555): Function "create_base_actions_structure" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:622): Function "generator" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:696): Function "test_generator_creates_mcp_server_for_test_bot" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:763): Function "test_generator_creates_tools_for_test_bot_with_4_behaviors" is 29 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:796): Function "test_generator_loads_trigger_words_from_behavior_folder" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:821): Function "test_generator_handles_missing_trigger_words" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:895): Function "test_generator_deploys_server_successfully" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920): Function "test_server_publishes_tool_catalog_with_metadata" is 30 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:951): Function "test_generator_fails_when_protocol_handler_not_running" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:997): Function "test_generator_creates_workspace_rules_file_with_trigger_patterns" is 40 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038): Function "test_rules_file_includes_bot_goal_and_behavior_descriptions" is 52 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1091): Function "test_rules_file_maps_trigger_patterns_to_tool_naming_conventions" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:38): Function "create_behavior_folder_duplicate_removed" is 37 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:171): Function "clean_env" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332): Function "test_entry_point_bootstraps_from_agent_json" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355): Function "test_environment_variable_takes_precedence_over_agent_json" is 35 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Function "test_missing_agent_json_with_preconfig_env_var_works" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419): Function "test_bot_initializes_with_bootstrapped_directories" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444): Function "test_workflow_state_created_in_workspace_directory" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476): Function "test_bot_config_loaded_from_bot_directory" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504): Function "test_behavior_folders_resolved_from_bot_directory" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529): Function "test_multiple_calls_use_cached_env_vars" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:207): Function "create_base_action_instructions_duplicate_removed" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:229): Function "setup_bot_for_testing" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:262): Function "create_behavior_trigger_words" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:39): Function "setup_bot" is 40 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:141): Function "match_and_execute" is 44 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312): Function "test_trigger_bot_only_no_behavior_or_action_specified" is 37 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350): Function "test_trigger_bot_and_behavior_no_action_specified" is 45 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396): Function "test_trigger_bot_behavior_and_action_explicitly" is 45 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442): Function "test_trigger_close_current_action" is 37 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241): Function "test_tool_invokes_behavior_action_when_called" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264): Function "test_tool_routes_to_correct_behavior_action_method" is 28 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297): Function "test_action_loads_and_merges_instructions" is 30 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438): Function "test_action_called_directly_saves_workflow_state" is 41 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484): Function "test_activity_logged_to_workspace_area_not_bot_area" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:29): Function "given_base_instructions_for_render_output_copied" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154): Function "test_activity_log_creates_file_if_not_exists" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192): Function "test_render_output_action_executes_successfully" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223): Function "test_all_template_variables_are_replaced_in_instructions" is 44 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268): Function "test_render_configs_format_includes_all_fields" is 81 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:64): Function "test_clear_python_bytecode_cache" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:28): Function "create_behavior_folder" is 38 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:141): Function "given_base_action_instructions_for_validate_rules" is 25 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:471): Function "load_scanner_class" is 33 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:505): Function "setup_test_rules" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:550): Function "validate_violation_details" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622): Function "test_track_activity_when_validate_rules_action_completes" is 35 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658): Function "test_track_multiple_validate_rules_invocations_across_behaviors" is 28 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:687): Function "test_activity_log_maintains_chronological_order" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:753): Function "test_workflow_state_shows_all_actions_completed" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:777): Function "test_activity_log_records_full_workflow_completion" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836): Function "test_validate_rules_returns_instructions_with_rules_as_context" is 111 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948): Function "test_validate_rules_provides_report_path_for_saving_validation_report" is 33 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024): Function "test_scanner_discovery_extracts_metadata_and_registers_scanners" is 41 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1118): Function "test_scanners_detect_violations_in_knowledge_graph" is 54 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1228): Function "create_comprehensive_story_graph" is 272 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1517): Function "get_expected_story_names_for_scope" is 41 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Function "test_validate_rules_respects_scope" is 83 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Function "test_validate_rules_scope_extraction" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936): Function "test_validate_rules_with_test_file_scope_parameter" is 66 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003): Function "test_validate_rules_with_test_files_scope_parameter" is 69 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073): Function "test_validate_rules_verifies_test_files_passed_to_scanner" is 81 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250): Function "test_violation_report_generation_in_different_formats" is 55 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489): Function "test_scanner_detects_violations" is 314 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812): Function "test_validate_code_files_action_accepts_test_files_parameter" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840): Function "test_validate_code_files_action_validates_each_file_from_parameters" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Function "test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files" is 48 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946): Function "test_validate_code_files_action_accepts_code_files_parameter" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:178): Function "create_test_workflow" is 33 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:257): Function "test_workflow_falls_back_to_completed_actions_when_current_action_missing" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:304): Function "test_workflow_out_of_order_navigation_removes_completed_actions_after_target" is 41 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354): Function "test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow" is 47 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Function "test_behavior_loads_from_actions_workflow_json" is 58 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474): Function "test_different_behaviors_can_have_different_action_orders" is 119 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594): Function "test_workflow_transitions_built_correctly_from_actions_workflow_json" is 74 lines - should be under 20 lines (extract complex logic to helper functions)

#### Tests Must Match Story Graph Exactly: 72 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800): Test method [test_action_loads_and_merges_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_epic_has_sub_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_story_has_scenarios](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_from_bot_with_path](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138): Test method [test_close_current_action_marks_complete_and_transitions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130): Test method [test_complete_workflow_end_to_end](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130) is approximately 55 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231): Test method [test_save_planning_data_when_parameters_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253): Test method [test_preserve_existing_planning_data_when_saving](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:327): Test method [test_track_activity_when_gather_context_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:327) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:393): Test method [test_workflow_resumes_at_decide_planning_criteria_after_interruption](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:393) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476): Test method [test_save_clarification_data_when_parameters_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505): Test method [test_preserve_existing_clarification_data_when_saving](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505) is approximately 26 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateBotTools](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateBehaviorTools](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:696): Test method [test_generator_creates_mcp_server_for_test_bot](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:696) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:763): Test method [test_generator_creates_tools_for_test_bot_with_4_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:763) is approximately 29 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:796): Test method [test_generator_loads_trigger_words_from_behavior_folder](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:796) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:821): Test method [test_generator_handles_missing_trigger_words](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:821) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:895): Test method [test_generator_deploys_server_successfully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:895) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920): Test method [test_server_publishes_tool_catalog_with_metadata](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920) is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:951): Test method [test_generator_fails_when_protocol_handler_not_running](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:951) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateCursorAwarenessFiles](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:997): Test method [test_generator_creates_workspace_rules_file_with_trigger_patterns](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:997) is approximately 40 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038): Test method [test_rules_file_includes_bot_goal_and_behavior_descriptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038) is approximately 52 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1091): Test method [test_rules_file_maps_trigger_patterns_to_tool_naming_conventions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1091) is approximately 31 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332): Test method [test_entry_point_bootstraps_from_agent_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355): Test method [test_environment_variable_takes_precedence_over_agent_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355) is approximately 35 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Test method [test_missing_agent_json_with_preconfig_env_var_works](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419): Test method [test_bot_initializes_with_bootstrapped_directories](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444): Test method [test_workflow_state_created_in_workspace_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476): Test method [test_bot_config_loaded_from_bot_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504): Test method [test_behavior_folders_resolved_from_bot_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529): Test method [test_multiple_calls_use_cached_env_vars](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312): Test method [test_trigger_bot_only_no_behavior_or_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312) is approximately 37 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350): Test method [test_trigger_bot_and_behavior_no_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350) is approximately 45 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396): Test method [test_trigger_bot_behavior_and_action_explicitly](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396) is approximately 45 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442): Test method [test_trigger_close_current_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442) is approximately 37 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241): Test method [test_tool_invokes_behavior_action_when_called](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264): Test method [test_tool_routes_to_correct_behavior_action_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297): Test method [test_action_loads_and_merges_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297) is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438): Test method [test_action_called_directly_saves_workflow_state](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438) is approximately 41 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484): Test method [test_activity_logged_to_workspace_area_not_bot_area](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154): Test method [test_activity_log_creates_file_if_not_exists](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192): Test method [test_render_output_action_executes_successfully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223) is approximately 44 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268): Test method [test_render_configs_format_includes_all_fields](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268) is approximately 81 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622): Test method [test_track_activity_when_validate_rules_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622) is approximately 35 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658): Test method [test_track_multiple_validate_rules_invocations_across_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:687): Test method [test_activity_log_maintains_chronological_order](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:687) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:753): Test method [test_workflow_state_shows_all_actions_completed](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:753) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:777): Test method [test_activity_log_records_full_workflow_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:777) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836): Test method [test_validate_rules_returns_instructions_with_rules_as_context](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836) is approximately 111 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948): Test method [test_validate_rules_provides_report_path_for_saving_validation_report](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948) is approximately 33 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024): Test method [test_scanner_discovery_extracts_metadata_and_registers_scanners](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024) is approximately 41 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1118): Test method [test_scanners_detect_violations_in_knowledge_graph](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1118) is approximately 54 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Test method [test_validate_rules_respects_scope](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820) is approximately 83 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Test method [test_validate_rules_scope_extraction](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904) is approximately 31 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936): Test method [test_validate_rules_with_test_file_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936) is approximately 66 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003): Test method [test_validate_rules_with_test_files_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003) is approximately 69 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073): Test method [test_validate_rules_verifies_test_files_passed_to_scanner](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073) is approximately 81 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py): Test class [TestGenerateViolationReport](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250): Test method [test_violation_report_generation_in_different_formats](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250) is approximately 55 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489): Test method [test_scanner_detects_violations](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489) is approximately 314 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812): Test method [test_validate_code_files_action_accepts_test_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840): Test method [test_validate_code_files_action_validates_each_file_from_parameters](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Test method [test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868) is approximately 48 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946): Test method [test_validate_code_files_action_accepts_code_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354): Test method [test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354) is approximately 47 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Test method [test_behavior_loads_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415) is approximately 58 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474): Test method [test_different_behaviors_can_have_different_action_orders](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474) is approximately 119 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594): Test method [test_workflow_transitions_built_correctly_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594) is approximately 74 lines - should be under 20 lines (extract to helpers)

#### Test File And Class Naming: 17 violation(s)

- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py): Test file name "test_base_action" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py): Test file name "test_bot_behavior_exceptions" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_bot_execute_behavior.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_execute_behavior.py): Test file name "test_bot_execute_behavior" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_build_agile_bots_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_agile_bots_helpers.py): Test file name "test_build_agile_bots_helpers" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py): Test file name "test_cli_exceptions" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py): Test file name "test_close_current_action" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py): Test file name "test_complete_workflow_integration" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test file name "test_generate_bot_server_and_tools" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py): Test file name "test_helpers" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py): Test file name "test_invoke_bot_cli" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py): Test file name "test_invoke_bot_tool" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py): Test file name "test_mcp_generator_exceptions" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py): Test file name "test_restart_mcp_server" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py): Test file name "test_router_exceptions" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py): Test file name "test_utils" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py): Test file name "test_validate_knowledge_and_content_against_rules" does not match any sub-epic name - file should be named test_<sub_epic_name>.py
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py): Test file name "test_workflow_action_sequence" does not match any sub-epic name - file should be named test_<sub_epic_name>.py

#### Use Arrange Act Assert: 88 violation(s)

- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:278): Test method [test_next_behavior_reminder_injected_when_final_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:278) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:294): Test method [test_next_behavior_reminder_not_injected_when_not_final_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:294) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:308): Test method [test_next_behavior_reminder_not_injected_when_no_next_behavior](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:308) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:80): Test method [test_bot_raises_exception_when_behavior_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:80) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:93): Test method [test_behavior_raises_exception_when_actions_workflow_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:93) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:128): Test method [test_track_activity_when_build_knowledge_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:128) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:131): Test method [test_track_activity_when_build_knowledge_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:131) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:144): Test method [test_seamless_transition_from_build_knowledge_to_validate_rules](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:144) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:147): Test method [test_workflow_state_captures_build_knowledge_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:147) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:778): Test method [test_action_injects_knowledge_graph_template](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:778) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:790): Test method [test_action_raises_error_when_template_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:790) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800): Test method [test_action_loads_and_merges_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:822): Test method [test_action_uses_base_instructions_when_behavior_instructions_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:822) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:872): Test method [test_behavior_updates_existing_story_graph_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:872) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:913): Test method [test_story_map_loads_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:913) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:917): Test method [test_epic_has_sub_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:917) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:923): Test method [test_sub_epic_has_story_groups](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:923) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:930): Test method [test_story_group_has_stories](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:930) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:937): Test method [test_story_has_properties](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:937) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:941): Test method [test_story_has_scenarios](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:941) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:946): Test method [test_scenario_has_properties](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:946) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:951): Test method [test_scenario_default_test_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:951) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:956): Test method [test_story_has_scenario_outlines](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:956) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:961): Test method [test_scenario_outline_has_examples](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:961) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:966): Test method [test_story_default_test_class](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:966) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:970): Test method [test_story_map_walk_traverses_all_nodes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:970) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:976): Test method [test_map_location_for_epic](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:976) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:981): Test method [test_map_location_for_sub_epic](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:981) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:986): Test method [test_map_location_for_story](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:986) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:991): Test method [test_scenario_map_location](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:991) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:996): Test method [test_scenario_outline_map_location](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:996) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1001): Test method [test_from_bot_loads_story_graph](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1001) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1010): Test method [test_from_bot_with_path](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1010) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1018): Test method [test_from_bot_raises_when_file_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1018) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:33): Test method [test_cli_raises_exception_when_parameter_description_cannot_be_inferred](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:33) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:162): Test method [test_close_action_at_final_action_stays_at_final](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:162) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:198): Test method [test_close_action_saves_to_completed_actions_list](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:198) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:213): Test method [test_close_handles_action_already_completed_gracefully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:213) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:233): Test method [test_bot_class_has_close_current_action_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:233) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:162): Test method [test_track_activity_when_planning_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:162) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:165): Test method [test_track_activity_when_planning_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:165) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:183): Test method [test_seamless_transition_from_planning_to_build_knowledge](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:183) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:186): Test method [test_workflow_state_captures_planning_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:186) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:375): Test method [test_seamless_transition_from_gather_context_to_decide_planning_criteria](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:375) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:384): Test method [test_workflow_state_captures_gather_context_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:384) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038): Test method [test_rules_file_includes_bot_goal_and_behavior_descriptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1123): Test method [test_generator_handles_file_write_errors_gracefully_creates_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1123) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1157): Test method [test_full_awareness_generation_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1157) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Test method [test_missing_agent_json_with_preconfig_env_var_works](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312): Test method [test_trigger_bot_only_no_behavior_or_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350): Test method [test_trigger_bot_and_behavior_no_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396): Test method [test_trigger_bot_behavior_and_action_explicitly](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442): Test method [test_trigger_close_current_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:62): Test method [test_bot_config](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:62) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484): Test method [test_activity_logged_to_workspace_area_not_bot_area](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:509): Test method [test_activity_log_contains_correct_entry](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:509) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:13): Test method [test_mcp_generator_raises_exception_when_base_actions_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:13) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:126): Test method [test_track_activity_when_render_output_action_starts](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:126) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:129): Test method [test_track_activity_when_render_output_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:129) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:140): Test method [test_track_multiple_render_output_invocations_across_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:140) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154): Test method [test_activity_log_creates_file_if_not_exists](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:186): Test method [test_seamless_transition_from_validate_rules_to_render_output](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:186) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:189): Test method [test_workflow_state_captures_render_output_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:189) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192): Test method [test_render_output_action_executes_successfully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268): Test method [test_render_configs_format_includes_all_fields](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:93): Test method [test_find_mcp_server_processes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:93) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:15): Test method [test_router_raises_exception_when_state_file_does_not_exist](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:15) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:28): Test method [test_router_raises_exception_when_no_completed_actions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:28) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:46): Test method [test_router_raises_exception_when_unknown_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:46) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:132): Test method [test_raises_error_when_behavior_folder_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:132) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1181): Test method [test_validate_rules_raises_exception_when_story_graph_not_found](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1181) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1199): Test method [test_validate_rules_raises_exception_when_story_graph_invalid_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1199) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Test method [test_validate_rules_respects_scope](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Test method [test_validate_rules_scope_extraction](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936): Test method [test_validate_rules_with_test_file_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003): Test method [test_validate_rules_with_test_files_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073): Test method [test_validate_rules_verifies_test_files_passed_to_scanner](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250): Test method [test_violation_report_generation_in_different_formats](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489): Test method [test_scanner_detects_violations](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:229): Test method [test_workflow_starts_at_first_action_when_no_completed_actions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:229) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:241): Test method [test_workflow_uses_current_action_when_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:241) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:257): Test method [test_workflow_falls_back_to_completed_actions_when_current_action_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:257) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:290): Test method [test_workflow_starts_at_first_action_when_no_workflow_state_file_exists](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:290) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354): Test method [test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:402): Test method [test_behavior_requires_actions_workflow_json_no_fallback](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:402) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Test method [test_behavior_loads_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415) does not follow Arrange-Act-Assert structure - add # Given/When/Then or # Arrange/Act/Assert comments

#### Use Ascii Only: 1 violation(s)

- 🔴 **ERROR** - [`test_helpers.py:1`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:1:1): Line contains Unicode characters: ﻿ - use ASCII alternatives like [PASS], [ERROR], [FAIL]

#### Use Class Based Organization: 72 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800): Test method [test_action_loads_and_merges_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:800) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:840) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_epic_has_sub_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_story_has_scenarios](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_from_bot_with_path](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138): Test method [test_close_current_action_marks_complete_and_transitions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:138) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130): Test method [test_complete_workflow_end_to_end](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:130) is approximately 55 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231): Test method [test_save_planning_data_when_parameters_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:231) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253): Test method [test_preserve_existing_planning_data_when_saving](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:253) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:327): Test method [test_track_activity_when_gather_context_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:327) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:393): Test method [test_workflow_resumes_at_decide_planning_criteria_after_interruption](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:393) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476): Test method [test_save_clarification_data_when_parameters_provided](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:476) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505): Test method [test_preserve_existing_clarification_data_when_saving](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:505) is approximately 26 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateBotTools](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateBehaviorTools](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:696): Test method [test_generator_creates_mcp_server_for_test_bot](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:696) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:763): Test method [test_generator_creates_tools_for_test_bot_with_4_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:763) is approximately 29 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:796): Test method [test_generator_loads_trigger_words_from_behavior_folder](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:796) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:821): Test method [test_generator_handles_missing_trigger_words](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:821) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:895): Test method [test_generator_deploys_server_successfully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:895) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920): Test method [test_server_publishes_tool_catalog_with_metadata](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:920) is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:951): Test method [test_generator_fails_when_protocol_handler_not_running](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:951) is approximately 21 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py): Test class [TestGenerateCursorAwarenessFiles](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:997): Test method [test_generator_creates_workspace_rules_file_with_trigger_patterns](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:997) is approximately 40 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038): Test method [test_rules_file_includes_bot_goal_and_behavior_descriptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1038) is approximately 52 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1091): Test method [test_rules_file_maps_trigger_patterns_to_tool_naming_conventions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1091) is approximately 31 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332): Test method [test_entry_point_bootstraps_from_agent_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:332) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355): Test method [test_environment_variable_takes_precedence_over_agent_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355) is approximately 35 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Test method [test_missing_agent_json_with_preconfig_env_var_works](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419): Test method [test_bot_initializes_with_bootstrapped_directories](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444): Test method [test_workflow_state_created_in_workspace_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476): Test method [test_bot_config_loaded_from_bot_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504): Test method [test_behavior_folders_resolved_from_bot_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529): Test method [test_multiple_calls_use_cached_env_vars](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312): Test method [test_trigger_bot_only_no_behavior_or_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:312) is approximately 37 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350): Test method [test_trigger_bot_and_behavior_no_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:350) is approximately 45 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396): Test method [test_trigger_bot_behavior_and_action_explicitly](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:396) is approximately 45 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442): Test method [test_trigger_close_current_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:442) is approximately 37 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241): Test method [test_tool_invokes_behavior_action_when_called](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:241) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264): Test method [test_tool_routes_to_correct_behavior_action_method](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:264) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297): Test method [test_action_loads_and_merges_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:297) is approximately 30 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438): Test method [test_action_called_directly_saves_workflow_state](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:438) is approximately 41 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484): Test method [test_activity_logged_to_workspace_area_not_bot_area](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:484) is approximately 24 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154): Test method [test_activity_log_creates_file_if_not_exists](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:154) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192): Test method [test_render_output_action_executes_successfully](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:192) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223): Test method [test_all_template_variables_are_replaced_in_instructions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:223) is approximately 44 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268): Test method [test_render_configs_format_includes_all_fields](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:268) is approximately 81 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622): Test method [test_track_activity_when_validate_rules_action_completes](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:622) is approximately 35 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658): Test method [test_track_multiple_validate_rules_invocations_across_behaviors](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:658) is approximately 28 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:687): Test method [test_activity_log_maintains_chronological_order](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:687) is approximately 22 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:753): Test method [test_workflow_state_shows_all_actions_completed](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:753) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:777): Test method [test_activity_log_records_full_workflow_completion](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:777) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836): Test method [test_validate_rules_returns_instructions_with_rules_as_context](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:836) is approximately 111 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948): Test method [test_validate_rules_provides_report_path_for_saving_validation_report](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:948) is approximately 33 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024): Test method [test_scanner_discovery_extracts_metadata_and_registers_scanners](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1024) is approximately 41 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1118): Test method [test_scanners_detect_violations_in_knowledge_graph](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1118) is approximately 54 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820): Test method [test_validate_rules_respects_scope](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1820) is approximately 83 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904): Test method [test_validate_rules_scope_extraction](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1904) is approximately 31 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936): Test method [test_validate_rules_with_test_file_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1936) is approximately 66 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003): Test method [test_validate_rules_with_test_files_scope_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2003) is approximately 69 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073): Test method [test_validate_rules_verifies_test_files_passed_to_scanner](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2073) is approximately 81 lines - should be under 20 lines (extract to helpers)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py): Test class [TestGenerateViolationReport](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py) appears abbreviated - should match story name exactly (Test<ExactStoryName>)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250): Test method [test_violation_report_generation_in_different_formats](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2250) is approximately 55 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489): Test method [test_scanner_detects_violations](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2489) is approximately 314 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812): Test method [test_validate_code_files_action_accepts_test_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2812) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840): Test method [test_validate_code_files_action_validates_each_file_from_parameters](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2840) is approximately 27 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868): Test method [test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2868) is approximately 48 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946): Test method [test_validate_code_files_action_accepts_code_files_parameter](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2946) is approximately 23 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354): Test method [test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:354) is approximately 47 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415): Test method [test_behavior_loads_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:415) is approximately 58 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474): Test method [test_different_behaviors_can_have_different_action_orders](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:474) is approximately 119 lines - should be under 20 lines (extract to helpers)
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594): Test method [test_workflow_transitions_built_correctly_from_actions_workflow_json](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:594) is approximately 74 lines - should be under 20 lines (extract to helpers)

#### Use Descriptive Function Names: 54 violation(s)

- 🟡 **WARNING** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:74): Helper function "given_standard_workflow_actions_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:85): Helper function "given_action_configs_exist_for_workflow_actions" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:208): Helper function "given_action_configs_exist_for_workflow_actions_with_render_output_after" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:45): Helper function "when_initializing_workflow_with_invalid_behavior" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_bot_behavior_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_behavior_exceptions.py:74): Helper function "then_exception_mentions_behavior_json_required" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:163): Helper function "given_knowledge_graph_config_file_created" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:244): Helper function "given_knowledge_graph_config_and_template_created" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:365): Helper function "then_config_path_matches_expected" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:486): Helper function "then_all_template_variables_replaced" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:507): Helper function "given_knowledge_graph_config_for_increments_created" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:535): Helper function "given_test_variables_for_exploration" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:542): Helper function "given_test_variables_for_shape_build_knowledge" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:581): Helper function "given_test_variables_for_prioritization" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:621): Helper function "given_knowledge_graph_config_for_story_graph_increments" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:908): Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:24): Helper function "when_cli_infers_parameter_description_for_unknown_command" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:33): Helper function "given_initial_completed_action_count" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:34): Helper function "given_planning_parameters_with_decisions_and_assumptions" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:47): Helper function "given_planning_parameters_for_shape_behavior" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:66): Helper function "given_planning_action_is_initialized" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:92): Helper function "when_action_executes_with_parameters" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:110): Helper function "given_clarification_parameters_with_questions_and_evidence" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:123): Helper function "given_clarification_parameters_for_shape_behavior" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:158): Helper function "given_gather_context_action_is_initialized" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:248): Helper function "when_action_executes_with_clarification_parameters" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:60): Helper function "given_bot_config_file_with_working_dir_and_behaviors" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:77): Helper function "given_bot_configured_by_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:143): Helper function "given_bot_config_file_with_invalid_json" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:155): Helper function "given_bot_config_does_not_exist" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:221): Helper function "when_bot_tool_generator_processes_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:227): Helper function "when_behavior_tool_generator_processes_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:233): Helper function "when_mcp_server_generator_receives_bot_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:514): Helper function "given_behaviors_config_with_descriptions_and_patterns" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:547): Helper function "then_awareness_file_contains_required_sections" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:80): Helper function "given_bot_directory_environment_variable_set" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:84): Helper function "given_workspace_directory_environment_variable_set" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:88): Helper function "given_legacy_working_dir_environment_variable_set" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:92): Helper function "given_bot_config_and_behavior_exist" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:119): Helper function "then_environment_variable_is_set" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:31): Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:133): Helper function "__init__" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:185): Helper function "given_bot_config_and_behavior_workflow" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:69): Helper function "given_render_configs_created" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:90): Helper function "then_render_configs_template_variable_replaced" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:97): Helper function "then_render_configs_include_all_required_fields" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:113): Helper function "then_render_instructions_template_variable_replaced" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:39): Helper function "given_validate_rules_action_initialized" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:71): Helper function "given_terminal_action_config" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:313): Helper function "when_action_executes_with_scope_parameters" contains abbreviations - use full descriptive words
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2107): Helper function "scan" uses vague/abbreviated name - use descriptive name that reveals purpose
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:122): Helper function "given_behavior_config_created" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:131): Helper function "when_behavior_is_initialized" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:156): Helper function "when_behavior_is_initialized_raises_error" contains abbreviations - use full descriptive words
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:168): Helper function "then_error_mentions_behavior_json_required" contains abbreviations - use full descriptive words

#### Use Exact Variable Names: 25 violation(s)

- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:152): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:167): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:287): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:259): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:288): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:348): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:369): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:393): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:413): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:433): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:473): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:730): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:874): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:973): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1857): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1985): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2064): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2138): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2835): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2861): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2906): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2933): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2965): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2984): Variable "result" uses generic name - use exact domain concept name from scenario/AC
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2998): Variable "result" uses generic name - use exact domain concept name from scenario/AC

#### Use Given When Then Helpers: 367 violation(s)

- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:280): Lines 280-285: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Next behavior reminder is injected when action is final action
GIVEN: validate_rules is the final action in behavior workflow
AND: bot_config.json defines behavior sequence
...
- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:296): Lines 296-300: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Next behavior reminder is NOT injected when action is not final
GIVEN: validate_rules is NOT the final action (render_output comes after)
AND: bot_config.json defines behavior sequence
...
- 🔴 **ERROR** - [`test_base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_base_action.py:310): Lines 310-314: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
GIVEN: discovery is the last behavior in bot_config.json
AND: render_output is the final action
...
- 🟡 **WARNING** - [`test_bot_execute_behavior.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_bot_execute_behavior.py:1): File has syntax error, cannot scan: unexpected indent (test_bot_execute_behavior.py, line 21)
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:131): Lines 131-133: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_track_activity_when_build_knowledge_action_completes(self, bot_directory, workspace_directory):
outputs = {'knowledge_items_count': 12, 'file_path': 'knowledge.json'}
duration = 420
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:802): Lines 802-805: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Action loads and merges instructions for shape build_knowledge
GIVEN: Base and behavior-specific instructions exist
WHEN: Action method is invoked
...
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:824): Lines 824-827: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Action uses base instructions when behavior-specific instructions are missing
GIVEN: Base instructions exist but behavior-specific instructions do not
WHEN: Action method is invoked
...
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:842): Lines 842-845: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: All template variables are replaced in final instructions
GIVEN: Base instructions with {{rules}}, {{schema}}, {{description}}, {{instructions}} placeholders
WHEN: Action loads and merges instructions with all injections
...
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:874): Lines 874-875: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
Test that prioritization behavior updates existing story-graph.json by adding increments array,
rather than creating a separate story-graph-increments.json file.
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:1020): Lines 1020-1021: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = self._create_mock_bot(bot_directory)
then_story_map_raises_file_not_found_error(bot)
- 🔴 **ERROR** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:134): Lines 134-140: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
Flow:
1. Start at gather_context
2. Execute gather_context
...
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:167): Lines 167-173: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
bot_directory,
workspace_directory,
PlanningAction,
...
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:233): Lines 233-238: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Save planning data when parameters are provided
GIVEN: decide_planning_criteria action is initialized
AND: parameters contain decisions_made and assumptions_made
...
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:255): Lines 255-260: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Preserve existing planning data when saving
GIVEN: planning.json already exists with data for 'discovery' behavior
AND: decide_planning_criteria action is initialized for 'shape' behavior
...
- 🔴 **ERROR** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:279): Lines 279-283: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Skip saving when no planning parameters are provided
GIVEN: decide_planning_criteria action is initialized
AND: parameters do not contain decisions_made or assumptions_made
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:309): Lines 309-312: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track activity when gather_context action starts
GIVEN: behavior is 'discovery' and action is 'gather_context'
WHEN: gather_context action starts execution
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:329): Lines 329-332: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track activity when gather_context action completes
GIVEN: gather_context action started
WHEN: gather_context action finishes execution
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:351): Lines 351-354: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track multiple gather_context invocations across behaviors
GIVEN: activity log contains entries for shape and discovery
WHEN: both entries are present
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:377): Lines 377-380: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Seamless transition from gather_context to decide_planning_criteria
GIVEN: gather_context action is complete
WHEN: workflow transitions
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:386): Lines 386-389: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workflow state captures gather_context completion
GIVEN: gather_context action completes
WHEN: Workflow saves completed action
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:395): Lines 395-398: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workflow resumes at decide_planning_criteria after interruption
GIVEN: gather_context is completed and chat was interrupted
WHEN: user reopens chat and invokes bot tool
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:478): Lines 478-483: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Save clarification data when parameters are provided
GIVEN: gather_context action is initialized
AND: parameters contain key_questions_answered and evidence_provided
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:499): Lines 499-503: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
clarification_file,
'shape',
expected_key_questions={'user_types': 'Game Masters'},
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:507): Lines 507-512: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Preserve existing clarification data when saving
GIVEN: clarification.json already exists with data for 'discovery' behavior
AND: gather_context action is initialized for 'shape' behavior
...
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:534): Lines 534-538: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Skip saving when no clarification parameters are provided
GIVEN: gather_context action is initialized
AND: parameters do not contain key_questions_answered or evidence_provided
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:650): Lines 650-654: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator creates bot tool for test_bot
GIVEN: A bot configuration file with a working directory and behaviors
AND: A bot that has been initialized with that config file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:674): Lines 674-678: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator creates behavior tools for test_bot with 4 behaviors
GIVEN: A bot configuration file with a working directory and behaviors
AND: A bot that has been initialized with that config file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:698): Lines 698-702: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator creates MCP server for test_bot
GIVEN: A bot configuration file with a working directory and behaviors
AND: A bot that has been initialized with that config file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:721): Lines 721-725: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator fails when Bot Config is missing
GIVEN: A bot directory exists
AND: Bot Config does NOT exist
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:741): Lines 741-745: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator fails when Bot Config is malformed
GIVEN: A bot directory exists
AND: Bot Config file exists with invalid JSON syntax
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:765): Lines 765-770: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator creates tools for test_bot with 4 behaviors
GIVEN: A bot configuration file with a working directory and behaviors
AND: Base actions structure exists
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:798): Lines 798-803: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator loads trigger words from behavior folder
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behavior has trigger words configured
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:823): Lines 823-828: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator handles missing trigger words file
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behavior does not have trigger words configured
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:897): Lines 897-902: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator deploys test_bot MCP Server successfully
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behavior workflow files exist for all behaviors
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:922): Lines 922-927: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Server publishes tool catalog with complete metadata
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behavior has trigger words configured
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:953): Lines 953-958: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator fails when MCP Protocol Handler not running
GIVEN: A bot configuration file with a working directory and behaviors
AND: A bot that has been initialized with that config file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:975): Lines 975-979: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Server handles initialization failure in separate thread
GIVEN: A bot directory exists
AND: Bot Config does NOT exist
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:999): Lines 999-1007: Multiple inline steps (9 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator creates bot-specific workspace rules file with trigger patterns
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behaviors have trigger words configured
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1040): Lines 1040-1045: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Rules file includes bot goal and behavior descriptions from instructions.json
GIVEN: Bot has instructions.json with goal and behavior descriptions
WHEN: Generator creates .cursor/rules/mcp-<bot-name>-awareness.mdc file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1053): Lines 1053-1060: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_root,
bot_name,
'Transform user needs into well-structured stories',
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1063): Lines 1063-1073: Multiple inline steps (11 lines) should be extracted into a Given/When/Then helper function. Block:
{
'name': '1_shape',
'description': 'Create initial story map outline from user context',
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1093): Lines 1093-1099: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Rules file maps trigger patterns to tool naming conventions in behavior sections
GIVEN: A bot configuration file with a working directory and behaviors
AND: Behaviors have trigger words configured
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1125): Lines 1125-1129: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator handles file write errors gracefully - creates directory
GIVEN: MCP Server Generator attempts to create awareness files
WHEN: .cursor/rules/ directory does not exist
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1141): Lines 1141-1145: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Generator handles file write errors with clear error message
GIVEN: .cursor/rules/ directory is write-protected
WHEN: Generator attempts to write file
...
- 🔴 **ERROR** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1159): Lines 1159-1163: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
INTEGRATION TEST: Full awareness generation workflow
GIVEN: MCP Server Generator initialized
WHEN: generate_awareness_files() called
...
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:1): File has syntax error, cannot scan: invalid non-printable character U+FEFF (test_helpers.py, line 1)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:230): Lines 230-233: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Bot directory resolved from environment variable
GIVEN: BOT_DIRECTORY environment variable is set
WHEN: get_bot_directory() is called
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:244): Lines 244-247: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workspace directory resolved from environment variable
GIVEN: WORKING_AREA environment variable is set
WHEN: get_workspace_directory() is called
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:258): Lines 258-262: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Backward compatibility with WORKING_DIR variable
GIVEN: WORKING_DIR environment variable is set (legacy name)
AND: WORKING_AREA is not set
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:275): Lines 275-279: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: WORKING_AREA takes precedence over legacy WORKING_DIR
GIVEN: Both WORKING_AREA and WORKING_DIR are set
AND: They have different values
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:282): Lines 282-284: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
different_dir = temp_workspace / 'different'
os.environ['WORKING_AREA'] = str(workspace_directory)
os.environ['WORKING_DIR'] = str(different_dir)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:290): Lines 290-291: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert result == workspace_directory
assert result != different_dir
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:299): Lines 299-303: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Missing BOT_DIRECTORY raises helpful error
GIVEN: BOT_DIRECTORY environment variable is NOT set
WHEN: get_bot_directory() is called
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:314): Lines 314-318: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Missing WORKING_AREA raises helpful error
GIVEN: WORKING_AREA and WORKING_DIR environment variables are NOT set
WHEN: get_workspace_directory() is called
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:321): Lines 321-322: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'WORKING_AREA' not in os.environ
assert 'WORKING_DIR' not in os.environ
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:334): Lines 334-339: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Entry point reads agent.json and sets environment
GIVEN: agent.json exists with WORKING_AREA field
AND: BOT_DIRECTORY can be self-detected from script location
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:352): Lines 352-353: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert get_bot_directory() == bot_directory
assert get_workspace_directory() == workspace_directory
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:355): Lines 355-357: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_environment_variable_takes_precedence_over_agent_json(
self, bot_directory, workspace_directory, temp_workspace
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:359): Lines 359-364: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Pre-set environment variable not overwritten
GIVEN: WORKING_AREA environment variable is already set (e.g., by mcp.json)
AND: agent.json also has WORKING_AREA field with different value
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:367): Lines 367-369: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
override_workspace = temp_workspace / 'override_workspace'
override_workspace.mkdir(parents=True, exist_ok=True)
os.environ['WORKING_AREA'] = str(override_workspace)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:377): Lines 377-382: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
if 'WORKING_AREA' not in os.environ:
agent_json_path = bot_directory / 'agent.json'
if agent_json_path.exists():
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:385): Lines 385-386: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert os.environ['WORKING_AREA'] == str(override_workspace)
assert os.environ['WORKING_AREA'] != str(workspace_directory)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:391): Lines 391-393: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_missing_agent_json_with_preconfig_env_var_works(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:395): Lines 395-401: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: agent.json not required if env vars pre-configured
GIVEN: WORKING_AREA environment variable is already set
AND: BOT_DIRECTORY environment variable is already set
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:404): Lines 404-405: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
os.environ['BOT_DIRECTORY'] = str(bot_directory)
os.environ['WORKING_AREA'] = str(workspace_directory)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:408): Lines 408-409: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
agent_json_path = bot_directory / 'agent.json'
assert not agent_json_path.exists()
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:412): Lines 412-413: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert get_bot_directory() == bot_directory
assert get_workspace_directory() == workspace_directory
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:419): Lines 419-421: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_bot_initializes_with_bootstrapped_directories(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:423): Lines 423-429: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Bot successfully initializes with bootstrapped environment
GIVEN: BOT_DIRECTORY environment variable is set
AND: WORKING_AREA environment variable is set
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:441): Lines 441-442: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert bot.bot_directory == bot_directory
assert bot.workspace_directory == workspace_directory
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:444): Lines 444-446: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_workflow_state_created_in_workspace_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:448): Lines 448-453: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workflow state file created in correct workspace
GIVEN: Environment is properly bootstrapped
AND: Bot is initialized with a behavior
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:466): Lines 466-467: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert workflow_file.parent == workspace_directory
assert workflow_file.name == 'workflow_state.json'
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:476): Lines 476-478: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_bot_config_loaded_from_bot_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:480): Lines 480-486: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Bot configuration loaded from bot directory (not workspace)
GIVEN: BOT_DIRECTORY is set to bot code location
AND: WORKING_AREA is set to workspace location
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:498): Lines 498-499: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert bot.bot_name == 'test_bot'
assert 'shape' in bot.behaviors
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:504): Lines 504-506: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_behavior_folders_resolved_from_bot_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:508): Lines 508-513: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Behavior folders resolved from bot directory
GIVEN: BOT_DIRECTORY is set
AND: WORKING_AREA is set to different location
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:523): Lines 523-524: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
expected_path = bot_directory / 'behaviors' / 'shape'
assert behavior_folder == expected_path
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:531): Lines 531-535: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Multiple calls read from cached environment (fast)
GIVEN: Environment variables are set
WHEN: get_workspace_directory() is called multiple times
...
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:542): Lines 542-544: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
result1 = get_workspace_directory()
result2 = get_workspace_directory()
result3 = get_workspace_directory()
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:314): Lines 314-320: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Trigger bot only (no behavior or action specified)
GIVEN: user types message containing trigger words
AND: bot is at specific behavior and action from workflow state
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:323): Lines 323-327: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_bot_triggers([
'lets work on stories',
'time to kick off stories',
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:329): Lines 329-330: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
trigger_message = 'lets work on stories'
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:333): Lines 333-334: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
for current_behavior in setup.behaviors:
for current_action in setup.actions:
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:337): Lines 337-341: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
route, result = helper.match_and_execute(
trigger_message,
current_behavior=current_behavior,
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:347): Lines 347-348: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
expected_action = 'gather_context' if current_action == 'initialize_workspace' else current_action
helper.assert_cli_result(result, current_behavior, expected_action)
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:352): Lines 352-358: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Trigger bot and behavior (no action specified)
GIVEN: user types message containing behavior-specific trigger words
AND: behavior is at specific action from workflow state
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:361): Lines 361-370: Multiple inline steps (10 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_triggers = {
'shape': 'kick off shaping for a new feature',
'prioritization': 'rank the backlog for launch',
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:372): Lines 372-374: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_behavior_triggers(
{behavior: [trigger] for behavior, trigger in behavior_triggers.items()}
)
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:379): Lines 379-380: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
for behavior, trigger_message in behavior_triggers.items():
for current_action in setup.actions:
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:383): Lines 383-387: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
route, result = helper.match_and_execute(
trigger_message,
current_behavior=behavior,
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:393): Lines 393-394: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
expected_action = 'gather_context' if current_action == 'initialize_workspace' else current_action
helper.assert_cli_result(result, behavior, expected_action)
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:398): Lines 398-403: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Trigger bot, behavior, and action explicitly
GIVEN: user types message containing action-specific trigger words
WHEN: Extension intercepts user message
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:406): Lines 406-413: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
action_trigger_templates = {
'initialize_workspace': 'set up the workspace area for {behavior}',
'gather_context': 'gather context for {behavior}',
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:417): Lines 417-420: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
for behavior in setup.behaviors:
for action, template in action_trigger_templates.items():
trigger = template.format(behavior=behavior)
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:425): Lines 425-427: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
for behavior in setup.behaviors:
for action, template in action_trigger_templates.items():
trigger_message = template.format(behavior=behavior)
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:429): Lines 429-433: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
route, result = helper.match_and_execute(
trigger_message,
current_behavior=None,  # Not needed for explicit triggers
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:439): Lines 439-440: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
expected_action = 'gather_context' if action == 'initialize_workspace' else action
helper.assert_cli_result(result, behavior, expected_action)
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:444): Lines 444-450: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Trigger close current action
GIVEN: user types message containing close trigger words
AND: bot is at specific behavior and action from workflow state
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:453): Lines 453-457: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
setup = TriggerTestSetup(bot_directory, workspace_directory).setup_bot().add_bot_triggers([
'close current action',
'done with this step',
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:459): Lines 459-460: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
helper = TriggerRouterTestHelper(setup.bot_directory, setup.workspace_directory, setup.bot_name, setup.bot_config)
trigger_message = 'done with this step'
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:463): Lines 463-464: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
for current_behavior in setup.behaviors:
for current_action in setup.actions:
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:467): Lines 467-471: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
route, result = helper.match_and_execute(
trigger_message,
current_behavior=current_behavior,
...
- 🔴 **ERROR** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:474): Lines 474-478: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
assert route is not None, f"Failed for {current_behavior}.{current_action}"
assert route['bot_name'] == setup.bot_name
assert route['action_name'] == 'close_current_action'
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:65): Lines 65-68: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
bot_directory,
'test_bot',
['shape', 'discovery', 'exploration', 'specification']
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:243): Lines 243-246: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: AI Chat invokes test_bot_shape_gather_context tool
GIVEN: Bot has behavior 'shape' with action 'gather_context'
WHEN: AI Chat invokes tool with parameters
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:258): Lines 258-259: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, test_bot_config)
result = bot.shape.gather_context()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:266): Lines 266-269: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Tool routes to correct behavior action method
GIVEN: Bot has multiple behaviors with build_knowledge action
WHEN: AI Chat invokes 'test_bot_exploration_build_knowledge'
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:277): Lines 277-279: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_root, 'test_bot', ['shape', 'discovery', 'exploration'], 'build_knowledge'
)
behavior_mapping = {'shape': '1_shape', 'discovery': '4_discovery', 'exploration': '5_exploration'}
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:287): Lines 287-288: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, test_bot_config)
result = bot.exploration.build_knowledge()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:299): Lines 299-302: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Action loads and merges instructions for shape gather_context
GIVEN: Base and behavior-specific instructions exist
WHEN: Action method is invoked
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:308): Lines 308-311: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
behavior = 'shape'
action = 'gather_context'
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:317): Lines 317-322: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
action_obj = GatherContextAction(
bot_name=bot_name,
behavior=behavior,
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:325): Lines 325-326: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'base_instructions' in merged_instructions
assert merged_instructions['action'] == action
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:334): Lines 334-337: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Bot tool forwards to current behavior and current action
GIVEN: workflow state shows current_behavior='discovery', current_action='build_knowledge'
WHEN: Bot tool receives invocation
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:347): Lines 347-348: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
result = bot.forward_to_current_behavior_and_current_action()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:355): Lines 355-358: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Bot tool defaults to first behavior and first action when state missing
GIVEN: workflow state does NOT exist
WHEN: Bot tool receives invocation
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:368): Lines 368-369: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
result = bot.forward_to_current_behavior_and_current_action()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:380): Lines 380-384: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Behavior tool forwards to current action within behavior
GIVEN: a behavior tool for 'discovery' behavior
AND: workflow state shows current_action='build_knowledge'
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:392): Lines 392-393: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
result = bot.discovery.forward_to_current_action()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:400): Lines 400-404: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Behavior tool sets workflow to current behavior when state shows different behavior
GIVEN: a behavior tool for 'exploration' behavior
AND: workflow state shows current_behavior='discovery'
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:412): Lines 412-413: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
result = bot.exploration.forward_to_current_action()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:420): Lines 420-424: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Behavior tool defaults to first action when state missing
GIVEN: a behavior tool for 'shape' behavior
AND: workflow state does NOT exist
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:432): Lines 432-433: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot = given_bot_instance_created('test_bot', bot_directory, bot_config)
result = bot.shape.forward_to_current_action()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:440): Lines 440-445: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Action called directly saves workflow state
GIVEN: Bot is initialized with WORKING_AREA set
AND: No workflow state exists yet
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:453): Lines 453-454: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
repo_root = get_python_workspace_root()
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:461): Lines 461-466: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
from agile_bot.bots.base_bot.src.bot.bot import Bot
bot = Bot(
bot_name='test_bot',
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:469): Lines 469-470: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
workflow_file = workspace_directory / 'workflow_state.json'
assert not workflow_file.exists(), "Workflow state should not exist yet"
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:486): Lines 486-492: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Activity logged to workspace_area not bot area
GIVEN: WORKING_AREA environment variable specifies workspace_area
AND: action 'gather_context' executes
...
- 🔴 **ERROR** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:511): Lines 511-517: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Activity log contains correct entry
GIVEN: action 'gather_context' executes in behavior 'discovery'
WHEN: Activity logger creates entry
...
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:15): Lines 15-17: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
bot_directory = tmp_path / 'agile_bot' / 'bots' / bot_name
bot_directory.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:22): Lines 22-23: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
fake_repo_root = tmp_path / 'agile_bot'
fake_repo_root.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:29): Lines 29-30: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(FileNotFoundError, match="Base actions directory not found"):
MCPServerGenerator(bot_directory=bot_directory)
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:131): Lines 131-138: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
bot_directory,
workspace_directory,
RenderOutputAction,
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:142): Lines 142-147: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_directory.mkdir(parents=True, exist_ok=True)
log_file = workspace_directory / 'activity_log.json'
from tinydb import TinyDB
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:149): Lines 149-152: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
log_data = read_activity_log(workspace_directory)
assert len(log_data) == 2
assert log_data[0]['action_state'] == 'story_bot.shape.render_output'
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:156): Lines 156-159: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Activity log creates file if it doesn't exist
GIVEN: workspace directory exists but no activity log
WHEN: Action tracks activity
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:164): Lines 164-165: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
log_file = workspace_directory / 'activity_log.json'
assert not log_file.exists()
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:168): Lines 168-173: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
action = RenderOutputAction(
bot_name='story_bot',
behavior='discovery',
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:194): Lines 194-197: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Render output action executes successfully
GIVEN: render_output action is initialized
WHEN: Action is executed
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:202): Lines 202-203: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'story_bot'
behavior = 'discovery'
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:205): Lines 205-209: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
action = RenderOutputAction(
bot_name=bot_name,
behavior=behavior,
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:212): Lines 212-213: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert action.bot_name == bot_name
assert action.behavior == behavior
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:225): Lines 225-228: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: All template variables are replaced in final instructions
GIVEN: Base instructions with {{render_configs}} and {{render_instructions}} placeholders
WHEN: Action loads and merges instructions with all injections
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:230): Lines 230-232: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
bot_name = 'test_bot'
behavior = 'shape'
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:235): Lines 235-237: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_dir = bot_directory / 'behaviors' / behavior
render_dir = behavior_dir / '2_content' / '2_render'
render_dir.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:240): Lines 240-258: Multiple inline steps (19 lines) should be extracted into a Given/When/Then helper function. Block:
{
'name': 'render_story_files',
'type': 'synchronizer',
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:270): Lines 270-273: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Formatted render_configs includes all fields referenced in instructions
GIVEN: Render configs with instructions, synchronizer, template, input, output fields
WHEN: Configs are formatted for injection
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:278): Lines 278-279: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
behavior = 'shape'
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:281): Lines 281-283: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_dir = bot_directory / 'behaviors' / behavior
render_dir = behavior_dir / '2_content' / '2_render'
render_dir.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:286): Lines 286-299: Multiple inline steps (14 lines) should be extracted into a Given/When/Then helper function. Block:
sync_config = render_dir / 'render_sync.json'
sync_config.write_text(
json.dumps({
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:302): Lines 302-314: Multiple inline steps (13 lines) should be extracted into a Given/When/Then helper function. Block:
template_config = render_dir / 'render_template.json'
template_config.write_text(
json.dumps({
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:317): Lines 317-321: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
action_obj = RenderOutputAction(
bot_name=bot_name,
behavior=behavior,
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:324): Lines 324-325: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_folder = action_obj._find_behavior_folder()
render_configs = action_obj._load_render_configs(behavior_folder)
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:331): Lines 331-332: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'render_sync' in formatted
assert 'render_template' in formatted
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:335): Lines 335-343: Multiple inline steps (9 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'Instructions:' in formatted or 'instructions' in formatted.lower()
assert 'Synchronizer:' in formatted or 'synchronizer' in formatted.lower()
assert 'synchronizers.test.TestSynchronizer' in formatted
...
- 🔴 **ERROR** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:346): Lines 346-348: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'Template:' in formatted or 'template' in formatted.lower()
assert 'templates/test-template.md' in formatted
assert 'test-output.md' in formatted
- 🔴 **ERROR** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:68): Lines 68-71: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
Given __pycache__ directories exist with .pyc files
When clear_python_cache is called
Then all __pycache__ directories are removed
...
- 🔴 **ERROR** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:74): Lines 74-78: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
cache_dirs = [
tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / '__pycache__',
tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / 'bot' / '__pycache__',
...
- 🔴 **ERROR** - [`test_restart_mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_restart_mcp_server.py:97): Lines 97-98: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
Note: This test requires actual MCP server to be running to be meaningful.
For now, just tests the function doesn't crash.
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:17): Lines 17-18: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
router = Router(workspace_root=tmp_path)
state_file = tmp_path / 'workflow_state.json'
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:24): Lines 24-25: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(FileNotFoundError, match="Workflow state file not found"):
router.determine_next_action_from_state(state_file)
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:30): Lines 30-31: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
router = Router(workspace_root=tmp_path)
state_file = tmp_path / 'workflow_state.json'
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:34): Lines 34-39: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
state_file.write_text(json.dumps({
'current_behavior': 'story_bot.shape',
'current_action': 'story_bot.shape.gather_context',
...
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:42): Lines 42-43: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(ValueError, match="no completed actions"):
router.determine_next_action_from_state(state_file)
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:48): Lines 48-49: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
router = Router(workspace_root=tmp_path)
state_file = tmp_path / 'workflow_state.json'
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:52): Lines 52-59: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
state_file.write_text(json.dumps({
'current_behavior': 'story_bot.shape',
'current_action': 'story_bot.shape.unknown_action',
...
- 🔴 **ERROR** - [`test_router_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_router_exceptions.py:62): Lines 62-63: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(ValueError, match="Unknown last action"):
router.determine_next_action_from_state(state_file)
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:77): Lines 77-80: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find behavior folder with number prefix
GIVEN: Behavior folder exists with number prefix (8_tests)
WHEN: find_behavior_folder is called with behavior name without prefix (tests)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:83): Lines 83-85: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
folder_name = '8_tests'
behavior_name = 'tests'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:93): Lines 93-94: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '8_tests'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:98): Lines 98-101: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find shape folder with number prefix
GIVEN: Behavior folder exists with number prefix (1_shape)
WHEN: find_behavior_folder is called with behavior name (shape)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:111): Lines 111-112: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '1_shape'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:116): Lines 116-119: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find exploration folder with number prefix
GIVEN: Behavior folder exists with number prefix (5_exploration)
WHEN: find_behavior_folder is called with behavior name (exploration)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:129): Lines 129-130: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '5_exploration'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:134): Lines 134-137: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Raises error when behavior folder doesn't exist
GIVEN: Behavior folder does not exist
WHEN: find_behavior_folder is called
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:140): Lines 140-141: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
behavior_name = 'nonexistent'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:144): Lines 144-145: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(FileNotFoundError, match='Behavior folder not found'):
Behavior.find_behavior_folder(bot_directory, bot_name, behavior_name)
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:149): Lines 149-152: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find prioritization folder with number prefix
GIVEN: Behavior folder exists as 2_prioritization
WHEN: find_behavior_folder is called with behavior name (prioritization)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:162): Lines 162-163: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '2_prioritization'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:167): Lines 167-170: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find scenarios folder with number prefix
GIVEN: Behavior folder exists as 6_scenarios
WHEN: find_behavior_folder is called with behavior name (scenarios)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:180): Lines 180-181: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '6_scenarios'
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:185): Lines 185-188: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Find examples folder with number prefix
GIVEN: Behavior folder exists as 7_examples
WHEN: find_behavior_folder is called with behavior name (examples)
...
- 🔴 **ERROR** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:198): Lines 198-199: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '7_examples'
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:604): Lines 604-607: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track activity when validate_rules action starts
GIVEN: behavior is 'exploration' and action is 'validate_rules'
WHEN: validate_rules action starts execution
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:624): Lines 624-627: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track activity when validate_rules action completes
GIVEN: validate_rules action started at timestamp
WHEN: validate_rules action finishes execution
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:638): Lines 638-645: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
action,
outputs={
'violations_count': 2,
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:649): Lines 649-656: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_directory,
expected_outputs={
'violations_count': 2,
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:660): Lines 660-663: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Track multiple validate_rules invocations across behaviors
GIVEN: activity log contains entries for shape and exploration validate_rules
WHEN: both entries are present
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:667): Lines 667-677: Multiple inline steps (11 lines) should be extracted into a Given/When/Then helper function. Block:
{
'action_state': 'story_bot.shape.validate_rules',
'timestamp': '2025-12-03T09:00:00Z',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:683): Lines 683-685: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert len(log_data) == 2
assert log_data[0]['action_state'] == 'story_bot.shape.validate_rules'
assert log_data[1]['action_state'] == 'story_bot.exploration.validate_rules'
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:689): Lines 689-692: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Activity log maintains chronological order
GIVEN: activity log contains 10 previous action entries
WHEN: validate_rules entry is appended
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:697): Lines 697-699: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
{'action_state': f'story_bot.discovery.action_{i}', 'timestamp': f'10:{i:02d}'}
for i in range(10)
])
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:706): Lines 706-708: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
log_data = read_activity_log(workspace_directory)
assert len(log_data) == 11
assert log_data[10]['action_state'] == 'story_bot.exploration.validate_rules'
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:720): Lines 720-724: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: validate_rules marks workflow as complete
GIVEN: validate_rules action is complete
AND: validate_rules is terminal action (next_action=null)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:737): Lines 737-741: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: validate_rules does NOT inject next action instructions
GIVEN: validate_rules action is complete
AND: validate_rules is terminal action
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:755): Lines 755-758: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workflow state shows all actions completed
GIVEN: validate_rules completes as final action
WHEN: Action tracks completion
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:769): Lines 769-772: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
action,
outputs={'violations_count': 0, 'workflow_complete': True},
duration=180
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:779): Lines 779-782: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Activity log records full workflow completion
GIVEN: validate_rules completes at timestamp
WHEN: Activity logger records completion
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:793): Lines 793-796: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
action,
outputs={'violations_count': 0, 'workflow_complete': True},
duration=180
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:803): Lines 803-807: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Workflow does NOT transition after validate_rules
GIVEN: validate_rules action is complete
AND: validate_rules is terminal action
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:820): Lines 820-823: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Behavior workflow completes at terminal action
GIVEN: exploration behavior has completed all 5 workflow actions
WHEN: validate_rules (terminal) is marked complete
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:827): Lines 827-828: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_directory, 'story_bot', 'exploration', 'validate_rules'
)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:838): Lines 838-842: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: validate_rules returns instructions with rules as supporting context
GIVEN: validate_rules action has base instructions and validation rules
WHEN: validate_rules action executes
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:849): Lines 849-851: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bot_directory, '1_shape', 'test_rule.json',
{'description': 'Test rule', 'examples': []}
)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:869): Lines 869-872: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
rules_data = action.inject_behavior_specific_and_bot_rules()
assert 'action_instructions' in rules_data, f"inject_behavior_specific_and_bot_rules must return 'action_instructions' key. Got: {rules_data}"
action_instructions_from_method = rules_data['action_instructions']
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:877): Lines 877-878: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'instructions' in result, "Result should contain 'instructions' key"
instructions = result['instructions']
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:881): Lines 881-888: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'base_instructions' in instructions, (
f"Expected 'base_instructions' in instructions, but got keys: {instructions.keys()}"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:892): Lines 892-894: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'clarification.json' in instructions_text or 'clarification' in instructions_text.lower(), (
f"base_instructions should contain the action instructions mentioning clarification.json. Got: {instructions_text[:500]}"
)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:897): Lines 897-903: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'validation_rules' in instructions, (
f"Expected 'validation_rules' in instructions, but got keys: {instructions.keys()}"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:908): Lines 908-914: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'content_to_validate' in instructions, (
f"Expected 'content_to_validate' in instructions, but got keys: {instructions.keys()}"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:916): Lines 916-925: Multiple inline steps (10 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'workspace_location' in content_info or 'project_location' in content_info, \
f"content_to_validate must contain 'workspace_location' or 'project_location' key: {content_info.keys()}"
location_key = 'workspace_location' if 'workspace_location' in content_info else 'project_location'
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:928): Lines 928-933: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
assert instructions.get('action') == 'validate_rules', (
"instructions should specify action='validate_rules'"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:936): Lines 936-942: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'report_path' in content_info, (
"content_to_validate should contain report_path where validation report should be saved"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:944): Lines 944-946: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert str(workspace_directory) in report_path or 'docs' in report_path, (
f"report_path should be in workspace directory, got: {report_path}"
)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:950): Lines 950-957: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: validate_rules provides report_path for saving validation report
GIVEN: validate_rules action executes
AND: workspace directory has docs/stories/ folder
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1026): Lines 1026-1030: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Scanner discovery extracts metadata and registers scanners
GIVEN: Rule files exist at specified paths
AND: Rule files contain scanner configurations
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1036): Lines 1036-1038: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
test_bot_dir = repo_root / 'agile_bot' / 'bots' / 'test_story_bot'
test_bot_dir.mkdir(parents=True, exist_ok=True)
setup_test_rules(repo_root, rule_file_paths, rule_file_content)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1041): Lines 1041-1046: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
action = ValidateRulesAction(
bot_name='test_story_bot',
behavior='shape',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1048): Lines 1048-1049: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
behavior = Behavior('shape', 'test_story_bot', test_bot_dir)
scanners = behavior.scanners
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1052): Lines 1052-1064: Multiple inline steps (13 lines) should be extracted into a Given/When/Then helper function. Block:
assert len(scanners) == expected_scanner_count, f"Expected {expected_scanner_count} scanner classes discovered, got {len(scanners)}"
for scanner_class in scanners:
assert isinstance(scanner_class, type), (
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1120): Lines 1120-1124: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Scanners detect violations in knowledge graph
GIVEN: Knowledge graph contains problems
AND: Rule file is specified
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1132): Lines 1132-1135: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
kg_file = workspace_directory / 'docs' / 'stories' / 'story-graph.json'
kg_file.parent.mkdir(parents=True, exist_ok=True)
kg_file.write_text(json.dumps(knowledge_graph, indent=2), encoding='utf-8')
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1138): Lines 1138-1143: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
test_bot_dir = repo_root / 'agile_bot' / 'bots' / 'test_story_bot'
action = ValidateRulesAction(
bot_name='test_story_bot',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1148): Lines 1148-1150: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
validation_rules = instructions['validation_rules']
assert len(validation_rules) > 0, "Instructions should contain validation rules"
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1152): Lines 1152-1167: Multiple inline steps (16 lines) should be extracted into a Given/When/Then helper function. Block:
for rule in validation_rules:
assert isinstance(rule, dict), f"Rule should be a dict, got: {type(rule)}"
assert 'rule_content' in rule, f"Rule must contain 'rule_content' key: {rule}"
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1169): Lines 1169-1171: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'base_instructions' in instructions, "Instructions must contain 'base_instructions' key"
base_instructions = instructions['base_instructions']
assert isinstance(base_instructions, list), "Base instructions should be a list"
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1183): Lines 1183-1186: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: ValidateRulesAction raises exception when story graph not found
GIVEN: Story graph file doesn't exist
WHEN: validate_rules action executes
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1189): Lines 1189-1190: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
from agile_bot.bots.base_bot.test.test_helpers import create_base_actions_structure
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1196): Lines 1196-1197: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(FileNotFoundError, match="Story graph file.*not found"):
action.do_execute(parameters={})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1201): Lines 1201-1204: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: ValidateRulesAction raises exception when story graph has syntax error
GIVEN: Story graph file exists but contains invalid JSON
WHEN: validate_rules action executes
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1207): Lines 1207-1208: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
from agile_bot.bots.base_bot.test.test_helpers import create_base_actions_structure
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1211): Lines 1211-1212: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
story_graph_file = docs_dir / 'story-graph.json'
story_graph_file.write_text('{ invalid json }', encoding='utf-8')
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1216): Lines 1216-1217: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises((json.JSONDecodeError, ValueError), match=".*"):
action.do_execute(parameters={})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1824): Lines 1824-1836: Multiple inline steps (13 lines) should be extracted into a Given/When/Then helper function. Block:
Tests various scope configurations:
- Single story
- Multiple stories
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1839): Lines 1839-1840: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_directory.mkdir(parents=True, exist_ok=True)
bootstrap_env(bot_directory, workspace_directory)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1843): Lines 1843-1844: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
story_graph_path = docs_stories_dir / 'story-graph.json'
story_graph_path.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1846): Lines 1846-1848: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
"description": "Stories must have scenarios",
"scanner": "agile_bot.bots.base_bot.src.scanners.scenarios_on_story_docs_scanner.ScenariosOnStoryDocsScanner"
})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1850): Lines 1850-1856: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
scope_config = test_case['scope_config']
if scope_config:
story_graph['_validation_scope'] = scope_config
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1859): Lines 1859-1860: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
validation_rules = instructions['validation_rules']
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1865): Lines 1865-1867: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
if isinstance(expected_stories_in_scope, list):
expected_stories_in_scope_set = set(expected_stories_in_scope)
elif expected_stories_in_scope is None:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1869): Lines 1869-1873: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
expected_stories_in_scope_set = set()
for epic in story_graph['epics']:
self._extract_story_names_from_epic(epic, expected_stories_in_scope_set)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1875): Lines 1875-1877: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
if isinstance(expected_violations_list, list):
expected_violations_set = set(expected_violations_list)
elif expected_violations_list is None:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1879): Lines 1879-1882: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
stories_with_scenarios = {"Select And Capture Tokens"}
if expected_stories_in_scope_set:
expected_violations_set = expected_stories_in_scope_set - stories_with_scenarios
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1884): Lines 1884-1889: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
all_story_names = set()
for epic in story_graph['epics']:
self._extract_story_names_from_epic(epic, all_story_names)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1894): Lines 1894-1896: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert violated_story_names.issubset(expected_stories_in_scope_set), \
f"Found violations for stories outside scope: {violated_story_names - expected_stories_in_scope_set}. " \
f"Expected scope: {expected_stories_in_scope_set}"
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1899): Lines 1899-1902: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
assert violated_story_names == expected_violations_set, \
f"Expected violations: {expected_violations_set}, but got: {violated_story_names}. " \
f"Missing: {expected_violations_set - violated_story_names}, " \
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1909): Lines 1909-1914: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
scope_config = {"increment_priorities": [1]}
expected = self.get_expected_story_names_for_scope(scope_config, story_graph)
assert "Select And Capture Tokens" in expected
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1917): Lines 1917-1922: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
scope_config = {"epic_names": ["Manage Mobs"]}
expected = self.get_expected_story_names_for_scope(scope_config, story_graph)
assert "Select And Capture Tokens" in expected
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1925): Lines 1925-1929: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
scope_config = {"epic_names": ["Manage Mobs", "Execute Mob Actions"]}
expected = self.get_expected_story_names_for_scope(scope_config, story_graph)
assert "Select And Capture Tokens" in expected  # Manage Mobs
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1932): Lines 1932-1934: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
scope_config = {"story_names": ["Select And Capture Tokens", "Handle Token Click And Intercept"]}
expected = self.get_expected_story_names_for_scope(scope_config, story_graph)
assert expected == {"Select And Capture Tokens", "Handle Token Click And Intercept"}
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1938): Lines 1938-1944: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Validate test file using test_file scope parameter
GIVEN: A test file exists with violations
AND: A rule with TestScanner exists
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1947): Lines 1947-1969: Multiple inline steps (23 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
story_graph = {
"epics": [
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1975): Lines 1975-1976: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_creates_order(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1980): Lines 1980-1982: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
"description": "Test classes must match story names exactly",
"scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1987): Lines 1987-1988: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
validation_rules = instructions['validation_rules']
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1990): Lines 1990-2000: Multiple inline steps (11 lines) should be extracted into a Given/When/Then helper function. Block:
assert len(all_violations) > 0, "TestScanner should detect violations in test file"
test_file_found_in_violations = any(
str(test_file) in str(v.get('location', '')) or
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2005): Lines 2005-2011: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Validate multiple test files using test_files scope parameter
GIVEN: Multiple test files exist with violations
AND: A rule with TestScanner exists
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2014): Lines 2014-2040: Multiple inline steps (27 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
story_graph = {
"epics": [
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2046): Lines 2046-2047: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_creates_order(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2054): Lines 2054-2055: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_cancels_order(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2059): Lines 2059-2061: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
"description": "Test classes must match story names exactly",
"scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2066): Lines 2066-2067: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
validation_rules = instructions['validation_rules']
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2075): Lines 2075-2080: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Verify that test files from scope parameters are actually passed to TestScanner
GIVEN: A test file exists
AND: A spy TestScanner that records knowledge_graph it receives
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2086): Lines 2086-2088: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
story_graph = {
"epics": []
}
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2091): Lines 2091-2094: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
docs_stories_dir = workspace_directory / 'docs' / 'stories'
docs_stories_dir.mkdir(parents=True, exist_ok=True)
story_graph_path = docs_stories_dir / 'story-graph.json'
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2097): Lines 2097-2100: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
test_file = workspace_directory / 'test_verify_scope.py'
test_file.write_text('''class TestVerifyScope:
def test_verifies_scope(self):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2106): Lines 2106-2107: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
class SpyTestScanner(TestScanner):
def scan(self, knowledge_graph: Dict[str, Any], rule_obj: Any = None) -> List[Dict[str, Any]]:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2118): Lines 2118-2125: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
rule_content = {
"description": "Test classes must match story names",
"scanner": "agile_bot.bots.base_bot.src.scanners.class_based_organization_scanner.ClassBasedOrganizationScanner"
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2128): Lines 2128-2132: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
action = ValidateRulesAction(
bot_name='test_bot',
behavior='write_tests',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2135): Lines 2135-2138: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
parameters = {
'test_file': str(test_file)
}
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2145): Lines 2145-2146: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
test_file_paths = [Path(str(test_file))]
test_knowledge_graph = story_graph.copy()
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2252): Lines 2252-2256: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Violation report generation in different formats
GIVEN: Violations have been detected
AND: Report format is specified
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2266): Lines 2266-2270: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
action = ValidateRulesAction(
bot_name='test_story_bot',
behavior='shape',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2277): Lines 2277-2280: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
if report_format == 'CHECKLIST':
assert 'checklist' in report, "CHECKLIST format should contain checklist key"
assert 'format' in report, "Report should contain format key"
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2282): Lines 2282-2291: Multiple inline steps (10 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'checklist' in report, "CHECKLIST format report must contain 'checklist' key"
checklist_text = report['checklist']
violation_count = checklist_text.count('- [ ]') if checklist_text != 'No violations found.' else 0
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2293): Lines 2293-2295: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'violations' in report, "Report should contain violations key"
assert isinstance(report['violations'], list), "Violations should be a list"
assert len(report['violations']) == expected_violation_count, f"Expected {expected_violation_count} violations, got {len(report['violations'])}"
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2298): Lines 2298-2304: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
if expected_violation_count > 0:
for violation in report['violations']:
assert validate_violation_structure(violation, ['rule', 'line_number', 'location', 'violation_message', 'severity']), (
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2491): Lines 2491-2494: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
SCENARIO: Scanner detects violations in bad examples
GIVEN: Scanner class path, behavior, bad example, and expected violation message
WHEN: Scanner is executed against bad example
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2502): Lines 2502-2503: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
scanner_class, error_msg = load_scanner_class(scanner_class_path)
assert scanner_class is not None, f"Failed to load scanner: {error_msg}"
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2506): Lines 2506-2510: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
rule_obj = Rule(
rule_file='test_rule.json',
rule_content={'scanner': scanner_class_path, 'description': 'Test rule'},
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2513): Lines 2513-2515: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
if bad_example is None and 'tests' in behavior:
test_file = workspace_directory / 'test_place_order.py'
test_file.parent.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2517): Lines 2517-2518: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
if 'class_based' in scanner_class_path.lower():
test_file.write_text('''class TestGenTools:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2520): Lines 2520-2521: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_creates_tool(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2523): Lines 2523-2531: Multiple inline steps (9 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {
'epics': [{'name': 'Places Order', 'sub_epics': [{'name': 'Validates Payment', 'story_groups': [{'stories': [{'name': 'Generate Bot Tools'}]}]}]}],
'test_files': [str(test_file)]
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2533): Lines 2533-2534: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_2():
assert user.name == 'John'
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2536): Lines 2536-2538: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'specification_match' in scanner_class_path.lower():
test_file.write_text('''def test_agent_init(self):
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2540): Lines 2540-2541: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
agent = Agent('story_bot')
assert agent.initialized
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2543): Lines 2543-2546: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
def test_process_order(self):
order = create_order()
result = process(order)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2553): Lines 2553-2554: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
test_file = workspace_directory / 'test_code.py'
test_file.parent.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2556): Lines 2556-2557: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
if 'useless_comments' in scanner_class_path.lower():
test_file.write_text('''def get_name(self):
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2560): Lines 2560-2561: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
Returns:
str: The name
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2566): Lines 2566-2567: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def load_state(self):
return self.state
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2569): Lines 2569-2573: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'intention_revealing' in scanner_class_path.lower():
test_file.write_text('''def process(data):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2575): Lines 2575-2581: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'separate_concerns' in scanner_class_path.lower():
test_file.write_text('''def calculate_total(items):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2583): Lines 2583-2591: Multiple inline steps (9 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'simplify_control_flow' in scanner_class_path.lower():
test_file.write_text('''def process(data):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2593): Lines 2593-2595: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'complete_refactoring' in scanner_class_path.lower():
test_file.write_text('''# Old way
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2599): Lines 2599-2600: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def new_process(data):
return data.process()
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2602): Lines 2602-2609: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'meaningful_context' in scanner_class_path.lower():
test_file.write_text('''def process():
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2611): Lines 2611-2616: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'minimize_mutable' in scanner_class_path.lower():
test_file.write_text('''def process(items):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2618): Lines 2618-2619: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'vertical_density' in scanner_class_path.lower():
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2621): Lines 2621-2635: Multiple inline steps (15 lines) should be extracted into a Given/When/Then helper function. Block:
long_function = 'def process_order(order):\n'
long_function += '    items = order.items\n'
long_function += '    discount = order.discount\n'
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2637): Lines 2637-2641: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
def handle_payment(payment):
process_payment(payment)
file = open('payment.log', 'w')
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2643): Lines 2643-2647: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'encapsulation' in scanner_class_path.lower():
test_file.write_text('''class Order:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2649): Lines 2649-2650: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def get_customer(self):
return self.customer.get_profile().get_address().get_street()
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2652): Lines 2652-2657: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'exception_classification' in scanner_class_path.lower():
test_file.write_text('''class DatabaseConnectionException(Exception):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2659): Lines 2659-2673: Multiple inline steps (15 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'error_handling_isolation' in scanner_class_path.lower():
test_file.write_text('''def process_order(order):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2675): Lines 2675-2678: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'third_party_isolation' in scanner_class_path.lower():
test_file.write_text('''from requests import get
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2680): Lines 2680-2683: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
def process_order(order):
response = get('https://api.example.com/orders')
s3 = client('s3')
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2685): Lines 2685-2693: Multiple inline steps (9 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'open_closed' in scanner_class_path.lower():
test_file.write_text('''def process_payment(payment):
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2695): Lines 2695-2700: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
bad_example = {'code_files': [str(test_file)]}
elif 'test_quality' in scanner_class_path.lower():
test_file.write_text('''def test_1():
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2702): Lines 2702-2703: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
def test_2():
assert user.name == 'John'
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2711): Lines 2711-2712: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
if isinstance(scanner_instance, TestScanner):
violations = []
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2714): Lines 2714-2718: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
test_files_to_scan = []
if bad_example:
if 'test_files' in bad_example:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2722): Lines 2722-2724: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
for test_file_path in test_files_to_scan:
file_path = Path(test_file_path)
if file_path.exists():
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2726): Lines 2726-2729: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
assert bad_example is not None, "bad_example must be provided for test scanners"
if 'knowledge_graph' in bad_example:
kg = bad_example['knowledge_graph']
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2732): Lines 2732-2736: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']}
if 'epics' not in kg:
kg = {}
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2738): Lines 2738-2739: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
if not violations and bad_example:
try:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2742): Lines 2742-2746: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
test_files_list = None
code_files_list = None
if 'test_files' in bad_example:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2748): Lines 2748-2750: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
test_files_list = [Path(cf) for cf in bad_example['code_files']]
if 'code_files' in bad_example:
code_files_list = [Path(cf) for cf in bad_example['code_files']]
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2752): Lines 2752-2755: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']}
violations = scanner_instance.scan(kg, rule_obj, test_files=test_files_list, code_files=code_files_list)
except Exception:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2759): Lines 2759-2765: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
violations = []
if bad_example and 'code_files' in bad_example:
for code_file_path in bad_example['code_files']:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2767): Lines 2767-2768: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
if not violations:
try:
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2770): Lines 2770-2773: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
code_files_list = None
if bad_example and 'code_files' in bad_example:
code_files_list = [Path(cf) for cf in bad_example['code_files']]
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2777): Lines 2777-2781: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
kg = {k: v for k, v in bad_example.items() if k not in ['test_files', 'code_files']} if bad_example else {}
violations = scanner_instance.scan(kg, rule_obj, code_files=code_files_list)
except Exception:
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2790): Lines 2790-2796: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
violation_messages = []
for v in violations:
assert 'violation_message' in v, f"Violation must contain 'violation_message' key: {v}"
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2799): Lines 2799-2802: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
for violation in violations:
assert validate_violation_structure(violation, ['rule', 'violation_message', 'severity']), (
f"Violation missing required fields: {violation}"
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2820): Lines 2820-2822: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class TestExampleStory:
def test_example_scenario(self):
assert True
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2827): Lines 2827-2829: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class TestAnotherStory:
def test_another_scenario(self):
assert True
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2848): Lines 2848-2850: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class TestExampleStory:
def test_scenario(self):
assert True
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2853): Lines 2853-2856: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
'rule_id': 'test_naming_rule',
'description': 'Test classes must follow naming convention',
'scanner': 'agile_bot.bots.base_bot.src.scanners.test_scanner.TestScanner'
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2864): Lines 2864-2866: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'violations' in result or 'report' in result, (
"ValidateCodeFilesAction should return violations or report"
)
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2873): Lines 2873-2888: Multiple inline steps (16 lines) should be extracted into a Given/When/Then helper function. Block:
verb_noun_rule_content = {
'description': 'Use verb-noun format for all story elements',
'scanner': 'agile_bot.bots.base_bot.src.scanners.verb_noun_scanner.VerbNounScanner',
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2890): Lines 2890-2891: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
'epics': [{'name': 'Bad Epic Name'}]  # Violation: noun-only format
})
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2895): Lines 2895-2897: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class TestExampleStory:
def test_scenario(self):
assert True
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2909): Lines 2909-2915: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'violations' in result or 'report' in result, (
"ValidateCodeFilesAction should return violations or report"
)
...
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2925): Lines 2925-2927: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class TestGeneratedStory:
def test_generated_scenario(self):
assert True
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2952): Lines 2952-2954: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class ExampleClass:
def example_method(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2957): Lines 2957-2959: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class AnotherClass:
def another_method(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2976): Lines 2976-2978: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
class GeneratedClass:
def generated_method(self):
pass
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3001): Lines 3001-3003: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert 'instructions' in result, (
"ValidateCodeFilesAction should return instructions even without file parameters"
)
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:247): Lines 247-249: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
completed = [
{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'}
]
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:261): Lines 261-265: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
completed = [
{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:45:00.000000'},
{'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:46:00.000000'},
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:270): Lines 270-277: Multiple inline steps (8 lines) should be extracted into a Given/When/Then helper function. Block:
states = ['gather_context', 'decide_planning_criteria',
'build_knowledge', 'validate_rules', 'render_output']
transitions = [
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:279): Lines 279-285: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
workflow = Workflow(
bot_name=bot_name,
behavior=behavior,
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:294): Lines 294-296: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bootstrap_env(bot_directory, workspace_directory)
workflow_file = workspace_directory / 'workflow_state.json'
assert not workflow_file.exists()
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:311): Lines 311-316: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
completed = [
{'action_state': f'{bot_name}.{behavior}.gather_context', 'timestamp': '2025-12-04T15:44:22.812230'},
{'action_state': f'{bot_name}.{behavior}.decide_planning_criteria', 'timestamp': '2025-12-04T15:45:00.000000'},
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:323): Lines 323-324: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
workspace_directory, bot_name, behavior, 'validate_rules', completed
)
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:358): Lines 358-389: Multiple inline steps (32 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_config = {
"behaviorName": "write_tests",
"description": "Test behavior: tests",
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:398): Lines 398-400: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
{'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
{'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
])
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:406): Lines 406-407: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_dir = bot_directory / 'behaviors' / behavior
behavior_dir.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:419): Lines 419-450: Multiple inline steps (32 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_config = {
"behaviorName": "write_tests",
"description": "Test behavior: tests",
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:461): Lines 461-466: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
from agile_bot.bots.base_bot.src.bot.bot import Behavior
behavior_instance = Behavior(
name=behavior,
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:469): Lines 469-472: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
expected_states = ['build_knowledge', 'render_output', 'validate_rules']
assert behavior_instance.workflow.states == expected_states, (
f"Should use order from behavior.json {expected_states}, got {behavior_instance.workflow.states}"
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:480): Lines 480-517: Multiple inline steps (38 lines) should be extracted into a Given/When/Then helper function. Block:
knowledge_behavior = '1_shape'
knowledge_behavior_dir = bot_directory / 'behaviors' / knowledge_behavior
knowledge_behavior_dir.mkdir(parents=True, exist_ok=True)
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:520): Lines 520-557: Multiple inline steps (38 lines) should be extracted into a Given/When/Then helper function. Block:
code_behavior = '7_write_tests'
code_behavior_dir = bot_directory / 'behaviors' / code_behavior
code_behavior_dir.mkdir(parents=True, exist_ok=True)
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:563): Lines 563-573: Multiple inline steps (11 lines) should be extracted into a Given/When/Then helper function. Block:
from agile_bot.bots.base_bot.src.bot.bot import Behavior
knowledge_behavior_instance = Behavior(
name=knowledge_behavior,
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:576): Lines 576-580: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
knowledge_expected_states = ['build_knowledge', 'validate_rules', 'render_output']
assert knowledge_behavior_instance.workflow.states == knowledge_expected_states, (
f"Knowledge behavior should have standard order {knowledge_expected_states}, "
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:583): Lines 583-587: Multiple inline steps (5 lines) should be extracted into a Given/When/Then helper function. Block:
code_expected_states = ['build_knowledge', 'render_output', 'validate_rules']
assert code_behavior_instance.workflow.states == code_expected_states, (
f"Code behavior should have reversed order {code_expected_states}, "
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:590): Lines 590-592: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
assert knowledge_behavior_instance.workflow.states != code_behavior_instance.workflow.states, (
"Different behaviors should have different action orders"
)
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:599): Lines 599-600: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_dir = bot_directory / 'behaviors' / behavior
behavior_dir.mkdir(parents=True, exist_ok=True)
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:603): Lines 603-620: Multiple inline steps (18 lines) should be extracted into a Given/When/Then helper function. Block:
actions_workflow = {
"actions": [
{
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:622): Lines 622-638: Multiple inline steps (17 lines) should be extracted into a Given/When/Then helper function. Block:
behavior_config = {
"behaviorName": "code",
"description": "Test behavior: code",
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:644): Lines 644-649: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
from agile_bot.bots.base_bot.src.bot.bot import Behavior
behavior_instance = Behavior(
name=behavior,
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:652): Lines 652-658: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
expected_transitions = [
{'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
{'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
...
- 🔴 **ERROR** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:661): Lines 661-667: Multiple inline steps (7 lines) should be extracted into a Given/When/Then helper function. Block:
transition_dict = {t['source']: t['dest'] for t in behavior_instance.workflow.transitions}
assert transition_dict['build_knowledge'] == 'render_output', (
"build_knowledge should transition to render_output"
...

#### Use Real Implementations: 79 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_cli_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_cli_exceptions.py:19): Line 19 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:173): Line 173 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria.py:22): Line 22 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:211): Line 211 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:298): Line 298 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:361): Line 361 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:445): Line 445 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:20): Line 20 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:376): Line 376 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:377): Line 377 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:393): Line 393 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:401): Line 401 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:737): Line 737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:757): Line 757 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:794): Line 794 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:884): Line 884 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:886): Line 886 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:947): Line 947 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:965): Line 965 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1029): Line 1029 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:1117): Line 1117 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:183): Line 183 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:229): Line 229 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:251): Line 251 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:293): Line 293 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:43): Line 43 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:41): Line 41 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:52): Line 52 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:63): Line 63 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:69): Line 69 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:82): Line 82 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:93): Line 93 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:101): Line 101 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:153): Line 153 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:243): Line 243 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:265): Line 265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_cli.py:277): Line 277 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:452): Line 452 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:457): Line 457 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:472): Line 472 has commented-out code - call production code directly, even if API doesn't exist yet
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:22): Line 22 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:23): Line 23 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:27): Line 27 uses fake/stub implementation - tests should call real production code directly
- 🟡 **WARNING** - [`test_mcp_generator_exceptions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_mcp_generator_exceptions.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:23): Line 23 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_utils.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_utils.py:33): Line 33 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:483): Line 483 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:490): Line 490 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:493): Line 493 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:576): Line 576 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:889): Line 889 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1075): Line 1075 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1082): Line 1082 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1089): Line 1089 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1096): Line 1096 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1110): Line 1110 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1553): Line 1553 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2156): Line 2156 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2265): Line 2265 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2272): Line 2272 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2273): Line 2273 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2355): Line 2355 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2363): Line 2363 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2596): Line 2596 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2597): Line 2597 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2713): Line 2713 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2731): Line 2731 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2737): Line 2737 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2751): Line 2751 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2758): Line 2758 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2766): Line 2766 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2774): Line 2774 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2776): Line 2776 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:218): Line 218 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:308): Line 308 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_workflow_action_sequence.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_workflow_action_sequence.py:519): Line 519 has commented-out code - call production code directly, even if API doesn't exist yet

### Cross-File Violations (Pass 2)

These violations were detected by analyzing all files together to find patterns that span multiple files.

#### Use Given When Then Helpers: 6 violation(s)

- 🔴 **ERROR** - [`test_close_current_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_close_current_action.py:42): Helper function "create_test_workflow" is defined in 2 different files. Consolidate into a shared helper file based on reuse scope. Found in: test_close_current_action.py:42, test_workflow_action_sequence.py:178
- 🔴 **ERROR** - [`test_complete_workflow_integration.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_complete_workflow_integration.py:107): Helper function "given_bot_name_and_behaviors_setup" is defined in 2 different files. Consolidate into a shared helper file based on reuse scope. Found in: test_complete_workflow_integration.py:107, test_generate_bot_server_and_tools.py:29
- 🟡 **WARNING** - [`test_build_agile_bots_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_agile_bots_helpers.py:21): Helper function "create_actions_workflow_json" is used in 8 files but defined in only one file (test_build_agile_bots_helpers.py). Consider moving to a higher-level helper file (sub-epic, epic, or global) based on reuse scope. Used in: test_base_action.py, test_invoke_bot_cli.py, test_bot_behavior_exceptions.py, test_close_current_action.py, test_invoke_bot_tool.py, test_generate_bot_server_and_tools.py, test_complete_workflow_integration.py, test_validate_knowledge_and_content_against_rules.py
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:555): Helper function "create_base_actions_structure" is used in 5 files but defined in only one file (test_generate_bot_server_and_tools.py). Consider moving to a higher-level helper file (sub-epic, epic, or global) based on reuse scope. Used in: test_invoke_bot_cli.py, test_invoke_bot_tool.py, test_generate_bot_server_and_tools.py, test_bot_behavior_exceptions.py, test_validate_knowledge_and_content_against_rules.py
- 🟡 **WARNING** - [`test_generate_bot_server_and_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py:35): Helper function "given_bot_name_and_behavior_setup" is used in 6 files but defined in only one file (test_generate_bot_server_and_tools.py). Consider moving to a higher-level helper file (sub-epic, epic, or global) based on reuse scope. Used in: test_gather_context.py, test_close_current_action.py, test_generate_bot_server_and_tools.py, test_decide_planning_criteria.py, test_validate_knowledge_and_content_against_rules.py, test_workflow_action_sequence.py
- 🟡 **WARNING** - [`test_invoke_bot_tool.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_bot_tool.py:83): Helper function "create_base_action_instructions" is used in 2 files but defined in only one file (test_invoke_bot_tool.py). Consider moving to a higher-level helper file (sub-epic, epic, or global) based on reuse scope. Used in: test_invoke_bot_tool.py, test_invoke_bot_cli.py

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
*... and 235 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\agile_bot\bots\base_bot\docs\stories\validation-report.md`
