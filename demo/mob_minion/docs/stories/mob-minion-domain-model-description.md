# Domain Model Description: Mob Minion

**File Name**: `mob-minion-domain-model-description.md`
**Location**: `demo/mob_minion/docs/stories/mob-minion-domain-model-description.md`

## Solution Purpose

Streamline minion management during combat in Foundry VTT for Mutants & Masterminds 3rd Edition. The Mob Minion module allows Game Masters (GMs) to control groups of minions (mobs) with a single interaction instead of clicking each individually, reducing tedious repetitive actions and automating tactical decisions via strategies.

---

## Domain Model Descriptions

### Mob

A **Mob** represents a coordinated group of minions that act together as a single tactical unit during combat. In the business domain of tabletop RPG combat management, a mob serves as the primary organizational container that transforms individual minion tokens into a cohesive fighting force.

**Key Responsibilities:**
- **Groups minions into coordinated unit**: The mob establishes relationships with individual Minion entities, creating a collective that can receive and execute commands as one. When a GM issues an attack command to a mob, all member minions participate in the action simultaneously.
- **Tracks member minions**: The mob maintains awareness of which minions belong to it, their current status, and their positions. This tracking enables the mob to coordinate movement and attacks effectively.

**Business Context:** GMs create mobs to eliminate the need to click on each minion individually during combat. A mob of 6 skeleton minions, for example, can be commanded with one action instead of six separate interactions.

### Minion

A **Minion** represents an individual token/actor in Foundry VTT that can be grouped into mobs for coordinated action. Minions are the fundamental building blocks of mob combat.

**Key Responsibilities:**
- **Individual token/actor in Foundry VTT**: Each minion corresponds to a single token on the virtual tabletop, with its own position, stats, and state.
- **Can belong to one mob**: A minion can be a member of exactly one mob at a time. This constraint ensures clear command hierarchy and prevents conflicting orders.

**Business Context:** In M&M 3e, minions are simplified adversaries that typically act in groups. The Mob Minion module leverages this by allowing multiple minion tokens to be treated as a single mob entity.

### Strategy

A **Strategy** defines the targeting and action algorithm that determines how a mob behaves during combat. Strategies automate the tactical decision-making that a GM would otherwise have to perform manually for each minion.

**Key Responsibilities:**
- **Determines target selection algorithm**: The strategy specifies the logic for choosing which enemy the mob attacks. Examples include "attack strongest target", "attack weakest target", "defend the leader", or "attack most damaged target".
- **Defines mob combat behavior**: Beyond target selection, the strategy may influence how the mob approaches combat, such as whether to prioritize movement or attacking.

**Business Context:** Strategies reduce GM cognitive load by automating tactical decisions. Instead of manually evaluating which target each minion should attack, the GM assigns a strategy and lets the system handle the details.

### Target

A **Target** represents an entity selected for mob attack based on the current strategy. It serves as the output of the strategy's targeting algorithm.

**Key Responsibilities:**
- **Entity selected for mob attack**: The target is the specific actor/token that the mob will focus its coordinated attack upon.

**Business Context:** The target abstraction allows strategies to be implemented without hard-coding specific actor types. Any valid combat target can be selected based on the strategy's criteria.

### MobTemplate

A **MobTemplate** is a reusable blueprint that defines a specific mob configuration including minion types, leader designation, and strategy. Templates enable rapid mob creation during game sessions.

**Key Responsibilities:**
- **Stores reusable mob configuration**: The template captures all the settings needed to recreate a particular type of mob, including which minion types to include and which strategy to apply.
- **Spawns new mob instances**: From a single template, multiple mob instances can be created. This is particularly useful when a GM needs several identical mobs (e.g., six patrol squads of guards).

**Business Context:** Templates support the user journey clarification that GMs should be able to "quickly create a new mob from a template" and "easily create six mobs from a specific mob definition."

---

## Source Material

**Primary Source:** `demo/mob_minion/input.txt`
**Game System:** Mutants & Masterminds 3rd Edition (Hero SRD)
**Platform:** Foundry Virtual Tabletop (Foundry VTT)
**Date Generated:** 2025-12-16
**Context:** Shape phase - Domain model extracted from story-graph.json
