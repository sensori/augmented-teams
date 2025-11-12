# 📝 User saves character with validation errors

**Epic:** Persist Character Data
**Feature:** Save Character

## Story Description

User saves character with validation errors - and system warns about errors but allows save to proceed (user control philosophy)

## Acceptance Criteria

**AC are located in feature document, NOT in story document**

See feature document for acceptance criteria: `⚙️ Save Character - Feature Overview.md`

## Notes

**CRITICAL - User Control Philosophy**:
- "Warn, Don't Prevent" - validation errors NEVER block save operations
- User is in control and may intentionally break rules (house rules, experimental builds, etc.)
- System highlights errors and warns clearly, but ultimate decision belongs to user
- This applies to ALL save operations: manual save, auto-save, revision save

**Consolidation Applied**:
- Warning system applies to all save operations (Stories 1, 2, 3)
- Error highlighting is consistent across manual and auto-save
- Navigation and actionable messages shared across save contexts

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Validation rules
- Discovery Refinements: "Warn, Don't Prevent" philosophy - user control over rule-breaking, errors highlight but never block save operations

