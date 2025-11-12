# ⚙️ Allocate Abilities - Feature Overview

**File Name**: `⚙️ Allocate Abilities - Feature Overview.md`

**Epic:** Create Character

## Feature Purpose

Enable users to allocate ability ranks for their character's 8 core abilities, with system automatically calculating costs, modifiers, and cascading updates to dependent values (defenses, skills, attacks).

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Ability:** Fundamental attribute of character (8 core abilities: Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- **Range**: Typically 0-20 ranks (10 is average human, can go negative)
- **Cost**: 2 points per rank
- **Modifier**: (Rank - 10) ÷ 2 rounded down
- **Starting Value**: 10 (average human) or 0 (depending on build approach)
- **Affects**: Skills (linked ability modifier), Defenses (various), Attack bonuses

**Character:** Player-created hero
- **Has**: 8 Abilities (Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- **Point Budget**: 15 × Power Level
- **Ability Point Tracking**: Tracks points spent on abilities separately

**Defense:** Resistance to attacks
- **Types**: Dodge (Agility), Toughness (Stamina), Parry (Fighting), Fortitude (Stamina), Will (Awareness)
- **Formula**: Base 10 + Ability modifier + purchased ranks
- **Cascades**: Updates when linked Ability changes

**Skill:** Trained capability
- **Based on**: Linked Ability (each skill links to one ability)
- **Total Modifier**: Ability modifier + Skill ranks
- **Cascades**: Recalculates when linked Ability changes

**Attack:** Offensive capability
- **Close Attack**: Uses Fighting ability for attack bonus, Strength for damage
- **Ranged Attack**: Uses Dexterity ability for attack bonus
- **Cascades**: Updates when linked Ability changes

---

### Domain Behaviors

**Increase Ability Rank:** Add ranks to ability
- **Cost**: 2 points per rank (incremental)
- **Updates**: Ability value, point budget, ability modifier
- **Cascades**: Triggers defense, skill, and attack updates if ability affects them

**Decrease Ability Rank:** Remove ranks from ability
- **Refund**: 2 points per rank
- **Updates**: Ability value, point budget, ability modifier
- **Cascades**: Triggers defense, skill, and attack updates if ability affects them

**Set Negative Rank:** Set ability below 0
- **Refund**: Refunds points for ranks below 10
- **Modifier**: Negative modifier applied
- **Use Case**: Character weaknesses or trade-offs

**Calculate Ability Modifier:** Derive modifier from rank
- **Formula**: (Rank - 10) ÷ 2 rounded down
- **Display**: Shows +/- modifier next to rank
- **Automatic**: Recalculates whenever rank changes

**Update Defenses:** Recalculate defenses when ability changes
- **Triggered by**: Ability rank change
- **Affected Defenses**: 
  - Dodge (Agility)
  - Toughness (Stamina)
  - Parry (Fighting)
  - Fortitude (Stamina)
  - Will (Awareness)
- **Cascades**: Multiple defenses update if multiple abilities affect them

**Update Skills:** Recalculate skill modifiers when ability changes
- **Triggered by**: Ability rank change affecting skills
- **Recalculates**: Total modifier for all skills linked to changed ability
- **Formula**: Ability modifier + Skill ranks

**Update Attacks:** Recalculate attack bonuses when ability changes
- **Triggered by**: Ability rank change affecting attacks
- **Affected Attacks**:
  - Close attack bonus (Fighting)
  - Close attack damage (Strength)
  - Ranged attack bonus (Dexterity)

---

### Domain Rules

**Ability Cost:**
- Formula: 2 points per rank
- Starting at rank 10 costs 0 points
- Rank 11 costs 2 points (1 rank above 10)
- Rank 15 costs 10 points (5 ranks above 10)

**Ability Modifier:**
- Formula: (Rank - 10) ÷ 2 rounded down
- Examples:
  - Rank 10 = 0 modifier
  - Rank 12 = +1 modifier
  - Rank 14 = +2 modifier
  - Rank 8 = -1 modifier
  - Rank 6 = -2 modifier

**Cascade Relationships:**
- Agility changes → Updates Dodge defense
- Stamina changes → Updates Toughness and Fortitude defenses
- Fighting changes → Updates Parry defense and close attack bonus
- Strength changes → Updates close attack damage
- Dexterity changes → Updates ranged attack bonus
- Awareness changes → Updates Will defense
- Any ability changes → Updates skills linked to that ability

---

## Stories (7 total)

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

### 5. **System updates defense values when ability affecting defense changes** - 📝 Cascade to defenses

**Story Description**: System updates defense values when ability affecting defense changes - Updates dodge (Agility), toughness (Stamina), parry (Fighting), fortitude (Stamina), will (Awareness)

#### Acceptance Criteria

##### Update Dodge
- **When** Agility rank changes, **then** system recalculates Dodge defense (Base 10 + Agility modifier + purchased Dodge ranks)

##### Update Toughness
- **When** Stamina rank changes, **then** system recalculates Toughness defense (Base 10 + Stamina modifier + purchased Toughness ranks)

##### Update Parry
- **When** Fighting rank changes, **then** system recalculates Parry defense (Base 10 + Fighting modifier + purchased Parry ranks)

##### Update Fortitude
- **When** Stamina rank changes, **then** system recalculates Fortitude defense (Base 10 + Stamina modifier)

##### Update Will
- **When** Awareness rank changes, **then** system recalculates Will defense (Base 10 + Awareness modifier)

##### Display Updated Defenses
- **When** defense values recalculate, **then** system displays updated defense values on character sheet

---

### 6. **System updates skill modifiers when ability affecting skills changes** - 📝 Cascade to skills

**Story Description**: System updates skill modifiers when ability affecting skills changes - Recalculates totals for skills linked to changed ability

#### Acceptance Criteria

##### Identify Linked Skills
- **When** ability rank changes, **then** system identifies all skills linked to that ability

##### Recalculate Skill Modifiers
- **When** system identifies linked skills, **then** system recalculates total modifier for each skill (new Ability modifier + Skill ranks)

##### Display Updated Skills
- **When** skill modifiers recalculate, **then** system displays updated skill totals on character sheet

---

### 7. **System updates attack bonuses when ability affecting attacks changes** - 📝 Cascade to attacks

**Story Description**: System updates attack bonuses when ability affecting attacks changes - Updates close attack (Fighting, Strength damage), ranged attack (Dexterity)

#### Acceptance Criteria

##### Update Close Attack Bonus
- **When** Fighting rank changes, **then** system recalculates close attack bonus (Fighting modifier)

##### Update Close Attack Damage
- **When** Strength rank changes, **then** system recalculates close attack damage bonus (Strength modifier)

##### Update Ranged Attack Bonus
- **When** Dexterity rank changes, **then** system recalculates ranged attack bonus (Dexterity modifier)

##### Display Updated Attacks
- **When** attack bonuses recalculate, **then** system displays updated attack values on character sheet

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Increase/Decrease operations (Stories 1, 2) - Same logic, opposite direction
- ✅ Cascade updates grouped by TYPE (Stories 5, 6, 7) - Defenses, Skills, Attacks separate

**Separated (Different Logic):**
- ❌ Negative ranks (Story 3) - Special handling for below 0, different from normal increase/decrease
- ❌ Modifier display (Story 4) - Pure calculation/display, no cost changes
- ❌ Each cascade type (Stories 5, 6, 7) - Different formulas and affected systems

**Result**: 7 stories with clear separation between direct manipulation and cascading updates

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 2: Abilities (pages 29-33) - Ability costs, modifiers, negative ranks
- Chapter 7: Combat (pages 168-187) - Attack calculations
- Ability Modifier Formula: (Rank - 10) ÷ 2 rounded down
- Ability Cost: 2 points per rank
- Defense calculations: Base 10 + Ability modifier + purchased ranks

**Discovery Refinements Applied:**
- Consolidated increase/decrease (same logic, opposite operations)
- Separated negative ranks (special handling)
- Grouped cascades by affected system type (defenses, skills, attacks)
- Documented which abilities affect which defenses/skills/attacks

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 2: Abilities (pages 29-33) - Complete ability system
- Discovery Refinements:
  - Cascade patterns documented (abilities → defenses/skills/attacks)
  - Negative rank handling
  - Modifier calculation formula

