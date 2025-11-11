import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from behaviors.bdd.bdd_runner import BDDScaffoldKeywordHeuristic, BDDScaffoldStateOrientedHeuristic
from behaviors.common_command_runner.common_command_runner import Content

c = Content('behaviors/stories/docs/stories_runner_test-hierarchy.txt')
c._ensure_content_loaded()
print(f'Content loaded: {len(c._content_lines)} lines')
print(f'Line 13: {repr(c._content_lines[12])}')
print(f'Line 14: {repr(c._content_lines[13])}')

h1 = BDDScaffoldKeywordHeuristic()
v1 = h1.detect_violations(c)
print(f'\nKeyword violations: {len(v1) if v1 else 0}')
if v1:
    print('  First 5:')
    for v in v1[:5]:
        print(f'    Line {v.line_number}: {v.message}')

h2 = BDDScaffoldStateOrientedHeuristic()
v2 = h2.detect_violations(c)
print(f'\nState-oriented violations: {len(v2) if v2 else 0}')
if v2:
    print('  First 5:')
    for v in v2[:5]:
        print(f'    Line {v.line_number}: {v.message}')

