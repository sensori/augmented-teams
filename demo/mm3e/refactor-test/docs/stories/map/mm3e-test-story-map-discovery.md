# Story Map: MM3E Character Creator Test

**File Name**: `mm3e-test-story-map.md`
**Location**: `demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map-discovery.md`

## System Purpose
A simplified online character creator for Mutants & Masterminds 3rd Edition that enables users to create basic superhero characters by allocating ability scores and selecting advantages.

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

🎯 **Create Character** (3 features, 18 stories)
│   *Relative Size: Simplified version of full MM3E creator*
│
├─ ⚙️ **Establish Identity** (3 stories - NOW INCREMENT)
│  ├─ 📝 User enters character name
│  │   - and system saves to character sheet
│  ├─ 📝 User selects power level
│  │   - and system calculates and displays point budget (15 × PL)
│  └─ 📝 User clears identity field
│     - and system removes value and updates display
│
├─ ⚙️ **Allocate Abilities** (10 stories - NOW INCREMENT)
│  ├─ 📝 User increases ability rank from current value
│  │   - and system calculates incremental cost (2 points/rank) and updates budget
│  ├─ 📝 User decreases ability rank from current value
│  │   - and system refunds points (2 points/rank) and updates budget
│  ├─ 📝 User sets ability to negative rank
│  │   - and system refunds points and applies negative modifier
│  ├─ 📝 System displays ability modifier
│  │   - Calculates (rank - 10) ÷ 2 rounded down
│  ├─ 📝 System updates dodge defense when agility changes
│  │   - Recalculates defense using new ability modifier
│  ├─ 📝 System updates toughness and fortitude when stamina changes
│  │   - Recalculates both defenses using new ability modifier
│  ├─ 📝 System updates parry defense and close attack when fighting changes
│  │   - Recalculates defense and attack bonus using new ability modifier
│  ├─ 📝 System updates close attack damage when strength changes
│  │   - Recalculates damage bonus using new ability modifier
│  ├─ 📝 System updates ranged attack when dexterity changes
│  │   - Recalculates attack bonus using new ability modifier
│  └─ 📝 System updates will defense when awareness changes
│     - Recalculates defense using new ability modifier
│
└─ ⚙️ **Select Advantages** (~5 stories - NEXT INCREMENT)
   ├─ 📝 User selects advantage without prerequisites
   │   - and system adds to sheet and deducts cost
   └─ 📝 ~4 more stories

---

🎯 **Validate Character** (2 features, ~10 stories)
│   *Relative Size: Simple validation rules*
│
├─ ⚙️ **Validate Point Expenditure** (5 stories - NOW INCREMENT)
│  ├─ 📝 System validates ability points at or under budget
│  │   - Flags overspend for ability category
│  ├─ 📝 System validates advantage points at or under budget
│  │   - Flags overspend for advantage category
│  ├─ 📝 System calculates unspent points by category
│  │   - Shows remaining budget per category
│  ├─ 📝 System displays total points spent
│  │   - Sum of all category expenditures
│  └─ 📝 System displays total points remaining
│     - Budget minus total spent
│
└─ ⚙️ **Validate Prerequisites** (~5 stories - NEXT INCREMENT)
   ├─ 📝 System validates advantage prerequisites met
   │   - Checks ability ranks, other advantages
   └─ 📝 ~4 more stories

---

## Source Material

**Primary Source**: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Location: demo/mm3e/HeroesHandbook.pdf
- Sections Referenced (Shaping): 
  - Chapter 1: Character Creation Overview (pages 16-28)
  - Chapter 2: Abilities (pages 29-33)
  - Chapter 4: Advantages (pages 64-77)
- Date Generated: November 12, 2025

**Discovery Refinements**: November 12, 2025
- **Increment in Focus**: Increment 1 - Basic Character Creation (NOW)
- **Additional Sections Referenced**:
  - Chapter 2: Abilities (pages 29-33) - Ability modifier formula, negative ranks, defense cascade patterns
  - Chapter 1: Point Budget (pages 18-20) - Category tracking (15 × PL formula)
- **Areas Elaborated**:
  - Increment 1 features fully decomposed (18 stories across 3 features)
  - Consolidated cascade updates by defense type (dodge, toughness/fortitude, parry/close attack, damage, ranged, will)
  - Separated ability changes from defense cascades (6 separate cascade stories by affected defense type)
  - Consolidated point validation by category (abilities, advantages)
- **Consolidation Rationale**:
  - Same logic, different data → CONSOLIDATED (e.g., point budget checks per category)
  - Different formulas/algorithms → SEPARATE (e.g., each defense has different calculation)

**Context for Exploration**: When writing acceptance criteria, reference sections above for ability modifier formula, point budget formula, and defense calculations.

