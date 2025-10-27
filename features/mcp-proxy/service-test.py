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

# AUTO-COMPLETE ASSERTIONS USING GPT:
# 1. Add OPENAI_API_KEY to environment: export OPENAI_API_KEY="your-key"
# 2. Uncomment the function below
# 3. Run: python service-test.py  # (any mode)
# 4. Copy the generated assertions into the test functions
#
# import openai
# import os
# 
# def complete_with_gpt():
#     with open('test.py', 'r') as f:
#         original = f.read()
#     with open(__file__, 'r') as f:
#         generated = f.read()
#     
#     # Use tools API for structured response
#     tools = [{
#         "type": "function",
#         "function": {
#             "name": "generate_assertions",
#             "description": "Generate assertions for each test function",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "assertions": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "function_name": {"type": "string"},
#                                 "assertion_code": {"type": "string", "description": "Python code for assertions"}
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }]
#     
#     prompt = f"Given original test.py:\n{{original}}\n\nAnd generated service-test:\n{{generated}}\n\nGenerate assertions for each test function."
#     
#     client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         tools=tools,
#         tool_choice={"type": "function", "function": {"name": "generate_assertions"}}
#     )
#     
#     # Parse tool call response
#     if response.choices[0].message.tool_calls:
#         for tool_call in response.choices[0].message.tool_calls:
#             if tool_call.function.name == "generate_assertions":
#                 result = json.loads(tool_call.function.arguments)
#                 for assertion in result['assertions']:
#                     print(f"
# {assertion['function_name']}:")
#                     print(assertion['assertion_code'])
# 
# # Uncomment to run:
# # complete_with_gpt()

def test_list_tools():
    """Test list tools endpoint"""
    url = f"{get_base_url(feature_path)}/tools"
    response = requests.get(url, timeout=30)
    result = response.json()
    assert "tools" in result
    assert isinstance(result["tools"], list)
    print("✅ test_list_tools passed")


def test_call_mcp_tool():
    """Test MCP tool call endpoint"""
    url = f"{get_base_url(feature_path)}/call"
    payload = {
        "tool": "github_search_code",
        "input": {"query": "test"}
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    assert result["success"] == True
    assert "result" in result
    print("✅ test_call_mcp_tool passed")


if __name__ == "__main__":
    run_service_tests([
        test_list_tools,
        test_call_mcp_tool
    ])

