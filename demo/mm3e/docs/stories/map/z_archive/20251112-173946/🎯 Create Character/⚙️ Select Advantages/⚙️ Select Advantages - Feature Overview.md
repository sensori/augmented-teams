# ⚙️ Select Advantages - Feature Overview

**File Name**: `⚙️ Select Advantages - Feature Overview.md`

**Epic:** Create Character

## Feature Purpose

Enable users to select advantages (special capabilities and benefits) for their character, with system validating prerequisites (ability, skill, advantage, power requirements), calculating costs (flat or per-rank), managing dependencies, and providing search/filtering capabilities across 80+ advantage catalog.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero
- **Advantages Collection**: Variable set of selected advantages
- **Prerequisite Validation State**: Tracks which prerequisites are met
- **Advantage Point Tracking**: Tracks points spent on advantages separately
- **Point Budget**: 15 × Power Level (portion allocated to advantages)

**Advantage:** Special capability or benefit (catalog of 80+ options)
- **Types**:
  - Flat Cost: Fixed point cost (e.g., 1 point)
  - Ranked: Variable ranks, cost per rank (e.g., 2 points/rank)
- **Prerequisites**: Requirements that must be met to select
  - Ability Prerequisite: Minimum ability rank (e.g., Strength 6+)
  - Skill Prerequisite: Minimum skill rank (e.g., Acrobatics 4+)
  - Advantage Prerequisite: Must have another advantage
  - Power Prerequisite: Must have specific power
  - Multiple Prerequisites: AND logic (all must be met)
  - Alternative Prerequisites: OR logic (at least one must be met)
- **Categories**: Combat, Fortune, General, Skill (affects organization and display)
- **Cost**: Flat (1-5 points) or Per-Rank (1-5 points per rank)
- **Effects**: Mechanical benefits described per advantage

**Prerequisite:** Requirement to select an advantage
- **Types**: Ability, Skill, Advantage, Power
- **Logic**: AND (all required), OR (at least one required)
- **Validation**: Checked before advantage added
- **Dependencies**: Some advantages require others (forms dependency chain)

---

### Domain Behaviors

**Select Advantage:** Add advantage to character
- **Without Prerequisites**: Simple add, deduct cost
- **With Prerequisites**: Validate requirements, then add if valid
- **Ranked Advantages**: Prompt for rank selection, deduct cost × ranks
- **Cost Deduction**: Flat cost or rank-based cost from advantage points

**Validate Prerequisites:** Check if character meets requirements
- **Ability Check**: Compare character's ability rank to minimum required
- **Skill Check**: Compare character's skill rank to minimum required
- **Advantage Check**: Verify character has required advantage
- **Power Check**: Verify character has required power
- **Multiple (AND)**: All requirements must be met
- **Alternative (OR)**: At least one requirement must be met

**Remove Advantage:** Remove advantage from character
- **Simple Removal**: Refund cost, update budget
- **Ranked Removal**: Prompt confirmation, refund cost based on ranks
- **Dependency Check**: Prevent removal if other advantages depend on it
- **Flag Dependents**: Show which advantages would become invalid

**Search/Filter Advantages:** Find advantages in catalog
- **By Name**: Text search across advantage names
- **By Category**: Filter to Combat, Fortune, General, or Skill advantages
- **Display**: Show matching advantages with costs and prerequisites

**Display Advantage Cost:** Show cost information
- **Flat Cost**: Single number (e.g., "2 points")
- **Ranked Cost**: Per-rank notation (e.g., "3 points/rank")
- **Total Cost**: For ranked advantages with selected ranks

---

### Domain Rules

**Advantage Costs:**
- Flat: Fixed cost (1-5 points typically)
- Ranked: Cost per rank (1-5 points/rank typically)
- Total for ranked: Cost per rank × number of ranks

**Prerequisite Types:**
- **Ability**: Minimum ability rank (e.g., "Strength 6+")
- **Skill**: Minimum skill rank (e.g., "Acrobatics 4+")
- **Advantage**: Must possess another advantage (e.g., "Requires: Improved Initiative")
- **Power**: Must have specific power (e.g., "Requires: Flight power")

