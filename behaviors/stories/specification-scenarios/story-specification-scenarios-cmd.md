### Command: /story-specification-scenarios

**[Purpose]:**
Create story specification scenarios by filling in the Scenarios section of story documents. Creates detailed Given/When/Then scenarios including Background and Scenario Outline patterns. Covers happy path, edge cases, and error cases based on the acceptance criteria already written.

**[Rule]:**
- `behaviors/stories/stories-rule.mdc` - Story writing practices and standards
- Applies principles: Universal (0.1, 0.2), Phase 4 Specification Scenarios (4.1)

**[Runner]:**
```bash
# Generate scenarios for story documents
python behaviors/stories/stories_runner.py story-specification-scenarios generate

# Validate scenarios
python behaviors/stories/stories_runner.py story-specification-scenarios validate

# Combined generate + validate
python behaviors/stories/stories_runner.py story-specification-scenarios execute
```

---

## Action 1: GENERATE

**Purpose**: Fill in Scenarios section of story documents with detailed Given/When/Then scenarios

### Step 1: Prompting Questions (Clarification) - MANDATORY FIRST STEP
**Performer**: AI Agent → User

**CRITICAL**: ALWAYS ask questions BEFORE generating. DO NOT skip this step.

**Scope Detection** (Determine what user wants):
- **@Feature Folder** or folder path → Process ALL stories in feature
- **@Epic Folder** → Process ALL stories in all features within epic
- **List of @story files** → Process all listed stories
- **Single @story file** → Process that story only
- **Feature name mentioned** → Find feature folder, process ALL stories
- **If unclear** → ASK which scope to use

**MANDATORY Questions to ask**:

1. **Scope Confirmation** (ALWAYS SHOW - NEVER SKIP):
   ```
   I found the following stories in [scope name]:
   1. Story Name 1
   2. Story Name 2
   3. Story Name 3
   
   Should I generate scenarios for:
   - All X stories (recommended when folder/feature provided)
   - Specific stories only (please specify which ones)
   - Ask me about each one before generating
   ```
   **Wait for user response before proceeding**

2. What are the main user flows or system flows to document?
   - Happy path scenarios?
   - Alternative paths or variations?

3. Are there any edge cases or alternative paths to consider?
   - Boundary conditions?
   - Error conditions?
   - Exceptional cases?

4. Do scenarios have repeated Given steps that could use Background?
   - Common setup across scenarios?
   - Shared context?

5. Are there scenarios with multiple value combinations (need Scenario Outline)?
   - Parameterized testing?
   - Multiple examples of same behavior?

**Decision Point**: If user answers are unclear or insufficient, ask follow-up questions before proceeding.
**DO NOT PROCEED** to Step 2 until user confirms scope and answers questions.

### Step 2: Review Acceptance Criteria
**Performer**: AI Agent

**Actions**:
1. Read story document to get existing acceptance criteria
2. Review feature document for domain and behavioral AC
3. Identify scenarios needed to cover all acceptance criteria
4. Determine scenario types:
   - Happy path scenarios (normal flow)
   - Edge case scenarios (boundary conditions)
   - Error case scenarios (failure conditions)
   - Scenario Outline candidates (parameterized)

**Decision Point**: If acceptance criteria are missing or unclear, warn user and suggest running `/story-explore` first.

### Step 3: Generate Scenario Structure
**Performer**: AI Agent + Runner (Code)

**Actions**:
1. **Determine Background** (if applicable):
   - Identify repeated Given steps across scenarios
   - Create Background section with common context
   
2. **Create Happy Path Scenarios**:
   - Main success scenarios
   - Use Given/When/Then/And/But structure
   - Link to acceptance criteria
   
3. **Create Edge Case Scenarios**:
   - Boundary conditions
   - Alternative paths
   - Special cases
   
4. **Create Error Case Scenarios**:
   - Failure conditions
   - Error handling
   - Invalid inputs
   
5. **Create Scenario Outlines** (if needed):
   - Parameterized scenarios with <placeholder> syntax
   - Examples table with | column | format
   - Multiple value combinations

**Decision Point**: If scenarios don't cover all acceptance criteria, add more scenarios.

### Step 4: Generate Scenario Content
**Performer**: Runner (Code)

**Actions**:
1. Use template: `behaviors/stories/specification-scenarios/scenario-template.md`
2. Fill in Scenarios section of story document
3. Use proper Gherkin keywords: Given/When/Then/And/But
4. Use Background for repeated Given steps
5. Use Scenario Outline for parameterized scenarios
6. Ensure behavioral language (not technical)

**Output**: Story document with Scenarios section filled in

