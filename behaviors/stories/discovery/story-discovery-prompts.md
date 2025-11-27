# Story Discovery Prompts

## Generate Action Prompts

### Prerequisite Questions (Prompting Questions)
These questions must be answered before discovery can proceed:

- Which market increment are we focusing on for discovery?
- What new information or insights have been discovered?
- Are there any changes to business priorities or constraints?
- What is the target delivery timeline for this increment?

### Discovery Refinement Prompts
Once context is established, guide the discovery process:

- Review the current story map - what has changed since initial shaping?
- Which increment(s) are the focus for this discovery session?
- **Increment(s) in Focus**: List ALL stories explicitly (no ~X stories notation)
- **Other Increments**: Use story counts (~X stories) for unexplored areas
- Are there stories that are too ambiguous to estimate?
- Are there stories that are too large (> 12 days)?
- Which features in non-focus increments need story count extrapolations?
- Have priorities changed for any increments?
- Are there dependencies between increments that affect order?

### Markdown Formatting for Continuation Lines
**CRITICAL: Use `&nbsp;` for continuation line spacing:**

Continuation lines (detail/sub-items after stories) MUST use `&nbsp;` entities instead of regular spaces:
- Story line: `│  ├─ 📝 User enters ability rank`
- Continuation: `│  │ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- and system calculates cost`
- Detail line: `│  │ &nbsp;&nbsp;&nbsp; - STR, STA, AGL, DEX`

**Why**: Markdown preview collapses multiple regular spaces into one. Use `&nbsp;` to preserve visual indentation.
**Apply to**: ANY line with a dash (`-`) that comes AFTER a story line (📝) and is NOT itself a story.

### Increment Vertical Slice Validation
**CRITICAL: Validate increments remain end-to-end flows:**

- Does this increment deliver a **complete working flow** from start to finish?
- Does it include **PARTIAL features from MULTIPLE epics** (not complete epics)?
- Can you demonstrate working software after this increment (input → process → validate → persist → display)?
- Are we building **vertical slices** (thin end-to-end) or **horizontal layers** (one complete feature at a time)?
- Does this increment touch multiple areas of the system to create integration?
- If focusing on one area, what minimal stories from other areas enable end-to-end demo?

### Story Refinement Prompts
Identify stories that need attention (based on description, NOT day estimates):

- Which stories lack clear scope or understanding?
- Which stories combine multiple responsibilities? (e.g., selection + calculation + validation)
- Which stories have descriptions that suggest high complexity?
- How should complex stories be split based on their responsibilities?
- Which stories need more detail before committing?
- Add inline **Discovery Refinement** notes for complex/ambiguous stories

### Story Decomposition by Logic Areas and Permutations

**Key Principle: Decompose by Distinct Units of Logic**

**4 Core Decomposition Rules:**
1. **Same logic, different data, same data structure → ONE Story** (consolidate identical UI/validation/calculation)
2. **Different formulas/rules/algorithms/structure → SEPARATE Stories** (split when logic differs)
3. **Enumerate ALL permutations** (identify every different path through requirements)
4. **Cascading updates → Own story when significant** (complex multi-value updates)

**Exhaustive Discovery Questions:**
- What are ALL the different formulas/validation rules/state transitions/data structures?
- What are ALL the permutations/paths through requirements?
- What are ALL the cascading effects and exception cases?
- Can we say "we've thought of everything" for this increment?

**For detailed examples and DO/DON'T patterns, see:**
- `behaviors/stories/stories-rule.mdc` - Principle 2.5: Exhaustive Logic Decomposition

**When to Consolidate vs Separate:**
- **CONSOLIDATE**: Same UI/validation/calculation/state (just different data)
- **SEPARATE**: Different business logic/formulas/rules/algorithms/data structures

### ⚠️ CRITICAL: Consolidation Validation Checklist

**Before finalizing discovery, validate each feature for over-decomposition:**

#### Common Consolidation Violations to Check:

**1. Text Input Fields (MUST CONSOLIDATE)**
- ❌ BAD: "User enters name", "User enters concept", "User enters description" (3 stories)
- ✅ GOOD: "User enters identity fields" (1 story covering name, concept, description)
- **Rule**: Same text input → save logic = ONE story
- **Pattern**: `User enters [field1]`, `User enters [field2]`, `User enters [field3]` with same save logic

**2. Category-Based Validation (CHECK FOR CONSOLIDATION)**
- ❌ BAD: "System validates ability points budget", "System validates skill points budget", "System validates advantage points budget" (3 stories)
- ✅ GOOD: "System validates category points budget" (1 story handling all categories)
- **Rule**: Same validation formula (spent ≤ budget) across categories = ONE story
- **Exception**: Keep separate ONLY if categories have different business rules

**3. Category-Based Calculations (CHECK FOR CONSOLIDATION)**
- ❌ BAD: "System calculates unspent ability points", "System calculates unspent skill points", "System calculates unspent advantage points" (3 stories)
- ✅ GOOD: "System calculates unspent points by category" (1 story)
- **Rule**: Same calculation formula (budget - spent) = ONE story
- **Pattern**: Same math operation on different data categories

