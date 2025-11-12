# 📝 User enters character name

## Story Information
**Feature**: Establish Identity
**Epic**: Create Character
**Status**: Scenarios Added

---

## Story Description

User enters character name - and system saves name to character

---

## Acceptance Criteria Reference
**Source**: Feature document - ⚙️ Establish Identity - Feature Overview.md

- AC1: When user enters character name, then system saves name to character

---

## Background

**Given** character creation screen is displayed
**And** the Establish Identity section is displayed
**And** the character name field is available

---

## Scenarios

### Scenario 1: Enter character name successfully (happy path)

**Purpose**: User enters character name and system saves it

**Given** the character name field is empty
**When** user types "Shadow Phoenix" into the character name field
**Then** system saves "Shadow Phoenix" as the character name
**And** the character name displays "Shadow Phoenix" in the field

**Acceptance Criteria Covered**: AC1

---

### Scenario 2: Update existing character name

**Purpose**: User changes previously entered character name

**Given** the character name field contains "Shadow Phoenix"
**When** user changes the character name to "Crimson Phoenix"
**Then** system saves "Crimson Phoenix" as the new character name
**And** the character name displays "Crimson Phoenix" in the field
**And** the previous value "Shadow Phoenix" is replaced

**Acceptance Criteria Covered**: AC1

---

### Scenario 3: Clear character name (empty entry)

**Purpose**: User removes character name by deleting all text

**Given** the character name field contains "Shadow Phoenix"
**When** user deletes all text from the character name field
**Then** system saves empty value for character name
**And** the character name field displays as empty

**Acceptance Criteria Covered**: AC1

---

### Scenario 4: Enter character name with special characters

**Purpose**: System accepts and saves names with special characters and punctuation

**Given** the character name field is empty
**When** user types "Dr. Quantum-7" into the character name field
**Then** system saves "Dr. Quantum-7" exactly as entered
**And** the character name displays "Dr. Quantum-7" with all special characters preserved
**And** punctuation and hyphen are displayed correctly

**Acceptance Criteria Covered**: AC1

---

### Scenario 5: Enter character name with unicode characters

**Purpose**: System accepts and saves names with international/unicode characters

**Given** the character name field is empty
**When** user types "Ñørdīç Thüñdër" into the character name field
**Then** system saves "Ñørdīç Thüñdër" exactly as entered
**And** the character name displays "Ñørdīç Thüñdër" with all unicode characters preserved
**And** all accents and special unicode symbols are displayed correctly

**Acceptance Criteria Covered**: AC1

---

### Scenario 6: Enter very long character name

**Purpose**: System handles long character names appropriately

**Given** the character name field is empty
**When** user types a 100-character name "The Incredibly Magnificent and Spectacularly Powerful Defender of Justice and Champion of the Weak Hero"
**Then** system saves the entire 100-character name to the character
**And** the character name displays the full text in the field
**And** the field provides appropriate display handling (scrolling, wrapping, or truncation with tooltip)

**Acceptance Criteria Covered**: AC1

---

### Scenario 7: Enter character name with leading and trailing whitespace

**Purpose**: System handles whitespace appropriately

**Given** the character name field is empty
**When** user types "  Shadow Phoenix  " with leading and trailing spaces
**Then** system saves the text with whitespace trimmed or preserved based on business rules
**And** the character name displays consistently in the field
**But** the functional character name is correctly stored

**Acceptance Criteria Covered**: AC1

---

### Scenario 8: Enter character name with only whitespace

**Purpose**: System handles whitespace-only entries

**Given** the character name field is empty
**When** user types only spaces "     " into the character name field
**Then** system saves the whitespace or treats as empty based on business rules
**And** the character name field displays appropriately
**And** system may validate or warn if whitespace-only is invalid

**Acceptance Criteria Covered**: AC1

---

### Scenario 9: Enter single character name

**Purpose**: System accepts minimum-length valid character names

**Given** the character name field is empty
**When** user types "X" as the character name
**Then** system saves "X" as the character name
**And** the character name displays "X" in the field

