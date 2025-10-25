# Containerization Architecture Documentation

This file contains the complete architecture documentation for the containerization feature.

## TABLE OF CONTENTS
// 1. CONTAINERIZATION ARCHITECTURE
//   1.1 Feature-First Cloud Architecture
//     1.1.1 Azure Container App deployment model
//     1.1.2 Feature-owned infrastructure pattern
//   1.2 Global Orchestration
//     1.2.1 Repository dispatch coordination
//     1.2.2 CI/CD workflow management
//   1.3 Container Templates
//     1.3.1 Dockerfile standards
//     1.3.2 Azure Container App configurations
//     1.3.3 Feature deployment workflows

# 🧭 Augmented Teams GPT — Feature-First Cloud Architecture Overview

## 🎯 Purpose

This architecture defines how Augmented Teams GPT is deployed to Azure using a feature-owned infrastructure model.
Each feature owns its own container, configuration, and deployment workflow, while a lightweight global orchestrator coordinates releases.

The goal is to ensure:

- **True modularity** — each feature can evolve, deploy, and scale independently
- **Seamless automation** — GitHub Actions handle builds and deployments
- **Full Azure alignment** — each service runs as its own Azure Container App
- **Composable orchestration** — the global layer coordinates, not controls

## 🧱 Design Principles

### Feature-Owned Infrastructure

Each feature defines its own:

- Source code
- Dockerfile
- `.azure/containerapp.yaml`
- GitHub Actions workflows (versioned in feature domain)
- Independent scaling and secrets

### Common Feature Template

All features MUST follow the standardized template based on the proven git integration pattern:

**Required 10 Files per Feature:**

| File | Scope | Location | Naming Convention | Conflict Risk |
|------|-------|----------|-------------------|---------------|
| 1. `main.py` | **LOCAL** | Feature domain only | `main.py` | ✅ No conflict |
| 2. `config/config.yaml` | **LOCAL** | Feature domain only | `config.yaml` | ✅ No conflict |
| 3. `config/Dockerfile` | **LOCAL** | Feature domain only | `Dockerfile` | ✅ No conflict |
| 4. `config/.azure/containerapp.yaml` | **LOCAL** | Feature domain only | `containerapp.yaml` | ✅ No conflict |
| 5. `config/deploy-github-action.yml` | **GLOBAL** | Deployed to `.github/workflows/` | `[feature-name]-deploy.yml` | ⚠️ **MUST prefix** |
| 6. `config/gpt-action.yml` | **GLOBAL** | Manual upload to ChatGPT | `[feature-name]-gpt-action.yml` | ⚠️ **MUST prefix** |
| 7. `config/provision-service.py` | **LOCAL** | Feature domain only (calls shared scripts) | `provision-service.py` | ✅ No conflict |
| 8. `test-service.py` | **LOCAL** | Feature domain only | `test-service.py` | ✅ No conflict |
| 9. `requirements.txt` | **LOCAL** | Feature domain only | `requirements.txt` | ✅ No conflict |
| 10. `config/env-template.txt` | **LOCAL** | Feature domain only | `env-template.txt` | ✅ No conflict |
| 11. `README.md` | **LOCAL** | Feature domain only | `README.md` | ✅ No conflict |

**Shared Scripts (in containerization feature):**
- `inject-config.py` - Configuration injection script
- `provision-service.py` - Core provisioning logic (called by feature scripts)

**Feature Provision Script Pattern:**
- Each feature has a tiny `config/provision-service.py` shell script
- Feature script just calls shared containerization script with feature path
- All provisioning logic is in shared containerization script
- Feature script is just 3-4 lines of code

**Global Deployment Files (Require Feature Prefix):**
- `config/deploy-github-action.yml` → `.github/workflows/[feature-name]-deploy.yml`
- `config/gpt-action.yml` → Manual upload to ChatGPT as `[feature-name]-gpt-action.yml`
- Example: `vector-search-deploy.yml`, `vector-search-gpt-action.yml`

**Local Files (No Prefix Needed):**
- All other files stay within feature domain
- No global deployment conflicts

**Common Scripts Pattern:**
- `config.yaml` - Single source of truth for all configuration values
- `provision-service.py` - Environment validation, dependency installation, service configuration, production readiness check, comprehensive testing
- `test-service.py` - Service health check, core functionality tests, authentication tests, integration tests
- `requirements.txt` - Standard dependencies (FastAPI, uvicorn, pydantic, requests, python-dotenv) plus feature-specific packages

**Shared Configuration Injection:**
- `inject-config.py` - Common script in containerization feature that injects configuration into any feature
- Usage: `python src/features/containerization/inject-config.py src/features/[feature-name]`

**Template Location:** `src/features/containerization/common-feature-template.md`

