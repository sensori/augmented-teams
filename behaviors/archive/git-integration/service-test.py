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

def test_root():
    """Test root endpoint"""
    url = f"{get_base_url(feature_path)}/"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✅ test_root passed")
    
def test_status():
    """Test status endpoint"""
    url = f"{get_base_url(feature_path)}/status"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "has_changes" in data or "error" in data, f"Expected valid response, got {data}"
    print("✅ test_status passed")


if __name__ == "__main__":
    run_service_tests([
        test_root,
        test_status
    ])

