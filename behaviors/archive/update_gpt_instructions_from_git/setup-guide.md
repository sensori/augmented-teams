# GPT Builder Setup Guide

## Overview

This guide walks you through setting up a real GPT Builder instance and connecting it to your Augmented Teams repository for automated instruction sync.

## Prerequisites

- OpenAI account with GPT Builder access
- GitHub repository with the Augmented Teams code
- GitHub Actions enabled
- OpenAI API key

## Step 1: Create GPT Builder Instance

### 1.1 Access GPT Builder
1. Go to [OpenAI GPT Builder](https://chat.openai.com/gpts)
2. Click "Create a GPT"
3. Choose "Create" (not "Configure")

### 1.2 Basic Configuration
1. **Name**: `Augmented Teams`
2. **Description**: `AI-powered team collaboration and knowledge management system`
3. **Instructions**: Leave blank initially (we'll sync from Git)

### 1.3 Connect Repository
1. In the GPT Builder interface, scroll down to "Connected Repository"
2. Click "Connect Repository"
3. Select your GitHub repository: `augmented-teams`
4. Grant necessary permissions

## Step 2: Configure GitHub Secrets

### 2.1 Add OpenAI API Key
1. Go to your repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Add new secret:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key

### 2.2 Verify Secrets
Ensure these secrets exist:
- `OPENAI_API_KEY` - Your OpenAI API key
- `API_KEY` - For vector search (if different)

## Step 3: Test the Integration

### 3.1 Manual Test
1. Make a small change to `instructions/OPERATING_MODEL.md`
2. Commit and push the change
3. Check GitHub Actions tab for "Sync GPT Builder Instructions" workflow
4. Verify the workflow runs successfully

### 3.2 Verify Sync
1. Go back to your GPT Builder instance
2. Check if the instructions have been updated
3. Test the GPT with a simple query

## Step 4: Configure Bootstrap Config

### 4.1 Update Config Path
The startup script expects `config/bootstrap-config.json`, but we moved it to `src/behaviors/gpt-builder-config/`. Update the path:

```bash
# Copy config to expected location
cp src/behaviors/gpt-builder-config/bootstrap-config.json config/
```

### 4.2 Test Startup Script
```bash
# Test the startup script
cd src/behaviors/gpt-builder-config
python startup.py --config ../../config/bootstrap-config.json
```

## Step 5: Complete Workflow Test

### 5.1 Test Full Cycle
1. **Edit**: Make changes to instruction files
2. **Commit**: Commit and push changes
3. **Sync**: GitHub Action triggers GPT Builder sync
4. **Verify**: Check GPT Builder has updated instructions
5. **Test**: Use the GPT to verify it's working

### 5.2 Test Startup Script
1. **Run**: Execute startup script
2. **Check**: Verify it pulls latest Git changes
3. **Validate**: Ensure all instruction files are present
4. **Summary**: Check runtime summary is generated

## Troubleshooting

### Common Issues

#### GitHub Action Fails
- Check `OPENAI_API_KEY` secret is set
- Verify repository permissions
- Check workflow file syntax

#### GPT Builder Not Updating
- Verify repository connection in GPT Builder
- Check if `triggerGitSync` action is working
- Review GitHub Action logs

#### Startup Script Errors
- Verify bootstrap config JSON syntax
- Check file paths are correct
- Ensure Git repository is accessible

### Debug Steps
1. Check GitHub Action logs
2. Verify GPT Builder connection
3. Test startup script manually
4. Review configuration files

## Advanced Configuration

### Custom Instruction Paths
Edit `bootstrap-config.json` to include additional paths:

```json
{
  "auto_refresh": {
    "instruction_paths": [
      "instructions/",
      "config/",
      "src/behaviors/gpt-builder-config/"
    ]
  }
}
```

### Scheduled Sync
The workflow includes a weekly sync schedule. Modify in `sync-gpt-builder.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Weekly on Mondays at 9 AM
```

### Multiple GPT Instances
You can connect multiple GPT instances to the same repository by:
1. Creating additional GPT Builder instances
2. Connecting each to the same repository
3. Each will sync independently

## Security Considerations

### API Key Security
- Never commit API keys to Git
- Use GitHub Secrets for all sensitive data
- Rotate keys regularly

### Repository Access
- Limit GPT Builder permissions to necessary actions
- Review connected repository settings
- Monitor sync activity

### Instruction Validation
- The workflow validates all instruction files
- Integrity checks prevent corrupted updates
- Audit trail through Git commits

## Next Steps

Once setup is complete:

1. **Test the complete workflow** with real instruction changes
2. **Monitor sync performance** and adjust as needed
3. **Add additional instruction files** as your system grows
4. **Integrate with other features** like vector search
5. **Scale to multiple GPT instances** if needed

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Action logs
3. Verify GPT Builder connection
4. Test components individually
5. Check configuration file syntax
