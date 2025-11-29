# Story Bot Behavior Structure

All behaviors now follow a consistent structure matching the `1_shape/2_content` pattern:

## Structure Pattern

```
{behavior}/
├── 1_knowledge_graph/ (optional - for prioritization)
│   ├── build_story_graph_{type}.json
│   └── story-graph-{type}.json
├── 2_content/ (for prioritization) OR content/ (for discovery/exploration)
│   ├── 1_knowledge_graph/
│   │   ├── build_story_graph_{type}.json
│   │   └── story-graph-{type}.json
│   ├── 2_render/
│   │   ├── render_{type}_drawio.json
│   │   └── templates/ (optional)
│   └── 3_synchronize/
│       └── synchronize_{type}_drawio.json
└── {other folders like guardrails, rules, etc.}
```

## Behavior-Specific Configurations

### 1_shape
- **Render**: `render-outline` → `story-map-outline.drawio`
- **Sync**: `synchronize` (type: outline)

### 2_prioritization
- **Render**: `render-increments` → `story-map-increments.drawio`
- **Sync**: `synchronize` (type: increments)
- **Path**: `docs/stories/`

### 4_discovery
- **Render**: `render-discovery` → `story-map-discovery-increment-{increment_names}.drawio`
- **Sync**: `sync-discovery` (with increment names)
- **Path**: `docs/stories/`
- **Note**: Supports multiple increments (multiple files possible)

### 5_exploration
- **Render**: `render-exploration` → `story-map-acceptance-criteria-{scope}.drawio`
- **Sync**: `sync-exploration` (with scope)
- **Path**: `docs/stories/`
- **Note**: Supports multiple scopes (multiple files possible)

## CLI Commands

All behaviors use the `story_io` CLI with these commands:

- `render-outline` - Outline rendering
- `render-increments` - Increments rendering
- `render-discovery` - Discovery increment(s) rendering (placeholder)
- `render-exploration` - Exploration acceptance criteria rendering (placeholder)
- `synchronize` or `sync` - Auto-detect sync type
- `sync-outline` - Outline synchronization
- `sync-increments` - Increments synchronization
- `sync-discovery` - Discovery synchronization (placeholder)
- `sync-exploration` - Exploration synchronization (placeholder)

## Naming Patterns

- **Discovery**: `story-map-discovery-increment-{increment_names}.drawio`
  - Example: `story-map-discovery-increment-v1-v2.drawio` (for multiple)
  - Example: `story-map-discovery-increment-v1.drawio` (for single)

- **Exploration**: `story-map-acceptance-criteria-{scope}.drawio`
  - Example: `story-map-acceptance-criteria-increment-v1.drawio`
  - Example: `story-map-acceptance-criteria-feature-auth.drawio`