**Acceptance Criteria Covered**: AC1

---

### Scenario 10: Enter character name with numbers

**Purpose**: System accepts names containing numeric characters

**Given** the character name field is empty
**When** user types "Agent 47" into the character name field
**Then** system saves "Agent 47" as the character name
**And** the character name displays "Agent 47" with numbers preserved

**Acceptance Criteria Covered**: AC1

---

### Scenario 11: Enter character name with emoji

**Purpose**: System handles modern text input including emoji

**Given** the character name field is empty
**When** user types "Phoenix 🔥" with emoji into the character name field
**Then** system saves "Phoenix 🔥" with emoji or strips emoji based on business rules
**And** the character name displays appropriately in the field

**Acceptance Criteria Covered**: AC1

---

### Scenario 12: Multiple rapid updates to character name

**Purpose**: System handles quick successive changes correctly

**Given** the character name field is empty
**When** user types "Shadow"
**And** immediately changes it to "Shadow Phoenix"
**And** immediately changes it to "Phoenix"
**Then** system saves "Phoenix" as the final character name
**And** the character name displays "Phoenix" in the field
**And** all intermediate states are handled correctly without data loss

**Acceptance Criteria Covered**: AC1

---

## Scenario Coverage Summary

### Happy Path Coverage
- ✅ Enter character name successfully (Scenario 1)
- ✅ Update existing name (Scenario 2)
- ✅ Clear name (Scenario 3)

### Edge Cases Coverage
- ✅ Special characters and punctuation (Scenario 4)
- ✅ Unicode and international characters (Scenario 5)
- ✅ Very long names (Scenario 6)
- ✅ Leading/trailing whitespace (Scenario 7)
- ✅ Whitespace-only entry (Scenario 8)
- ✅ Minimum length (single character) (Scenario 9)
- ✅ Names with numbers (Scenario 10)
- ✅ Names with emoji (Scenario 11)
- ✅ Rapid successive updates (Scenario 12)

### Acceptance Criteria Coverage
- ✅ AC1: Enter character name - All 12 scenarios

**Total Scenarios**: 12 (3 happy path + 9 edge cases)

---

## Notes

### Business Rules to Clarify
- **Whitespace Handling**: Should leading/trailing whitespace be trimmed or preserved?
- **Whitespace-Only**: Should whitespace-only entries be treated as empty or invalid?
- **Maximum Length**: What is the character limit? (Tested 100 chars in Scenario 6)
- **Emoji Support**: Should emoji be allowed or stripped from character names?
- **Required Field**: Is character name required, or can it be left empty?

### Text Input Patterns
- **Alphanumeric**: Letters and numbers supported
- **Special Characters**: Punctuation, hyphens, periods supported
- **Unicode**: International characters and accents supported
- **Case Sensitivity**: Case is preserved as entered

### Related Stories
- **User enters identity text fields** - Consolidated story covering all text fields
- **User clears identity field** - Explicit clear action (different from backspace/delete)
- **User selects power level** - Next step after establishing identity

---

## Source Material

**Inherited From**: Story Map → Feature Document
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Character identity fields

**Exploration Phase**:
- Scenarios generated: November 12, 2025
- Edge cases derived from standard text input patterns
- Unicode and special character support for superhero naming conventions
- Rapid update handling for real-time user input

---

## Implementation Guidance

### Character Name Field
- **Field Type**: Single-line text input
- **Validation**: Should accept standard text, special characters, and unicode
- **Display**: Show full name with appropriate overflow handling
- **Save Timing**: Auto-save on blur or after brief typing delay
- **Default**: Empty/placeholder text like "Enter character name..."

### Special Considerations
- **Superhero Names**: Often include special characters (Dr., -, numbers, etc.)
- **International Support**: Unicode for players creating characters with international names
- **Visual Feedback**: Indicate when name is saved/syncing
- **Empty Names**: Decide if character can be created without name (recommend: allow empty during creation)

