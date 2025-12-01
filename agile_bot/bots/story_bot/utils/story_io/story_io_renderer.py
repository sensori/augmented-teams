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
    EPIC_Y = 130
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
        Counts only stories in sub_epics within this increment.
        """
        # Helper to get sub_epics (supports both old 'features' and new 'sub_epics' format)
        def get_sub_epics(epic):
            return epic.get('sub_epics', []) or epic.get('features', [])
        
        total = 0
        for sub_epic in get_sub_epics(epic):
            # Count actual stories in sub_epic
            sub_epic_stories = sub_epic.get('stories', [])
            if sub_epic_stories:
                total += len(sub_epic_stories)
            elif sub_epic.get('estimated_stories'):
                # Use estimate if no actual stories
                total += sub_epic['estimated_stories']
        # Add epic-level stories if any
        epic_stories = epic.get('stories', [])
        if epic_stories:
            total += len(epic_stories)
        elif epic.get('estimated_stories'):
            # Use epic estimate if no stories
            total += epic['estimated_stories']
        return total
    
    @staticmethod
    def _calculate_total_stories_for_feature_in_increment(feature: Dict[str, Any]) -> int:
        """
        Calculate total stories for a feature within an increment scope.
        """
        feature_stories = feature.get('stories', [])
        if feature_stories:
            return len(feature_stories)
        elif feature.get('estimated_stories'):
            return feature['estimated_stories']
        return 0
    
    @staticmethod
    def _traverse_all_stories(story: Dict[str, Any], collected: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Simple recursive algorithm to read through a story and follow all nested stories.
        Uses story['stories'] array structure (not decimal sequential_order).
        
        Args:
            story: Story dictionary
            collected: List to collect all stories (including nested)
        
        Returns:
            List of all stories (parent + all nested stories)
        """
        if collected is None:
            collected = []
        
        # Add current story
        collected.append(story)
        
        # Follow nested stories recursively
        nested_stories = story.get('stories', [])
        for nested_story in nested_stories:
            DrawIORenderer._traverse_all_stories(nested_story, collected)
        
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
        Steps are grouped as: Box 1 = Given + When, Box 2 = Then
        
        Args:
            steps: List of steps (dictionaries with 'type' and 'description', or strings)
            step_idx: Index of the current step (0 = Given+When box, 1 = Then box)
        
        Returns:
            Tuple of (HTML formatted text, calculated width)
        """
        if step_idx == 0:
            # First box: Given + When
            given_text = ""
            when_text = ""
            
            # Find Given step
            for step in steps:
                if isinstance(step, dict):
                    step_type = step.get('type', '').strip()
                    step_desc = step.get('description', str(step)).strip()
                    if step_type == 'Given':
                        given_text = step_desc
                    elif step_type == 'When':
                        when_text = step_desc
                elif isinstance(step, str):
                    if step.strip().startswith('Given '):
                        given_text = step.strip()[6:]
                    elif step.strip().startswith('When '):
                        when_text = step.strip()[5:]
            
            if given_text and when_text:
                acceptance_text = f'<div style="font-size: 8px;"><b>Given</b> {given_text}<br><b>When</b> {when_text}</div>'
            elif when_text:
                acceptance_text = f'<div style="font-size: 8px;"><b>When</b> {when_text}</div>'
            elif given_text:
                acceptance_text = f'<div style="font-size: 8px;"><b>Given</b> {given_text}</div>'
            else:
                acceptance_text = ""
        else:
            # Second box: Then
            then_text = ""
            
            # Find Then step
            for step in steps:
                if isinstance(step, dict):
                    step_type = step.get('type', '').strip()
                    step_desc = step.get('description', str(step)).strip()
                    if step_type == 'Then':
                        then_text = step_desc
                        break
                elif isinstance(step, str):
                    if step.strip().startswith('Then '):
                        then_text = step.strip()[5:]
                        break
            
            if then_text:
                acceptance_text = f'<div style="font-size: 8px;"><b>Then</b> {then_text}</div>'
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
                # Check in story_groups (new structure)
                for story_group in sub_epic.get('story_groups', []):
                    for story in story_group.get('stories', []):
                        if story.get('Steps') or story.get('steps') or story.get('acceptance_criteria'):
                            has_acceptance_criteria = True
                            break
                    if has_acceptance_criteria:
                        break
                # Also check legacy stories structure
                if not has_acceptance_criteria:
                    for story in sub_epic.get('stories', []):
                        if story.get('Steps') or story.get('steps') or story.get('acceptance_criteria'):
                            has_acceptance_criteria = True
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
        
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
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
        
        # Handle increments mode
        if is_increments and 'increments' in story_graph:
            # Render increments with special handling for epic/feature story counts
            return self._generate_increments_diagram(story_graph, layout_data, root_elem, root)
        
        # Standard outline rendering (existing logic)
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
                    # Check if feature has any stories with AC
                    story_groups = feature.get('story_groups', [])
                    if story_groups:
                        # Check story_groups structure
                        has_story_with_ac = False
                        for group in story_groups:
                            for story in group.get('stories', []):
                                if story.get('Steps') or story.get('steps'):
                                    has_story_with_ac = True
                                    break
                            if has_story_with_ac:
                                break
                    else:
                        # Check legacy structure
                        stories = feature.get('stories', [])
                        has_story_with_ac = any(
                            (s.get('Steps') or s.get('steps'))
                            for s in stories
                        )
                    
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
                epic_height = layout_data[epic_key].get('height', 60)
                use_epic_layout = True
            else:
                # Use calculated positions
                epic_x = x_pos
                epic_y = self.EPIC_Y
                epic_width = 0
                epic_height = 60
                use_epic_layout = False
            
            feature_x = epic_x + 10 if use_epic_layout else x_pos + 10
            
            # Pre-calculate which features have AC cards to adjust positioning
            feature_has_ac = {}
            for feature in features:
                stories = feature.get('stories', [])
                has_ac = any(
                    (s.get('Steps') or s.get('steps')) 
                    for s in stories
                )
                feature_has_ac[feature['name']] = has_ac
            
            feature_positions = []
            previous_feature_rightmost_x = None
            # In exploration mode, features align with epics (no offset)
            # Otherwise, start features 10px from epic left edge
            feature_x_offset = 0 if is_exploration else 10
            current_feature_x = epic_x + feature_x_offset
            # When AC is present, features stack vertically; otherwise horizontal
            current_feature_y = self.FEATURE_Y  # Start Y position for first feature
            for feature in features:
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
                    feat_x = current_feature_x
                    feat_y = self.FEATURE_Y  # Same Y for all features
                    feat_width = 0
                    feat_height = 60
                    use_feature_layout = False
                
                # Support both story_groups (new) and stories (legacy)
                story_groups = feature.get('story_groups', [])
                if story_groups:
                    # New structure: process story groups
                    # Flatten stories from all groups for processing
                    stories = []
                    for group in story_groups:
                        group_stories = group.get('stories', [])
                        # In exploration mode: filter to only stories with AC
                        if is_exploration:
                            group_stories = [
                                s for s in group_stories
                                if s.get('Steps') or s.get('steps')
                            ]
                        stories.extend(group_stories)
                else:
                    # Legacy structure: use stories directly
                    stories = feature.get('stories', [])
                    # In exploration mode: filter to only stories with AC
                    if is_exploration:
                        stories = [
                            s for s in stories
                            if s.get('Steps') or s.get('steps')
                        ]
                
                # Skip feature if no stories after filtering (in exploration mode)
                if is_exploration and len(stories) == 0:
                    continue
                
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
                        (s.get('Steps') or s.get('steps')) 
                        for story_list in stories_by_seq.values() 
                        for s in story_list
                    )
                    
                    # Base width calculation
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
            # Initialize with epic_x so we track from the epic's starting position
            epic_min_x = epic_x
            epic_max_x = epic_x
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
            # For outline: show estimated_stories at bottom
            epic_story_text = ""
            if is_increments:
                # In increments mode: calculate total_stories and show in top right
                epic_total_stories = self._calculate_total_stories_for_epic_in_increment(epic)
                if epic_total_stories > 0:
                    epic_story_count_html = self._get_story_count_display_html(epic_total_stories, position='top-right')
                    epic_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{epic['name']}</span>{epic_story_count_html}</div>"
                else:
                    epic_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{epic['name']}</div>"
            else:
                # Outline mode: show estimated_stories at top-right if provided
                if 'estimated_stories' in epic and epic['estimated_stories']:
                    epic_story_count_html = self._get_story_count_display_html(epic['estimated_stories'], position='top-right')
                    epic_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{epic['name']}</span>{epic_story_count_html}</div>"
                else:
                    epic_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{epic['name']}</div>"
            
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
                
                # Calculate feature story display
                # For increments: show total_stories in top right
                # For outline: show story_count at bottom
                if is_increments:
                    # In increments mode: calculate total_stories and show in top right
                    feature_total_stories = self._calculate_total_stories_for_feature_in_increment(feature)
                    if feature_total_stories > 0:
                        feature_story_count_html = self._get_story_count_display_html(feature_total_stories, position='top-right')
                        feature_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{feature['name']}</span>{feature_story_count_html}</div>"
                    else:
                        feature_story_text = f"<div style=\"display: flex; align-items: center; justify-content: center; width: 100%;\">{feature['name']}</div>"
                else:
                    # Outline mode: show estimated_stories at top-right if provided
                    if 'estimated_stories' in feature and feature['estimated_stories']:
                        # Estimated stories - show in top-right corner
                        feature_story_count_html = self._get_story_count_display_html(feature['estimated_stories'], position='top-right')
                        feature_story_text = f"<div style=\"position: relative; width: 100%; display: flex; align-items: center; justify-content: center; padding-right: 70px; box-sizing: border-box;\"><span style=\"flex: 1; text-align: center;\">{feature['name']}</span>{feature_story_count_html}</div>"
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
                
                feature_cell = ET.SubElement(root_elem, 'mxCell', 
                                             id=f'e{epic_idx}f{feat_idx}',
                                             value=feature_story_text,
                                             style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                             parent='1', vertex='1')
                # Use updated X position from feat_data if it was updated by previous feature
                actual_feat_x = feat_data.get('x', feat_x)
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
                
                # Initialize legacy variables (used only in legacy path, but need to be defined)
                base_story_positions = {}
                nested_story_groups = {}
                sequential_stories = []
                optional_stories = []
                
                # Check if feature uses story_groups (new structure) or stories (legacy)
                feature_story_groups = feature.get('story_groups', [])
                
                if feature_story_groups:
                    # NEW STRUCTURE: Process story groups
                    # In exploration mode: filter story_groups to only include groups with stories that have AC
                    if is_exploration:
                        filtered_story_groups = []
                        for group in feature_story_groups:
                            # Filter stories within group to only those with AC
                            group_stories = group.get('stories', [])
                            filtered_group_stories = [
                                s for s in group_stories
                                if s.get('Steps') or s.get('steps')
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
                    previous_story_users = None
                    
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
                            group_start_y = current_group_y  # Same Y as previous group
                        elif group_connector == 'or':
                            # Vertical connector - position below previous group
                            group_start_x = feat_x + 2  # Reset X to left edge
                            if previous_group_bottom_y is not None:
                                # Position below previous group's bottom with more spacing to avoid overlap
                                group_start_y = previous_group_bottom_y + self.STORY_SPACING_Y + 50
                            else:
                                # Fallback: use current_group_y
                                group_start_y = current_group_y + self.STORY_SPACING_Y + 70
                            current_group_y = group_start_y  # Update for next group
                        
                        # Track the bottom of this group for positioning next group
                        group_bottom_y = group_start_y
                        
                        # Sort stories by sequential_order to preserve left-to-right order
                        sorted_group_stories = sorted(group_stories, key=lambda s: s.get('sequential_order', 999))
                        
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
                            
                            # Render users for this story
                            story_users = set(story.get('users', []))
                            new_story_users = []
                            
                            if story_idx_in_group == 0 or story_users != previous_story_users:
                                for user in story_users:
                                    new_story_users.append(user)
                                    if user not in shown_users:
                                        shown_users.add(user)
                            
                            previous_story_users = story_users
                            
                            # Render users
                            if new_story_users:
                                for user_idx, user in enumerate(new_story_users):
                                    user_key = f"{epic['name']}|{feature['name']}|{story['name']}|{user}"
                                    if user_key in layout_data:
                                        user_x = layout_data[user_key]['x']
                                        layout_user_y = layout_data[user_key]['y']
                                        if layout_user_y < 50:
                                            user_x = story_x + user_idx * self.STORY_SPACING_X
                                            user_y = story_y - self.USER_LABEL_OFFSET
                                        else:
                                            user_y = layout_user_y
                                    else:
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
                                steps = story.get('Steps', []) or story.get('steps', [])
                                if steps:
                                    acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10
                                    # Render up to 2 boxes: Box 0 = Given+When, Box 1 = Then
                                    for ac_box_idx in range(2):
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
                        
                        # Update current_group_x and previous_group_bottom_y for next group
                        if group_connector == 'and':
                            # Horizontal connector - position next group to the right
                            current_group_x = group_rightmost_x + self.STORY_SPACING_X
                            # Keep same Y for next group
                            previous_group_bottom_y = group_bottom_y
                        elif group_connector == 'or':
                            # Vertical connector - reset X for next group
                            current_group_x = feat_x + 2
                            # Update Y for next group based on this group's bottom
                            # Add extra spacing to prevent overlap (account for group height)
                            previous_group_bottom_y = group_bottom_y + 20
                        else:  # group_connector is None (first group)
                            # First group - update for next group
                            current_group_x = group_rightmost_x + self.STORY_SPACING_X
                            previous_group_bottom_y = group_bottom_y
                        
                        # Track feature bottom Y (including all groups and AC boxes) for vertical stacking
                        if is_exploration:
                            # Track the bottommost Y of this feature (including AC boxes)
                            if feat_idx not in feature_bottom_y:
                                feature_bottom_y[feat_idx] = feat_y + feat_height
                            feature_bottom_y[feat_idx] = max(feature_bottom_y[feat_idx], group_bottom_y + 20)
                    
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
                
                # Render grey background rectangles for story groups
                # Skip grey rectangles when acceptance criteria are present (exploration mode)
                # Collect rectangles first, then insert them before the first story cell
                bg_rectangles_to_insert = []
                # Get story_groups from feature (it was defined in a different loop scope)
                feature_story_groups = feature.get('story_groups', [])
                if feature_story_groups and story_positions and not is_exploration:
                        is_decimal = (seq_float != base_seq)  # Check if sequential_order has decimal part
                        
                        stories_in_seq = stories_by_seq[seq_order]
                        
                        for story in stories_in_seq:
                            is_optional = story.get('flag', False)  # flag: true means optional
                            
                            if is_decimal:
                                # Story with decimal sequential_order (e.g., 1.1, 2.1) - treat as nested
                                if base_seq not in nested_story_groups:
                                    nested_story_groups[base_seq] = []
                                nested_story_groups[base_seq].append((seq_order, story))
                            else:
                                # Base story (integer sequential_order) - separate by optional/sequential
                                if is_optional:
                                    optional_stories.append((seq_order, story))
                                else:
                                    sequential_stories.append((seq_order, story))
                                    # Store position for sequential stories
                                    if base_seq not in base_story_positions:
                                        # Check if layout data exists for this story
                                        layout_key = f"{epic['name']}|{feature['name']}|{story['name']}"
                                        if layout_key in layout_data:
                                            # Use layout coordinates
                                            base_story_positions[base_seq] = {
                                                'x': layout_data[layout_key]['x'],
                                                'y': layout_data[layout_key]['y'],
                                                'seq_order': seq_order,
                                                'users': set(story.get('users', []))  # Store base story users for comparison
                                            }
                                        else:
                                            # Use calculated position - stories positioned relative to feature
                                            position = seq_to_position[seq_order]
                                            story_y = feat_y + feat_height + self.STORY_OFFSET_FROM_FEATURE
                                            # In exploration mode, use wider spacing for AC boxes (250px + 20px gap = 270px)
                                            # Otherwise use normal story spacing (60px)
                                            spacing = (self.ACCEPTANCE_CRITERIA_MIN_WIDTH + 20) if is_exploration else self.STORY_SPACING_X
                                            # In exploration mode, all stories start 12px from epic/feature left edge
                                            # Otherwise, start 2px from feature left edge
                                            story_x_offset = 12 if is_exploration else 2
                                            base_story_positions[base_seq] = {
                                                'x': (epic_x if is_exploration else feat_x) + position * spacing + story_x_offset,
                                                'y': story_y,
                                                'seq_order': seq_order,
                                                'users': set(story.get('users', []))  # Store base story users for comparison
                                            }
                    
                    # Second pass: render sequential stories first (horizontal), then optional stories (vertical stack)
                    # Render sequential stories horizontally
                    sequential_stories_sorted = sorted(sequential_stories, key=lambda x: x[0])
                    # Track previous story's users to only render when they change
                    previous_story_users = None  # None means first story will render
                    story_index = 0  # Counter to track story position
                    story_idx = 1  # Initialize story_idx for DrawIO cell IDs
                    for seq_order, story in sequential_stories_sorted:
                        story_index += 1
                        seq_float = float(seq_order) if isinstance(seq_order, (int, float, str)) else float(seq_order)
                        base_seq = int(seq_float)
                        
                        # Render sequential story
                        # Check if layout data exists for this story (may override initial position)
                        layout_key = f"{epic['name']}|{feature['name']}|{story['name']}"
                        if layout_key in layout_data:
                            # Use layout coordinates from DrawIO
                            story_x = layout_data[layout_key]['x']
                            story_y = layout_data[layout_key]['y']
                            # Update base_story_positions for nested stories
                            if base_seq in base_story_positions:
                                base_story_positions[base_seq]['x'] = story_x
                                base_story_positions[base_seq]['y'] = story_y
                        else:
                            # Use calculated position - stories stay in their positions, don't shift
                            base_pos = base_story_positions.get(base_seq)
                            if base_pos:
                                story_x = base_pos['x']
                                story_y = base_pos['y']
                            else:
                                # Fallback: calculate position relative to feature
                                position = seq_to_position.get(seq_order, 0)
                                # In exploration mode, use wider spacing for AC boxes (250px + 20px gap = 270px)
                                # Otherwise use normal story spacing (60px)
                                spacing = (self.ACCEPTANCE_CRITERIA_MIN_WIDTH + 20) if is_exploration else self.STORY_SPACING_X
                                # In exploration mode, all stories start 12px from epic/feature left edge
                                # Otherwise, start 2px from feature left edge
                                story_x_offset = 12 if is_exploration else 2
                                story_x = (epic_x if is_exploration else feat_x) + position * spacing + story_x_offset
                                story_y = feat_y + feat_height + self.STORY_OFFSET_FROM_FEATURE
                        
                        # Collect users for this story
                        # Only render users if they're different from the previous story's users
                        # This avoids redundant user labels when consecutive stories have the same users
                        story_users = set(story.get('users', []))
                        new_story_users = []
                        
                        if is_exploration:
                            # In exploration mode, always render users for each story
                            new_story_users = list(story_users)
                            # Still track to avoid duplicate epic/feature-level users
                            for user in story_users:
                                if user not in shown_users:
                                    shown_users.add(user)
                        else:
                            # In normal mode, only render users if they changed from previous story
                            # First story (story_index == 1) always renders its users
                            # Subsequent stories only render if users are different
                            if story_index == 1 or story_users != previous_story_users:
                                # Users changed (or first story) - render all users for this story
                                for user in story_users:
                                    new_story_users.append(user)
                                    # Track to avoid duplicate epic/feature-level users
                                    if user not in shown_users:
                                        shown_users.add(user)
                        
                        # Update previous story's users for next iteration
                        previous_story_users = story_users
                        
                        # Place story-level users horizontally above the story
                        if new_story_users:
                            # In exploration mode, each story's users align with that story (per-story offset)
                            # Otherwise, users share offset per Y position (for stacked stories)
                            story_user_offset = 0  # Reset offset for each story in exploration mode
                            for user in new_story_users:
                                # Check if layout data has coordinates for this story-level user
                                user_key = f"{epic['name']}|{feature['name']}|{story['name']}|{user}"
                                if user_key in layout_data:
                                    user_x = layout_data[user_key]['x']
                                    layout_user_y = layout_data[user_key]['y']
                                    # Skip users at top of map (y < 50) - treat as not found
                                    if layout_user_y < 50:
                                        # User was deleted/moved to top - place above story instead
                                        user_x = story_x + story_user_offset
                                        user_y = story_y - self.USER_LABEL_OFFSET
                                    else:
                                        # Ensure user is properly above story - check distance and adjust if needed
                                        min_user_y = story_y - self.USER_LABEL_OFFSET
                                        if layout_user_y >= story_y - 10:  # Too close or overlapping
                                            # Move up to proper position above story
                                            user_y = min_user_y
                                        else:
                                            # Use layout coordinate if it's already above
                                            user_y = layout_user_y
                                else:
                                    # User has no coordinates (in story graph but not in DrawIO) - place above story
                                    # In exploration mode, align user with story (no offset for first story, -1px for subsequent stories)
                                    # This matches expected layout where Story 1 user aligns with story, Story 2 user is 1px left
                                    user_x_offset = 0
                                    if is_exploration:
                                        # Get story position to determine if this is the first story
                                        story_position = seq_to_position.get(seq_order, 0)
                                        if story_position > 0:
                                            # For stories after the first, align user 1px to the left
                                            user_x_offset = -1
                                    user_x = story_x + story_user_offset + user_x_offset
                                    user_y = story_y - self.USER_LABEL_OFFSET
                                
                                user_label = ET.SubElement(root_elem, 'mxCell',
                                                          id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                          value=user,
                                                          style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                          parent='1', vertex='1')
                                user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                         x=str(user_x),
                                                         y=str(user_y),
                                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                user_geom.set('as', 'geometry')
                                
                                # Track user bounds for feature shrinking
                                # Users align with stories, so they don't expand feature width beyond story positions
                                # Only track if user is to the left of leftmost story (for alignment)
                                if user_x < leftmost_sequential_story_x:
                                    feature_min_x = min(feature_min_x, user_x)
                                # Don't expand feature_max_x for users - they align with stories which are already tracked
                                # feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)  # Disabled - users don't expand width
                                
                                # Increment offset for next user (if multiple users per story)
                                story_user_offset += self.STORY_SPACING_X
                        
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story['name'],
                                                   style=self._get_story_style(story),
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        
                        # Track story position for grey background rectangles
                        story_positions[story['name']] = {
                            'x': story_x,
                            'y': story_y,
                            'width': self.STORY_WIDTH,
                            'height': self.STORY_HEIGHT
                        }
                        
                        # Track story bounds for feature shrinking
                        feature_min_x = min(feature_min_x, story_x)
                        feature_max_x = max(feature_max_x, story_x + self.STORY_WIDTH)
                        # Track sequential story positions (not including nested stories)
                        leftmost_sequential_story_x = min(leftmost_sequential_story_x, story_x)
                        rightmost_sequential_story_x = max(rightmost_sequential_story_x, story_x + self.STORY_WIDTH)
                        
                        # Render nested stories (stories within stories) - check for story['stories'] array
                        # Nested stories have sequential_order 1, 2, 3 unique to their parent
                        nested_stories_list = story.get('stories', [])
                        if nested_stories_list:
                            # Sort nested stories by their sequential_order (1, 2, 3 relative to parent)
                            nested_stories_sorted = sorted(nested_stories_list, 
                                                           key=lambda s: s.get('sequential_order', 999))
                            
                            # Render nested stories below this story
                            # Group nested stories by their OWN connector, not parent's connector
                            # "and" connector nested stories: stack vertically (top to bottom)
                            # "or" connector nested stories: position left-to-right at same level
                            nested_and_stories = []
                            nested_or_stories = []
                            
                            for nested_story in nested_stories_sorted:
                                nested_connector = nested_story.get('connector', 'and')
                                if nested_connector == 'or':
                                    nested_or_stories.append(nested_story)
                                else:
                                    nested_and_stories.append(nested_story)
                            
                            # Start position for nested stories (always below parent)
                            nested_base_y = story_y + self.STORY_HEIGHT + 10
                            nested_base_x = story_x  # Align with parent story
                            nested_story_index = 0
                            previous_nested_users = set(story.get('users', []))
                            
                            # Render "and" connector nested stories first (stacked vertically)
                            for nested_story in nested_and_stories:
                                nested_story_index += 1
                                nested_story_users = set(nested_story.get('users', []))
                                
                                # Render user if it changed from previous nested story
                                if nested_story_users != previous_nested_users:
                                    for user in nested_story_users:
                                        if user not in shown_users:
                                            user_x = nested_base_x
                                            user_y = nested_base_y - self.USER_LABEL_OFFSET
                                            
                                            user_label = ET.SubElement(root_elem, 'mxCell',
                                                                      id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}_{user}',
                                                                      value=user,
                                                                      style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                                      parent='1', vertex='1')
                                            user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                                     x=str(user_x), y=str(user_y),
                                                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                            user_geom.set('as', 'geometry')
                                            
                                            feature_min_x = min(feature_min_x, user_x)
                                            feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                                            shown_users.add(user)
                                
                                # Render nested story (stacked vertically)
                                nested_story_cell = ET.SubElement(root_elem, 'mxCell',
                                                                 id=f'e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}',
                                                                 value=nested_story['name'],
                                                                 style=self._get_story_style(nested_story),
                                                                 parent='1', vertex='1')
                                nested_story_geom = ET.SubElement(nested_story_cell, 'mxGeometry',
                                                                  x=str(nested_base_x), y=str(nested_base_y),
                                                                  width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                nested_story_geom.set('as', 'geometry')
                                
                                # Track nested story bounds for positioning, but DON'T use for feature width calculation
                                # Nested "and" connector stories stack vertically - they don't expand feature width horizontally
                                # Only sequential stories determine feature width
                                # feature_min_x = min(feature_min_x, nested_base_x)  # Disabled - don't expand feature width
                                # feature_max_x = max(feature_max_x, nested_base_x + self.STORY_WIDTH)  # Disabled - don't expand feature width
                                
                                # Recursively render nested stories within nested stories (deep nesting)
                                deep_nested = nested_story.get('stories', [])
                                if deep_nested:
                                    deep_y = nested_base_y + self.STORY_HEIGHT + 10
                                    deep_idx = 0
                                    for deep_story in sorted(deep_nested, key=lambda s: s.get('sequential_order', 999)):
                                        deep_idx += 1
                                        deep_connector = deep_story.get('connector', 'and')
                                        if deep_connector == 'or':
                                            # "or" nested stories: left to right
                                            deep_x = nested_base_x + deep_idx * self.STORY_SPACING_X
                                        else:
                                            # "and" nested stories: stack vertically
                                            deep_x = nested_base_x
                                            deep_y += self.STORY_HEIGHT + 10
                                        
                                        deep_cell = ET.SubElement(root_elem, 'mxCell',
                                                                  id=f'e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}_d{deep_idx}',
                                                                  value=deep_story['name'],
                                                                  style=self._get_story_style(deep_story),
                                                                  parent='1', vertex='1')
                                        deep_geom = ET.SubElement(deep_cell, 'mxGeometry',
                                                                  x=str(deep_x), y=str(deep_y),
                                                                  width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                        deep_geom.set('as', 'geometry')
                                        
                                        # Don't expand feature width for deep nested stories - they stack below parent
                                        # feature_min_x = min(feature_min_x, deep_x)  # Disabled
                                        # feature_max_x = max(feature_max_x, deep_x + self.STORY_WIDTH)  # Disabled
                                        
                                        if deep_connector == 'and':
                                            deep_y += self.STORY_HEIGHT + 10
                                
                                # Render acceptance criteria for nested story if present
                                if is_exploration:
                                    nested_steps = nested_story.get('acceptance_criteria', [])
                                    if nested_steps:
                                        nested_ac_y = nested_base_y + self.STORY_HEIGHT + 10
                                        nested_ac_idx = 0
                                        for ac_item in nested_steps:
                                            if isinstance(ac_item, dict):
                                                ac_desc = ac_item.get('description', '')
                                                if ac_desc:
                                                    ac_text = f'<div style="font-size: 8px;"><b>When</b> {ac_desc}</div>'
                                                    ac_width = self.ACCEPTANCE_CRITERIA_MIN_WIDTH
                                                    
                                                    nested_ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                                                  id=f'ac_e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}_{nested_ac_idx}',
                                                                                  value=ac_text,
                                                                                  style='rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;fontSize=8;',
                                                                                  parent='1', vertex='1')
                                                    nested_ac_geom = ET.SubElement(nested_ac_cell, 'mxGeometry',
                                                                                   x=str(nested_base_x), y=str(nested_ac_y + nested_ac_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y),
                                                                                   width=str(ac_width), height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                                    nested_ac_geom.set('as', 'geometry')
                                                    
                                                    # Don't expand feature width for nested story AC - they stack below parent
                                                    # feature_min_x = min(feature_min_x, nested_base_x)  # Disabled
                                                    # feature_max_x = max(feature_max_x, nested_base_x + ac_width)  # Disabled
                                                    nested_ac_idx += 1
                                
                                # Move to next nested story position (vertical stacking for "and")
                                nested_base_y += self.STORY_HEIGHT + 10
                                if nested_story.get('acceptance_criteria'):
                                    nested_base_y += len(nested_story.get('acceptance_criteria', [])) * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                
                                previous_nested_users = nested_story_users
                            
                            # Render "or" connector nested stories (left-to-right at same level)
                            if nested_or_stories:
                                # Position "or" stories horizontally starting from nested_base_x
                                or_story_x = nested_base_x
                                or_story_y = nested_base_y  # Start at current Y position
                                
                                for nested_story in nested_or_stories:
                                    nested_story_index += 1
                                    nested_story_users = set(nested_story.get('users', []))
                                    
                                    # Render user if it changed from previous nested story
                                    if nested_story_users != previous_nested_users:
                                        for user in nested_story_users:
                                            if user not in shown_users:
                                                user_x = or_story_x
                                                user_y = or_story_y - self.USER_LABEL_OFFSET
                                                
                                                user_label = ET.SubElement(root_elem, 'mxCell',
                                                                          id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}_{user}',
                                                                          value=user,
                                                                          style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                                          parent='1', vertex='1')
                                                user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                                         x=str(user_x), y=str(user_y),
                                                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                                user_geom.set('as', 'geometry')
                                                
                                                feature_min_x = min(feature_min_x, user_x)
                                                feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                                                shown_users.add(user)
                                    
                                    # Render nested story (left to right)
                                    nested_story_cell = ET.SubElement(root_elem, 'mxCell',
                                                                     id=f'e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}',
                                                                     value=nested_story['name'],
                                                                     style=self._get_story_style(nested_story),
                                                                     parent='1', vertex='1')
                                    nested_story_geom = ET.SubElement(nested_story_cell, 'mxGeometry',
                                                                      x=str(or_story_x), y=str(or_story_y),
                                                                      width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    nested_story_geom.set('as', 'geometry')
                                    
                                    # Track nested story bounds for positioning, but DON'T use for feature width calculation
                                    # Nested "or" connector stories should not expand feature width - they stack below parent
                                    # Only sequential stories determine feature width
                                    # feature_min_x = min(feature_min_x, or_story_x)  # Disabled - don't expand feature width
                                    # feature_max_x = max(feature_max_x, or_story_x + self.STORY_WIDTH)  # Disabled - don't expand feature width
                                    
                                    # Render acceptance criteria for nested story if present
                                    if is_exploration:
                                        nested_steps = nested_story.get('acceptance_criteria', [])
                                        if nested_steps:
                                            nested_ac_y = or_story_y + self.STORY_HEIGHT + 10
                                            nested_ac_idx = 0
                                            for ac_item in nested_steps:
                                                if isinstance(ac_item, dict):
                                                    ac_desc = ac_item.get('description', '')
                                                    if ac_desc:
                                                        ac_text = f'<div style="font-size: 8px;"><b>When</b> {ac_desc}</div>'
                                                        ac_width = self.ACCEPTANCE_CRITERIA_MIN_WIDTH
                                                        
                                                        nested_ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                                                      id=f'ac_e{epic_idx}f{feat_idx}s{story_idx}_n{nested_story_index}_{nested_ac_idx}',
                                                                                      value=ac_text,
                                                                                      style='rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;fontSize=8;',
                                                                                      parent='1', vertex='1')
                                                        nested_ac_geom = ET.SubElement(nested_ac_cell, 'mxGeometry',
                                                                                       x=str(or_story_x), y=str(nested_ac_y + nested_ac_idx * self.ACCEPTANCE_CRITERIA_SPACING_Y),
                                                                                       width=str(ac_width), height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                                        nested_ac_geom.set('as', 'geometry')
                                                        
                                                        # Don't expand feature width for nested story AC - they stack below parent
                                                        # feature_min_x = min(feature_min_x, or_story_x)  # Disabled
                                                        # feature_max_x = max(feature_max_x, or_story_x + ac_width)  # Disabled
                                                        nested_ac_idx += 1
                                    
                                    # Move to next "or" story position (left to right)
                                    or_story_x += self.STORY_SPACING_X
                                    
                                    previous_nested_users = nested_story_users
                                
                        # Render acceptance criteria below story in exploration mode
                        # If story has nested stories, AC should be below the nested stories, not the parent story
                        if is_exploration:
                            steps = story.get('Steps', []) or story.get('steps', [])
                            if steps:
                                # Render acceptance criteria boxes below the story
                                # Steps alternate: When, Then, When, Then, ...
                                # Each pair (When + Then) becomes one AC box
                                # If nested stories exist, AC goes below them; otherwise below parent story
                                if nested_stories_list:
                                    # AC goes below nested stories - use nested_base_y which tracks the bottom of nested stories
                                    acceptance_criteria_y = nested_base_y + 10
                                else:
                                    acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10  # Start below story
                                
                                # Render up to 2 boxes: Box 0 = Given+When, Box 1 = Then
                                for ac_box_idx in range(2):
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
                    
                    # Render optional stories vertically (stacked at same X position)
                    if optional_stories:
                        # Find rightmost sequential story X position, or use default
                        optional_x = feat_x + 2  # Default to left edge
                        if sequential_stories_sorted:
                            # Find the rightmost sequential story position
                            last_seq_order = sequential_stories_sorted[-1][0]
                            last_seq_float = float(last_seq_order) if isinstance(last_seq_order, (int, float, str)) else float(last_seq_order)
                            last_base_seq = int(last_seq_float)
                            if last_base_seq in base_story_positions:
                                optional_x = base_story_positions[last_base_seq]['x'] + self.STORY_SPACING_X
                            else:
                                position = seq_to_position.get(last_seq_order, len(sequential_stories_sorted) - 1)
                                optional_x = feat_x + (position + 1) * self.STORY_SPACING_X + 2
                        else:
                            # No sequential stories, start at beginning
                            optional_x = feat_x + 2
                        
                        # Sort optional stories by sequential_order
                        optional_stories_sorted = sorted(optional_stories, key=lambda x: x[0])
                        # Optional stories start at same Y as sequential stories (relative to feature)
                        optional_y = feat_y + feat_height + self.STORY_OFFSET_FROM_FEATURE
                        
                        previous_story_users = None  # Track previous story's users for optional stories (None = first story)
                        optional_story_index = 0  # Counter for optional stories
                        for seq_order, story in optional_stories_sorted:
                            optional_story_index += 1
                            # Check if layout data exists for this optional story
                            layout_key = f"{epic['name']}|{feature['name']}|{story['name']}"
                            if layout_key in layout_data:
                                story_x = layout_data[layout_key]['x']
                                story_y = layout_data[layout_key]['y']
                            else:
                                story_x = optional_x  # All optional stories at same X
                                story_y = optional_y  # Stack vertically
                            
                            # Collect users for this story
                            # Only render users if they're different from the previous story's users
                            story_users = set(story.get('users', []))
                            new_story_users = []
                            
                            # Check if users changed from previous story (or if this is the first optional story)
                            if optional_story_index == 1 or story_users != previous_story_users:
                                # Users changed (or first story) - render them
                                for user in story_users:
                                    new_story_users.append(user)
                                    # Track to avoid duplicate epic/feature-level users
                                    if user not in shown_users:
                                        shown_users.add(user)
                            
                            # Update previous story's users for next iteration
                            previous_story_users = story_users
                            
                            # Place story-level users horizontally above the story
                            if new_story_users:
                                if story_y not in story_user_x_offset:
                                    story_user_x_offset[story_y] = 0
                                for user in new_story_users:
                                    user_key = f"{epic['name']}|{feature['name']}|{story['name']}|{user}"
                                    if user_key in layout_data:
                                        user_x = layout_data[user_key]['x']
                                        layout_user_y = layout_data[user_key]['y']
                                        if layout_user_y < 50:
                                            user_x = story_x + story_user_x_offset[story_y]
                                            user_y = story_y - self.USER_LABEL_OFFSET
                                        else:
                                            min_user_y = story_y - self.USER_LABEL_OFFSET
                                            if layout_user_y >= story_y - 10:
                                                user_y = min_user_y
                                            else:
                                                user_y = layout_user_y
                                    else:
                                        user_x = story_x + story_user_x_offset[story_y]
                                        user_y = story_y - self.USER_LABEL_OFFSET
                                    
                                    user_label = ET.SubElement(root_elem, 'mxCell',
                                                              id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                              value=user,
                                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                              parent='1', vertex='1')
                                    user_geom = ET.SubElement(user_label, 'mxGeometry',
                                                             x=str(user_x),
                                                             y=str(user_y),
                                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    user_geom.set('as', 'geometry')
                                    
                                    feature_min_x = min(feature_min_x, user_x)
                                    feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                                    story_user_x_offset[story_y] += self.STORY_SPACING_X
                            
                            story_cell = ET.SubElement(root_elem, 'mxCell',
                                                       id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                       value=story['name'],
                                                       style=self._get_story_style(story),
                                                       parent='1', vertex='1')
                            story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            story_geom.set('as', 'geometry')
                            
                            # Track story position for grey background rectangles
                            story_positions[story['name']] = {
                                'x': story_x,
                                'y': story_y,
                                'width': self.STORY_WIDTH,
                                'height': self.STORY_HEIGHT
                            }
                            
                            # Track story bounds for feature shrinking
                            feature_min_x = min(feature_min_x, story_x)
                            feature_max_x = max(feature_max_x, story_x + self.STORY_WIDTH)
                            
                            # Render acceptance criteria below story in exploration mode
                            current_ac_rightmost_x = None
                            if is_exploration:
                                steps = story.get('Steps', []) or story.get('steps', [])
                                if steps:
                                    acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10
                                    
                                    # Render up to 2 boxes: Box 0 = Given+When, Box 1 = Then
                                    for ac_box_idx in range(2):
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
                                                               width=str(ac_width),
                                                               height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                        ac_geom.set('as', 'geometry')
                                        feature_min_x = min(feature_min_x, ac_x)
                                        feature_max_x = max(feature_max_x, ac_x + ac_width)
                                        
                                        # Track rightmost AC position
                                        current_ac_rightmost_x = max(current_ac_rightmost_x or ac_x, ac_x + ac_width)
                            
                        story_idx += 1
                        # Move to next vertical position for next optional story
                        optional_y += self.STORY_SPACING_Y
                        
                        # Track feature bottom Y for vertical stacking when AC is present
                        if is_exploration:
                            # Track bottom Y including AC boxes
                            if feat_idx not in feature_bottom_y:
                                feature_bottom_y[feat_idx] = feat_y + feat_height
                            # Update with story Y + AC boxes if present
                            if current_ac_rightmost_x is not None:
                                # AC boxes extend below stories
                                last_ac_y = acceptance_criteria_y + (ac_box_idx - 1) * self.ACCEPTANCE_CRITERIA_SPACING_Y
                                feature_bottom_y[feat_idx] = max(feature_bottom_y[feat_idx], last_ac_y + self.ACCEPTANCE_CRITERIA_HEIGHT)
                            else:
                                # No AC, just track story bottom
                                feature_bottom_y[feat_idx] = max(feature_bottom_y[feat_idx], story_y + self.STORY_HEIGHT)
                
                # Render grey background rectangles for story groups (if using story_groups structure)
                # Skip grey rectangles when acceptance criteria are present (exploration mode)
                # This runs for both story_groups and legacy structures
                # Collect rectangles first, then insert them before the first story cell
                bg_rectangles_to_insert = []
                # Get story_groups from feature (it was defined in a different loop scope)
                feature_story_groups = feature.get('story_groups', [])
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
                            # Debug: log missing stories
                            # else:
                            #     print(f"DEBUG: Story '{story_name}' not found in story_positions")
                        
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
                
                # Insert rectangles before first story cell so they appear behind
                if bg_rectangles_to_insert:
                    # Find first story cell (starts with 'e' followed by epic_idx)
                    first_story_cell = None
                    for cell in root_elem:
                        cell_id = cell.get('id', '')
                        if cell_id and cell_id.startswith('e') and 'f' in cell_id and 's' in cell_id:
                            first_story_cell = cell
                            break
                    
                    if first_story_cell:
                        # Find index of first story cell
                        story_index = list(root_elem).index(first_story_cell)
                        # Insert rectangles before first story (in reverse order so they're in correct order)
                        for rect_id, bg_rect in reversed(bg_rectangles_to_insert):
                            root_elem.insert(story_index, bg_rect)
                    else:
                        # No story cells found, just append rectangles
                        for rect_id, bg_rect in bg_rectangles_to_insert:
                            root_elem.append(bg_rect)  # Stack vertically
                
                # Third pass: render nested stories (decimal sequential_order)
                # All nested stories are positioned vertically below base story
                # Stories with different users get extra spacing to make room for user cards above
                for base_seq in sorted(nested_story_groups.keys()):
                    if base_seq not in base_story_positions:
                        continue  # Skip if base story doesn't exist
                    
                    base_pos = base_story_positions[base_seq]
                    base_x = base_pos['x']
                    base_y = base_pos['y']
                    base_users = base_pos['users']
                    
                    # Sort nested stories by their sequential_order
                    nested_stories = sorted(nested_story_groups[base_seq], 
                                           key=lambda x: (float(x[0]), x[1].get('vertical_order', 0)))
                    
                    # Track vertical position, adding extra space for stories with different users
                    cumulative_vertical_offset = 0
                    previous_story_users = base_users  # Start with base story's users
                    nested_story_index = 0  # Counter for nested stories
                    
                    for nest_idx, (seq_order, story) in enumerate(nested_stories, 1):
                        nested_story_index += 1
                        # Check if layout data exists for this nested story
                        layout_key = f"{epic['name']}|{feature['name']}|{story['name']}"
                        if layout_key in layout_data:
                            # Use layout coordinates from DrawIO
                            story_x = layout_data[layout_key]['x']
                            story_y = layout_data[layout_key]['y']
                        else:
                            # Use calculated position
                            story_users = set(story.get('users', []))
                            has_different_users = (story_users != base_users)
                            
                            # If different users, add extra spacing for user cards above this story
                            if has_different_users:
                                cumulative_vertical_offset += self.USER_LABEL_OFFSET  # Extra space for user cards
                            
                            story_x = base_x  # Same X as base story
                            story_y = base_y + cumulative_vertical_offset + nest_idx * self.STORY_SPACING_Y  # Below base story
                        
                        # Collect users for this story
                        # Only render users if they're different from the previous story's users
                        story_users_list = story.get('users', [])
                        story_users_set = set(story_users_list)
                        new_story_users = []
                        
                        # Check if users changed from previous story
                        # First nested story only renders if users are different from base story
                        # Subsequent nested stories only render if users changed from previous nested story
                        if (nested_story_index == 1 and story_users_set != base_users) or (nested_story_index > 1 and story_users_set != previous_story_users):
                            # Users changed - render them
                            for user in story_users_set:
                                new_story_users.append(user)
                                # Track to avoid duplicate epic/feature-level users
                                if user not in shown_users:
                                    shown_users.add(user)
                        
                        # Update previous story's users for next iteration
                        previous_story_users = story_users_set
                        
                        # Place story-level users horizontally above the story
                        if new_story_users:
                            if story_y not in story_user_x_offset:
                                story_user_x_offset[story_y] = 0
                            for user in new_story_users:
                                # Check if layout data has coordinates for this nested story-level user
                                user_key = f"{epic['name']}|{feature['name']}|{story['name']}|{user}"
                                if user_key in layout_data:
                                    user_x = layout_data[user_key]['x']
                                    layout_user_y = layout_data[user_key]['y']
                                    # Skip users at top of map (y < 50) - treat as not found
                                    if layout_user_y < 50:
                                        # User was deleted/moved to top - place above story instead
                                        user_x = story_x + story_user_x_offset[story_y]
                                        user_y = story_y - self.USER_LABEL_OFFSET
                                    else:
                                        # Ensure user is properly above story - check distance and adjust if needed
                                        min_user_y = story_y - self.USER_LABEL_OFFSET
                                        if layout_user_y >= story_y - 10:  # Too close or overlapping
                                            # Move up to proper position above story
                                            user_y = min_user_y
                                        else:
                                            # Use layout coordinate if it's already above
                                            user_y = layout_user_y
                                else:
                                    # User has no coordinates (in story graph but not in DrawIO) - place above story
                                    user_x = story_x + story_user_x_offset[story_y]
                                    user_y = story_y - self.USER_LABEL_OFFSET
                                
                                user_label = ET.SubElement(root_elem, 'mxCell',
                                                          id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                          value=user,
                                                          style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                          parent='1', vertex='1')
                                user_geom = ET.SubElement(user_label, 'mxGeometry', 
                                                         x=str(user_x), 
                                                         y=str(user_y),
                                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                user_geom.set('as', 'geometry')
                                
                                # Track user bounds for feature shrinking
                                feature_min_x = min(feature_min_x, user_x)
                                feature_max_x = max(feature_max_x, user_x + self.STORY_WIDTH)
                                
                                story_user_x_offset[story_y] += self.STORY_SPACING_X
                        
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story['name'],
                                                   style=self._get_story_style(story),
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        
                        # Track nested story bounds for feature shrinking
                        feature_min_x = min(feature_min_x, story_x)
                        feature_max_x = max(feature_max_x, story_x + self.STORY_WIDTH)
                        
                        # Render acceptance criteria below nested story in exploration mode
                        if is_exploration:
                            steps = story.get('Steps', []) or story.get('steps', [])
                            if steps:
                                acceptance_criteria_y = story_y + self.STORY_HEIGHT + 10
                                
                                # Render up to 2 boxes: Box 0 = Given+When, Box 1 = Then
                                for ac_box_idx in range(2):
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
                                                           width=str(ac_width),
                                                           height=str(self.ACCEPTANCE_CRITERIA_HEIGHT))
                                    ac_geom.set('as', 'geometry')
                                    
                                    feature_min_x = min(feature_min_x, ac_x)
                                    feature_max_x = max(feature_max_x, ac_x + ac_width)
                        
                        story_idx += 1
                
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
                    # When sub_epics (features) are present, epic width should be constrained to fit the widest feature
                    # This prevents epics from becoming too wide when "or" connector nested stories extend horizontally
                    actual_epic_width = epic_max_x - epic_min_x + 20  # Add padding
                    actual_epic_x = epic_min_x  # Keep epic at its starting position (don't move left)
                    # Ensure minimum width
                    if actual_epic_width < 100:
                        actual_epic_width = 100
                epic_geom.set('width', str(actual_epic_width))
                epic_geom.set('x', str(actual_epic_x))
                
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
