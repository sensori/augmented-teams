# ⚙️ Validate Prerequisites - Feature Overview

**File Name**: `⚙️ Validate Prerequisites - Feature Overview.md`

**Epic:** Validate Character

## Feature Purpose

Enable system to validate that character's selected advantages meet all prerequisite requirements (ability, skill, advantage, power) with proper AND/OR logic handling, flagging violations when requirements not met, and ensuring prerequisite integrity throughout character building.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero
- **Advantages Collection**: Set of selected advantages
- **Abilities**: 8 ability ranks (Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- **Skills**: Variable set with ranks
- **Powers**: Variable set of power effects
- **Prerequisite Validation State**: Valid (all met) or Invalid (missing requirements)

**Advantage:** Special capability with potential prerequisites
- **Prerequisites**: Requirements to select (see Prerequisite concept)
- **Validation**: Checked against character's current state
- **Dependency**: May be prerequisite for other advantages

**Prerequisite:** Requirement to select an advantage
- **Types**:
  - Ability Score: Minimum ability rank (e.g., Strength 6+)
  - Skill Rank: Minimum skill rank (e.g., Acrobatics 4+)
  - Advantage: Must possess another advantage
  - Power: Must have specific power
- **Logic Operators**:
  - AND: All listed requirements must be met
  - OR: At least one listed requirement must be met
- **Validation Result**: Met or Unmet

**Validation Error:** Prerequisite violation
- **Advantage**: Which advantage has unmet prerequisite
- **Requirement**: What is missing
- **Current State**: What character currently has
- **Severity**: Warning (displayed but character can be saved)

---

### Domain Behaviors

**Validate Ability Score Prerequisite:** Check minimum ability rank
- **Check**: Compare character's ability rank to required minimum
- **Result**: Met (rank ≥ minimum) or Unmet (rank < minimum)
- **Error Message**: Shows required vs actual (e.g., "Requires Strength 6+, you have 4")

**Validate Skill Rank Prerequisite:** Check minimum skill rank
- **Check**: Compare character's skill rank to required minimum
- **Result**: Met (rank ≥ minimum) or Unmet (rank < minimum)
- **Error Message**: Shows required vs actual (e.g., "Requires Acrobatics 4+, you have 2")

**Validate Advantage Prerequisite:** Check possession of required advantage
- **Check**: Verify character has required advantage in collection
- **Result**: Met (has advantage) or Unmet (missing advantage)
- **Error Message**: Shows required advantage name (e.g., "Requires: Improved Initiative")

**Validate Power Prerequisite:** Check possession of required power
- **Check**: Verify character has required power
- **Result**: Met (has power) or Unmet (missing power)
- **Error Message**: Shows required power name (e.g., "Requires: Flight power")

**Validate Multiple Prerequisites (AND):** Check all requirements met
- **Logic**: ALL prerequisites must be satisfied
- **Check**: Evaluate each prerequisite, result is AND of all
- **Result**: Met (all valid) or Unmet (any invalid)
- **Error Message**: Lists ALL unmet requirements

**Validate Alternative Prerequisites (OR):** Check at least one requirement met
- **Logic**: AT LEAST ONE prerequisite must be satisfied
- **Check**: Evaluate each prerequisite, result is OR of all
- **Result**: Met (any valid) or Unmet (all invalid)
- **Error Message**: Shows ALL alternatives were unmet

---

### Domain Rules

**Prerequisite Validation Rules:**
- **Ability Score**: Character ability rank ≥ Required minimum
- **Skill Rank**: Character skill rank ≥ Required minimum
- **Advantage**: Character possesses required advantage in collection
- **Power**: Character possesses required power

**Boolean Logic:**
- **AND Logic**: ALL prerequisites must be met
  - Example: "Strength 8+ AND Fighting 6+" → Both must be satisfied
  - Fails if ANY requirement unmet
- **OR Logic**: AT LEAST ONE prerequisite must be met
  - Example: "Acrobatics 4+ OR Athletics 4+" → Either satisfies requirement
  - Fails only if ALL alternatives unmet

**Error Display:**
- **Format**: "Requires: [Prerequisite], you have: [Current Value]"
- **Multiple Errors**: List all unmet requirements for AND logic
- **Alternative Errors**: Show all alternatives for OR logic
- **Severity**: Warning (doesn't block save)

**Validation Timing:**
- **On Selection**: Check when user selects advantage (prevent invalid selection)
- **On Character Change**: Re-validate when abilities/skills/advantages/powers change
- **On Load**: Validate loaded character (catch data integrity issues)

---

## Stories (6 total)

### 1. **System validates ability score prerequisites for advantages** - 📝 Ability prerequisite checking

**Story Description**: System validates ability score prerequisites for advantages - Checks minimum ability rank required

#### Acceptance Criteria

##### Identify Advantages with Ability Prerequisites
- **When** validation runs, **then** system identifies all advantages in character collection that have ability score prerequisites

##### Check Each Ability Requirement
- **When** advantage has ability prerequisite, **then** system compares character's ability rank to required minimum

##### Flag if Unmet
- **When** character's ability rank < required minimum, **then** system flags prerequisite violation for that advantage

##### Display Error
- **When** ability prerequisite unmet, **then** system displays error showing required vs actual (e.g., "Precise Attack requires Dexterity 8+, you have 6")

---

### 2. **System validates skill rank prerequisites for advantages** - 📝 Skill prerequisite checking

**Story Description**: System validates skill rank prerequisites for advantages - Checks minimum skill rank required

#### Acceptance Criteria

##### Identify Advantages with Skill Prerequisites
- **When** validation runs, **then** system identifies all advantages with skill rank prerequisites

##### Check Each Skill Requirement
- **When** advantage has skill prerequisite, **then** system compares character's skill rank to required minimum

##### Flag if Unmet
- **When** character's skill rank < required minimum, **then** system flags prerequisite violation

##### Display Error
- **When** skill prerequisite unmet, **then** system displays error showing required vs actual (e.g., "Defensive Roll requires Acrobatics 4+, you have 2")

---

### 3. **System validates other advantage prerequisites for advantages** - 📝 Advantage dependency checking

**Story Description**: System validates other advantage prerequisites for advantages - Checks character has required advantage

#### Acceptance Criteria

##### Identify Advantages with Advantage Prerequisites
- **When** validation runs, **then** system identifies all advantages that require other advantages

##### Check Advantage Possession
- **When** advantage has advantage prerequisite, **then** system checks if character possesses required advantage in collection

##### Flag if Missing
- **When** character does not have required advantage, **then** system flags prerequisite violation

##### Display Error
- **When** advantage prerequisite unmet, **then** system displays error showing required advantage name (e.g., "Lightning Reflexes requires: Improved Initiative")

---

### 4. **System validates power prerequisites for advantages** - 📝 Power prerequisite checking

**Story Description**: System validates power prerequisites for advantages - Checks character has required power

#### Acceptance Criteria

##### Identify Advantages with Power Prerequisites
- **When** validation runs, **then** system identifies all advantages that require specific powers

##### Check Power Possession
- **When** advantage has power prerequisite, **then** system checks if character possesses required power

##### Flag if Missing
- **When** character does not have required power, **then** system flags prerequisite violation

##### Display Error
- **When** power prerequisite unmet, **then** system displays error showing required power (e.g., "Power Attack requires: Damage power")

---

### 5. **System validates multiple prerequisites with AND logic** - 📝 Multiple requirements all required

**Story Description**: System validates multiple prerequisites with AND logic - Checks all requirements met

#### Acceptance Criteria

##### Identify AND Logic Prerequisites
- **When** validation runs, **then** system identifies advantages with multiple prerequisites requiring AND logic (all must be met)

##### Check Each Requirement
- **When** advantage has AND prerequisites, **then** system validates each prerequisite independently

##### Pass if All Met
- **When** ALL prerequisites are met, **then** system marks advantage prerequisite validation as passed

##### Flag if Any Unmet
- **When** ANY prerequisite is unmet, **then** system flags prerequisite violation for that advantage

##### Display All Unmet
- **When** AND prerequisites violated, **then** system displays ALL unmet requirements in single error message (e.g., "Ultimate Effort requires: Strength 8+ (have 6) AND Will 8+ (have 7)")

---

### 6. **System validates alternative prerequisites with OR logic** - 📝 Alternative requirements one required

**Story Description**: System validates alternative prerequisites with OR logic - Checks at least one requirement met

#### Acceptance Criteria

##### Identify OR Logic Prerequisites
- **When** validation runs, **then** system identifies advantages with alternative prerequisites requiring OR logic (at least one must be met)

##### Check Each Alternative
- **When** advantage has OR prerequisites, **then** system validates each alternative prerequisite

##### Pass if Any Met
- **When** AT LEAST ONE prerequisite is met, **then** system marks advantage prerequisite validation as passed

##### Flag if None Met
- **When** NO prerequisites are met, **then** system flags prerequisite violation for that advantage

##### Display All Alternatives
- **When** OR prerequisites violated, **then** system displays ALL alternatives that were unmet (e.g., "Skill Mastery requires one of: Acrobatics 8+ (have 4) OR Athletics 8+ (have 5) OR Stealth 8+ (have 3)")

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Prerequisite validations (Stories 1-4) - Same validation pattern (compare/check), different data sources (SEPARATED by type)
- ✅ Boolean logic (Stories 5-6) - Same concept (combining prerequisites), different algorithms (AND vs OR)

**Separated (Different Logic):**
- ❌ Each prerequisite type (Stories 1-4) - Different data sources (abilities vs skills vs advantages vs powers)
- ❌ AND vs OR logic (Stories 5-6) - Different boolean operators (all required vs any required)

**Result**: 6 stories covering all prerequisite types and boolean logic combinations for comprehensive validation

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 4: Advantages (pages 64-77) - Prerequisite patterns and rules
- Prerequisite Types: Ability, Skill, Advantage, Power
- Boolean Logic: AND (all), OR (any)
- Validation Rules: Specific to each prerequisite type

**Discovery Refinements Applied:**
- Enumerated ALL prerequisite types (4 types)
- Separated AND vs OR boolean logic (different algorithms)
- Validation timing patterns (on selection, on change, on load)
- Error message formats for each type

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 4: Advantages (pages 64-77) - Prerequisite system, validation rules
- Discovery Refinements:
  - Prerequisite type enumeration (ability, skill, advantage, power)
  - Boolean logic patterns (AND all required, OR any required)
  - Error message templates per type
  - Validation timing (selection, change, load)


