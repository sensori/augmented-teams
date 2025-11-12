# ⚙️ Validate Point Expenditure - Feature Overview

**File Name**: `⚙️ Validate Point Expenditure - Feature Overview.md`

**Epic:** Validate Character

## Feature Purpose

Enable system to validate character's point expenditure against total and category budgets, flagging overspend errors with category-specific UI, calculating unspent points by category, and displaying remaining budget available for character building.

---

## Domain AC (Feature Level)

### Core Domain Concepts

**Character:** Player-created hero
- **Total Point Budget**: 15 × Power Level
- **Category Budgets**: Portion of total allocated to each category
- **Point Expenditure Tracking**: Tracks spent vs available by category
- **Validation State**: Valid (within budget) or Overspend (exceeds budget)

**Point Budget:** Total and category-level point allocation
- **Total**: 15 × Power Level (all categories combined)
- **Categories**: 
  - Abilities (typically 20-40 points)
  - Skills (typically 20-30 points)
  - Advantages (typically 20-30 points)
  - Powers (typically 40-60 points)
  - Defenses (typically 10-20 points)
- **Formula**: Total = Abilities + Skills + Advantages + Powers + Defenses
- **Constraint**: Total spent ≤ Total budget

**Category:** Point expenditure grouping
- **Name**: Abilities, Skills, Advantages, Powers, Defenses
- **Spent**: Points allocated to category
- **Available**: Budget - Spent
- **Overspend**: When Spent > Budget (error state)

