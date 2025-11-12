# Story Specification Scenarios Prompts

## Overview
These prompts guide the AI agent in asking clarifying questions before generating or validating scenario specifications. They ensure the agent has sufficient context to create comprehensive scenarios that cover happy paths, edge cases, and error cases.

---

## CRITICAL: Scope Detection and Processing

### ALWAYS Detect Scope from User Context

**Before asking any questions, detect scope**:

1. **Folder Attachment** (@Feature or @Epic):
   - User attached folder like `@⚙️ Establish Identity`
   - Find ALL story files (📝 *.md) in that folder
   - Exclude Feature Overview files (⚙️ *Feature Overview.md)
   - Process ALL story files found

2. **Multiple File Attachments**:
   - User attached multiple story files
   - Process ALL attached story files

3. **Single File Attachment**:
   - User attached single story file
   - Process that file only

4. **Story Names in Text**:
   - User mentioned story names (e.g., "User enters name" and "User selects power level")
   - Find story files matching those names
   - Process all matched stories

**Scope Confirmation (MANDATORY - ALWAYS DO THIS)**:
```
I found the following stories in [scope name]:
1. 📝 User enters identity text fields (already has scenarios - skip)
2. 📝 User enters identity numeric fields (needs scenarios)
3. 📝 User selects gender (needs scenarios)
4. 📝 User selects power level (needs scenarios)
5. 📝 User clears identity field (needs scenarios)

I'll generate scenarios for stories 2, 3, 4, 5 (skipping story 1 which already has scenarios).

Should I proceed with all 4 stories, or would you like to select specific ones?
```

**Wait for user confirmation before proceeding to generation.**

---

## Generate Action Prompts

### Category 1: Scope and Target (ALWAYS ASK FIRST)
**Purpose**: Identify which stories need scenarios

**CRITICAL**: Detect scope from user context:
- **Folder attached** (e.g., @⚙️ Feature Folder) → Generate for ALL stories in folder
- **Epic folder attached** (e.g., @🎯 Epic Folder) → Generate for ALL stories in all features
- **Multiple files attached** → Generate for all attached files
- **Single file attached** → Generate for that file only
- **Story names provided** → Find and generate for named stories

**Questions**:
1. **Scope Confirmation** (ALWAYS show this):
   - "I found [X] stories in [scope name]. Here they are:"
   - List all stories that will be processed
   - "Should I generate scenarios for all of them, or would you like to select specific ones?"
   - Wait for confirmation before proceeding

2. Which stories need scenario-based specifications?
   - Specific story documents (provide paths)?
   - All stories in a feature?
   - Stories in current increment?
   - Stories with specific status (e.g., "Explored")?
   - **DEFAULT**: If folder/feature provided, process ALL stories in scope

3. Where are the story documents located?
   - Full path to story-doc.md files?
   - Feature folder location?
   - Multiple features or single feature?

### Category 2: Scenario Types
**Purpose**: Understand what scenarios are needed

**Questions**:
3. What are the main user flows or system flows to document?
   - Primary happy path flows?
   - Alternative success paths?
   - Which acceptance criteria need scenarios?

4. Are there any edge cases or alternative paths to consider?
   - Boundary conditions (min/max values, empty/full states)?
   - Optional paths or variations?
   - Special cases or exceptions?
   - Platform-specific behaviors?

5. What error conditions should be covered?
   - Invalid inputs or data?
   - Failed operations or services?
   - Permission or authorization failures?
   - Timeout or network errors?

### Category 3: Scenario Structure
**Purpose**: Determine if advanced Gherkin features are needed

**Questions**:
6. Do scenarios have repeated Given steps that could use Background?
   - Common STATE setup across multiple scenarios?
   - Shared authentication or data STATE?
   - Repeated STATE context that all scenarios need?
   - **CRITICAL**: Given statements describe STATES, not actions (borrowed from BDD principles)
     - ✅ "Given character is being edited" (state)
     - ✅ "Given screen is displayed" (state)
     - ❌ "Given user is on screen" (implies navigation action)

7. Are there scenarios with multiple value combinations (need Scenario Outline)?
   - Testing same behavior with different data?
   - Validation rules with multiple examples?
   - Boundary testing with multiple values?
   - Parameterized scenarios (3+ similar cases)?

### Category 4: Domain Context
**Purpose**: Understand domain-specific terminology and rules

**Questions**:
8. Are there domain-specific terms or concepts that should be used?
   - Business terminology (not technical terms)?
   - Domain objects and their relationships?
   - Business rules or constraints?
   - Domain STATES that should be described in Given statements?

9. What level of detail is appropriate for these scenarios?
   - High-level user journey?
   - Detailed step-by-step interaction?
   - Focus on system behavior or user experience?
   - **REMINDER**: Given = STATE description, When = ACTION trigger, Then = OUTCOME

### Category 5: Coverage
**Purpose**: Ensure comprehensive scenario coverage

**Questions**:
10. Should scenarios cover all acceptance criteria or focus on specific ones?
    - Cover all AC in story document?
    - Cover feature-level domain AC?
    - Focus on critical or risky AC first?

