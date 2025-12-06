# Domain Model Diagram: Mob Minion

**File Name**: `mob-minion-domain-model-diagram.md`
**Location**: `demo/mob_minion/mob-minion-domain-model-diagram.md`

## Solution Purpose
Virtual tabletop game management - specifically minion/mob combat management within Foundry VTT.

---

## Domain Model Diagram

```mermaid
classDiagram
    class Mob {
        +Groups minions together()
        +Executes actions for all members()
        +Manages mob configuration()
    }
    
    class Minion {
        +Represents individual game entity()
        +Belongs to mob()
        +Executes actions when mob acts()
    }
    
    class MobTemplate {
        +Defines mob configuration()
        +Spawns mobs from templates()
    }
    
    class Strategy {
        +Determines target selection behavior()
        +Defines attack patterns()
        +Controls mob behavior()
    }
    
    class TargetSelection {
        +Chooses targets based on strategy()
        +Identifies most powerful target()
        +Identifies weakest target()
        +Identifies most damaged target()
        +Identifies fleeing targets()
    }
    
    class Actions {
        +Executes combat actions()
        +Performs attacks()
        +Handles movement()
    }
    
    class Target {
        +Represents potential attack target()
        +Has power level()
        +Has threat level()
    }
    
    class Movement {
        +Moves minions to target()
        +Handles pathfinding around obstacles()
        +Maximizes distance in range()
    }
    
    class Range {
        +Determines if movement is needed()
        +Calculates distance to target()
        +Checks if target is in range()
    }
    
    class Attack {
        +Executes melee attacks()
        +Executes ranged attacks()
        +Executes area attacks()
    }
    
    class AreaAttack {
        +Affects multiple targets()
        +Uses area templates()
    }
    
    %% Associations
    Mob --> Minion : contains
    Mob --> Strategy : uses
    Mob --> Actions : executes
    MobTemplate --> Mob : spawns
    MobTemplate --> Minion : spawns
    Strategy --> TargetSelection : determines
    Strategy --> Actions : defines
    Strategy --> Mob : controls
    TargetSelection --> Strategy : based on
    Actions --> Mob : executes for
    Actions --> Strategy : coordinates with
    Actions --> TargetSelection : performs
    Actions --> Range : handles
    Target --> TargetSelection : identified by
    Movement --> Mob : moves
    Movement --> Range : coordinates with
    Range --> Movement : determines need for
    Attack --> Mob : executes for
    Attack --> TargetSelection : uses
    Attack --> Range : checks
    AreaAttack --> Attack : extends
    AreaAttack --> TargetSelection : affects
```

**Example:**
```mermaid
classDiagram
    class Payment {
        +Validates card number()
        +Authorizes transaction()
        +Processes payment()
    }
    
    class Order {
        +Creates order()
        +Calculates total()
        +Updates status()
    }
    
    Order --> Payment : processes
```

**Diagram Notes:**
- Domain concepts are shown as classes with their responsibilities
- Responsibilities are listed as methods in the class (format: +{responsibility}())
- Relationships show dependencies and associations between concepts
- Inheritance relationships show specialization (--|>)
- Associations show usage and collaboration (-->)

---

## Source Material

**Source**: story-graph.json domain_concepts extracted from epics and sub_epics
**Generated**: 2024-12-19
**Context**: Domain concepts identified during story shaping phase for mob minion management system

