with open('agile_bot/bots/base_bot/test/test_gather_context.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
    # Count triple quotes
    triple_quotes = content.count('"""')
    print(f'Total triple quotes: {triple_quotes} (should be even)')
    
    # Check around line 596
    print('\nLines 590-600:')
    for i in range(589, min(600, len(lines))):
        line = lines[i]
        if '"""' in line:
            print(f'Line {i+1}: {repr(line)}')

