"""
Remove consolidation comments and Args/Returns sections from test file docstrings,
keeping only Given/When/Then descriptions.
"""
import re
from pathlib import Path

def clean_docstring(docstring):
    """Clean a docstring by removing consolidation comments and Args/Returns sections."""
    if not docstring:
        return docstring
    
    lines = docstring.split('\n')
    cleaned_lines = []
    skip_until_next_section = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip consolidation comments
        if 'Consolidates duplicate' in stripped or 'Consolidates duplicates' in stripped:
            skip_until_next_section = True
            continue
        
        # Skip Args: and Returns: sections
        if stripped.startswith('Args:') or stripped.startswith('Returns:'):
            skip_until_next_section = True
            continue
        
        # Stop skipping when we hit a blank line after Args/Returns section
        if skip_until_next_section and stripped == '':
            # Check if next non-empty line is not part of Args/Returns
            next_non_empty = None
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    next_non_empty = lines[j].strip()
                    break
            if next_non_empty and not (next_non_empty.startswith('Args:') or 
                                       next_non_empty.startswith('Returns:') or
                                       'Consolidates' in next_non_empty):
                skip_until_next_section = False
            continue
        
        # Skip lines that are part of Args/Returns (indented parameter descriptions)
        if skip_until_next_section:
            if stripped and (stripped.startswith('-') or ':' in stripped and not stripped.startswith('Given') and not stripped.startswith('When') and not stripped.startswith('Then')):
                continue
            # If we hit a blank line or a new section, stop skipping
            if stripped == '' or stripped.startswith('Given') or stripped.startswith('When') or stripped.startswith('Then'):
                skip_until_next_section = False
        
        cleaned_lines.append(line)
    
    # Join and clean up extra blank lines
    result = '\n'.join(cleaned_lines)
    # Remove trailing blank lines
    result = result.rstrip()
    # Remove multiple consecutive blank lines (keep max 1)
    result = re.sub(r'\n\n\n+', '\n\n', result)
    
    return result

def clean_file(file_path):
    """Clean all docstrings in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match docstrings (triple quotes)
        # This is a simplified approach - we'll match """...""" patterns
        pattern = r'("""(?:[^"\\]|\\.|"(?!"))*""")'
        
        def replace_docstring(match):
            docstring = match.group(1)
            # Remove the quotes temporarily
            inner = docstring[3:-3]
            cleaned = clean_docstring(inner)
            # Return with quotes
            return f'"""{cleaned}"""'
        
        # Replace docstrings
        cleaned_content = re.sub(pattern, replace_docstring, content, flags=re.DOTALL)
        
        # Also handle single-quote docstrings
        pattern_single = r"('''(?:[^'\\]|\\.|'(?!'))*''')"
        def replace_docstring_single(match):
            docstring = match.group(1)
            inner = docstring[3:-3]
            cleaned = clean_docstring(inner)
            return f"'''{cleaned}'''"
        
        cleaned_content = re.sub(pattern_single, replace_docstring_single, cleaned_content, flags=re.DOTALL)
        
        # Only write if content changed
        if cleaned_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    test_dir = Path('agile_bot/bots/base_bot/test')
    cleaned_count = 0
    
    for test_file in test_dir.glob('test_*.py'):
        if clean_file(test_file):
            print(f"Cleaned: {test_file.name}")
            cleaned_count += 1
    
    # Also clean conftest.py
    conftest = test_dir / 'conftest.py'
    if conftest.exists():
        if clean_file(conftest):
            print(f"Cleaned: conftest.py")
            cleaned_count += 1
    
    print(f"\nCleaned {cleaned_count} files")

if __name__ == '__main__':
    main()
