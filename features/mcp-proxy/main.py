#!/usr/bin/env python3
"""
MCP Proxy - Core Business Logic
Provides MCP server proxy functionality that bridges HTTP to MCP protocol
"""

import requests
import json
import os
import subprocess
from typing import Dict, Any


def inject_default_repo_params(tool_name: str, input_data: dict) -> dict:
    """Inject default owner/repo into input_data if not provided"""
    # Default repository for augmented-teams project
    default_owner = "thomasjeffreyandersontwin"
    default_repo = "augmented-teams"
    
    # Tools that need owner/repo params (actual names from GitHub MCP server)
    repo_required_tools = [
        "get_file_contents", "create_issue", "list_pull_requests",
        "list_commits", "get_commit", "create_branch",
        "push_files", "delete_file", "create_pull_request",
        "update_issue", "add_issue_comment", "update_pull_request",
        "pull_request_read", "get_issue", "list_issues"
    ]
    
    # Don't modify if search_code - it searches across GitHub
    if tool_name == "search_code":
        return input_data
    
    # Inject defaults if owner/repo not provided
    if tool_name in repo_required_tools:
        if "owner" not in input_data:
            input_data["owner"] = default_owner
        if "repo" not in input_data:
            input_data["repo"] = default_repo
    
    return input_data


def proxy_mcp_call(tool_name: str, input_data: dict, mcp_server: str = "github") -> dict:
    """
    Proxy an MCP call - handles both Docker (stdio) and URL (HTTP) protocols
    """
    # Get the GitHub token from environment
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    
    if not github_token:
        return {
            "success": False,
            "error": "GITHUB_PERSONAL_ACCESS_TOKEN not set"
        }
    
    # Get MCP server configuration
    config = get_mcp_server_config(mcp_server)
    if not config:
        return {
            "success": False,
            "error": f"Unknown MCP server: {mcp_server}"
        }
    
    try:
        # Inject default owner/repo parameters if not provided
        input_data = inject_default_repo_params(tool_name, input_data)
        
        # Build the MCP request following the protocol
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": input_data
            }
        }
        
        # Check if Docker protocol or URL protocol
        server_type = config.get("command", "unknown")
        
        if server_type == "docker":
            # Docker stdio protocol (like Cursor does)
            return _call_via_docker(mcp_request, config, github_token, tool_name)
        elif "url" in config:
            # HTTP/URL protocol
            return _call_via_http(mcp_request, config, tool_name)
        else:
            return {
                "success": False,
                "error": f"Unknown server type: {server_type}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call MCP server: {str(e)}"
        }


def _call_via_docker(mcp_request: dict, config: dict, github_token: str, tool_name: str) -> dict:
    """Call MCP server via Docker stdio protocol - uses shared helper"""
    try:
        # Use shared helper to send the request
        response = _send_mcp_request_via_docker(mcp_request, config, timeout=30)
        
        # Check for errors from helper
        if "error" in response:
            return {
                "success": False,
                "error": response["error"],
                "tool": tool_name
            }
        
        if "result" in response:
            return {
                "success": True,
                "tool": tool_name,
                "result": response["result"]
            }
        else:
            return {
                "success": True,
                "tool": tool_name,
                "result": response
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "MCP server call timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Docker call failed: {str(e)}"
        }


def _call_via_http(mcp_request: dict, config: dict, tool_name: str) -> dict:
    """Call MCP server via HTTP/URL protocol"""
    try:
        url = config["url"]
        headers = {"Content-Type": "application/json"}
        
        # Add auth if provided
        if "token" in config:
            headers["Authorization"] = config["token"]
        
        response = requests.post(url, json=mcp_request, headers=headers, timeout=30)
        
        if not response.ok:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "tool": tool_name
            }
        
        result = response.json()
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "tool": tool_name
            }
        
        if "result" in result:
            return {
                "success": True,
                "tool": tool_name,
                "result": result["result"]
            }
        else:
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "HTTP call timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"HTTP call failed: {str(e)}"
        }


