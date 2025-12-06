# Prompt-Based Command Infrastructure Refactoring Plan

## Overview

Extend the prompt-file-based command pattern from stories to all behaviors, with MANDATORY interactive workflows. ALL generate/validate commands MUST follow explicit pause-point workflows: check context → ask questions → execute action → document assumptions → create clarifying questions → wait for user → recommend proceed. Base command enforces these workflows; prompt files inject specific instructions.

---

## Problem Statement

Currently, we have duplication across command runners where each behavior implements custom `generate()` and `validate()` methods with hardcoded instruction strings. More critically, commands lack consistent interactive workflows with explicit pause points for user feedback.

---

## Solution: Mandatory Interactive Workflows + Prompt Files

**Core Principle:** EVERY generate/validate command MUST follow an explicit interactive workflow that:

1. **Checks context first** - Examines prompting questions, stops if unanswered
2. **Asks user questions** - Never assumes, always clarifies missing context
3. **Executes action** - Generates or validates with full context
4. **Documents assumptions** - Lists every assumption made
5. **Creates clarifying questions** - Identifies where assumptions need validation
6. **Waits for user feedback** - NEVER automatically proceeds
7. **Recommends next step** - Only after user responds

This workflow is MANDATORY, not optional. Base command infrastructure enforces it; prompt files inject command-specific details.

---

## MANDATORY Workflows

### Generate Workflow (ALL commands must follow)

```
1. CHECK CONTEXT
   ├─ Review prompting questions list
   ├─ Check if questions answered in context
   └─ If NO → STOP and ASK USER → WAIT for response
   
2. GENERATE CONTENT
   ├─ Use full context provided
   ├─ Apply command-specific instructions from prompt file
   └─ Apply rule principles
   
3. DOCUMENT ASSUMPTIONS
   ├─ List EVERY assumption made
   ├─ Explain what you inferred
   └─ Identify judgment calls
   
4. CREATE CLARIFYING QUESTIONS
   ├─ Questions to validate assumptions
   ├─ Questions about alternatives
   └─ Questions about priorities
   
5. PRESENT TO USER
   ├─ Show generated content
   ├─ Show assumptions list
   ├─ Show clarifying questions
   └─ WAIT for user feedback (DO NOT recommend proceeding yet)
   
6. AFTER USER RESPONDS
   └─ Now you can recommend to proceed to validation
```

### Validate Workflow (ALL commands must follow)

```
1. CHECK CONTEXT
   ├─ Review prompting questions list
   ├─ Check if questions answered in context
   └─ If NO → STOP and ASK USER → WAIT for response
   
2. RUN CODE HEURISTICS
   ├─ Automated scans run first
   └─ Collect heuristic violations
   
3. AI VALIDATES AGAINST PRINCIPLES
   ├─ Review ALL principles (not just heuristics)
   ├─ Find violations heuristics missed
   └─ Apply command-specific validation from prompt file
   
4. DOCUMENT ASSUMPTIONS
   ├─ List assumptions made during validation
   ├─ Explain interpretation choices
   └─ Identify uncertain recommendations
   
5. CREATE CLARIFYING QUESTIONS
   ├─ Questions about how to fix violations
   ├─ Questions about priorities
   └─ Questions about alternatives
   
6. PRESENT TO USER
   ├─ Show validation results (violations)
   ├─ Show assumptions list
   ├─ Show clarifying questions
   └─ WAIT for user to answer (DO NOT recommend fixes yet)
   
7. AFTER USER RESPONDS
   ├─ Apply fixes based on user guidance
   └─ Now you can recommend to proceed
```

**Critical Rules:**
- ❌ NEVER skip asking questions if context is missing
- ❌ NEVER automatically proceed without user feedback
- ❌ NEVER hide assumptions - make them explicit
- ✅ ALWAYS wait for user after presenting results
- ✅ ALWAYS create clarifying questions
- ✅ ALWAYS document what you're uncertain about

---

## Division of Responsibility: Base Workflow vs Prompt Files

### Base Workflow (Common to ALL Commands)

**Lives in:** `common_command_runner.py` base prompt templates

**Provides:**
- Pause point structure (check context → ask → execute → document → clarify → wait)
- Generic instructions for each step ("list assumptions", "create clarifying questions")
- Workflow enforcement (MUST check context, MUST wait for user, etc.)
- Standard formatting for assumptions and questions

**Does NOT provide:**
- What specific content to generate
- Which principles apply
- Where assumptions are likely
- What questions to ask

### Prompt Files (Specific to Each Command)

**Lives in:** `behaviors/{feature}/{command}/{command}-prompts.md`

**Must Provide:**

#### 1. Prompting Questions Section
**What:** Explicit list of questions that MUST be answered before action can proceed

**Example - Story Shaping:**
```markdown
## Prompting Questions

CRITICAL - Check if these are answered in context. If not, STOP and ASK USER:

- What is the product vision and high-level goals?
- Who are the primary users and stakeholders?
- What are the key business outcomes or value delivered?
- What is in scope and out of scope for this initiative?
- Where should the story map be created? (infer from open files/context)
```

**Example - Story Discovery:**
```markdown
## Prompting Questions

CRITICAL - Check if these are answered in context. If not, STOP and ASK USER:

- Which market increment(s) are we focusing on for discovery?
- What new information or insights have been discovered since shaping?
- Are there any changes to business priorities or constraints?
- What is the target delivery timeline for this increment?
- Where is the existing story map file located?
```

#### 2. Specific Instructions Section
**What:** Detailed instructions on what to create, which principles to apply, and HOW to apply them

