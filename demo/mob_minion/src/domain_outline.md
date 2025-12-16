# Domain Outline: Mob Minion

## Domain Concepts

Mob
    Groups minions into coordinated unit: Minion
    Tracks member minions: Minion

Minion
    Individual token/actor in Foundry VTT: 
    Can belong to one mob: Mob

Strategy
    Determines target selection algorithm: Target
    Defines mob combat behavior: Mob

Target
    Entity selected for mob attack: Strategy

MobTemplate
    Stores reusable mob configuration: Mob, Strategy
    Spawns new mob instances: Mob

## Instructions
- Use clear, concise domain concepts and responsibilities.
- List each responsibility as: {responsibility}: {collaborator},{collaborator},...
- Only include meaningful relationships; avoid unnecessary boilerplate or filler.
- Ensure each domain concept is followed by its set of responsibilities.
