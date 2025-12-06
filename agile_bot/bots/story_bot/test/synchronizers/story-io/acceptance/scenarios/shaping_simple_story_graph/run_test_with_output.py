"""Run test and capture output to file."""
import sys
import subprocess
from pathlib import Path

test_dir = Path(__file__).parent
test_script = test_dir / "test_render_sync_render_round_trip.py"
log_file = test_dir / "test_output.log"

print(f"Running test: {test_script}")
print(f"Logging output to: {log_file}")

with open(log_file, 'w', encoding='utf-8') as log:
    result = subprocess.run(
        [sys.executable, '-u', str(test_script)],
        cwd=str(test_dir),
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True
    )

# Read and display log
print("\n=== TEST OUTPUT ===")
if log_file.exists():
    with open(log_file, 'r', encoding='utf-8') as f:
        print(f.read())
else:
    print("No log file created")

print(f"\nExit code: {result.returncode}")
sys.exit(result.returncode)





