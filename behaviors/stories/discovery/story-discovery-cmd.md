### Command: /story-discovery

**[Purpose]:**
Guide through discovery stage for next market increment. Refine marketable increments on story map, apply story mapping practices, and groom stories for next increment.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 2: Discovery Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-discovery generate [story-map-file]` — Generate discovery refinements for increment
* CLI: `python behaviors/stories/stories_runner.py story-discovery validate [story-map-file]` — Validate discovery refinements against principles
* CLI: `python behaviors/stories/stories_runner.py story-discovery execute [story-map-file]` — Execute full workflow (generate then validate)

---

## Action 1: GENERATE

**Purpose**: Refine marketable increments and groom stories for next increment

**Steps**:
1. **[User]** Invokes `/story-discovery` command with story map file
2. **[AI Agent]** READS source material section from story map:
   - Extracts "Source Material" section from bottom of story map
   - Identifies primary source document/content
   - Notes sections/pages already referenced during Shaping
   - **AUTOMATICALLY loads source material into context** (no need for user to re-attach)
3. **[AI Agent]** Checks prompting questions are answered in context
4. **[AI Agent]** If questions not answered, generates prompts to ask user
5. **[AI Agent]** Enumerates stories for increment(s) in focus:
   - **References SAME source material** used during Shaping
   - **References additional sections/pages** as needed for exhaustive decomposition
   - Enumerates ALL stories for increment(s) in focus
   - Identifies all permutations, formulas, validation rules, state transitions
6. **[AI Agent]** ⚠️ BEFORE finalizing, presents CONSOLIDATION REVIEW to user:
   - **IDENTIFIES** potential consolidation candidates (similar stories)
   - **LISTS QUESTIONS** that need domain expert answers
   - **DOCUMENTS ASSUMPTIONS** being made about same/different logic
   - **PRESENTS** Consolidation Decision Matrix to user
   - **WAITS** for user to confirm assumptions or provide corrections
   - **CRITICAL**: Do NOT automatically consolidate without user confirmation!
7. **[User]** Reviews consolidation questions and provides domain knowledge:
   - Answers which stories have same vs different logic
   - Clarifies formulas, validation rules, business rules
   - Approves consolidation decisions
8. **[AI Agent]** Applies user's consolidation decisions and generates final discovery:
   - Refines marketable increments on story map
   - Updates story map based on discovery insights and user input
   - Applies story mapping practices (from principles)
   - Grooms stories (identifies ambiguous/complex stories, suggests splits)
   - Adds story counts to other increments where exact stories unknown
9. **[AI Agent]** UPDATES source material section:
   - Adds "Discovery Refinements" subsection
   - Lists additional sections/pages referenced during Discovery
   - Notes specific areas explored in detail
   - Documents consolidation decisions and rationale
10. **[Runner]** Saves updated story map documents
11. **[Runner]** Returns updated documents to user

**Prompting Questions**:
- Which market increment are we focusing on for discovery?
- What new information or insights have been discovered?
- Are there any changes to business priorities or constraints?
- What is the target delivery timeline for this increment?

**Output**:
- Updated `<solution-folder>/docs/stories/map/[product-name]-story-map.md` with discovery refinements
- Updated `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md` with refined increment definitions
- Story count extrapolations for unexplored areas (e.g., "~15 stories")
- Discovery refinement notes identifying ambiguous or oversized stories
- Updated "Source Material" section with Discovery refinements:
  ```markdown
  ---
  ## Source Material
  
  **Primary Source**: [from Shaping phase]
  - Location: [path or description]
  - Sections Referenced (Shaping): [pages/chapters used during Shape]
  - Date Generated: [shape timestamp]
  
  **Discovery Refinements**: [current timestamp]
  - Increment in Focus: [increment name(s)]
  - Additional Sections Referenced: [new pages/chapters explored during Discovery]
  - Areas Elaborated: [specific features/stories decomposed exhaustively]
  
  **Context for Exploration**: When writing acceptance criteria, reference sections above for domain rules and behavioral details.
  ```

---

## Action 2: GENERATE FEEDBACK

**Purpose**: User reviews generated discovery refinements

**Steps**:
1. **[User]** Reviews updated story map documents
2. **[User]** Verifies increments are well-defined
3. **[User]** Confirms story counts are reasonable
4. **[User]** Checks that discovery insights are captured
5. **[User]** Provides feedback or approval

---

## Action 3: VALIDATE

**Purpose**: Validate discovery refinements against principles

**Steps**:
1. **[User]** Invokes `/story-discovery --action validate`
2. **[Runner]** Loads updated story map documents
3. **[Heuristic]** Validates refinement occurred (content changed)
4. **[Heuristic]** Validates story counts added for unexplored areas
5. **[Heuristic]** Validates increments are well-defined
6. **[Heuristic]** Validates story refinement applied (ambiguous/large stories identified)
7. **[Runner]** Returns validation results with violations and suggestions

**Validation Checks**:
- ✅ Story map content changed (refinement occurred)
- ✅ Story counts added for unexplored areas ("~X stories")
- ✅ Increments have clear definitions
- ✅ Refinement notes present (ambiguous/large stories flagged)

---

## Action 4: VALIDATE FEEDBACK

**Purpose**: User reviews validation results

**Steps**:
1. **[User]** Reviews validation report
2. **[User]** Addresses any violations or warnings
3. **[User]** Re-runs validation if changes made
4. **[User]** Proceeds when validation passes

