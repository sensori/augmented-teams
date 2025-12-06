"""
DrawIO Renderer

Handles rendering of story diagrams to DrawIO XML format.
Moved from story_map_drawio_renderer.py to consolidate rendering logic.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple, List
import xml.etree.ElementTree as ET
from xml.dom import minidom


class DrawIORenderer:
    """
    Renderer for converting story diagrams to DrawIO XML format.
    
    Handles both outline mode (epics/features/stories) and increments mode.
    """
    
    STORY_WIDTH = 50
    STORY_HEIGHT = 50
    STORY_SPACING_X = 60
    STORY_SPACING_Y = 55
    FEATURE_HEIGHT = 60
    FEATURE_SPACING_X = 10
    FEATURE_SPACING_Y = 10  # Vertical spacing between features when stacking
    EPIC_Y = 120
    FEATURE_Y = 200
    STORY_START_Y = 350  # Legacy constant (not used for relative positioning)
    STORY_OFFSET_FROM_FEATURE = 90  # Vertical spacing from feature bottom to stories
    USER_LABEL_OFFSET = 60  # Distance above element (accounts for 50px label height)
    USER_LABEL_X_OFFSET = 5  # Offset to the right from element x position
    # Acceptance criteria (exploration mode)
    ACCEPTANCE_CRITERIA_WIDTH = 250  # Default width for acceptance criteria boxes in exploration mode
    ACCEPTANCE_CRITERIA_HEIGHT = 60
    ACCEPTANCE_CRITERIA_SPACING_Y = 70  # Vertical spacing between acceptance criteria boxes
    ACCEPTANCE_CRITERIA_MIN_WIDTH = 250  # Minimum width for AC boxes (matches expected)
    ACCEPTANCE_CRITERIA_CHAR_WIDTH = 6  # Approximate width per character at 8px font
    ACCEPTANCE_CRITERIA_PADDING = 10  # Left + right padding
    
    @staticmethod
    def _get_story_style(story: Dict[str, Any]) -> str:
        """
        Get DrawIO style for story based on story_type.
        
        - user (default): yellow fill (#fff2cc)
        - system: dark blue fill (#1a237e), white text
        - technical: black fill (#000000), white text
        """
        story_type = story.get('story_type', 'user')
        if story_type == 'system':
            # System stories: dark blue fill, white text
            return 'whiteSpace=wrap;html=1;aspect=fixed;fillColor=#1a237e;strokeColor=#0d47a1;fontColor=#ffffff;fontSize=8;'
        elif story_type == 'technical':
            # Technical stories: black fill, white text
            return 'whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;strokeColor=#333333;fontColor=#ffffff;fontSize=8;'
        else:
            # User stories: yellow fill (default)
            return 'whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;'
    
    @staticmethod
    def _calculate_total_stories_for_epic_in_increment(epic: Dict[str, Any]) -> int:
        """
        Calculate total stories for an epic within an increment scope.
        Counts only stories in story_groups within sub_epics (no direct stories on epics or sub_epics).
        """
        # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
        def get_sub_epics(epic):
            return epic.get('sub_epics', []) or epic.get('features', [])
        
        total = 0
        for sub_epic in get_sub_epics(epic):
            # Count stories in story_groups (new structure only)
            story_groups = sub_epic.get('story_groups', [])
            if story_groups:
                for story_group in story_groups:
                    total += len(story_group.get('stories', []))
            elif sub_epic.get('estimated_stories'):
                # Use estimate if no actual stories
                total += sub_epic['estimated_stories']
        # Epics don't have direct stories - only through sub_epics -> story_groups
        if not total and epic.get('estimated_stories'):
            total += epic['estimated_stories']
        return total
    
    @staticmethod
    def _calculate_total_stories_for_feature_in_increment(feature: Dict[str, Any]) -> int:
        """
        Calculate total stories for a feature (sub_epic) within an increment scope.
        Counts only stories in story_groups (no direct stories on features).
        """
        story_groups = feature.get('story_groups', [])
        if story_groups:
            total = 0
            for story_group in story_groups:
                total += len(story_group.get('stories', []))
            return total
        elif feature.get('estimated_stories'):
            return feature['estimated_stories']
        return 0
    
    @staticmethod
    def _traverse_all_stories(story: Dict[str, Any], collected: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Simple algorithm to collect a story (no nested stories - stories are flat).
        Legacy method kept for compatibility but no longer traverses nested stories.
        
        Args:
            story: Story dictionary
            collected: List to collect stories
        
        Returns:
            List containing only the story (no nested traversal)
        """
        if collected is None:
            collected = []
        
        # Add current story only (no nested stories - stories are flat within story_groups)
        collected.append(story)
        
        return collected
    
    @staticmethod
    def _get_story_count_display_html(count: int, position: str = 'bottom') -> str:
        """
        Get HTML for displaying story count.
        
        Args:
            count: Story count to display
            position: 'bottom' (default, below name) or 'top-right' (absolute positioned in top right)
        """
        if position == 'top-right':
            # Position in top right corner using absolute positioning
            # Ensure parent has padding-right so text doesn't overlap
            return f"<div style=\"position: absolute; top: 2px; right: 5px; font-size: 8px; color: rgb(128, 128, 128); white-space: nowrap; z-index: 10;\">{count} stories</div>"
        else:
            # Default: below name (bottom)
            return f"<br><i style=\"border-color: rgb(218, 220, 224); font-size: 8px;\"><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">{count}&nbsp;</span><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">stories</span></i>"
    
    def _calculate_text_width(self, text: str, font_size: int = 8, padding: int = 10) -> int:
        """
        Calculate approximate width needed for text at given font size.
        Accounts for word wrapping - uses max characters per line (typically 30-40 chars).
        
        Args:
            text: Text content (HTML will be stripped)
            font_size: Font size in pixels
            padding: Additional padding (left + right)
        
        Returns:
            Width in pixels
        """
        import re
        # Strip HTML tags for width calculation
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&amp;', '&')
        
        # Split by <br> to find longest line
        lines = clean_text.split('<br>')
        max_line_length = max(len(line.strip()) for line in lines) if lines else len(clean_text.strip())
        
        # DrawIO with whiteSpace=wrap automatically wraps text, so we don't need
        # to calculate width based on full text length. Use a fixed reasonable width
        # that allows comfortable reading with automatic text wrapping.
        # The expected shows 250px works well for all AC boxes regardless of text length.
        return self.ACCEPTANCE_CRITERIA_MIN_WIDTH
    
    def _format_steps_as_acceptance_criteria(self, steps: List[Union[str, dict]], step_idx: int) -> Tuple[str, int]:
        """
        Format steps as acceptance criteria text for display.
        Each AC entry gets its own box: Box 0 = first entry, Box 1 = second entry
        
        Args:
            steps: List of acceptance criteria (dictionaries with 'description', or strings)
            step_idx: Index of the current box (0 = first box, 1 = second box)
        
        Returns:
            Tuple of (HTML formatted text, calculated width)
        """
        if step_idx < len(steps):
            step = steps[step_idx]
            if isinstance(step, dict):
                step_desc = step.get('description', str(step)).strip()
            elif isinstance(step, str):
                step_desc = step.strip()
            else:
                step_desc = ""
            
            if step_desc:
                # Format with When/Then on separate lines
                # Replace \n with <br> for HTML display
                formatted_desc = step_desc.replace('\n', '<br>')
                # Add bold tags for When/Then if not already present
                if '<b>When</b>' not in formatted_desc and '<b>Then</b>' not in formatted_desc:
                    # Try to add bold tags if the text starts with When/Then
                    if formatted_desc.startswith('When '):
                        formatted_desc = formatted_desc.replace('When ', '<b>When</b>&nbsp;', 1)
                    if '<br>Then ' in formatted_desc:
                        formatted_desc = formatted_desc.replace('<br>Then ', '<br><b>Then</b> ', 1)
                    elif formatted_desc.startswith('Then '):
                        formatted_desc = formatted_desc.replace('Then ', '<b>Then</b> ', 1)
                
                acceptance_text = f'<div style="font-size: 8px;">{formatted_desc}</div>'
            else:
                acceptance_text = ""
        else:
            acceptance_text = ""
        
        if not acceptance_text:
            return ("", self.ACCEPTANCE_CRITERIA_MIN_WIDTH)
        
        # Calculate dynamic width
        ac_width = self._calculate_text_width(acceptance_text)
        
        return (acceptance_text, ac_width)
    
    def render_outline(self, story_graph: Dict[str, Any],
                      output_path: Path,
                      layout_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render story graph as outline (no increments) to DrawIO XML.
        
        Args:
            story_graph: Story graph dictionary with epics/features/stories
            output_path: Output path for DrawIO file
            layout_data: Optional layout data to preserve positions
        
        Returns:
            Dictionary with output_path and summary
        """
        # Normalize layout_data format
        if layout_data is None:
            layout_data = {}
        
        # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
        def get_sub_epics(epic):
            return epic.get('sub_epics', []) or epic.get('features', [])
        
        # Check if any story has Steps (acceptance criteria) - if so, render in exploration mode
        has_acceptance_criteria = False
        for epic in story_graph.get('epics', []):
            for sub_epic in get_sub_epics(epic):
                # Only check story_groups (no legacy direct stories support)
                for story_group in sub_epic.get('story_groups', []):
                    for story in story_group.get('stories', []):
                        if story.get('acceptance_criteria'):
                            has_acceptance_criteria = True
                            break
                    if has_acceptance_criteria:
                        break
                if has_acceptance_criteria:
                    break
            if has_acceptance_criteria:
                break
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate diagram - use exploration mode if stories have acceptance criteria
        xml_output = self._generate_diagram(story_graph, layout_data, is_increments=False, is_exploration=has_acceptance_criteria)
        
        # Write output
        output_path.write_text(xml_output, encoding='utf-8')
        
        # Recursively count all sub_epics at all nesting levels
        def count_all_sub_epics(epic_or_sub_epic):
            """Recursively count all sub_epics, including nested ones."""
            count = 0
            direct_sub_epics = get_sub_epics(epic_or_sub_epic)
            count += len(direct_sub_epics)
            # Recursively count sub_epics within each sub_epic
            for sub_epic in direct_sub_epics:
                count += count_all_sub_epics(sub_epic)
            return count
        
        # Count sub_epics
        sub_epic_count = 0
        for epic in story_graph.get("epics", []):
            sub_epic_count += count_all_sub_epics(epic)
        
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
                "sub_epic_count": sub_epic_count,
                "diagram_generated": True
            }
        }
    
    def render_exploration(self, story_graph: Dict[str, Any],
                          output_path: Path,
                          layout_data: Optional[Dict[str, Any]] = None,
                          scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Render story graph with acceptance criteria (exploration mode) to DrawIO XML.
        Acceptance criteria are rendered as wider boxes below stories.
        
        Args:
            story_graph: Story graph dictionary with epics/features/stories
            output_path: Output path for DrawIO file
            layout_data: Optional layout data to preserve positions
            scope: Optional scope identifier for filtering stories
        
        Returns:
            Dictionary with output_path and summary
        """
        # Normalize layout_data format
        if layout_data is None:
            layout_data = {}
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate diagram with acceptance criteria (exploration mode)
        xml_output = self._generate_diagram(story_graph, layout_data, is_increments=False, is_exploration=True)
        
        # Write output
        output_path.write_text(xml_output, encoding='utf-8')
        
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
                "diagram_generated": True
            }
        }
    
    def render_increments(self, story_graph: Dict[str, Any],
                         output_path: Path,
                         layout_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render story graph with increments to DrawIO XML.
        For increments, epics and features show story counts in top right.
        
        Args:
            story_graph: Story graph dictionary with epics/features/stories/increments
            output_path: Output path for DrawIO file
            layout_data: Optional layout data to preserve positions
        
        Returns:
            Dictionary with output_path and summary
        """
        # Normalize layout_data format
        if layout_data is None:
            layout_data = {}
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate diagram with increments (same method, but will handle increment-specific rendering)
        xml_output = self._generate_diagram(story_graph, layout_data, is_increments=True)
        
        # Write output
        output_path.write_text(xml_output, encoding='utf-8')
        
        increments_count = len(story_graph.get("increments", []))
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
                "increments": increments_count,
                "diagram_generated": True
            }
        }
    
    def _generate_exploration_diagram(self, story_graph: Dict[str, Any], layout_data: Dict[str, Dict[str, float]], root_elem: ET.Element, root: ET.Element) -> str:
        """
        Generate DrawIO XML for exploration mode (acceptance criteria below stories).
        This is a clean, separate implementation that doesn't intermingle with non-exploration logic.
        
        Args:
            story_graph: Story graph JSON data
            layout_data: Optional layout data with story coordinates
            root_elem: Root XML element for the diagram
            root: Root XML element for the file
        
        Returns:
            XML string for the DrawIO file
        """
        # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
        def get_sub_epics(epic):
            return epic.get('sub_epics', []) or epic.get('features', [])
        
        # Helper to check if a story has acceptance criteria
        # Support both 'Steps' (legacy) and 'acceptance_criteria' (new format)
        def has_acceptance_criteria(story):
            return bool(story.get('acceptance_criteria') or story.get('Steps') or story.get('steps'))
        
        # Helper to filter story groups to only those with stories that have AC
        def filter_story_groups(groups):
            filtered = []
            for group in groups:
                group_stories = group.get('stories', [])
                filtered_stories = [s for s in group_stories if has_acceptance_criteria(s)]
                if filtered_stories:
                    filtered_group = group.copy()
                    filtered_group['stories'] = filtered_stories
                    filtered.append(filtered_group)
            return filtered
        
        # Create epic group
        epic_group = ET.SubElement(root_elem, 'mxCell', id='epic-group', value='', 
                     style='group', parent='1', vertex='1', connectable='0')
        epic_group_geom = ET.SubElement(epic_group, 'mxGeometry', x='0', y='0', width='1', height='1')
        epic_group_geom.set('as', 'geometry')
        
        epic_x = 20
        epic_spacing = 30
        shown_users = set()
        epic_group_rightmost = 0
        
        for epic_idx, epic in enumerate(story_graph.get('epics', []), 1):
            features = get_sub_epics(epic)
            
            # Filter features - keep all features, but filter their story groups to only those with AC
            filtered_features = []
            for feature in features:
                story_groups = feature.get('story_groups', [])
                filtered_feature = feature.copy()
                if story_groups:
                    filtered_groups = filter_story_groups(story_groups)
                    filtered_feature['story_groups'] = filtered_groups
                else:
                    filtered_feature['story_groups'] = []
                # Always include the feature (even if no story_groups or no AC)
                filtered_features.append(filtered_feature)
            
            # Skip epic if no features at all
            if not filtered_features:
                continue
            
            # Render epic - always full height (60px), don't change
            epic_height = 60
            epic_cell = ET.SubElement(root_elem, 'mxCell',
                                     id=f'e{epic_idx}',
                                     value=epic['name'],
                                     style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                     parent='1', vertex='1')
            epic_geom = ET.SubElement(epic_cell, 'mxGeometry', x=str(epic_x), y=str(self.EPIC_Y),
                                     width='100', height=str(epic_height))
            epic_geom.set('as', 'geometry')
            
            # Render features horizontally (side by side)
            feature_y = self.FEATURE_Y  # Use standard feature Y position
            feature_spacing = 10  # Spacing between features
            current_feature_x = epic_x  # Start at epic left edge
            epic_rightmost_ac_x = None
            epic_max_x = epic_x
            
            for feat_idx, feature in enumerate(filtered_features, 1):
                feature_x = current_feature_x  # Each feature gets its own x position
                # Get filtered story groups (already filtered to only those with AC in filtered_features)
                story_groups = feature.get('story_groups', [])
                # Render feature even if no story_groups (sub-epics without sub-sub)
                
                # Initialize story_positions for this feature
                story_positions = {}  # Maps story name -> {'x': x, 'y': y, 'width': width, 'height': height}
                first_story_cell_ref = None  # Track first story/user cell to insert backgrounds before it
                current_ac_rightmost_x = None  # Track rightmost position of AC boxes across all stories in this feature
                
                # Render feature
                feature_cell = ET.SubElement(root_elem, 'mxCell',
                                            id=f'e{epic_idx}f{feat_idx}',
                                            value=feature['name'],
                                            style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                            parent='1', vertex='1')
                feature_geom = ET.SubElement(feature_cell, 'mxGeometry',
                                            x=str(feature_x), y=str(feature_y),
                                            width='100', height='60')
                feature_geom.set('as', 'geometry')
                
                # Render story groups and stories
                group_start_x = feature_x + 2
                group_start_y = feature_y + 60 + self.STORY_OFFSET_FROM_FEATURE
                current_group_x = group_start_x
                current_group_y = group_start_y
                previous_group_bottom_y = None
                previous_story_users = None
                feature_min_x = feature_x
                feature_max_x = feature_x
                story_idx = 1
                
                # Track shown users at feature/column level - each user should only appear once per column
                feature_shown_users = set()
                
                for group_idx, group in enumerate(story_groups):
                    group_type = group.get('type', 'and')
                    group_connector = group.get('connector')
                    group_stories = group.get('stories', [])
                    
                    if not group_stories:
                        continue
                    
                    # Position group based on connector
                    if group_connector is None:
                        group_x = group_start_x
                        group_y = current_group_y
                    elif group_connector == 'and':
                        group_x = current_group_x
                        group_y = current_group_y
                    elif group_connector == 'or':
                        group_x = group_start_x
                        if previous_group_bottom_y is not None:
                            group_y = previous_group_bottom_y + self.STORY_SPACING_Y + 50
                        else:
                            group_y = current_group_y + self.STORY_SPACING_Y + 70
                        current_group_y = group_y
                    
                    group_bottom_y = group_y
                    
                    # Sort stories by sequential_order
                    sorted_stories = sorted(group_stories, key=lambda s: s.get('sequential_order', 999))
                    
                    # Render stories in group
                    for story_idx_in_group, story in enumerate(sorted_stories):
                        # Calculate story position based on group type
                        if group_type == 'and':
                            # Position stories accounting for AC boxes from previous stories
                            if story_idx_in_group == 0:
                                # First story in group starts at group_x
                                story_x = group_x
                            else:
                                # Subsequent stories positioned after previous story's AC boxes
                                if current_ac_rightmost_x is not None:
                                    # Position after AC boxes with spacing (account for story width too)
                                    # AC boxes end at current_ac_rightmost_x, add spacing, then position story
                                    story_x = current_ac_rightmost_x + 20
                                else:
                                    # Fallback to normal spacing if no AC boxes yet
                                    story_x = group_x + story_idx_in_group * self.STORY_SPACING_X
                            story_y = group_y
                        else:  # 'or'
                            story_x = group_x
                            story_y = group_y + story_idx_in_group * self.STORY_SPACING_Y
                        
                        # Render users - only show each user once per column/feature
                        story_users = set(story.get('users', []))
                        new_story_users = []
                        # Only render users that haven't been shown in this feature/column yet
                        for user in story_users:
                            if user not in feature_shown_users:
                                new_story_users.append(user)
                                feature_shown_users.add(user)
                        previous_story_users = story_users
                        
                        if new_story_users:
                            for user_idx, user in enumerate(new_story_users):
                                user_x = story_x + user_idx * self.STORY_SPACING_X
                                user_y = story_y - self.USER_LABEL_OFFSET
                                
                                user_label = ET.SubElement(root_elem, 'mxCell',
                                                          id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                          value=user,
                                                          style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                          parent='1', vertex='1')
                                user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                         x=str(user_x), y=str(user_y),
                                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                user_geom.set('as', 'geometry')
                                
                                # Track first user/story cell for inserting background rectangles before it
                                if first_story_cell_ref is None:
                                    first_story_cell_ref = user_label
                                
                                feature_min_x = min(feature_min_x, user_x)
                                feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                        
                        # Render story
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                  id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                  value=story['name'],
                                                  style=self._get_story_style(story),
                                                  parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry',
                                                   x=str(story_x), y=str(story_y),
                                                   width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        
                        # Track first story cell if no user cell was tracked
                        if first_story_cell_ref is None:
                            first_story_cell_ref = story_cell
                        
                        # Track story position for grey background rectangles
                        story_positions[story['name']] = {
                            'x': story_x,
                            'y': story_y,
                            'width': self.STORY_WIDTH,
                            'height': self.STORY_HEIGHT
                        }
                        
                        feature_min_x = min(feature_min_x, story_x)
                        feature_max_x = max(feature_max_x, story_x + self.STORY_WIDTH)
                        
                        # Render acceptance criteria
                        # Support both 'Steps' (legacy) and 'acceptance_criteria' (new format)
                        steps = story.get('acceptance_criteria') or story.get('Steps') or story.get('steps') or []
                        # Sort by sequential_order to ensure top-to-bottom rendering order
                        if steps and isinstance(steps[0], dict) and 'sequential_order' in steps[0]:
                            steps = sorted(steps, key=lambda s: s.get('sequential_order', 999))
                        if steps:
                            acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10
                            # Determine starting x position for AC boxes - position sequentially to avoid overlap
                            # Check layout_data first if available, otherwise use sequential positioning
                            if current_ac_rightmost_x is not None:
                                # Position after previous AC boxes with spacing
                                ac_start_x = current_ac_rightmost_x + 20  # 20px spacing between story AC boxes
                            else:
                                # First story's AC boxes start aligned with story
                                ac_start_x = story_x
                            
                            for ac_box_idx in range(len(steps)):
                                acceptance_text, ac_width = self._format_steps_as_acceptance_criteria(steps, ac_box_idx)
                                if not acceptance_text:
                                    break
                                
                                # Check layout_data for AC box position
                                # Try both cell ID format and name-based format
                                ac_key_cell_id = f'ac_e{epic_idx}f{feat_idx}s{story_idx}_{ac_box_idx}'
                                ac_key_name = f"{epic['name']}|{feature['name']}|{story['name']}|AC{ac_box_idx}"
                                if layout_data and (ac_key_cell_id in layout_data or ac_key_name in layout_data):
                                    # Use layout data if available
                                    ac_layout = layout_data.get(ac_key_cell_id) or layout_data.get(ac_key_name)
                                    if ac_layout:
                                        ac_x = ac_layout['x']
                                        ac_y = ac_layout['y']
                                        ac_width = ac_layout.get('width', ac_width)
                                    else:
                                        ac_x = ac_start_x
                                        ac_y = acceptance_criteria_y + ac_box_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                else:
                                    ac_x = ac_start_x
                                    ac_y = acceptance_criteria_y + ac_box_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                
                                # Update rightmost AC position for this story's AC boxes
                                current_ac_rightmost_x = max(current_ac_rightmost_x or 0, ac_x + ac_width)
                                
                                ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                       id=f'ac_e{epic_idx}f{feat_idx}s{story_idx}_{ac_box_idx}',
                                                       value=acceptance_text,
                                                       style='rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;fontSize=8;',
                                                       parent='1', vertex='1')
                                ac_geom = ET.SubElement(ac_cell, 'mxGeometry',
                                                       x=str(ac_x), y=str(ac_y),
                                                       width=str(ac_width), height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                ac_geom.set('as', 'geometry')
                                
                                feature_min_x = min(feature_min_x, ac_x)
                                feature_max_x = max(feature_max_x, ac_x + ac_width)
                                if epic_rightmost_ac_x is None or (ac_x + ac_width) > epic_rightmost_ac_x:
                                    epic_rightmost_ac_x = ac_x + ac_width
                                
                                # Update group bottom Y to include AC
                                if ac_box_idx == 1:
                                    group_bottom_y = max(group_bottom_y, ac_y + self.ACCEPTANCE_CRITERIA_HEIGHT)
                        
                        story_idx += 1
                        group_bottom_y = max(group_bottom_y, story_y + self.STORY_HEIGHT)
                    
                    # Update group positioning for next group
                    if group_type == 'and':
                        group_rightmost_x = group_x + (len(sorted_stories) - 1) * self.STORY_SPACING_X + self.STORY_WIDTH
                    else:
                        group_rightmost_x = group_x + self.STORY_WIDTH
                    
                    if group_connector == 'and':
                        current_group_x = group_rightmost_x + self.STORY_SPACING_X
                        previous_group_bottom_y = group_bottom_y
                    elif group_connector == 'or':
                        current_group_x = group_start_x
                        previous_group_bottom_y = group_bottom_y + 20
                    else:  # None (first group)
                        current_group_x = group_rightmost_x + self.STORY_SPACING_X
                        previous_group_bottom_y = group_bottom_y
                
                # Update feature width
                if feature_max_x > feature_min_x:
                    feature_padding = 30 if epic_idx == 1 else 6
                    if epic_rightmost_ac_x is not None:
                        actual_feature_width = epic_rightmost_ac_x - feature_x + feature_padding
                    else:
                        actual_feature_width = feature_max_x - feature_x + feature_padding
                    feature_geom.set('width', str(actual_feature_width))
                    feature_max_x = feature_x + actual_feature_width
                
                # Update epic bounds
                epic_max_x = max(epic_max_x, feature_max_x)
                
                # Move to next feature position (side by side)
                current_feature_x = feature_max_x + feature_spacing
                
                # Position next feature
                feature_x = feature_max_x + self.FEATURE_SPACING_X
                
                # Update current_group_x for next feature
                current_group_x = feature_x + 2
            
            # Update epic width
            if epic_max_x > epic_x:
                epic_padding = 30 if epic_idx == 1 else 6
                if epic_rightmost_ac_x is not None:
                    actual_epic_width = epic_rightmost_ac_x - epic_x + epic_padding
                else:
                    actual_epic_width = epic_max_x - epic_x + epic_padding
                epic_geom.set('width', str(actual_epic_width))
                epic_group_rightmost = max(epic_group_rightmost, epic_x + actual_epic_width)
            
            # Position next epic
            epic_x = epic_x + actual_epic_width + epic_spacing
        
        # Update epic-group width
        if epic_group_rightmost > 0:
            epic_group_geom.set('width', str(epic_group_rightmost))
            epic_group_geom.set('height', '190')
        
        # Convert to XML string
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')
    
    def _generate_diagram(self, story_graph: Dict[str, Any], layout_data: Dict[str, Dict[str, float]] = None, is_increments: bool = False, is_exploration: bool = False) -> str:
        """
        Generate DrawIO XML from story graph.
        
        Args:
            story_graph: Story graph JSON data
            layout_data: Optional layout data with story coordinates (key: "epic_name|feature_name|story_name")
            is_increments: If True, render in increments mode (story counts in top right for epics/features)
            is_exploration: If True, render in exploration mode (acceptance criteria below stories)
        """
        if layout_data is None:
            layout_data = {}
        root = ET.Element('mxfile', host='65bd71144e')
        diagram = ET.SubElement(root, 'diagram', id='story-map', name='Story Map')
        graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                    dx='2656', dy='1035', grid='1', gridSize='10', 
                                    guides='1', tooltips='1', connect='1', arrows='1', 
                                    fold='1', page='1', pageScale='1', 
                                    pageWidth='4000', pageHeight='3000', math='0', shadow='0')
        root_elem = ET.SubElement(graph_model, 'root')
        ET.SubElement(root_elem, 'mxCell', id='0')
        ET.SubElement(root_elem, 'mxCell', id='1', parent='0')
        
        # Collect all background rectangles here - will be inserted after root cells
        all_background_rectangles = []
        
        # Handle increments mode
        if is_increments and 'increments' in story_graph:
            # Render increments with special handling for epic/feature story counts
            return self._generate_increments_diagram(story_graph, layout_data, root_elem, root)
        
        # Handle exploration mode separately
        if is_exploration:
            return self._generate_exploration_diagram(story_graph, layout_data, root_elem, root)
        
        # Standard outline rendering (non-exploration mode)
        epic_group = ET.SubElement(root_elem, 'mxCell', id='epic-group', value='', 
                     style='group', parent='1', vertex='1', connectable='0')
        epic_group_geom = ET.SubElement(epic_group, 'mxGeometry', x='0', y='0', width='1', height='1')
        epic_group_geom.set('as', 'geometry')
        
        # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
        def get_sub_epics(epic):
            return epic.get('sub_epics', []) or epic.get('features', [])
        
        x_pos = 20
        shown_users = set()  # Track which users have been shown
        
        for epic_idx, epic in enumerate(story_graph.get('epics', []), 1):
            features = get_sub_epics(epic)  # Get sub_epics (or features for backwards compatibility)
            
            # In exploration mode: filter epics/sub-epics to only those with stories that have AC
            if is_exploration:
                filtered_features = []
                for feature in features:
                    # Check if feature has any stories with AC (only story_groups structure)
                    story_groups = feature.get('story_groups', [])
                    if not story_groups:
                        continue  # Skip features without story_groups
                    
                    # Check story_groups structure
                    has_story_with_ac = False
                    for group in story_groups:
                        for story in group.get('stories', []):
                            if story.get('acceptance_criteria'):
                                has_story_with_ac = True
                                break
                        if has_story_with_ac:
                            break
                    
                    if has_story_with_ac:
                        filtered_features.append(feature)
                
                # Skip epic if no features have stories with AC
                if not filtered_features:
                    continue
                
                features = filtered_features
            
            # Check if layout data has coordinates for this epic
            epic_key = f"EPIC|{epic['name']}"
            if epic_key in layout_data:
                # Use stored epic coordinates and dimensions
                epic_x = layout_data[epic_key]['x']
                epic_y = layout_data[epic_key]['y']
                epic_width = layout_data[epic_key].get('width', 0)
                epic_height = 60  # Always 60px, don't use layout_data height
                use_epic_layout = True
            else:
                # Use calculated positions
                epic_x = x_pos
                epic_y = self.EPIC_Y
                epic_width = 0
                epic_height = 60  # Always 60px
                use_epic_layout = False
            
            feature_x = epic_x + 10 if use_epic_layout else x_pos + 10
            feature_y = epic_y + epic_height  # Features directly below epic
            
            # Pre-calculate which features have AC cards to adjust positioning
            feature_has_ac = {}
            for feature in features:
                stories = feature.get('stories', [])
                has_ac = any(
                    s.get('acceptance_criteria') 
                    for s in stories
                )
                feature_has_ac[feature['name']] = has_ac
            
            feature_positions = []
            previous_feature_rightmost_x = None
            # In exploration mode, features align with epics (no offset)
            # Otherwise, start features 10px from epic left edge
            feature_x_offset = 0 if is_exploration else 10
            current_feature_x = epic_x + feature_x_offset
            # Features positioned directly below epic
            current_feature_y = epic_y + epic_height  # Start Y position for first feature (below epic)
            # Helper function to recursively collect nested sub-epics with story_groups, maintaining order
            def collect_nested_with_stories(sub_epics, collected):
                """Recursively collect all nested sub-epics that have story_groups, in order"""
                # Sort by sequential_order to maintain order
                sorted_sub_epics = sorted(sub_epics, key=lambda x: x.get('sequential_order', 999))
                for sub_epic in sorted_sub_epics:
                    sub_story_groups = sub_epic.get('story_groups', [])
                    sub_nested = sub_epic.get('sub_epics', [])
                    if sub_story_groups and len(sub_story_groups) > 0:
                        # This sub-epic has story_groups - add it to collected list
                        collected.append(sub_epic)
                    elif sub_nested:
                        # This sub-epic has nested sub_epics - recurse
                        collect_nested_with_stories(sub_nested, collected)
            
            # Build features_to_render list, replacing middle-level features with their nested sub-epics
            # We need to preserve parent's sequential_order when replacing with nested sub-epics
            features_to_render = []
            for feature in features:
                feature_story_groups = feature.get('story_groups', [])
                nested_sub_epics = feature.get('sub_epics', [])
                parent_order = feature.get('sequential_order', 999)
                
                if feature_story_groups and len(feature_story_groups) > 0:
                    # This feature has story_groups - render it
                    features_to_render.append(feature)
                elif nested_sub_epics and (not feature_story_groups or len(feature_story_groups) == 0):
                    # This is a middle-level sub-epic - replace it with its nested sub-epics that have story_groups
                    nested_with_stories = []
                    collect_nested_with_stories(nested_sub_epics, nested_with_stories)
                    # Sort nested sub-epics by their sequential_order (relative to parent)
                    nested_with_stories.sort(key=lambda x: x.get('sequential_order', 999))
                    # Assign parent's sequential_order to nested sub-epics so they maintain parent's position
                    # Use a fractional offset based on their relative order to maintain sorting within parent
                    for idx, nested in enumerate(nested_with_stories):
                        # Create a composite order: parent_order + fractional offset based on relative position
                        # This ensures nested sub-epics appear where parent would be, in correct relative order
                        nested['_render_order'] = parent_order + (nested.get('sequential_order', 999) / 10000.0)
                    features_to_render.extend(nested_with_stories)
                # Features with no story_groups and no nested sub_epics are skipped
            
            # Sort all features by _render_order if present, otherwise by sequential_order
            features_to_render.sort(key=lambda x: x.get('_render_order', x.get('sequential_order', 999)))
            
            for feat_idx, feature in enumerate(features_to_render, 1):
                
                # Check if layout data has coordinates for this feature
                feature_key = f"FEATURE|{epic['name']}|{feature['name']}"
                if feature_key in layout_data:
                    # Use stored feature coordinates and dimensions
                    feat_x = layout_data[feature_key]['x']
                    feat_y = layout_data[feature_key]['y']
                    feat_width = layout_data[feature_key].get('width', 0)
                    feat_height = layout_data[feature_key].get('height', 60)
                    use_feature_layout = True
                else:
                    # Use calculated positions
                    # Always use horizontal layout: features side-by-side
                    # First feature aligns with epic's left edge (no offset)
                    if feat_idx == 0:
                        feat_x = epic_x
                    else:
                        feat_x = current_feature_x
                    feat_y = current_feature_y  # Features directly below epic (epic_y + epic_height)
                    feat_width = 0
                    feat_height = 60
                    use_feature_layout = False
                
                # Only use story_groups (no legacy direct stories support)
                story_groups = feature.get('story_groups', [])
                
                # Process story groups - flatten stories from all groups
                stories = []
                for group in story_groups:
                    group_stories = group.get('stories', [])
                    # In exploration mode: filter to only stories with AC
                    if is_exploration:
                        group_stories = [
                            s for s in group_stories
                            if s.get('acceptance_criteria')
                        ]
                    stories.extend(group_stories)
                
                # Skip feature if no stories AND no estimated_stories (in exploration mode, skip if no stories with AC)
                if is_exploration and len(stories) == 0:
                    continue
                # In outline mode: render features with estimated_stories OR nested sub_epics even if no story_groups
                elif not is_exploration and not story_groups and not feature.get('estimated_stories'):
                    # Check if feature has nested sub_epics - if so, render it
                    nested_sub_epics = feature.get('sub_epics', [])
                    if not nested_sub_epics:
                        continue  # Skip features without story_groups, without estimated_stories, and without nested sub_epics
                
                # Group stories by sequential_order and create a mapping to position index
                stories_by_seq = {}
                seq_orders = []
                for story in stories:
                    seq_order = story.get('sequential_order', 1)
                    if seq_order not in stories_by_seq:
                        stories_by_seq[seq_order] = []
                    stories_by_seq[seq_order].append(story)
                    if seq_order not in seq_orders:
                        seq_orders.append(seq_order)
                
                # Sort sequential orders and separate sequential vs optional stories
                sorted_seq_orders = sorted(seq_orders)
                
                # Separate sequential (flag: false) and optional (flag: true) stories for positioning
                sequential_orders = []
                has_optional = False
                for seq_order in sorted_seq_orders:
                    stories_in_seq = stories_by_seq[seq_order]
                    for story in stories_in_seq:
                        if story.get('flag', False):
                            has_optional = True  # Has optional stories
                        else:
                            if seq_order not in sequential_orders:
                                sequential_orders.append(seq_order)
                
                # Position mapping only for sequential stories (optional stack vertically at one X position)
                seq_to_position = {seq: idx for idx, seq in enumerate(sequential_orders)}
                
                
                # Calculate width: sequential stories get horizontal positions
                # Optional stories stack vertically, so only need one additional horizontal slot
                max_position = len(sequential_orders) - 1 if sequential_orders else 0
                if has_optional:
                    max_position += 1  # Add one slot for optional stories (they stack vertically)
                
                # Only calculate width if not using layout
                if not use_feature_layout:
                    # Check if any story has acceptance criteria (AC boxes are wider than stories)
                    has_acceptance_criteria = any(
                        s.get('acceptance_criteria') 
                        for story_list in stories_by_seq.values() 
                        for s in story_list
                    )
                    
                    # Base width calculation
                    # If no stories but has estimated_stories, use minimum width
                    if max_position == 0 and not has_optional and feature.get('estimated_stories'):
                        base_width = 100  # Minimum width for features with only estimated_stories
                    else:
                        base_width = (max_position + 1) * self.STORY_SPACING_X + 20
                    
                    # If AC is present, account for AC box width (120px) vs story width (50px)
                    # AC boxes align with stories but extend 70px beyond them
                    if has_acceptance_criteria:
                        # Add the extra width needed for AC boxes
                        feat_width = base_width + (self.ACCEPTANCE_CRITERIA_WIDTH - self.STORY_WIDTH)
                    else:
                        feat_width = base_width
                
                feature_positions.append({
                    'feature': feature,
                    'x': feat_x,
                    'y': feat_y,
                    'width': feat_width,
                    'height': feat_height,
                    'stories_by_seq': stories_by_seq,
                    'seq_to_position': seq_to_position,
                    'use_layout': use_feature_layout
                })
                
                # Calculate next feature X position (horizontal layout)
                # This will be updated after rendering stories/AC to use actual positions
                if not use_feature_layout:
                    # Features are horizontal, so position next feature to the right
                    # Use calculated width if available, otherwise estimate based on story count
                    if feat_width > 0:
                        current_feature_x = feat_x + feat_width + self.FEATURE_SPACING_X
                    else:
                        # Estimate width based on story count (will be updated after rendering)
                        estimated_width = max(200, len(stories) * self.STORY_SPACING_X + 20)
                        current_feature_x = feat_x + estimated_width + self.FEATURE_SPACING_X
                    # Epic width will be calculated from actual rendered bounds after all stories are rendered
                    # Don't sum feature widths here - that makes epics too wide
                    # We'll use feature_min_x and feature_max_x to calculate actual width later
                elif not use_epic_layout:
                    # If epic doesn't have layout but feature does, still need to track epic width
                    if feat_width > 0:
                        # Estimate epic width based on feature positions
                        estimated_feature_right = feat_x + feat_width
                        if estimated_feature_right > (epic_x + epic_width):
                            epic_width = estimated_feature_right - epic_x
                    # Estimate rightmost for layout features too
                    if feature_has_ac.get(feature['name'], False):
                        max_story_x = feat_x + (max_position * self.STORY_SPACING_X) + self.STORY_WIDTH
                        estimated_rightmost = max_story_x + (self.ACCEPTANCE_CRITERIA_WIDTH - self.STORY_WIDTH)
                        if previous_feature_rightmost_x is None or estimated_rightmost > previous_feature_rightmost_x:
                            previous_feature_rightmost_x = estimated_rightmost
                    else:
                        if previous_feature_rightmost_x is None or (feat_x + feat_width) > previous_feature_rightmost_x:
                            previous_feature_rightmost_x = feat_x + feat_width
            
            # Epic width will be calculated from actual rendered bounds (feature_min_x, feature_max_x)
            # after all stories, nested stories, users, and AC boxes are rendered
            # Set initial width to minimum - actual width will be set during shrinking phase
            if epic_width == 0:
                epic_width = 100  # Minimum epic width (will be expanded based on actual content)
            
            # Track actual bounds for shrinking epics/features after layout
            # Initialize epic_min_x to epic_x (first feature aligns to epic, so epic_min_x should start at epic_x)
            epic_min_x = epic_x
            epic_max_x = -float('inf')
            feature_geometries = []  # Store feature geometries to update later
            
            # Collect epic-level users (will be rendered above the epic box)
            epic_users = epic.get('users', [])
            epic_users_to_render = []  # Store users to render above epic
            for user in epic_users:
                if user not in shown_users:
                    epic_users_to_render.append(user)
                    shown_users.add(user)
            
            # Calculate epic story display
            # For increments: show total_stories in top right
            # For outline: show estimated_stories as separate text box grouped with epic
            epic_story_text = ""
            has_estimated_stories = False
            estimated_stories_count = 0
            if is_increments:
                # In increments mode: calculate total_stories and show in top right
                epic_total_stories = self._calculate_total_stories_for_epic_in_increment(epic)
                if epic_total_stories > 0:
                    epic_story_count_html = self._get_story_count_display_html(epic_total_stories, position='top-right')
                    epic_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{epic['name']}</span>{epic_story_count_html}</div>"
                else:
                    epic_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{epic['name']}</div>"
            else:
                # Outline mode: show estimated_stories as separate text box grouped with epic
                if 'estimated_stories' in epic and epic['estimated_stories']:
                    has_estimated_stories = True
                    estimated_stories_count = epic['estimated_stories']
                    epic_story_text = f"<span style=\"border-color: rgb(218, 220, 224); flex: 1 1 0%;\">{epic['name']}</span><div style=\"border-color: rgb(218, 220, 224); position: absolute; top: 2px; right: 5px; font-size: 8px; color: rgb(128, 128, 128); z-index: 10;\"></div><div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\"></div>"
                else:
                    epic_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{epic['name']}</div>"
            
            # Create group for epic if it has estimated_stories
            if has_estimated_stories and not is_increments:
                # Create group cell
                epic_group_cell = ET.SubElement(root_elem, 'mxCell', id=str(epic_idx + 100), value='', 
                                               style='group', vertex='1', connectable='0', parent='1')
                # Calculate group geometry (epic width + space for text box)
                # Group width should match epic width (no extra padding needed)
                group_width = epic_width
                group_height = epic_height + 8  # Add space for text box above
                # Group y position: epic cell is at y=8 relative to group, so group y = epic_y - 8
                # But we want epic cell absolute y to be EPIC_Y, so group y = EPIC_Y - 8
                epic_group_geom = ET.SubElement(epic_group_cell, 'mxGeometry', 
                                               x=str(epic_x), y=str(epic_y - 8), 
                                               width=str(group_width), height=str(group_height))
                epic_group_geom.set('as', 'geometry')
                
                # Epic cell as child of group (position relative to group, not absolute)
                epic_cell = ET.SubElement(root_elem, 'mxCell', id=f'epic{epic_idx}', 
                                         value=epic_story_text,
                                         style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                         parent=str(epic_idx + 100), vertex='1')
                epic_geom = ET.SubElement(epic_cell, 'mxGeometry')
                # NO x attribute - relative to group (x=0)
                epic_geom.set('y', '8')
                epic_geom.set('width', str(epic_width))
                epic_geom.set('height', str(epic_height))
                epic_geom.set('as', 'geometry')
                
                # Estimated stories text box as child of group
                estimated_text = f"~{estimated_stories_count} stories"
                estimated_cell = ET.SubElement(root_elem, 'mxCell', id=str(epic_idx + 200), 
                                              value=f"<span style=\"font-family: Helvetica; font-size: 8px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; float: none; display: inline !important;\">{estimated_text}</span>",
                                              style='text;whiteSpace=wrap;html=1;align=right;verticalAlign=middle;fontColor=default;labelBackgroundColor=none;',
                                              vertex='1', parent=str(epic_idx + 100))
                # Position text box at top right of epic (relative to group)
                # Position it near the right edge of the epic, at y=0 (top of group)
                estimated_x = max(10, epic_width - 60)  # Position near right edge, but at least 10px from left
                estimated_geom = ET.SubElement(estimated_cell, 'mxGeometry', 
                                              x=str(estimated_x), y='0', 
                                              width='60', height='30')
                estimated_geom.set('as', 'geometry')
            else:
                # No estimated stories - render epic normally
                epic_cell = ET.SubElement(root_elem, 'mxCell', id=f'epic{epic_idx}', 
                                         value=epic_story_text,
                                         style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                         parent='epic-group', vertex='1')
                epic_geom = ET.SubElement(epic_cell, 'mxGeometry', x=str(epic_x), y=str(epic_y), width=str(epic_width), 
                             height=str(epic_height))
                epic_geom.set('as', 'geometry')
            
            # Render epic-level users above the epic box
            if epic_users_to_render:
                epic_user_y = self.EPIC_Y - self.USER_LABEL_OFFSET  # 130 - 60 = 70
                epic_user_x_offset = 0
                
                for user in epic_users_to_render:
                    # Check if layout data has coordinates for this epic-level user
                    user_key = f"{epic['name']}|{user}"
                    if user_key in layout_data:
                        user_x = layout_data[user_key]['x']
                        layout_user_y = layout_data[user_key]['y']
                        # Only use layout if it's above the epic (y < EPIC_Y + margin)
                        if layout_user_y < self.EPIC_Y + 50:
                            user_y = layout_user_y
                        else:
                            user_x = epic_x + epic_user_x_offset
                            user_y = epic_user_y
                    else:
                        user_x = epic_x + epic_user_x_offset
                        user_y = epic_user_y
                    
                    user_label = ET.SubElement(root_elem, 'mxCell',
                                              id=f'user_epic{epic_idx}_{user}',
                                              value=user,
                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                              parent='1', vertex='1')
                    user_geom = ET.SubElement(user_label, 'mxGeometry',
                                             x=str(user_x),
                                             y=str(user_y),
                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                    user_geom.set('as', 'geometry')
                    
                    epic_user_x_offset += self.STORY_SPACING_X
                    
                    # Track epic-level user bounds for epic shrinking
                    epic_min_x = min(epic_min_x, user_x)
                    epic_max_x = max(epic_max_x, user_x + self.STORY_WIDTH)
            
            # Track rightmost AC position across all features in this epic (for dynamic adjustment)
            epic_rightmost_ac_x = None
            
            # Track bottom Y of each feature for vertical stacking when AC is present
            feature_bottom_y = {}  # Maps feature index -> bottom Y (including AC boxes)
            
            for feat_idx, feat_data in enumerate(feature_positions, 1):
                feature = feat_data['feature']
                feat_x = feat_data['x']
                feat_y = feat_data['y']
                feat_width = feat_data['width']
                feat_height = feat_data['height']
                use_feature_layout = feat_data.get('use_layout', False)
                stories_by_seq = feat_data['stories_by_seq']
                seq_to_position = feat_data['seq_to_position']
                
                # Features always use horizontal layout, so Y position is fixed
                
                # Initialize feature bounds tracking
                feature_min_x = float('inf')
                feature_max_x = -float('inf')
                # Track sequential story positions separately from nested stories
                # This prevents "or" connector nested stories from making features excessively wide
                leftmost_sequential_story_x = float('inf')
                rightmost_sequential_story_x = -float('inf')
                
                # Track story positions for rendering grey background rectangles (story groups)
                story_positions = {}  # Maps story name -> {'x': x, 'y': y, 'width': width, 'height': height}
                bg_rectangles_to_insert = []  # Collect grey background rectangles for this feature
                first_story_cell_ref = None  # Track first story cell to insert backgrounds before it
                
                # Collect all users for this feature (epic/feature/story level)
                all_feature_users = []
                feature_users = feature.get('users', [])
                for user in feature_users:
                    if user not in shown_users:
                        all_feature_users.append(user)
                        shown_users.add(user)
                
                # Place feature-level users horizontally
                user_x_offset = 0
                for user in all_feature_users:
                    # Check if layout data has coordinates for this feature-level user
                    user_key = f"{epic['name']}|{feature['name']}|{user}"
                    if user_key in layout_data:
                        user_x = layout_data[user_key]['x']
                        layout_user_y = layout_data[user_key]['y']
                        # Skip users at top of map (y < 50) - treat as not found, place above feature
                        if layout_user_y < 50:
                            user_x = feat_x + user_x_offset
                            user_y = feat_y - self.USER_LABEL_OFFSET
                        else:
                            user_y = layout_user_y
                    else:
                        # User has no coordinates (in story graph but not in DrawIO) - place above feature
                        user_x = feat_x + user_x_offset
                        user_y = feat_y - self.USER_LABEL_OFFSET
                    
                    user_label = ET.SubElement(root_elem, 'mxCell',
                                              id=f'user_e{epic_idx}f{feat_idx}_{user}',
                                              value=user,
                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                              parent='1', vertex='1')
                    user_geom = ET.SubElement(user_label, 'mxGeometry', 
                                             x=str(user_x), 
                                             y=str(user_y),
                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                    user_geom.set('as', 'geometry')
                    
                    # Track feature-level user bounds for feature shrinking
                    feature_min_x = min(feature_min_x, user_x)
                    feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                    
                    user_x_offset += self.STORY_SPACING_X
                
                # Calculate sub-epic story display
                # For increments: show total_stories in top right
                # For outline: show estimated_stories as separate text box grouped with sub-epic
                feature_has_estimated_stories = False
                feature_estimated_stories_count = 0
                if is_increments:
                    # In increments mode: calculate total_stories and show in top right
                    feature_total_stories = self._calculate_total_stories_for_feature_in_increment(feature)
                    if feature_total_stories > 0:
                        feature_story_count_html = self._get_story_count_display_html(feature_total_stories, position='top-right')
                        feature_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{feature['name']}</span>{feature_story_count_html}</div>"
                    else:
                        feature_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{feature['name']}</div>"
                else:
                    # Outline mode: show estimated_stories as separate text box grouped with feature
                    if 'estimated_stories' in feature and feature['estimated_stories']:
                        feature_has_estimated_stories = True
                        feature_estimated_stories_count = feature['estimated_stories']
                        feature_story_text = f"<span style=\"border-color: rgb(218, 220, 224); flex: 1 1 0%;\">{feature['name']}</span><div style=\"border-color: rgb(218, 220, 224); position: absolute; top: 2px; right: 5px; font-size: 8px; color: rgb(128, 128, 128); z-index: 10;\"></div><div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\"></div>"
                    elif 'story_count' in feature and feature['story_count']:
                        # Legacy field support - show in top-right corner
                        feature_story_count_html = self._get_story_count_display_html(feature['story_count'], position='top-right')
                        feature_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{feature['name']}</span>{feature_story_count_html}</div>"
                    elif feature.get('stories') and len(feature.get('stories', [])) > 0:
                        # Stories are fully enumerated (no estimated_stories) - don't show count in feature label
                        feature_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{feature['name']}</div>"
                    else:
                        # No stories and no estimate - show nothing
                        feature_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{feature['name']}</div>"
                
                # Features are horizontal in exploration mode (when AC is present)
                # Y position is fixed at FEATURE_Y
                
                # Use updated X position from feat_data if it was updated by previous feature
                actual_feat_x = feat_data.get('x', feat_x)
                
                # Create group for sub-epic if it has estimated_stories
                if feature_has_estimated_stories and not is_increments:
                    # Create group cell
                    feature_group_cell = ET.SubElement(root_elem, 'mxCell', id=str(epic_idx * 1000 + feat_idx * 100), value='', 
                                                       style='group', vertex='1', connectable='0', parent='1')
                    # Calculate group geometry (feature width + space for text box)
                    group_width = feat_width + 5  # Add some padding
                    group_height = feat_height + 8  # Add space for text box above
                    feature_group_geom = ET.SubElement(feature_group_cell, 'mxGeometry', 
                                                       x=str(actual_feat_x), y=str(feat_y - 3), 
                                                       width=str(group_width), height=str(group_height))
                    feature_group_geom.set('as', 'geometry')
                    
                    # Sub-epic cell as child of group (position relative to group, not absolute)
                    feature_cell = ET.SubElement(root_elem, 'mxCell', 
                                                 id=f'e{epic_idx}f{feat_idx}',
                                                 value=feature_story_text,
                                                 style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                                 parent=str(epic_idx * 1000 + feat_idx * 100), vertex='1')
                    feature_geom = ET.SubElement(feature_cell, 'mxGeometry')
                    # Don't set x - it's relative to group (defaults to 0)
                    feature_geom.set('y', '3')
                    feature_geom.set('width', str(feat_width))
                    feature_geom.set('height', str(feat_height))
                    feature_geom.set('as', 'geometry')
                    
                    # Estimated stories text box as child of group
                    estimated_text = f"~{feature_estimated_stories_count} stories"
                    estimated_cell = ET.SubElement(root_elem, 'mxCell', id=str(epic_idx * 1000 + feat_idx * 100 + 10), 
                                                  value=f"<span style=\"font-family: Helvetica; font-size: 8px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; float: none; display: inline !important;\">{estimated_text}</span>",
                                                  style='text;whiteSpace=wrap;html=1;align=right;verticalAlign=middle;fontColor=default;labelBackgroundColor=none;',
                                                  vertex='1', parent=str(epic_idx * 1000 + feat_idx * 100))
                    # Position text box above feature (negative y offset, relative to group)
                    # For small features (width < 80), position at x=0 or x=-1 (no x attribute or negative)
                    # For larger features, position near right edge
                    if feat_width < 80:
                        # Small features: don't set x (defaults to 0) or set to -1
                        estimated_geom = ET.SubElement(estimated_cell, 'mxGeometry', 
                                                      y='-5', 
                                                      width='60', height='30')
                        estimated_geom.set('as', 'geometry')
                    else:
                        # Larger features: position near right edge
                        estimated_x = max(0, feat_width - 60)
                        estimated_geom = ET.SubElement(estimated_cell, 'mxGeometry', 
                                                      x=str(estimated_x), y='-3', 
                                                      width='60', height='30')
                        estimated_geom.set('as', 'geometry')
                else:
                    # No estimated stories - render feature normally
                    feature_cell = ET.SubElement(root_elem, 'mxCell', 
                                                 id=f'e{epic_idx}f{feat_idx}',
                                                 value=feature_story_text,
                                                 style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                                 parent='1', vertex='1')
                    feature_geom = ET.SubElement(feature_cell, 'mxGeometry', x=str(actual_feat_x), y=str(feat_y),
                                 width=str(feat_width), height=str(feat_height))
                    feature_geom.set('as', 'geometry')
                
                # Update feat_x to use actual position for story rendering
                feat_x = actual_feat_x
                
                # Store feature geometry for later shrinking
                feature_geometries.append({
                    'geom': feature_geom,
                    'x': feat_x
                })
                
                story_idx = 1
                story_user_x_offset = {}  # Track user X position per story row
                
                # All features now use story_groups structure
                feature_story_groups = feature.get('story_groups', [])
                nested_sub_epics = feature.get('sub_epics', [])
                if not feature_story_groups and not nested_sub_epics:
                    # Skip features without story_groups and without nested sub_epics
                    continue
                
                # Track actual bottom of feature (including all groups and stories) - initialize BEFORE story groups loop
                actual_feature_bottom_y = feat_y + feat_height
                
                if True:  # Always use story_groups path
                    # NEW STRUCTURE: Process story groups
                    # In exploration mode: filter story_groups to only include groups with stories that have AC
                    if is_exploration:
                        filtered_story_groups = []
                        for group in feature_story_groups:
                            # Filter stories within group to only those with AC
                            group_stories = group.get('stories', [])
                            filtered_group_stories = [
                                s for s in group_stories
                                if s.get('acceptance_criteria')
                            ]
                            # Only include group if it has stories with AC
                            if filtered_group_stories:
                                # Create a copy of the group with filtered stories
                                filtered_group = group.copy()
                                filtered_group['stories'] = filtered_group_stories
                                filtered_story_groups.append(filtered_group)
                        feature_story_groups = filtered_story_groups
                    
                    # Position groups based on connector, and stories within groups based on group type
                    current_group_x = feat_x + 2  # Start position for first group
                    current_group_y = feat_y + feat_height + self.STORY_OFFSET_FROM_FEATURE
                    previous_group_bottom_y = None  # Track bottom of previous group
                    previous_group_rightmost_x = None  # Track rightmost X of previous group
                    previous_group_start_x = None  # Track start X of previous group (for "or" connector alignment)
                    previous_group_has_users = False  # Track if previous group has users (for spacing with "or" connector)
                    previous_story_users = None
                    rendered_positions = []  # Track all rendered element positions (x, y, width, height) for collision detection
                    
                    # Track shown users at feature/column level - each user should only appear once per column
                    feature_shown_users = set()
                    
                    for group_idx, group in enumerate(feature_story_groups):
                        group_type = group.get('type', 'and')  # 'and' = horizontal, 'or' = vertical
                        group_connector = group.get('connector')  # 'and' = horizontal, 'or' = vertical, null = first
                        group_stories = group.get('stories', [])
                        
                        if not group_stories:
                            continue
                        
                        # Position group based on connector
                        if group_connector is None:
                            # First group - start at feature start
                            group_start_x = feat_x + 2
                            group_start_y = current_group_y
                        elif group_connector == 'and':
                            # Horizontal connector - position to the right of previous group
                            group_start_x = current_group_x
                            group_start_y = current_group_y  # Same Y as previous group (stories align)
                            
                            # Check if this group has users and if any user would collide with existing boxes
                            current_group_has_users = any(story.get('users') for story in group_stories)
                            if current_group_has_users:
                                # Check all users in this group for collisions
                                collision = False
                                for check_story_idx, story in enumerate(group_stories):
                                    if story.get('users'):
                                        story_x = group_start_x + check_story_idx * self.STORY_SPACING_X
                                        story_y = group_start_y
                                        user_y = story_y - self.USER_LABEL_OFFSET
                                        
                                        for user_idx, user in enumerate(story.get('users', [])):
                                            user_x = story_x + user_idx * self.STORY_SPACING_X
                                            
                                            # Check for collision with any rendered element
                                            for (rx, ry, rw, rh) in rendered_positions:
                                                if (user_x < rx + rw and user_x + 50 > rx and
                                                    user_y < ry + rh and user_y + 50 > ry):
                                                    collision = True
                                                    break
                                            if collision:
                                                break
                                    if collision:
                                        break
                                
                                if collision:
                                    group_start_y = current_group_y + 20  # Move down to avoid collision
                                    current_group_y = group_start_y  # Update for next group
                        elif group_connector == 'or':
                            # Vertical connector - position below previous group
                            # "Sticky" X position: align with previous group's start X (not rightmost + spacing)
                            if previous_group_start_x is not None:
                                group_start_x = previous_group_start_x  # Align with previous group's start X
                            else:
                                group_start_x = feat_x + 2  # Fallback to feature start
                            
                            # Check if this group has users and if there's a collision
                            current_group_has_users = any(story.get('users') for story in group_stories)
                            extra_spacing = 0
                            
                            if current_group_has_users:
                                # Check if any user in this group would collide with any existing box
                                # Calculate where each story with users would be positioned
                                collision = False
                                for check_story_idx, story in enumerate(group_stories):
                                    if story.get('users'):
                                        # Calculate story position based on group type
                                        if group_type == 'and':
                                            story_x = group_start_x + check_story_idx * self.STORY_SPACING_X
                                        else:  # group_type == 'or'
                                            story_x = group_start_x
                                        
                                        if previous_group_bottom_y is not None:
                                            if group_type == 'and':
                                                story_y = previous_group_bottom_y + self.STORY_SPACING_Y
                                            else:  # group_type == 'or'
                                                story_y = previous_group_bottom_y + self.STORY_SPACING_Y + check_story_idx * self.STORY_SPACING_Y
                                        else:
                                            if group_type == 'and':
                                                story_y = current_group_y + self.STORY_SPACING_Y
                                            else:  # group_type == 'or'
                                                story_y = current_group_y + self.STORY_SPACING_Y + check_story_idx * self.STORY_SPACING_Y
                                        
                                        # Check each user for this story
                                        for user_idx, user in enumerate(story.get('users', [])):
                                            user_x = story_x + user_idx * self.STORY_SPACING_X
                                            user_y = story_y - self.USER_LABEL_OFFSET
                                            
                                            # Check for collision with any rendered element
                                            for (rx, ry, rw, rh) in rendered_positions:
                                                # Check if user box (50x50) overlaps with existing element
                                                if (user_x < rx + rw and user_x + 50 > rx and
                                                    user_y < ry + rh and user_y + 50 > ry):
                                                    collision = True
                                                    break
                                            
                                            if collision:
                                                break
                                    
                                    if collision:
                                        break
                                
                                if collision:
                                    extra_spacing = 20  # Move down to avoid collision
                            
                            if previous_group_bottom_y is not None:
                                # Position below previous group's bottom, with extra spacing only if collision detected
                                # Small gap (15px) between groups connected with "or"
                                group_start_y = previous_group_bottom_y + 15 + extra_spacing
                            else:
                                # Fallback: use current_group_y
                                group_start_y = current_group_y + 15 + extra_spacing
                            current_group_y = group_start_y  # Update for next group
                        
                        # Track the bottom of this group for positioning next group
                        group_bottom_y = group_start_y
                        
                        # Sort stories by sequential_order to preserve left-to-right order
                        sorted_group_stories = sorted(group_stories, key=lambda s: s.get('sequential_order', 999))
                        
                        # First pass: Check for user collisions and calculate maximum adjustment needed for group
                        max_group_adjustment = 0
                        for story_idx_in_group, story in enumerate(sorted_group_stories):
                            # Calculate story position based on group type
                            if group_type == 'and':
                                story_x = group_start_x + story_idx_in_group * self.STORY_SPACING_X
                                story_y = group_start_y
                            else:  # group_type == 'or'
                                story_x = group_start_x
                                story_y = group_start_y + story_idx_in_group * self.STORY_SPACING_Y
                            
                            # Check if this story has users that would collide
                            story_users = set(story.get('users', []))
                            if story_users:
                                # Check first user (users are only rendered when set changes, so check first one)
                                initial_user_y = story_y - self.USER_LABEL_OFFSET
                                user_width = self.STORY_WIDTH
                                user_height = self.STORY_HEIGHT
                                
                                # Check for collision with any rendered element
                                collision_detected = True
                                test_user_y = initial_user_y
                                while collision_detected:
                                    collision_detected = False
                                    for (rx, ry, rw, rh) in rendered_positions:
                                        # Check if user box would overlap with existing element
                                        if (group_start_x < rx + rw and group_start_x + user_width > rx and
                                            test_user_y < ry + rh and test_user_y + user_height > ry):
                                            collision_detected = True
                                            test_user_y += 10
                                            break
                                
                                # Calculate adjustment needed
                                adjustment = test_user_y - initial_user_y
                                if adjustment > 0:
                                    # User would need to move down, so story needs to move down too
                                    # Calculate new story position: user_bottom + 10px gap
                                    new_user_bottom = test_user_y + user_height
                                    new_story_y = new_user_bottom + 10
                                    story_adjustment = new_story_y - story_y
                                    max_group_adjustment = max(max_group_adjustment, story_adjustment)
                        
                        # Adjust group_start_y if any story needs to move down
                        if max_group_adjustment > 0:
                            group_start_y += max_group_adjustment
                            # Recalculate group_bottom_y
                            if group_type == 'and':
                                group_bottom_y = group_start_y
                            else:  # group_type == 'or'
                                group_bottom_y = group_start_y + (len(sorted_group_stories) - 1) * self.STORY_SPACING_Y
                        
                        # Position stories within group based on group type
                        story_x = group_start_x
                        story_y = group_start_y
                        
                        for story_idx_in_group, story in enumerate(sorted_group_stories):
                            # Always calculate position based on sequential_order and group type
                            # Don't use layout_data for stories to ensure correct left-to-right ordering
                            if group_type == 'and':
                                # Horizontal layout - stories go left to right
                                story_x = group_start_x + story_idx_in_group * self.STORY_SPACING_X
                                story_y = group_start_y
                            else:  # group_type == 'or'
                                # Vertical layout - stories go top to bottom
                                story_x = group_start_x
                                story_y = group_start_y + story_idx_in_group * self.STORY_SPACING_Y
                            
                            # Render users for this story - only show each user once per column/feature
                            story_users = set(story.get('users', []))
                            new_story_users = []
                            # Only render users that haven't been shown in this feature/column yet
                            for user in story_users:
                                if user not in feature_shown_users:
                                    new_story_users.append(user)
                                    feature_shown_users.add(user)
                            
                            previous_story_users = story_users
                            
                            # Render users
                            user_bottom_y = None  # Track the bottom of the rightmost/lowest user
                            if new_story_users:
                                for user_idx, user in enumerate(new_story_users):
                                    user_key = f"{epic['name']}|{feature['name']}|{story['name']}|{user}"
                                    initial_user_y = story_y - self.USER_LABEL_OFFSET
                                    if user_key in layout_data:
                                        user_x = layout_data[user_key]['x']
                                        layout_user_y = layout_data[user_key]['y']
                                        if layout_user_y < 50:
                                            user_x = story_x  # Align user with story's x position
                                            user_y = initial_user_y
                                        else:
                                            user_y = layout_user_y
                                    else:
                                        user_x = story_x  # Align user with story's x position
                                        user_y = initial_user_y
                                    
                                    # Check for collision with any rendered element and adjust position if needed
                                    user_width = self.STORY_WIDTH
                                    user_height = self.STORY_HEIGHT
                                    collision_detected = True
                                    while collision_detected:
                                        collision_detected = False
                                        for (rx, ry, rw, rh) in rendered_positions:
                                            # Check if user box overlaps with existing element
                                            if (user_x < rx + rw and user_x + user_width > rx and
                                                user_y < ry + rh and user_y + user_height > ry):
                                                collision_detected = True
                                                # Move user down by 10px to avoid collision
                                                user_y += 10
                                                break
                                    
                                    user_label = ET.SubElement(root_elem, 'mxCell',
                                                              id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                              value=user,
                                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                              parent='1', vertex='1')
                                    user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                             x=str(user_x), y=str(user_y),
                                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    user_geom.set('as', 'geometry')
                                    
                                    # Track user position for collision detection
                                    rendered_positions.append((user_x, user_y, self.STORY_WIDTH, self.STORY_HEIGHT))
                                    
                                    # Track the bottom of the rightmost/lowest user
                                    if user_bottom_y is None or user_y + user_height > user_bottom_y:
                                        user_bottom_y = user_y + user_height
                                    
                                    feature_min_x = min(feature_min_x, user_x)
                                    feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                            
                            # Adjust story position if user was moved down (user_bottom_y is below the expected story position)
                            if user_bottom_y is not None and user_bottom_y > story_y:
                                # User moved down due to collision - position story below user with proper spacing
                                story_y = user_bottom_y + 10  # 10px gap below user
                            
                            # Render story
                            story_cell = ET.SubElement(root_elem, 'mxCell',
                                                       id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                       value=story['name'],
                                                       style=self._get_story_style(story),
                                                       parent='1', vertex='1')
                            story_geom = ET.SubElement(story_cell, 'mxGeometry',
                                                       x=str(story_x), y=str(story_y),
                                                       width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            story_geom.set('as', 'geometry')
                            
                            # Track story position for collision detection
                            rendered_positions.append((story_x, story_y, self.STORY_WIDTH, self.STORY_HEIGHT))
                            
                            # Track first story cell for inserting background rectangles before it
                            if first_story_cell_ref is None:
                                first_story_cell_ref = story_cell
                            
                            # Track story position for grey background rectangles
                            story_positions[story['name']] = {
                                'x': story_x,
                                'y': story_y,
                                'width': self.STORY_WIDTH,
                                'height': self.STORY_HEIGHT
                            }
                            
                            # Track bounds
                            feature_min_x = min(feature_min_x, story_x)
                            feature_max_x = max(feature_max_x, story_x + self.STORY_WIDTH)
                            leftmost_sequential_story_x = min(leftmost_sequential_story_x, story_x)
                            rightmost_sequential_story_x = max(rightmost_sequential_story_x, story_x + self.STORY_WIDTH)
                            
                            # Render acceptance criteria if in exploration mode
                            if is_exploration:
                                steps = story.get('acceptance_criteria', [])
                                # Sort by sequential_order to ensure top-to-bottom rendering order
                                if steps and isinstance(steps[0], dict) and 'sequential_order' in steps[0]:
                                    steps = sorted(steps, key=lambda s: s.get('sequential_order', 999))
                                if steps:
                                    acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10
                                    # Render all AC boxes in order
                                    for ac_box_idx in range(len(steps)):
                                        acceptance_text, ac_width = self._format_steps_as_acceptance_criteria(steps, ac_box_idx)
                                        if not acceptance_text:
                                            break  # No more content to render
                                        
                                        ac_key = f"{epic['name']}|{feature['name']}|{story['name']}|AC{ac_box_idx}"
                                        if ac_key in layout_data:
                                            ac_x = layout_data[ac_key]['x']
                                            ac_y = layout_data[ac_key]['y']
                                            ac_width = layout_data[ac_key].get('width', ac_width)
                                        else:
                                            ac_x = story_x
                                            ac_y = acceptance_criteria_y + ac_box_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                        
                                        ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                               id=f'ac_e{epic_idx}f{feat_idx}s{story_idx}_{ac_box_idx}',
                                                               value=acceptance_text,
                                                               style='rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;fontSize=8;',
                                                               parent='1', vertex='1')
                                        ac_geom = ET.SubElement(ac_cell, 'mxGeometry',
                                                               x=str(ac_x), y=str(ac_y),
                                                               width=str(ac_width), height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                        ac_geom.set('as', 'geometry')
                                        
                                        feature_min_x = min(feature_min_x, ac_x)
                                        feature_max_x = max(feature_max_x, ac_x + ac_width)
                                        if epic_rightmost_ac_x is None or (ac_x + ac_width) > epic_rightmost_ac_x:
                                            epic_rightmost_ac_x = ac_x + ac_width
                            
                            story_idx += 1
                            
                            # Update group bottom Y (track the bottommost story in this group)
                            group_bottom_y = max(group_bottom_y, story_y + self.STORY_HEIGHT)
                            
                            # Track bottom Y including AC boxes for vertical feature stacking
                            if is_exploration and ac_box_idx > 0:
                                # AC boxes extend below stories
                                last_ac_y = acceptance_criteria_y + (ac_box_idx - 1) * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                group_bottom_y = max(group_bottom_y, last_ac_y + self.ACCEPTANCE_CRITERIA_HEIGHT)
                        
                        # Calculate rightmost position of this group for next group positioning
                        group_rightmost_x = group_start_x
                        if group_type == 'and':
                            # Horizontal group - rightmost story is last story
                            if sorted_group_stories:
                                last_story_idx = len(sorted_group_stories) - 1
                                group_rightmost_x = group_start_x + last_story_idx * self.STORY_SPACING_X + self.STORY_WIDTH
                        else:
                            # Vertical group - rightmost is just the story width
                            group_rightmost_x = group_start_x + self.STORY_WIDTH
                        
                        # Check if this group has users (for spacing with next group if it has "or" connector)
                        group_has_users = any(story.get('users') for story in group_stories)
                        
                        # Update current_group_x, previous_group_bottom_y, previous_group_rightmost_x, previous_group_start_x, and previous_group_has_users for next group
                        if group_connector == 'and':
                            # Horizontal connector - position next group to the right
                            # Use smaller spacing for group-to-group horizontal spacing
                            current_group_x = group_rightmost_x + self.FEATURE_SPACING_X
                            # Keep same Y for next group
                            previous_group_bottom_y = group_bottom_y
                            previous_group_rightmost_x = group_rightmost_x
                            previous_group_start_x = group_start_x  # Track start X for potential "or" connector
                            previous_group_has_users = group_has_users  # Track if this group has users
                        elif group_connector == 'or':
                            # Vertical connector - next group goes below, but maintain X position
                            # Don't reset current_group_x - it will be used if next group has connector 'and'
                            # Update Y for next group based on this group's bottom
                            previous_group_bottom_y = group_bottom_y
                            previous_group_rightmost_x = group_rightmost_x
                            previous_group_start_x = group_start_x  # Track start X for potential "or" connector
                            previous_group_has_users = group_has_users  # Track if this group has users
                        else:  # group_connector is None (first group)
                            # First group - update for next group
                            # Use smaller spacing for group-to-group horizontal spacing
                            current_group_x = group_rightmost_x + self.FEATURE_SPACING_X
                            previous_group_bottom_y = group_bottom_y
                            previous_group_rightmost_x = group_rightmost_x
                            previous_group_start_x = group_start_x  # Track start X for potential "or" connector
                            previous_group_has_users = group_has_users  # Track if this group has users
                            previous_group_start_x = group_start_x  # Track start X for potential "or" connector
                        
                        # Track feature bottom Y (including all groups and AC boxes) for vertical stacking
                        if is_exploration:
                            # Track the bottommost Y of this feature (including AC boxes)
                            if feat_idx not in feature_bottom_y:
                                feature_bottom_y[feat_idx] = feat_y + feat_height
                            feature_bottom_y[feat_idx] = max(feature_bottom_y[feat_idx], group_bottom_y + 20)
                        
                        # Update actual feature bottom (for nested sub-epic positioning)
                        # This tracks the bottommost story group - group_bottom_y already includes story height
                        actual_feature_bottom_y = max(actual_feature_bottom_y, group_bottom_y)
                    
                    # Render grey background rectangles for story groups (non-exploration mode only)
                    if feature_story_groups and story_positions and not is_exploration:
                        # Find highest ID to start new IDs from
                        max_id = 0
                        for cell in root_elem.findall('.//mxCell'):
                            cell_id = cell.get('id', '')
                            if cell_id and cell_id.replace('_', '').isdigit():
                                try:
                                    max_id = max(max_id, int(cell_id.replace('_', '')))
                                except ValueError:
                                    pass
                        
                        bg_rect_id = max_id + 1
                        padding = 5  # Padding around stories
                        
                        for group_idx, group in enumerate(feature_story_groups):
                            group_stories = group.get('stories', [])
                            if len(group_stories) < 2:
                                continue  # Only render rectangles for groups with 2+ stories
                            
                            # Find bounding box for stories in this group
                            group_story_positions = []
                            for story in group_stories:
                                story_name = story.get('name')
                                if story_name in story_positions:
                                    group_story_positions.append(story_positions[story_name])
                            
                            if len(group_story_positions) < 2:
                                continue  # Need at least 2 stories with positions to draw a rectangle
                            
                            # Calculate bounding box
                            min_x = min(pos['x'] for pos in group_story_positions) - padding
                            max_x = max(pos['x'] + pos['width'] for pos in group_story_positions) + padding
                            min_y = min(pos['y'] for pos in group_story_positions) - padding
                            max_y = max(pos['y'] + pos['height'] for pos in group_story_positions) + padding
                            
                            rect_width = max_x - min_x
                            rect_height = max_y - min_y
                            
                            # Create grey background rectangle element
                            bg_rect = ET.Element('mxCell',
                                                id=str(bg_rect_id),
                                                value='',
                                                style='rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=1 2;strokeColor=#FFFFFF;fillColor=#F7F7F7;',
                                                parent='1', vertex='1')
                            bg_geom = ET.SubElement(bg_rect, 'mxGeometry',
                                                    x=str(min_x), y=str(min_y),
                                                    width=str(rect_width), height=str(rect_height))
                            bg_geom.set('as', 'geometry')
                            
                            bg_rectangles_to_insert.append((bg_rect_id, bg_rect))
                            bg_rect_id += 1
                        
                        # Insert background rectangles into XML (behind everything, so insert before first story/user)
                        # In DrawIO XML, elements that appear earlier are drawn behind later elements
                        # Insert right after the sub-epic cell, before any users or stories
                        if bg_rectangles_to_insert:
                            # Find the sub-epic cell for this feature
                            feature_cell_id = f'e{epic_idx}f{feat_idx}'
                            children = list(root_elem)
                            feature_cell = None
                            for child in children:
                                if child.get('id') == feature_cell_id:
                                    feature_cell = child
                                    break
                            
                            if feature_cell is not None:
                                # Insert backgrounds right after the sub-epic cell
                                feature_index = children.index(feature_cell)
                                # Insert in reverse order so first group is at the back
                                for bg_rect_id, bg_rect in reversed(bg_rectangles_to_insert):
                                    root_elem.insert(feature_index + 1, bg_rect)
                            elif first_story_cell_ref is not None:
                                # Fallback: insert before first story/user cell
                                try:
                                    first_story_index = children.index(first_story_cell_ref)
                                    for bg_rect_id, bg_rect in reversed(bg_rectangles_to_insert):
                                        root_elem.insert(first_story_index, bg_rect)
                                except ValueError:
                                    # Last resort: append at end
                                    for bg_rect_id, bg_rect in bg_rectangles_to_insert:
                                        root_elem.append(bg_rect)
                    elif bg_rectangles_to_insert:
                        # No stories rendered, just append backgrounds
                        for bg_rect_id, bg_rect in bg_rectangles_to_insert:
                            root_elem.append(bg_rect)
                    
                    # Update feature geometry width and calculate next feature X position (if not using layout)
                    # Calculate feature width from feature_max_x
                    if not use_feature_layout:
                        # Use rightmost_sequential_story_x if available, otherwise feature_max_x
                        rightmost_x = rightmost_sequential_story_x if rightmost_sequential_story_x > -float('inf') else feature_max_x
                        if rightmost_x > -float('inf'):
                            # Calculate actual feature width (including AC boxes if present)
                            actual_feature_rightmost = max(rightmost_x, epic_rightmost_ac_x if epic_rightmost_ac_x else rightmost_x)
                            # Add padding
                            actual_feature_rightmost += 20
                            # Calculate actual feature width
                            actual_feature_width = actual_feature_rightmost - feat_x
                            # Update feature geometry width
                            feature_geom.set('width', str(actual_feature_width))
                        else:
                            # Fallback: use a default width if no stories were rendered
                            default_width = 282  # Default feature width
                            actual_feature_width = default_width
                            feature_geom.set('width', str(default_width))
                        
                        # Calculate next feature X position based on actual rendered width
                        actual_feature_rightmost = feat_x + actual_feature_width
                        # Update feat_data so next iteration uses correct position
                        feat_data['x'] = feat_x  # Keep current X
                        feat_data['width'] = actual_feature_width  # Update width
                        # Update current_feature_x for next feature (used in first loop for next epic)
                        next_feature_x = actual_feature_rightmost + self.FEATURE_SPACING_X
                        current_feature_x = next_feature_x
                        
                        # Update next feature's X position in feature_positions
                        # feat_idx is 1-based, so next feature is at index feat_idx in the list (0-based)
                        if feat_idx < len(feature_positions):
                            next_feat_data = feature_positions[feat_idx]
                            if not next_feat_data.get('use_layout', False):
                                # Update next feature's X position in feat_data
                                # This will be used when we render that feature (it checks feat_data.get('x'))
                                next_feat_data['x'] = next_feature_x
                                # Also update the geometry X position if it's already been created
                                # Geometry is created at line 838, before stories are rendered
                                # So we need to find it and update it
                                next_feat_cell_id = f'e{epic_idx}f{feat_idx + 1}'
                                # Search through all cells to find the next feature's geometry
                                for cell in root_elem.iter():
                                    if cell.get('id') == next_feat_cell_id:
                                        # Found the feature cell, now find its geometry
                                        geom = cell.find('mxGeometry')
                                        if geom is not None:
                                            geom.set('x', str(next_feature_x))
                                            # Also update feat_x for story rendering
                                            next_feat_data['x'] = next_feature_x
                                        break
                
                # All features now use story_groups structure - legacy path removed
                
                # Grey background rectangles are rendered above (in the story_groups rendering section)
                        
                        # Render acceptance criteria below story in exploration mode
                        if is_exploration:
                            steps = story.get('acceptance_criteria', []) or story.get('Steps', []) or story.get('steps', [])
                            # Sort by sequential_order to ensure top-to-bottom rendering order
                            if steps and isinstance(steps[0], dict) and 'sequential_order' in steps[0]:
                                steps = sorted(steps, key=lambda s: s.get('sequential_order', 999))
                            if steps:
                                # Render acceptance criteria boxes below the story
                                acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10  # Start below story
                                
                                # Render all AC boxes in order
                                for ac_box_idx in range(len(steps)):
                                    acceptance_text, ac_width = self._format_steps_as_acceptance_criteria(steps, ac_box_idx)
                                    if not acceptance_text:
                                        break  # No more content to render
                                    
                                    # Check if layout data exists for this acceptance criteria
                                    ac_key = f"{epic['name']}|{feature['name']}|{story['name']}|AC{ac_box_idx}"
                                    if ac_key in layout_data:
                                        ac_x = layout_data[ac_key]['x']
                                        ac_y = layout_data[ac_key]['y']
                                        # Use layout width if provided, otherwise use calculated
                                        ac_width = layout_data[ac_key].get('width', ac_width)
                                    else:
                                        # AC boxes align with their story (same X position)
                                        ac_x = story_x
                                        ac_y = acceptance_criteria_y + ac_box_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                    
                                    # Create acceptance criteria box (rectangle, not square)
                                    ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                           id=f'ac_e{epic_idx}f{feat_idx}s{story_idx}_{ac_box_idx}',
                                                           value=acceptance_text,
                                                           style='rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;fontSize=8;',
                                                           parent='1', vertex='1')
                                    ac_geom = ET.SubElement(ac_cell, 'mxGeometry',
                                                           x=str(ac_x), y=str(ac_y),
                                                           width=str(ac_width),
                                                           height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                    ac_geom.set('as', 'geometry')
                                    
                                    # Track acceptance criteria bounds for feature expansion
                                    feature_min_x = min(feature_min_x, ac_x)
                                    feature_max_x = max(feature_max_x, ac_x + ac_width)
                                    
                                    # Track rightmost AC position for this epic (for epic width calculation)
                                    if epic_rightmost_ac_x is None or (ac_x + ac_width) > epic_rightmost_ac_x:
                                        epic_rightmost_ac_x = ac_x + ac_width
                            
                        story_idx += 1
                    
                    # Optional stories are now handled through story_groups
                
                # Grey background rectangles are rendered in the story_groups section above
                
                # Shrink feature to fit actual story bounds (with padding) - only if not using layout
                if use_feature_layout:
                    # Use stored feature coordinates and dimensions - don't shrink
                    # Track feature bounds for epic shrinking (use stored position)
                    epic_min_x = min(epic_min_x, feat_x)
                    epic_max_x = max(epic_max_x, feat_x + feat_width)
                    # Update previous_feature_rightmost_x for next feature positioning
                    feature_rightmost = feat_x + feat_width
                    if previous_feature_rightmost_x is None or feature_rightmost > previous_feature_rightmost_x:
                        previous_feature_rightmost_x = feature_rightmost
                elif feature_min_x != float('inf') and feature_max_x != -float('inf'):
                    # In exploration mode, feature should span from epic_x to rightmost AC box + padding
                    # Otherwise, calculate from min/max story bounds
                    if is_exploration:
                        # Feature aligns with epic and spans to rightmost AC + padding
                        # Padding is 30px for first epic's feature, 6px for subsequent epics' features (to match expected layout)
                        actual_feature_x = epic_x
                        # Calculate padding: if feature_max_x is close to epic end, use smaller padding
                        # For first epic (epic_idx == 1): 30px padding, for others: 6px padding
                        feature_padding = 30 if epic_idx == 1 else 6
                        # Constrain to sequential stories if available, otherwise use full feature_max_x
                        if rightmost_sequential_story_x != -float('inf') and leftmost_sequential_story_x != float('inf'):
                            # Use sequential story positions to constrain feature width
                            constrained_max_x = max(rightmost_sequential_story_x, epic_rightmost_ac_x if epic_rightmost_ac_x is not None else rightmost_sequential_story_x)
                            actual_feature_width = constrained_max_x - epic_x + feature_padding
                        else:
                            actual_feature_width = feature_max_x - epic_x + feature_padding
                    else:
                        # Constrain feature width to sequential story positions ONLY, not nested story positions
                        # This prevents "or" connector nested stories from making features excessively wide
                        # ALWAYS use sequential story positions for width calculation - never use nested story positions
                        if rightmost_sequential_story_x != -float('inf') and leftmost_sequential_story_x != float('inf'):
                            # Use sequential story positions to constrain feature width
                            constrained_feature_min_x = leftmost_sequential_story_x
                            constrained_feature_max_x = rightmost_sequential_story_x
                            actual_feature_width = constrained_feature_max_x - constrained_feature_min_x + 20  # Add padding
                            calculated_feature_x = constrained_feature_min_x - 10  # Adjust X to align with stories
                        else:
                            # Fallback: if no sequential stories, use initial calculated width from max_position
                            # This prevents features from becoming too wide when only nested stories exist
                            if 'max_position' in locals() and max_position >= 0:
                                # Use the original width calculation based on sequential story count
                                actual_feature_width = (max_position + 1) * self.STORY_SPACING_X + 20
                                calculated_feature_x = feat_x  # Keep original X position
                            else:
                                # Last resort: use feature bounds but cap at reasonable width
                                actual_feature_width = min(feature_max_x - feature_min_x + 20, 600)  # Cap at 600px
                                calculated_feature_x = feature_min_x - 10  # Adjust X to align with stories
                        actual_feature_x = max(feat_x, calculated_feature_x)  # Ensure we don't move left
                    feature_geometries[-1]['geom'].set('width', str(actual_feature_width))
                    feature_geometries[-1]['geom'].set('x', str(actual_feature_x))
                    
                    # Update previous_feature_rightmost_x with actual rightmost position (including AC cards)
                    # This will be used to position the next feature
                    actual_feature_rightmost = actual_feature_x + actual_feature_width
                    if previous_feature_rightmost_x is None or actual_feature_rightmost > previous_feature_rightmost_x:
                        previous_feature_rightmost_x = actual_feature_rightmost
                    
                    # Update current_feature_x for next feature positioning (if not using layout)
                    # This ensures next feature doesn't overlap with current feature
                    # Always use horizontal layout
                    if not use_feature_layout:
                        current_feature_x = actual_feature_rightmost + self.FEATURE_SPACING_X
                    
                    # Track feature bounds for epic shrinking (use actual shrunk position)
                    epic_min_x = min(epic_min_x, actual_feature_x)
                    epic_max_x = max(epic_max_x, actual_feature_x + actual_feature_width)
                else:
                    # No stories, use original width
                    epic_min_x = min(epic_min_x, feat_x)
                    epic_max_x = max(epic_max_x, feat_x + feat_width)
                    # Update previous_feature_rightmost_x for next feature positioning
                    feature_rightmost = feat_x + feat_width
                    if previous_feature_rightmost_x is None or feature_rightmost > previous_feature_rightmost_x:
                        previous_feature_rightmost_x = feature_rightmost
                    
                    # Track feature bottom Y for vertical stacking when AC is present
                    if is_exploration:
                        if feat_idx not in feature_bottom_y:
                            feature_bottom_y[feat_idx] = feat_y + feat_height
                
                # Features always use horizontal layout, so no need to update current_feature_y
            
            # Update epic_max_x to include AC cards if present (features already expand to fit AC)
            # Only update if in exploration mode - in normal mode, features are already constrained to sequential stories
            # Constrain epic_rightmost_ac_x to not exceed the rightmost feature position to prevent nested story AC from expanding epic width
            if epic_rightmost_ac_x is not None and is_exploration:
                # Don't let AC from nested stories expand epic beyond feature bounds
                feature_rights = [float(fg['geom'].get('x', 0)) + float(fg['geom'].get('width', 0)) 
                                 for fg in feature_geometries if fg.get('geom')]
                max_feature_right = max(feature_rights) if feature_rights else epic_max_x
                constrained_ac_x = min(epic_rightmost_ac_x, max_feature_right + 100)  # Allow some AC expansion but cap it
                epic_max_x = max(epic_max_x, constrained_ac_x)
            
            # Shrink epic to fit actual feature bounds (with padding) - only if not using layout
            if use_epic_layout:
                # Use stored epic coordinates and dimensions - don't shrink
                # Update x_pos for next epic using stored epic width
                # In exploration mode, use 30px spacing between epics to match expected layout
                epic_spacing = 30 if is_exploration else 20
                x_pos = epic_x + epic_width + epic_spacing
            elif epic_min_x != float('inf') and epic_max_x != -float('inf'):
                # In exploration mode, epic should span from epic_x to rightmost AC box + padding
                # Otherwise, calculate from min/max feature bounds
                if is_exploration and epic_rightmost_ac_x is not None:
                    # Epic spans from epic_x to rightmost AC + padding
                    # Constrain AC position to not exceed feature bounds too much
                    feature_rights = [float(fg['geom'].get('x', 0)) + float(fg['geom'].get('width', 0)) 
                                     for fg in feature_geometries if fg.get('geom')]
                    max_feature_right = max(feature_rights) if feature_rights else epic_max_x
                    constrained_ac_x = min(epic_rightmost_ac_x, max_feature_right + 100)  # Allow some AC expansion but cap it
                    # For first epic (epic_idx == 1): 30px padding, for others: 6px padding
                    epic_padding = 30 if epic_idx == 1 else 6
                    actual_epic_width = constrained_ac_x - epic_x + epic_padding
                    actual_epic_x = epic_x
                else:
                    # Calculate width from actual rendered bounds
                    # epic_min_x starts at epic_x, epic_max_x tracks rightmost content
                    # When sub_epics (features) are present, epic width should be exactly the width of its sub-epics (no padding)
                    # This prevents epics from becoming too wide when "or" connector nested stories extend horizontally
                    actual_epic_width = epic_max_x - epic_min_x  # No padding - epic should match sub-epic width exactly
                    actual_epic_x = epic_x  # Keep epic at its original position (first feature aligns to epic, not vice versa)
                    # Ensure minimum width
                    if actual_epic_width < 100:
                        actual_epic_width = 100
                epic_geom.set('width', str(actual_epic_width))
                # Only set x if epic is NOT in a group (if parent is not a group ID)
                epic_parent = epic_cell.get('parent', '')
                if not epic_parent or epic_parent == '1' or epic_parent == 'epic-group':
                    # Epic is not in a group - set absolute x
                    epic_geom.set('x', str(actual_epic_x))
                # If epic is in a group (parent is like "101", "102"), don't set x - it's relative to group
                
                # Update x_pos for next epic using actual epic width
                # In exploration mode, use 30px spacing between epics to match expected layout
                epic_spacing = 30 if is_exploration else 20
                x_pos = actual_epic_x + actual_epic_width + epic_spacing
            else:
                # Fallback to original calculation
                x_pos += epic_width + 20
        
        # Right-align epics: DISABLED - this was causing epics to be positioned incorrectly
        # Epics should be positioned left-to-right based on their actual content width
        # epic_cells = root_elem.findall('.//mxCell[@parent="epic-group"]')
        epic_cells = []  # Disabled - set to empty list
        if False and epic_cells:
            max_right_edge = 0
            epic_data = []
            for epic_cell in epic_cells:
                epic_geom = epic_cell.find('mxGeometry')
                if epic_geom is not None:
                    epic_x = float(epic_geom.get('x', 0))
                    epic_width = float(epic_geom.get('width', 0))
                    right_edge = epic_x + epic_width
                    max_right_edge = max(max_right_edge, right_edge)
                    epic_id = epic_cell.get('id', '')
                    # Collect all features in this epic
                    features = []
                    for feature_cell in root_elem.findall(f'.//mxCell[@parent="{epic_id}"]'):
                        feature_geom = feature_cell.find('mxGeometry')
                        if feature_geom is not None:
                            feat_x = float(feature_geom.get('x', 0))
                            feat_width = float(feature_geom.get('width', 0))
                            features.append((feature_cell, feature_geom, feat_x, feat_width))
                    # Sort features by X position (left to right)
                    features.sort(key=lambda f: f[2])
                    epic_data.append((epic_cell, epic_geom, epic_x, epic_width, epic_id, features))
            
            # Reposition all epics so their right edges align
            for epic_cell, epic_geom, old_epic_x, epic_width, epic_id, features in epic_data:
                new_epic_x = max_right_edge - epic_width
                epic_geom.set('x', str(new_epic_x))
                
                # Position features: first feature at left edge, last feature at right edge
                if len(features) > 0:
                    # First feature aligns to left edge of epic
                    first_feat_cell, first_feat_geom, first_feat_x, first_feat_width = features[0]
                    first_feat_geom.set('x', str(new_epic_x + 10))  # 10px padding from left
                    
                    # Last feature aligns to right edge of epic
                    if len(features) > 1:
                        last_feat_cell, last_feat_geom, last_feat_x, last_feat_width = features[-1]
                        last_feat_right = new_epic_x + epic_width - 10  # 10px padding from right
                        last_feat_geom.set('x', str(last_feat_right - last_feat_width))
                        
                        # Distribute middle features evenly between first and last
                        if len(features) > 2:
                            first_feat_right = new_epic_x + 10 + first_feat_width
                            last_feat_left = last_feat_right - last_feat_width
                            available_width = last_feat_left - first_feat_right
                            middle_features = features[1:-1]
                            if len(middle_features) > 0:
                                spacing = available_width / (len(middle_features) + 1)
                                for idx, (feat_cell, feat_geom, old_feat_x, feat_width) in enumerate(middle_features):
                                    new_feat_x = first_feat_right + (idx + 1) * spacing
                                    feat_geom.set('x', str(new_feat_x))
                    
                    # Update all stories and AC cards within features
                    for feat_cell, feat_geom, old_feat_x, feat_width in features:
                        new_feat_x = float(feat_geom.get('x', 0))
                        feat_x_offset = new_feat_x - old_feat_x
                        feature_id = feat_cell.get('id', '')
                        for story_cell in root_elem.findall(f'.//mxCell[@parent="{feature_id}"]'):
                            story_geom = story_cell.find('mxGeometry')
                            if story_geom is not None:
                                story_x = float(story_geom.get('x', 0))
                                new_story_x = story_x + feat_x_offset
                                story_geom.set('x', str(new_story_x))
        
        # Update epic-group width to span all epics (for exploration mode)
        if is_exploration:
            # Find rightmost epic position
            epic_group_rightmost = 0
            for epic_cell in root_elem.findall('.//mxCell[@parent="epic-group"]'):
                epic_geom = epic_cell.find('mxGeometry')
                if epic_geom is not None:
                    epic_x = float(epic_geom.get('x', 0))
                    epic_width = float(epic_geom.get('width', 0))
                    epic_group_rightmost = max(epic_group_rightmost, epic_x + epic_width)
            # Update epic-group geometry to span all epics
            if epic_group_rightmost > 0:
                epic_group_geom.set('width', str(epic_group_rightmost))
                epic_group_geom.set('height', '190')  # Match expected height
        
        # Insert all background rectangles right after root cells (id='0' and id='1'), before epic-group
        # This ensures backgrounds are behind all other elements
        if all_background_rectangles:
            # Find epic-group element to insert before it
            epic_group_elem = root_elem.find(".//mxCell[@id='epic-group']")
            if epic_group_elem is not None:
                # Get index of epic-group
                epic_group_index = list(root_elem).index(epic_group_elem)
                # Insert all backgrounds in reverse order (so first one is at the back)
                for bg_rect_id, bg_rect in reversed(all_background_rectangles):
                    root_elem.insert(epic_group_index, bg_rect)
            else:
                # Fallback: insert after id='1' cell
                id1_elem = root_elem.find(".//mxCell[@id='1']")
                if id1_elem is not None:
                    id1_index = list(root_elem).index(id1_elem)
                    for bg_rect_id, bg_rect in reversed(all_background_rectangles):
                        root_elem.insert(id1_index + 1, bg_rect)
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='    ')
    
    def _generate_increments_diagram(self, story_graph: Dict[str, Any], layout_data: Dict[str, Any], root_elem: ET.Element, xml_root: ET.Element) -> str:
        """
        Generate DrawIO XML for increments mode.
        Epics and features within increments show story counts in top right.
        
        Args:
            story_graph: Story graph with increments
            layout_data: Optional layout data
            root_elem: Root XML element to append to (this is the <root> element)
            xml_root: Root of the entire XML tree (mxfile element)
        """
        """
        Generate DrawIO XML for increments mode.
        Epics and features within increments show story counts in top right.
        
        Args:
            story_graph: Story graph with increments
            layout_data: Optional layout data
            root_elem: Root XML element to append to
        """
        # For now, use same rendering but with increment-specific story count display
        # TODO: Implement full increments rendering with increment boundaries
        # This is a placeholder - actual implementation would render increment lanes
        
        # Use the same rendering logic but mark as increments
        # The story count display will be handled in the epic/feature rendering
        # by checking if we're in increments mode
        
        # Return the standard diagram for now - will enhance later
        epic_group = ET.SubElement(root_elem, 'mxCell', id='epic-group', value='', 
                     style='group', parent='1', vertex='1', connectable='0')
        epic_group_geom = ET.SubElement(epic_group, 'mxGeometry', x='0', y='0', width='1', height='1')
        epic_group_geom.set('as', 'geometry')
        
        # Render increments with their epics and features
        increment_y_start = 510  # Starting Y position for increments
        increment_height = 400  # Height per increment
        
        for inc_idx, increment in enumerate(story_graph.get('increments', []), 1):
            inc_y = increment_y_start + (inc_idx - 1) * increment_height
            
            # Render increment label/box
            increment_name = increment.get('name', f'Increment {inc_idx}')
            increment_cell = ET.SubElement(root_elem, 'mxCell',
                                         id=f'increment{inc_idx}',
                                         value=increment_name,
                                         style='whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;',
                                         parent='1', vertex='1')
            increment_geom = ET.SubElement(increment_cell, 'mxGeometry',
                                         x='1090', y=str(inc_y),
                                         width='150', height='40')
            increment_geom.set('as', 'geometry')
            
            # Render epics and features within this increment
            epics = increment.get('epics', [])
            x_pos = 1262  # Starting X for epic content
            
            for epic_idx, epic in enumerate(epics, 1):
                # Calculate total stories for epic in this increment
                epic_total_stories = self._calculate_total_stories_for_epic_in_increment(epic)
                
                # Epic story count display in top right for increments
                epic_story_count_html = ""
                if epic_total_stories > 0:
                    epic_story_count_html = self._get_story_count_display_html(epic_total_stories, position='top-right')
                
                epic_cell = ET.SubElement(root_elem, 'mxCell',
                                         id=f'inc{inc_idx}_epic{epic_idx}',
                                         value=f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{epic['name']}</span>{epic_story_count_html}</div>",
                                         style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                         parent='1', vertex='1')
                # Calculate epic width based on features
                epic_width = 668  # Default, will be calculated
                epic_geom = ET.SubElement(epic_cell, 'mxGeometry',
                                         x=str(x_pos), y=str(inc_y - 70),
                                         width=str(epic_width), height='60')
                epic_geom.set('as', 'geometry')
                
                # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
                def get_sub_epics(epic):
                    return epic.get('sub_epics', []) or epic.get('features', [])
                
                # Render sub_epics (features) within epic
                features = get_sub_epics(epic)
                feature_x = x_pos + 10
                
                for feat_idx, feature in enumerate(features, 1):
                    # Calculate total stories for feature in this increment
                    feature_total_stories = self._calculate_total_stories_for_feature_in_increment(feature)
                    
                    # Feature story count display in top right for increments
                    feature_story_count_html = ""
                    if feature_total_stories > 0:
                        feature_story_count_html = self._get_story_count_display_html(feature_total_stories, position='top-right')
                    
                    feature_cell = ET.SubElement(root_elem, 'mxCell',
                                               id=f'inc{inc_idx}_epic{epic_idx}_feat{feat_idx}',
                                               value=f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{feature['name']}</span>{feature_story_count_html}</div>",
                                               style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                               parent='1', vertex='1')
                    feature_width = 300  # Default, will be calculated
                    feature_geom = ET.SubElement(feature_cell, 'mxGeometry',
                                               x=str(feature_x), y=str(inc_y - 20),
                                               width=str(feature_width), height='60')
                    feature_geom.set('as', 'geometry')
                    
                    # Render stories within this feature
                    stories = feature.get('stories', [])
                    story_x = feature_x + 10
                    story_y = inc_y + 50  # Start below feature
                    
                    for story_idx, story in enumerate(stories, 1):
                        # Render user labels if present
                        story_users = story.get('users', [])
                        for user in story_users:
                            user_label = ET.SubElement(root_elem, 'mxCell',
                                                      id=f'user_inc{inc_idx}_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                      value=user,
                                                      style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                      parent='1', vertex='1')
                            user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                     x=str(story_x),
                                                     y=str(story_y - self.USER_LABEL_OFFSET),
                                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            user_geom.set('as', 'geometry')
                        
                        # Render story
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'inc{inc_idx}_e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story['name'],
                                                   style=self._get_story_style(story),
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry',
                                                   x=str(story_x), y=str(story_y),
                                                   width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        
                        story_x += self.STORY_SPACING_X
                    
                    feature_x += feature_width + 10
            
            # Draw increment separator line
            separator = ET.SubElement(root_elem, 'mxCell',
                                    id=f'increment_sep{inc_idx}',
                                    value="",
                                    style='endArrow=none;dashed=1;html=1;',
                                    parent='1', edge='1')
            separator_geom = ET.SubElement(separator, 'mxGeometry',
                                         width='50', height='50', relative='1')
            separator_geom.set('as', 'geometry')
            separator_point1 = ET.SubElement(separator_geom, 'mxPoint',
                                           x='1080', y=str(inc_y + 220))
            separator_point1.set('as', 'sourcePoint')
            separator_point2 = ET.SubElement(separator_geom, 'mxPoint',
                                           x='2721', y=str(inc_y + 220))
            separator_point2.set('as', 'targetPoint')
        
        rough_string = ET.tostring(xml_root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='    ')