**4. Dropdown/Selection Fields (MUST CONSOLIDATE)**
- ❌ BAD: "User selects status", "User selects priority", "User selects category" (3 stories)
- ✅ GOOD: "User selects enumeration fields" (1 story)
- **Rule**: Same dropdown selection logic = ONE story

**5. Display/UI Grouping (CHECK FOR CONSOLIDATION)**
- ❌ BAD: "System groups by category A", "System groups by category B" (2 stories)
- ✅ GOOD: "System groups by category" (1 story)
- **Rule**: Same grouping algorithm = ONE story

#### When to Keep Stories Separate (Do NOT Consolidate):

**1. Different Formulas/Calculations**
- ✅ KEEP SEPARATE: "Calculate half-rank cost (untrained skills)" vs "Calculate full-rank cost (trained skills)"
- **Reason**: Different formulas (0.5 points/rank vs 1 point/rank)

**2. Different State Transitions**
- ✅ KEEP SEPARATE: "Increase from zero" vs "Increase from non-zero"
- **Reason**: Different initial state handling or cascading logic

**3. Different Validation Rules**
- ✅ KEEP SEPARATE: "Validate prerequisite: ability" vs "Validate prerequisite: skill"
- **Reason**: Different prerequisite checking algorithms (ability rank vs skill rank)

**4. Different Post-Processing**
- ✅ KEEP SEPARATE: "Load identity (populate)" vs "Load abilities (populate + recalculate)"
- **Reason**: Different post-load behavior

#### ⚠️ CRITICAL: Discovery Consolidation Workflow

**BEFORE making any consolidation decisions, the AI agent MUST:**

1. **IDENTIFY potential consolidation candidates** (stories that look similar)
2. **LIST QUESTIONS that need domain expert answers**
3. **DOCUMENT ASSUMPTIONS being made**
4. **PRESENT questions and assumptions to USER**
5. **WAIT for user to provide domain knowledge**
6. **THEN apply consolidation based on user's answers**

**DO NOT automatically consolidate or separate without user input!**

#### Discovery Consolidation Questions for User:

**For each feature with similar stories, present these questions:**

**About Formulas/Calculations:**
1. Do [Story A] and [Story B] use the SAME formula/calculation?
   - If different, what is the formula for each?
   - Example: "Do ability points and skill points use the same budget calculation?"

**About Validation Rules:**
2. Do [Story A] and [Story B] have the SAME validation rules?
   - If different, what validation rules apply to each?
   - Example: "Do all categories validate the same way (spent ≤ budget), or do some categories have additional rules?"

**About State Transitions:**
3. Do [Story A] and [Story B] handle state transitions the SAME way?
   - If different, what happens in each case?
   - Example: "Does increasing from zero trigger different logic than increasing from non-zero?"

**About Post-Processing:**
4. Do [Story A] and [Story B] have the SAME post-processing/cascading effects?
   - If different, what additional processing happens?
   - Example: "Does loading abilities require recalculation while loading identity fields does not?"

**About Business Rules:**
5. Do [Story A] and [Story B] follow the SAME business rules?
   - If different, what business rule distinguishes them?
   - Example: "Can trained-only skills go to zero ranks, or must they maintain at least rank 1?"

#### Document Assumptions Before Proceeding:

**For each consolidation decision, document:**

**Assumption Log:**
```
Feature: [Feature Name]
Stories Under Review:
- Story A: [title]
- Story B: [title]
- Story C: [title]

ASSUMPTION: These stories use the same [formula/validation/logic]
QUESTION FOR USER: Is this assumption correct, or do they differ?
- If same → Will consolidate to: [proposed consolidated story]
- If different → Will keep separate because: [reason]

USER INPUT NEEDED: Please confirm or correct this assumption.
```

#### Consolidation Decision Matrix:

Present to user in this format:

| Stories | Assumed Same Logic? | Question for User | If Same → Action | If Different → Action |
|---------|---------------------|-------------------|------------------|----------------------|
| "User enters name" + "User enters concept" | Text input → save | Do these have the same save logic? | Consolidate to "User enters identity fields" | Keep separate (explain why) |
| "System validates ability points" + "System validates skill points" | spent ≤ budget | Do all categories use the same validation formula? | Consolidate to "System validates category points" | Keep separate (document different rules) |

**USER MUST REVIEW AND APPROVE before consolidation applied!**

**Story Format Rules:**
- Title: "User [verb] [noun]" or "System [verb] [noun] when [trigger]"
- Single "and" clause: "- and system [immediate response]"
- NO extra notes, NO examples in story map (save for exploration)
- User action + immediate system response = ONE story (not two)
- System story = system-to-system communication only

**For detailed examples, see:**
- `behaviors/stories/stories-rule.mdc` - Principle 2.6: Story Format and Clarity

### Seek Significant Differences in Business Logic, State, Rules, and Data Structure

