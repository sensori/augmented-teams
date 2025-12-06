---
title: Episode Summary Template
description: Template for episode summaries generated from episode content
feature: character
---

# Episode Summary Template

This template defines the structure for episode summaries. Parameters are filled when generating a summary via `/episode summarize`.

```markdown
# Episode {episode-number}: {episode-name}

## Summary

{summary}

## Key Plot Advancement

{key-plot-advancement}

## Detailed Summary

{detailed-summary}

## New NPCs Encountered

{new-npcs}

## Returning Characters

{returning-characters}

## Key Locations

{key-locations}

## Technology/Items

{technology-items}

## Continuity Notes

{continuity-notes}
```

## Template Variables

### Episode Information
- `{episode-number}` - Episode number (sequential, from count of existing episodes)
- `{episode-name}` - Episode name/title (from episode file header)

### Summary Sections
- `{summary}` - Brief summary (2-3 sentences) - Generated from episode content
- `{key-plot-advancement}` - Main plot points - Extracted from episode content
- `{detailed-summary}` - Comprehensive events - Generated from episode content

### Character Context (from character profile)
- `{character-background}` - Character background (from character-profile.mdc → Character Background section)
- `{character-personality}` - Character personality traits (from character-profile.mdc → Personality Traits section)
- `{character-interests}` - Character interests (from character-profile.mdc → Interests section)

### Episode Details
- `{new-npcs}` - New NPCs encountered (with character summaries) - Extracted from episode content
- `{returning-characters}` - Returning characters - Extracted from episode content
- `{key-locations}` - Key locations - Extracted from episode content
- `{technology-items}` - Technology/items - Extracted from episode content
- `{continuity-notes}` - Continuity notes - Generated from episode content

## NPC Character Summary Format

For each new NPC in the `{new-npcs}` section, include:
- **Role/Title**: NPC's role or title
- **Description**: Physical appearance and description
- **Personality**: Key personality traits
- **Relationship**: Relationship to the character
- **Key Actions/Events**: Important actions or events involving this NPC
- **Notes**: Additional important information

Example NPC entry:
```markdown
### Dr. Vile
- **Role/Title**: Mad Scientist
- **Description**: Tall, gaunt figure in a lab coat with wild hair
- **Personality**: Cunning, obsessive, megalomaniacal
- **Relationship**: Antagonist, former colleague
- **Key Actions/Events**: Confronted in lab, escaped after setting traps
- **Notes**: Has knowledge of character's weaknesses
```

## Usage

This template is used when generating episode summaries via `/episode summarize` command. The summary is generated from:
- Episode file content (`current-episode-in-progress.md` or `episode-{N}.md`)
- Character profile context (for understanding character's perspective)

The generated summary is presented to the user for approval. Once approved, it is appended to the character's `plot.md` file Section 4 via `/episode update plot` command.

## Character Context Integration

When generating summaries, the character profile provides context for understanding events from the character's perspective:
- Character background helps understand motivations and reactions
- Personality traits inform how the character would interpret events
- Interests help identify what the character would focus on or remember

This context is used to generate summaries that reflect the character's perspective and understanding of events.

