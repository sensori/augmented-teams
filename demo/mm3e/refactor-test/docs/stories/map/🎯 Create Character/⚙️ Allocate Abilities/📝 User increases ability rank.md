# 📝 User increases ability rank

**Epic:** Create Character
**Feature:** Allocate Abilities

## Story Description

User increases ability rank

## Acceptance Criteria

**AC are located in feature document**
See: ⚙️ Allocate Abilities - Feature Overview.md

---

## Scenarios

### Background
**Given** a character exists with Strength at rank 10
**And** the character has 30 available points in budget
**And** ability cost is 2 points per rank

### Scenario 1: User increases ability rank by one
**Given** Strength is at rank 10
**When** user increases Strength rank by 1
**Then** Strength rank should be 11
**And** ability modifier should be +0 (calculated as (11-10)÷2 = 0.5 rounded down)
**And** 2 points should be deducted from available budget
**And** available points should be 28

### Scenario 2: User increases ability to rank that changes modifier
**Given** Strength is at rank 11
**When** user increases Strength rank by 1
**Then** Strength rank should be 12
**And** ability modifier should be +1 (calculated as (12-10)÷2 = 1)
**And** 2 points should be deducted from budget

### Scenario 3: Attempt increase with insufficient budget (error case)
**Given** Strength is at rank 10
**And** character has 1 available point
**When** user attempts to increase Strength rank by 1
**Then** system should prevent the increase
**And** system should display error "Insufficient points: need 2, have 1"
**And** Strength rank should remain at 10

### Scenario Outline: Ability modifier calculation for various ranks
**Given** Strength is at rank <initial_rank>
**When** user increases Strength to rank <new_rank>
**Then** Strength modifier becomes <expected_modifier>

**Examples:**
| initial_rank | new_rank | expected_modifier | calculation |
|--------------|----------|-------------------|-------------|
| 10           | 11       | +0                | (11-10)÷2=0.5→0 |
| 10           | 12       | +1                | (12-10)÷2=1 |
| 10           | 14       | +2                | (14-10)÷2=2 |
| 12           | 16       | +3                | (16-10)÷2=3 |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