**Example - Story Shaping Generate:**
```markdown
## Generate Action Prompts

### Specific Instructions

Generate TWO story map files following hierarchical decomposition:

1. **{product-name}-story-map.md** - Tree structure with:
   - 🎯 Epic → 📂 Sub-Epic → ⚙️ Feature → 📝 Story hierarchy
   - Tree characters (│ ├─ └─) for visual structure
   - Legend at top explaining emoji meanings
   - 10-20% of stories identified, rest use ~X stories counts
   
2. **{product-name}-story-map-increments.md** - Value increments with:
   - NOW/NEXT/LATER priority organization
   - Marketable increments of value
   - Relative sizing notes

### Principles to Apply

Apply these principles from stories-rule.mdc Section 1:
- **§1.1 Story Map Hierarchy** - Use emoji 4-level hierarchy
- **§1.2 Business Language** - [Verb] [Noun] format, NO technical jargon
- **§1.3 User AND System Activities** - Both perspectives required
- **§1.4 Story Counting** - Use ~X stories for unexplored areas
- **§1.5 7±2 Sizing** - Epics: 4-9 features, Features: 4-9 stories

### Where AI Will Make Assumptions (Document These)

You will likely assume:
- Product name if not provided (document: "Assumed product name: X based on context")
- Epic/feature boundaries (document: "Grouped stories into features based on functional similarity")
- Story counts for unexplored areas (document: "Estimated ~X stories based on similar features")
- Priority of increments (document: "Assigned NOW/NEXT/LATER based on dependencies and typical order")
- Location to create files (document: "Creating in {path} based on open files in context")

### Clarifying Questions You Should Ask

After generating, ask user:
1. "Is the product name '{name}' correct?"
2. "I've estimated ~X stories for {feature}. Does this seem reasonable compared to similar features?"
3. "I've organized increments as NOW/NEXT/LATER based on dependencies. Should any be reprioritized?"
4. "I created files at {location}. Is this the correct location?"
```

**Example - Story Discovery Generate with Decompose/Consolidate Decisions:**
```markdown
## Generate Action Prompts

### Specific Instructions

Update existing story map with exhaustive decomposition for increment(s) in focus:

**For EACH story in focus increment, decide:**
- **Same logic, different data → CONSOLIDATE into one story**
- **Different logic/formula/rule/algorithm → SEPARATE into different stories**

**Decision Framework:**

1. **Same UI/Validation/Calculation Logic?**
   - YES → Consider CONSOLIDATE
   - NO → SEPARATE
   
2. **Different Business Rules?**
   - YES → SEPARATE  
   - NO → Consider CONSOLIDATE

3. **Different Data Structures?**
   - YES → SEPARATE
   - NO → Consider CONSOLIDATE

**DOCUMENT EVERY DECISION:**
```
Story Decision Log:
- Stories [X, Y, Z]: CONSOLIDATED
  Reasoning: Same selection UI logic, just different catalogs
  Uncertainty: Medium - could be separate if validation differs
  
- Stories [A] and [B]: SEPARATED
  Reasoning: A has prerequisite checking, B has cost calculation
  Uncertainty: Low - clearly different algorithms
```

### Principles to Apply

Apply these principles from stories-rule.mdc Section 2:
- **§2.5 Exhaustive Logic Decomposition** - Enumerate ALL permutations
- **§2.6 Story Format** - "User [verb] [noun]" format
- **§2.4 Story Grooming** - Flag ambiguous/complex stories

### Where AI Will Make Assumptions (Document These)

**HIGH ASSUMPTION AREA - Decompose vs Consolidate:**

You will make judgment calls about:
- Whether logic is "same" or "different"
- Whether to consolidate or separate similar stories
- What constitutes "different business logic"
- Complexity assessment from descriptions
- Whether validation rules differ enough to warrant separation

**For EACH consolidate/separate decision, document:**
- Decision: [Consolidated Stories X+Y / Separated Stories A and B]
- Reasoning: [Same UI/validation/calc logic / Different formula/rules]
- Uncertainty Level: [High/Medium/Low]
- Could be interpreted differently because: [explain]

### Clarifying Questions You Should Ask

**For each decompose/consolidate decision with Medium/High uncertainty:**

**Story Consolidation Decision:**
```
Stories: [list stories being considered]
Current Decision: CONSOLIDATED into one story
Reasoning: Both use same validation rules, just different data values
Uncertainty: Medium

Question for User:
"Should these remain as ONE story (same logic, different data) or 
 SEPARATE stories (if business logic actually differs)?
 
 Current assessment: Same logic
 - [Story X]: User selects advantage from catalog
 - [Story Y]: User selects power from catalog
 - [Story Z]: User selects equipment from catalog
 
 All use same selection UI and validation. Consolidated as:
 'User selects item from character catalog'
 
 Is this correct, or do advantages/powers/equipment have different
 enough logic (different prerequisites, costs, validation rules) to
 warrant separate stories?"
```

**Story Separation Decision:**
```
Stories: [list]
Current Decision: SEPARATED into different stories
Reasoning: Different calculation formulas/algorithms
Uncertainty: Medium

Question for User:
"Are these formulas different enough to warrant separate stories,
 or should they be consolidated?
 
 - [Story A]: Calculate defense using armor formula
 - [Story B]: Calculate defense using power formula
 
 I separated these because formulas differ. However, if the UI and
 result handling are identical, should they be consolidated?"
```
```

