### Command: /story-discovery generate

**[Purpose]:**
Generate discovery refinements for next market increment

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 2: Discovery Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-discovery generate [story-map-file]` — Generate discovery refinements for increment

---

## Generate Action

**Performer**: AI Agent + Runner

**Steps**:
1. Check prompting questions are answered (especially: which increment(s) are in focus?)
2. Load existing story map documents
3. Apply exhaustive logic decomposition for increment(s) in focus:
   - **Increment(s) in Focus**: List ALL stories explicitly (no ~X stories)
   - **Other Increments**: Use story counts for unexplored areas (~X stories)
   - Enumerate ALL permutations (prerequisite types, validation rules, calculation paths)
   - Use format: "User [verb] [noun] - and system [immediate response]"
   - NO extra notes, NO examples in story map
   - DO NOT add "Status: DISCOVERY" lines
   - DO NOT add day estimates - estimates require human entry and comparison
   - DO NOT create separate increment files
4. ⚠️ **CRITICAL STEP - CONSOLIDATION REVIEW (present to user BEFORE finalizing):**
   - **IDENTIFY** potential consolidation candidates (stories that look similar)
   - **LIST QUESTIONS** for user about whether logic is same or different
   - **DOCUMENT ASSUMPTIONS** about same/different formulas, validations, rules
   - **PRESENT** Consolidation Decision Matrix showing:
     - Stories under review
     - Assumed same/different logic
     - Questions for domain expert
     - Proposed consolidation if same
     - Proposed separation if different
   - **WAIT** for user to provide domain knowledge and confirm decisions
   - **DO NOT automatically consolidate or separate** without user confirmation!
5. After user provides consolidation decisions:
   - Apply user's answers about same vs different logic
   - Consolidate stories where user confirms same logic, different data
   - Keep separate stories where user confirms different logic
   - Document consolidation rationale in Discovery Notes
6. Generate updated story map with increments document
7. Save document to workspace (single file)
8. Return updated document to user

**Prompting Questions**:
- Which market increment are we focusing on for discovery?
- What new information or insights have been discovered?
- Are there any changes to business priorities or constraints?
- What is the target delivery timeline for this increment?

**Output Files**:
- `[product-name]-story-map-increments.md` (single file with NOW/NEXT/LATER increments)
- Discovery refinement notes (inline within increment document)

**Principles Applied**:
- Principle 2.1: Refining Marketable Increments on Story Map
- Principle 2.2: Story Mapping Practices
- Principle 2.3: Story Mapping Estimation and Counting
- Principle 2.4: Story Refinement
- Principle 2.5: Exhaustive Logic Decomposition (NEW)
- Principle 2.6: Story Format and Clarity (NEW)

**For detailed DO/DON'T examples and patterns, refer to:**
- `behaviors/stories/stories-rule.mdc` - Section 2: Discovery Principles
- `behaviors/stories/discovery/story-discovery-prompts.md` - Discovery workflow prompts

