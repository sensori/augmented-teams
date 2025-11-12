# Story Map: MM3E Character Creator Test

**File Name**: `mm3e-test-story-map.md`
**Location**: `demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md`

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

🎯 **Create Character** (3 features, ~20 stories)
│   *Relative Size: Simplified version of full MM3E creator*
│
├─ ⚙️ **Establish Identity** (~5 stories)
│  ├─ 📝 User enters character name
│  │   - and system saves to character sheet
│  ├─ 📝 User selects power level
│  │   - and system calculates and displays point budget
│  └─ 📝 ~3 more stories
│
├─ ⚙️ **Allocate Abilities** (~8 stories)
│  ├─ 📝 User increases ability rank
│  │   - and system calculates cost and updates budget
│  ├─ 📝 User decreases ability rank
│  │   - and system refunds points and updates budget
│  ├─ 📝 System displays ability modifier
│  │   - Calculates (rank - 10) ÷ 2 rounded down
│  └─ 📝 ~5 more stories
│
└─ ⚙️ **Select Advantages** (~7 stories)
   ├─ 📝 User selects advantage without prerequisites
   │   - and system adds to sheet and deducts cost
   ├─ 📝 User selects advantage with ability prerequisite
   │   - and system validates requirement and adds if valid
   └─ 📝 ~5 more stories

---

🎯 **Validate Character** (2 features, ~8 stories)
│   *Relative Size: Simple validation rules*
│
├─ ⚙️ **Validate Point Expenditure** (~4 stories)
│  ├─ 📝 System validates total points at or under budget
│  │   - Flags overspend in real-time
│  └─ 📝 ~3 more stories
│
└─ ⚙️ **Validate Prerequisites** (~4 stories)
   ├─ 📝 System validates advantage prerequisites met
   │   - Checks ability ranks, other advantages
   └─ 📝 ~3 more stories

---

## Source Material

**Primary Source**: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Location: demo/mm3e/HeroesHandbook.pdf
- Sections Referenced: 
  - Chapter 1: Character Creation Overview (pages 16-28)
  - Chapter 2: Abilities (pages 29-33)
  - Chapter 4: Advantages (pages 64-77)
- Date Generated: November 12, 2025

**Context for Discovery**: When proceeding to Discovery phase, reference the same source material sections to elaborate stories for the first increment.

