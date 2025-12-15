#!/usr/bin/env python3
"""Compare LOC of ALL test files before and after refactoring."""
import subprocess
import os
from pathlib import Path

def get_line_count_from_git(commit, filepath):
    """Get line count of a file at a specific commit."""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit}:{filepath}'],
            capture_output=True,
            text=True,
            errors='ignore',
            check=True
        )
        return len(result.stdout.splitlines())
    except subprocess.CalledProcessError:
        return None

def get_current_line_count(filepath):
    """Get current line count of a file."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    return None

# Get all test files
test_dir = Path('agile_bot/bots/base_bot/test')
test_files = sorted([f.name for f in test_dir.glob('test_*.py')])

commits = {
    'Before Refactor 2': '4fdcfdbf^',
    'Refactor 2': '4fdcfdbf',
    'Refactor 3': '9cc3cc5d',
}

print("=" * 120)
print("ALL TEST FILES LOC COMPARISON: Before First Refactoring vs Now")
print("=" * 120)
print(f"{'File':<50} | {'Before Refactor 2':<18} | {'Refactor 2':<12} | {'Refactor 3':<12} | {'Current':<10} | {'Change'}")
print("-" * 120)

results = []
for test_file in test_files:
    filepath = f'agile_bot/bots/base_bot/test/{test_file}'
    before_ref2 = get_line_count_from_git(commits['Before Refactor 2'], filepath)
    refactor2 = get_line_count_from_git(commits['Refactor 2'], filepath)
    refactor3 = get_line_count_from_git(commits['Refactor 3'], filepath)
    current = get_current_line_count(filepath)
    
    before_str = str(before_ref2) if before_ref2 is not None else 'N/A'
    ref2_str = str(refactor2) if refactor2 is not None else 'N/A'
    ref3_str = str(refactor3) if refactor3 is not None else 'N/A'
    current_str = str(current) if current is not None else 'N/A'
    
    if refactor3 is not None and current is not None:
        change = current - refactor3
        change_str = f"{change:+d}" if change != 0 else "0"
    else:
        change_str = "N/A"
    
    print(f"{test_file:<50} | {before_str:>18} | {ref2_str:>12} | {ref3_str:>12} | {current_str:>10} | {change_str:>6}")
    
    results.append({
        'file': test_file,
        'before_ref2': before_ref2,
        'refactor2': refactor2,
        'refactor3': refactor3,
        'current': current
    })

print("\n" + "=" * 120)
print("SUMMARY")
print("=" * 120)

# Calculate totals
total_before_ref2 = sum(r['before_ref2'] or 0 for r in results)
total_refactor2 = sum(r['refactor2'] or 0 for r in results)
total_refactor3 = sum(r['refactor3'] or 0 for r in results)
total_current = sum(r['current'] or 0 for r in results)

print(f"Total LOC Before Refactor 2: {total_before_ref2 if total_before_ref2 > 0 else 'N/A'}")
print(f"Total LOC After Refactor 2:   {total_refactor2:,}")
print(f"Total LOC After Refactor 3:   {total_refactor3:,}")
print(f"Total LOC Current:            {total_current:,}")
if total_refactor3 > 0 and total_current > 0:
    change = total_current - total_refactor3
    pct_change = (change / total_refactor3) * 100
    print(f"Change since Refactor 3:      {change:+,d} lines ({pct_change:+.1f}%)")

print("\n" + "=" * 120)
print("FILES THAT EXISTED BEFORE REFACTOR 2")
print("=" * 120)
files_before = [r for r in results if r['before_ref2'] is not None]
if files_before:
    for r in files_before:
        change_from_before = (r['current'] or 0) - (r['before_ref2'] or 0)
        print(f"{r['file']:<50} | Before: {r['before_ref2']:>6} | Current: {r['current']:>6} | Change: {change_from_before:>+7}")
else:
    print("No files existed before Refactor 2")


