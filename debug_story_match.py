import re
from pathlib import Path

def normalize_name(name):
    """Normalize names for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

story_name = "Invoke Bot CLI"
story_normalized = normalize_name(story_name)
print(f"Story: {story_name}")
print(f"Story normalized: {story_normalized}")

test_dir = Path('agile_bot/bots/base_bot/test')

best_file_match = None
best_file_score = 0

for test_file in test_dir.glob('test_*.py'):
    if test_file.name.endswith('_helpers.py'):
        continue
    file_base = test_file.stem.replace('test_', '')
    file_base_normalized = normalize_name(file_base)
    
    print(f"\nChecking: {test_file.name}")
    print(f"  file_base: {file_base}")
    print(f"  file_base_normalized: {file_base_normalized}")
    
    # Calculate match score: longer common substring = better match
    if story_normalized in file_base_normalized:
        score = len(story_normalized) / len(file_base_normalized) if file_base_normalized else 0
        print(f"  story in file: score = {score}")
    elif file_base_normalized in story_normalized:
        score = len(file_base_normalized) / len(story_normalized) if story_normalized else 0
        print(f"  file in story: score = {score}")
    else:
        score = 0
        print(f"  no match: score = {score}")
    
    if score > best_file_score:
        best_file_score = score
        best_file_match = test_file.name
        print(f"  -> NEW BEST MATCH!")

print(f"\nBest file match: {best_file_match}")
print(f"Best score: {best_file_score}")
