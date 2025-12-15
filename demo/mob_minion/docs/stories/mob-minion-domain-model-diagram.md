# Domain Model Diagram: Mob Minion Management

**File Name**: `mob-minion-domain-model-diagram.md`
**Location**: `demo/mob_minion/docs/stories/mob-minion-domain-model-diagram.md`

## Solution Purpose
Enable Game Masters using Foundry VTT to efficiently manage groups of minions (mobs) that can act together as a single unit. The system allows GMs to create mobs by grouping minion tokens, assign behavioral strategies to mobs, and execute coordinated actions for all minions in a mob with a single click.

---

## Domain Model Diagram

```mermaid
classDiagram
    class Mob {
        +Groups minions together into collection()
        +Maintains collection of minion tokens()
        +Associates with active strategy()
    }
    
    class Minion {
        +Represents individual game entity()
        +Belongs to mob collection()
        +Executes actions when mob acts()
    }
    
    class Token {
        +Represents minion visually on game board()
        +Receives click commands()
    }
    
    class Strategy {
        +Determines target selection behavior()
        +Defines mob action patterns()
    }
    
    class TargetSelection {
        +Determines which enemy to attack based on strategy()
        +Evaluates enemy attributes for strategy matching()
    }
    
    class Action {
        +Executes attack against selected target()
        +Executes movement to reach target()
        +Executes area attack affecting multiple targets()
    }
    
    class MobTemplate {
        +Defines predefined mob configuration()
        +Specifies actor types for mob members()
    }
    
    class Actor {
        +Represents game entity data in Foundry()
        +Spawns tokens on game board()
    }
    
    %% Associations
    Mob --> Minion : contains
    Mob --> Strategy : uses
    Mob --> Action : executes
    Minion --> Token : represented by
    Minion --> Action : participates in
    Strategy --> TargetSelection : determines
    Action --> TargetSelection : uses
    MobTemplate --> Mob : creates
    MobTemplate --> Actor : specifies
    Actor --> Token : spawns
```

**Diagram Notes:**
- Domain concepts are shown as classes with their responsibilities
- Responsibilities are listed as methods in the class (format: +{responsibility}())
- Relationships show dependencies and associations between concepts
- Inheritance relationships show specialization (--|>)
- Associations show usage and collaboration (-->)

---

## Source Material

- Original user input describing the need for mob management in Foundry VTT
- Clarification data capturing user types, goals, and domain concepts
- Story graph defining epics, sub-epics, and stories for mob management functionality


