**Example - Story Discovery Validate:**
```markdown
## Validate Action Prompts

### Specific Validation Checks

After code heuristics run, YOU MUST validate:

1. **Exhaustive Decomposition Check (Principle §2.5)**
   - For increment(s) in focus: Are ALL stories listed (NO ~X stories)?
   - Are logic permutations enumerated?
   - Are similar data items consolidated when logic is identical?
   - Are different business logic items separated?
   
2. **Consolidation Correctness Check**
   - For EACH consolidated story, verify:
     * Do consolidated stories have SAME logic? ✅
     * If logic differs → VIOLATION: Should be separate
     * Document: "Checked [story]: consolidation [correct/incorrect]"
   
3. **Separation Correctness Check**
   - For EACH separated story group, verify:
     * Do separated stories have DIFFERENT logic? ✅
     * If logic is same → VIOLATION: Should consolidate
     * Document: "Checked [stories]: separation [correct/incorrect]"

4. **Story Format Check (Principle §2.6)**
   - Format: "User [verb] [noun]" or "System [verb] [noun] when [trigger]"
   - Single "and system [response]" clause allowed
   - NO examples or extra notes in story titles

5. **No AI Additions Check**
   - NO "Status: DISCOVERY" lines (ERROR if found)
   - NO day estimates (ERROR if found - humans add estimates)
   - NO separate increment files (ERROR if found)

### Where You'll Make Validation Assumptions (Document These)

You will assume:
- Complexity based on description length/wording
- Whether logic differs or just data differs
- What constitutes "different business logic"
- Whether grooming notes are sufficient
- Whether consolidation/separation decisions are correct

**DOCUMENT each assumption:**
```
Validation Assumption Log:
- Assumption: Stories X+Y correctly consolidated
  Based on: Both descriptions mention "selection from list"
  Uncertainty: Medium - can't verify actual validation logic without code
  
- Assumption: Stories A and B correctly separated  
  Based on: Different verb phrases ("calculate" vs "validate")
  Uncertainty: Low - descriptions clearly indicate different processes
```

### Clarifying Questions for Fixes

**For each consolidation/separation violation found:**

```
Violation: Stories X and Y are consolidated but seem to have different logic
Description X: "User selects advantage and system validates prerequisites"
Description Y: "User selects power and system calculates cost"

Analysis: These mention different system behaviors (validate vs calculate)
Suggests: Different business logic → Should be SEPARATED

Question for User:
"Looking at these consolidated stories, do they:
 a) Have same logic (keep consolidated) - just poor wording in descriptions
 b) Have different logic (split into separate) - validate ≠ calculate
 c) Need more detail in descriptions to determine

Current Assessment: Different logic - should be split (option b)
User Decision Needed: Which option is correct?"
```

```
Violation: Stories A and B are separated but appear to have same logic
Description A: "User selects melee weapon from equipment list"
Description B: "User selects ranged weapon from equipment list"

Analysis: Both use same selection UI, same list type
Suggests: Same logic, just different data → Should be CONSOLIDATED

Question for User:
"These are currently separate stories. Should they:
 a) Stay separate - melee and ranged have different rules/validation
 b) Be consolidated - same selection logic, just different weapon types
 c) Need more context about weapon rules to determine
 
Current Assessment: Same logic - should consolidate (option b)
User Decision Needed: Which option is correct?"
```
```

#### 3. Common Issues / Anti-Patterns Section
**What:** Specific mistakes AI tends to make for THIS command

**Example - Story Shaping:**
```markdown
### Common Issues to Avoid

- Using technical language (getDescriptor, PowerItem) instead of domain language
- Creating epic/feature folders during Shape (done in Arrange phase)
- Over-identifying stories (>20% detailed)
- Missing story counts for unexplored areas
- Using "Epic:", "Feature:" prefixes (just use emoji + name)
- Sub-Epics not using [Verb] [Noun] format
```

**Example - Story Discovery:**
```markdown
### Common Issues to Avoid

- Using ~X stories notation in increment(s) marked as focus (must be exhaustive)
- Creating separate increment files (single file only)
- Adding "Status: DISCOVERY" lines (forbidden)
- Adding day estimates (AI cannot estimate)
- **Over-consolidating**: Merging stories with different business logic
- **Over-separating**: Splitting stories with same logic but different data
- Not documenting consolidate/separate reasoning
- Not asking user about uncertain decisions
```

---

## Base Workflow with Command-Specific Injection Points

### Generate Action - Full Workflow with Injections

```
=== INTERACTIVE AI GENERATE ACTION ===

STEP 1: CHECK CONTEXT
━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific prompting questions from prompt file

Base Prompt:
"Review the following prompting questions and check if ALL are answered in context:"

[INJECTED CONTENT FROM PROMPT FILE - Prompting Questions Section]

Base Prompt:
"- If ALL questions answered → Proceed to Step 2
 - If ANY questions unanswered → STOP and go to Step 2"


STEP 2: ASK USER (IF CONTEXT MISSING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"If ANY critical context is missing:
 1. List which questions are unanswered
 2. ASK USER to provide this information
 3. WAIT for user response before proceeding
 
 DO NOT PROCEED without critical context."


STEP 3: GENERATE CONTENT
━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific generation instructions from prompt file

Base Prompt:
"Now generate content following these instructions:"

[INJECTED CONTENT FROM PROMPT FILE - Specific Instructions Section]

Base Prompt:
"Apply principles from the rule file as specified in the instructions above."


STEP 4: DOCUMENT ASSUMPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific assumption guidance from prompt file

Base Prompt:
"After generation, explicitly list ALL assumptions you made:"

[INJECTED CONTENT FROM PROMPT FILE - Where AI Will Make Assumptions Section]

Base Prompt:
"Format your assumptions as:

**Assumptions Made:**
- Assumption 1: [description] - Impact: [what this affects] - Uncertainty: [High/Medium/Low]
- Assumption 2: [description] - Impact: [what this affects] - Uncertainty: [High/Medium/Low]
- ...

For high-uncertainty assumptions, explain why you're uncertain."


STEP 5: CREATE CLARIFYING QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific question templates from prompt file

Base Prompt:
"Create questions to help user validate your assumptions.
Use these question templates and guidelines:"

[INJECTED CONTENT FROM PROMPT FILE - Clarifying Questions Section]

Base Prompt:
"Format your questions as:

**Questions for User:**

1. [Question about assumption 1]?
   - Option A: [approach]
   - Option B: [approach]
   - Current choice: [your assumption]
   - Why uncertain: [explanation]

2. [Question about assumption 2]?
   ..."


STEP 6: PRESENT TO USER & WAIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"Present to user:
 
 === GENERATED CONTENT ===
 [Show generated files/content]
 
 === ASSUMPTIONS MADE ===
 [Show assumptions list from Step 4]
 
 === QUESTIONS FOR YOU ===
 [Show clarifying questions from Step 5]
 
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
 🛑 WAITING FOR YOUR FEEDBACK
 
 Please review the above and provide:
 - Answers to the questions
 - Corrections to any assumptions
 - Any changes needed to generated content
 
 DO NOT RECOMMEND proceeding to validation yet."


STEP 7: AFTER USER RESPONDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"[After user provides feedback]

Thank you for the feedback. Based on your responses:
- [Summarize what was confirmed]
- [Summarize what was corrected]

Now you can proceed to validation when ready."
```

