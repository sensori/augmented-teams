import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from simple_function import get_instructions
    
    result = get_instructions()
    print(f"Function returned: {result}")
    
    # Write to a known location
    output_file = Path(__file__).parent / 'test_result.txt'
    output_file.write_text(str(result))
    print(f"Result written to: {output_file.absolute()}")
    print(f"File exists: {output_file.exists()}")
    if output_file.exists():
        print(f"File content: {output_file.read_text()}")
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)




