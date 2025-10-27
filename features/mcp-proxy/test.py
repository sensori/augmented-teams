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

from main import proxy_mcp_call, get_mcp_tools

def test_get_mcp_tools():
    """Test getting list of MCP tools"""
    result = get_mcp_tools()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) > 0, "Expected tools list to not be empty"
    print("✅ test_get_mcp_tools passed")

def test_proxy_mcp_call():
    """Test MCP proxy call"""
    result = proxy_mcp_call("github_search_code", {"query": "test"})
    assert result["success"] == True, f"Expected success=True, got {result}"
    assert result["tool"] == "github_search_code", f"Expected tool name, got {result}"
    print("✅ test_proxy_mcp_call passed")

def test_proxy_mcp_call_with_data():
    """Test MCP proxy call with input data"""
    input_data = {"query": "python", "language": "python"}
    result = proxy_mcp_call("github_search_code", input_data)
    assert result["success"] == True
    assert "result" in result
    print("✅ test_proxy_mcp_call_with_data passed")

if __name__ == "__main__":
    test_get_mcp_tools()
    test_proxy_mcp_call()
    test_proxy_mcp_call_with_data()
    print("✅ All tests passed")
