"""
Reverse parser: Extract story graph JSON from DrawIO diagram.

This script parses a DrawIO XML file and reconstructs the story graph JSON structure
based on visual positioning and styling rules.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import json


class DrawIOToStoryGraph:
    """Converts DrawIO diagram back to story graph JSON."""
    
    # Visual markers from construction rules
    EPIC_COLOR = "#e1d5e7"  # Purple
    SUB_EPIC_COLOR = "#d5e8d4"  # Green
    STORY_COLOR = "#fff2cc"  # Yellow
    USER_COLOR = "#dae8fc"  # Blue
    
    # Y-position thresholds (approximate)
    EPIC_Y = 130
    SUB_EPIC_Y_MIN = 196
    SUB_EPIC_Y_MAX = 250
    STORY_Y_MIN = 337
    
    def __init__(self, drawio_path: str):
        self.drawio_path = drawio_path
        self.tree = ET.parse(drawio_path)
        self.root = self.tree.getroot()
        self.elements = []
        self.users = []
        self.epics = []
        self.sub_epics = []
        self.stories = []
        
    def parse(self) -> Dict[str, Any]:
        """Parse DrawIO file and return story graph JSON."""
        # Extract all mxCell elements
        self._extract_elements()
        
        # Categorize elements
        self._categorize_elements()
        
        # Build hierarchy
        self._build_hierarchy()
        
        # Generate JSON structure
        return self._generate_json()
    
    def _extract_elements(self):
        """Extract all mxCell elements with geometry."""
        for cell in self.root.findall(".//mxCell[@vertex='1']"):
            value = cell.get('value', '')
            style = cell.get('style', '')
            geometry = cell.find('mxGeometry')
            
            if geometry is None:
                continue
                
            x = float(geometry.get('x', 0))
            y = float(geometry.get('y', 0))
            width = float(geometry.get('width', 0))
            height = float(geometry.get('height', 0))
            
            self.elements.append({
                'id': cell.get('id'),
                'value': value,
                'style': style,
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })
    
    def _categorize_elements(self):
        """Categorize elements into epics, sub-epics, stories, and users."""
        for elem in self.elements:
            style = elem['style']
            y = elem['y']
            
            # Check for user circles (blue, typically 50x50)
            if self.USER_COLOR in style and elem['width'] == 50 and elem['height'] == 50:
                self.users.append(elem)
            # Check for epics (purple, rounded, typically at y≈130)
            elif self.EPIC_COLOR in style and 'rounded=1' in style and abs(y - self.EPIC_Y) < 50:
                self.epics.append(elem)
            # Check for sub-epics (green, rounded, typically at y≈200-240)
            elif self.SUB_EPIC_COLOR in style and 'rounded=1' in style and self.SUB_EPIC_Y_MIN <= y <= self.SUB_EPIC_Y_MAX:
                self.sub_epics.append(elem)
            # Check for stories (yellow, dark blue, or black)
            elif y >= self.STORY_Y_MIN:
                # System stories: dark blue (#1a237e)
                if '#1a237e' in style or '#0d47a1' in style:
                    elem['story_type'] = 'system'
                    self.stories.append(elem)
                # Technical stories: black (#000000)
                elif '#000000' in style and 'fillColor=#000000' in style:
                    elem['story_type'] = 'technical'
                    self.stories.append(elem)
                # User stories: yellow (default)
                elif self.STORY_COLOR in style:
                    elem['story_type'] = 'user'
                    self.stories.append(elem)
    
    def _build_hierarchy(self):
        """Build parent-child relationships based on positioning."""
        # Sort by x-position for sequential order
        self.epics.sort(key=lambda e: e['x'])
        self.sub_epics.sort(key=lambda e: e['x'])
        self.stories.sort(key=lambda e: (e['y'], e['x']))
        
        # Group sub-epics under epics (by x-position overlap)
        for epic in self.epics:
            epic['sub_epics'] = []
            epic['stories'] = []
            epic_x_end = epic['x'] + epic['width']
            
            for sub_epic in self.sub_epics:
                if epic['x'] <= sub_epic['x'] <= epic_x_end:
                    sub_epic['stories'] = []
                    epic['sub_epics'].append(sub_epic)
        
        # Group stories under sub-epics or epics
        for story in self.stories:
            # Find closest parent (sub-epic or epic)
            parent = self._find_parent(story)
            if parent:
                parent['stories'].append(story)
        
        # Assign users to stories
        self._assign_users_to_stories()
    
    def _find_parent(self, story: Dict) -> Optional[Dict]:
        """Find the parent epic or sub-epic for a story."""
        story_x = story['x']
        story_y = story['y']
        
        # First check sub-epics (more specific)
        for sub_epic in self.sub_epics:
            sub_x_start = sub_epic['x']
            sub_x_end = sub_epic['x'] + sub_epic['width']
            sub_y = sub_epic['y']
            
            # Story should be below and within x-range of sub-epic
            if sub_x_start <= story_x <= sub_x_end and story_y > sub_y:
                return sub_epic
        
        # Then check epics
        for epic in self.epics:
            epic_x_start = epic['x']
            epic_x_end = epic['x'] + epic['width']
            epic_y = epic['y']
            
            if epic_x_start <= story_x <= epic_x_end and story_y > epic_y:
                return epic
        
        return None
    
    def _assign_users_to_stories(self):
        """Assign user circles to stories based on proximity."""
        for story in self.stories:
            story['users'] = []
            
            # Find user circles above this story (within reasonable distance)
            story_x = story['x']
            story_y = story['y']
            
            for user in self.users:
                user_x = user['x']
                user_y = user['y']
                
                # User should be above story and roughly aligned horizontally
                if user_y < story_y and abs(user_x - story_x) < 100:
                    user_name = user['value'].strip()
                    if user_name and user_name not in story['users']:
                        story['users'].append(user_name)
    
    def _infer_connector(self, story: Dict, siblings: List[Dict], parent: Optional[Dict] = None) -> str:
        """
        Sophisticated connector inference based on positioning patterns.
        
        Rules:
        1. Horizontal flow (same y, increasing x) = "and" (sequential)
        2. Vertical stacking below = "or" (alternatives) or "opt" (optional)
        3. Multiple stories at same y below parent = "or"
        4. Single story below parent = "opt"
        5. Nested AND inside OR = positioned to the right (x offset)
        6. Column-based patterns (Bot-Behavior, AI Chat) = sequential "and"
        """
        story_y = story['y']
        story_x = story['x']
        
        # Find stories at the same y-level (within tolerance)
        Y_TOLERANCE = 10  # pixels
        same_y_stories = [s for s in siblings if abs(s['y'] - story_y) < Y_TOLERANCE]
        same_y_stories.sort(key=lambda s: s['x'])
        
        # Rule 1: Multiple stories at same y-level = horizontal sequential flow = "and"
        if len(same_y_stories) > 1:
            # Check if they're in increasing x order (horizontal flow)
            x_positions = [s['x'] for s in same_y_stories]
            if x_positions == sorted(x_positions):
                return "and"
        
        # Rule 2: Check if story is significantly below base level
        if siblings:
            base_y = min([s['y'] for s in siblings])
            vertical_offset = story_y - base_y
            
            # Significant vertical offset (>50px) indicates vertical stacking
            if vertical_offset > 50:
                # Find other stories at similar y-level below base
                below_base_stories = [
                    s for s in siblings 
                    if s['y'] > base_y + 50 and abs(s['y'] - story_y) < Y_TOLERANCE
                ]
                
                # Rule 3: Multiple stories at same y below = "or" (alternatives)
                if len(below_base_stories) > 1:
                    return "or"
                
                # Rule 4: Single story below = "opt" (optional)
                # But check if it's part of a column pattern first
                if not self._is_column_pattern(story, siblings):
                    return "opt"
        
        # Rule 5: Check for nested AND inside OR (positioned to the right)
        if parent:
            parent_stories = parent.get('stories', [])
            if parent_stories:
                # Check if parent has "or" connector (would have vertical stacking)
                parent_base_y = min([s['y'] for s in parent_stories])
                parent_has_vertical = any(s['y'] > parent_base_y + 50 for s in parent_stories)
                
                if parent_has_vertical:
                    # Check if this story is to the right of a vertically stacked story
                    for parent_story in parent_stories:
                        if parent_story['y'] > parent_base_y + 50:
                            # If this story is to the right and at similar y, it's nested AND
                            if abs(story_x - parent_story['x']) > 50 and abs(story_y - parent_story['y']) < Y_TOLERANCE:
                                return "and"
        
        # Rule 6: Column-based patterns (Bot-Behavior, AI Chat columns)
        if self._is_column_pattern(story, siblings):
            return "and"
        
        # Default: If story is at base level or slightly below, assume sequential
        if siblings:
            base_y = min([s['y'] for s in siblings])
            if abs(story_y - base_y) < Y_TOLERANCE:
                return "and"
        
        # Final default: sequential flow (80% of workflows are linear)
        return "and"
    
    def _is_column_pattern(self, story: Dict, siblings: List[Dict]) -> bool:
        """
        Detect column-based patterns (Bot-Behavior, AI Chat columns).
        Columns are typically spaced ~60-80px apart horizontally.
        """
        if not siblings:
            return False
        
        # Group stories by x-position (columns)
        x_positions = sorted(set([s['x'] for s in siblings + [story]]))
        
        # Check if x positions form regular columns (spacing ~60-80px)
        if len(x_positions) > 1:
            spacings = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1)]
            avg_spacing = sum(spacings) / len(spacings) if spacings else 0
            
            # Column pattern: regular spacing between 50-100px
            if 50 <= avg_spacing <= 100:
                # Check if story is part of this column pattern
                story_column = min(x_positions, key=lambda x: abs(x - story['x']))
                if abs(story['x'] - story_column) < 20:  # Within column tolerance
                    return True
        
        return False
    
    def _generate_json(self) -> Dict[str, Any]:
        """Generate story graph JSON structure."""
        epics_json = []
        
        for epic_idx, epic in enumerate(self.epics, 1):
            epic_json = {
                "name": epic['value'],
                "sequential_order": epic_idx,
                "estimated_stories": None,
                "sub_epics": [],
                "stories": []
            }
            
            # Process sub-epics
            for sub_idx, sub_epic in enumerate(epic.get('sub_epics', []), 1):
                sub_epic_json = {
                    "name": sub_epic['value'],
                    "sequential_order": sub_idx,
                    "estimated_stories": None,
                    "sub_epics": [],
                    "stories": []
                }
                
                # Process stories in sub-epic
                sub_stories = sub_epic.get('stories', [])
                sub_stories.sort(key=lambda s: (s['y'], s['x']))
                
                # Identify top-level stories (not nested under other stories)
                top_level_stories = self._identify_top_level_stories(sub_stories)
                
                for story_idx, story in enumerate(top_level_stories, 1):
                    story_json = self._story_to_json(story, story_idx, top_level_stories, sub_epic, all_stories=sub_stories)
                    sub_epic_json['stories'].append(story_json)
                
                epic_json['sub_epics'].append(sub_epic_json)
            
            # Process epic-level stories (if any)
            epic_stories = epic.get('stories', [])
            epic_stories.sort(key=lambda s: (s['y'], s['x']))
            
            # Identify top-level stories
            top_level_stories = self._identify_top_level_stories(epic_stories)
            
            for story_idx, story in enumerate(top_level_stories, 1):
                story_json = self._story_to_json(story, story_idx, top_level_stories, epic, all_stories=epic_stories)
                epic_json['stories'].append(story_json)
            
            epics_json.append(epic_json)
        
        return {"epics": epics_json}
    
    def _identify_top_level_stories(self, all_stories: List[Dict]) -> List[Dict]:
        """Identify top-level stories (not nested under other stories)."""
        if not all_stories:
            return []
        
        # Sort by y, then x
        sorted_stories = sorted(all_stories, key=lambda s: (s['y'], s['x']))
        base_y = sorted_stories[0]['y']
        Y_TOLERANCE = 10
        
        top_level = []
        processed = set()
        
        for story in sorted_stories:
            story_id = story.get('id')
            if story_id in processed:
                continue
            
            story_y = story['y']
            story_x = story['x']
            
            # Check if this story is nested under any already-processed top-level story
            is_nested = False
            for top_story in top_level:
                top_y = top_story['y']
                top_x = top_story['x']
                
                # Directly below (vertical nesting)
                if story_y > top_y + 50 and abs(story_x - top_x) < 100:
                    is_nested = True
                    break
                # To the right of vertically stacked story (nested AND inside OR)
                elif story_y > top_y + 50 and story_x > top_x + 50 and abs(story_y - top_y) < 100:
                    # Check if top_story is alone at its level (OR/OPT)
                    same_level = [s for s in all_stories if abs(s['y'] - top_y) < Y_TOLERANCE]
                    if len(same_level) == 1:  # Top story is alone (OR/OPT)
                        is_nested = True
                        break
            
            if not is_nested:
                top_level.append(story)
                processed.add(story_id)
        
        return top_level
    
    def _story_to_json(self, story: Dict, story_idx: int, siblings: List[Dict], parent: Optional[Dict] = None, all_stories: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Convert story element to JSON structure."""
        if all_stories is None:
            all_stories = siblings
        
        story_json = {
            "name": story['value'],
            "sequential_order": story_idx,
            "connector": self._infer_connector(story, siblings, parent),
            "users": story.get('users', []),
            "story_type": story.get('story_type', 'user')  # Infer from style
        }
        
        # Find nested stories from all_stories (not just siblings)
        nested = []
        story_y = story['y']
        story_x = story['x']
        Y_TOLERANCE = 10
        
        for s in all_stories:
            if s.get('id') == story.get('id'):
                continue  # Skip self
            
            s_y = s['y']
            s_x = s['x']
            
            # Directly below (vertical nesting)
            if s_y > story_y + 50 and abs(s_x - story_x) < 100:
                # Check if s is not nested under another story between story and s
                is_directly_nested = True
                for other in all_stories:
                    if other.get('id') == story.get('id') or other.get('id') == s.get('id'):
                        continue
                    other_y = other['y']
                    other_x = other['x']
                    if story_y < other_y < s_y and abs(other_x - story_x) < 100:
                        is_directly_nested = False
                        break
                
                if is_directly_nested:
                    nested.append(s)
            
            # To the right of vertically stacked story (nested AND inside OR)
            elif s_y > story_y + 50 and s_x > story_x + 50 and abs(s_y - story_y) < 100:
                # Check if this story is part of a vertical stack (OR/OPT)
                same_level_as_story = [sib for sib in all_stories if abs(sib['y'] - story_y) < Y_TOLERANCE]
                if len(same_level_as_story) == 1:  # This story is alone (OR/OPT)
                    nested.append(s)
        
        if nested:
            nested.sort(key=lambda s: (s['y'], s['x']))
            # Remove duplicates
            seen_ids = set()
            unique_nested = []
            for n in nested:
                n_id = n.get('id')
                if n_id not in seen_ids:
                    unique_nested.append(n)
                    seen_ids.add(n_id)
            
            story_json['stories'] = []
            for nested_idx, nested_story in enumerate(unique_nested, 1):
                nested_json = self._story_to_json(nested_story, nested_idx, unique_nested, story, all_stories=all_stories)
                story_json['stories'].append(nested_json)
        
        return story_json


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python drawio_to_story_graph.py <drawio_file> [output_json]")
        sys.exit(1)
    
    drawio_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else drawio_path.replace('.drawio', '-extracted.json')
    
    try:
        parser = DrawIOToStoryGraph(drawio_path)
        story_graph = parser.parse()
        
        # Write JSON output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(story_graph, f, indent=2, ensure_ascii=False)
        
        print(f"Extracted story graph to: {output_path}")
        print(f"Found {len(story_graph['epics'])} epics")
        
        # Count total stories
        total_stories = 0
        for epic in story_graph['epics']:
            for sub_epic in epic.get('sub_epics', []):
                total_stories += len(sub_epic.get('stories', []))
            total_stories += len(epic.get('stories', []))
        print(f"Total stories extracted: {total_stories}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


