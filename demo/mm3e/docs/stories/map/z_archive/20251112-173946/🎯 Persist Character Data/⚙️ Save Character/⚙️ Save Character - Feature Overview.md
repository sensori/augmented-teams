# ⚙️ Save Character - Feature Overview

**File Name**: `⚙️ Save Character - Feature Overview.md`

**Epic:** Persist Character Data

## Feature Purpose

Enable users to persist character data to cloud storage through manual saves, automatic saves, and versioned revisions, with validation warnings that inform but never prevent save operations.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero in Mutants & Masterminds 3rd Edition game system
- **Composed of**: 8 Abilities, Skills (variable count), Advantages, Powers, Defenses, Attacks, Equipment
- **Identity**: Name, real name, concept, description, player name, age, height, weight, gender
- **Point Budget**: 15 × Power Level (total points available for building character)
- **States**: Draft (work in progress, may have validation errors), Complete (ready for play)
- **Validation Philosophy**: "Warn, Don't Prevent" - errors warn user but never block saves

**Ability:** Fundamental attribute of character (8 core abilities: Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence)
- **Range**: 0-20 ranks (10 is average human)
- **Cost**: 2 points per rank
- **Modifier**: (Rank - 10) ÷ 2 rounded down
- **Affects**: Skills (linked ability modifier), Defenses (various), Attack bonuses

**Skill:** Trained capability based on linked Ability
- **Types**: Untrained (0.5 pts/rank), Trained-only (1 pt/rank)
- **Total Modifier**: Ability modifier + Skill ranks
- **Categories**: Grouped by linked Ability

**Advantage:** Special capability or benefit
- **Cost**: Flat cost or per-rank cost (ranked advantages)
- **Prerequisites**: May require specific Ability ranks, Skills, other Advantages, or Powers

**Power:** Superhuman capability
- **Components**: Base effect, Extras (increase cost), Flaws (decrease cost)
- **Categories**: Various power types defined in game rules

**Defense:** Resistance to attacks (Dodge, Parry, Fortitude, Toughness, Will)
- **Calculation**: Base 10 + Ability modifier + purchased ranks (varies by defense type)

**Attack:** Offensive capability
- **Types**: Close combat, Ranged combat, Power-based
- **Attack Bonus**: Based on relevant Ability
- **Damage**: Based on Ability or Power

**Equipment:** Gear and gadgets
- **Cost**: Equipment points (separate from character points)

---

### Domain Behaviors

**Save:** Persist Character to storage
- **Operations**: 
  - Create: First save of new Character (no existing record)
  - Update: Subsequent save of existing Character
  - Save As Revision: Create versioned snapshot in version history
- **Complete Saves**: Always saves entire Character (all components), never partial updates
- **Triggers**: 
  - Manual: User clicks Save button
  - Auto-Save: Timer expires (2-minute interval)
  - Revision: User clicks "Save as Revision" with version note
- **Validation**: Warns about errors, never prevents save

**Validate:** Check Character against game rules
- **Categories**: Point expenditure, Prerequisites, Power Level limits, Required fields
- **Error Handling**: Highlights errors on sheet, groups by category, provides actionable messages
- **Philosophy**: "Warn, Don't Prevent" - user maintains control, can save with errors
- **Persistence**: Warnings remain after save (not cleared)

**Auto-Save:** Background save without user action
- **Timer**: 2 minutes from last save or last edit
- **Behavior**: Non-intrusive, doesn't interrupt user
- **Error Recovery**: Network errors retry silently on next interval

---

### Domain Rules

**Point Budget:**
- Formula: 15 × Power Level
- Example: Power Level 10 = 150 total points

**Point Costs:**
- Abilities: 2 points per rank
- Skills (Untrained): 0.5 points per rank
- Skills (Trained-only): 1 point per rank
- Advantages: Varies by advantage (flat or per-rank)
- Powers: Varies by effect, extras, flaws

**Ability Modifier:**
- Formula: (Rank - 10) ÷ 2 rounded down
- Example: Strength 14 = +2 modifier

**Validation Philosophy:**
- **"Warn, Don't Prevent"**: Validation errors display warnings but NEVER block save operations
- **User Control**: User can intentionally break rules (house rules, experimental builds)
- **Persistent Warnings**: Errors remain highlighted after save
- **Error Grouping**: By category (point expenditure, prerequisites, power level limits)

**Auto-Save Timing:**
- Interval: 2 minutes from last save or last edit
- Reset: Manual save resets timer

**Save Status States:**
- "Saving..." / "Auto-saving..." (in progress)
- "Saved at [timestamp]" (success)
- "Unsaved changes" (modified since save)
- "Error - [message]" (failure with retry)

---

## Stories (5 total)

### 1. **User saves character to cloud storage** - 📝 Manual save with create/update modes

**Story Description**: User saves character to cloud storage - and system validates data completeness and creates or updates record

#### Acceptance Criteria

##### Create New Character
- **When** user clicks Save button for character that does not exist in cloud storage, **then** system creates new character record with all character data

##### Update Existing Character  
- **When** user clicks Save button for character that exists in cloud storage, **then** system updates existing character record with current character data

##### Data Completeness
- **When** system saves character, **then** system includes all character sections: identity, abilities, skills, advantages, powers, defenses, attacks, equipment

##### Save Success Feedback
- **When** save operation completes successfully, **then** system displays "Saved" status with timestamp and marks character as having no unsaved changes

##### Save with Validation Errors (Warn, Don't Prevent)
- **When** user clicks Save button for character with validation errors, **then** system displays warning message with error list and allows save to proceed
- **When** system saves character with validation errors, **then** system highlights errors on character sheet and groups errors by category (point expenditure, prerequisites, power level limits)

