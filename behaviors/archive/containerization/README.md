# Common Orchestration Configuration

This directory contains common orchestration files for the containerization feature.

## Files

### Core Components
- `provisioner.py` - Provision and deploy features (CODE, SERVICE, CONTAINER, AZURE modes)
- `inject-config.py` - Generate Dockerfile and Azure config from feature-config.yaml
- `service_test_base.py` - Common test infrastructure
- `generate-service-test.py` - Generate service-test.py from test.py
- `ai-assisted-deploy.py` - **NEW**: AI-powered deployment with automatic error recovery

### Orchestration Scripts
- `common-deploy.yml` - Common deployment orchestration workflow
- `common-ci.yml` - Common CI/CD workflow
- `environment.yaml` - Shared Azure environment configuration
- `deploy-all.sh` - Script to orchestrate all feature deployments

### Documentation
- `docs/feature_deployment_architecture.md` - Architecture overview
- `docs/ai_assisted_delivery_pipeline.md` - AI-assisted deployment workflow

## Usage

These files should be copied to the appropriate locations when setting up the containerization system:

1. Copy `common-deploy.yml` to `.github/workflows/common-deploy.yml`
2. Copy `common-ci.yml` to `.github/workflows/common-ci.yml`
3. Copy `environment.yaml` to `common/.azure/environment.yaml`
4. Copy `deploy-all.sh` to `common/scripts/deploy-all.sh`

## AI-Assisted Deployment

The `ai-assisted-deploy.py` tool combines automated code execution with AI-powered judgment to deploy features with intelligent error recovery.

### Basic Usage

```bash
# Full AI-assisted deployment
python behaviors/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "payment-api" \
  --requirements "Create REST API for payment processing" \
  --mode AZURE

# Skip code regeneration (deploy existing code)
python behaviors/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "existing-feature" \
  --no-regenerate

# Local testing only (CONTAINER mode)
python behaviors/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "test-feature" \
  --mode CONTAINER

# Dry run (preview only)
python behaviors/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "new-feature" \
  --dry-run
```

### Features

- **Test-Driven Development**: AI generates tests first, then code to pass tests
- **Intelligent Error Recovery**: Automatically diagnose and fix common deployment issues
- **Flexible Configuration**: Control code generation, rebuilds, and AI involvement
- **Integration with Provisioner**: Uses existing provisioner infrastructure
- **Git Integration**: AI-generated commit messages with semantic tags
- **Conversational Logging**: Timestamped logs capturing variables, prompts, responses, and outcomes

### Setup

1. **Install Dependencies**:
   ```bash
   pip install openai python-dotenv
   ```

2. **Set OpenAI API Key**:
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Run Deployment**:
   ```bash
   python behaviors/containerization/ai-assisted-deployment/ai-assisted-deploy.py --feature "my-feature"
   ```

### Logging

Each deployment creates a timestamped log file in `behaviors/containerization/logs/`:
- `ai-assisted-deployment-YYYYMMDD-HHMMSS.log`

Logs capture:
- Configuration variables
- Function calls with parameters and results
- AI prompts and responses
- Step outcomes (success/failure)
- Full conversational context for debugging

See `docs/ai_assisted_delivery_pipeline.md` for complete documentation.

## Domain-Oriented Design Compliance

All common orchestration files are contained within the containerization feature domain, ensuring:
- Feature localization
- Domain boundaries
- Self-contained configuration
- No global dependencies
