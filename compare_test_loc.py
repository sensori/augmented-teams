#!/usr/bin/env python3
"""Compare LOC of test files before and after refactoring."""
import subprocess
import os

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

# Test files to compare
test_files = {
    'test_execute_behavior_actions.py': 'agile_bot/bots/base_bot/test/test_execute_behavior_actions.py',
    'test_perform_behavior_action.py': 'agile_bot/bots/base_bot/test/test_perform_behavior_action.py',
    'test_generate_mcp_tools.py': 'agile_bot/bots/base_bot/test/test_generate_mcp_tools.py',
}

commits = {
    'Before Refactor 2': '4fdcfdbf^',
    'Refactor 2': '4fdcfdbf',
    'Refactor 3': '9cc3cc5d',
}

print("=" * 100)
print("TEST FILE LOC COMPARISON: Before First Refactoring vs Now")
print("=" * 100)
print(f"{'File':<40} | {'Before Refactor 2':<18} | {'Refactor 2':<12} | {'Refactor 3':<12} | {'Current':<10} | {'Change'}")
print("-" * 100)

for short_name, filepath in test_files.items():
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
    
    print(f"{short_name:<40} | {before_str:>18} | {ref2_str:>12} | {ref3_str:>12} | {current_str:>10} | {change_str:>6}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

# Calculate totals
total_before_ref2 = 0
total_refactor2 = 0
total_refactor3 = 0
total_current = 0

for short_name, filepath in test_files.items():
    before_ref2 = get_line_count_from_git(commits['Before Refactor 2'], filepath)
    refactor2 = get_line_count_from_git(commits['Refactor 2'], filepath)
    refactor3 = get_line_count_from_git(commits['Refactor 3'], filepath)
    current = get_current_line_count(filepath)
    
    if before_ref2: total_before_ref2 += before_ref2
    if refactor2: total_refactor2 += refactor2
    if refactor3: total_refactor3 += refactor3
    if current: total_current += current

print(f"Total LOC Before Refactor 2: {total_before_ref2 if total_before_ref2 > 0 else 'N/A'}")
print(f"Total LOC After Refactor 2:   {total_refactor2}")
print(f"Total LOC After Refactor 3:   {total_refactor3}")
print(f"Total LOC Current:            {total_current}")
if total_refactor3 > 0 and total_current > 0:
    change = total_current - total_refactor3
    print(f"Change since Refactor 3:      {change:+d} lines ({change/total_refactor3*100:+.1f}%)")
