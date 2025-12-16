# Domain Model Diagram: Mob Minion

**File Name**: `mob-minion-domain-model-diagram.md`
**Location**: `demo/mob_minion/docs/stories/mob-minion-domain-model-diagram.md`

## Solution Purpose

Streamline minion management during combat in Foundry VTT for Mutants & Masterminds 3rd Edition. The Mob Minion module allows Game Masters (GMs) to control groups of minions (mobs) with a single interaction instead of clicking each individually.

---

## Domain Model Diagram

```mermaid
classDiagram
    class Mob {
        +groups_minions_into_coordinated_unit()
        +tracks_member_minions()
    }
    
    class Minion {
        +individual_token_actor_in_foundry_vtt()
        +can_belong_to_one_mob()
    }
    
    class Strategy {
        +determines_target_selection_algorithm()
        +defines_mob_combat_behavior()
    }
    
    class Target {
        +entity_selected_for_mob_attack()
    }
    
    class MobTemplate {
        +stores_reusable_mob_configuration()
        +spawns_new_mob_instances()
    }
    
    Mob "1" --> "*" Minion : contains
    Minion "0..1" --> "1" Mob : belongs to
    Strategy --> Target : selects
    Strategy --> Mob : defines behavior for
    MobTemplate --> Mob : spawns
    MobTemplate --> Strategy : configures
```

## Relationship Summary

```mermaid
graph TD
    subgraph "Core Domain"
        Mob[Mob<br/>Groups minions into unit]
        Minion[Minion<br/>Individual token/actor]
        Strategy[Strategy<br/>Target selection algorithm]
        Target[Target<br/>Selected attack target]
    end
    
    subgraph "Template Domain"
        MobTemplate[MobTemplate<br/>Reusable configuration]
    end
    
    Mob -->|contains| Minion
    Minion -->|belongs to| Mob
    Strategy -->|selects| Target
    Strategy -->|defines behavior| Mob
    MobTemplate -->|spawns| Mob
    MobTemplate -->|configures| Strategy
```

## Domain Concepts by Epic

### Epic: Manage Mobs
- **Mob**: Groups minions, tracks members
- **Minion**: Individual token, belongs to mob

### Epic: Configure Strategy
- **Strategy**: Target selection, combat behavior
- **Target**: Selected attack entity

### Epic: Mob Templates
- **MobTemplate**: Stores config, spawns instances

---

## Source Material

**Primary Source:** `demo/mob_minion/input.txt`
**Game System:** Mutants & Masterminds 3rd Edition (Hero SRD)
**Platform:** Foundry Virtual Tabletop (Foundry VTT)
**Date Generated:** 2025-12-16
**Context:** Shape phase - Domain diagram generated from story-graph.json
