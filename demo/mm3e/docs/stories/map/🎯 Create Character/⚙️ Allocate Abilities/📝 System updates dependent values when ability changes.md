# 📝 System updates dependent values when ability changes

**Epic:** Create Character
**Feature:** Allocate Abilities

## Story Description

System updates dependent values when ability changes

## Acceptance Criteria

**AC are located in feature document**
See: ⚙️ Allocate Abilities - Feature Overview.md 

---

## Scenarios

### Background
**Given** a character exists with all abilities at rank 10 (modifier +0)
**And** defenses are at base values:
  - Dodge: 10 (base 10 + Agility 0)
  - Toughness: 10 (base 10 + Stamina 0)
  - Parry: 10 (base 10 + Fighting 0)
  - Fortitude: 10 (base 10 + Stamina 0)
  - Will: 10 (base 10 + Awareness 0)
**And** close attack bonus: +0 (Fighting modifier)
**And** close attack damage: +0 (Strength modifier)
**And** ranged attack bonus: +0 (Dexterity modifier)

### Scenario 1: Agility change updates Dodge defense
**Given** Agility is at rank 10 (modifier +0)
**And** Dodge defense is 10 (base 10 + Agility modifier 0)
**When** user increases Agility to rank 14 (modifier +2)
**Then** Dodge defense should recalculate to 12 (base 10 + Agility modifier +2)
**And** character sheet should display updated Dodge value "Dodge 12"
**But** other defenses should not change

### Scenario 2: Stamina change updates multiple defenses
**Given** Stamina is at rank 10 (modifier +0)
**And** Toughness defense is 10 (base 10 + Stamina modifier 0)
**And** Fortitude defense is 10 (base 10 + Stamina modifier 0)
**When** user increases Stamina to rank 16 (modifier +3)
**Then** Toughness defense should recalculate to 13 (base 10 + Stamina modifier +3)
**And** Fortitude defense should recalculate to 13 (base 10 + Stamina modifier +3)
**And** both updated defenses should display on character sheet
**But** other defenses (Dodge, Parry, Will) should not change

### Scenario 3: Fighting change updates Parry defense and close attack
**Given** Fighting is at rank 10 (modifier +0)
**And** Parry defense is 10
**And** close attack bonus is +0
**When** user increases Fighting to rank 18 (modifier +4)
**Then** Parry defense should recalculate to 14 (base 10 + Fighting modifier +4)
**And** close attack bonus should update to +4 (Fighting modifier)
**And** both Parry and close attack should display updated values
**But** Strength-based damage should not change

### Scenario 4: Strength change updates close attack damage
**Given** Strength is at rank 10 (modifier +0)
**And** close attack damage is +0
**When** user increases Strength to rank 14 (modifier +2)
**Then** close attack damage should update to +2 (Strength modifier)
**And** character sheet should display "Close Attack Damage: +2"
**But** close attack bonus (Fighting-based) should not change

### Scenario 5: Dexterity change updates ranged attack bonus
**Given** Dexterity is at rank 10 (modifier +0)
**And** ranged attack bonus is +0
**When** user increases Dexterity to rank 16 (modifier +3)
**Then** ranged attack bonus should update to +3 (Dexterity modifier)
**And** character sheet should display "Ranged Attack: +3"
**But** close attack values should not change

### Scenario 6: Awareness change updates Will defense
**Given** Awareness is at rank 10 (modifier +0)
**And** Will defense is 10
**When** user increases Awareness to rank 12 (modifier +1)
**Then** Will defense should recalculate to 11 (base 10 + Awareness modifier +1)
**And** character sheet should display updated Will value "Will 11"
**But** other defenses should not change

### Scenario 7: Skill modifiers update when linked ability changes
**Given** Intellect is at rank 10 (modifier +0)
**And** Investigation skill has 4 ranks (total modifier: +4 = Intellect 0 + ranks 4)
**And** Technology skill has 2 ranks (total modifier: +2 = Intellect 0 + ranks 2)
**When** user increases Intellect to rank 14 (modifier +2)
**Then** Investigation skill total should update to +6 (Intellect +2 + ranks 4)
**And** Technology skill total should update to +4 (Intellect +2 + ranks 2)
**And** all Intellect-linked skills should display updated totals
**But** skills linked to other abilities should not change

### Scenario 8: Defense with purchased ranks updates correctly
**Given** Agility is at rank 12 (modifier +1)
**And** Dodge defense has 3 purchased ranks
**And** Dodge defense is 14 (base 10 + Agility +1 + purchased ranks 3)
**When** user increases Agility to rank 16 (modifier +3)
**Then** Dodge defense should recalculate to 16 (base 10 + Agility +3 + purchased ranks 3)
**And** purchased ranks should be preserved in calculation
**And** display should show breakdown "Dodge 16 (10 base + 3 Agility + 3 ranks)"

### Scenario 9: Multiple cascading updates from single ability change
**Given** Stamina is at rank 10
**And** Toughness defense is 12 (base 10 + Stamina 0 + 2 purchased ranks)
**And** Fortitude defense is 10 (base 10 + Stamina 0)
**And** character has Stamina-linked skills (Concentration +3)
**When** user increases Stamina to rank 14 (modifier +2)
**Then** Toughness should update to 14 (base 10 + Stamina +2 + 2 purchased ranks)
**And** Fortitude should update to 12 (base 10 + Stamina +2)
**And** Concentration skill should update to +5 (Stamina +2 + skill ranks 3)
**And** all three updates should happen simultaneously
**And** character sheet should display all updated values

### Scenario 10: Decrease ability triggers cascading decreases
**Given** Fighting is at rank 16 (modifier +3)
**And** Parry defense is 15 (base 10 + Fighting +3 + 2 purchased ranks)
**And** close attack bonus is +3
**When** user decreases Fighting to rank 10 (modifier +0)
**Then** Parry defense should decrease to 12 (base 10 + Fighting 0 + 2 purchased ranks)
**And** close attack bonus should decrease to +0
**And** character sheet should display both decreased values

### Scenario Outline: Verify cascade for each ability-defense relationship
**Given** <ability> is at rank 10 (modifier +0)
**And** <defense> is at base value 10
**When** user increases <ability> to rank <new_rank> (modifier <new_modifier>)
**Then** <defense> should update to <expected_defense> (base 10 + modifier <new_modifier>)

**Examples**:
| ability   | defense    | new_rank | new_modifier | expected_defense |
|-----------|------------|----------|--------------|------------------|
| Agility   | Dodge      | 14       | +2           | 12               |
| Stamina   | Toughness  | 16       | +3           | 13               |
| Stamina   | Fortitude  | 16       | +3           | 13               |
| Fighting  | Parry      | 18       | +4           | 14               |
| Awareness | Will       | 12       | +1           | 11               |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

