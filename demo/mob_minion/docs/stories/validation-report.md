# Validation Report - 8 Code

**Generated:** 2025-12-12 01:50:35
**Project:** mob_minion
**Behavior:** 8_code
**Action:** validate_rules

## Summary

Validated story map and domain model against **41 validation rules**.

## Content Validated

- **Clarification:** `clarification.json`
- **Planning:** `planning.json`
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

### Rule: Classify Exceptions By Caller Needs
**Description:** Design exceptions based on how callers will handle them. Create exception types based on caller's needs, use special case objects for predictable failures, and wrap third-party exceptions at boundaries.

### Rule: Eliminate Duplication
**Description:** CRITICAL: Every piece of knowledge should have a single, authoritative representation (DRY principle). Extract repeated logic into reusable functions and use abstraction to capture common patterns.

### Rule: Enforce Encapsulation
**Description:** CRITICAL: Hide implementation details and expose minimal interface. Make fields private by default, expose behavior not data, and follow Law of Demeter (principle of least knowledge).

### Rule: Enforce Team Formatting Consensus
**Description:** Formatting should be consistent and automated. Agree on formatting rules as a team, use automated formatters (prettier, black, gofmt), and enforce formatting in CI/CD pipeline.

### Rule: Follow Open Closed Principle
**Description:** Open for extension, closed for modification. Design for extension without modification, depend on interfaces/abstractions not concrete types, and use composition over inheritance.

### Rule: Handle Backward Compatibility
**Description:** When refactoring public interfaces, provide migration paths to avoid breaking existing code. Maintain backward compatibility during transitions and deprecate old interfaces gracefully.

### Rule: Isolate Error Handling
**Description:** Keep error handling separate from business logic. Extract try/catch blocks into dedicated functions and handle errors at appropriate abstraction levels.

### Rule: Isolate Third Party Code
**Description:** CRITICAL: Don't let external APIs spread through your codebase. Wrap third-party APIs behind your interfaces, create learning tests for external dependencies, and isolate boundary code from business logic.

### Rule: Keep Classes Single Responsibility
**Description:** CRITICAL: Each class should have one reason to change. Keep classes cohesive (methods/data interdependent), focus on single responsibility, and extract multi-responsibility classes.

### Rule: Keep Classes Small Compact
**Description:** Classes should be small and free of dead code. Keep classes under 200-300 lines, eliminate dead/unused code, and favor many small classes over few large ones.

### Rule: Keep Functions Single Responsibility
**Description:** CRITICAL: Functions should do one thing and do it well, with no hidden side effects. Each function must have a single, well-defined responsibility.

### Rule: Keep Functions Small Focused
**Description:** Functions should be small enough to understand at a glance. Keep functions under 20 lines when possible and extract complex logic into named helper functions.

### Rule: Maintain Abstraction Levels
**Description:** Code should flow from high-level concepts down to details. Follow 'newspaper metaphor' (high-level first), keep related functions close together, and step down one abstraction level at a time.

### Rule: Maintain Test Quality
**Description:** CRITICAL: Tests should be as clean as production code. Keep tests readable and maintainable, use descriptive test names, and follow FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely).

*... and 21 more rules*

## Violations Found

**Total Violations:** 29

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
*... and 219 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\demo\mob_minion\docs\stories\validation-report.md`
