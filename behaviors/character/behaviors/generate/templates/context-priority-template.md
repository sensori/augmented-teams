---
title: Context Priority Template
description: Template for defining the order in which context files should be consulted
feature: character
---

# Context Priority

This file defines the order in which context files should be consulted when building prompts for character chat.

**Default Priority** (if this file is not present): See `/character-chat-rule` Principle 10 for default priority order and canon source hierarchy.

## Priority Order

List files in order of priority (highest priority first). Use relative paths from the context folder.

**Note:** This priority file only affects ordering WITHIN the canon source hierarchy. The hierarchy itself cannot be overridden:
1. Character Background (from character-profile.mdc) - always first
2. Episode Summaries (from plot.md Section 4) - PRIMARY SOURCE
3. Plot Background (from plot.md Sections 2-3) - SECONDARY SOURCE
4. Other context files (TERTIARY SOURCE) - use this priority file to order them

Example priority order for context files:
1. `episode-summary.md` (or `plot-summary.md`)
2. `world-information.md`
3. `canon-documents.md`
4. `other-context-file.md`

**Canon Hierarchy:** See `/character-chat-rule` Principle 10 for complete canon source hierarchy. Episodes (Section 4) always override plot background (Sections 2-3) when conflicts occur.

