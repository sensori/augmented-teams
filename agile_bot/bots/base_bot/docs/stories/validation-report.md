# Validation Report - 7 Write Tests

**Generated:** 2025-12-14 20:27:57
**Project:** base_bot
**Behavior:** 7_write_tests
**Action:** validate_rules

## Summary

Validated story map and domain model against **31 validation rules**.

## Content Validated

- **Planning:** `planning.json`
- **Rendered Outputs:**
  - `build-bot-domain-model-description.md`
  - `build-bot-domain-model-diagram.md`
  - `story-graph.json`
  - `story-map-increments.md`
- **Test Files Scanned:**
  - `test\test_perform_behavior_action.py`
  - **Total:** 1 test file(s)

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

### Rule: Helper Extraction And Reuse
**Description:** Extract duplicate test setup to reusable helper functions and factory functions. Keep test bodies focused on specific behavior being tested. Balance shared context with test-specific setup. Avoid duplication through helper extraction. From BDD Rules 8.3 (Helper Extraction) and 4 (Balance Context Sharing with Localization).

### Rule: Match Specification Scenarios
**Description:** CRITICAL: Test variables, test methods, test assertiosn etc must match specification scenarios . Test names and steps describe the behavior from specification. Assertions verify exactly what the scenario states - no more, no less. Use exact variable names and terminology from specification.

### Rule: Mock Only Boundaries
**Description:** Mock ONLY at architectural boundaries: external APIs, network calls, uncontrollable services. DON'T mock internal business logic, classes under test, or file operations (use temp files). Mocking internal code defeats the purpose of tests. From BDD Rule 8.2 (Proper Mocking).

### Rule: No Fallbacks In Tests
**Description:** Tests must fail if a fallback or default branch is executed. Every assertion should cover the explicitly intended path so that regressions do not hide behind fallback/default handling.

### Rule: Production Code Explicit Dependencies
**Description:** PRODUCTION CODE RULE: Make dependencies explicit through constructor injection. Pass all external dependencies (file systems, APIs, services) as constructor parameters. No hidden global state or singleton access. Tests should easily inject test doubles when needed. Follow user's rule: 'Maximize use of constructor injection - objects should have external dependencies passed in at construction time'.

### Rule: Production Code Single Responsibility
**Description:** PRODUCTION CODE RULE: Each function/method should do ONE thing and do it well. No hidden side effects. Name reveals complete behavior. Keep functions under 20 lines. Extract multiple concerns into separate functions. Tests should verify single responsibility - if test needs multiple unrelated assertions, function probably does too much.

*... and 11 more rules*

## Violations Found

**Total Violations:** 28
- **File-by-File Violations:** 28
- **Cross-File Violations:** 0

### File-by-File Violations (Pass 1)

These violations were detected by scanning each file individually.

#### Map Sequential Spine Vs Optional Paths: 13 violation(s)

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

#### Stories Developed And Tested In Days: 4 violation(s)

- 🟡 **WARNING** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[0].sub_epics[1].name): Sub-epic "Generate CLI" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[0].name): Sub-epic "Init Project" has 1 1 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[1].sub_epics[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].name): Sub-epic "Perform Behavior Action" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[2].sub_epics[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].name): Sub-epic "Validate Knowledge & Content Against Rules" has 14 14 stories (should be 4-10)

#### Match Specification Scenarios: 2 violation(s)

- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2447): Test method [test_bot_paths_raises_error_when_working_area_not_set](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2447) has vague name - should clearly describe behavior from specification scenario
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2460): Test method [test_bot_paths_raises_error_when_bot_directory_not_set](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2460) has vague name - should clearly describe behavior from specification scenario

#### No Fallbacks In Tests: 1 violation(s)

- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2042): Line 2042 uses fallback/default value - tests should use explicit test data, not fallbacks

#### Use Class Based Organization: 1 violation(s)

- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py): Test method [test_get_next_behavior](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py) appears abbreviated - should match scenario name exactly

#### Use Given When Then Helpers: 7 violation(s)

- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2132): Lines 2132-2133: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_behavior is not None
assert found_behavior.name == '2_prioritization'
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2159): Lines 2159-2160: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert next_behavior is not None
assert next_behavior.name == '2_prioritization'
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2187): Lines 2187-2190: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
assert len(behavior_names) == 3
assert '1_shape' in behavior_names
assert '2_prioritization' in behavior_names
...
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2200): Lines 2200-2201: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
exists = behaviors.check_exists('1_shape')
not_exists = behaviors.check_exists('nonexistent')
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2204): Lines 2204-2205: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert exists is True
assert not_exists is False
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2450): Lines 2450-2455: Multiple inline steps (6 lines) should be extracted into a Given/When/Then helper function. Block:
import os
os.environ['BOT_DIRECTORY'] = str(bot_directory)
if 'WORKING_AREA' in os.environ:
...
- 🔴 **ERROR** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:2463): Lines 2463-2466: Multiple inline steps (4 lines) should be extracted into a Given/When/Then helper function. Block:
import os
os.environ['WORKING_AREA'] = str(tmp_path)
if 'BOT_DIRECTORY' in os.environ:
...

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
*... and 221 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\agile_bot\bots\base_bot\docs\stories\validation-report.md`
