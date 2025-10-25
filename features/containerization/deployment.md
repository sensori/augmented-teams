# Containerization Deployment Guide

This guide covers the deployment process for the containerization feature.

## Deployment Process

1. **Feature-Level Deployment**
   - Each feature deploys independently
   - Uses Azure Container Apps
   - Managed by GitHub Actions

2. **Common Orchestration**
   - Coordinates multiple feature deployments
   - Uses repository_dispatch events
   - Maintains deployment order

## Common Orchestration Setup

To set up common orchestration:

1. **Copy common files from containerization feature:**
   ```bash
   # Copy common deployment workflow
   cp src/features/containerization/common-deploy.yml .github/workflows/common-deploy.yml
   
   # Copy common CI workflow  
   cp src/features/containerization/common-ci.yml .github/workflows/common-ci.yml
   
   # Copy environment configuration
   cp src/features/containerization/common/environment.yaml common/.azure/environment.yaml
   
   # Copy deployment script
   cp src/features/containerization/common/deploy-all.sh common/scripts/deploy-all.sh
   ```

2. **Configure GitHub Secrets:**
   - `AZURE_CREDENTIALS`
   - `ACR_NAME` 
   - `AZURE_RESOURCE_GROUP`

## Configuration

- Azure Container Registry settings
- Resource group configuration
- Container App scaling settings
- Health check configurations

## Monitoring

- Azure Container App metrics
- GitHub Actions workflow status
- Application health checks
