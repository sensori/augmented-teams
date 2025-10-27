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

@app.get("/tools")
def list_tools():
    """List available MCP tools"""
    return {"tools": mcp_main.get_mcp_tools()}

@app.post("/call", response_model=MCPToolResponse)
def call_mcp_tool(request: MCPToolCall):
    """Call an MCP tool"""
    try:
        result = mcp_main.proxy_mcp_call(request.tool, request.input)
        return MCPToolResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8000)
