# Domain Model Description: Mob Minion

**File Name**: `mob-minion-domain-model-description.md`
**Location**: `demo/mob_minion/mob-minion-domain-model-description.md`

## Solution Purpose
Virtual tabletop game management - specifically minion/mob combat management within Foundry VTT.

---

## Domain Model Descriptions

A **Mob** represents a collection of minions that act together as a single unit. Mobs group minions together and execute actions for all members simultaneously. When a Game Master clicks on any minion in a mob, all minions in that mob perform the same action. Mobs manage their configuration, including which minions belong to the mob and how they behave.

A **Minion** represents an individual game entity or token within the Foundry VTT system. Minions belong to mobs and execute actions when the mob acts. Each minion maintains its own state and properties, but when part of a mob, it follows the mob's strategy and actions.

A **MobTemplate** defines a mob configuration that can be used to spawn multiple mobs with the same setup. Templates specify the mob's composition and can spawn mobs from actor templates or other mob templates, allowing Game Masters to quickly create consistent mob groups.

A **Strategy** determines target selection behavior and defines attack patterns for mobs. Strategies control how mobs behave in combat, including which targets to prioritize (most powerful, weakest, most damaged, fleeing, etc.). Strategies work with Target Selection to identify appropriate targets and with Actions to execute combat behaviors.

**Target Selection** chooses targets based on the current strategy. It identifies the most powerful target, the weakest target, the most damaged target, or fleeing targets depending on the strategy in use. Target Selection collaborates with Strategy to determine which targets are appropriate for the mob's current behavior.

**Actions** execute combat actions for mobs, including attacks, movement, and area attacks. Actions work with Mob and Strategy to coordinate behavior, and with Target Selection to determine who to attack. Actions handle different types of combat: melee attacks, ranged attacks, and area attacks that affect multiple targets.

A **Target** represents a potential attack target in the game. Targets have power levels and threat levels that help determine which targets should be prioritized. Targets are identified through scanning and assessment processes before actions are executed.

**Movement** moves minions to their targets when they are out of range. Movement handles pathfinding around obstacles such as walls and cover, and maximizes distance while staying in range. Movement collaborates with Mob to coordinate minion positioning and with Range to determine if movement is needed.

**Range** determines if movement is needed before attacking. Range calculates the distance to targets and checks if targets are in range for attacks. Range works with Movement to coordinate positioning and with Attack to determine when ranged attacks can be executed.

An **Attack** executes combat attacks for mobs, including melee attacks, ranged attacks, and area attacks. Attacks work with Mob and Target Selection to coordinate combat behavior. Different attack types have different range requirements and target selection criteria.

An **AreaAttack** affects multiple targets simultaneously using area templates. Area attacks work with Attack and Target Selection to identify all targets within the attack area and apply damage or effects to all of them.

---

## Source Material

**Source**: story-graph.json domain_concepts extracted from epics and sub_epics
**Generated**: 2024-12-19
**Context**: Domain concepts identified during story shaping phase for mob minion management system

