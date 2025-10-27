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

from service_test_base import get_base_url, run_service_tests

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

def test_hello_world():
    """Test hello function"""
    url = f"{get_base_url(feature_path)}/hello"
    response = requests.get(url, params={"name": "World"}, timeout=5)
    result = response.json()["message"]
    assert result == "Hello World!", f"Expected 'Hello World!', got '{result}'"
    print("✅ test_hello_world passed")


def test_hello_custom():
    """Test hello with custom name"""
    url = f"{get_base_url(feature_path)}/hello"
    response = requests.get(url, params={"name": "Alice"}, timeout=5)
    result = response.json()["message"]
    assert result == "Hello Alice!", f"Expected 'Hello Alice!', got '{result}'"
    print("✅ test_hello_custom passed")


def test_add_numbers():
    """Test add_numbers function"""
    url = f"{get_base_url(feature_path)}/add"
    response = requests.get(url, params={"a": 2, "b": 3}, timeout=5)
    result = response.json()["result"]
    assert result == 5, f"Expected 5, got {result}"
    print("✅ test_add_numbers passed")


def test_goodbye():
    """Test goodbye function"""
    url = f"{get_base_url(feature_path)}/goodbye"
    response = requests.get(url, params={"param": "World"}, timeout=5)
    result = response.json()["message"]
    assert result == "Goodbye World!", f"Expected 'Goodbye World!', got '{result}'"
    print("✅ test_goodbye passed")


if __name__ == "__main__":
    run_service_tests([
        test_hello_world,
        test_hello_custom,
        test_add_numbers,
        test_goodbye
    ])