### Step 5: Present Generated Scenarios
**Performer**: AI Agent → User

**Actions**:
1. Show generated scenarios
2. Highlight:
   - Number of scenarios created (happy path, edge cases, error cases)
   - Use of Background (if any)
   - Use of Scenario Outline (if any)
   - Coverage of acceptance criteria
3. Ask for user review

---

## Action 2: GENERATE FEEDBACK

**Purpose**: User reviews and provides feedback on generated scenarios

### Step 1: User Review
**Performer**: User

**Review Checklist**:
- [ ] Do scenarios cover all acceptance criteria?
- [ ] Are happy path, edge cases, and error cases included?
- [ ] Is Background used appropriately for repeated Given steps?
- [ ] Is Scenario Outline used for parameterized scenarios?
- [ ] Are scenarios written in behavioral language (not technical)?
- [ ] Are scenarios clear and understandable?

### Step 2: User Feedback
**Performer**: User → AI Agent

**Options**:
1. **Accept**: Scenarios are good, proceed to validation
2. **Revise**: Scenarios need changes (provide specific feedback)
3. **Add More**: Need additional scenarios for uncovered cases
4. **Clarify**: Need more information about specific scenarios

**Decision Point**: If revisions needed, go back to Step 3 of Action 1.

---

## Action 3: VALIDATE

**Purpose**: Validate scenario structure and completeness

### Step 1: Run Validation
**Performer**: Runner (Code) + AI Agent

**Validations**:
1. **Structure Validation**:
   - ✅ Scenarios section exists
   - ✅ Proper Given/When/Then structure
   - ✅ Background used correctly (if present)
   - ✅ Scenario Outline has Examples table (if present)
   
2. **Content Validation**:
   - ✅ Behavioral language (not technical/code)
   - ✅ Covers all acceptance criteria
   - ✅ Happy path included
   - ✅ Edge cases considered
   - ✅ Error cases included
   
3. **Gherkin Validation**:
   - ✅ Proper keyword usage (Given/When/Then/And/But)
   - ✅ Background has only Given/And steps
   - ✅ Scenario Outline uses <parameter> syntax
   - ✅ Examples table has proper | format |

**Decision Point**: If validation fails, present violations to user.

### Step 2: Apply Heuristics
**Performer**: AI Agent (using StorySpecificationScenariosHeuristic)

**Heuristics**:
1. Check for missing scenarios (gaps in coverage)
2. Check for technical language in scenarios
3. Check for proper Gherkin structure
4. Check for Background misuse
5. Check for Scenario Outline without Examples table
6. Check for missing When...Then patterns

**Output**: Validation report with violations (if any)

### Step 3: Present Validation Results
**Performer**: AI Agent → User

**Actions**:
1. Show validation results
2. For each violation:
   - Type (MISSING_SCENARIOS, TECHNICAL_LANGUAGE, etc.)
   - Severity (ERROR, WARNING, INFO)
   - Message (what's wrong)
   - Suggestion (how to fix)
   - Slide reference (PowerPoint source)
3. Provide summary: PASS or FAIL with count of violations

---

## Action 4: VALIDATE FEEDBACK

**Purpose**: User reviews validation results and decides next steps

### Step 1: User Review
**Performer**: User

**Review Validation Results**:
- Check violations and suggestions
- Determine if fixes are needed
- Decide whether to accept or revise

### Step 2: User Decision
**Performer**: User → AI Agent

**Options**:
1. **Accept**: Validation passed or violations acceptable
2. **Fix**: Apply suggested fixes automatically
3. **Manual Fix**: User will fix manually
4. **Revise**: Go back and regenerate scenarios

**Decision Point**: 
- If "Fix", apply corrections and re-validate
- If "Revise", go back to Action 1 Step 3
- If "Accept" or "Manual Fix", complete command

---

## Notes

### Scenario Guidelines
- Cover happy path, edge cases, and error cases
- Use Given/When/Then/But structure consistently
- Use Background for repeated Given steps across scenarios
- Use Scenario Outline for parameterized scenarios with multiple value combinations
- Each scenario describes a specific interaction flow
- Scenarios are narrative descriptions (not code)
- Link scenarios to acceptance criteria

### PowerPoint References
- Slide 16: Story specification and scenario creation
- Slides 149-154: Scenario patterns and examples
- Slide 154: Purchase Textbook example (happy path scenario)

### Examples Section
- Examples section filled in Phase 5 (separate command: `/story-specification-examples`)
- This command focuses ONLY on scenarios structure

### Related Commands
- **Prerequisite**: `/story-explore` (must have acceptance criteria)
- **Next**: `/story-specification-examples` (adds examples to scenarios)


