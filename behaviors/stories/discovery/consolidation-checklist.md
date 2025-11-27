# Story Consolidation Checklist

**Purpose**: Validate discovered stories against consolidation principle before finalizing increment.

**Principle**: Same logic, different data, same data structure → ONE Story

---

## Quick Validation Questions

For each feature with multiple stories, ask:

1. ✅ **Do these stories use the SAME algorithm/formula?** → If yes, consider consolidating
2. ✅ **Do these stories differ only in data field names?** → If yes, consolidate
3. ✅ **Would the implementation code be identical except for field names?** → If yes, consolidate
4. ❌ **Do these stories have different business rules?** → If yes, keep separate
5. ❌ **Do these stories have different state transitions?** → If yes, keep separate
6. ❌ **Do these stories have different formulas/calculations?** → If yes, keep separate

---

## Common Consolidation Patterns

### Pattern 1: Text Input Fields
**Violation Pattern**:
```
📝 User enters name - and system saves to character sheet
📝 User enters concept - and system saves as descriptor
📝 User enters description - and system saves to profile
```

**Consolidation**:
```
📝 User enters identity fields - and system saves name, concept, and description
```

**Rule**: Same text input → save logic = ONE story

---

### Pattern 2: Category-Based Validation
**Violation Pattern**:
```
📝 System validates ability points at or under budget - Flags overspend in abilities
📝 System validates skill points at or under budget - Flags overspend in skills
📝 System validates advantage points at or under budget - Flags overspend in advantages
```

**Consolidation**:
```
📝 System validates category points at or under budget - Flags overspend by category
```

**Rule**: Same validation formula (spent ≤ budget) = ONE story  
**Exception**: Keep separate if categories have different validation rules

---

### Pattern 3: Category-Based Calculations
**Violation Pattern**:
```
📝 System calculates unspent ability points - and displays remaining abilities
📝 System calculates unspent skill points - and displays remaining skills
📝 System calculates unspent advantage points - and displays remaining advantages
```

**Consolidation**:
```
📝 System calculates unspent points by category - and displays remaining by category
```

**Rule**: Same calculation (budget - spent) = ONE story

---

### Pattern 4: Enumeration/Dropdown Selection
**Violation Pattern**:
```
📝 User selects priority - and system saves selection
📝 User selects status - and system saves selection
📝 User selects category - and system saves selection
```

**Consolidation**:
```
📝 User selects enumeration fields - and system saves selections
```

**Rule**: Same dropdown selection logic = ONE story

---

### Pattern 5: Grouping/Filtering Operations
**Violation Pattern**:
```
📝 System groups skills by strength - Displays skills under strength
📝 System groups skills by agility - Displays skills under agility
📝 System groups skills by intellect - Displays skills under intellect
```

**Consolidation**:
```
📝 System groups skills by ability category - Displays skills under each ability
```

**Rule**: Same grouping algorithm = ONE story

---

## When to Keep Stories SEPARATE

### ✅ Different Formulas/Calculations
```
✅ KEEP SEPARATE:
📝 User adds rank to untrained skill - and system calculates half-rank cost
📝 User adds rank to trained-only skill - and system validates training and calculates full-rank cost
```
**Reason**: Different formulas (0.5 points/rank vs 1 point/rank) + additional validation

---

### ✅ Different State Transitions
```
✅ KEEP SEPARATE:
📝 User increases ability rank from zero - and system calculates cost
📝 User increases ability rank from non-zero - and system calculates incremental cost
```
**Reason**: Different initial state handling ("cost" vs "incremental cost")

---

### ✅ Different Validation Rules
```
✅ KEEP SEPARATE:
📝 System validates ability score prerequisite - Checks minimum ability rank required
📝 System validates skill rank prerequisite - Checks minimum skill rank required
📝 System validates other advantage prerequisite - Checks character has required advantage
```
**Reason**: Different prerequisite checking algorithms (ability rank vs skill rank vs advantage presence)

---

### ✅ Different Post-Processing Logic
```
✅ KEEP SEPARATE:
📝 System loads character identity fields - Populates name, concept, real name
📝 System loads character abilities - Populates ability ranks and recalculates modifiers
📝 System loads character skills - Populates skill ranks and recalculates totals
```
**Reason**: Different post-load behavior (simple populate vs populate + recalculate)

---

### ✅ Different Business Rules
```
✅ KEEP SEPARATE:
📝 User saves new character to cloud storage - and system validates data completeness
📝 User saves existing character changes - and system updates existing record
```
**Reason**: Different save paths (create with validation vs update existing)

---

## Checklist for Each Feature

Use this checklist when reviewing discovered stories:

### Feature: ___________________

**Stories Count**: _____ stories

#### Step 1: Identify Similar Stories
List stories that sound similar:
- [ ] Story 1: _________________
- [ ] Story 2: _________________
- [ ] Story 3: _________________

#### Step 2: Compare Logic
- [ ] Do they use the same algorithm/formula?
- [ ] Do they differ only in field names?
- [ ] Would implementation code be identical except for names?

#### Step 3: Check for Differences
- [ ] Different formulas/calculations? → Keep separate
- [ ] Different validation rules? → Keep separate
- [ ] Different state transitions? → Keep separate
- [ ] Different post-processing? → Keep separate

#### Step 4: Decision
- [ ] **CONSOLIDATE**: Same logic, different data
- [ ] **KEEP SEPARATE**: Different business logic

#### Step 5: Document Rationale
**Decision**: ___________________  
**Reason**: ___________________

---

## Post-Discovery Validation

After completing discovery for an increment, validate:

1. [ ] No multiple "User enters [field]" stories with same save logic
2. [ ] No multiple "System validates [category]" with same formula
3. [ ] No multiple "System calculates [category]" with same formula
4. [ ] No multiple "System groups/filters by [category]" with same algorithm
5. [ ] No multiple "User selects [enum]" with same dropdown logic
6. [ ] All similar stories have documented rationale for keeping separate
7. [ ] Consolidation decisions documented in Discovery Notes section

---

## Reference

**Rule Source**: `behaviors/stories/stories-rule.mdc` - Principle 2.5: Exhaustive Logic Decomposition  
**Prompts**: `behaviors/stories/discovery/story-discovery-prompts.md` - Consolidation Validation Checklist  
**Command**: `/story-discovery-validate` - Check 5: Consolidation Principle Applied

