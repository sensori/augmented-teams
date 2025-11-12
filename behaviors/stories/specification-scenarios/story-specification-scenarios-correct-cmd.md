### Command: /story-specification-scenarios-correct

**[Purpose]:**
Correct scenario specifications based on validation errors or user feedback, particularly Given statement state violations.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 4: Specification Scenarios Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-specification-scenarios correct [story-doc-path] [chat-context]` — Correct scenarios based on errors and chat context

---

## Action: CORRECT

**Purpose**: Correct scenario specifications based on validation errors or user feedback

**Steps**:
1. **[User]** Invokes `/story-specification-scenarios-correct` with validation errors or feedback context
2. **[AI Agent]** Reads validation results and user feedback
3. **[AI Agent]** Identifies corrections needed:
   - **Given statements using action-oriented language** (Principle 4.1)
   - Missing Scenarios section
   - Scenarios missing proper Given/When/Then structure
   - Missing Background for repeated Given steps
   - Scenario Outline missing Examples table
   - Scenarios using technical language instead of behavioral language
   - Scenarios not covering all acceptance criteria
   - Missing edge cases or error cases
4. **[AI Agent]** Applies corrections:
   - **Converts action-oriented Given to state-oriented Given** (Principle 4.1)
     - "user is on screen" → "screen is displayed"
     - "user logged in" → "user is authenticated"
     - "user navigated to page" → "page is displayed"
   - Adds missing Scenarios section to story documents
   - Adds proper Given/When/Then structure to scenarios
   - Adds Background for repeated Given steps (if 3+ scenarios share Given)
   - Adds Examples table to Scenario Outline
   - Rewrites technical language in behavioral language
   - Adds missing scenarios to cover all acceptance criteria
   - Adds edge cases and error cases
5. **[AI Agent]** Updates story documents with corrections
6. **[Runner]** Saves corrected story documents
7. **[AI Agent]** Presents correction summary to user

**Output**:
- Corrected story documents with proper scenario structure
- Correction summary showing what was fixed
- Suggestion to re-run validation

---

## Common Corrections

### 1. Given Statements Using Action-Oriented Language (Principle 4.1)
**Problem**: Given statements describe actions instead of states
**Examples**:
- ❌ "Given user is on the character creation screen"
- ❌ "Given user logged in"
- ❌ "Given user navigated to page"
- ❌ "Given user clicked button"

**Fix**: Convert to state-oriented language (BDD-inspired patterns)
**Examples**:
- ✅ "Given character creation screen is displayed"
- ✅ "Given user is authenticated"
- ✅ "Given page is displayed"
- ✅ "Given button has been activated"

**State Patterns to Use**:
- "that has been [past participle]" - completed states (e.g., "character has been created")
- "that is being [verb]" - ongoing states (e.g., "character is being edited")
- "that is [adjective/noun]" - current states (e.g., "screen is displayed", "user is authenticated")
- "that has [noun]" - possession states (e.g., "character has invalid data")

### 2. Missing Scenarios Section
**Problem**: Story document missing Scenarios section
**Fix**: Add `## Scenarios` section with at least one scenario

### 3. Missing Given/When/Then Structure
**Problem**: Scenarios don't follow proper Gherkin structure
**Fix**: Ensure each scenario has:
- **Given** (STATE - not action)
- **When** (action/trigger)
- **Then** (expected outcome)
- **And/But** (optional continuation/negative assertion)

### 4. Missing Background for Repeated Given
**Problem**: Multiple scenarios repeat same Given steps
**Fix**: Extract common Given steps to Background section (if 3+ scenarios share steps)

### 5. Scenario Outline Missing Examples
**Problem**: Scenario Outline defined but no Examples table
**Fix**: Add Examples table with parameter values in | column | format

### 6. Technical Language in Scenarios
**Problem**: Scenarios use code patterns or technical terms
**Fix**: Rewrite in behavioral language:
- ❌ "When POST /orders endpoint is called"
- ✅ "When user submits order"
- ❌ "Then database record is created"
- ✅ "Then order is saved"

### 7. Missing Scenario Coverage
**Problem**: Not all acceptance criteria have corresponding scenarios
**Fix**: Add scenarios to cover:
- All acceptance criteria from feature document
- Happy path (main success flow)
- Edge cases (boundary conditions)
- Error cases (failure handling)

### 8. And Statements in Wrong Context
**Problem**: And statements checked for state-orientation when they follow When/Then/But
**Note**: The heuristic correctly tracks context - And after Given is validated, And after When/Then/But is not

---

## Validation After Correction

After applying corrections, suggest user run validation again:

```
python behaviors/stories/stories_runner.py story-specification-scenarios validate [story-doc-path]
```

Or use test script:
```python
python test_validation.py
```

---

## Reference

**BDD State Patterns**: See `behaviors/bdd/bdd-rule.mdc` Section 2 (Fluency, Hierarchy, and Storytelling)
**Story Rules**: See `behaviors/stories/stories-rule.mdc` Section 4 (Specification Scenarios Principles)
**Template**: See `behaviors/stories/specification-scenarios/scenario-template.md`

