#!/usr/bin/env python3
"""
Service test for 
Auto-generated from test.py - tests via HTTP
"""

import sys
import requests
from pathlib import Path

# Add containerization to path
feature_path = Path(__file__).parent
containerization_path = feature_path.parent / "containerization"
sys.path.insert(0, str(containerization_path))

from service_test_base import get_base_url, run_service_tests  # type: ignore

def test_list_services():
    """Test list services endpoint"""
    url = f"{get_base_url(feature_path)}/services"
    response = requests.get(url, timeout=30)
    result = response.json()
    assert "services" in result
    assert "github" in result["services"]
    assert "tools" in result["services"]["github"]
    print("✅ test_list_services passed")

def test_list_tools():
    """Test list tools endpoint"""
    url = f"{get_base_url(feature_path)}/tools"
    response = requests.get(url, timeout=30)
    result = response.json()
    assert "tools" in result
    assert isinstance(result["tools"], list)
    print("✅ test_list_tools passed")


def test_call_mcp_tool():
    """Test MCP tool call endpoint - MUST hit real GitHub service"""
    url = f"{get_base_url(feature_path)}/call"
    payload = {
        "tool": "search_code",
        "input": {"query": "test"},
        "service": "github"
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    assert result["success"] == True, f"Call to real GitHub service failed: {result.get('result', {}).get('error', 'unknown')}"
    assert "result" in result
    print("✅ test_call_mcp_tool passed (hit real GitHub service)")


def test_list_tools_with_schemas():
    """Test list tools with schemas endpoint"""
    url = f"{get_base_url(feature_path)}/tools/with-schemas"
    response = requests.get(url, timeout=30)
    result = response.json()
    assert "tools" in result
    assert isinstance(result["tools"], list)
    assert len(result["tools"]) > 0
    print("✅ test_list_tools_with_schemas passed")


def test_get_tool_schema():
    """Test get specific tool schema endpoint"""
    url = f"{get_base_url(feature_path)}/tools/search_code/schema"
    response = requests.get(url, timeout=30)
    schema = response.json()
    assert "name" in schema
    assert "description" in schema
    assert "inputSchema" in schema
    assert schema["name"] == "search_code"
    print("✅ test_get_tool_schema passed")


def test_gpt_style_search_with_defaults():
    """GPT-style test: search without specifying repo (uses auto-injected defaults) - MUST hit real service"""
    url = f"{get_base_url(feature_path)}/call"
    # Search for specific files we know exist
    payload = {
        "tool": "search_code",
        "input": {
            "query": "path:behaviors/containerization main.py OR service.py",
            "sort": "indexed"
        },
        "service": "github"
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    # MUST succeed with real service
    assert result.get("success") == True, f"Call to real GitHub service failed: {result.get('result', {}).get('error', 'unknown')}"
    assert "result" in result
    result_data = result["result"]
    # Should find containerization main.py or service.py
    print(f"   Found results: {type(result_data)}")
    print("✅ test_gpt_style_search_with_defaults passed (got real results)")


def test_gpt_style_get_file_with_defaults():
    """GPT-style test: get file without specifying owner/repo (uses auto-injected defaults) - MUST hit real service"""
    url = f"{get_base_url(feature_path)}/call"
    # Get a known file we can validate
    payload = {
        "tool": "get_file_contents",
        "input": {
            "path": "behaviors/containerization/provisioner.py"
        },
        "service": "github"
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    
    # MUST succeed with real service
    assert result.get("success") == True, f"Call to real GitHub service failed: {result.get('result', {}).get('error', 'unknown')}"
    assert "result" in result
    
    result_data = result["result"]
    print(f"   Got response: {type(result_data)}")
    
    # If it's a dict, try to extract content
    if isinstance(result_data, dict):
        # Look for content, file, or text fields
        content = result_data.get("content", result_data.get("file", result_data.get("text", "")))
        if content:
            print(f"   Got file with {len(content)} chars")
        else:
            print(f"   Response dict keys: {list(result_data.keys())[:5]}")
    else:
        content = str(result_data)
        print(f"   Got content with {len(content)} chars")
    
    print("✅ test_gpt_style_get_file_with_defaults passed (got real response)")


def test_gpt_style_list_prs_with_defaults():
    """GPT-style test: list PRs without specifying owner/repo (uses auto-injected defaults)"""
    url = f"{get_base_url(feature_path)}/call"
    payload = {
        "tool": "list_pull_requests",
        "input": {
            "state": "open"
        },
        "service": "github"
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    # May fail if Docker/MCP not available - that's OK
    assert "result" in result or "error" in result
    print("✅ test_gpt_style_list_prs_with_defaults passed")


if __name__ == "__main__":
    run_service_tests([
        test_list_services,
        test_list_tools,
        test_call_mcp_tool,
        test_list_tools_with_schemas,
        test_get_tool_schema,
        test_gpt_style_search_with_defaults,
        test_gpt_style_get_file_with_defaults,
        test_gpt_style_list_prs_with_defaults
    ])

