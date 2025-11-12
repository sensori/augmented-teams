# ⚙️ Purchase Skills - Feature Overview

**File Name**: `⚙️ Purchase Skills - Feature Overview.md`

**Epic:** Create Character

## Feature Purpose

Enable users to purchase skill ranks for their character, with system calculating costs based on skill training type (untrained vs trained-only), applying ability modifiers, grouping skills by ability, and providing filtering capabilities.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Skill:** Trained capability based on linked Ability
- **Types**: 
  - Untrained: Can be used with 0 ranks, costs 0.5 points per rank
  - Trained-only: Requires minimum 1 rank, costs 1 point per rank
- **Linked Ability**: Each skill links to one ability (e.g., Athletics → Strength)
- **Total Modifier**: Ability modifier + Skill ranks
- **Display**: Grouped by linked ability category

**Character:** Player-created hero
- **Has**: Variable number of skills (can purchase any skills)
- **Skill Point Tracking**: Tracks points spent on skills separately from ability points

**Ability:** Fundamental attribute affecting skills
- **Provides**: Modifier to linked skills
- **Formula**: (Rank - 10) ÷ 2 rounded down

**Skill Rank:** Number of ranks purchased in a skill
- **Range**: 0+ for untrained, 1+ for trained-only
- **Cost**: 0.5 points (untrained) or 1 point (trained-only) per rank

---

### Domain Behaviors

**Add Ranks to Untrained Skill:** Purchase ranks for skill usable at 0 ranks
- **Cost**: 0.5 points per rank
- **Can start at**: 0 ranks (no minimum)
- **Total**: Ability modifier + Skill ranks
- **Display**: Shows total modifier

**Add Ranks to Trained-Only Skill:** Purchase ranks for skill requiring training
- **Cost**: 1 point per rank
- **Minimum**: 1 rank required (validates minimum when first added)
- **Total**: Ability modifier + Skill ranks
- **Display**: Shows total modifier

**Decrease to Zero on Untrained:** Remove all ranks from untrained skill
- **Refund**: 0.5 points per rank removed
- **Result**: Skill remains visible at 0 ranks (still usable untrained)
- **Display**: Updates to show 0 ranks with ability modifier only

