---
title: Episode Template
description: Template for episode file structure
feature: character
---

# Episode Template

This template defines the structure for episode files. Parameters are filled when creating a new episode via `/episode start`.

```markdown
# Test Episode for MCP Tools



---

**Date**: 2025-11-18
**Character**: Roach-Boy

---

## Episode Content

[Episode content goes here - character interactions, roll results, etc. are automatically appended to this section]

```

## Template Variables

- `Test Episode for MCP Tools` - Episode title (from parameter or default: "Episode {date}")
- `` - Episode description (from parameter or empty)
- `2025-11-18` - Current date (automatically generated)
- `Roach-Boy` - Character name (from parameter or default from CharacterChatAgent)

## Usage

This template is used when creating new episodes via `/episode start` command. The template is copied to `behaviors/character/profiles/Roach-Boy/episodes/current-episode-in-progress.md` with all placeholders filled in.

## Episode Content Format

As character interactions are written to the episode file, they are appended to the "Episode Content" section in chronological order. The format is simple and clean:

- **Original input** (what the character is responding to)
- **Character response** (what the character says/does)

No metadata (timestamps, character name, mode, etc.) is included - just the content. Metadata can be stored elsewhere if needed.

Example episode content entries:
```markdown
## Episode Content

see maa man picking On a bunch of immigrants immediately jumps to their defense

I drop from the fire escape above, roaches cushioning my fall as I land between him and the immigrants. My antennae extend from my shoulders, sensing every movement, and the roaches swarm forward.

"Oh, hey! So, like, you know what's messed up? You. You're messed up. See, roaches are scavengers—we eat what's already dead or dying. But you? You're actively hunting people who are just trying to survive. That makes you worse than a roach!"

Hey i hava america flag i use it as sleeping cover

I'm disgusted and I reach behind me, pulling a filthy, tattered flag out seemingly from my butt, roaches skittering off it as it unfurls.

"Oh, hey! So you've got a gross flag? Cool, cool. I've got one too! See, roaches can survive on almost anything—cardboard, hair, even flags that've been... places. But at least mine's honest about being gross. Yours is just trying too hard!"
```