**Prerequisite Logic:**
- **AND**: All prerequisites listed must be met
- **OR**: At least one of listed prerequisites must be met
- Example AND: "Strength 8+ AND Fighting 6+" (both required)
- Example OR: "Acrobatics 4+ OR Athletics 4+" (either works)

**Dependency Validation:**
- When removing advantage: Check if any other advantages list it as prerequisite
- If dependencies exist: Prevent removal and flag dependent advantages
- User must remove dependents first (cascading removal)

**Advantage Categories:**
- **Combat**: Attack/defense bonuses, combat maneuvers
- **Fortune**: Hero point mechanics, rerolls, luck
- **General**: Broad benefits (wealth, connections, leadership)
- **Skill**: Skill-related bonuses and capabilities

---

## Stories (14 total)

### 1. **User selects advantage without prerequisites** - 📝 Simple advantage selection

**Story Description**: User selects advantage without prerequisites - and system adds to sheet and deducts flat cost

#### Acceptance Criteria

##### Select Advantage
- **When** user selects advantage from catalog that has no prerequisites, **then** system adds advantage to character sheet

##### Deduct Cost
- **When** system adds advantage, **then** system deducts advantage cost from available advantage points

##### Update Display
- **When** advantage added, **then** system displays advantage on character sheet with cost

##### Update Budget
- **When** cost deducted, **then** system updates remaining advantage points display

---

### 2. **User selects ranked advantage without prerequisites** - 📝 Ranked advantage with rank selection

**Story Description**: User selects ranked advantage without prerequisites - and system prompts for rank selection and deducts cost per rank

#### Acceptance Criteria

##### Prompt for Ranks
- **When** user selects ranked advantage from catalog, **then** system prompts user to select number of ranks

##### Accept Rank Selection
- **When** user enters number of ranks, **then** system validates rank is positive integer

##### Calculate Total Cost
- **When** ranks selected, **then** system calculates total cost (cost per rank × number of ranks)

##### Deduct Total Cost
- **When** total cost calculated, **then** system deducts total from available advantage points

##### Display with Ranks
- **When** ranked advantage added, **then** system displays advantage with rank count and total cost (e.g., "Benefit 3 (9 points)")

---

### 3. **User selects advantage with ability score prerequisite** - 📝 Ability prerequisite validation

**Story Description**: User selects advantage with ability score prerequisite - and system validates minimum ability rank and adds if valid

#### Acceptance Criteria

##### Check Ability Rank
- **When** user selects advantage with ability prerequisite, **then** system compares character's ability rank to minimum required

##### Add if Valid
- **When** character's ability rank meets or exceeds minimum, **then** system adds advantage and deducts cost

##### Reject if Invalid
- **When** character's ability rank is below minimum, **then** system prevents addition and displays prerequisite requirement message (e.g., "Requires Strength 6+, you have Strength 4")

---

### 4. **User selects advantage with skill rank prerequisite** - 📝 Skill prerequisite validation

**Story Description**: User selects advantage with skill rank prerequisite - and system validates minimum skill rank and adds if valid

#### Acceptance Criteria

##### Check Skill Rank
- **When** user selects advantage with skill prerequisite, **then** system compares character's skill rank to minimum required

##### Add if Valid
- **When** character's skill rank meets or exceeds minimum, **then** system adds advantage and deducts cost

##### Reject if Invalid
- **When** character's skill rank is below minimum, **then** system prevents addition and displays prerequisite requirement message (e.g., "Requires Acrobatics 4+, you have Acrobatics 2")

---

### 5. **User selects advantage with other advantage prerequisite** - 📝 Advantage prerequisite validation

**Story Description**: User selects advantage with other advantage prerequisite - and system validates character has required advantage and adds if valid

#### Acceptance Criteria

##### Check Advantage Possession
- **When** user selects advantage with advantage prerequisite, **then** system checks if character has required advantage

##### Add if Valid
- **When** character has required advantage, **then** system adds new advantage and deducts cost

