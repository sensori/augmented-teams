# 📝 User enters identity text fields

## Story Information
**Feature**: Establish Identity
**Epic**: Create Character
**Status**: Scenarios Added

---

## Story Description

User enters identity text fields - and system saves name, real name, concept, description, and player name

---

## Acceptance Criteria Reference
**Source**: Feature document - ⚙️ Establish Identity - Feature Overview.md

- AC1: When user enters character name, then system saves name to character
- AC2: When user enters real name, then system saves real name to character
- AC3: When user enters character concept, then system saves concept to character
- AC4: When user enters character description, then system saves description to character
- AC5: When user enters player name, then system saves player name to character

---

## Background

**Given** character creation screen is displayed
**And** the Establish Identity section is displayed
**And** all identity text fields are initially empty

---

## Scenarios

### Scenario 1: Enter character name successfully

**Purpose**: User enters character name and system saves it

**Given** the character name field is empty
**When** user types "Shadow Phoenix" into the character name field
**Then** system saves "Shadow Phoenix" as the character name
**And** the character name displays "Shadow Phoenix" in the field
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC1

---

### Scenario 2: Enter real name successfully

**Purpose**: User enters character's real name and system saves it

**Given** the real name field is empty
**When** user types "Marcus Thompson" into the real name field
**Then** system saves "Marcus Thompson" as the character's real name
**And** the real name displays "Marcus Thompson" in the field
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC2

---

### Scenario 3: Enter character concept successfully

**Purpose**: User enters character concept and system saves it

**Given** the concept field is empty
**When** user types "Street-smart vigilante with fire powers" into the concept field
**Then** system saves "Street-smart vigilante with fire powers" as the character concept
**And** the concept displays in the field
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC3

---

### Scenario 4: Enter character description successfully

**Purpose**: User enters character description and system saves it

**Given** the description field is empty
**When** user types "A former firefighter who gained pyrokinetic abilities during a chemical plant explosion" into the description field
**Then** system saves the description text to the character
**And** the description displays in the field
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC4

---

### Scenario 5: Enter player name successfully

**Purpose**: User enters player name and system saves it

**Given** the player name field is empty
**When** user types "Alex Johnson" into the player name field
**Then** system saves "Alex Johnson" as the player name
**And** the player name displays "Alex Johnson" in the field
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC5

---

### Scenario 6: Enter text with special characters

**Purpose**: System accepts and saves text with special characters, punctuation, and unicode

**Given** the character name field is empty
**When** user types "Ñørdīç Thüñdër" into the character name field
**Then** system saves "Ñørdīç Thüñdër" exactly as entered
**And** the character name displays "Ñørdīç Thüñdër" with all special characters preserved
**And** unicode characters are displayed correctly

**Acceptance Criteria Covered**: AC1

---

### Scenario 7: Enter very long text

**Purpose**: System handles very long text entries appropriately

**Given** the description field is empty
**When** user types a 500-character description
**Then** system saves the entire 500-character text to the character
**And** the description displays the full text in the field
**And** the field provides scrolling or wrapping to display all text

**Acceptance Criteria Covered**: AC4

---

### Scenario 8: Enter text with leading and trailing whitespace

**Purpose**: System handles whitespace appropriately

**Given** the character name field is empty
**When** user types "  Shadow Phoenix  " with leading and trailing spaces
**Then** system saves the text with whitespace preserved or trimmed based on business rules
**And** the character name displays consistently in the field

**Acceptance Criteria Covered**: AC1

---

### Scenario 9: Update existing text field value

**Purpose**: User can overwrite previously saved text

**Given** the character name field contains "Shadow Phoenix"
**When** user changes the character name to "Crimson Phoenix"
**Then** system saves "Crimson Phoenix" as the new character name
**And** the character name displays "Crimson Phoenix" in the field
**And** the previous value "Shadow Phoenix" is replaced
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC1

---

### Scenario 10: Enter empty text (clear existing value)

**Purpose**: System handles empty/blank text entry

**Given** the character name field contains "Shadow Phoenix"
**When** user deletes all text from the character name field
**Then** system saves empty value for character name
**And** the character name field displays as empty
**But** no other identity fields are affected

**Acceptance Criteria Covered**: AC1

**Note**: This scenario covers empty text entry. For explicit "clear field" action, see separate story: "User clears identity field"

