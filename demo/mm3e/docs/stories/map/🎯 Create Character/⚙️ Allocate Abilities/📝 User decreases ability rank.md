# 📝 User decreases ability rank


**Epic:** Create Character
**Feature:** Allocate Abilities

## Story Description

User decreases ability rank

## Acceptance Criteria

**AC are located in feature document**
See: ⚙️ Allocate Abilities - Feature Overview.md 

---

## Scenarios

### Background
**Given** a character exists with Strength at rank 14 (modifier +2)
**And** the character has 20 available ability points
**And** ability refund is 2 points per rank decreased

### Scenario 1: Decrease ability rank by one
**Given** Strength is at rank 14
**When** user decreases Strength rank by 1
**Then** Strength rank should be 13
**And** ability modifier should be +1 (calculated as (13-10)÷2 = 1.5 rounded down)
**And** 2 points should be refunded to available budget
**And** available points should be 22
**And** new rank and modifier should be displayed as "Strength 13 (+1)"

### Scenario 2: Decrease ability multiple ranks
**Given** Strength is at rank 14
**When** user decreases Strength rank by 1 four times
**Then** Strength rank should be 10
**And** ability modifier should be +0 (calculated as (10-10)÷2 = 0)
**And** 8 points should be refunded to available budget (4 ranks × 2 points)
**And** available points should be 28

### Scenario 3: Decrease to below average human (boundary condition)
**Given** Strength is at rank 10
**And** character has 20 available points
**When** user decreases Strength rank by 1 twice
**Then** Strength rank should be 8
**And** ability modifier should be -1 (calculated as (8-10)÷2 = -1)
**And** 4 points should be refunded (2 ranks below 10 × 2 points)
**And** available points should be 24
**And** display should show "Strength 8 (-1)" with negative modifier

### Scenario 4: Decrease to negative rank (edge case)
**Given** Strength is at rank 4
**When** user decreases Strength rank by 1 five times
**Then** Strength rank should be -1
**And** ability modifier should be -6 (calculated as (-1-10)÷2 = -5.5 rounded down to -6)
**And** 10 points should be refunded (5 ranks × 2 points)
**And** display should clearly show negative values "Strength -1 (-6)"

### Scenario 5: Decrease to minimum (cannot decrease below minimum)
**Given** Strength is at rank -10 (system minimum)
**When** user attempts to decrease Strength rank by 1
**Then** system should prevent the decrease
**And** system should display message "Cannot decrease below minimum rank"
**And** Strength rank should remain at -10

### Scenario 6: Cascading defense update triggered
**Given** Fighting is at rank 16 (+3 modifier)
**And** Parry defense is 15 (10 base + 3 Fighting modifier + 2 purchased ranks)
**When** user decreases Fighting rank to 12 (+1 modifier)
**Then** Fighting modifier should update to +1
**And** Parry defense should recalculate to 13 (10 base + 1 Fighting modifier + 2 purchased ranks)
**And** character sheet should display updated Parry value immediately

### Scenario Outline: Ability modifier calculation when decreasing ranks
**Given** an ability is at rank <initial_rank>
**When** user decreases ability to rank <new_rank>
**Then** ability modifier should be <expected_modifier>
**And** system should display "<ability_name> <new_rank> (<expected_modifier>)"

**Examples**:
| initial_rank | new_rank | expected_modifier | calculation |
|--------------|----------|-------------------|-------------|
| 14           | 13       | +1                | (13-10)÷2=1.5→1 |
| 14           | 12       | +1                | (12-10)÷2=1 |
| 14           | 10       | +0                | (10-10)÷2=0 |
| 10           | 8        | -1                | (8-10)÷2=-1 |
| 10           | 6        | -2                | (6-10)÷2=-2 |
| 10           | 4        | -3                | (4-10)÷2=-3 |
| 8            | 0        | -5                | (0-10)÷2=-5 |
| 4            | -2       | -6                | (-2-10)÷2=-6 |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

