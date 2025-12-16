# Validation Report - Shape

**Generated:** 2025-12-16 13:30:53
**Project:** mob_minion
**Behavior:** shape
**Action:** validate_rules

## Summary

Validated story map and domain model against **41 validation rules**.

## Content Validated

- **Clarification:** `clarification.json`
- **Rendered Outputs:**
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

### Rule: Apply 7 Plus Minus 2 Hierarchy
**Description:** Apply 7±2 rule for hierarchy: epics contain 4-9 sub-epics, sub-epics contain 4-9 stories. Split when exceeding, merge when below minimum.

### Rule: Avoid Noun Redundancy
**Description:** When shaping stories, avoid noun redundancy in domain and concept names

### Rule: Avoid Technical Abstractions
**Description:** CRITICAL: Domain concepts must stay at the domain level, even if concrete. Don't separate technical details from domain concepts—they should be the same (class vs object vs file—all represent the same domain concept).

### Rule: Avoid Technical Implementation Language
**Description:** When shaping stories, avoid technical implementation language in user-facing story elements

### Rule: Avoid Technical Stories
**Description:** Technical stories represent implementation tasks that do not describe system behavior. They are normally avoided in favor of user stories and system stories. When technical stories are necessary, they should be marked with story_type: 'technical' and kept minimal.

### Rule: Balance Fine Grained Testable Stories
**Description:** Balance fine-grained stories with testable and valuable independent units. Stories must deliver value and be independently testable.

### Rule: Chain Dependencies Properly
**Description:** CRITICAL: Domain concepts must chain dependencies properly with constructor injection. Map dependencies in a chain: highest-level object → collaborator → sub-collaborator. Inject collaborators at construction time so methods can use them without passing them as parameters. Access sub-collaborators through their owning objects.

### Rule: Create Lightweight Precise Docs
**Description:** Create lightweight but precise documentation during shaping. Focus on structure and scope, not detailed specifications.

### Rule: Delegate To Lowest Level
**Description:** CRITICAL: Domain concepts must delegate responsibilities to the lowest-level object that can handle them. If a collection class can do something, delegate to it rather than implementing it in the parent.

### Rule: Discover Relationships From Story Map
**Description:** Domain Discovery determines relationships and responsibilities between core domain objects by walking through the story map, then suggests story refinements to rebuild the story map to complement the domain model.

### Rule: Encapsulate Through Properties
**Description:** CRITICAL: Domain concepts must encapsulate state and behavior through properties. Properties control access to object state, hide internal representation, and allow objects to manage their own data. Objects expose properties representing what they are or contain, not raw data access methods.

### Rule: Enforce Behavioral Journey Flow
**Description:** When shaping stories, CRITICAL: Stories must show user/system journey flow, not just list operations. Stories must include context (when/why actions happen) and connect logically. Order by user journey, not technical sequential_order.

### Rule: Enforce Functional Accomplishment
**Description:** CRITICAL: Stories must represent complete functional accomplishments, not data access operations or implementation steps. Stories must deliver value independently.

### Rule: Enforce Specificity In Stories
**Description:** CRITICAL: Stories must be specific about what, when, why, and who. Generic operations like 'Add Sub-Epic' or 'Read Epics' are insufficient - stories must include context and specificity.

*... and 21 more rules*

## Violations Found

✅ **No violations found.** All rules passed validation.

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
*... and 222 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\demo\mob_minion\docs\stories\validation-report.md`