---

### Scenario 11: Enter text with only whitespace

**Purpose**: System handles whitespace-only entries

**Given** the concept field is empty
**When** user types only spaces "     " into the concept field
**Then** system saves the whitespace or treats as empty based on business rules
**And** the concept field displays appropriately
**And** system may validate or warn if whitespace-only is invalid

**Acceptance Criteria Covered**: AC3

---

### Scenario 12: Enter text with line breaks and paragraphs

**Purpose**: System handles multi-line text in description field

**Given** the description field is empty
**When** user types multi-line text with paragraphs:
```
Marcus was a firefighter in Metro City.

During a rescue mission, he gained fire powers.

Now he fights crime as Shadow Phoenix.
```
**Then** system saves the multi-line text with line breaks preserved
**And** the description displays with proper formatting and line breaks
**And** all paragraphs are readable

**Acceptance Criteria Covered**: AC4

---

### Scenario 13: Enter text while other identity fields have values

**Purpose**: Entering text in one field does not affect other filled fields

**Given** the character name field contains "Shadow Phoenix"
**And** the real name field contains "Marcus Thompson"
**And** the concept field contains "Fire-wielding vigilante"
**When** user types "Wears a red and gold costume with phoenix emblem" into the description field
**Then** system saves the description text
**And** the character name still displays "Shadow Phoenix"
**And** the real name still displays "Marcus Thompson"
**And** the concept still displays "Fire-wielding vigilante"
**And** all previously entered values remain unchanged

**Acceptance Criteria Covered**: AC4, AC1, AC2, AC3

---

## Scenario Coverage Summary

### Happy Path Coverage
- ✅ Enter character name (Scenario 1)
- ✅ Enter real name (Scenario 2)
- ✅ Enter character concept (Scenario 3)
- ✅ Enter character description (Scenario 4)
- ✅ Enter player name (Scenario 5)

### Edge Cases Coverage
- ✅ Special characters and unicode (Scenario 6)
- ✅ Very long text (Scenario 7)
- ✅ Leading/trailing whitespace (Scenario 8)
- ✅ Update existing value (Scenario 9)
- ✅ Empty text entry (Scenario 10)
- ✅ Whitespace-only entry (Scenario 11)
- ✅ Multi-line text with line breaks (Scenario 12)
- ✅ Multiple fields with existing values (Scenario 13)

### Acceptance Criteria Coverage
- ✅ AC1: Enter character name - Scenarios 1, 6, 8, 9, 10, 13
- ✅ AC2: Enter real name - Scenarios 2, 13
- ✅ AC3: Enter character concept - Scenarios 3, 11, 13
- ✅ AC4: Enter character description - Scenarios 4, 7, 12, 13
- ✅ AC5: Enter player name - Scenario 5

**Total Scenarios**: 13 (5 happy path + 8 edge cases)

---

## Notes

### Business Rules to Clarify
- **Whitespace Handling**: Should leading/trailing whitespace be trimmed or preserved?
- **Whitespace-Only**: Should whitespace-only entries be treated as empty or invalid?
- **Maximum Length**: Are there character limits on text fields? (Tested 500 chars in Scenario 7)
- **Multi-line Support**: Which fields support line breaks? (Description likely supports, name fields may not)

### Related Stories
- **User clears identity field** - Handles explicit clear action (different from backspace/delete)
- **User enters identity numeric fields** - Different validation (numeric only)
- **User selects gender** - Different UI pattern (selection vs text input)

---

## Source Material

**Inherited From**: Story Map → Feature Document
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Identity fields

**Exploration Phase**:
- Scenarios generated: November 12, 2025
- Edge cases derived from standard text input patterns
- Multi-field independence verified (Scenario 13)

---

## Implementation Guidance

### Text Field Types
- **Single-line**: Name, Real Name, Player Name, Concept
- **Multi-line**: Description (supports paragraphs and line breaks)

### Validation Considerations
- Special characters and unicode should be supported for international names
- Very long text should have reasonable limits (suggest 500-1000 chars for description)
- Empty values should be allowed (fields are optional during character creation)
- Multi-line text should preserve formatting in description field

### UI Considerations
- Auto-save on blur or after brief delay
- Visual feedback when value is saved
- Scrolling or text wrapping for long descriptions
- Character count indicator for description field (optional)

