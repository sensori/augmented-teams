### Command: /story-explore

**[Purpose]:**
Write acceptance criteria for stories in next increment. Define Domain AC (feature level) and Behavioral AC (story level) with exhaustive logic decomposition and consolidation review.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 3: Story Exploration Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-explore generate [feature-doc-path]` — Generate acceptance criteria for feature
* CLI: `python behaviors/stories/stories_runner.py story-explore validate [feature-doc-path]` — Validate acceptance criteria against principles
* CLI: `python behaviors/stories/stories_runner.py story-explore execute [feature-doc-path]` — Execute full workflow (generate then validate)

---

## Action 1: GENERATE

**Purpose**: Write acceptance criteria for stories with exhaustive AC decomposition and consolidation review

**Steps**:
1. **[User]** Invokes `/story-explore` command with story and feature context
2. **[AI Agent]** READS source material and domain artifacts:
   - Extracts "Source Material" section from story map including Discovery Refinements
   - **Checks for domain map** at `<solution-folder>/<system-name>-domain-map.txt` (if exists, loads relevant sections)
   - **Checks for domain interactions** at `<solution-folder>/<system-name>-domain-interactions.txt` (if available)
   - Identifies domain rules, formulas, validation patterns documented during Discovery
   - **AUTOMATICALLY loads source material into context** (no need for user to re-attach)
3. **[AI Agent]** Checks prompting questions are answered in context
4. **[AI Agent]** If questions not answered, generates prompts to ask user
5. **[AI Agent]** Enumerates acceptance criteria for story/feature in focus:
   - **References Discovery Refinements** for domain rules and formulas
   - **References domain map** (if exists) to extract relevant domain concepts for this feature
   - **References domain interactions** (if available) to understand how concepts work together
   - **For Domain AC**: Create hierarchical domain AC using FEATURE-SCOPED DOMAIN PERSPECTIVE (⭐ CRITICAL PATTERN):
     - **Define domain concepts through the lens of THIS feature's concerns**
     - **DO NOT copy entire domain model** - define only the facets/aspects THIS feature operates on
     - **Same concept, different facets per feature** (e.g., "Character" in Establish Identity shows identity fields; "Character" in Save Character shows persistence states)
     - Check higher levels first
     - **Step 1 - Check Higher Levels**:
       - Check story map for **Solution-level Domain AC** (concepts used across ALL epics)
       - Check for **Epic document** (`🎯 [Epic Name] - Epic Overview.md`) with epic-level Domain AC
       - Check for **Sub-Epic document** (`📂 [Sub-Epic Name] - Sub-Epic Overview.md`) if epic has sub-epics
       - Identify which concepts are already defined at higher levels
     - **Step 2 - Determine Hierarchy** (Feature → Sub-Epic → Epic → Solution):
       - **Shared across ALL epics** (Character, User, System) → Solution-level (story map)
       - **Shared across features in epic** (Ability for Create Character epic) → Epic-level
       - **Shared across features in sub-epic** → Sub-Epic-level (if applicable)
       - **Specific to THIS feature** (Save-specific state machine) → Feature-level only
     - **Step 3 - Feature Domain AC** (only feature-specific concepts):
       - Reference higher-level concepts (don't duplicate)
       - Define only concepts unique to this feature
       - **Structure**: Shared Concepts (references) → Feature Concepts → Behaviors → Rules
     - **Step 4 - Suggest Elevation**: If concepts are shared across multiple features, suggest moving to epic/solution level
     - Apply DDD principles from `behaviors/ddd/ddd-rule.mdc` (Principles 1, 4, 5, 7, 10)
     - **NOT** operations-first without business concepts
   - **Enumerates ALL acceptance criteria permutations** for each story
   - Identifies all validation paths, calculation branches, state transitions, exception cases
   - Applies exhaustive logic decomposition at AC level (Principle 2.5 applied to ACs)
6. **[AI Agent]** ⚠️ BEFORE finalizing, presents CONSOLIDATION REVIEW to user:
   - **IDENTIFIES** potential consolidation candidates (similar acceptance criteria)
   - **LISTS QUESTIONS** that need domain expert answers about logic similarity
   - **DOCUMENTS ASSUMPTIONS** being made about same/different logic at AC level
   - **PRESENTS** Consolidation Decision Matrix showing consolidation opportunities
   - **WAITS** for user to confirm assumptions or provide corrections
   - **CRITICAL**: Do NOT automatically consolidate ACs without user confirmation!
7. **[User]** Reviews AC consolidation questions and provides domain knowledge:
   - Answers which ACs use same vs different logic/formulas
   - Clarifies validation rules, calculation algorithms, state transitions
   - Approves or rejects consolidation decisions for each AC group
8. **[AI Agent]** Applies user's consolidation decisions and generates final acceptance criteria:
   - Writes Domain AC at feature level (domain concepts, constraints, relationships)
   - Writes Acceptance Criteria at story level (When/Then format - always behavioral)
   - Applies user's consolidation decisions to final AC set
   - Documents consolidation rationale in feature document
9. **[AI Agent]** UPDATES feature documents:
   - Adds Domain AC section (Core Concepts → Behaviors → Rules)
   - Adds Acceptance Criteria for each story (labeled "#### Acceptance Criteria", not "Behavioral")
   - Documents AC consolidation decisions and assumptions
   - References source material formulas and rules
10. **[Runner]** Saves updated feature documents
11. **[Runner]** Returns updated documents to user

**Prompting Questions**:
- Which feature(s) or story/stories are we exploring?
- Are there specific domain rules or edge cases not yet documented?
- Are there known exception paths or error scenarios?
- What are the critical validation rules for this feature?

**Output**:
- Updated feature document(s) in `<solution-folder>/docs/stories/map/[Epic]/[Feature]/`
- **Feature document filename**: `⚙️ [Feature Name] - Feature Overview.md` (gear emoji makes it obvious)
- **Domain AC** section defining domain concepts and relationships (feature level)
  - Structure: Core Concepts → Domain Behaviors → Domain Rules
- **Acceptance Criteria** for each story in When/Then format (NO "Given" clauses - save for spec)
  - Labeled "#### Acceptance Criteria" (NOT "Behavioral" - redundant at story level)
- **AC consolidation decisions** documented with rationale (BELOW all AC)
- **Source material** references to formulas and validation rules (BELOW all AC)
- **CRITICAL**: ALL AC written in feature document, NOT in story documents
- **CRITICAL**: All notes, consolidation decisions, domain rules, and source material go BELOW all acceptance criteria
- **Story documents** only contain story description and reference to feature document for AC

---

## Action 2: GENERATE FEEDBACK

**Purpose**: User reviews generated acceptance criteria

**Steps**:
1. **[User]** Reviews feature documents with acceptance criteria
2. **[User]** Verifies Domain AC captures domain concepts correctly
3. **[User]** Verifies Behavioral AC is testable and complete
4. **[User]** Checks consolidation decisions align with actual business logic
5. **[User]** Provides feedback or approval

---

## Action 3: VALIDATE

**Purpose**: Validate acceptance criteria against principles

**Steps**:
1. **[User]** Invokes `/story-explore --action validate`
2. **[Runner]** Loads feature documents with acceptance criteria
3. **[Heuristic]** Validates Domain AC present at feature level
4. **[Heuristic]** Validates Behavioral AC present for each story
5. **[Heuristic]** Validates AC uses behavioral language (not technical)
6. **[Heuristic]** Validates AC consolidation review occurred
7. **[Runner]** Returns validation results with violations and suggestions

**Validation Checks**:
- ✅ Domain AC present at feature level
- ✅ Behavioral AC present for each story
- ✅ AC written in Given/When/Then or When/Then format
- ✅ AC uses behavioral language (not code patterns)
- ✅ AC consolidation review documented
- ✅ Source material references included

---

## Action 4: VALIDATE FEEDBACK

**Purpose**: User reviews validation results

**Steps**:
1. **[User]** Reviews validation report
2. **[User]** Addresses any violations or warnings
3. **[User]** Re-runs validation if changes made
4. **[User]** Proceeds when validation passes




