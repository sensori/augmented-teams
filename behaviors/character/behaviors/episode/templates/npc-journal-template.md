---
title: NPC Journal Template
description: Template for NPC journal files created during character synchronization
feature: character
---

# NPC Journal Template

This template defines the structure for NPC journal files. NPC files are automatically created/updated during character synchronization after episode plot updates.

```markdown
# {npc-name}

## Episode Appearances

- Episode {episode-number}: {episode-name} ({episode-date})

[Add additional episodes as NPC appears in more episodes]

## Character Information

### Role/Title
{role-title}

### Description
{description}

### Personality
{personality}

### Relationship to {character-name}
{relationship}

## Episode-Specific Information

### Episode {episode-number}: {episode-name}

#### Key Actions/Events
{key-actions-events}

#### Notes
{notes}

[Repeat Episode-Specific Information section for each episode where NPC appeared]
```

## Template Variables

### NPC Information (from episode summary)
- `{npc-name}` - NPC name (from "New NPCs Encountered" section)
- `{role-title}` - NPC's role or title
- `{description}` - Physical description and appearance
- `{personality}` - Key personality traits
- `{relationship}` - Relationship to the character

### Episode Information
- `{episode-number}` - Episode number where NPC appeared
- `{episode-name}` - Episode name/title
- `{episode-date}` - Episode date
- `{key-actions-events}` - Important actions or events involving this NPC in this episode
- `{notes}` - Additional important information from this episode

## Usage

This template is used automatically during character synchronization (NPC sync) after `/episode update plot` command:

1. **Extraction**: NPCs are extracted from "New NPCs Encountered" section of approved episode summary
2. **File Creation**: New NPC files are created in `behaviors/character/profiles/{character-name}/episodes/npcs/{npc-name}.md`
3. **File Updates**: Existing NPC files are updated with new episode appearance information

## NPC File Structure

### New NPCs
- Create new file using this template
- Fill in Character Information section
- Add Episode-Specific Information section for first appearance

### Returning NPCs
- Update existing NPC file
- Add new episode to Episode Appearances list
- Add new Episode-Specific Information section for new appearance
- Preserve all previous episode information

## File Location

NPC journal files are stored in:
- `behaviors/character/profiles/{character-name}/episodes/npcs/{npc-name}.md`

## Example

```markdown
# Dr. Vile

## Episode Appearances

- Episode 1: The Rejuvenation Project (2024-01-15)
- Episode 3: The Lab Confrontation (2024-01-22)

## Character Information

### Role/Title
Mad Scientist

### Description
Tall, gaunt figure in a lab coat with wild hair and piercing eyes

### Personality
Cunning, obsessive, megalomaniacal

### Relationship to Roach_Boy
Antagonist, former colleague

## Episode-Specific Information

### Episode 1: The Rejuvenation Project

#### Key Actions/Events
Confronted in lab, escaped after setting traps

#### Notes
Has knowledge of character's weaknesses

### Episode 3: The Lab Confrontation

#### Key Actions/Events
Returned to lab, attempted to steal research data

#### Notes
Revealed connection to Cerion Capital
```