**Validation Error:** Point budget violation
- **Scope**: Total budget or category budget
- **Severity**: Warning (displayed but doesn't prevent save)
- **Display**: Category-specific UI with overspend amount
- **Message**: Actionable guidance on how to fix

---

### Domain Behaviors

**Validate Total Points:** Check if total spent within budget
- **Calculation**: Sum all category expenditures
- **Comparison**: Total spent ≤ Total budget
- **Result**: Pass (valid) or Fail (overspend)
- **Error Display**: Flags overspend amount and affected categories

**Validate Category Points:** Check if category spent within reasonable allocation
- **Per Category**: Abilities, Skills, Advantages, Powers, Defenses
- **Calculation**: Sum points spent in category
- **Comparison**: Category spent compared to typical allocation ranges
- **Result**: Pass or Warning (overspend)
- **UI**: Category-specific error displays (highlights category section)

**Calculate Unspent Points:** Determine remaining points available
- **By Category**: Budget - Spent for each category
- **Total**: Total budget - Total spent
- **Display**: Shows remaining points available for allocation
- **Real-Time**: Recalculates whenever points spent/refunded

---

### Domain Rules

**Total Point Budget:**
- Formula: 15 × Power Level
- Examples:
  - PL 8 = 120 points
  - PL 10 = 150 points
  - PL 12 = 180 points

**Category Budget Validation:**
- **Abilities**: 2 points per rank
- **Skills**: 0.5 points (untrained) or 1 point (trained-only) per rank
- **Advantages**: Flat cost or per-rank cost (varies by advantage)
- **Powers**: Varies by effect, extras, flaws
- **Defenses**: 1 point per rank

**Validation Philosophy:**
- **"Warn, Don't Prevent"**: Validation errors display warnings but NEVER block operations
- **Overspend Allowed**: User can intentionally exceed budget (house rules, experimental builds)
- **Persistent Warnings**: Errors remain highlighted until fixed
- **Category-Specific UI**: Each category has dedicated error display

**Unspent Points Calculation:**
- Formula: Budget - Spent = Unspent
- Per category: Shows available points in each category
- Total: Shows overall remaining budget

---

## Stories (5 total)

### 1. **System validates total points at or under budget** - 📝 Total budget validation

**Story Description**: System validates total points at or under budget - Flags overspend errors when total exceeds budget

#### Acceptance Criteria

##### Calculate Total Spent
- **When** character is validated, **then** system calculates total points spent across all categories (Abilities + Skills + Advantages + Powers + Defenses)

##### Compare to Total Budget
- **When** total spent calculated, **then** system compares total spent to total budget (15 × PL)

##### Pass if Within Budget
- **When** total spent ≤ total budget, **then** system marks total budget validation as passed

##### Flag Overspend
- **When** total spent > total budget, **then** system flags overspend error with amount over (e.g., "Total: 165/150 points - 15 points over budget")

##### Display Error
- **When** overspend flagged, **then** system displays overspend error at top of character sheet with actionable message

---

### 2. **System validates ability points at or under budget** - 📝 Ability category validation

**Story Description**: System validates ability points at or under budget - Flags overspend in abilities category with category-specific UI

#### Acceptance Criteria

##### Calculate Ability Spent
- **When** character is validated, **then** system calculates total points spent on abilities (sum of 8 ability costs)

##### Identify Overspend
- **When** ability points calculated, **then** system checks if spent amount is reasonable for character concept

##### Flag if Excessive
- **When** ability points exceed typical allocation, **then** system flags warning in abilities category

##### Display in Abilities Section
- **When** ability overspend flagged, **then** system highlights abilities section with warning indicator and spent amount

---

### 3. **System validates skill points at or under budget** - 📝 Skill category validation

**Story Description**: System validates skill points at or under budget - Flags overspend in skills category with category-specific UI

#### Acceptance Criteria

##### Calculate Skill Spent
- **When** character is validated, **then** system calculates total points spent on skills (sum of all skill costs)

##### Identify Overspend
- **When** skill points calculated, **then** system checks if spent amount is reasonable for character concept

##### Flag if Excessive
- **When** skill points exceed typical allocation, **then** system flags warning in skills category

##### Display in Skills Section
- **When** skill overspend flagged, **then** system highlights skills section with warning indicator and spent amount

---

### 4. **System validates advantage points at or under budget** - 📝 Advantage category validation

**Story Description**: System validates advantage points at or under budget - Flags overspend in advantages category with category-specific UI

#### Acceptance Criteria

##### Calculate Advantage Spent
- **When** character is validated, **then** system calculates total points spent on advantages (sum of all advantage costs)

##### Identify Overspend
- **When** advantage points calculated, **then** system checks if spent amount is reasonable for character concept

##### Flag if Excessive
- **When** advantage points exceed typical allocation, **then** system flags warning in advantages category

##### Display in Advantages Section
- **When** advantage overspend flagged, **then** system highlights advantages section with warning indicator and spent amount

---

### 5. **System calculates unspent points by category** - 📝 Remaining budget calculation

**Story Description**: System calculates unspent points by category - and displays remaining points for abilities, skills, and advantages

#### Acceptance Criteria

##### Calculate Unspent by Category
- **When** character is displayed, **then** system calculates unspent points for each category (Budget - Spent = Unspent)

##### Display Remaining Points
- **When** unspent calculated, **then** system displays remaining points for each category (e.g., "Abilities: 12 points remaining")

##### Calculate Total Unspent
- **When** unspent by category calculated, **then** system calculates total unspent (Total budget - Total spent)

##### Display Total Remaining
- **When** total unspent calculated, **then** system displays total remaining points available (e.g., "Total: 25 points remaining")

##### Real-Time Updates
- **When** user spends or refunds points in any category, **then** system immediately recalculates and updates unspent displays

---

## Consolidation Decisions

**Consolidated (Same Logic):**
- ✅ Category validations (Stories 2, 3, 4) - Same validation pattern, different categories (SEPARATED for category-specific UI)

**Separated (Different Logic):**
- ❌ Total vs Category validation (Stories 1 vs 2-4) - Total is hard limit, category is guidance
- ❌ Each category (Stories 2, 3, 4) - Different UI locations (abilities section, skills section, advantages section)
- ❌ Unspent calculation (Story 5) - Display calculation, not validation

**Result**: 5 stories with clear separation between total budget (hard limit) and category budgets (guidance), plus real-time unspent tracking

---

## Domain Rules Referenced

**From Hero's Handbook:**
- Chapter 1: Character Creation (pages 16-28) - Point budget system
- Total Budget Formula: 15 × PL
- Category allocations: Suggested ranges, not hard limits
- Validation Philosophy: "Warn, Don't Prevent" - overspend warnings don't block saves

**Discovery Refinements Applied:**
- Separated total (hard limit) from category (guidance) validation
- Category-specific UI for warnings (each category has dedicated error display)
- Unspent calculation separated from validation (display vs error checking)
- Real-time recalculation for immediate feedback

---

## Source Material

**Inherited From**: Story Map (Discovery Refinements)
- Primary Source: Mutants & Masterminds 3rd Edition - Hero's Handbook
- Chapter 1: Character Creation (pages 16-28) - Point budget, allocation patterns
- Discovery Refinements:
  - Total budget formula (15 × PL)
  - Category-based point tracking
  - "Warn, Don't Prevent" validation philosophy
  - Category-specific UI patterns


