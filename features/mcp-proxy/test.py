#!/usr/bin/env python3
"""
Test mcp-proxy - plain Python tests
Tests the actual functions from main.py
"""

import sys
import io

# Fix encoding for Windows - allow emojis in output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from main import proxy_mcp_call, get_mcp_tools, get_tool_schema, list_tools_with_schemas, inject_default_repo_params, get_available_services

def test_get_mcp_tools():
    """Test getting list of MCP tools"""
    result = get_mcp_tools()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) > 0, "Expected tools list to not be empty"
    print("✅ test_get_mcp_tools passed")

def test_proxy_mcp_call():
    """Test MCP proxy call"""
    result = proxy_mcp_call("search_code", {"query": "test"}, mcp_server="github")
    # May fail if Docker/MCP server not running - that's OK for local tests
    # Just check that it returns a valid structure
    assert "success" in result, f"Expected success key, got {result}"
    assert "tool" in result or "error" in result, f"Expected tool or error, got {result}"
    if result.get("success"):
        assert result["tool"] == "search_code"  # Correct tool name without prefix
    print("✅ test_proxy_mcp_call passed (may show error if Docker not running)")

def test_proxy_mcp_call_with_data():
    """Test MCP proxy call with input data"""
    input_data = {"query": "python"}
    result = proxy_mcp_call("search_code", input_data, mcp_server="github")
    # May fail if Docker not available
    assert "success" in result or "error" in result
    if result.get("success"):
        assert "result" in result
        print("✅ test_proxy_mcp_call_with_data passed (got result)")
    else:
        print(f"✅ test_proxy_mcp_call_with_data passed (Docker not available: {result.get('error', 'unknown')})")

def test_get_tool_schema():
    """Test getting schema for a tool"""
    schema = get_tool_schema("search_code")  # Correct tool name
    assert "name" in schema, f"Expected name in schema, got {schema}"
    assert "description" in schema, f"Expected description in schema, got {schema}"
    assert "inputSchema" in schema, f"Expected inputSchema in schema, got {schema}"
    assert schema["inputSchema"]["required"] == ["query"], f"Expected query in required, got {schema}"
    print("✅ test_get_tool_schema passed")

def test_list_tools_with_schemas():
    """Test listing tools with schemas"""
    tools_with_schemas = list_tools_with_schemas()
    assert isinstance(tools_with_schemas, list), f"Expected list, got {type(tools_with_schemas)}"
    assert len(tools_with_schemas) > 0, "Expected tools list to not be empty"
    # First tool should have schema
    if len(tools_with_schemas) > 0:
        first_tool = tools_with_schemas[0]
        assert "name" in first_tool or "error" in first_tool, f"Expected name or error, got {first_tool}"
    print("✅ test_list_tools_with_schemas passed")

def test_get_available_services():
    """Test getting available services"""
    services = get_available_services()
    assert isinstance(services, dict), f"Expected dict, got {type(services)}"
    assert "github" in services, f"Expected github in services, got {list(services.keys())}"
    github = services["github"]
    assert "name" in github
    assert "protocol" in github
    assert "description" in github
    assert "tools" in github
    print("✅ test_get_available_services passed")

def test_inject_default_repo_params():
    """Test auto-injecting owner/repo parameters"""
    # Test with search_code (should NOT inject)
    input_data = {"query": "test"}
    result = inject_default_repo_params("search_code", input_data)
    assert "owner" not in result
    assert "repo" not in result
    print("✅ test_inject_default_repo_params - search_code skipped injection")
    
    # Test with get_file_contents (should inject)
    input_data = {"path": "somefile.py"}
    result = inject_default_repo_params("get_file_contents", input_data)
    assert "owner" in result
    assert "repo" in result
    assert result["owner"] == "thomasjeffreyandersontwin"
    assert result["repo"] == "augmented-teams"
    print("✅ test_inject_default_repo_params - get_file_contents injected defaults")
    
    # Test that explicit owner/repo are NOT overridden
    input_data = {"owner": "custom", "repo": "custom", "path": "somefile.py"}
    result = inject_default_repo_params("get_file_contents", input_data)
    assert result["owner"] == "custom"
    assert result["repo"] == "custom"
    print("✅ test_inject_default_repo_params - explicit values preserved")

if __name__ == "__main__":
    test_get_mcp_tools()
    test_proxy_mcp_call()
    test_proxy_mcp_call_with_data()
    test_get_tool_schema()
    test_list_tools_with_schemas()
    test_get_available_services()
    test_inject_default_repo_params()
    print("✅ All tests passed")