**Decrease to Zero on Trained-Only:** Remove all ranks from trained-only skill
- **Refund**: 1 point per rank removed
- **Result**: Skill removed from display (can't use without training)
- **Validation**: Removes skill from character

**Calculate Skill Total:** Compute skill's total modifier
- **Formula**: Ability modifier + Skill ranks
- **Automatic**: Recalculates when ability or skill ranks change
- **Display**: Shows total modifier

**Group Skills by Ability:** Organize skills by linked ability
- **Grouping**: Skills organized under their linked ability
- **Display**: Shows ability name as category header with skills beneath
- **Purpose**: Makes it clear which ability affects which skills

**Filter Skills:** Show subset of skills based on criteria
- **By Training Status**: Show only untrained or trained-only skills
- **By Search Term**: Show skills matching name search
- **Display**: Filtered list of matching skills

---

### Domain Rules

**Skill Costs:**
- Untrained: 0.5 points per rank
- Trained-only: 1 point per rank

**Skill Total Modifier:**
- Formula: Ability modifier + Skill ranks
- Example: Ability modifier +3, Skill ranks 4 = Total +7

**Training Requirements:**
- Untrained skills: Can use with 0 ranks (ability modifier only)
- Trained-only skills: Requires minimum 1 rank to use

**Ability-Skill Linking:**
- Each skill links to specific ability
- Common links: Athletics (Strength), Acrobatics (Agility), Perception (Awareness)
- Skill total recalculates when linked ability changes

**Skill Removal:**
- Untrained: Remains at 0 ranks (still visible and usable)
- Trained-only: Removed from character sheet (not usable without training)

---

## Stories (7 total)

### 1. **User adds ranks to untrained skill** - 📝 Purchase untrained skill ranks

**Story Description**: User adds ranks to untrained skill - and system calculates cost (0.5 points/rank) and displays total modifier

#### Acceptance Criteria

##### Add Ranks
- **When** user adds ranks to untrained skill, **then** system increases skill rank count

##### Calculate Cost
- **When** system adds skill ranks, **then** system calculates cost (0.5 points per rank)

##### Deduct Points
- **When** system calculates cost, **then** system deducts points from skill points budget

##### Calculate Total Modifier
- **When** skill ranks change, **then** system calculates total modifier (Ability modifier + Skill ranks)

##### Display Total
- **When** system calculates total modifier, **then** system displays total modifier next to skill (e.g., "+7")

---

### 2. **User adds ranks to trained-only skill** - 📝 Purchase trained-only skill ranks

**Story Description**: User adds ranks to trained-only skill - and system validates minimum 1 rank and calculates cost (1 point/rank) and displays total modifier

#### Acceptance Criteria

##### Validate Minimum Rank
- **When** user adds first rank to trained-only skill, **then** system ensures minimum 1 rank is maintained

##### Add Ranks
- **When** user adds ranks to trained-only skill, **then** system increases skill rank count

##### Calculate Cost
- **When** system adds skill ranks, **then** system calculates cost (1 point per rank)

##### Deduct Points
- **When** system calculates cost, **then** system deducts points from skill points budget

##### Calculate Total Modifier
- **When** skill ranks change, **then** system calculates total modifier (Ability modifier + Skill ranks)

##### Display Total
- **When** system calculates total modifier, **then** system displays total modifier next to skill

---

### 3. **User decreases skill ranks to zero on untrained skill** - 📝 Remove all ranks from untrained

**Story Description**: User decreases skill ranks to zero on untrained skill - and system refunds points and updates total

#### Acceptance Criteria

##### Decrease to Zero
- **When** user decreases untrained skill ranks to 0, **then** system sets skill ranks to 0

##### Refund Points
- **When** system decreases skill ranks, **then** system refunds points (0.5 points per rank removed)

##### Keep Skill Visible
- **When** untrained skill reaches 0 ranks, **then** system keeps skill visible on character sheet (still usable)

##### Display Ability Modifier Only
- **When** untrained skill is at 0 ranks, **then** system displays only ability modifier as total (no skill ranks)

---

### 4. **User decreases skill ranks to zero on trained-only skill** - 📝 Remove all ranks from trained

**Story Description**: User decreases skill ranks to zero on trained-only skill - and system refunds points and removes skill from display

#### Acceptance Criteria

##### Decrease to Zero
- **When** user decreases trained-only skill ranks to 0, **then** system removes skill ranks

##### Refund Points
- **When** system decreases skill ranks, **then** system refunds points (1 point per rank removed)

##### Remove from Display
- **When** trained-only skill reaches 0 ranks, **then** system removes skill from character sheet (not usable without training)

---

### 5. **System calculates skill total modifier** - 📝 Compute skill total

**Story Description**: System calculates skill total modifier - Adds ability modifier + skill ranks

#### Acceptance Criteria

##### Calculate Total
- **When** skill ranks or linked ability changes, **then** system calculates total modifier (Ability modifier + Skill ranks)

##### Display Total
- **When** system calculates total, **then** system displays total modifier on character sheet

##### Real-Time Updates
- **When** linked ability modifier changes, **then** system immediately recalculates and displays new skill total

---

### 6. **System groups skills by ability category** - 📝 Organize skills by linked ability

**Story Description**: System groups skills by ability category - Displays skills organized under their linked abilities

#### Acceptance Criteria

##### Group by Linked Ability
- **When** system displays skill list, **then** system organizes skills under their linked ability categories

##### Display Ability Headers
- **When** system groups skills, **then** system displays ability name as category header (e.g., "Strength Skills", "Agility Skills")

##### Show Skills Under Ability
- **When** system displays grouped skills, **then** system shows all skills linked to each ability beneath that ability's header

---

### 7. **User filters skills by training status or search term** - 📝 Filter skill display

**Story Description**: User filters skills by training status or search term - and system displays matching skills

#### Acceptance Criteria

##### Filter by Training Status
- **When** user selects "Untrained" filter, **then** system displays only untrained skills

##### Filter by Trained-Only
- **When** user selects "Trained-only" filter, **then** system displays only trained-only skills

##### Search by Name
- **When** user enters search term, **then** system displays skills with names matching search term

##### Clear Filter
- **When** user clears filter or search, **then** system displays all skills

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Add ranks (Stories 1, 2) - Same add logic, different cost formulas (separated)
- ✅ Decrease to zero (Stories 3, 4) - Same decrease logic, different result behaviors (separated)

**Separated (Different Logic):**
- ❌ Untrained vs Trained-only - Different cost formulas (0.5 vs 1 point/rank)
- ❌ Zero-rank behavior - Untrained stays visible, trained-only removed
- ❌ System calculations (Story 5) - Pure calculation, no point changes
- ❌ Grouping (Story 6) - Display organization, no data changes
- ❌ Filtering (Story 7) - Display filtering, no data changes

**Result**: 7 stories separating different cost formulas, zero-rank behaviors, and display operations

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 3: Skills (pages 34-63) - Complete skill system
- Skill Cost Formulas: Untrained (0.5 pts/rank), Trained-only (1 pt/rank)
- Skill Total: Ability modifier + Skill ranks
- Training requirements and skill categories

**Discovery Refinements Applied:**
- Separated untrained vs trained-only (different cost formulas)
- Separated zero-rank behaviors (display vs removal)
- Grouped system operations (calculate, group, filter) as separate stories

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 3: Skills (pages 34-63) - Skill system, training rules, ability linking
- Discovery Refinements:
  - Cost formula differences (0.5 vs 1.0 points/rank)
  - Training requirement patterns
  - Zero-rank behavior differences
  - Ability-skill linking patterns

