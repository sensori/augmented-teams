# Validation Report - Shape

**Generated:** 2025-12-16 13:53:03
**Project:** mob_minion
**Behavior:** shape
**Action:** validate_rules

## Summary

Validated story map and domain model against **41 validation rules**.

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

**Total Violations:** 60
- **File-by-File Violations:** 60
- **Cross-File Violations:** 0

### File-by-File Violations (Pass 1)

These violations were detected by scanning each file individually.

#### Maintain Verb Noun Consistency: 9 violation(s)

- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].sub_epics[0].story_groups[0].stories[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].story_groups[0].stories[0].name): Story name "Creates New Mob Container" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[2].sub_epics[0].story_groups[0].stories[1].name): Story name "Minions move toward target as needed" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].story_groups[0].stories[1].name): Story name "Creates New Mob from Template" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")

#### Map Sequential Spine Vs Optional Paths: 5 violation(s)

- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements

#### Stories Developed And Tested In Days: 4 violation(s)

- 🟡 **WARNING** - [`epics[0].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].name): Sub-epic "Create and Configure Mob" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[1].name): Sub-epic "Modify Mob Membership" has 2 2 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].sub_epics[0].name): Sub-epic "Assign Strategy to Mob" has 3 3 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[3].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].name): Sub-epic "Manage Templates" has 3 3 stories (should be 4-10)

#### Story Names Must Follow Verb Noun Format: 9 violation(s)

- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].sub_epics[0].story_groups[0].stories[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].story_groups[0].stories[0].name): Story name "Creates New Mob Container" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[2].sub_epics[0].story_groups[0].stories[1].name): Story name "Minions move toward target as needed" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].story_groups[0].stories[1].name): Story name "Creates New Mob from Template" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")

#### Use Verb Noun Format For Story Elements: 9 violation(s)

- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].domain_concepts[1]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].domain_concepts[1]): Unknown name "Minion" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[0].sub_epics[0].story_groups[0].stories[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].story_groups[0].stories[0].name): Story name "Creates New Mob Container" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[1].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].domain_concepts[0]): Unknown name "Strategy" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[2].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[2].sub_epics[0].story_groups[0].stories[1].name): Story name "Minions move toward target as needed" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].domain_concepts[0]`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].domain_concepts[0]): Unknown name "MobTemplate" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")
- 🔴 **ERROR** - [`epics[3].sub_epics[0].story_groups[0].stories[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].story_groups[0].stories[1].name): Story name "Creates New Mob from Template" uses third-person singular verb form ("Creates") - use base verb form instead (e.g., "Creat Multiple Tokens" not "Creates Multiple Tokens")

#### Apply 7 Plus Minus 2 Hierarchy: 4 violation(s)

- 🟡 **WARNING** - [`epics[0].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].name): Sub-epic "Create and Configure Mob" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[1].name): Sub-epic "Modify Mob Membership" has 2 2 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].sub_epics[0].name): Sub-epic "Assign Strategy to Mob" has 3 3 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[3].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].name): Sub-epic "Manage Templates" has 3 3 stories (should be 4-10)

#### Avoid Technical Implementation Language: 5 violation(s)

- 🔴 **ERROR** - [`Create and Configure Mob`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Create and Configure Mob): Story element "Create and Configure Mob" uses technical implementation verb "create" - use business language focusing on user experience
- 🔴 **ERROR** - [`Creates New Mob Container`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Creates New Mob Container): Story element "Creates New Mob Container" uses technical implementation verb "create" - use business language focusing on user experience
- 🔴 **ERROR** - [`Configure Strategy`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Configure Strategy): Story element "Configure Strategy" uses technical implementation verb "configure" - use business language focusing on user experience
- 🔴 **ERROR** - [`Saves Mob Configuration as Template`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Saves Mob Configuration as Template): Story element "Saves Mob Configuration as Template" uses technical implementation phrase "configuration" - focus on what user experiences, not how it's implemented
- 🔴 **ERROR** - [`Creates New Mob from Template`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Creates New Mob from Template): Story element "Creates New Mob from Template" uses technical implementation verb "create" - use business language focusing on user experience

#### Enforce Specificity In Stories: 4 violation(s)

- 🔴 **ERROR** - [`epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].name): Epic name "Manage Mobs" is too generic - add context (e.g., "Process Order Payment" not "Process Payment")
- 🔴 **ERROR** - [`epics[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].name): Epic name "Configure Strategy" is too generic - add context (e.g., "Process Order Payment" not "Process Payment")
- 🔴 **ERROR** - [`epics[3].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].name): Epic name "Mob Templates" is too generic - add context (e.g., "Process Order Payment" not "Process Payment")
- 🔴 **ERROR** - [`epics[3].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].name): Sub_epic name "Manage Templates" is too generic - add context (e.g., "Process Order Payment" not "Process Payment")

#### Establish Spine Vs Optional Enhanced Behavior: 5 violation(s)

- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements

#### Prevent Implementation Details As Stories: 2 violation(s)

- 🔴 **ERROR** - [`Create and Configure Mob`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Create and Configure Mob): Story "Create and Configure Mob" appears to be an implementation operation - should be a step within a story that describes user/system outcome
- 🔴 **ERROR** - [`Configure Strategy`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/Configure Strategy): Story "Configure Strategy" appears to be an implementation operation - should be a step within a story that describes user/system outcome

#### Size Stories 3 To 12 Days: 4 violation(s)

- 🟡 **WARNING** - [`epics[0].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[0].name): Sub-epic "Create and Configure Mob" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[0].sub_epics[1].name): Sub-epic "Modify Mob Membership" has 2 2 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[1].sub_epics[0].name): Sub-epic "Assign Strategy to Mob" has 3 3 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[3].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/demo/mob_minion/epics[3].sub_epics[0].name): Sub-epic "Manage Templates" has 3 3 stories (should be 4-10)

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
*... and 230 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\demo\mob_minion\docs\stories\validation-report.md`
