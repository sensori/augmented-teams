#!/usr/bin/env python3
"""Compare ALL test files from 3 commits ago vs now."""
import subprocess
import os
from pathlib import Path

def get_all_test_files_at_commit(commit):
    """Get all test_*.py files at a specific commit."""
    try:
        result = subprocess.run(
            ['git', 'ls-tree', '-r', '--name-only', commit, '--', 'agile_bot/bots/base_bot/test/'],
            capture_output=True,
            text=True,
            check=True
        )
        files = [f for f in result.stdout.strip().split('\n') if f and f.endswith('.py') and 'test_' in f]
        # Extract just the filename
        return sorted([os.path.basename(f) for f in files])
    except subprocess.CalledProcessError:
        return []

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

# Get commits
three_commits_ago = 'HEAD~3'
current = 'HEAD'

print("=" * 120)
print("COMPLETE TEST FILES COMPARISON: 3 Commits Ago vs Now")
print("=" * 120)

# Get all test files at both commits
files_3_ago = get_all_test_files_at_commit(three_commits_ago)
files_current = sorted([f.name for f in Path('agile_bot/bots/base_bot/test').glob('test_*.py')])

# Get commit hash and message
commit_hash = subprocess.run(['git', 'rev-parse', '--short', three_commits_ago], 
                            capture_output=True, text=True).stdout.strip()
commit_msg = subprocess.run(['git', 'log', '-1', '--format=%s', three_commits_ago], 
                           capture_output=True, text=True).stdout.strip()

print(f"\n3 Commits Ago: {commit_hash} - {commit_msg}")
print(f"Current: HEAD\n")

# Combine all files (from both time periods)
all_files = sorted(set(files_3_ago + files_current))

print(f"{'File':<55} | {'3 Commits Ago':<15} | {'Current':<10} | {'Change'}")
print("-" * 120)

results = []
for test_file in all_files:
    filepath = f'agile_bot/bots/base_bot/test/{test_file}'
    
    # Skip story io files
    if 'story' in test_file.lower() and 'io' in test_file.lower():
        continue
    
    loc_3_ago = get_line_count_from_git(three_commits_ago, filepath)
    loc_current = get_current_line_count(filepath)
    
    loc_3_ago_str = str(loc_3_ago) if loc_3_ago is not None else 'N/A (didn\'t exist)'
    loc_current_str = str(loc_current) if loc_current is not None else 'N/A (deleted)'
    
    if loc_3_ago is not None and loc_current is not None:
        change = loc_current - loc_3_ago
        change_str = f"{change:+d}"
    elif loc_3_ago is None and loc_current is not None:
        change_str = f"+{loc_current} (new)"
    elif loc_3_ago is not None and loc_current is None:
        change_str = f"-{loc_3_ago} (deleted)"
    else:
        change_str = "N/A"
    
    print(f"{test_file:<55} | {loc_3_ago_str:>15} | {loc_current_str:>10} | {change_str}")
    
    results.append({
        'file': test_file,
        'loc_3_ago': loc_3_ago,
        'loc_current': loc_current
    })

print("\n" + "=" * 120)
print("SUMMARY")
print("=" * 120)

# Calculate totals
total_3_ago = sum(r['loc_3_ago'] or 0 for r in results)
total_current = sum(r['loc_current'] or 0 for r in results)

print(f"Total LOC 3 Commits Ago: {total_3_ago:,}")
print(f"Total LOC Current:        {total_current:,}")
if total_3_ago > 0:
    change = total_current - total_3_ago
    pct_change = (change / total_3_ago) * 100
    print(f"Net Change:               {change:+,d} lines ({pct_change:+.1f}%)")

print("\n" + "=" * 120)
print("BREAKDOWN")
print("=" * 120)

files_existed_both = [r for r in results if r['loc_3_ago'] is not None and r['loc_current'] is not None]
files_new = [r for r in results if r['loc_3_ago'] is None and r['loc_current'] is not None]
files_deleted = [r for r in results if r['loc_3_ago'] is not None and r['loc_current'] is None]

print(f"\nFiles that existed in both periods: {len(files_existed_both)}")
if files_existed_both:
    total_before = sum(r['loc_3_ago'] for r in files_existed_both)
    total_after = sum(r['loc_current'] for r in files_existed_both)
    change_existing = total_after - total_before
    print(f"  Total LOC before: {total_before:,}")
    print(f"  Total LOC after:  {total_after:,}")
    print(f"  Change:           {change_existing:+,d} lines ({change_existing/total_before*100:+.1f}%)")

print(f"\nNew files: {len(files_new)}")
if files_new:
    total_new = sum(r['loc_current'] for r in files_new)
    print(f"  Total LOC: {total_new:,}")
    for r in files_new:
        print(f"    - {r['file']}: {r['loc_current']} lines")

print(f"\nDeleted files: {len(files_deleted)}")
if files_deleted:
    total_deleted = sum(r['loc_3_ago'] for r in files_deleted)
    print(f"  Total LOC removed: {total_deleted:,}")
    for r in files_deleted:
        print(f"    - {r['file']}: {r['loc_3_ago']} lines")



