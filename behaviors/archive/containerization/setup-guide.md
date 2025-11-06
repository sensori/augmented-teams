# Containerization Feature Setup Guide

This guide explains how to set up and use the containerization feature for Augmented Teams GPT.

## Prerequisites

- Azure CLI installed and configured
- Docker installed
- GitHub Actions secrets configured
- Azure Container Registry (ACR) created

## Setup Steps

1. **Configure Azure Secrets**
   - `AZURE_CREDENTIALS`
   - `ACR_NAME`
   - `AZURE_RESOURCE_GROUP`

2. **Deploy Features**
   - Use `workflow_dispatch` to test individual features
   - Use global deploy for coordinated releases

3. **Monitor Deployments**
   - Check Azure Container Apps in Azure Portal
   - Monitor GitHub Actions workflows

## Troubleshooting

- Check Azure Container App logs
- Verify GitHub Actions workflow status
- Ensure secrets are properly configured

