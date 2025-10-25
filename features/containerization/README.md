# Common Orchestration Configuration

This directory contains common orchestration files for the containerization feature.

## Files

- `common-deploy.yml` - Common deployment orchestration workflow
- `common-ci.yml` - Common CI/CD workflow
- `environment.yaml` - Shared Azure environment configuration
- `deploy-all.sh` - Script to orchestrate all feature deployments

## Usage

These files should be copied to the appropriate locations when setting up the containerization system:

1. Copy `common-deploy.yml` to `.github/workflows/common-deploy.yml`
2. Copy `common-ci.yml` to `.github/workflows/common-ci.yml`
3. Copy `environment.yaml` to `common/.azure/environment.yaml`
4. Copy `deploy-all.sh` to `common/scripts/deploy-all.sh`

## Domain-Oriented Design Compliance

All common orchestration files are contained within the containerization feature domain, ensuring:
- Feature localization
- Domain boundaries
- Self-contained configuration
- No global dependencies