### Validate Action - Full Workflow with Injections

```
=== INTERACTIVE AI VALIDATE ACTION ===

STEP 1: CHECK CONTEXT
━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific prompting questions (if different from generate)

[Same as Generate Step 1]


STEP 2: RUN CODE HEURISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"Automated heuristics have scanned the content.
Review the heuristic violations report below:

[HEURISTIC VIOLATIONS REPORT]"


STEP 3: AI VALIDATES AGAINST PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Command-specific validation checks from prompt file

Base Prompt:
"CRITICAL: Code heuristics are LIMITED. They only catch syntax/pattern issues.

YOU MUST actively validate content against ALL principles:
1. Read and understand ALL principles in the rules
2. Check if content follows EACH principle
3. Identify violations heuristics missed
4. Validate meaning, flow, context - not just syntax
5. Report ALL violations you find

The heuristics provide initial findings. YOU must validate comprehensively.

Now perform these specific validation checks:"

[INJECTED CONTENT FROM PROMPT FILE - Specific Validation Checks Section]


STEP 4: LIST VIOLATIONS
━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles formatting

Base Prompt:
"Report ALL violations found (from heuristics AND your principle validation):

**Violations Found:**

ERROR: [Principle X.Y violated]
- Line #: [line number]
- Issue: [what's wrong]
- Impact: [why this matters]
- Suggested Fix: [how to fix]
- Confidence: [High/Medium/Low]

WARNING: [Principle Z violated]
- Line #: [line number]
- Issue: [what's wrong]
- Suggested Fix: [how to fix]
- Confidence: [High/Medium/Low]"


STEP 5: DOCUMENT ASSUMPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Validation-specific assumption guidance from prompt file

Base Prompt:
"List assumptions you made during validation:"

[INJECTED CONTENT FROM PROMPT FILE - Where You'll Make Validation Assumptions Section]

Base Prompt:
"Format:

**Validation Assumptions:**
- Assumption 1: [what you assumed] - Uncertainty: [High/Medium/Low]
- Assumption 2: [what you assumed] - Uncertainty: [High/Medium/Low]"


STEP 6: CREATE CLARIFYING QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 INJECT: Fix-related question templates from prompt file

Base Prompt:
"Create questions to clarify best fix approach:"

[INJECTED CONTENT FROM PROMPT FILE - Clarifying Questions for Fixes Section]

Base Prompt:
"Format:

**Questions About Fixes:**

For Violation [#1]:
- Violation: [description]
- Current Fix Suggestion: [your suggestion]
- Question: [ask user for guidance]
- Options:
  a) [option 1]
  b) [option 2]
  c) [option 3]
- Recommended: [which option and why]
- Uncertainty: [why you need user input]"


STEP 7: PRESENT TO USER & WAIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"Present to user:

=== VALIDATION RESULTS ===
Status: [PASS / FAIL - X errors, Y warnings]

[Show violations from Step 4]

=== VALIDATION ASSUMPTIONS ===
[Show assumptions from Step 5]

=== QUESTIONS ABOUT FIXES ===
[Show questions from Step 6]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛑 WAITING FOR YOUR GUIDANCE

Please review and provide:
- Answers to questions about fixes
- Corrections to any validation assumptions
- Priorities for which violations to fix first
- Any additional context that affects validation

DO NOT RECOMMEND fixes or proceeding yet."


STEP 8: AFTER USER RESPONDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No injection - base handles this

Base Prompt:
"[After user provides feedback]

Thank you for the guidance. Based on your responses:
- [Summarize fix approach confirmed]
- [Summarize priorities]

Now I can apply fixes or you can apply them and re-run validation."
```

---

## Concrete Example: Story Discovery Decompose/Consolidate

### Scenario: AI encounters these stories in a story map

```
📝 User selects advantage from advantage list
📝 User selects power from power list
📝 User selects equipment from equipment list
📝 User calculates defense from armor values
📝 User calculates defense from power bonuses
```

### Step 3: Generate with Injected Instructions

**Base Prompt:** "Now generate content following these instructions:"

