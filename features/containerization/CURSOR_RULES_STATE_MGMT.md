# Cursor Rules for State-Managed Delivery Pipeline

Use these prompts in your Cursor rules to interact with the delivery pipeline.

## Quick Commands

### Check Feature Deployment State
```
@delivery-pipeline.py status --feature vector-search
```
**What it does:** Shows current pipeline state, completed steps, failures
**When to use:** Debugging failed deployments, checking progress

### Start/Run Pipeline
```
@delivery-pipeline.py run --feature vector-search --mode AZURE
```
**What it does:** Executes the full deployment pipeline for a feature
**When to use:** Initial deployment, or resume after pause
**Options:**
- `--mode SERVICE` - Local development
- `--mode CONTAINER` - Local Docker
- `--mode AZURE` - Production deployment

### Pause Pipeline (Manual Intervention)
```
@delivery-pipeline.py pause --feature vector-search
```
**What it does:** Pauses pipeline after current step
**When to use:** Need to fix something before next step, inspect logs
**Note:** State saved in `.deployment-state.json`

### Resume Pipeline
```
@delivery-pipeline.py resume --feature vector-search
```
**What it does:** Resumes from last incomplete step
**When to use:** After fixing issues or manual verification

### Clear State (Start Fresh)
```
@delivery-pipeline.py clear --feature vector-search
```
**What it does:** Deletes `.deployment-state.json`, reset pipeline
**When to use:** Testing, debugging state corruption, starting over

## Integration with Provisioner

### Provision Single Feature (Simple)
```
python features/containerization/provisioner.py AZURE features/vector-search --always
```
**What it does:** Direct provision without state management
**When to use:** Quick deploys, no orchestration needed

### Provision with State Tracking
```
python features/containerization/delivery-pipeline.py run --feature vector-search --mode AZURE
```
**What it does:** Full pipeline with state tracking, pause/resume
**When to use:** Production deploys, multi-step workflows

## GitHub Actions Integration

### Workflow Dispatch (Manual Trigger)
In Cursor rules file, add:
```yaml
# Manually trigger deployment for specific feature
deploy_feature:
  prompt: "Deploy {feature_name} to Azure"
  command: |
    python features/containerization/delivery-pipeline.py run \
      --feature {feature_name} \
      --mode AZURE
  examples:
    - "Deploy vector-search to Azure"
    - "Deploy mcp-proxy to production"
```

### Status Check (Before Deployment)
```yaml
check_deployment:
  prompt: "Check deployment status for {feature_name}"
  command: |
    python features/containerization/delivery-pipeline.py status \
      --feature {feature_name} | jq
  examples:
    - "Check vector-search deployment status"
```

## Advanced Workflows

### Conditional Deployment
```python
# Check if feature needs redeployment
@delivery-pipeline.py status --feature vector-search | grep "status"
if status != 'completed':
    # Run deployment
    @delivery-pipeline.py run --feature vector-search
```

### Multi-Feature Deployment
```bash
# Deploy all pending features
for feature in vector-search mcp-proxy git-integration; do
  python features/containerization/delivery-pipeline.py run \
    --feature $feature \
    --mode AZURE
done
```

### Debugging Failed Deployment
```bash
# 1. Check what failed
python features/containerization/delivery-pipeline.py status --feature failing-feature

# 2. Look at state file
cat features/failing-feature/.deployment-state.json

# 3. Fix the issue
# ... make changes ...

# 4. Resume from failure point
python features/containerization/delivery-pipeline.py resume --feature failing-feature
```

## Cursor Rules File Structure

Add this to your `.cursorrules` or `practices.txt`:

```
# === DELIVERY PIPELINE COMMANDS ===

@cmd deploy-feature <feature-name>
python features/containerization/delivery-pipeline.py run --feature <feature-name> --mode AZURE

@cmd check-pipeline <feature-name>  
python features/containerization/delivery-pipeline.py status --feature <feature-name>

@cmd pause-pipeline <feature-name>
python features/containerization/delivery-pipeline.py pause --feature <feature-name>

@cmd resume-pipeline <feature-name>
python features/containerization/delivery-pipeline.py resume --feature <feature-name>

@cmd reset-pipeline <feature-name>
python features/containerization/delivery-pipeline.py clear --feature <feature-name>

# Quick provision without state management
@cmd quick-provision <feature-name>
python features/containerization/provisioner.py AZURE features/<feature-name> --always
```

## Common Patterns

### Pattern 1: Safe Deployment with Rollback Checkpoint
```bash
# 1. Save current state
cp features/mcp-proxy/.deployment-state.json features/mcp-proxy/.deployment-state.json.backup

# 2. Deploy
python features/containerization/delivery-pipeline.py run --feature mcp-proxy

# 3. If failed, restore
cp features/mcp-proxy/.deployment-state.json.backup features/mcp-proxy/.deployment-state.json
```

### Pattern 2: Test Before Deploy
```bash
# Test locally first
python features/containerization/provisioner.py SERVICE features/new-feature
python features/new-feature/service-test.py SERVICE

# Then deploy to Azure
python features/containerization/delivery-pipeline.py run --feature new-feature --mode AZURE
```

### Pattern 3: Dry Run
```bash
# Check what would happen (without deploying)
python features/containerization/delivery-pipeline.py status --feature test-feature
echo "Would deploy: test-feature"
```

## Example Workflow

```bash
# User: I want to deploy vector-search

# AI checks status
python features/containerization/delivery-pipeline.py status --feature vector-search

# Output:
# {"status":"pending","current_step":null,"completed":0,"failed":0}

# AI starts deployment
python features/containerization/delivery-pipeline.py run --feature vector-search --mode AZURE

# Pipeline executes:
# [STEP] Checking feature structure...
# [STEP] Provisioning to Azure...
# Building Docker image...
# Pushing to ACR...
# Deploying to Container Apps...
# [SUCCESS] Pipeline completed

# User: Check status
python features/containerization/delivery-pipeline.py status --feature vector-search

# Output:
# {"status":"completed","current_step":"VERIFY_DEPLOYMENT","completed":7,"failed":0}
```

