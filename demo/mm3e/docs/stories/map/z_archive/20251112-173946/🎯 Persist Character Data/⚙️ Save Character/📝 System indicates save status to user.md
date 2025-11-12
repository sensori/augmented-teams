# 📝 System indicates save status to user

**Epic:** Persist Character Data
**Feature:** Save Character

## Story Description

System indicates save status to user - Displays "Saving...", "Saved", or "Error" status with appropriate visual feedback

## Acceptance Criteria

**AC are located in feature document, NOT in story document**

See feature document for acceptance criteria: `⚙️ Save Character - Feature Overview.md`

## Notes

**Shared Component**:
- Status indicator is a SHARED UI component used by all save operations (Stories 1, 2, 3, 4)
- Different prominence levels: Manual save (prominent), Auto-save (subtle)
- Status states: Saving, Saved (with timestamp), Unsaved Changes, Error (with retry)

**Consolidation Applied**:
- Single status indicator component serves all save contexts
- Prominence level adjusts based on save type (manual vs auto)
- Validation warnings (Story 4) work alongside status indicators

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Discovery Refinements: Shared status indicator component, prominence levels for different save types, timestamp display for user awareness