### GitHub Actions Versioning Strategy

**First-Class Location (Versioned):**
- Workflows are stored in feature domains with descriptive names
- Example: `src/features/vector-search/deploy-github-action.yml`
- Example: `src/features/containerization/common-orchestration-github-action.yml`

**Deployment Location (Runtime):**
- Workflows are copied to `.github/workflows/` during build/deployment
- Renamed to standard GitHub Actions format
- Example: `.github/workflows/deploy.yml`
- Example: `.github/workflows/common-deploy.yml`

**Build Process:**
- Copy workflows from feature domains to `.github/workflows/`
- Rename to remove "-github-action" suffix
- Maintain version control in feature domains

### Common Coordination, Not Control

The common orchestration workflow (`common-deploy.yml`) simply triggers feature-level workflows using `repository_dispatch`.

### Separation of Concerns

- **Common** → CI/CD orchestration and shared settings
- **Feature** → Logic, container, and deployment

### Composable Cloud

Each feature runs as a separate Azure Container App; collectively, they form the "Augmented Teams GPT" system.

## 📂 Directory Structure

```
repo/
├─ .github/
│  ├─ workflows/
│  │  ├─ common-deploy.yml              # orchestrates sub-feature deploys via repository_dispatch
│  │  └─ (optional) common-ci.yml       # common lint/test workflow
├─ features/
│  ├─ git-integration/
│  │  ├─ main.py                      # Main application entry point
│  │  ├─ config/
│  │  │  ├─ config.yaml               # centralized configuration (single source of truth)
│  │  │  ├─ Dockerfile                # generated from config.yaml
│  │  │  ├─ .azure/
│  │  │  │  └─ containerapp.yaml     # generated from config.yaml
│  │  │  ├─ deploy-github-action.yml  # versioned workflow in feature domain
│  │  │  ├─ gpt-action.yml            # GPT Action schema (manual upload to ChatGPT)
│  │  │  ├─ provision-service.py      # calls shared containerization scripts
│  │  │  └─ env-template.txt          # generated from config.yaml
│  │  ├─ test-service.py             # comprehensive test suite
│  │  ├─ requirements.txt             # Python dependencies
│  │  └─ README.md
│  ├─ notion-sync/
│  │  ├─ main.py                      # Main application entry point
│  │  ├─ config/
│  │  │  ├─ config.yaml               # centralized configuration
│  │  │  ├─ Dockerfile                # generated from config.yaml
│  │  │  ├─ .azure/containerapp.yaml # generated from config.yaml
│  │  │  ├─ deploy-github-action.yml  # versioned workflow in feature domain
│  │  │  ├─ gpt-action.yml            # GPT Action schema (manual upload to ChatGPT)
│  │  │  ├─ provision-service.py      # calls shared containerization scripts
│  │  │  └─ env-template.txt          # generated from config.yaml
│  │  ├─ test-service.py             # comprehensive test suite
│  │  ├─ requirements.txt             # Python dependencies
│  │  └─ README.md
│  ├─ vector-search/
│  │  ├─ main.py                      # Main application entry point
│  │  ├─ config/
│  │  │  ├─ config.yaml               # centralized configuration
│  │  │  ├─ Dockerfile                # generated from config.yaml
│  │  │  ├─ .azure/containerapp.yaml # generated from config.yaml
│  │  │  ├─ deploy-github-action.yml  # versioned workflow in feature domain
│  │  │  ├─ gpt-action.yml            # GPT Action schema (manual upload to ChatGPT)
│  │  │  ├─ provision-service.py      # calls shared containerization scripts
│  │  │  └─ env-template.txt          # generated from config.yaml
│  │  ├─ test-service.py             # comprehensive test suite
│  │  ├─ requirements.txt             # Python dependencies
│  │  └─ README.md
│  ├─ core/
│  │  ├─ main.py                      # Main application entry point
│  │  ├─ config/
│  │  │  ├─ config.yaml               # centralized configuration
│  │  │  ├─ Dockerfile                # generated from config.yaml
│  │  │  ├─ .azure/containerapp.yaml # generated from config.yaml
│  │  │  ├─ deploy-github-action.yml  # versioned workflow in feature domain
│  │  │  ├─ gpt-action.yml            # GPT Action schema (manual upload to ChatGPT)
│  │  │  ├─ provision-service.py      # calls shared containerization scripts
│  │  │  └─ env-template.txt          # generated from config.yaml
│  │  ├─ test-service.py             # comprehensive test suite
│  │  ├─ requirements.txt             # Python dependencies
│  │  └─ README.md
│  └─ containerization/
│     ├─ inject-config.py             # shared configuration injection script
│     ├─ provision-service.py         # shared provisioning script (parameterized)
│     ├─ common-orchestration-github-action.yml  # versioned common workflow
│     ├─ common-ci-github-action.yml             # versioned common CI workflow
│     ├─ common-feature-template.md               # standard template for all features
│     ├─ environment.yaml                          # shared Azure environment config
│     └─ deploy-all.sh                            # deployment orchestration script
└─ .github/
   └─ workflows/                      # deployment location (not versioned)
      ├─ vector-search-deploy.yml     # copied from vector-search feature
      ├─ git-integration-deploy.yml   # copied from git-integration feature
      ├─ notion-sync-deploy.yml       # copied from notion-sync feature
      ├─ core-deploy.yml              # copied from core feature
      ├─ common-deploy.yml            # copied from containerization feature
      └─ common-ci.yml                # copied from containerization feature
```