##### Reject if Invalid
- **When** character does not have required advantage, **then** system prevents addition and displays prerequisite requirement message (e.g., "Requires: Improved Initiative")

---

### 6. **User selects advantage with power prerequisite** - 📝 Power prerequisite validation

**Story Description**: User selects advantage with power prerequisite - and system validates character has required power and adds if valid

#### Acceptance Criteria

##### Check Power Possession
- **When** user selects advantage with power prerequisite, **then** system checks if character has required power

##### Add if Valid
- **When** character has required power, **then** system adds advantage and deducts cost

##### Reject if Invalid
- **When** character does not have required power, **then** system prevents addition and displays prerequisite requirement message (e.g., "Requires: Flight power")

---

### 7. **User selects advantage with multiple prerequisites (AND logic)** - 📝 Multiple prerequisites all required

**Story Description**: User selects advantage with multiple prerequisites (AND logic) - and system validates all requirements met and adds if valid

#### Acceptance Criteria

##### Check All Prerequisites
- **When** user selects advantage with AND logic prerequisites, **then** system validates each prerequisite in list

##### Add if All Valid
- **When** ALL prerequisites are met, **then** system adds advantage and deducts cost

##### Reject if Any Invalid
- **When** ANY prerequisite is not met, **then** system prevents addition and displays ALL unmet requirements (e.g., "Requires: Strength 8+ (have 6), Fighting 6+ (have 4)")

---

### 8. **User selects advantage with alternative prerequisites (OR logic)** - 📝 Alternative prerequisites one required

**Story Description**: User selects advantage with alternative prerequisites (OR logic) - and system validates at least one requirement met and adds if valid

#### Acceptance Criteria

##### Check Each Alternative
- **When** user selects advantage with OR logic prerequisites, **then** system validates each alternative prerequisite

##### Add if Any Valid
- **When** AT LEAST ONE prerequisite is met, **then** system adds advantage and deducts cost

##### Reject if None Valid
- **When** NO prerequisites are met, **then** system prevents addition and displays ALL alternatives (e.g., "Requires one of: Acrobatics 4+ (have 2) OR Athletics 4+ (have 1)")

---

### 9. **User removes advantage from character** - 📝 Simple advantage removal

**Story Description**: User removes advantage from character - and system refunds cost and updates budget

#### Acceptance Criteria

##### Remove Advantage
- **When** user removes advantage from character sheet, **then** system removes advantage from character

##### Refund Cost
- **When** advantage removed, **then** system refunds advantage cost to available advantage points

##### Update Display
- **When** cost refunded, **then** system updates character sheet and remaining advantage points display

---

### 10. **User removes ranked advantage from character** - 📝 Ranked advantage removal with confirmation

**Story Description**: User removes ranked advantage from character - and system prompts for removal confirmation and refunds cost based on ranks

#### Acceptance Criteria

##### Prompt Confirmation
- **When** user removes ranked advantage, **then** system prompts for removal confirmation showing ranks and total cost to be refunded

##### Remove on Confirm
- **When** user confirms removal, **then** system removes advantage from character

##### Refund Total Cost
- **When** ranked advantage removed, **then** system refunds total cost (cost per rank × ranks) to available advantage points

##### Cancel on Reject
- **When** user cancels removal, **then** system keeps advantage on character unchanged

---

### 11. **User removes advantage that is prerequisite for another** - 📝 Dependency prevention

**Story Description**: User removes advantage that is prerequisite for another - and system flags dependent advantages and prevents removal

#### Acceptance Criteria

##### Check Dependencies
- **When** user attempts to remove advantage, **then** system checks if any other advantages list it as prerequisite

##### Prevent Removal if Dependencies
- **When** advantage is prerequisite for other advantages, **then** system prevents removal

##### Display Dependent List
- **When** removal prevented, **then** system displays list of advantages that depend on this one (e.g., "Cannot remove Improved Initiative: Required by Lightning Reflexes, Uncanny Dodge")

##### Guide User
- **When** dependencies shown, **then** system instructs user to remove dependent advantages first