**INJECTED from story-discovery-prompts.md:**
```
For EACH story, decide:
- Same logic, different data → CONSOLIDATE
- Different logic/formula → SEPARATE

Decision Framework:
1. Same UI/Validation/Calculation? → Consider CONSOLIDATE
2. Different Business Rules? → SEPARATE
3. Different Data Structures? → SEPARATE
```

**AI Applies Logic:**
- Stories 1-3: Same selection UI logic → Consider CONSOLIDATE
- Stories 4-5: Different formulas → Keep SEPARATE

### Step 4: Document Assumptions with Injected Guidance

**Base Prompt:** "List ALL assumptions made:"

**INJECTED from story-discovery-prompts.md:**
```
For EACH consolidate/separate decision, document:
- Decision: [what you decided]
- Reasoning: [why]
- Uncertainty: [High/Medium/Low]
```

**AI Documents:**
```
**Assumptions Made:**

1. CONSOLIDATED Stories 1-3
   - Decision: Merged into "User selects character option from catalog"
   - Reasoning: All three use same selection UI (pick from list)
   - Impact: Reduces from 3 stories to 1
   - Uncertainty: MEDIUM - can't verify if validation rules differ without code
   - Could be wrong if: Advantages have prerequisite checks that powers don't

2. SEPARATED Stories 4-5  
   - Decision: Kept as separate stories
   - Reasoning: Different calculation formulas (armor vs power bonuses)
   - Impact: Maintains 2 separate stories
   - Uncertainty: LOW - descriptions clearly indicate different algorithms
   - Could be wrong if: Both formulas feed same defense calculation engine
```

### Step 5: Create Clarifying Questions with Injected Templates

**Base Prompt:** "Create questions to validate assumptions:"

**INJECTED from story-discovery-prompts.md:**
```
For each Medium/High uncertainty decision:

Story Consolidation Decision:
- Stories: [list]
- Current Decision: CONSOLIDATED
- Reasoning: [why]
- Question: "Should these remain ONE or SEPARATE?"
```

**AI Creates Questions:**
```
**Questions for User:**

1. **Consolidation Decision - Character Options**
   
   Stories consolidated:
   - "User selects advantage from advantage list"
   - "User selects power from power list"  
   - "User selects equipment from equipment list"
   
   Consolidated as: "User selects character option from catalog"
   
   Reasoning: All use same selection UI pattern
   Uncertainty: MEDIUM
   
   **Question:** Do advantages, powers, and equipment have:
   - Option A: Same selection logic → Keep as ONE consolidated story ✓
   - Option B: Different validation/prerequisites → Split into SEPARATE stories
   - Option C: Need to review rules to determine
   
   **Current choice:** Option A (consolidated)
   **Why uncertain:** Can't see actual validation rules in descriptions
   
   **Your decision:** A, B, or C?

2. **Separation Decision - Defense Calculations**
   
   Stories kept separate:
   - "User calculates defense from armor values"
   - "User calculates defense from power bonuses"
   
   Reasoning: Different formulas mentioned
   Uncertainty: LOW
   
   **Question:** Should these calculations:
   - Option A: Stay SEPARATE → Different algorithms justify separate stories ✓
   - Option B: Be CONSOLIDATED → If they use same calculation engine
   
   **Current choice:** Option A (separate)
   **Why asking:** Just confirming - seems clearly different
   
   **Your decision:** A or B?
```

### Step 6: Present & Wait

```
=== GENERATED CONTENT ===
Updated story map with:
- 1 consolidated story: "User selects character option from catalog"
- 2 separate stories: Defense calculations

=== ASSUMPTIONS MADE ===
[Shows assumptions from Step 4 above]

=== QUESTIONS FOR YOU ===
[Shows questions from Step 5 above]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛑 WAITING FOR YOUR FEEDBACK
```

### User Responds

```
User: "Actually, advantages have prerequisite checks and powers have cost calculations,
      so they should be separate stories. Equipment can stay consolidated if it's
      just simple selection. So split into:
      1. User selects advantage (with prerequisites)
      2. User selects power (with cost calc)
      3. User selects equipment
      
      Defense calculations - yes keep separate, correct."
```

### Step 7: After User Responds

```
Thank you for the feedback. Based on your responses:

✓ Confirmed: Defense calculations correctly separated (different formulas)
✗ Corrected: Split advantages/powers/equipment based on different business logic:
  - Advantages: Have prerequisite validation
  - Powers: Have cost calculation
  - Equipment: Simple selection

Updated decomposition:
- 3 stories for character options (not 1 consolidated)
- 2 stories for defense calculations (confirmed)

Total: 5 stories (was showing 3)

You can now proceed to validation when ready.
```

---

## Phase 1: Enhance Base Command Infrastructure

### 1.1 Add Interactive AI Pattern to Base Command

**File:** `behaviors/common_command_runner/common_command_runner.py`

**Changes:**

**A. Add prompt file loading:**
- Add `prompt_file_path` parameter to `Command.__init__()`
- Add `_load_prompts_from_file()` method that reads markdown sections
- Add `prompting_questions` attribute for pre-action questions

**B. Add base interactive AI prompt structure:**
- Create `_build_base_generate_prompt()` that injects command-specific content at steps 1, 3, 4, 5
- Create `_build_base_validate_prompt()` that injects command-specific content at steps 1, 3, 5, 6
- Create `_build_base_plan_prompt()` with similar injection pattern

**New signature:**
```python
class Command:
    def __init__(self, content=None, base_rule=None, 
                 validate_instructions=None, generate_instructions=None,
                 prompt_file_path=None, prompting_questions=None, params=None):
        # Load from prompt file if provided, inject into base structure
        # prompting_questions = list of questions to check before action
```

### 1.2 Create Prompt File Template

**File:** `behaviors/common_command_runner/command_prompt_template.md`