def _send_mcp_request_via_docker(mcp_request: dict, config: dict, timeout: int = 10) -> dict:
    """Send any MCP request via Docker stdio protocol - generic helper"""
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    
    docker_cmd = ["docker", "run", "-i", "--rm"]
    for key, value in config.get("env", {}).items():
        if value:
            docker_cmd.extend(["-e", f"{key}={value}"])
    docker_cmd.append(config.get("image", "ghcr.io/github/github-mcp-server"))
    
    process = subprocess.Popen(
        docker_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    request_json = json.dumps(mcp_request) + "\n"
    stdout, stderr = process.communicate(input=request_json, timeout=timeout)
    
    if process.returncode != 0:
        return {"error": f"MCP server error: {stderr}"}
    
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse MCP response: {e}"}


def get_mcp_tools(mcp_server: str = "github") -> list:
    """Get list of available MCP tools - filtered to allowed tools only"""
    config = get_mcp_server_config(mcp_server)
    if not config:
        return []
    
    allowed_tools = config.get("allowed_tools", [])
    
    try:
        # Query MCP server for tools list
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        if config.get("command") == "docker":
            # Call via Docker using shared helper
            response = _send_mcp_request_via_docker(request, config, timeout=10)
            if "result" in response and "tools" in response["result"]:
                actual_tools = [tool["name"] for tool in response["result"]["tools"]]
                # Filter to only return allowed tools
                return [tool for tool in actual_tools if tool in allowed_tools]
    except:
        pass
    
    # Fallback to allowed tools if query fails
    return allowed_tools


# GitHub MCP tool schemas - service-specific
GITHUB_TOOL_SCHEMAS = {
        "search_code": {
            "name": "search_code",
            "description": "Search for code in GitHub repositories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query using GitHub code search syntax"
                    },
                    "sort": {"type": "string", "description": "Sort field"},
                    "order": {"type": "string", "description": "Sort order"},
                    "page": {"type": "number", "description": "Page number for pagination"},
                    "perPage": {"type": "number", "description": "Results per page (1-100)"}
                },
                "required": ["query"]
            }
        },
        "get_file_contents": {
            "name": "get_file_contents",
            "description": "Get contents of a file from a GitHub repository (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "path": {"type": "string", "description": "File path in repository"},
                    "ref": {"type": "string", "description": "Branch, tag, or commit SHA"}
                },
                "required": ["path"]
            }
        },
        "create_issue": {
            "name": "create_issue",
            "description": "Create a new GitHub issue (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body"},
                    "labels": {"type": "array", "description": "Labels to apply"}
                },
                "required": ["title"]
            }
        },
        "list_pull_requests": {
            "name": "list_pull_requests",
            "description": "List pull requests in a repository (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "state": {"type": "string", "description": "Filter by state (open, closed, all)"},
                    "base": {"type": "string", "description": "Filter by base branch"},
                    "head": {"type": "string", "description": "Filter by head branch"}
                },
                "required": []
            }
        },
        "list_commits": {
            "name": "list_commits",
            "description": "List commits in a repository or branch (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "sha": {"type": "string", "description": "Branch or commit SHA"},
                    "author": {"type": "string", "description": "Filter by author"}
                },
                "required": []
            }
        },
        "get_commit": {
            "name": "get_commit",
            "description": "Get details of a specific commit (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "sha": {"type": "string", "description": "Commit SHA"},
                    "include_diff": {"type": "boolean", "description": "Include file diffs in response"}
                },
                "required": ["sha"]
            }
        },
        "create_branch": {
            "name": "create_branch",
            "description": "Create a new branch in a repository (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "branch": {"type": "string", "description": "New branch name"},
                    "from_branch": {"type": "string", "description": "Branch to create from (defaults to default branch)"}
                },
                "required": ["branch"]
            }
        },
        "push_files": {
            "name": "push_files",
            "description": "Push multiple files to a repository in a single commit (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "branch": {"type": "string", "description": "Branch to push to"},
                    "message": {"type": "string", "description": "Commit message"},
                    "files": {
                        "type": "array",
                        "description": "Array of file objects with path and content",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["branch", "files", "message"]
            }
        },
        "delete_file": {
            "name": "delete_file",
            "description": "Delete a file from a repository (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "path": {"type": "string", "description": "Path to file to delete"},
                    "message": {"type": "string", "description": "Commit message"},
                    "branch": {"type": "string", "description": "Branch to delete from"}
                },
                "required": ["path", "message", "branch"]
            }
        },
        "create_pull_request": {
            "name": "create_pull_request",
            "description": "Create a new pull request (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "title": {"type": "string", "description": "PR title"},
                    "body": {"type": "string", "description": "PR description"},
                    "head": {"type": "string", "description": "Branch containing changes"},
                    "base": {"type": "string", "description": "Branch to merge into"},
                    "draft": {"type": "boolean", "description": "Create as draft PR"}
                },
                "required": ["title", "head", "base"]
            }
        },
        "update_issue": {
            "name": "update_issue",
            "description": "Update an existing GitHub issue (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "issue_number": {"type": "number", "description": "Issue number to update"},
                    "title": {"type": "string", "description": "New issue title"},
                    "body": {"type": "string", "description": "New issue body"},
                    "state": {"type": "string", "description": "Issue state (open, closed)"},
                    "labels": {"type": "array", "description": "Labels to apply"}
                },
                "required": ["issue_number"]
            }
        },
        "create_repository": {
            "name": "create_repository",
            "description": "Create a new GitHub repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Repository name"},
                    "description": {"type": "string", "description": "Repository description"},
                    "private": {"type": "boolean", "description": "Make repository private"},
                    "organization": {"type": "string", "description": "Organization to create in (optional)"},
                    "autoInit": {"type": "boolean", "description": "Initialize with README"}
                },
                "required": ["name"]
            }
        }
}


def get_tool_schema(tool_name: str, mcp_server: str = "github") -> dict:
    """Get schema for a specific tool from global schemas registry"""
    if mcp_server == "github":
        schema = GITHUB_TOOL_SCHEMAS.get(tool_name)
        if not schema:
            return {"error": f"Unknown tool: {tool_name} for server: {mcp_server}"}
        return schema
    
    return {"error": f"Unknown MCP server: {mcp_server}"}


def list_tools_with_schemas(mcp_server: str = "github") -> list:
    """List all tools with their schemas for full introspection"""
    tools = get_mcp_tools(mcp_server)
    return [
        get_tool_schema(tool, mcp_server) for tool in tools
    ]


def get_available_services() -> dict:
    """Get list of available MCP services with their configurations"""
    return {
        "github": {
            "name": "github",
            "protocol": "docker",
            "description": "GitHub MCP server for repository operations",
            "image": "ghcr.io/github/github-mcp-server",
            "tools": get_mcp_tools("github")
        }
    }


def get_mcp_server_config(mcp_server: str = "github") -> dict:
    """
    Get configuration for an MCP server - includes allowed tools and schemas
    
    Reads from the mcp.json format to get server config
    """
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    
    config = {
        "github": {
            "command": "docker",
            "image": "ghcr.io/github/github-mcp-server",
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": github_token
            },
            "allowed_tools": [
                "search_code",
                "get_file_contents",
                "create_issue",
                "list_pull_requests",
                "list_commits",
                "get_commit",
                "create_branch",
                "push_files",
                "delete_file",
                "create_pull_request",
                "update_issue",
                "create_repository"
            ]
        }
    }
    return config.get(mcp_server, {})
