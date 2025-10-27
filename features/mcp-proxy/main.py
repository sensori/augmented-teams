#!/usr/bin/env python3
"""
MCP Proxy - Core Business Logic
Provides MCP server proxy functionality that bridges HTTP to MCP protocol
"""

import requests
import json
import os
from typing import Dict, Any


def inject_default_repo_params(tool_name: str, input_data: dict) -> dict:
    """Inject default owner/repo into input_data if not provided"""
    # Default repository for augmented-teams project
    default_owner = "thomasjeffreyandersontwin"
    default_repo = "augmented-teams"
    
    # Tools that need owner/repo params
    repo_required_tools = [
        "github_get_file_contents", "github_create_issue", "github_list_pull_requests",
        "github_list_commits", "github_get_commit", "github_create_branch",
        "github_push_files", "github_delete_file", "github_create_pull_request",
        "github_update_issue"
    ]
    
    # Don't modify if search_code - it searches across GitHub
    if tool_name == "github_search_code":
        return input_data
    
    # Inject defaults if owner/repo not provided
    if tool_name in repo_required_tools:
        if "owner" not in input_data:
            input_data["owner"] = default_owner
        if "repo" not in input_data:
            input_data["repo"] = default_repo
    
    return input_data


def proxy_mcp_call(tool_name: str, input_data: dict, mcp_server: str = "github") -> dict:
    

    # Get the GitHub token from environment
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    
    if not github_token:
        return {
            "success": False,
            "error": "GITHUB_PERSONAL_ACCESS_TOKEN not set"
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
        
        # Call external GitHub MCP server
        headers = {
            "Authorization": github_token,  # Already includes "ghp_..." or "Bearer ..."
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.githubcopilot.com/mcp/",
            json=mcp_request,
            headers=headers,
            timeout=30
        )
        
        if not response.ok:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "tool": tool_name
            }
        
        result = response.json()
        
        # Check for errors in response
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "tool": tool_name
            }
        
        # Extract result from MCP response
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
            "error": "MCP server call timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call MCP server: {str(e)}"
        }


def get_mcp_tools(mcp_server: str = "github") -> list:
    """Get list of available MCP tools"""
    # TODO: Query the MCP server via stdio for actual tools
    return [
        "github_search_code",
        "github_get_file_contents",
        "github_create_issue",
        "github_list_pull_requests",
        "github_list_commits",
        "github_get_commit",
        "github_create_branch",
        "github_push_files",
        "github_delete_file",
        "github_create_pull_request",
        "github_update_issue",
        "github_create_repository"
    ]


def get_tool_schema(tool_name: str) -> dict:
    """Get schema for a specific tool - supports ChatGPT introspection"""
    # Tool schemas based on GitHub MCP server documentation
    schemas = {
        "github_search_code": {
            "name": "github_search_code",
            "description": "Search for code in GitHub repositories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query using GitHub code search syntax"
                    },
                    "language": {
                        "type": "string",
                        "description": "Filter by programming language (e.g., 'python', 'javascript')"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Repository owner to search within"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Specific repository to search"
                    }
                },
                "required": ["query"]
            }
        },
        "github_get_file_contents": {
            "name": "github_get_file_contents",
            "description": "Get contents of a file from a GitHub repository (defaults to augmented-teams repo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (defaults to thomasjeffreyandersontwin)"},
                    "repo": {"type": "string", "description": "Repository name (defaults to augmented-teams)"},
                    "path": {"type": "string", "description": "File path in repository"},
                    "ref": {"type": "string", "description": "Branch or commit SHA"}
                },
                "required": ["path"]
            }
        },
        "github_create_issue": {
            "name": "github_create_issue",
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
        "github_list_pull_requests": {
            "name": "github_list_pull_requests",
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
        "github_list_commits": {
            "name": "github_list_commits",
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
        "github_get_commit": {
            "name": "github_get_commit",
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
        "github_create_branch": {
            "name": "github_create_branch",
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
        "github_push_files": {
            "name": "github_push_files",
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
        "github_delete_file": {
            "name": "github_delete_file",
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
        "github_create_pull_request": {
            "name": "github_create_pull_request",
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
        "github_update_issue": {
            "name": "github_update_issue",
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
        "github_create_repository": {
            "name": "github_create_repository",
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
    return schemas.get(tool_name, {"error": f"Unknown tool: {tool_name}"})


def list_tools_with_schemas() -> list:
    """List all tools with their schemas for full introspection"""
    tools = get_mcp_tools()
    return [
        get_tool_schema(tool) for tool in tools
    ]


def get_mcp_server_config(mcp_server: str = "github") -> dict:
    """
    Get configuration for an MCP server
    
    Reads from the mcp.json format to get server config
    """
    config = {
        "github": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "-e",
                f"GITHUB_PERSONAL_ACCESS_TOKEN={os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN', '')}",
                "ghcr.io/github/github-mcp-server"
            ]
        }
    }
    return config.get(mcp_server, {})
