# Update GPT Instructions from Git Feature

## Overview

This feature manages the automatic updating of GPT instructions from Git repository changes, ensuring that GPT instances always have the latest operating model, style guides, and configuration.

## Architecture Philosophy

🧭 **Principle**: "Instructions flow downstream, not upstream."

- **Git Repository** = Single source of truth
- **GPT Builder** = Cache/default boot config  
- **GPT Runtime** = Active runtime with pull capabilities
- **Write-back** = Disabled by default (explicit only)

## Feature Components

### 1. Bootstrap Configuration
- **File**: `bootstrap-config.json`
- **Purpose**: Auto-refresh configuration for GPT Builder
- **Behavior**: Pulls latest instructions from Git on startup

### 2. GitHub Action Sync
- **File**: `sync-gpt-builder.yml`
- **Purpose**: Automatically sync GPT Builder with Git changes
- **Triggers**: Push to `instructions/**` or `config/**`

### 3. Instruction Flow
- **Mode**: Unidirectional (Git → GPT Builder)
- **Refresh**: Auto-refresh on startup
- **Write-back**: Disabled (explicit only)
- **Audit**: Git commits provide versioned changes

## File Structure

```
src/behaviors/gpt-builder-config/
├── README.md                    # This file
├── bootstrap-config.json        # GPT Builder auto-refresh config
├── sync-gpt-builder.yml        # GitHub Action for syncing
└── docs/                       # Additional documentation
    ├── architecture.md         # Detailed architecture docs
    └── deployment.md           # Deployment instructions
```

## Usage

### Automatic Sync
The system automatically syncs when:
1. Instructions are updated in Git
2. Configuration files change
3. Manual trigger via GitHub Actions

### Manual Sync
```bash
# Trigger manual sync
gh workflow run sync-gpt-builder.yml
```

### Bootstrap Configuration
The GPT Builder reads `bootstrap-config.json` on startup to:
1. Check for auto-refresh settings
2. Pull latest instructions from Git
3. Load runtime operating model
4. Cache instructions for session

## Security Model

- **Immutable by default**: GPT cannot corrupt source of truth
- **Explicit authorship**: Only human-approved changes get versioned
- **Traceable evolution**: Every instruction change in Git history
- **Composable knowledge**: Deterministic behavior (same repo state → same behavior)

## Integration Points

### With Vector Search Feature
- Instructions can reference vector search capabilities
- Search results inform instruction updates
- Both features share Git as source of truth

### With Git Integration
- Uses existing git sync functionality
- Leverages repository as instruction store
- Maintains version control for all changes

## Development Workflow

1. **Update Instructions**: Edit files in `instructions/` folder
2. **Commit Changes**: Standard Git commit process
3. **Auto-Sync**: GitHub Action triggers GPT Builder sync
4. **Runtime Update**: GPT Builder auto-refreshes on next startup

## Configuration Options

### Bootstrap Config Settings
- `auto_refresh.enabled`: Enable/disable auto-refresh
- `instruction_paths`: Which folders to monitor
- `refresh_triggers`: When to refresh (startup, manual, github_action)
- `git_integration.read_only`: Prevent write-back
- `security.immutable_by_default`: Security setting

### GitHub Action Settings
- `paths`: Which file changes trigger sync
- `schedule`: Optional scheduled syncs
- `workflow_dispatch`: Manual trigger capability

## Troubleshooting

### Common Issues
1. **Sync not triggering**: Check file paths in GitHub Action
2. **Instructions not updating**: Verify bootstrap config
3. **Write-back attempts**: Check security settings

### Debug Steps
1. Check GitHub Action logs
2. Verify bootstrap config syntax
3. Test manual sync trigger
4. Review instruction file integrity

## Future Enhancements

- [ ] Webhook integration for real-time sync
- [ ] Instruction validation rules
- [ ] Multi-environment support
- [ ] Advanced caching strategies
- [ ] Instruction diff visualization