**Structure:**
```markdown
# {Command Name} Prompts

## Prompting Questions

**CRITICAL:** Check if these are answered in context before proceeding. If not, ASK USER.

- Question 1 about critical context?
- Question 2 about critical context?
- Question 3 about critical context?

---

## Generate Action Prompts

### Specific Instructions

{Command-specific generation instructions - these get injected into base prompt}

### Principles to Apply

{Which principles from rule file to apply and HOW}

### Where AI Will Make Assumptions (Document These)

{Guidance on likely assumptions and how to document them}

### Clarifying Questions You Should Ask

{Templates for questions to ask user about assumptions}

### Expected Output

{Description of what should be generated}

### Common Issues

{Anti-patterns to avoid}

---

## Validate Action Prompts

### Specific Validation Checks

{Command-specific validation instructions - these get injected into base prompt}

### Where You'll Make Validation Assumptions (Document These)

{Guidance on validation assumptions to document}

### Clarifying Questions for Fixes

{Templates for questions about how to fix violations}

### Violation Severity

- ERROR: {What constitutes an error}
- WARNING: {What constitutes a warning}

---

## Plan Action Prompts (Optional)

### Planning Instructions

{Command-specific planning instructions - these get injected into base prompt}

### Plan Structure

{Expected plan format}
```

### 1.3 Create Base Prompt Templates

**File:** `behaviors/common_command_runner/base_generate_prompt.txt`

See "Base Workflow with Command-Specific Injection Points" section above for full content.

**File:** `behaviors/common_command_runner/base_validate_prompt.txt`

See "Base Workflow with Command-Specific Injection Points" section above for full content.

**File:** `behaviors/common_command_runner/base_plan_prompt.txt`

Similar structure with injection points.

---

## Phase 2: Identify Commands for Refactoring

### 2.1 Audit Current Runners

**Commands with hardcoded instructions to refactor:**

1. **DDD Runner** (`behaviors/ddd/ddd_runner.py`)
   - `DDDStructureCommand.generate()` - Lines 36-57
   - `DDDStructureCommand.validate()` - Lines 59-75
   - `DDDInteractionCommand.generate()` - Lines 81-99
   - `DDDInteractionCommand.validate()` - Lines 101-112

2. **Clean Code Runner** (`behaviors/clean-code/clean-code_runner.py`)
   - Currently empty - needs implementation with prompts

3. **BDD Runner** (`behaviors/bdd/bdd-runner.py`)
   - Has complex workflow logic - keep custom code for algorithms
   - Only extract pure prompt content to files

4. **Code Agent Runner** (`behaviors/code-agent/code_agent_runner.py`)
   - Already uses templates - good pattern
   - Verify consistency with new base approach

### 2.2 Keep Custom Code Where Needed

**Keep custom implementations for:**
- Algorithm-heavy logic (BDD workflow state machine, test execution)
- File system operations (creating folders, moving files - like `StoryArrangeCommand.generate()`)
- Complex heuristics and validation logic
- Actual code execution (running tests, parsing results)

**Rule:** If the method does MORE than just returning prompt strings, keep custom code

---

## Phase 3: Create Prompt Files for Each Command

### 3.1 DDD Commands

**Create:** `behaviors/ddd/structure/ddd-structure-prompts.md`
- Extract from `DDDStructureCommand.generate()` and `.validate()` methods
- Add prompting questions, assumption guidance, clarifying question templates

**Create:** `behaviors/ddd/interaction/ddd-interaction-prompts.md`
- Extract from `DDDInteractionCommand.generate()` and `.validate()` methods
- Add prompting questions, assumption guidance, clarifying question templates

### 3.2 Clean Code Commands

**Create:** `behaviors/clean-code/validate/clean-code-validate-prompts.md`
- Based on `behaviors/clean-code/clean-code-rule.mdc` principles
- Add prompting questions, validation checks, assumption guidance

**Create:** `behaviors/clean-code/refactor/clean-code-refactor-prompts.md`
- Based on refactoring patterns from clean code principles
- Add prompting questions, refactoring guidance, assumption documentation

### 3.3 Update Stories Prompts

**Update:** `behaviors/stories/shape/story-shape-prompts.md`
- Ensure follows new standard format with all required sections
- Add "Where AI Will Make Assumptions" section
- Enhance clarifying questions with templates

**Update:** `behaviors/stories/discovery/story-discovery-prompts.md`
- Add comprehensive decompose/consolidate decision guidance
- Add assumption documentation templates
- Add clarifying question templates for consolidate/separate decisions

---

## Phase 4: Refactor Runners to Use Prompt Files

### 4.1 Refactor DDD Runner

**File:** `behaviors/ddd/ddd_runner.py`

**Changes:**
```python
class DDDStructureCommand(DDDCommand):
    def __init__(self, content: Content, base_rule_file_name: str = 'ddd-rule.mdc'):
        base_rule = BaseRule(base_rule_file_name)
        prompt_file = Path(__file__).parent / "structure" / "ddd-structure-prompts.md"
        prompting_questions = [
            "What is the source file to analyze?",
            "What domain concepts should be highlighted?",
            "Are there known relationships to capture?"
        ]
        super().__init__(
            content, base_rule, 
            prompt_file_path=str(prompt_file),
            prompting_questions=prompting_questions
        )
    
    # Remove generate() and validate() methods - use base implementation
```

**Delete lines:** 36-75 (hardcoded generate/validate)

### 4.2 Implement Clean Code Runner

**File:** `behaviors/clean-code/clean-code_runner.py`

