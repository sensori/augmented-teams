### Command: /story-explore-correct

**[Purpose]:**
Correct acceptance criteria based on validation errors or user feedback.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 3: Story Exploration Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-explore correct [feature-doc-path] [chat-context]` — Correct acceptance criteria based on errors and chat context

---

## Action: CORRECT

**Purpose**: Correct acceptance criteria based on validation errors or user feedback

**Steps**:
1. **[User]** Invokes `/story-explore-correct` with validation errors or feedback context
2. **[AI Agent]** Reads validation results and user feedback
3. **[AI Agent]** Identifies corrections needed:
   - Missing Domain AC sections
   - Missing Behavioral AC for stories
   - AC using "Given" clauses (should be When/Then only)
   - AC using technical language (should be behavioral)
   - AC in story documents instead of feature documents
   - Missing consolidation documentation
   - Missing source material references
4. **[AI Agent]** Applies corrections:
   - Adds missing Domain AC sections to feature documents
   - Adds missing Behavioral AC to feature documents under stories
   - Converts "Given/When/Then" to "When/Then" format
   - Rewrites technical AC in behavioral language
   - Moves AC from story documents to feature documents
   - Documents consolidation decisions
   - Adds source material references
5. **[AI Agent]** Updates feature documents with corrections
6. **[Runner]** Saves corrected feature documents
7. **[AI Agent]** Presents correction summary to user

**Output**:
- Corrected feature documents with proper AC structure
- Correction summary showing what was fixed
- Suggestion to re-run validation

---

## Common Corrections

### 1. AC in Wrong Location
**Problem**: AC found in story documents
**Fix**: Move all AC to feature document, update story documents to reference feature doc

### 2. Wrong AC Format
**Problem**: AC uses "Given/When/Then" format
**Fix**: Convert to "When/Then" format (save "Given" for specifications)

### 3. Technical Language
**Problem**: AC uses code patterns or technical terms
**Fix**: Rewrite in behavioral language (user/system interactions)

### 4. Missing Domain AC
**Problem**: Feature document missing Domain AC section
**Fix**: Add Domain AC section with domain concepts, constraints, relationships

### 5. Missing Consolidation Decisions
**Problem**: No consolidation rationale documented
**Fix**: Document which ACs were consolidated and why

### 6. Incorrect Feature Document Structure
**Problem**: Notes, consolidation decisions, domain rules, or source material appear ABOVE acceptance criteria
**Fix**: Move all notes, consolidation decisions, domain rules, and source material sections BELOW all acceptance criteria
**Correct Order**: Feature Purpose → Domain AC → Stories (with Behavioral AC) → Notes → Consolidation Decisions → Domain Rules Referenced → Source Material

### 7. Missing Gear Emoji in Feature Document Filename
**Problem**: Feature document filename doesn't start with ⚙️ emoji
**Fix**: Rename file from `[Feature Name] - Feature Overview.md` to `⚙️ [Feature Name] - Feature Overview.md`
**Also Fix**: Update all story file references to use gear emoji filename

