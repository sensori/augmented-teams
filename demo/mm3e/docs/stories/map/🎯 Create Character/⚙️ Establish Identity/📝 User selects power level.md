# 📝 User selects power level

## Story Information
**Feature**: Establish Identity
**Epic**: Create Character
**Status**: Scenarios Added

---

## Story Description

User selects power level - and system calculates and displays total point budget

---

## Acceptance Criteria Reference
**Source**: Feature document - ⚙️ Establish Identity - Feature Overview.md

- AC1: When user selects power level, then system saves power level to character
- AC2: When user selects power level, then system calculates total point budget using formula (15 × PL)
- AC3: When system calculates point budget, then system displays total points available for character building
- AC4: When user changes power level, then system recalculates and updates point budget display

---

## Background

**Given** character creation screen is displayed
**And** Establish Identity section is displayed
**And** power level selector is available

---

## Scenarios

### Scenario 1: Select power level successfully

**Purpose**: User selects a power level and system calculates and displays point budget

**Given** no power level has been selected
**When** user selects power level 10 from the power level selector
**Then** system saves power level 10 to the character
**And** system calculates point budget as 150 points (15 × 10)
**And** system displays "150 points available" for character building
**And** point budget is visible to user

**Acceptance Criteria Covered**: AC1, AC2, AC3

---

### Scenario 2: Change power level to higher value

**Purpose**: User changes power level and system recalculates budget

**Given** character has power level 8 selected
**And** point budget shows 120 points (15 × 8)
**When** user changes power level to 12
**Then** system saves power level 12 to the character
**And** system recalculates point budget as 180 points (15 × 12)
**And** system updates point budget display to show "180 points available"
**And** budget display reflects the new value immediately

**Acceptance Criteria Covered**: AC1, AC4

---

### Scenario 3: Change power level to lower value

**Purpose**: User decreases power level and system recalculates budget

**Given** character has power level 10 selected
**And** point budget shows 150 points (15 × 10)
**When** user changes power level to 6
**Then** system saves power level 6 to the character
**And** system recalculates point budget as 90 points (15 × 6)
**And** system updates point budget display to show "90 points available"
**And** budget display reflects the new value immediately

**Acceptance Criteria Covered**: AC1, AC4

---

### Scenario 4: Select minimum power level

**Purpose**: System handles minimum power level correctly

**Given** no power level has been selected
**When** user selects power level 1 from the power level selector
**Then** system saves power level 1 to the character
**And** system calculates point budget as 15 points (15 × 1)
**And** system displays "15 points available"

**Acceptance Criteria Covered**: AC1, AC2, AC3

---

### Scenario 5: Select typical superhero power level

**Purpose**: System handles standard power level (PL 10 - typical superhero)

**Given** no power level has been selected
**When** user selects power level 10 from the power level selector
**Then** system saves power level 10 to the character
**And** system calculates point budget as 150 points (15 × 10)
**And** system displays "150 points available"
**And** user can proceed with character building

**Acceptance Criteria Covered**: AC1, AC2, AC3

---

### Scenario 6: Select high power level

**Purpose**: System handles high power levels correctly

**Given** no power level has been selected
**When** user selects power level 15 from the power level selector
**Then** system saves power level 15 to the character
**And** system calculates point budget as 225 points (15 × 15)
**And** system displays "225 points available"

**Acceptance Criteria Covered**: AC1, AC2, AC3

---

### Scenario Outline: Calculate point budget for various power levels

**Purpose**: Verify budget calculation formula (15 × PL) for multiple power levels

**Given** no power level has been selected
**When** user selects power level <PL>
**Then** system calculates point budget as <points> points
**And** system displays "<points> points available"

**Examples**:
| PL | points | description                  |
|----|--------|------------------------------|
| 1  | 15     | Minimum (street level hero)  |
| 5  | 75     | Low power                    |
| 8  | 120    | Standard game start          |
| 10 | 150    | Typical superhero            |
| 12 | 180    | Powerful hero                |
| 15 | 225    | High power                   |
| 20 | 300    | Maximum (cosmic level)       |

**Acceptance Criteria Covered**: AC1, AC2, AC3

---

## Scenario Coverage Summary

### Happy Path Coverage
- ✅ Select power level successfully (Scenario 1)
- ✅ Select typical superhero power level (Scenario 5)

### Edge Cases Coverage
- ✅ Change to higher power level (Scenario 2)
- ✅ Change to lower power level (Scenario 3)
- ✅ Minimum power level (Scenario 4)
- ✅ High power level (Scenario 6)
- ✅ Multiple power levels with formula verification (Scenario Outline)

### Acceptance Criteria Coverage
- ✅ AC1: Select power level - All scenarios
- ✅ AC2: Calculate point budget - Scenarios 1, 4, 5, 6, Scenario Outline
- ✅ AC3: Display point budget - Scenarios 1, 4, 5, 6, Scenario Outline
- ✅ AC4: Update budget display when changed - Scenarios 2, 3

**Total Scenarios**: 7 (6 individual scenarios + 1 scenario outline with 7 examples)

---

## Notes

### Business Rules Documented
- **Point Budget Formula**: 15 × Power Level
- **Power Level Range**: Typically 1-20 (from Hero's Handbook)
  - PL 1: Street level hero (15 points)
  - PL 8: Standard game start (120 points)
  - PL 10: Typical superhero (150 points)
  - PL 15: Powerful hero (225 points)
  - PL 20: Cosmic level (300 points)
- **Budget Recalculation**: Immediate when power level changes
- **Display Pattern**: "[points] points available"

### Related Stories
- **User enters identity text fields** - Basic character info entry
- **Allocate Abilities** - Uses point budget calculated here
- **Purchase Skills** - Uses point budget calculated here
- **Select Advantages** - Uses point budget calculated here

---

## Source Material

**Inherited From**: Story Map → Feature Document
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Power level selection and point budget formula
- Point Budget Formula: 15 × PL (documented on page 20)

**Exploration Phase**:
- Scenarios generated: November 12, 2025
- Formula verification scenarios added (Scenario Outline)
- Power level examples from Hero's Handbook Chapter 1

---

## Implementation Guidance

### Power Level Selection
- **UI Component**: Dropdown or slider with values 1-20
- **Default Value**: PL 10 (typical superhero) recommended as default
- **Display**: Show both power level number and point budget

### Budget Calculation
- **Formula**: points = 15 × power_level
- **Timing**: Calculate immediately when power level selected or changed
- **Display Update**: Real-time update without page refresh

### Budget Display
- **Format**: "[points] points available for character building"
- **Location**: Prominently displayed at top of character sheet
- **Update Pattern**: Immediate visual feedback when power level changes

