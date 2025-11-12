# ⚙️ [Feature Name] - Feature Overview

**File Name**: `⚙️ [Feature Name] - Feature Overview.md`

**Epic:** [Epic Name]

## Feature Purpose

[One paragraph describing what this feature enables users to do and why it matters to the system]

---

## Domain AC (Feature Level)

⭐ **FEATURE-SCOPED DOMAIN PERSPECTIVE**: Define domain concepts through the lens of THIS feature's concerns. Do NOT copy entire domain model - define only the facets/aspects THIS feature operates on.

### Core Domain Concepts

**[Domain Concept 1]:** [Brief description - ONLY the facets relevant to THIS feature]
- **[Facet 1]**: [Attribute or property this feature touches]
- **[Facet 2]**: [Another attribute this feature operates on]
- **[Relationship]**: [How this concept relates to others in THIS feature's context]

**[Domain Concept 2]:** [Brief description]
- **[Facet 1]**: [Only aspects relevant to this feature]
- **[Facet 2]**: [Not every attribute of the concept, just what matters here]

**[Domain Concept 3]:** [Brief description]
- **[Facet 1]**: [Feature-specific perspective]

---

### Domain Behaviors

**[Behavior 1]:** [Verb describing operation on domain concept]
- **[Aspect 1]**: [How behavior works in this feature's context]
- **[Aspect 2]**: [Result or effect]
- **[Aspect 3]**: [Constraints or rules]

**[Behavior 2]:** [Another operation]
- **[Aspect 1]**: [Details specific to this feature]

---

### Domain Rules

**[Rule Category 1]:**
- Formula: [Mathematical or logical formula]
- Examples:
  - [Example 1]
  - [Example 2]

**[Rule Category 2]:**
- Constraint: [Business constraint]
- Validation: [How rule is enforced]

---

## Stories ([N] total)

### 1. **[Story Title]** - 📝 [Short description]

**Story Description**: [Story title] - and system [immediate system response]

#### Acceptance Criteria

##### [AC Group 1]
- **When** [condition/action], **then** [observable outcome]

##### [AC Group 2]
- **When** [condition/action], **then** [observable outcome]

---

### 2. **[Story Title]** - 📝 [Short description]

**Story Description**: [Story title] - and system [immediate system response]

#### Acceptance Criteria

##### [AC Group 1]
- **When** [condition/action], **then** [observable outcome]

---

[Repeat for all stories in feature]

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ [What was consolidated] - [Rationale: same logic/formula/algorithm]

**Separated (Different Logic):**
- ❌ [What was separated] - [Rationale: different formulas/rules/algorithms]

**Result**: [N] stories with [description of separation strategy]

---

## Domain Rules Referenced

**From [Source Material]:**
- [Section/Chapter]: [Page range] - [What was referenced]
- [Formula/Rule]: [Specific rule extracted]
- [Pattern]: [Business pattern documented]

**Discovery Refinements Applied:**
- [Consolidation decision applied]
- [Logic pattern identified]
- [Formula or rule clarified]

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: [Source material name]
- [Section/Chapter]: [Page range] - [What domain knowledge extracted]
- Discovery Refinements:
  - [Specific refinement applied]
  - [Consolidation pattern used]
  - [Formula or calculation documented]

---

## EXAMPLES: Feature-Scoped Domain Perspective

### Example 1: "Character" concept across 3 features

**Feature: Establish Identity**
```
Character:
- Identity Fields (name, real name, concept, description, player name)
- Demographics (age, height, weight, gender)
- Power Level (determines character's power scale)
- Point Budget (15 × Power Level)
```
→ Shows identity and setup facets ONLY

**Feature: Allocate Abilities**
```
Character:
- Has 8 Abilities (Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- Point Budget (15 × Power Level)
- Ability Point Tracking (tracks points spent on abilities separately)
```
→ Shows ability system facets ONLY

**Feature: Save Character**
```
Character:
- Composed of: 8 Abilities, Skills (variable count), Advantages, Powers, Defenses, Attacks, Equipment
- Identity: Name, real name, concept, description, player name, age, height, weight, gender
- Point Budget: 15 × Power Level (total points available for building character)
- States: Draft (work in progress, may have validation errors), Complete (ready for play)
- Validation Philosophy: "Warn, Don't Prevent" - errors warn user but never block saves
```
→ Shows persistence and validation facets ONLY

**Same domain concept (Character), different facets emphasized per feature context!**

### Why This Works

✅ **Bounded Context Principle** - Each feature shows only what matters in its context
✅ **No Duplication** - Each feature defines aspects relevant to it, not everything
✅ **Clear Dependencies** - You see exactly which domain concepts a feature touches
✅ **Testable Scope** - AC can reference these feature-specific facets directly
✅ **Domain Language** - Always business concepts, never technical implementation
✅ **Maintainable** - Changes to a concept only update features that use those aspects

### Anti-Pattern: Full Domain Model in Every Feature

❌ **DON'T** copy the entire Character definition (all 50+ attributes) into every feature
❌ **DON'T** define attributes/behaviors not used by this feature
❌ **DON'T** duplicate domain rules across features

### Correct Pattern: Feature-Relevant Facets Only

✅ **DO** define only the aspects of Character relevant to this feature
✅ **DO** emphasize the facets this feature operates on
✅ **DO** reference shared concepts from higher levels when available (epic/solution level)


