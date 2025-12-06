# Domain Model Description: Mob Minion

**File Name**: `mob-minion-domain-model-description.md`
**Location**: `demo/mob_minion/mob-minion-domain-model-description.md`

## Solution Purpose
Mob Minion is a feature extension for the Foundry Virtual Tabletop system that enables Game Masters to efficiently manage groups of minions (mobs) during combat encounters. The system allows GMs to group minion tokens together so they can be controlled with single actions rather than requiring individual clicks on every minion token. Once grouped into mobs, strategies can be applied to determine how the mob selects targets and performs coordinated actions.

---

## Domain Model Descriptions

### Mob
A Mob represents a collection of minions that act together as a coordinated group. A Mob groups minions together for coordinated actions and maintains a collection of minions that act together. Mobs enable efficient combat management by allowing all minions in the mob to perform the same action when the mob acts. Mobs can be created from selected minion tokens, spawned from multiple actors, or spawned from mob templates.

### Minion
A Minion represents an individual game entity that can be controlled within the Foundry Virtual Tabletop system. A Minion represents an individual game entity that can be controlled and can be grouped into mobs for coordinated actions. Minions are the basic units that make up mobs, and each minion is associated with an Actor and Token in the Foundry system.

### Actor
An Actor represents a game character or creature in the Foundry Virtual Tabletop system. Actors provide the underlying game entity data that minions and tokens are based on. Actors represent game characters/creatures in Foundry system and are the foundation for creating minion tokens.

### Token
A Token provides the visual representation of an actor on the virtual tabletop. Tokens are the visual elements that Game Masters interact with on the tabletop interface. A Token provides visual representation of actor on virtual tabletop and connects Actors to their visual representation in the game space.

### Strategy
A Strategy defines behavioral rules for target selection and actions that determine how a mob selects targets and performs actions. Strategies determine how mob selects targets and performs actions and define behavioral rules for target selection and actions. Examples of strategies include: attack the most powerful target, attack the weakest target, defend the leader, and attack the most damaged target. Strategies can also be based on aggression rules or power effects.

### Target Selection
Target Selection is the process of choosing which entities to attack based on strategy rules. Target Selection chooses which entities to attack based on strategy rules and evaluates available targets based on strategy criteria. The target selection process considers factors such as target power level, health status, damage status, and leader status to determine the appropriate target according to the applied strategy.

---

## Source Material

**Primary Source**: `demo/mob_minion/docs/stories/story-graph.json`
**Sections Referenced**: 
- Epic 1 "Manage Mobs" - domain_concepts section (Mob, Minion, Actor, Token)
- Epic 2 "Apply Strategies to Mobs" - domain_concepts section (Strategy, Target Selection)
**Date Generated**: 2025-12-06
**Context Note**: Domain concepts extracted from story-graph.json epics and sub-epics. All domain concepts represent core business entities in the virtual tabletop combat management domain.
