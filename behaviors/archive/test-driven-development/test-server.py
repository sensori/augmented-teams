#!/usr/bin/env python3
"""Test the MCP server locally"""

import json
import subprocess
import sys
from pathlib import Path

# Change to the directory with mcp-server.py
import os
os.chdir(Path(__file__).parent)

# Test requests
test_requests = [
    {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {"protocolVersion": "2024-11-05"}},
    {"jsonrpc": "2.0", "method": "tools/list", "id": 2},
    {"jsonrpc": "2.0", "method": "tools/call", "id": 3, "params": {"name": "get_current_step", "arguments": {"feature_name": "test-feature"}}}
]

# Run the server with test input
input_data = "\n".join(json.dumps(req) for req in test_requests)

result = subprocess.run(
    ["python", "mcp-server.py"],
    input=input_data,
    text=True,
    capture_output=True,
    cwd=os.getcwd()
)

print("=== STDOUT ===")
print(result.stdout)
print("\n=== STDERR ===")
print(result.stderr)
print(f"\n=== EXIT CODE: {result.returncode} ===")
