### Command: /story-explore-generate

**[Purpose]:**
Generate acceptance criteria for stories with exhaustive AC decomposition and consolidation review.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 3: Story Exploration Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-explore generate [feature-doc-path]` — Generate acceptance criteria for feature

---

## Delegate to Main Command

This command delegates to **Action 1: GENERATE** in the main `/story-explore` command.

See: `behaviors/stories/exploration/story-explore-cmd.md` - Action 1: GENERATE

---

## Summary

This command:
1. Reads source material from story map (Discovery Refinements)
2. Enumerates ALL acceptance criteria permutations for stories/features
3. Presents CONSOLIDATION REVIEW to user (identifies similar ACs, asks questions)
4. Waits for user confirmation on consolidation decisions
5. Generates final Domain AC (feature level) and Behavioral AC (story level)
6. Updates feature documents with AC (NOT story documents)
7. Uses When/Then format (NO "Given" clauses at AC level)

**Output**: Feature documents with Domain AC and Behavioral AC for all stories

---

## CRITICAL: Feature-Scoped Domain Perspective

### The Pattern

**Each feature defines domain concepts through the lens of that feature's concerns.**

Do NOT define the entire domain model in every feature. Instead, define only the facets/aspects of domain concepts that matter to THIS feature.

### Example: "Character" concept across 3 features

**Feature 1: Establish Identity**
```
Character:
- Identity Fields (name, real name, concept...)
- Demographics (age, height, weight, gender)
- Power Level (determines scale)
- Point Budget (15 × PL)
```

**Feature 2: Allocate Abilities**
```
Character:
- Has 8 Abilities (Strength, Stamina, Agility...)
- Point Budget (15 × Power Level)
- Ability Point Tracking (separate category)
```

**Feature 3: Save Character**
```
Character:
- Composed of: Abilities, Skills, Advantages, Powers...
- States: Draft vs Complete
- Validation Philosophy: "Warn, Don't Prevent"
```

**Same domain concept, different facets emphasized per feature context!**

### Why This Works

✅ **Bounded Context Principle** - Each feature shows only what matters in its context
✅ **No Duplication** - Each feature defines aspects relevant to it, not everything
✅ **Clear Dependencies** - You see exactly which domain concepts a feature touches
✅ **Testable Scope** - AC can reference these feature-specific facets directly
✅ **Domain Language** - Always business concepts, never technical implementation
✅ **Maintainable** - Changes to a concept only update features that use those aspects

### Anti-Pattern: Full Domain Model in Every Feature

❌ **DON'T** copy the entire Character definition into every feature
❌ **DON'T** define attributes/behaviors not used by this feature
❌ **DON'T** duplicate domain rules across features

### Correct Pattern: Feature-Relevant Facets Only

✅ **DO** define only the aspects of Character relevant to this feature
✅ **DO** emphasize the facets this feature operates on
✅ **DO** reference shared concepts from higher levels when available

### Canonical Reference

See: `demo/mm3e/docs/stories/map/` for examples:
- `⚙️ Establish Identity - Feature Overview.md` - Identity facets
- `⚙️ Allocate Abilities - Feature Overview.md` - Ability system facets
- `⚙️ Save Character - Feature Overview.md` - Persistence facets