11. Are there any acceptance criteria that are particularly complex or risky?
    - Critical business rules?
    - Complex validations?
    - Integration points with other systems?

---

## Validate Action Prompts

### Category 1: Validation Scope
**Purpose**: Determine what to validate

**Questions**:
1. Which story documents should be validated?
   - Specific story documents (provide paths)?
   - All stories in a feature?
   - Recently modified stories?

2. What validation level is needed?
   - Structure only (Gherkin syntax)?
   - Content (behavioral language, coverage)?
   - Comprehensive (structure + content + heuristics)?

### Category 2: Validation Criteria
**Purpose**: Understand validation expectations

**Questions**:
3. What severity level of violations should fail validation?
   - Only ERROR level fails?
   - WARNING level also fails?
   - INFO level included in report?

4. Are there specific heuristics or rules to emphasize?
   - Coverage of all acceptance criteria mandatory?
   - Behavioral language strictly enforced?
   - Edge cases required or optional?

### Category 3: Context for Validation
**Purpose**: Get context needed for validation

**Questions**:
5. Where are the acceptance criteria for these stories?
   - In story documents?
   - In feature documents?
   - Both locations?

6. Are there existing scenarios to validate or are we validating newly generated ones?
   - Validating after generation?
   - Validating existing scenarios?
   - Comparing against previous version?

---

## Decision-Making Flow Prompts

### When to Ask Questions
**Trigger**: Before generating or validating scenarios

**Decision Logic**:
1. If story paths not provided → Ask Category 1 (Scope) questions
2. If scenario types unclear → Ask Category 2 (Types) questions
3. If complexity unknown → Ask Category 3 (Structure) questions
4. If domain context missing → Ask Category 4 (Domain) questions
5. If coverage expectations unclear → Ask Category 5 (Coverage) questions

### When to Skip Questions
**Skip if**:
- User provided comprehensive context in request
- Previous command context available (e.g., from `/story-explore`)
- Defaults are acceptable (happy path + basic edge cases)

### Follow-up Questions
**When initial answers are unclear**:
- "Can you provide more details about [specific aspect]?"
- "Would you like me to [suggested approach] or [alternative approach]?"
- "Should I assume [default behavior] or do you need something different?"

---

## Example Prompt Sequences

### Example 1: Minimal Context
**User Request**: "Generate scenarios for the login story"

**AI Agent Prompts**:
1. "Where is the login story document located? (e.g., path to story-doc.md)"
2. "Should I cover just the happy path or also include edge cases (invalid credentials, locked accounts, etc.)?"
3. "Do you have any specific error conditions you want covered?"

### Example 2: Comprehensive Context
**User Request**: "Generate scenarios for all stories in the Order Management feature. Include happy paths, edge cases for boundary conditions, and error handling for payment failures. Use Background for the common authentication setup."

**AI Agent Prompts**:
- None needed - user provided comprehensive context
- Proceed directly to generation

### Example 3: Validation Context
**User Request**: "Validate the checkout scenarios"

**AI Agent Prompts**:
1. "Where is the checkout story document? (e.g., path to story-doc.md)"
2. "Should validation fail on WARNING level violations or only ERROR level?"
3. "Do you want me to check coverage against acceptance criteria in the feature document or just validate structure?"

---

## Prompt Response Handling

### If User Provides Partial Answer
**Action**: Ask follow-up questions for missing information

**Example**:
- User: "Generate scenarios for payment processing"
- AI: "Got it. Should I include edge cases like failed transactions, timeout errors, and declined payments?"

### If User Says "Use Defaults"
**Defaults**:
- Cover happy path scenarios
- Include basic edge cases (boundary conditions)
- Include basic error cases (invalid inputs, failed operations)
- Use Background if 3+ scenarios share Given steps
- Use Scenario Outline if 3+ similar cases with different data

### If User Says "All Stories in Feature"
**Action**: 
1. Ask for feature folder path
2. Discover all story-doc.md files in that feature
3. Generate scenarios for each story
4. Report progress as each story is completed

---

## Clarification Question Templates

### For Scope
- "Which [stories/features/documents] should I [generate/validate] scenarios for?"
- "Should I process [all stories/specific stories/stories matching criteria]?"

### For Coverage
- "Should scenarios cover [all acceptance criteria/specific criteria/critical criteria only]?"
- "Do you want [happy path only/happy path + edge cases/comprehensive coverage]?"

### For Structure
- "Should I use Background for [common STATE setup/repeated STATE context]?"
- "Do you need Scenario Outline for [parameterized testing/multiple value combinations]?"
- **REMINDER**: Given describes STATES (e.g., "character is being edited"), not actions

### For Detail Level
- "Should scenarios be [high-level user journeys/detailed step-by-step/focused on specific aspects]?"
- "What level of detail is appropriate: [brief/standard/comprehensive]?"

---

## PowerPoint References
- Slide 16: Story specification guidance
- Slides 149-154: Scenario patterns and examples
- Slide 154: Purchase Textbook example (demonstrates comprehensive scenario)


