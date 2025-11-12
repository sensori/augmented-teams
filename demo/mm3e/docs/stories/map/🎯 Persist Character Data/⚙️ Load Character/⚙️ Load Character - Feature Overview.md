# ⚙️ Load Character - Feature Overview

**File Name**: `⚙️ Load Character - Feature Overview.md`

**Epic:** Persist Character Data

## Feature Purpose

Enable users to load previously saved characters from cloud storage or version history, with system populating all character fields, recalculating derived values (ability modifiers, skill totals, defenses), validating data integrity, and offering repair options for corrupted data.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero (persisted state)
- **Storage State**: Saved (in cloud storage), Versioned (in version history)
- **Load Source**: Current version or historical version
- **Components**: Identity, 8 Abilities, Skills, Advantages, Powers, Defenses, Attacks, Equipment
- **Derived Values**: Ability modifiers, skill totals, defense values, attack bonuses (calculated from base values)
- **Data Integrity**: Valid (complete fields, consistent relationships) or Corrupted (missing/invalid fields)

**Ability:** Fundamental attribute (persisted and derived)
- **Persisted**: Rank value
- **Derived**: Modifier = (Rank - 10) ÷ 2 rounded down
- **Cascade**: Affects skills, defenses, attacks

**Skill:** Trained capability (persisted and derived)
- **Persisted**: Rank value
- **Derived**: Total modifier = Ability modifier + Skill ranks

**Defense:** Resistance to attacks (persisted and derived)
- **Persisted**: Purchased ranks
- **Derived**: Total = Base 10 + Ability modifier + Purchased ranks

**Attack:** Offensive capability (persisted and derived)
- **Persisted**: Base configuration
- **Derived**: Attack bonus, damage bonus (from abilities)

**Version History:** Timestamped character snapshots
- **Entry**: Timestamp, version note, complete character snapshot
- **Load**: Retrieves historical state (not current version)

**Data Integrity Check:** Validation of loaded data
- **Missing Fields**: Required fields not present
- **Invalid Values**: Out-of-range or malformed values
- **Broken Relationships**: References to non-existent data (e.g., skill referencing invalid ability)
- **Repair Options**: Auto-fix, manual fix, load different version

---

### Domain Behaviors

**Load Character:** Retrieve and populate character from storage
- **Source**: Current version or version history entry
- **Populate**: All character fields from persisted data
- **Trigger Recalculation**: Derived values calculated after load
- **Result**: Character fully populated and ready for editing

**Recalculate Derived Values:** Recompute calculated fields
- **Ability Modifiers**: (Rank - 10) ÷ 2 rounded down for each ability
- **Skill Totals**: Ability modifier + Skill ranks for each skill
- **Defense Values**: Base 10 + Ability modifier + Purchased ranks
- **Attack Bonuses**: Ability modifiers applied to attacks
- **Timing**: Triggered automatically after load completes

**Validate Data Integrity:** Check loaded data for errors
- **Missing Fields**: Scan for required fields not present
- **Invalid Values**: Check ranges and data types
- **Broken Relationships**: Verify references are valid
- **Result**: Valid or Corrupted (with error list)

**Repair Data:** Fix corrupted character data
- **Auto-Fix**: Apply default values for missing fields
- **Manual Fix**: Prompt user to correct invalid values
- **Version Rollback**: Offer to load earlier version
- **Error Guidance**: Actionable messages for each corruption type

---

### Domain Rules

**Derived Value Formulas:**
- **Ability Modifier**: (Rank - 10) ÷ 2 rounded down
- **Skill Total**: Ability modifier + Skill ranks
- **Defense**: Base 10 + Ability modifier + Purchased ranks (varies by defense type)
- **Attack Bonus**: Ability modifier (Fighting for close, Dexterity for ranged)

**Recalculation Order:**
1. Ability modifiers (base calculation)
2. Skill totals (depends on ability modifiers)
3. Defense values (depends on ability modifiers)
4. Attack bonuses (depends on ability modifiers)

**Data Integrity Rules:**
- **Required Fields**: Name, Power Level (minimum identity)
- **Valid Ranges**: Abilities (0-20), Skills (0+), Power Level (1-20)
- **Valid References**: Skills reference valid abilities, attacks reference valid abilities

**Repair Strategies:**
- **Missing Name**: Prompt user for name
- **Missing Power Level**: Default to 10 (standard)
- **Invalid Ability**: Clamp to valid range (0-20)
- **Broken Reference**: Remove invalid skill/attack or fix reference

---

## Stories (4 total)

### 1. **User loads character from storage or version history** - 📝 Character retrieval and population

**Story Description**: User loads character from storage or version history - and system populates all character fields

#### Acceptance Criteria

##### Load from Current Storage
- **When** user selects character from storage list, **then** system retrieves current version of character from cloud storage

##### Load from Version History
- **When** user selects version from history list, **then** system retrieves historical snapshot from version history

##### Populate Identity Fields
- **When** character loaded, **then** system populates all identity fields (name, real name, concept, description, player name, age, height, weight, gender, power level)

##### Populate Abilities
- **When** character loaded, **then** system populates all 8 ability ranks from persisted values

##### Populate Skills
- **When** character loaded, **then** system populates all skill ranks from persisted values

##### Populate Advantages
- **When** character loaded, **then** system populates advantages collection from persisted values

