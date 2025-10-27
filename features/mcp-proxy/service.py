#!/usr/bin/env python3
"""
MCP Proxy - FastAPI Service
Exposes MCP server functionality as HTTP API for GPT Actions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import yaml
import sys

# Add current directory to path so we can import main
sys.path.insert(0, str(Path(__file__).parent))

import main as mcp_main

# Load configuration
def load_config():
    """Load configuration from feature-config.yaml"""
    config_file = Path(__file__).parent / "config" / "feature-config.yaml"
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# FastAPI service
app = FastAPI(
    title=config['feature']['name'],
    description=config['feature']['description'],
    version=config['feature']['version']
)

class MCPToolCall(BaseModel):
    """MCP Tool call request"""
    tool: str
    input: dict
    service: str = "github"  # Default to github

class MCPToolResponse(BaseModel):
    """MCP Tool call response"""
    success: bool
    result: dict

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "service": config['feature']['name'],
        "version": config['feature']['version']
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}

@app.get("/services")
def list_services():
    """List available MCP services with their tools - helps GPT choose which service to use"""
    return {"services": mcp_main.get_available_services()}

@app.get("/services/{service_name}/tools")
def list_service_tools(service_name: str):
    """List tools available for a specific service"""
    services = mcp_main.get_available_services()
    if service_name not in services:
        raise HTTPException(status_code=404, detail=f"Service not found: {service_name}")
    return {"tools": mcp_main.get_mcp_tools(service_name)}

@app.get("/tools")
def list_tools():
    """List available MCP tools (defaults to github)"""
    return {"tools": mcp_main.get_mcp_tools()}

@app.get("/tools/with-schemas")
def list_tools_with_schemas():
    """List all tools with their full schemas for ChatGPT introspection"""
    return {"tools": mcp_main.list_tools_with_schemas()}

@app.get("/tools/{tool_name}/schema")
def get_tool_schema(tool_name: str):
    """Get schema for a specific tool - enables ChatGPT to understand parameters"""
    schema = mcp_main.get_tool_schema(tool_name)
    if "error" in schema:
        raise HTTPException(status_code=404, detail=schema["error"])
    return schema

@app.post("/call", response_model=MCPToolResponse)
def call_mcp_tool(request: MCPToolCall):
    """Call an MCP tool on a specific service"""
    try:
        result = mcp_main.proxy_mcp_call(request.tool, request.input, request.service)
        if result.get("success"):
            return MCPToolResponse(success=True, result=result)
        else:
            return MCPToolResponse(success=False, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8000)