**Core Question:** "What fundamentally different business logic must be built?"

**Look for differences in:**
- Business Logic (different algorithms, workflows, processes)
- State Management (different state transitions or lifecycle)
- Business Rules (different constraints or validation rules)
- Data Structure (different data models or relationships)

**Rule of Thumb:** If you'd write significantly different code with different classes/functions/algorithms, it's a different story.

**For detailed DO/DON'T examples (Turn car vs Turn plane, Process credit card vs cryptocurrency, etc.), see:**
- `behaviors/stories/stories-rule.mdc` - Principle 2.5: Exhaustive Logic Decomposition

**CRITICAL COMPLEXITY DETECTION:**

When you see large collections of similar things (80+ advantages, 40+ product types, 30+ rule types, etc.):
- ✅ DO: Create stories per TYPE of behavior, not per collection item
- ❌ DON'T: One generic story for 80+ items that have different behavioral types

**Examples of collections that hide complexity:**
- Catalogs (advantages, powers, equipment, etc.)
- Product types (physical goods, digital goods, services, subscriptions)
- Inventory types (raw materials, work-in-progress, finished goods)
- Rule types (validation rules, calculation rules, business rules)
- Entity types (users, organizations, teams, projects)
- Configuration types (settings, preferences, policies)

**Complexity estimation by collection size:**
- 10-20 items → 3-5 stories (2-3 behavioral types)
- 20-40 items → 5-8 stories (3-5 behavioral types)
- 40-80 items → 8-15 stories (5-8 behavioral types with variation)
- 80+ items → 15-25 stories (8-12 behavioral types with complex variations)

**Red flags for underestimation:**
- ~X items where X > 30 handled in < 5 stories
- "Collection", "catalog", or "types" without breaking down by behavioral type
- Single validation story for multiple validation types
- Single calculation story for multiple formulas
- Single CRUD story for entities with different state models
- Pages of requirements per story (should be many stories per page, not the reverse)

**CRITICAL**: 
- Discovery does NOT add day estimates. Estimates require human entry and comparison to previous work.
- Discovery does NOT add "Status: DISCOVERY" lines
- Discovery does create separate increment files for incement of focus
- Discovery DOES decompose stories by types/rules/exceptions with different behaviors

### Decomposition Level: Shaping vs Discovery

**SHAPING (10-20% decomposition):**
- Representative samples, use story counts (~X stories) for most areas
- Capture main flow, acknowledge variations exist

**DISCOVERY (100% decomposition for increment in focus):**
- Enumerate ALL logic permutations exhaustively
- NO story counts (~X) - everything explicit
- Ask "Have we thought of everything for this increment?"

**For detailed comparison and examples, see:**
- `behaviors/stories/stories-rule.mdc` - Section 1 (Shaping) vs Section 2 (Discovery) principles

### Story Counting Prompts
For increments NOT in focus (unexplored areas):

- Which features in non-focus increments are not yet decomposed?
- Based on similar features, how many stories might this feature have?
- What is the estimated story count? (Use "~X stories" format)
- Which epics need story count rollups?

**CRITICAL**: Increment(s) in focus must have ALL stories listed explicitly (no ~X stories)

## Validate Action Prompts

### Review Prompts
Guide user through validation results:

- Review the validation report
- Are there any ERROR-level violations?
- Are there any WARNING-level violations?
- What changes are needed to address violations?
- Should validation be re-run after changes?

### Refinement Check Prompts
If no refinement detected:

- Has the story map changed since initial shaping?
- What discovery insights should be captured?
- Which increments need updates?

### Story Count Check Prompts
If story counts missing:

- Which features are not yet decomposed?
- Add story counts to unexplored areas using "~X stories" format
- Which epics need story count rollups?

### Refinement Check Prompts
If refinement notes missing:

- Which stories are too ambiguous?
- Which stories exceed 12 days?
- How should large stories be split?
- Document refinement notes inline or in separate file

## Workflow Guidance

### When to Use Discovery
- After initial story shaping is complete
- Before committing to next increment
- When new information changes priorities
- When team is ready to finalize stories for development

### What Discovery Produces
- Single story-map-increments.md file with NOW/NEXT/LATER organization
- Increment(s) in focus with ALL stories explicitly listed
- Other increments with story counts (~X stories) for unexplored areas
- Inline refinement notes for ambiguous/large/complex stories
- Updated priorities based on new insights
- NO separate increment files
- NO "Status: DISCOVERY" lines
- NO day estimates (added by humans only)

### Success Criteria
- ✅ Increment(s) in focus have ALL stories explicitly listed (no ~X stories)
- ✅ Other increments use story counts (~X stories) for unexplored areas
- ✅ Story map shows refinement from initial shaping
- ✅ Refinement notes added inline for ambiguous/large/complex stories
- ✅ Increments have clear definitions with NOW/NEXT/LATER priorities
- ✅ NO separate increment files created
- ✅ NO "Status: DISCOVERY" lines added
- ✅ NO day estimates added by AI
- ✅ Team agrees on increment scope