##### Network Error Handling
- **When** save operation fails due to network error, **then** system displays "Error" status with retry option
- **When** save operation fails due to server error, **then** system displays "Error" status with error message

---

### 2. **System auto-saves character during editing** - 📝 Timer-based background save

**Story Description**: System auto-saves character during editing - Saves draft every 2 minutes without user action

#### Acceptance Criteria

##### Auto-Save Timer
- **When** 2 minutes have elapsed since last save or last edit, **then** system automatically saves character draft without user interaction

##### Non-Intrusive Save
- **When** auto-save operation runs while user is editing character, **then** system completes save without interrupting user input or navigation

##### Auto-Save Status Indication
- **When** auto-save operation starts, **then** system displays subtle "Auto-saving..." status indicator (less prominent than manual save)
- **When** auto-save operation completes successfully, **then** system updates "Saved" status with last-saved timestamp

##### Timer Reset on Manual Save
- **When** manual save completes, **then** system resets auto-save timer to start new 2-minute countdown

##### Auto-Save with Validation Errors (Warn, Don't Prevent)
- **When** auto-save timer expires for character with validation errors, **then** system saves draft with errors and displays warning indicators on character sheet

##### Silent Error Recovery
- **When** auto-save operation fails due to network error, **then** system retries silently on next timer interval without displaying error to user

---

### 3. **User saves character revision with version note** - 📝 Versioned snapshot creation

**Story Description**: User saves character revision with version note - and system creates version history entry with timestamp and note

#### Acceptance Criteria

##### Version Note Prompt
- **When** user clicks "Save as Revision" button, **then** system prompts user for version note text

##### Create Version History Entry
- **When** user submits version note, **then** system creates version history entry with current timestamp, user-provided note, and complete character snapshot

##### Maintain Active Version
- **When** revision save completes, **then** system keeps current character as active version (revision is saved separately, not as replacement)

##### Version Count Feedback
- **When** revision save completes successfully, **then** system displays confirmation message with total revision count (e.g., "Revision #3 saved")

##### Revision with Validation Errors (Warn, Don't Prevent)
- **When** user saves revision for character with validation errors, **then** system displays warning message with error list and allows revision save to proceed

---

### 4. **User saves character with validation errors** - 📝 Warning system that never prevents save

**Story Description**: User saves character with validation errors - and system warns about errors but allows save to proceed (user control philosophy)

#### Acceptance Criteria

##### Warning Display on Save Attempt
- **When** user attempts save (manual or auto) for character with validation errors, **then** system displays warning message with complete error list

##### Error Categorization
- **When** system displays validation warnings, **then** system groups errors by category: point expenditure, prerequisites, power level limits, required fields

##### Error Highlighting on Sheet
- **When** system displays validation warnings, **then** system highlights error locations on character sheet (visual indicators on fields/sections with errors)

##### Actionable Error Messages
- **When** user views error list, **then** system provides actionable error messages explaining what rule is violated and how to fix it

##### Navigation to Errors
- **When** user clicks on validation error in warning list, **then** system navigates to the character sheet section/field with the error

##### Save Proceeds with Warnings
- **When** user confirms save despite validation warnings, **then** system completes save operation with character in current state (errors included)

##### Persistent Warning Indicators
- **When** character with validation errors is loaded later, **then** system displays warning indicators showing errors still exist

---

### 5. **System indicates save status to user** - 📝 Shared status component with state machine

**Story Description**: System indicates save status to user - Displays "Saving...", "Saved", or "Error" status with appropriate visual feedback

#### Acceptance Criteria

##### Saving Status
- **When** save operation starts (manual or auto-save), **then** system displays "Saving..." status indicator

##### Saved Status with Timestamp
- **When** save operation completes successfully, **then** system displays "Saved" status indicator with timestamp of last save (e.g., "Saved at 2:30 PM")

##### Error Status with Retry
- **When** save operation fails, **then** system displays "Error" status indicator with error message and retry option

##### Unsaved Changes Indicator
- **When** user makes any change to character after successful save, **then** system changes status to "Unsaved changes" indicator

##### Auto-Save Status (Subtle)
- **When** auto-save operation runs, **then** system shows subtle "Auto-saving..." indicator less prominent than manual save indicator

##### Status Persistence
- **When** character is loaded from storage, **then** system displays "Saved" status with timestamp from last save operation

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Save operations (Stories 1, 2, 3) - Same save logic, different triggers
- ✅ Status indicators (Story 5) - Shared component across all saves
- ✅ Validation warnings (Story 4) - Applied consistently to all save operations

**Separated (Different Logic):**
- ❌ Error handling strategies - Manual save (user-visible) vs Auto-save (silent retry)
- ❌ Status prominence - Manual save (prominent) vs Auto-save (subtle)
- ❌ Warning dialogs - Manual/Revision (blocking dialog) vs Auto-save (subtle indicators)

**Result**: 5 stories with clear separation of concerns and shared domain concepts

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 1: Character Creation (pages 16-28) - Save/load patterns, character data
- Point Budget Formula: 15 × PL (for validation warnings)
- Power Level Limits: Various caps that may be violated with warnings

**Discovery Refinements Applied:**
- Unified save operation for all save types (manual, auto-save, revision)
- "Warn, Don't Prevent" validation philosophy
- 2-minute auto-save interval
- "Save As Revision" pattern for version history
- Shared status indicator component

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Save/load workflows
- Discovery Refinements: 
  - Single save API pattern
  - "Warn, Don't Prevent" validation philosophy
  - Auto-save interval and silent retry
  - Version history "Save As" pattern
  - Category-based validation error grouping