---

### 12. **User searches advantages by name** - 📝 Text search filtering

**Story Description**: User searches advantages by name - and system filters displayed advantages

#### Acceptance Criteria

##### Accept Search Term
- **When** user enters text in advantage search field, **then** system accepts search term

##### Filter by Name Match
- **When** search term entered, **then** system filters advantage catalog to show only advantages with names matching search term (case-insensitive)

##### Display Matches
- **When** filtering applied, **then** system displays matching advantages with costs and prerequisites

##### Clear Search
- **When** user clears search field, **then** system displays all advantages

---

### 13. **User filters advantages by category** - 📝 Category filtering

**Story Description**: User filters advantages by category - and system displays advantages matching category with category-specific effects

#### Acceptance Criteria

##### Select Category Filter
- **When** user selects category filter (Combat, Fortune, General, Skill), **then** system filters advantage catalog to show only advantages in selected category

##### Display Category Advantages
- **When** category filter applied, **then** system displays matching advantages organized by category

##### Show Category Effects
- **When** category advantages displayed, **then** system shows category-specific effect descriptions (e.g., Combat advantages show attack/defense bonuses)

##### Clear Category Filter
- **When** user clears category filter, **then** system displays all advantages across all categories

---

### 14. **System displays advantage cost** - 📝 Cost display logic

**Story Description**: System displays advantage cost - Shows flat cost or per-rank cost based on advantage type

#### Acceptance Criteria

##### Display Flat Cost
- **When** displaying flat-cost advantage, **then** system shows cost as single number (e.g., "2 points")

##### Display Ranked Cost
- **When** displaying ranked advantage, **then** system shows cost per rank (e.g., "3 points/rank")

##### Display Selected Total
- **When** displaying ranked advantage already selected with ranks, **then** system shows total cost (e.g., "3 points/rank × 4 ranks = 12 points")

##### Highlight Affordability
- **When** displaying advantage cost, **then** system indicates if character has enough points (e.g., grayed out if unaffordable)

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Prerequisite validation (Stories 3-8) - Same validation pattern, different prerequisite types (SEPARATED by type)
- ✅ Simple vs ranked removal (Stories 9-10) - Different confirmation flows (SEPARATED)

**Separated (Different Logic):**
- ❌ Each prerequisite type (Stories 3-6) - Different data sources checked (ability vs skill vs advantage vs power)
- ❌ AND vs OR logic (Stories 7-8) - Different boolean logic (all required vs any required)
- ❌ Dependency check (Story 11) - Additional validation not in simple removal
- ❌ Search vs category filter (Stories 12-13) - Different filtering algorithms (text match vs category match)

**Result**: 14 stories covering 80+ advantage catalog with comprehensive prerequisite validation, dependency management, and filtering

**Catalog Complexity Note**: 80+ advantages organized into 4 categories with varying prerequisite patterns. Stories enumerate prerequisite TYPE permutations (6 types × validation paths), not individual advantages.

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 4: Advantages (pages 64-77) - Complete advantage catalog
- Advantage Types: Flat vs Ranked costs
- Prerequisite Patterns: Ability, Skill, Advantage, Power prerequisites
- Boolean Logic: AND (all) vs OR (any) prerequisite combinations
- Categories: Combat, Fortune, General, Skill
- Dependency Rules: Cannot remove if prerequisite for others

**Discovery Refinements Applied:**
- Separated by prerequisite TYPE, not by individual advantage
- 80+ advantages → 14 stories (type-based decomposition)
- AND vs OR logic separated (different boolean algorithms)
- Dependency checking separate story (complex validation)
- Search vs filter separated (different matching algorithms)

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 4: Advantages (pages 64-77) - Advantage catalog, prerequisites, costs
- Discovery Refinements:
  - Prerequisite type enumeration (6 types: none, ability, skill, advantage, power, AND, OR)
  - Catalog complexity note: 80+ items decomposed by behavioral TYPE not by individual item
  - Dependency chain validation patterns
  - Category organization and filtering patterns