## 🔄 Workflow Deployment Process

### Build-Time Workflow Deployment

During the build process, workflows are deployed from feature domains to `.github/workflows/`:

```bash
# Example build script
#!/bin/bash

echo "🔄 Deploying GitHub Actions workflows..."

# Deploy common orchestration workflows
cp src/features/containerization/common-orchestration-github-action.yml .github/workflows/common-deploy.yml
cp src/features/containerization/common-ci-github-action.yml .github/workflows/common-ci.yml

# Deploy feature-specific workflows with proper naming
for feature_dir in src/features/*/; do
    if [ -d "$feature_dir" ]; then
        feature_name=$(basename "$feature_dir")
        if [ -f "$feature_dir/config/deploy-github-action.yml" ]; then
            # Use feature name prefix to prevent conflicts
            cp "$feature_dir/config/deploy-github-action.yml" ".github/workflows/$feature_name-deploy.yml"
            echo "✅ Deployed workflow for $feature_name as $feature_name-deploy.yml"
        fi
    fi
done

echo "🎉 All workflows deployed successfully!"
```

### Workflow Naming Convention

**Feature Domain (Versioned):**
- `deploy-github-action.yml` - Feature deployment workflow
- `common-orchestration-github-action.yml` - Common orchestration workflow
- `common-ci-github-action.yml` - Common CI workflow

**Deployment Location (Runtime) - WITH FEATURE PREFIX:**
- `[feature-name]-deploy.yml` - Feature deployment workflow (PREVENTS CONFLICTS)
- `common-deploy.yml` - Common orchestration workflow
- `common-ci.yml` - Common CI workflow

**Examples:**
- `src/features/vector-search/config/deploy-github-action.yml` → `.github/workflows/vector-search-deploy.yml`
- `src/features/git-integration/config/deploy-github-action.yml` → `.github/workflows/git-integration-deploy.yml`
- `src/features/notion-sync/config/deploy-github-action.yml` → `.github/workflows/notion-sync-deploy.yml`

### Benefits of This Approach

1. **Version Control** - Workflows are versioned with their features
2. **Domain Isolation** - Each feature owns its workflow logic
3. **Deployment Flexibility** - Workflows can be customized per environment
4. **Maintainability** - Changes to workflows stay with feature code
5. **Auditability** - Workflow changes are tracked with feature changes

## ⚙️ Common Orchestrator (Simplified)

### `.github/workflows/common-deploy.yml`

```yaml
name: Common Deploy Orchestrator
on:
  push:
    branches: [ main ]

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Trigger Git Integration Deployment
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          event-type: deploy-git-integration

      - name: Trigger Notion Sync Deployment
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          event-type: deploy-notion-sync

      - name: Trigger Vector Search Deployment
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          event-type: deploy-vector-search

      - name: Trigger Core Deployment
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          event-type: deploy-core
```

## 🧩 Example Feature Workflow

### `features/git-integration/.github/workflows/deploy.yml`

```yaml
name: Deploy Git Integration Feature
on:
  repository_dispatch:
    types: [deploy-git-integration]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build & Deploy to Azure
        uses: azure/container-apps-deploy-action@v2
        with:
          appSourcePath: features/git-integration
          acrName: augmentedteamacr
          containerAppName: git-integration
          resourceGroup: augmented-team-rg
```

## ✅ Benefits Summary

| Benefit | Description |
|---------|-------------|
| Feature autonomy | Each feature has its own CI/CD and cloud deployment |
| Minimal coupling | Common orchestration doesn't break feature workflows |
| Scalability | Each container scales independently in Azure |
| Auditability | Infra changes live alongside feature code |
| Flexibility | Features can be deployed independently or all together |

## 🎯 TL;DR — One-Sentence Summary

Build an Azure-based, feature-first cloud architecture where each feature owns its own container, deployment config, and GitHub workflow under `/features/<feature>`, while a top-level `common-deploy.yml` orchestrates all feature deploys using `repository_dispatch`.
