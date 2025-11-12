# ⚙️ Establish Identity - Feature Overview

**File Name**: `⚙️ Establish Identity - Feature Overview.md`

**Epic:** Create Character

## Feature Purpose

Enable users to establish basic character identity by entering identifying information (name, concept, demographics) and selecting power level which determines the character's point budget for building.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero in Mutants & Masterminds 3rd Edition game system
- **Identity Fields**: Name, real name, concept, description, player name (text)
- **Demographics**: Age, height, weight (numeric), gender (selection)
- **Power Level**: Determines character's power scale and point budget
- **Point Budget**: 15 × Power Level (total points available)

**Power Level:** Scale of character's superhuman capabilities
- **Range**: Typically 1-20 (10 is standard superhero)
- **Determines**: Total point budget (15 × PL)
- **Example**: Power Level 10 = 150 total points

**Point Budget:** Total points available for character building
- **Formula**: 15 × Power Level
- **Categories**: Abilities, Skills, Advantages, Powers, Defenses
- **Display**: Shows total available when power level selected

---

### Domain Behaviors

**Enter Identity:** Capture character identifying information
- **Text Fields**: Name, real name, concept, description, player name
- **Numeric Fields**: Age, height, weight
- **Selection**: Gender
- **Saves**: All fields save immediately to character

**Select Power Level:** Choose character's power scale
- **Action**: User selects from power level options
- **Calculation**: System calculates point budget (15 × PL)
- **Display**: Shows total points available

**Clear Field:** Remove value from identity field
- **Action**: User clears any identity field
- **Result**: Value removed, display updated

---

### Domain Rules

**Power Level Point Budget:**
- Formula: 15 × Power Level
- Examples:
  - PL 8 = 120 points
  - PL 10 = 150 points
  - PL 12 = 180 points

**Identity Field Types:**
- Text fields: Name, real name, concept, description, player name
- Numeric fields: Age, height, weight (positive numbers)
- Selection field: Gender (predefined options)

---

## Stories (5 total)

### 1. **User enters identity text fields** - 📝 Capture character identifying text

**Story Description**: User enters identity text fields - and system saves name, real name, concept, description, and player name

#### Acceptance Criteria

##### Enter Name
- **When** user enters character name, **then** system saves name to character

##### Enter Real Name
- **When** user enters real name, **then** system saves real name to character

##### Enter Concept
- **When** user enters character concept, **then** system saves concept to character

##### Enter Description
- **When** user enters character description, **then** system saves description to character

##### Enter Player Name
- **When** user enters player name, **then** system saves player name to character

---

### 2. **User enters identity numeric fields** - 📝 Capture character demographics

**Story Description**: User enters identity numeric fields - and system saves age, height, and weight

#### Acceptance Criteria

##### Enter Age
- **When** user enters age, **then** system saves age to character

##### Enter Height
- **When** user enters height, **then** system saves height to character

##### Enter Weight
- **When** user enters weight, **then** system saves weight to character

##### Numeric Validation
- **When** user enters non-numeric value in numeric field, **then** system prevents entry and displays validation message

---

### 3. **User selects gender** - 📝 Choose character gender

**Story Description**: User selects gender - and system saves selection

#### Acceptance Criteria

##### Select Gender
- **When** user selects gender from options, **then** system saves gender selection to character

##### Display Gender Options
- **When** user opens gender selector, **then** system displays available gender options

---

### 4. **User selects power level** - 📝 Set character power scale

**Story Description**: User selects power level - and system calculates and displays total point budget

#### Acceptance Criteria

##### Select Power Level
- **When** user selects power level, **then** system saves power level to character

##### Calculate Point Budget
- **When** user selects power level, **then** system calculates total point budget using formula (15 × PL)

##### Display Point Budget
- **When** system calculates point budget, **then** system displays total points available for character building

##### Update Budget Display
- **When** user changes power level, **then** system recalculates and updates point budget display

---

### 5. **User clears identity field** - 📝 Remove identity value

**Story Description**: User clears identity field - and system removes value and updates display

#### Acceptance Criteria

##### Clear Text Field
- **When** user clears text identity field, **then** system removes value from character and updates display to show empty field

##### Clear Numeric Field
- **When** user clears numeric identity field, **then** system removes value from character and updates display to show empty field

##### Clear Selection Field
- **When** user clears selection field (gender), **then** system removes selection from character and updates display to show no selection

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Text fields (Stories 1) - Same text input logic for name, real name, concept, description, player name
- ✅ Numeric fields (Story 2) - Same numeric input logic for age, height, weight
- ✅ Clear operations (Story 5) - Same clear logic for all field types

**Separated (Different Logic):**
- ❌ Text vs Numeric fields - Different validation (text allows any, numeric requires numbers)
- ❌ Selection field (gender) - Different UI (dropdown vs text input)
- ❌ Power level - Separate story because triggers calculation (point budget)

**Result**: 5 stories with clear field type separation

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 1: Character Creation (pages 16-28) - Identity fields, power level selection
- Point Budget Formula: 15 × PL
- Power Level ranges: 1-20 (10 is standard)

**Discovery Refinements Applied:**
- Consolidated text fields (5 fields → 1 story, same logic)
- Consolidated numeric fields (3 fields → 1 story, same logic)
- Separated power level (triggers calculation, different from simple text entry)
- Clear operation applies to all field types

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Identity and setup
- Discovery Refinements:
  - Text field consolidation (same input logic)
  - Numeric field consolidation (same validation)
  - Power level calculation (15 × PL formula)

