# Arrange Behavior - Content

This directory contains content generation configurations for the arrange behavior.

## Structure

- `2_render/` - Render configurations and scripts for creating folder structure

## Render Output

The `render_folder_structure` renderer creates the folder hierarchy from `story-graph.json`:

- Epic folders: `🎯 {Epic Name}/`
- Sub-epic folders: `⚙️ {Sub-Epic Name}/`
- Location: `{project_path}/docs/stories/map/`

Follows arrange behavior rules:
- Folder structure matches story graph hierarchy exactly
- Uses emoji prefixes (🎯 for epics, ⚙️ for sub_epics)
- Reads from structured JSON, not markdown
- Archives obsolete folders instead of deleting
