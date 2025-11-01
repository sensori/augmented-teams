#!/usr/bin/env python3
"""Quick check if watchers have run."""
from pathlib import Path
import time
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

files = {
    'consistency': '.cursor/watchers/last-run-consistency.txt',
    'structure': '.cursor/watchers/last-run-structure.txt',
    'sync': '.cursor/watchers/last-run-sync.txt'
}

for name, filepath in files.items():
    p = Path(filepath)
    if p.exists():
        timestamp = float(p.read_text())
        age = time.time() - timestamp
        print(f"{name}: OK RAN {age:.1f} seconds ago")
    else:
        print(f"{name}: NOT RUN")