**Implement:**
```python
class CleanCodeValidateCommand(Command):
    def __init__(self, content: Content):
        base_rule = BaseRule('clean-code-rule.mdc')
        prompt_file = Path(__file__).parent / "validate" / "clean-code-validate-prompts.md"
        prompting_questions = [
            "What file should be validated?",
            "Are there specific principles to focus on?",
            "What is the target refactoring level (file/function/class)?"
        ]
        super().__init__(
            content, base_rule,
            prompt_file_path=str(prompt_file),
            prompting_questions=prompting_questions
        )

class CleanCodeRefactorCommand(Command):
    def __init__(self, content: Content):
        base_rule = BaseRule('clean-code-rule.mdc')
        prompt_file = Path(__file__).parent / "refactor" / "clean-code-refactor-prompts.md"
        prompting_questions = [
            "What violations should be fixed?",
            "Should fixes be automatic or suggested?",
            "Are there constraints on refactoring scope?"
        ]
        super().__init__(
            content, base_rule,
            prompt_file_path=str(prompt_file),
            prompting_questions=prompting_questions
        )
```

### 4.3 Update Stories Runner

**File:** `behaviors/stories/stories_runner.py`

**Refactor to use new pattern:**
```python
class StoryShapeCommand(Command):
    def __init__(self, content: Content, base_rule: BaseRule):
        prompt_file = Path(__file__).parent / "shape" / "story-shape-prompts.md"
        prompting_questions = [
            "What is the product vision and high-level goals?",
            "Who are the primary users and stakeholders?",
            "What are the key business outcomes or value delivered?",
            "What is in scope and out of scope for this initiative?"
        ]
        super().__init__(
            content, base_rule,
            prompt_file_path=str(prompt_file),
            prompting_questions=prompting_questions
        )

class StoryDiscoveryCommand(Command):
    def __init__(self, content: Content, base_rule: BaseRule):
        prompt_file = Path(__file__).parent / "discovery" / "story-discovery-prompts.md"
        prompting_questions = [
            "Which market increment(s) are we focusing on for discovery?",
            "What new information or insights have been discovered?",
            "Are there any changes to business priorities or constraints?",
            "What is the target delivery timeline for this increment?"
        ]
        super().__init__(
            content, base_rule,
            prompt_file_path=str(prompt_file),
            prompting_questions=prompting_questions
        )
```

---

## Phase 5: Add Meta-Validation (Code Agent Validates Workflow Compliance)

### 5.1 Update Code Agent Rule

**File:** `.cursor/rules/code-agent-rule.mdc`

**Add new principle:**

```markdown
## X. Mandatory Interactive Workflow Pattern

ALL commands MUST implement the interactive workflow with explicit pause points.

### Required Workflow Elements

**For Generate Actions:**
1. Check prompting questions against context
2. Stop and ask user if context missing
3. Generate with full context
4. Document all assumptions made
5. Create clarifying questions about assumptions
6. Present results + assumptions + questions to user
7. Wait for user feedback before recommending proceed

**For Validate Actions:**
1. Check prompting questions against context
2. Stop and ask user if context missing
3. Run code heuristics first
4. AI validates against principles comprehensively
5. Document validation assumptions
6. Create clarifying questions about fixes
7. Present violations + assumptions + questions to user
8. Wait for user to answer before recommending fixes

### Implementation Pattern

**✅ DO:** Use prompt files with base command injection
```python
class MyCommand(Command):
    def __init__(self, content, base_rule):
        prompt_file = Path(__file__).parent / "my-command-prompts.md"
        prompting_questions = [
            "Critical question 1?",
            "Critical question 2?"
        ]
        super().__init__(content, base_rule, 
                        prompt_file_path=str(prompt_file),
                        prompting_questions=prompting_questions)
```

**✅ DO:** Include all required sections in prompt file
```markdown
## Prompting Questions
## Generate Action Prompts
  ### Specific Instructions
  ### Where AI Will Make Assumptions
  ### Clarifying Questions You Should Ask
## Validate Action Prompts
  ### Specific Validation Checks
  ### Where You'll Make Validation Assumptions
  ### Clarifying Questions for Fixes
```

**❌ DON'T:** Skip workflow steps
**❌ DON'T:** Hardcode instructions in Python
**❌ DON'T:** Proceed without user feedback
**❌ DON'T:** Hide assumptions from user
```

### 5.2 Add Workflow Compliance Heuristic

**File:** `behaviors/code-agent/code_agent_runner.py`

**Add new heuristic class:**
```python
class WorkflowComplianceHeuristic(CodeHeuristic):
    """Validates that commands follow the mandatory interactive workflow pattern"""
    
    def __init__(self):
        super().__init__("workflow_compliance")
    
    def detect_violations(self, content):
        """Check if command follows interactive workflow"""
        violations = []
        
        # Check for prompt file existence
        if not self._has_prompt_file(content):
            violations.append(Violation(
                1, 
                "Missing prompt file - commands must use prompt files, not hardcoded strings",
                severity="ERROR"
            ))
        
        # Check for prompting questions
        if not self._has_prompting_questions(content):
            violations.append(Violation(
                1,
                "Missing prompting questions list - commands must define questions to check context",
                severity="ERROR"
            ))
        
        # Check prompt file structure
        prompt_file_path = self._get_prompt_file_path(content)
        if prompt_file_path and prompt_file_path.exists():
            violations.extend(self._validate_prompt_file_structure(prompt_file_path))
        
        return violations if violations else None
    
    def _validate_prompt_file_structure(self, prompt_file_path):
        """Validate prompt file has all required sections"""
        violations = []
        content = prompt_file_path.read_text()
        
        required_sections = [
            ("## Prompting Questions", "Missing 'Prompting Questions' section"),
            ("## Generate Action Prompts", "Missing 'Generate Action Prompts' section"),
            ("### Specific Instructions", "Missing 'Specific Instructions' subsection"),
            ("### Where AI Will Make Assumptions", "Missing 'Where AI Will Make Assumptions' subsection"),
            ("### Clarifying Questions", "Missing 'Clarifying Questions' subsection"),
            ("## Validate Action Prompts", "Missing 'Validate Action Prompts' section"),
            ("### Specific Validation Checks", "Missing 'Specific Validation Checks' subsection"),
        ]
        
        for section_header, error_msg in required_sections:
            if section_header not in content:
                violations.append(Violation(1, error_msg, severity="ERROR"))
        
        # Check for workflow keywords
        workflow_keywords = [
            "assumptions", "clarifying questions", "wait for user", 
            "do not proceed", "stop and ask", "uncertainty"
        ]
        
        missing_keywords = [
            kw for kw in workflow_keywords 
            if kw.lower() not in content.lower()
        ]
        
        if missing_keywords:
            violations.append(Violation(
                1,
                f"Prompt file missing workflow keywords: {', '.join(missing_keywords)}",
                severity="WARNING"
            ))
        
        return violations
```

