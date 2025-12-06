# Validation Report: Mob Minion Story Map

**Generated:** 2025-12-06  
**Project:** Mob Minion  
**Behavior:** shape  
**Validation Status:** Completed with violations

---

## Summary

- **Total Documents Validated:** 3
  - `story-graph.json`
  - `mob-minion-domain-model-description.md`
  - `mob-minion-domain-model-diagram.md`
- **Rules Checked:** 25 behavior-specific rules + common bot rules
- **Violations Found:** 11 naming/format violations
- **Requirements Verified:** ✓ Domain concepts align with clarification.json, ✓ Business domain matches, ✓ Core concepts identified, ✓ User goals addressed

---

## Violations Found

### 1. Naming Format Violations (Verb-Noun, Capitalization, Typos)

**Rule Violated:** `use_active_behavioral_language.json` - Stories must use verb-noun format with action verbs

**Violations:**

1. **Line 130:** `"Add Minion To Mob"` 
   - **Issue:** Should use third person for consistency
   - **Suggested:** `"Adds Minion To Mob"` (preserving context "To Mob")

2. **Line 137:** `"Clone Minions In Mob"`
   - **Issue:** Should use third person for consistency
   - **Suggested:** `"Clones Minions In Mob"` (preserving context "In Mob")

3. **Line 104:** `"Manage Mob MInions"`
   - **Issue:** Typo - "MInions" should be "Minions"
   - **Suggested:** `"Manage Mob Minions"`

4. **Line 300:** `"Limit Based On senses"`
   - **Issue:** Inconsistent capitalization, should use third person
   - **Suggested:** `"Limits Based On Senses"`

5. **Line 322:** `"Select  Strategy"`
   - **Issue:** Double space
   - **Suggested:** `"Selects Strategy"`

6. **Line 359:** `"Attack Who did most damage"`
   - **Issue:** Inconsistent capitalization, should use third person
   - **Suggested:** `"Attacks Who Did Most Damage"` or `"Attacks Highest Damage Dealer"`

7. **Line 368:** `"Attack targets In Area"`
   - **Issue:** Inconsistent capitalization, should use third person
   - **Suggested:** `"Attacks Targets In Area"`

8. **Line 377:** `"Attack  Biggest Threat"`
   - **Issue:** Double space, should use third person
   - **Suggested:** `"Attacks Biggest Threat"`

9. **Line 386:** `"Attack  Based On Aggresion"`
   - **Issue:** Double space, typo "Aggresion" should be "Aggression", should use third person
   - **Suggested:** `"Attacks Based On Aggression"`

10. **Line 468:** `"Maximize Distance In Range"`
    - **Issue:** Should use third person
    - **Suggested:** `"Maximizes Distance In Range"`

11. **Line 475:** `"Take Advantage Of Wallls /Cover"`
    - **Issue:** Typo "Wallls" should be "Walls", inconsistent spacing
    - **Suggested:** `"Takes Advantage Of Walls And Cover"`

---

## Requirements Verification

### ✓ Clarification.json Requirements
- **Domain concepts:** All core concepts from clarification.json are present (Mob, Minion, Strategy, Target Selection, Actions)
- **Business domain:** Matches "Virtual tabletop game management - specifically minion/mob combat management within Foundry VTT"
- **User goals:** Addressed - Control multiple minions as a single mob unit
- **Core concepts:** Identified correctly - Mob groups minions, Strategy determines behavior

### ✓ Planning.json Requirements
- **Flow scope:** Stories have `sequential_order` which provides context (when/why/outcome from position in sequence)
- **Depth of shaping:** Workflow structure is present with logical process and alternate/or conditions
- **Bounded context:** Grouped by business capability (Mob Management, Action Execution)

**Note:** Detailed flow validation (end-to-end user-system behavior, one interaction/response) will be handled in discovery phase - not flagged as violations in shape phase.

---

## Suggested Corrections

1. **Fix naming violations:** Update all story names to consistent third-person verb-noun format
2. **Fix typos:** 
   - "MInions" → "Minions" (line 104)
   - "Aggresion" → "Aggression" (line 386)
   - "Wallls" → "Walls" (line 475)
3. **Remove double spaces:** Fix spacing issues in sub-epic and story names (lines 322, 377, 386)
4. **Standardize capitalization:** Ensure consistent capitalization in story names

---

## Content Quality Assessment

**Strengths:**
- Domain concepts are well-structured and align with business requirements
- Story order provides context through `sequential_order`
- Domain model descriptions are clear and use ubiquitous language
- Relationships between concepts are properly documented

**Areas for Improvement:**
- Naming consistency (verb tense, capitalization)
- Typo corrections needed
- Spacing consistency

---

## Next Steps

1. Apply suggested corrections to story-graph.json
2. Re-run validation after corrections
3. Proceed to discovery phase for detailed flow validation

---

## Source Material

**Source:** Validation performed against story-graph.json, domain-model-description.md, domain-model-diagram.md  
**Clarification Reference:** `demo/mob_minion/docs/stories/clarification.json`  
**Planning Reference:** `demo/mob_minion/docs/stories/planning.json`  
**Rules Applied:** 25 behavior-specific rules from `agile_bot/bots/story_bot/behaviors/1_shape/3_rules/`
