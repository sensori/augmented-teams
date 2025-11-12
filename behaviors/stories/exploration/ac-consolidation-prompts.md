# Acceptance Criteria Consolidation Prompts

**Purpose**: Guide AC enumeration and consolidation review during Exploration phase, using Feature Overview template.

**Template Reference**: `behaviors/stories/templates/feature-overview-template.md`
**Principle Reference**: `behaviors/stories/stories-rule.mdc` - Principle 2.5 (applied to ACs), Principle 3.2
**Consolidation Patterns**: `behaviors/stories/discovery/consolidation-checklist.md` (same patterns apply to ACs)

---

## Template Usage

**MANDATORY**: Load template file:
- `behaviors/stories/templates/feature-overview-template.md`

**Key Placeholder:**
- `{stories_with_ac}`: This is where you fill in all stories with their acceptance criteria

**Format for {stories_with_ac}:**
```markdown
### 1. **[Story Title]** - 📝 [Verb] [Noun]

**Story Description**: [description]

#### Acceptance Criteria

##### [AC Group Name]
- **When** [condition], **then** [outcome]
- **When** [condition], **then** [outcome]

---
```

---

## Core Consolidation Rule (Applied to ACs)

**Same logic, different data, same data structure** → ONE Acceptance Criterion  
**Different formulas/rules/algorithms/structure** → SEPARATE Acceptance Criteria

---

## AC Enumeration Prompts

### Step 1: Enumerate ALL AC Permutations

For each story, ask:
- What are ALL the validation paths?
- What are ALL the calculation branches?
- What are ALL the state transitions?
- What are ALL the exception cases?
- What are ALL the different outcomes?
- What edge cases exist?

### Step 2: Document Initial AC List

List every acceptance criterion before consolidation:
```
Story: [Story Name]

Initial AC Enumeration (before consolidation):
1. When [condition A for field 1], then [outcome]
2. When [condition A for field 2], then [outcome]
3. When [condition A for field 3], then [outcome]
...
```

---

## Consolidation Review Prompts

### Step 3: Identify Consolidation Candidates

Group ACs that MIGHT have same logic:
- Do these ACs use the same formula/algorithm?
- Do they differ only in field/category names?
- Would the implementation code be identical except for variable names?
- Do they have the same validation pattern?
- Do they follow the same state transition?

### Step 4: Document Assumptions

For each consolidation candidate group:

**Assumption Documentation Template:**
```
AC Consolidation Candidate Group:
- AC 1: When [condition for X], then [outcome]
- AC 2: When [condition for Y], then [outcome]  
- AC 3: When [condition for Z], then [outcome]

ASSUMPTION: These use the same [formula/validation/algorithm/pattern]
- Formula: [document the formula]
- Only differs by: [field name / category / entity type]
- Would consolidate to: When [generalized condition], then [outcome]

QUESTION FOR DOMAIN EXPERT:
- Is the [formula/validation/algorithm] truly identical for X, Y, and Z?
- Are there any edge cases where X, Y, or Z behave differently?
- Any business rules that differ between these?
```

### Step 5: Present Consolidation Decision Matrix

**Consolidation Decision Matrix Template:**
```markdown
| AC Group | Consolidation Opportunity | Same Logic? | Recommendation | Decision |
|----------|---------------------------|-------------|----------------|----------|
| ACs 1-3 (field validations) | Same required field pattern | ❓ | CONSOLIDATE? | ⏸️ WAIT |
| ACs 4-6 (calculations) | Different formulas per type | ❌ No | KEEP SEPARATE | ⏸️ WAIT |
| ACs 7-9 (state transitions) | ❓ Unknown | ❓ | ASK USER | ⏸️ WAIT |
```

### Step 6: Ask Clarifying Questions

For each uncertain consolidation:

**Question Template:**
```
CLARIFYING QUESTION [#N]:

Story: [Story Name]
ACs in Question: [AC numbers]

SCENARIO: [Describe the acceptance criteria]

ASSUMPTION: We assume these use [same formula/algorithm/pattern]

QUESTION: 
- Do [entity A] and [entity B] use the same [validation/calculation/logic]?
- Are there any differences in how [A] vs [B] handle [specific scenario]?
- Any edge cases where behavior differs?

IF SAME: We'll consolidate to 1 AC
IF DIFFERENT: We'll keep as separate ACs
```

---

## Consolidation Patterns (Reference)

See `behaviors/stories/discovery/consolidation-checklist.md` for detailed patterns.

### Common AC Consolidation Patterns

#### Pattern 1: Field Validation
**Consolidation Candidate:**
```
- When name field is empty, then show required error
- When email field is empty, then show required error
- When phone field is empty, then show required error
```

**Decision:**
- Same validation logic? → CONSOLIDATE to "When required field is empty, then show required error"
- Different validation (e.g., email has format check)? → KEEP SEPARATE

#### Pattern 2: Calculation by Category
**Consolidation Candidate:**
```
- When ability points exceed budget, then flag overspend
- When skill points exceed budget, then flag overspend
- When advantage points exceed budget, then flag overspend
```

**Decision:**
- Same formula (points ≤ budget)? → CONSOLIDATE to "When category points exceed budget, then flag overspend"
- Different formulas per category? → KEEP SEPARATE

#### Pattern 3: State Transition by Type
**Consolidation Candidate:**
```
- When character gains negative rank in Strength, then recalculate Strength modifier
- When character gains negative rank in Agility, then recalculate Agility modifier
- When character gains negative rank in Stamina, then recalculate Stamina modifier
```

**Decision:**
- Same calculation pattern? → CONSOLIDATE to "When character gains negative rank in ability, then recalculate ability modifier"
- Different calculations per ability? → KEEP SEPARATE

---

## Post-Consolidation Documentation

After user confirms consolidation decisions:

### Document Consolidation Rationale

In feature document, add:
```markdown
**AC Consolidation Decisions:**
- ✅ ACs 1-3 consolidated: Same required field validation (formula: field != empty)
- ✅ ACs 7-9 consolidated: Same budget check (formula: spent ≤ budget)
- ❌ ACs 4-6 kept separate: Different cost formulas (0.5 vs 1.0 vs 2.0 points/rank)
- ❌ ACs 10-12 kept separate: Different prerequisite algorithms (ability rank vs skill rank vs advantage presence)
```

### Reference Source Material

Link to formulas/rules from Discovery Refinements:
```markdown
**Source Material References:**
- Ability modifier: (rank - 10) ÷ 2 rounded down (Source: Discovery Refinements, Chapter 2)
- Point budget: 15 × PL (Source: Discovery Refinements, Chapter 1)
- Skill costs: 0.5 pts/rank (untrained), 1.0 pts/rank (trained) (Source: Discovery Refinements, Chapter 3)
```

---

## Critical Reminders

1. ⚠️ **DO NOT** automatically consolidate without user confirmation
2. ⚠️ **DO** document ALL assumptions about logic similarity
3. ⚠️ **DO** present consolidation decision matrix BEFORE finalizing
4. ⚠️ **DO** wait for user to answer clarifying questions
5. ⚠️ **DO** apply same consolidation rules as story-level (Principle 2.5)

---

## Reference Documents

- **Core Principle**: `behaviors/stories/stories-rule.mdc` - Principle 2.5: Exhaustive Logic Decomposition
- **Exploration Principle**: `behaviors/stories/stories-rule.mdc` - Principle 3.2: Apply Logic Decomposition at AC Level
- **Consolidation Patterns**: `behaviors/stories/discovery/consolidation-checklist.md`
- **Command Workflow**: `behaviors/stories/exploration/story-explore-cmd.md` - Steps 6-8




