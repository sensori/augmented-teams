### Command: /story-explore-validate

**[Purpose]:**
Validate acceptance criteria against story exploration principles.

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 3: Story Exploration Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-explore validate [feature-doc-path]` — Validate acceptance criteria against principles

---

## Delegate to Main Command

This command delegates to **Action 3: VALIDATE** in the main `/story-explore` command.

See: `behaviors/stories/exploration/story-explore-cmd.md` - Action 3: VALIDATE

---

## Summary

This command validates:
1. ✅ Domain AC present at feature level (in feature document)
2. ✅ Domain AC structured as mini domain map (Core Concepts → Behaviors → Rules)
   - Starts with Core Domain Concepts (nouns): Character, Ability, Skill, etc.
   - Then Domain Behaviors (verbs ON concepts): Save Character, Validate Character
   - Then Domain Rules: Formulas, patterns, constraints
   - NOT operations-first without defining business concepts
3. ✅ Domain AC references domain map when available (checks for `<system-name>-domain-map.txt`)
   - If domain map exists: validates that Domain AC uses concepts from domain map
   - If domain map exists: validates that Domain AC references relevant domain map sections
4. ✅ Domain AC uses domain language, NOT technical language (see `behaviors/ddd/ddd-rule.mdc` Principles 1, 4, 5, 7, 10)
   - Uses domain nouns for concepts: "Character", "Ability", "Skill"
   - NOT technical terms: "API", "JSON", "Database", "Endpoint", "Schema"
   - Focuses on WHAT domain does, NOT HOW it's implemented
5. ✅ Behavioral AC present for each story (in feature document under each story)
6. ✅ AC written in When/Then format (NO "Given" clauses)
7. ✅ AC uses behavioral language (not technical/code patterns)
8. ✅ AC consolidation review documented (BELOW all AC)
9. ✅ Source material references included (BELOW all AC)
10. ✅ AC located in feature documents, NOT in story documents
11. ✅ Notes, consolidation decisions, domain rules, and source material are BELOW all acceptance criteria

**Output**: Validation report with violations and suggestions

