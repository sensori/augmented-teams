# Validation Report - 7 Write Tests

**Generated:** 2025-12-14 04:26:58
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
  - `test\test_build_knowledge.py`
  - `test\test_decide_planning_criteria_action.py`
  - `test\test_execute_behavior_actions.py`
  - `test\test_gather_context.py`
  - `test\test_generate_cli.py`
  - `test\test_generate_mcp_tools.py`
  - `test\test_helpers.py`
  - `test\test_init_project.py`
  - `test\test_invoke_bot.py`
  - `test\test_invoke_cli.py`
  - `test\test_invoke_mcp.py`
  - `test\test_perform_behavior_action.py`
  - `test\test_render_output.py`
  - `test\test_validate_knowledge_and_content_against_rules.py`
  - **Total:** 14 test file(s)

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

**Total Violations:** 59
- **File-by-File Violations:** 59
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

#### Call Production Code Directly: 18 violation(s)

- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:71): Test method [test_generator_creates_workspace_rules_file_with_trigger_patterns](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:71) (line 71) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:107): Test method [test_rules_file_includes_bot_goal_and_behavior_descriptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:107) (line 107) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:158): Test method [test_rules_file_maps_trigger_patterns_to_tool_naming_conventions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:158) (line 158) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:188): Test method [test_generator_handles_file_write_errors_gracefully_creates_directory](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:188) (line 188) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:202): Test method [test_generator_handles_file_write_errors_with_clear_error_message](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:202) (line 202) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:219): Test method [test_full_awareness_generation_workflow](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:219) (line 219) does not call production code from src folder. Tests must import and call production code directly. If the code doesn't exist, the test should fail with ImportError or AttributeError, not silently pass.
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1237): Line 1237 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1238): Line 1238 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1239): Line 1239 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1240): Line 1240 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1243): Line 1243 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1246): Line 1246 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1258): Line 1258 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1265): Line 1265 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1266): Line 1266 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1269): Line 1269 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:570): Line 570 uses fake/stub implementation - tests should call real production code directly
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:740): Line 740 uses fake/stub implementation - tests should call real production code directly

#### Use Class Based Organization: 4 violation(s)

- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_epic_has_sub_epics](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly. Expected name based on epic/story: "Execute Behavior Actions - Epic Has Sub Epics"
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_story_has_scenarios](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly. Expected name based on epic/story: "Execute Behavior Actions - Story Has Scenarios"
- 🔴 **ERROR** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py): Test method [test_from_bot_with_path](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py) appears abbreviated - should match scenario name exactly. Expected name based on epic/story: "Execute Behavior Actions - From Bot With Path"
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py): Test file name "test_helpers" does not match any sub-epic name and test methods do not span multiple sub-epics - file should be named test_<sub_epic_name>.py.

#### Use Given When Then Helpers: 20 violation(s)

- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:521): Lines 521-523: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
folder_name = '8_tests'
behavior_name = 'tests'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:531): Lines 531-532: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '8_tests'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:549): Lines 549-550: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '1_shape'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:567): Lines 567-568: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '5_exploration'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:578): Lines 578-579: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
bot_name = 'test_bot'
behavior_name = 'nonexistent'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:583): Lines 583-584: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
with pytest.raises(FileNotFoundError, match='Behavior folder not found'):
Behavior.find_behavior_folder(bot_directory, bot_name, behavior_name)
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:601): Lines 601-602: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '2_prioritization'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:619): Lines 619-620: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '6_scenarios'
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:637): Lines 637-638: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert found_folder == behavior_folder
assert found_folder.name == '7_examples'
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:429): Lines 429-431: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_environment_variable_takes_precedence_over_agent_json(
self, bot_directory, workspace_directory, temp_workspace
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:451): Lines 451-452: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert os.environ['WORKING_AREA'] == str(override_workspace)
assert os.environ['WORKING_AREA'] != str(workspace_directory)
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:457): Lines 457-459: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_missing_agent_json_with_preconfig_env_var_works(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:483): Lines 483-485: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_bot_initializes_with_bootstrapped_directories(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:507): Lines 507-509: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_workflow_state_created_in_workspace_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:529): Lines 529-530: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
assert workflow_file.parent == workspace_directory
assert workflow_file.name == 'workflow_state.json'
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:539): Lines 539-541: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_bot_config_loaded_from_bot_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:566): Lines 566-568: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
def test_behavior_folders_resolved_from_bot_directory(
self, bot_directory, workspace_directory
):
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:585): Lines 585-586: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
expected_path = bot_directory / 'behaviors' / 'shape'
assert behavior_folder == expected_path
- 🔴 **ERROR** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:604): Lines 604-606: Multiple inline steps (3 lines) should be extracted into a Given/When/Then helper function. Block:
result1 = get_workspace_directory()
result2 = get_workspace_directory()
result3 = get_workspace_directory()
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2210): Lines 2210-2211: Multiple inline steps (2 lines) should be extracted into a Given/When/Then helper function. Block:
action, action_result = self._verify_action_setup_and_execution(bot_directory, workspace_directory)
instructions, content_info = self._verify_instructions_structure(action_result, workspace_directory)

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
*... and 220 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\agile_bot\bots\base_bot\docs\stories\validation-report.md`