##### Populate Powers
- **When** character loaded, **then** system populates powers collection from persisted values

##### Populate Defenses
- **When** character loaded, **then** system populates purchased defense ranks from persisted values

##### Populate Attacks
- **When** character loaded, **then** system populates attack configurations from persisted values

##### Populate Equipment
- **When** character loaded, **then** system populates equipment collection from persisted values

##### Display Loaded Character
- **When** all fields populated, **then** system displays complete character sheet ready for viewing/editing

---

### 2. **System recalculates derived values when loading character** - 📝 Derived value reconstruction

**Story Description**: System recalculates derived values when loading character - Recalculates ability modifiers, skill totals, defense values

#### Acceptance Criteria

##### Recalculate Ability Modifiers
- **When** abilities populated from storage, **then** system recalculates all 8 ability modifiers using formula (Rank - 10) ÷ 2 rounded down

##### Recalculate Skill Totals
- **When** skills and ability modifiers loaded, **then** system recalculates total modifier for each skill (Ability modifier + Skill ranks)

##### Recalculate Defense Values
- **When** abilities and purchased defense ranks loaded, **then** system recalculates each defense value (Base 10 + Ability modifier + Purchased ranks)

##### Recalculate Attack Bonuses
- **When** abilities and attacks loaded, **then** system recalculates attack bonuses (Fighting for close, Dexterity for ranged, Strength for close damage)

##### Display Derived Values
- **When** all derived values recalculated, **then** system displays calculated values on character sheet (modifiers, totals, bonuses)

##### Recalculation Order
- **When** loading character, **then** system recalculates in order: ability modifiers → skill totals → defenses → attacks (dependency order)

---

### 3. **System validates loaded character data integrity** - 📝 Data corruption detection

**Story Description**: System validates loaded character data integrity - Checks for missing or corrupted fields and flags errors

#### Acceptance Criteria

##### Check Required Fields
- **When** character loaded, **then** system checks all required fields are present (name, power level minimum)

##### Flag Missing Fields
- **When** required field missing, **then** system flags data integrity error specifying missing field

##### Check Value Ranges
- **When** character loaded, **then** system validates all numeric values are within valid ranges (abilities 0-20, skills 0+, power level 1-20)

##### Flag Invalid Values
- **When** value out of range, **then** system flags data integrity error specifying field and invalid value

##### Check Relationships
- **When** character loaded, **then** system validates all references are valid (skills reference valid abilities, attacks reference valid abilities)

##### Flag Broken References
- **When** invalid reference found, **then** system flags data integrity error specifying broken relationship

##### Display Integrity Report
- **When** validation complete, **then** system displays data integrity status (Valid or Corrupted with error count)

---

### 4. **User loads character with invalid data** - 📝 Error handling and repair

**Story Description**: User loads character with invalid data - and system displays error message and offers repair options

#### Acceptance Criteria

##### Display Error Summary
- **When** character load detects data integrity errors, **then** system displays error summary with count and severity

##### List All Errors
- **When** integrity errors found, **then** system displays complete list of errors with field names and issues

##### Offer Auto-Repair
- **When** errors are auto-fixable (missing optional fields, invalid ranges), **then** system offers "Auto-Repair" option to apply default values

##### Offer Manual Repair
- **When** errors require user input (missing required fields), **then** system offers "Manual Repair" option to prompt user for corrections

##### Offer Version Rollback
- **When** character has version history, **then** system offers "Load Previous Version" option to rollback to earlier valid state

##### Apply Repair Choice
- **When** user selects repair option, **then** system applies chosen repair strategy and re-validates

##### Allow Load Despite Errors
- **When** user chooses to load without repair, **then** system loads character with errors flagged (follows "Warn, Don't Prevent" philosophy)

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Field population (Story 1) - Same load logic for all field types, enumerated for completeness
- ✅ Derived value recalculation (Story 2) - Same recalculation pattern, different formulas (ordered by dependency)

**Separated (Different Logic):**
- ❌ Load vs Recalculate (Stories 1 vs 2) - Load retrieves persisted, recalculate derives from persisted
- ❌ Integrity check vs Repair (Stories 3 vs 4) - Detection vs correction (different algorithms)

**Result**: 4 stories covering complete load workflow: retrieve → populate → recalculate → validate → repair

**Integration Point Note**: Story 2 (recalculate derived values) cascades to multiple systems (abilities → skills → defenses → attacks). This is complex coordination but treated as single story because it's one operation: "recalculate everything in dependency order."

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 1: Character Creation (pages 16-28) - Character structure, load patterns
- Chapter 2: Abilities (pages 29-33) - Ability modifier formula
- Chapter 3: Skills (pages 34-63) - Skill total calculation
- Chapter 7: Combat (pages 168-187) - Defense and attack calculations

**Discovery Refinements Applied:**
- Load workflow: retrieve → populate → recalculate → validate → repair
- Recalculation dependency order (ability mods first, then cascades)
- Data integrity patterns (missing, invalid, broken references)
- Repair strategy options (auto, manual, rollback)
- "Warn, Don't Prevent" philosophy (can load with errors)

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Character data structure
- Multiple chapters for derived value formulas
- Discovery Refinements:
  - Complete load workflow documented
  - Recalculation cascade order
  - Data integrity error types
  - Repair options and strategies


