Mob
    Groups minions together into collection: Minion
    Maintains collection of minion tokens: Token
    Associates with active strategy: Strategy

Minion
    Represents individual game entity:
    Belongs to mob collection: Mob
    Executes actions when mob acts: Mob,Action

Token
    Represents minion visually on game board: Minion
    Receives click commands:

Strategy
    Determines target selection behavior: Target Selection
    Defines mob action patterns: Mob,Action

Target Selection
    Determines which enemy to attack based on strategy: Strategy,Enemy
    Evaluates enemy attributes for strategy matching: Enemy,Strategy

Action
    Executes attack against selected target: Mob,Target Selection,Foundry Combat System
    Executes movement to reach target: Mob,Foundry Movement System
    Executes area attack affecting multiple targets: Mob,Foundry Combat System

Mob Template
    Defines predefined mob configuration: Mob
    Specifies actor types for mob members: Actor

Actor
    Represents game entity data in Foundry:
    Spawns tokens on game board: Token











