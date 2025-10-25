# Feature Template

This template provides the standard structure for new features in the Augmented Teams GPT system.

## 📁 Directory Structure

```
src/features/[feature-name]/
├── src/                          # Source code
├── .github/workflows/deploy.yml  # Feature-specific deployment
├── .azure/containerapp.yaml      # Azure Container App config
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
└── README.md                     # Feature documentation
```

## 🚀 Quick Start

1. **Copy this template** to `src/features/[your-feature-name]/`
2. **Update the feature name** in all files
3. **Add your source code** to the `src/` directory
4. **Update dependencies** in `requirements.txt`
5. **Configure Azure settings** in `.azure/containerapp.yaml`
6. **Add deployment trigger** to `.github/workflows/global-deploy.yml`

## 📋 Required Files

### `.github/workflows/deploy.yml`
```yaml
name: Deploy [Feature Name] Feature

on:
  repository_dispatch:
    types: [deploy-[feature-name]]
  workflow_dispatch:

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

      - name: Build & Deploy to Azure Container App
        uses: azure/container-apps-deploy-action@v2
        with:
          appSourcePath: src/features/[feature-name]
          acrName: ${{ secrets.ACR_NAME }}
          containerAppName: [feature-name]
          resourceGroup: ${{ secrets.AZURE_RESOURCE_GROUP }}
```

### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### `.azure/containerapp.yaml`
```yaml
apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: [feature-name]
  namespace: augmented-teams
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: [feature-name]
        feature: [feature-name]
    spec:
      containers:
      - name: [feature-name]
        image: augmentedteamacr.azurecr.io/[feature-name]:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
```

## 🔧 Integration Steps

1. **Add to global orchestrator** (`.github/workflows/global-deploy.yml`):
```yaml
- name: Trigger [Feature Name] Deployment
  uses: peter-evans/repository-dispatch@v3
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    event-type: deploy-[feature-name]
    client-payload: '{"ref": "${{ github.ref }}", "sha": "${{ github.sha }}"}'
```

2. **Update architecture documentation** (`docs/architecture-overview.md`)

3. **Test deployment** using `workflow_dispatch` trigger

## ✅ Checklist

- [ ] Feature follows 5-7 file rule
- [ ] All files are feature-localized
- [ ] Dockerfile builds successfully
- [ ] Azure Container App config is valid
- [ ] Deployment workflow triggers correctly
- [ ] Health checks are implemented
- [ ] README.md documents the feature
- [ ] No cross-feature dependencies
- [ ] Self-contained configuration

## 🎯 Domain-Oriented Design Compliance

This template ensures compliance with:
- **Feature Localization**: Everything stays within the feature folder
- **Domain Boundaries**: Self-contained feature domain
- **5-7 File Rule**: Standard file structure
- **Clear Interfaces**: Clean APIs for cross-feature communication
- **Self-contained**: Independent configuration and deployment

