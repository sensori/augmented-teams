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
**Given** a character exists with Strength at rank 10 (0 modifier)
**And** the character has 30 available ability points
**And** ability cost is 2 points per rank

### Scenario 1: Increase ability rank by one
**Given** Strength is at rank 10
**When** user increases Strength rank by 1
**Then** Strength rank should be 11
**And** ability modifier should be +0 (calculated as (11-10)÷2 = 0.5 rounded down)
**And** 2 points should be deducted from available budget
**And** available points should be 28
**And** new rank and modifier should be displayed as "Strength 11 (+0)"

### Scenario 2: Increase ability multiple ranks
**Given** Strength is at rank 10
**When** user increases Strength rank by 1 four times
**Then** Strength rank should be 14
**And** ability modifier should be +2 (calculated as (14-10)÷2 = 2)
**And** 8 points should be deducted from available budget (4 ranks × 2 points)
**And** available points should be 22

### Scenario 3: Increase beyond typical maximum (boundary condition)
**Given** Strength is at rank 18
**And** character has 10 available points
**When** user increases Strength rank by 1 twice
**Then** Strength rank should be 20
**And** ability modifier should be +5 (calculated as (20-10)÷2 = 5)
**And** 4 points should be deducted
**And** available points should be 6

### Scenario 4: Attempt increase with insufficient points (error case)
**Given** Strength is at rank 10
**And** character has 1 available point
**When** user attempts to increase Strength rank by 1
**Then** system should prevent the increase
**And** system should display error message "Insufficient points. Need 2 points, have 1 point."
**And** Strength rank should remain at 10
**And** available points should remain at 1

### Scenario 5: Cascading defense update triggered
**Given** Strength is at rank 10
**And** close attack damage is +0 (Strength modifier)
**When** user increases Strength rank to 14
**Then** Strength modifier should update to +2
**And** close attack damage should update to +2
**And** character sheet should display updated attack damage immediately

### Scenario Outline: Ability modifier calculation for various ranks
**Given** an ability is at rank <initial_rank>
**When** user increases ability to rank <new_rank>
**Then** ability modifier should be <expected_modifier>
**And** system should display "<ability_name> <new_rank> (<expected_modifier>)"

**Examples**:
| initial_rank | new_rank | expected_modifier | calculation |
|--------------|----------|-------------------|-------------|
| 10           | 11       | +0                | (11-10)÷2=0.5→0 |
| 10           | 12       | +1                | (12-10)÷2=1 |
| 10           | 14       | +2                | (14-10)÷2=2 |
| 10           | 16       | +3                | (16-10)÷2=3 |
| 10           | 18       | +4                | (18-10)÷2=4 |
| 10           | 20       | +5                | (20-10)÷2=5 |
| 12           | 15       | +2                | (15-10)÷2=2.5→2 |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

