#!/usr/bin/env python3
"""
Generate service-test.py from test.py
Analyzes test functions and generates HTTP calls
"""

import re
import ast
from pathlib import Path

def analyze_test_file(test_file):
    """Analyze test.py to extract function calls and parameters"""
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse AST
    tree = ast.parse(content)
    
    test_info = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            # Extract calls to functions from main module
            calls = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        func_name = child.func.id
                        # Get arguments
                        args = []
                        for arg in child.args:
                            if isinstance(arg, (ast.Constant, ast.Str)):
                                args.append(f'"{arg.value if hasattr(arg, "value") else arg.s}"')
                            elif isinstance(arg, (ast.Num, ast.Str)):
                                args.append(f'"{arg.n if hasattr(arg, "n") else arg.s}"')
                        calls.append({
                            'func': func_name,
                            'args': args
                        })
            
            test_info.append({
                'name': node.name,
                'doc': ast.get_docstring(node) or f"Test {node.name}",
                'calls': calls
            })
    
    return test_info

def infer_endpoint_name(func_name):
    """Convert function name to endpoint name"""
    # If it's "add_numbers", endpoint is probably "/add"
    if 'add' in func_name.lower():
        return '/add'
    elif 'hello' in func_name.lower():
        return '/hello'
    # Default: use function name as endpoint
    return f'/{func_name.replace("test_", "")}'

def generate_service_test(feature_path, test_functions):
    """Generate service-test.py content"""
    
    header = '''#!/usr/bin/env python3
"""
Service test for {feature_name}
Auto-generated from test.py - tests via HTTP
"""

import sys
import requests
from pathlib import Path

# Add containerization to path
feature_path = Path(__file__).parent
containerization_path = feature_path.parent.parent / "containerization"
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
#     prompt = f"Given original test.py:\\n{{original}}\\n\\nAnd generated service-test:\\n{{generated}}\\n\\nGenerate assertions for each test function."
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
#                     print(f"\n# {assertion['function_name']}:")
#                     print(assertion['assertion_code'])
# 
# # Uncomment to run:
# # complete_with_gpt()

'''
    
    # Generate each test function
    test_stubs = []
    
    for test_info in test_functions:
        func_name = test_info['name']
        doc = test_info['doc']
        
        # Try to infer endpoint and params from calls
        endpoint = '/endpoint'  # default
        params = {}
        
        if test_info['calls']:
            # Take first call as reference
            call = test_info['calls'][0]
            if call['args']:
                # Infer endpoint from function name
                endpoint = infer_endpoint_name(call['func'])
                
                # Try to infer params
                if call['args']:
                    if 'hello' in func_name.lower() and call['args']:
                        params = {'name': call['args'][0]} if call['args'] else {}
                    elif 'add' in func_name.lower() and len(call['args']) >= 2:
                        params = {'a': '2', 'b': '3'}
        
        # Generate test function
        test_func = f'''def {func_name}():
    """{doc}"""
    url = f"{{get_base_url(feature_path)}}{endpoint}"
'''
        
        if params:
            # Format params as dict
            params_dict = '{' + ', '.join([f'"{k}": {v}' for k, v in params.items()]) + '}'
            test_func += f'    response = requests.get(url, params={params_dict}, timeout=5)\n'
        else:
            test_func += '    response = requests.get(url, timeout=5)\n'
        
        test_func += '''    # TODO: Add assertions based on expected response
    # result = response.json()["field"]
    # assert result == expected, f"Expected 'expected', got '{result}'"
    print("TODO: Implement assertions")
    pass

'''
        
        test_stubs.append(test_func)
    
    # Generate test list for main block
    test_names = [f"        {tf['name']}" for tf in test_functions]
    
    # Main block
    main_block = f'''
if __name__ == "__main__":
    run_service_tests([
{',\n'.join(test_names)}
    ])

'''
    
    # Format header - replace feature_name but keep GPT template intact
    content = header.replace('{feature_name}', feature_path.name)
    content += '\n'.join(test_stubs)
    content += main_block
    
    return content

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('feature_path', type=Path)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    
    feature_path = Path(args.feature_path)
    test_file = feature_path / 'test.py'
    service_test_file = feature_path / 'service-test.py'
    
    if not test_file.exists():
        print(f"test.py not found in {feature_path}")
        return 1
    
    # Check if regeneration needed
    if not args.force and service_test_file.exists():
        test_mtime = test_file.stat().st_mtime
        service_test_mtime = service_test_file.stat().st_mtime
        if test_mtime <= service_test_mtime:
            print(f"service-test.py is up to date")
            return 0
    
    print(f"Generating service-test.py from test.py...")
    
    # Analyze test functions
    test_info = analyze_test_file(test_file)
    
    if not test_info:
        print(f"No test_* functions found in test.py")
        return 1
    
    # Generate service-test.py
    content = generate_service_test(feature_path, test_info)
    
    # Write file
    with open(service_test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated {service_test_file} with {len(test_info)} test function(s)")
    print(f"TODO: Review and implement assertions for each test")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
