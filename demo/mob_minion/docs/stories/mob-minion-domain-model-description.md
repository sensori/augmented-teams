# Domain Model Description: Mob Minion Management

**File Name**: `mob-minion-domain-model-description.md`
**Location**: `demo/mob_minion/docs/stories/mob-minion-domain-model-description.md`

## Solution Purpose
Enable Game Masters using Foundry VTT to efficiently manage groups of minions (mobs) that can act together as a single unit. The system allows GMs to create mobs by grouping minion tokens, assign behavioral strategies to mobs, and execute coordinated actions for all minions in a mob with a single click. This eliminates the time-consuming process of individually selecting and commanding each minion token during combat encounters.

---

## Domain Model Descriptions

### Mob
A **Mob** is a collection of minions that act together as a coordinated unit. The mob groups minions together into a single collection and maintains references to all minion tokens that belong to it. Each mob can be associated with an active strategy that determines how the mob selects targets and executes actions. When a Game Master clicks any token belonging to a mob, the entire mob responds as a unified group.

**Key Responsibilities:**
- Groups minions together into collection (collaborates with Minion)
- Maintains collection of minion tokens (collaborates with Token)
- Associates with active strategy (collaborates with Strategy)

**Example:** A Game Master selects five goblin tokens on the Foundry canvas and groups them into a "Goblin Raiding Party" mob. When the GM clicks any one of the goblin tokens, all five goblins perform the same action together.

### Minion
A **Minion** represents an individual game entity within the virtual tabletop system. Each minion belongs to a mob collection and executes actions when the mob acts. Minions are the fundamental building blocks of mobs - they retain their individual game statistics and capabilities while participating in coordinated mob behavior.

**Key Responsibilities:**
- Represents individual game entity
- Belongs to mob collection (collaborates with Mob)
- Executes actions when mob acts (collaborates with Mob and Action)

**Example:** A single goblin warrior is a minion. When it's part of a mob, it still has its own hit points, armor class, and abilities, but it acts in coordination with other minions in the mob.

### Token
A **Token** is the visual representation of a minion on the Foundry VTT game board. Tokens receive click commands from the Game Master and provide the interface for interacting with minions. Each token is linked to a minion and can be part of a mob.

**Key Responsibilities:**
- Represents minion visually on game board (collaborates with Minion)
- Receives click commands

**Example:** When a Game Master clicks a goblin token on the map, the system identifies which minion the token represents and which mob (if any) the minion belongs to.

### Strategy
A **Strategy** defines behavioral rules for how a mob selects targets and executes actions. Strategies determine target selection behavior and define mob action patterns. Common strategies include attacking the most powerful target, attacking the weakest target, defending a leader, or attacking the most damaged enemy.

**Key Responsibilities:**
- Determines target selection behavior (collaborates with Target Selection)
- Defines mob action patterns (collaborates with Mob and Action)

**Example:** A mob assigned the "Attack Weakest Target" strategy will automatically identify and attack the enemy with the lowest power level or hit points when the mob acts.

### Target Selection
**Target Selection** is the process of determining which enemy to attack based on the mob's assigned strategy. It evaluates enemy attributes to match them against the strategy's criteria, such as power level, health, or damage taken.

**Key Responsibilities:**
- Determines which enemy to attack based on strategy (collaborates with Strategy and Enemy)
- Evaluates enemy attributes for strategy matching (collaborates with Enemy and Strategy)

**Example:** When a mob with "Attack Most Powerful Target" strategy acts, the target selection process scans all available enemies, evaluates their power levels, and selects the one with the highest power rating.

### Action
An **Action** represents the execution of a mob's behavior, such as attacking a target, moving to reach a target, or performing an area attack. Actions coordinate the behavior of all minions in a mob to achieve the desired outcome.

**Key Responsibilities:**
- Executes attack against selected target (collaborates with Mob, Target Selection, and Foundry Combat System)
- Executes movement to reach target (collaborates with Mob and Foundry Movement System)
- Executes area attack affecting multiple targets (collaborates with Mob and Foundry Combat System)

**Example:** When a Game Master clicks a mob token and selects "Attack", the action system uses the mob's strategy to determine the target, then executes attacks for all minions in the mob against that target.

### Mob Template
A **Mob Template** defines a predefined mob configuration that can be used to quickly spawn mobs. Templates specify the actor types and counts for mob members, allowing Game Masters to create standardized mob groups without manually selecting tokens.

**Key Responsibilities:**
- Defines predefined mob configuration (collaborates with Mob)
- Specifies actor types for mob members (collaborates with Actor)

**Example:** A "Goblin Raiding Party" template might specify 5 goblin warrior actors. When spawned, it creates 5 tokens from those actors and groups them into a mob.

### Actor
An **Actor** represents game entity data in Foundry VTT. Actors contain the game statistics, abilities, and properties of game entities. They can spawn tokens on the game board and serve as templates for creating minions.

**Key Responsibilities:**
- Represents game entity data in Foundry
- Spawns tokens on game board (collaborates with Token)

**Example:** A "Goblin Warrior" actor contains the goblin's statistics, abilities, and equipment. When used in a mob template, it spawns tokens that represent goblin warriors on the map.

---

## Relationships and Constraints

- **Mob ↔ Minion**: A mob contains multiple minions, and each minion belongs to exactly one mob (or none). This is a one-to-many relationship.

- **Minion ↔ Token**: Each minion has exactly one token representation on the game board. This is a one-to-one relationship.

- **Mob ↔ Strategy**: A mob has exactly one active strategy at a time, but strategies can be changed. This is a many-to-one relationship (many mobs can use the same strategy type).

- **Strategy → Target Selection**: Strategies determine how target selection works. Each strategy type has a specific target selection algorithm.

- **Mob → Action**: Mobs execute actions, and actions coordinate the behavior of all minions in the mob.

- **Mob Template → Actor**: Templates reference actor types to define what minions should be created when spawning a mob.

- **Actor → Token**: Actors spawn tokens when creating minions for a mob.

**Constraints:**
- A mob must contain at least one minion. If the last minion is removed, the mob is deleted.
- A mob can only have one active strategy at a time.
- All minions in a mob execute the same action when the mob acts.
- Tokens must be linked to valid minions and actors in Foundry's system.

---

## Source Material

- Original user input describing the need for mob management in Foundry VTT
- Clarification data capturing user types, goals, and domain concepts
- Story graph defining epics, sub-epics, and stories for mob management functionality

