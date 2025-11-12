### Command: /story-specification-scenarios generate

**[Purpose]:**
Generate scenario-based specifications by filling in the Scenarios section of story documents with detailed Given/When/Then scenarios.

**[Parent Command]:**
`/story-specification-scenarios` - Delegates to this command for generation action

**[Rule]:**
- `behaviors/stories/stories-rule.mdc` - Story writing practices and standards
- Applies principles: Universal (0.1, 0.2), Phase 4 Specification Scenarios (4.1)

---

## Generation Process

### Step 1: Prompting Questions (MANDATORY - Ask BEFORE generating)
**CRITICAL**: ALWAYS ask clarifying questions BEFORE starting generation

**Scope Detection**:
- If user provides **folder/feature/epic**: Generate for ALL stories in that scope
- If user provides **list of story files**: Generate for all listed stories
- If user provides **single story**: Generate for that story only
- If unclear: ASK for clarification

**Ask user for clarification**:
1. **Scope confirmation**: 
   - "I found X stories in [feature/folder]. Should I generate scenarios for all of them?"
   - List the stories that will be processed
   - Confirm user wants all or specific subset

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

**DO NOT PROCEED** until user answers or confirms defaults

### Step 2: Review Acceptance Criteria
**Read and analyze**:
- Story document acceptance criteria
- Feature document domain and behavioral AC
- Identify scenario types needed (happy path, edge cases, error cases)

### Step 3: Generate Scenario Structure
**Create**:
1. Background section (if repeated Given steps exist)
2. Happy path scenarios (main success flows)
3. Edge case scenarios (boundary conditions)
4. Error case scenarios (failure handling)
5. Scenario Outline (if parameterized scenarios needed)

### Step 4: Generate Scenario Content
**Use template**: `behaviors/stories/specification-scenarios/scenario-template.md`

**Fill in**:
- Background (optional)
- Scenario 1: [Happy Path]
  - Given [context]
  - And [additional context]
  - When [action]
  - Then [expected outcome]
  - And [additional outcome]
  - But [should NOT happen]
- Scenario 2: [Edge Case]
- Scenario 3: [Error Case]
- Scenario Outline: [Parameterized] (optional)
  - With <parameter> placeholders
  - Examples table with | columns |

### Step 5: Present Results
**Show**:
- Generated scenarios
- Number of scenarios (by type)
- Coverage of acceptance criteria
- Use of Background and Scenario Outline

---

## Output Format

Story document with Scenarios section filled:

```markdown
## Scenarios

### Background (Optional)
**Given** [common context for all scenarios]
**And** [additional common context]

### Scenario 1: [Happy Path Name]
**Given** [initial context/state]
**And** [additional context]
**When** [user/system action]
**Then** [expected outcome]
**And** [additional outcome]
**But** [should NOT happen]

### Scenario 2: [Edge Case Name]
**Given** [context]
**When** [boundary condition]
**Then** [expected handling]

### Scenario 3: [Error Case Name]
**Given** [context]
**When** [error condition]
**Then** [error handling outcome]
**And** [error message or recovery]

### Scenario Outline: [Parameterized Name] (Optional)
**Given** there are <start> items
**When** I perform action with <value>
**Then** result should be <expected>

**Examples**:
| start | value | expected |
|-------|-------|----------|
| 12    | 5     | 7        |
| 20    | 5     | 15       |
```

---

## Decision Points

### If acceptance criteria are missing
**Action**: Warn user and suggest running `/story-explore` first

### If scenarios don't cover all AC
**Action**: Add more scenarios to ensure full coverage

### If user feedback indicates revisions needed
**Action**: Regenerate scenarios with user input

---

## PowerPoint References
- Slide 16: Story specification guidance
- Slides 149-154: Scenario patterns and examples
- Slide 154: Purchase Textbook scenario (concrete example)


