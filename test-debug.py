from pathlib import Path
import re

# Read the Python test file
content = Path('behaviors/code-agent/code_agent_runner_test.py').read_text(encoding='utf-8')
lines = content.split('\n')

print(f"Total lines: {len(lines)}\n")

# Check first 100 lines for patterns
for i, line in enumerate(lines[:100], 1):
    if 'with description(' in line or 'with context(' in line or 'with it(' in line:
        print(f"Line {i}: {line[:80]}")
        
        # Try to match
        match = re.search(r"with (?:description|describe|context)\(['\"]([^'\"]+)['\"]", line)
        if match:
            print(f"  MATCHED: {match.group(1)}\n")
        else:
            print(f"  NO MATCH\n")

