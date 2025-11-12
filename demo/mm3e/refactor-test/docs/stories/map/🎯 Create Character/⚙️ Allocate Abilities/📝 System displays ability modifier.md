# 📝 System displays ability modifier

**Epic:** Create Character
**Feature:** Allocate Abilities

## Story Description

System displays ability modifier

## Acceptance Criteria

**AC are located in feature document**
See: ⚙️ Allocate Abilities - Feature Overview.md

---

## Scenarios

### Background
**Given** a character exists with abilities at rank 10

### Scenario 1: Calculate and display positive modifier
**Given** Strength is at rank 14
**When** system calculates modifier
**Then** modifier should be +2 (calculated as (14-10)÷2 = 2)
**And** system should display "Strength 14 (+2)"

### Scenario 2: Calculate and display zero modifier
**Given** Strength is at rank 10
**When** system calculates modifier
**Then** modifier should be +0 (calculated as (10-10)÷2 = 0)
**And** system should display "Strength 10 (+0)"

### Scenario 3: Calculate and display negative modifier
**Given** Strength is at rank 6
**When** system calculates modifier
**Then** modifier should be -2 (calculated as (6-10)÷2 = -2)
**And** system should display "Strength 6 (-2)"

### Scenario 4: Modifier updates immediately when rank changes
**Given** Strength is at rank 12 with modifier +1
**When** user increases Strength to rank 14
**Then** modifier should update to +2
**And** display should update to "Strength 14 (+2)" immediately

### Scenario Outline: Modifier calculation formula verification
**Given** an ability is at rank <rank>
**When** system calculates modifier
**Then** modifier should be <expected_modifier>

**Examples:**
| rank | expected_modifier | calculation |
|------|-------------------|-------------|
| 8    | -1                | (8-10)÷2=-1 |
| 10   | +0                | (10-10)÷2=0 |
| 13   | +1                | (13-10)÷2=1.5→1 |
| 16   | +3                | (16-10)÷2=3 |
| 20   | +5                | (20-10)÷2=5 |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

