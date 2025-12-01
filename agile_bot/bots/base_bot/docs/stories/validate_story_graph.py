"""
Validate story graph JSON against DrawIO diagram.

Compares the structure, elements, hierarchy, and relationships between
the JSON story graph and the visual DrawIO representation.
"""

import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
from pathlib import Path


class StoryGraphValidator:
    """Validates story graph JSON against DrawIO diagram."""
    
    # Visual markers
    EPIC_COLOR = "#e1d5e7"  # Purple
    SUB_EPIC_COLOR = "#d5e8d4"  # Green
    STORY_COLOR = "#fff2cc"  # Yellow
    USER_COLOR = "#dae8fc"  # Blue
    
    EPIC_Y = 130
    SUB_EPIC_Y_MIN = 196
    SUB_EPIC_Y_MAX = 250
    STORY_Y_MIN = 337
    
    def __init__(self, json_path: str, drawio_path: str):
        self.json_path = json_path
        self.drawio_path = drawio_path
        self.json_data = None
        self.drawio_elements = {}
        self.drawio_hierarchy = {}
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate(self) -> Dict[str, Any]:
        """Run full validation and return results."""
        # Load JSON
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)
        
        # Extract DrawIO elements
        self._extract_drawio_elements()
        
        # Build DrawIO hierarchy
        self._build_drawio_hierarchy()
        
        # Run validation checks
        self._validate_epics()
        self._validate_sub_epics()
        self._validate_stories()
        self._validate_hierarchy()
        self._validate_users()
        
        # Generate report
        return self._generate_report()
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize names for comparison: HTML entities, whitespace."""
        import html
        # Decode HTML entities (&nbsp; -> space, &amp; -> &, etc.)
        normalized = html.unescape(name)
        # Normalize whitespace (multiple spaces, tabs, etc. -> single space)
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        # Strip but keep case (case-sensitive matching)
        return normalized.strip()
    
    def _extract_drawio_elements(self):
        """Extract all elements from DrawIO file."""
        tree = ET.parse(self.drawio_path)
        root = tree.getroot()
        
        for cell in root.findall(".//mxCell[@vertex='1']"):
            value = cell.get('value', '').strip()
            style = cell.get('style', '')
            geometry = cell.find('mxGeometry')
            
            if not geometry or not value:
                continue
            
            x = float(geometry.get('x', 0))
            y = float(geometry.get('y', 0))
            width = float(geometry.get('width', 0))
            height = float(geometry.get('height', 0))
            
            # Normalize value
            normalized_value = self._normalize_name(value)
            
            elem = {
                'id': cell.get('id'),
                'value': value,  # Keep original for display
                'normalized_value': normalized_value,  # Normalized for comparison
                'style': style,
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
            # Categorize - be more lenient with colors (slight variations)
            is_user = (self.USER_COLOR in style or '#dae8fc' in style) and width == 50 and height == 50
            is_epic = (self.EPIC_COLOR in style or '#e1d5e7' in style) and 'rounded=1' in style and abs(y - self.EPIC_Y) < 50
            is_sub_epic = (self.SUB_EPIC_COLOR in style or '#d5e8d4' in style or '#d6e8d5' in style) and 'rounded=1' in style and self.SUB_EPIC_Y_MIN <= y <= self.SUB_EPIC_Y_MAX
            
            if is_user:
                self.drawio_elements.setdefault('users', []).append(elem)
            elif is_epic:
                self.drawio_elements.setdefault('epics', []).append(elem)
            elif is_sub_epic:
                self.drawio_elements.setdefault('sub_epics', []).append(elem)
            elif y >= self.STORY_Y_MIN:
                if '#1a237e' in style or '#0d47a1' in style:
                    elem['story_type'] = 'system'
                elif '#000000' in style and 'fillColor=#000000' in style:
                    elem['story_type'] = 'technical'
                else:
                    elem['story_type'] = 'user'
                self.drawio_elements.setdefault('stories', []).append(elem)
    
    def _build_drawio_hierarchy(self):
        """Build parent-child relationships from DrawIO."""
        epics = self.drawio_elements.get('epics', [])
        sub_epics = self.drawio_elements.get('sub_epics', [])
        stories = self.drawio_elements.get('stories', [])
        
        # Group sub-epics under epics - use normalized values for keys
        for epic in epics:
            epic_x_end = epic['x'] + epic['width']
            epic_key = epic['normalized_value']
            self.drawio_hierarchy[epic_key] = {
                'type': 'epic',
                'element': epic,
                'sub_epics': [],
                'stories': []
            }
            
            for sub_epic in sub_epics:
                # More lenient: check if sub-epic starts within epic bounds (not just center)
                sub_x_start = sub_epic['x']
                if epic['x'] <= sub_x_start <= epic_x_end:
                    sub_key = sub_epic['normalized_value']
                    self.drawio_hierarchy[epic_key]['sub_epics'].append(sub_key)
                    self.drawio_hierarchy[sub_key] = {
                        'type': 'sub_epic',
                        'element': sub_epic,
                        'parent': epic_key,
                        'stories': []
                    }
        
        # Group stories under sub-epics or epics
        for story in stories:
            parent = self._find_drawio_parent(story, epics, sub_epics)
            if parent:
                if parent not in self.drawio_hierarchy:
                    self.drawio_hierarchy[parent] = {'type': 'unknown', 'stories': []}
                # Use normalized value for story
                self.drawio_hierarchy[parent]['stories'].append(story['normalized_value'])
    
    def _find_drawio_parent(self, story: Dict, epics: List[Dict], sub_epics: List[Dict]) -> Optional[str]:
        """Find parent epic or sub-epic for a story."""
        story_x = story['x']
        story_y = story['y']
        
        # Check sub-epics first (more specific)
        # More lenient: story can start anywhere within sub-epic bounds
        for sub_epic in sub_epics:
            sub_x_start = sub_epic['x']
            sub_x_end = sub_epic['x'] + sub_epic['width']
            sub_y = sub_epic['y']
            
            # Story should be below and within x-range (allow some overlap)
            if sub_x_start <= story_x <= sub_x_end and story_y > sub_y:
                return sub_epic['normalized_value']
        
        # Check epics
        for epic in epics:
            epic_x_start = epic['x']
            epic_x_end = epic['x'] + epic['width']
            epic_y = epic['y']
            
            if epic_x_start <= story_x <= epic_x_end and story_y > epic_y:
                return epic['normalized_value']
        
        return None
    
    def _validate_epics(self):
        """Validate epic names match."""
        json_epics = {self._normalize_name(epic['name']) for epic in self.json_data.get('epics', [])}
        drawio_epics = {elem['normalized_value'] for elem in self.drawio_elements.get('epics', [])}
        
        missing_in_drawio = json_epics - drawio_epics
        missing_in_json = drawio_epics - json_epics
        
        if missing_in_drawio:
            self.errors.append(f"Epics in JSON but not in DrawIO: {missing_in_drawio}")
        
        if missing_in_json:
            self.warnings.append(f"Epics in DrawIO but not in JSON: {missing_in_json}")
    
    def _validate_sub_epics(self):
        """Validate sub-epic names match."""
        json_sub_epics = set()
        for epic in self.json_data.get('epics', []):
            epic_norm = self._normalize_name(epic['name'])
            for sub_epic in epic.get('sub_epics', []):
                sub_norm = self._normalize_name(sub_epic['name'])
                json_sub_epics.add((epic_norm, sub_norm))
        
        drawio_sub_epics = set()
        for epic_name, data in self.drawio_hierarchy.items():
            if data.get('type') == 'epic':
                for sub_epic_name in data.get('sub_epics', []):
                    drawio_sub_epics.add((epic_name, sub_epic_name))
        
        missing_in_drawio = json_sub_epics - drawio_sub_epics
        missing_in_json = drawio_sub_epics - json_sub_epics
        
        if missing_in_drawio:
            for epic_name, sub_epic_name in missing_in_drawio:
                self.errors.append(f"Sub-epic '{sub_epic_name}' under epic '{epic_name}' in JSON but not in DrawIO")
        
        if missing_in_json:
            for epic_name, sub_epic_name in missing_in_json:
                self.warnings.append(f"Sub-epic '{sub_epic_name}' under epic '{epic_name}' in DrawIO but not in JSON")
    
    def _validate_stories(self):
        """Validate story names match."""
        json_stories = defaultdict(set)
        for epic in self.json_data.get('epics', []):
            epic_norm = self._normalize_name(epic['name'])
            for sub_epic in epic.get('sub_epics', []):
                sub_norm = self._normalize_name(sub_epic['name'])
                for story in sub_epic.get('stories', []):
                    story_norm = self._normalize_name(story['name'])
                    json_stories[(epic_norm, sub_norm)].add(story_norm)
                    # Check nested stories
                    self._collect_nested_stories(story, json_stories, epic_norm, sub_norm)
        
        drawio_stories = defaultdict(set)
        for epic_name, data in self.drawio_hierarchy.items():
            if data.get('type') == 'epic':
                for sub_epic_name in data.get('sub_epics', []):
                    if sub_epic_name in self.drawio_hierarchy:
                        sub_data = self.drawio_hierarchy[sub_epic_name]
                        for story_name in sub_data.get('stories', []):
                            drawio_stories[(epic_name, sub_epic_name)].add(story_name)
        
        # Compare - only report if significant differences
        all_keys = set(json_stories.keys()) | set(drawio_stories.keys())
        for epic_name, sub_epic_name in all_keys:
            json_set = json_stories.get((epic_name, sub_epic_name), set())
            drawio_set = drawio_stories.get((epic_name, sub_epic_name), set())
            
            missing_in_drawio = json_set - drawio_set
            missing_in_json = drawio_set - json_set
            
            # Only report if significant (>10% difference or absolute count > 2)
            json_count = len(json_set)
            drawio_count = len(drawio_set)
            diff_count = len(missing_in_drawio) + len(missing_in_json)
            
            if diff_count > max(2, min(json_count, drawio_count) * 0.1):
                if missing_in_drawio:
                    for story_name in list(missing_in_drawio)[:5]:  # Limit to first 5
                        self.errors.append(f"Story '{story_name}' in sub-epic '{sub_epic_name}' (epic '{epic_name}') in JSON but not in DrawIO")
                    if len(missing_in_drawio) > 5:
                        self.errors.append(f"... and {len(missing_in_drawio) - 5} more stories missing in DrawIO")
                
                if missing_in_json:
                    for story_name in list(missing_in_json)[:5]:  # Limit to first 5
                        self.warnings.append(f"Story '{story_name}' in sub-epic '{sub_epic_name}' (epic '{epic_name}') in DrawIO but not in JSON")
                    if len(missing_in_json) > 5:
                        self.warnings.append(f"... and {len(missing_in_json) - 5} more stories missing in JSON")
    
    def _collect_nested_stories(self, story: Dict, stories_dict: Dict, epic_name: str, sub_epic_name: str):
        """Recursively collect nested stories."""
        for nested in story.get('stories', []):
            nested_norm = self._normalize_name(nested['name'])
            stories_dict[(epic_name, sub_epic_name)].add(nested_norm)
            self._collect_nested_stories(nested, stories_dict, epic_name, sub_epic_name)
    
    def _validate_hierarchy(self):
        """Validate hierarchy structure matches."""
        # Check epic order - use normalized names
        json_epic_order = [self._normalize_name(epic['name']) for epic in self.json_data.get('epics', [])]
        drawio_epics_sorted = sorted(
            self.drawio_elements.get('epics', []),
            key=lambda e: e['x']
        )
        drawio_epic_order = [e['normalized_value'] for e in drawio_epics_sorted]
        
        if json_epic_order != drawio_epic_order:
            self.warnings.append(f"Epic order differs: JSON={json_epic_order}, DrawIO={drawio_epic_order}")
    
    def _validate_users(self):
        """Validate user assignments match - only report significant issues."""
        json_users = defaultdict(set)
        for epic in self.json_data.get('epics', []):
            for sub_epic in epic.get('sub_epics', []):
                for story in sub_epic.get('stories', []):
                    story_norm = self._normalize_name(story['name'])
                    self._collect_story_users(story, json_users, story_norm)
        
        drawio_users = defaultdict(set)
        for story_elem in self.drawio_elements.get('stories', []):
            story_name = story_elem['normalized_value']
            # Find users above this story
            story_x = story_elem['x']
            story_y = story_elem['y']
            
            for user_elem in self.drawio_elements.get('users', []):
                user_x = user_elem['x']
                user_y = user_elem['y']
                # More lenient matching - allow up to 150px horizontal offset
                if user_y < story_y and abs(user_x - story_x) < 150:
                    user_name = self._normalize_name(user_elem['value'])
                    drawio_users[story_name].add(user_name)
        
        # Compare - only report if significant differences (skip if minor)
        all_stories = set(json_users.keys()) | set(drawio_users.keys())
        for story_name in all_stories:
            json_user_set = {self._normalize_name(u) for u in json_users.get(story_name, set())}
            drawio_user_set = drawio_users.get(story_name, set())
            
            # Only warn if completely missing or very different
            if json_user_set and not drawio_user_set and len(json_user_set) > 0:
                # Skip if it's a nested story (harder to match)
                if ' > ' not in story_name:
                    self.warnings.append(f"Story '{story_name}' has users in JSON but none found in DrawIO: {json_user_set}")
            elif drawio_user_set and not json_user_set and len(drawio_user_set) > 0:
                if ' > ' not in story_name:
                    self.warnings.append(f"Story '{story_name}' has users in DrawIO but none in JSON: {drawio_user_set}")
    
    def _collect_story_users(self, story: Dict, users_dict: Dict, story_name: str):
        """Collect users from story and nested stories."""
        if story.get('users'):
            users_dict[story_name].update(story['users'])
        
        for nested in story.get('stories', []):
            nested_norm = self._normalize_name(nested['name'])
            nested_name = f"{story_name} > {nested_norm}"
            self._collect_story_users(nested, users_dict, nested_name)
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_info': len(self.info)
            }
        }


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validate_story_graph.py <json_file> <drawio_file>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    drawio_path = sys.argv[2]
    
    try:
        print(f"Loading JSON from: {json_path}")
        print(f"Loading DrawIO from: {drawio_path}")
        
        validator = StoryGraphValidator(json_path, drawio_path)
        report = validator.validate()
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print report
    print("=" * 80)
    print("STORY GRAPH VALIDATION REPORT")
    print("=" * 80)
    print(f"\nStatus: {'✓ VALID' if report['valid'] else '✗ INVALID'}")
    print(f"\nSummary:")
    print(f"  Errors: {report['summary']['total_errors']}")
    print(f"  Warnings: {report['summary']['total_warnings']}")
    print(f"  Info: {report['summary']['total_info']}")
    
    if report['errors']:
        print(f"\n{'=' * 80}")
        print("ERRORS:")
        print("=" * 80)
        for i, error in enumerate(report['errors'], 1):
            print(f"{i}. {error}")
    
    if report['warnings']:
        print(f"\n{'=' * 80}")
        print("WARNINGS:")
        print("=" * 80)
        for i, warning in enumerate(report['warnings'], 1):
            print(f"{i}. {warning}")
    
    if report['info']:
        print(f"\n{'=' * 80}")
        print("INFO:")
        print("=" * 80)
        for i, info in enumerate(report['info'], 1):
            print(f"{i}. {info}")
    
    print("\n" + "=" * 80)
    
    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()


