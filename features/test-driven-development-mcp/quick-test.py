import sys
from pathlib import Path

print("Current directory:", Path.cwd())
print("Looking for delivery_pipeline.py...")

files = list(Path(".").glob("delivery*.py"))
print("Found files:", [f.name for f in files])

try:
    import delivery_pipeline
    print("SUCCESS: Import works")
except Exception as e:
    print(f"FAILED: {e}")


