# GitHub MCP Server

This is a standalone deployment of the GitHub MCP server that runs in Docker.

## Purpose

The mcp-proxy service needs to connect to a GitHub MCP server to access GitHub APIs. Instead of running Docker commands (which don't work in Azure), this deploys the MCP server as a separate service.

## Architecture

- **mcp-proxy**: HTTP API that clients call
- **git-mcp**: MCP protocol server that mcp-proxy connects to via stdio
- Both deploy as separate Azure Container Apps

## Setup

The server requires:
- Docker image: `ghcr.io/github/github-mcp-server`
- Environment variable: `GITHUB_PERSONAL_ACCESS_TOKEN`

## Deployment

This will be deployed alongside mcp-proxy, running on the same container environment but as a separate service.