### 5.3 Add Workflow Fix Suggestion

**File:** `behaviors/code-agent/code_agent_runner.py`

**Extend CommandCommand to validate workflow compliance:**
```python
class CommandCommand(CodeAgentCommand):
    """Command validation now includes workflow compliance checking"""
    
    def validate(self):
        """Override validate to check workflow compliance"""
        # Run base validation
        result = super().validate()
        
        # Check workflow compliance
        compliance_violations = self._check_workflow_compliance()
        
        if compliance_violations:
            result += "\n\n=== WORKFLOW COMPLIANCE ISSUES ===\n"
            result += self._format_compliance_violations(compliance_violations)
            result += "\n\n=== SUGGESTED FIXES ===\n"
            result += self._suggest_workflow_fixes(compliance_violations)
        
        return result
    
    def _suggest_workflow_fixes(self, violations):
        """Generate specific fixes for workflow violations"""
        fixes = []
        
        for violation in violations:
            if "Missing prompt file" in violation.message:
                fixes.append(
                    f"CREATE: {self.command_name}-prompts.md with required sections\n"
                    f"UPDATE: Command __init__ to use prompt_file_path parameter"
                )
            
            elif "Missing prompting questions" in violation.message:
                fixes.append(
                    f"ADD: prompting_questions list to Command __init__\n"
                    f"EXAMPLE:\n"
                    f"  prompting_questions = [\n"
                    f"    'What is the target entity?',\n"
                    f"    'What are the requirements?'\n"
                    f"  ]"
                )
            
            elif "Missing" in violation.message and "section" in violation.message:
                section = violation.message.split("'")[1]
                fixes.append(
                    f"ADD: '{section}' section to prompt file\n"
                    f"TEMPLATE: See behaviors/common_command_runner/command_prompt_template.md"
                )
        
        return "\n\n".join(fixes)
```

---

## Phase 6: Testing and Validation

### 6.1 Test Each Refactored Command

For each refactored command:
1. Run generate action - verify prompts load and inject correctly
2. Verify pause points work (stops when context missing)
3. Verify assumptions are documented
4. Verify clarifying questions are generated
5. Run validate action - verify same workflow
6. Verify backward compatibility with existing commands

### 6.2 Validate Prompt File Format

Create validator script to check:
- All prompt files follow standard structure
- Required sections present (Prompting Questions, Generate, Validate)
- Workflow keywords present (assumptions, clarifying questions, etc.)
- Markdown formatting is valid

---

## Success Criteria

- ✅ Base `Command` class loads prompts from markdown and injects into workflow
- ✅ All commands follow mandatory interactive workflow (7 steps for generate, 8 for validate)
- ✅ DDD runner uses prompt files (0 lines of hardcoded instructions)
- ✅ Clean Code runner uses prompt files
- ✅ Stories runner updated for consistency with new pattern
- ✅ All prompt files have required sections with assumption/question guidance
- ✅ Code-agent validates workflow compliance and suggests fixes
- ✅ Story Discovery properly handles decompose/consolidate with explicit assumptions
- ✅ Documentation updated with new pattern and examples
- ✅ No regression in existing command functionality

---

## Benefits

- **Reduced Code:** Eliminate 50-100+ lines per command (generate/validate methods)
- **Mandatory Workflows:** ALL commands follow same interactive pattern with pause points
- **Explicit Assumptions:** Every command documents what it assumes
- **User Control:** User answers questions before AND after each action
- **Better Decisions:** AI asks for clarification on uncertain decisions (especially decompose/consolidate)
- **Easier Maintenance:** Prompts in markdown, not buried in Python strings
- **Consistency:** All commands use same pattern
- **AI-Friendly:** Prompts in plain text, easier for AI to understand/modify
- **Extensibility:** Adding new commands requires only prompt file + minimal Python
- **Quality Control:** Code-agent validates that commands follow the pattern

---

## Implementation Order

1. **Phase 1** - Enhance base command infrastructure (1-2 days)
2. **Phase 3** - Create/update prompt files for Stories (validate pattern) (1 day)
3. **Phase 4.3** - Refactor Stories runner (validate refactor works) (1 day)
4. **Phase 3** - Create prompt files for DDD and Clean Code (1-2 days)
5. **Phase 4.1-4.2** - Refactor DDD and Clean Code runners (1 day)
6. **Phase 5** - Add workflow compliance validation to code-agent (1-2 days)
7. **Phase 6** - Testing and documentation (1-2 days)

**Total estimated time:** 8-12 days

