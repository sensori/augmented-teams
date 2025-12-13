# Create and Command Mobs - Increment Exploration

**Navigation:** [📋 Story Map](story-map.txt) | [📊 Increments](story-map-increments.txt)

**File Name**: `create-and-command-mobs-exploration.md`
**Location**: `demo/mob_minion/docs/stories/create-and-command-mobs-exploration.md`

**Priority:** 1
**Relative Size:** 6 stories

## Increment Purpose

Game Master creates mobs from minion tokens and commands them with a single click so that combat encounters with multiple minions can be managed efficiently without individually selecting and commanding each token.

---

## Domain AC (Increment Level)

### Core Domain Concepts

- **Mob**: Collection of minions that act together as a coordinated unit. Groups minions together into collection, maintains collection of minion tokens, associates with active strategy.
- **Minion**: Individual game entity within Foundry VTT. Represents individual game entity, belongs to mob collection, executes actions when mob acts.
- **Token**: Visual representation of a minion on the Foundry game board. Represents minion visually on game board, receives click commands.
- **Strategy**: Behavioral rules for mob actions. Determines target selection behavior, defines mob action patterns.

---

### Domain Behaviors

- **Mob groups minions together**: Maintains collection of minion tokens and associates them with a single mob entity
- **Mob associates with strategy**: Links mob to behavioral rules that determine target selection and action patterns
- **Minion executes actions when mob acts**: All minions in a mob perform the same action when the mob is commanded
- **Token receives click commands**: Token click events trigger mob identification and action execution

---

### Domain Rules

- **Mob must contain at least one minion**: A mob cannot exist without at least one minion. If the last token is removed, the mob entity is deleted.
- **Clicking any token in a mob commands the entire mob**: Any token belonging to a mob can be used to command all minions in that mob.
- **All minions in a mob execute the same action**: When a mob acts, all minions perform the identical action (e.g., all attack the same target).
- **Must work within Foundry VTT's existing systems**: Integration must use Foundry's Token API, Actor System, and Combat System without breaking existing functionality.

---

## Stories (6 total)

### 📝 Select Multiple Tokens

**Acceptance Criteria:**
- **When** Game Master selects multiple minion tokens on Foundry canvas, **then** Foundry Token API returns array of selected token objects
- **When** Game Master selects zero tokens, **then** system shows error message indicating at least one token must be selected
- **When** Game Master selects tokens that already belong to another mob, **then** system identifies conflicting tokens and prompts user for resolution

---

### 📝 Group Tokens Into Mob

**Acceptance Criteria:**
- **When** Game Master selects multiple tokens and initiates mob creation, **then** system creates new Mob entity containing selected tokens
- **When** Mob is created, **then** all tokens in mob are linked to mob entity via Foundry Token API
- **When** tokens are linked to mob, **then** mob entity stores references to all token IDs and actor IDs

---

### 📝 Display Mob Creation Confirmation

**Acceptance Criteria:**
- **When** Mob is successfully created, **then** system displays confirmation dialog showing mob name and token count
- **When** Game Master confirms mob creation, **then** mob is persisted in Foundry actor system
- **When** Game Master cancels mob creation, **then** mob entity is discarded and tokens remain ungrouped

---

### 📝 Click Mob Token To Command

**Acceptance Criteria:**
- **When** Game Master clicks any token belonging to mob, **then** system identifies mob associated with clicked token
- **When** mob is identified, **then** system prepares to execute action for all minions in mob
- **When** clicked token does not belong to any mob, **then** system treats it as individual minion (no mob action)

---

### 📝 Determine Target From Strategy

**Acceptance Criteria:**
- **When** mob action is initiated, **then** system uses mob's assigned strategy to determine target
- **When** mob has no strategy assigned, **then** system uses default strategy (e.g., nearest enemy or first available target)
- **When** target is determined, **then** system selects appropriate enemy based on strategy rules using Foundry combat system

---

### 📝 Execute Attack Action

**Acceptance Criteria:**
- **When** target is determined and attack action is selected, **then** system executes attack for all minions in mob via Foundry combat system
- **When** attack is executed, **then** all minions perform attack action against selected target
- **When** attack completes, **then** system updates combat tracker with results for all minions in mob

---

## Consolidation Decisions

- **No consolidation needed**: Each acceptance criteria represents distinct user-system interactions with different formulas and validation rules
- **Stories remain appropriately sized**: Each story captures a complete back-and-forth (user-system-user) interaction cycle
- **Acceptance criteria follow user-system behavioral pattern**: Each AC focuses on interaction points between Game Master and Foundry VTT system

---

## Domain Rules Referenced

- Mob must contain at least one minion (enforced in Group Tokens Into Mob)
- Clicking any token in a mob commands the entire mob (enforced in Click Mob Token To Command)
- All minions execute the same action (enforced in Execute Attack Action)
- Integration with Foundry VTT systems (enforced across all stories)

---

## Source Material

- Original user input describing mob management needs
- Clarification data from Shape stage (user types, goals, integrations)
- Discovery workflow analysis (mob creation and command flows)
- Story graph with detailed acceptance criteria











