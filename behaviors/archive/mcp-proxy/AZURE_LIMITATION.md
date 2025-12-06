# Azure Deployment Limitation

## Issue

The mcp-proxy service requires running Docker commands (`docker run`) to execute the GitHub MCP server. This does NOT work in Azure Container Apps because:

- Azure Container Apps provide an isolated container runtime
- They cannot execute Docker commands from within a container
- No Docker-in-Docker support

## Current Status

- ✅ **Local deployment**: Works (Docker available)
- ✅ **Container deployment**: Works (Docker available in Docker Desktop)
- ❌ **Azure deployment**: Fails (Docker not available)

## Solutions for Azure

### Option 1: Don't Deploy to Azure
- Use mcp-proxy only in environments with Docker (local, VM, etc.)

### Option 2: Separate MCP Server Service
- Deploy the GitHub MCP server as a separate Azure Container App
- Modify mcp-proxy to connect via HTTP/stdio instead of spawning Docker

### Option 3: VM-Based Deployment  
- Deploy to an Azure VM with Docker installed
- Can run Docker commands as needed

## Workaround Applied

The Azure tests currently fail with: "Docker call failed: No such file or directory: 'docker'"

This is expected behavior in Azure Container Apps environment.
