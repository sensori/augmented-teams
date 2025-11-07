import sys
from pathlib import Path
import importlib.util

# Import bdd-runner.py (hyphenated name requires importlib)
_runner_path = Path("behaviors/bdd/bdd-runner.py")
_spec = importlib.util.spec_from_file_location("bdd_runner", _runner_path)
_bdd_runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bdd_runner)

extract_test_structure_chunks = _bdd_runner.extract_test_structure_chunks

test_file = 'behaviors/code-agent/code_agent_runner_test.py'
framework = 'mamba'

chunks = extract_test_structure_chunks(test_file, framework)
print(f"Chunks returned: {len(chunks)}")
for i, chunk in enumerate(chunks[:3]):
    print(f"\nChunk {i+1}:")
    print(f"  Start line: {chunk.get('start_line')}")
    print(f"  End line: {chunk.get('end_line')}")
    structure = chunk.get('structure', '')
    print(f"  Structure length: {len(structure)}")
    print(f"  First 200 chars: {structure[:200]}")

