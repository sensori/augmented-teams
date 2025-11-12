# ⚙️ Allocate Abilities - Feature Overview

**File Name**: `⚙️ Allocate Abilities - Feature Overview.md`

**Epic:** Create Character

## Feature Purpose

Enable users to allocate ability ranks for their character's 8 core abilities, with system automatically calculating costs, modifiers, and cascading updates to dependent values (defenses, attacks).

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Ability:** Fundamental attribute of character (8 core abilities: Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- **Range**: Typically 0-20 ranks (10 is average human, can go negative)
- **Cost**: 2 points per rank
- **Modifier**: (Rank - 10) ÷ 2 rounded down
- **Affects**: Defenses (Dodge, Toughness, Parry, Fortitude, Will), Attacks

**Defense:** Resistance to attacks
- **Types**: Dodge (Agility), Toughness (Stamina), Parry (Fighting), Fortitude (Stamina), Will (Awareness)
- **Formula**: Base 10 + Ability modifier
- **Cascades**: Updates when linked Ability changes

**Attack:** Offensive capability
- **Close Attack Bonus**: Uses Fighting ability modifier
- **Close Attack Damage**: Uses Strength ability modifier
- **Ranged Attack Bonus**: Uses Dexterity ability modifier
- **Cascades**: Updates when linked Ability changes

---

### Domain Behaviors

**Increase Ability Rank:** Add ranks to ability
- **Cost**: 2 points per rank
- **Updates**: Ability value, point budget, ability modifier
- **Cascades**: Triggers defense and attack updates if ability affects them

**Decrease Ability Rank:** Remove ranks from ability
- **Refund**: 2 points per rank
- **Updates**: Ability value, point budget, ability modifier
- **Cascades**: Triggers defense and attack updates if ability affects them

**Calculate Ability Modifier:** Derive modifier from rank
- **Formula**: (Rank - 10) ÷ 2 rounded down
- **Display**: Shows +/- modifier next to rank
- **Automatic**: Recalculates whenever rank changes

**Update Defenses:** Recalculate defenses when ability changes
- **Affected Defenses**: Dodge (Agility), Toughness/Fortitude (Stamina), Parry (Fighting), Will (Awareness)
- **Cascades**: Multiple defenses update if affected

**Update Attacks:** Recalculate attack bonuses when ability changes
- **Affected Attacks**: Close bonus (Fighting), Close damage (Strength), Ranged bonus (Dexterity)

---

### Domain Rules

**Ability Cost:**
- Formula: 2 points per rank
- Rank 10 costs 0 points (starting baseline)
- Above 10: 2 points per rank increase
- Below 10: 2 points refunded per rank decrease

**Ability Modifier:**
- Formula: (Rank - 10) ÷ 2 rounded down
- Examples:
  - Rank 10 = 0 modifier
  - Rank 12 = +1 modifier
  - Rank 8 = -1 modifier

**Cascade Relationships:**
- Agility → Dodge defense
- Stamina → Toughness and Fortitude defenses
- Fighting → Parry defense and close attack bonus
- Strength → Close attack damage
- Dexterity → Ranged attack bonus
- Awareness → Will defense

---

## Stories (10 total)

### 1. **User increases ability rank from current value** - 📝 Add ranks to ability

**Story Description**: User increases ability rank from current value - and system calculates incremental cost (2 points/rank) and updates budget

#### Acceptance Criteria

##### Increase Rank
- **When** user increases ability rank, **then** system increases ability rank by 1

##### Calculate Cost
- **When** system increases ability rank, **then** system calculates incremental cost (2 points per rank)

##### Deduct Points
- **When** system calculates ability cost, **then** system deducts points from available budget

##### Update Display
- **When** system updates ability rank and budget, **then** system displays new rank and remaining budget

##### Calculate Modifier
- **When** ability rank changes, **then** system calculates new ability modifier using formula (Rank - 10) ÷ 2 rounded down

---

### 2. **User decreases ability rank from current value** - 📝 Remove ranks from ability

**Story Description**: User decreases ability rank from current value - and system refunds points (2 points/rank) and updates budget

#### Acceptance Criteria

##### Decrease Rank
- **When** user decreases ability rank, **then** system decreases ability rank by 1

##### Refund Points
- **When** system decreases ability rank, **then** system refunds 2 points per rank to available budget

##### Update Display
- **When** system updates ability rank and budget, **then** system displays new rank and remaining budget

##### Calculate Modifier
- **When** ability rank changes, **then** system recalculates ability modifier using formula (Rank - 10) ÷ 2 rounded down

---

### 3. **User sets ability to negative rank** - 📝 Set ability below average

**Story Description**: User sets ability to negative rank - and system refunds points and applies negative modifier

#### Acceptance Criteria

##### Allow Negative Ranks
- **When** user sets ability rank below 0, **then** system accepts negative rank value

##### Refund Points for Below 10
- **When** ability rank is below 10, **then** system refunds points (2 points per rank below 10)

##### Calculate Negative Modifier
- **When** ability rank is below 10, **then** system calculates negative modifier using formula (Rank - 10) ÷ 2 rounded down

##### Display Negative Values
- **When** ability has negative rank or modifier, **then** system displays negative values clearly (e.g., "-2")

---

### 4. **System displays ability modifier** - 📝 Show derived modifier

**Story Description**: System displays ability modifier - Calculates (rank - 10) ÷ 2 rounded down

#### Acceptance Criteria

##### Calculate Modifier
- **When** ability rank is set or changed, **then** system calculates modifier using formula (Rank - 10) ÷ 2 rounded down

##### Display Modifier
- **When** system calculates modifier, **then** system displays modifier next to ability rank (e.g., "Strength 14 (+2)")

##### Update Modifier Display
- **When** ability rank changes, **then** system updates modifier display immediately

---

### 5. **System updates dodge defense when agility changes** - 📝 Cascade to dodge

**Story Description**: System updates dodge defense when agility changes

#### Acceptance Criteria

##### Update Dodge
- **When** Agility rank changes, **then** system recalculates Dodge defense (Base 10 + Agility modifier)

##### Display Updated Defense
- **When** Dodge defense recalculates, **then** system displays updated value on character sheet

---

### 6. **System updates toughness and fortitude when stamina changes** - 📝 Cascade to stamina defenses

**Story Description**: System updates toughness and fortitude defenses when stamina changes

#### Acceptance Criteria

##### Update Toughness
- **When** Stamina rank changes, **then** system recalculates Toughness defense (Base 10 + Stamina modifier)

##### Update Fortitude
- **When** Stamina rank changes, **then** system recalculates Fortitude defense (Base 10 + Stamina modifier)

##### Display Updated Defenses
- **When** defenses recalculate, **then** system displays both updated values on character sheet

---

### 7. **System updates parry defense and close attack when fighting changes** - 📝 Cascade to fighting

**Story Description**: System updates parry defense and close attack bonus when fighting changes

#### Acceptance Criteria

##### Update Parry
- **When** Fighting rank changes, **then** system recalculates Parry defense (Base 10 + Fighting modifier)

##### Update Close Attack Bonus
- **When** Fighting rank changes, **then** system recalculates close attack bonus (Fighting modifier)

##### Display Updated Values
- **When** values recalculate, **then** system displays updated Parry and close attack on character sheet

---

### 8. **System updates close attack damage when strength changes** - 📝 Cascade to damage

**Story Description**: System updates close attack damage bonus when strength changes

#### Acceptance Criteria

##### Update Damage Bonus
- **When** Strength rank changes, **then** system recalculates close attack damage bonus (Strength modifier)

##### Display Updated Damage
- **When** damage recalculates, **then** system displays updated damage value on character sheet

---

### 9. **System updates ranged attack when dexterity changes** - 📝 Cascade to ranged

**Story Description**: System updates ranged attack bonus when dexterity changes

#### Acceptance Criteria

##### Update Ranged Attack
- **When** Dexterity rank changes, **then** system recalculates ranged attack bonus (Dexterity modifier)

##### Display Updated Attack
- **When** attack recalculates, **then** system displays updated ranged attack on character sheet

---

### 10. **System updates will defense when awareness changes** - 📝 Cascade to will

**Story Description**: System updates will defense when awareness changes

#### Acceptance Criteria

##### Update Will
- **When** Awareness rank changes, **then** system recalculates Will defense (Base 10 + Awareness modifier)

##### Display Updated Defense
- **When** Will defense recalculates, **then** system displays updated value on character sheet

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Point validation by category (abilities, advantages) - Same formula: spent ≤ budget
- ✅ Unspent calculation by category - Same formula: budget - spent = unspent

**Separated (Different Logic):**
- ❌ Each cascade type (Stories 5-10) - Different affected defenses/attacks per ability
- ❌ Increase vs Decrease (Stories 1-2) - Opposite operations kept separate for clarity
- ❌ Negative ranks (Story 3) - Special handling for below 10
- ❌ Modifier display (Story 4) - Pure calculation/display, no budget changes

**Result**: 10 stories with clear separation between direct manipulation and cascading updates by type

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 2: Abilities (pages 29-33) - Ability costs, modifiers, negative ranks
- Ability Modifier Formula: (Rank - 10) ÷ 2 rounded down
- Ability Cost: 2 points per rank
- Defense calculations: Base 10 + Ability modifier

**Discovery Refinements Applied:**
- Separated cascades by affected system type (6 cascade stories)
- Consolidated budget validations (same formula)
- Documented which abilities affect which defenses/attacks

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 2: Abilities (pages 29-33) - Complete ability system
- Discovery Refinements:
  - Cascade patterns documented (abilities → defenses/attacks)
  - Negative rank handling
  - Modifier calculation formula

