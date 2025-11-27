"""
DrawIO Story Map Builder for Story Bot Shape Behavior

Transforms story_graph.json into a DrawIO diagram for visualization.

Pattern: template/config (story_map_drawio.json) → builder → project output (story-map.drawio)
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys


class DrawIOStoryShapeBuilder:
    """
    Builds DrawIO story map diagrams from structured story graph JSON.
    
    Generates a visual story map with:
    - Epics (purple boxes)
    - Features (green boxes)
    - Stories (yellow boxes)
    - Users (blue boxes, shown above relevant elements)
    """
    
    STORY_WIDTH = 50
    STORY_HEIGHT = 50
    STORY_SPACING_X = 60
    STORY_SPACING_Y = 55
    FEATURE_HEIGHT = 60
    FEATURE_SPACING_X = 10
    ACTOR_ROW_Y = 20  # Fixed Y position for all actors (same row)
    EPIC_Y = 130
    FEATURE_Y = 200
    STORY_START_Y = 270
    USER_LABEL_X_OFFSET = 5  # Offset to the right from element x position
    USER_SPACING_X = 55  # Horizontal spacing between user labels
    
    def __init__(self, story_map_json_path: Path, output_path: Optional[Path] = None):
        """
        Initialize the builder.
        
        Args:
            story_map_json_path: Path to the story_map.json file
            output_path: Optional output path for the generated DrawIO file
        """
        self.story_map_json_path = Path(story_map_json_path)
        self.output_path = output_path
        
    def _load_story_graph(self) -> Dict[str, Any]:
        """Load the story graph from JSON file."""
        if not self.story_map_json_path.exists():
            raise FileNotFoundError(
                f"Story map JSON file not found: {self.story_map_json_path}"
            )
        
        with open(self.story_map_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _remove_actor_from_story_name(self, story_name: str, actors: list) -> str:
        """
        Remove actor names from the beginning of story names.
        
        Since actor cards are shown separately, we don't need actor names in story labels.
        Example: "Human Triggers Bot" -> "Triggers Bot"
        """
        story_name_clean = story_name.strip()
        for actor in actors:
            # Check if story name starts with actor name (case-insensitive)
            actor_prefix = actor + " "
            if story_name_clean.startswith(actor_prefix):
                story_name_clean = story_name_clean[len(actor_prefix):].strip()
                break  # Only remove the first matching actor
        return story_name_clean
    
    def build(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Build the DrawIO story map diagram.
        
        Args:
            output_path: Optional override for output path
            
        Returns:
            Dictionary with output_path and summary information
        """
        story_graph = self._load_story_graph()
        
        if output_path is None:
            output_path = self.output_path
        
        if output_path is None:
            # Default to same directory as story_map.json
            output_path = self.story_map_json_path.parent / "story-map.drawio"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        xml_output = self._generate_diagram(story_graph)
        
        output_path.write_text(xml_output, encoding='utf-8')
        
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
                "diagram_generated": True
            }
        }
    
    def _generate_diagram(self, story_graph: Dict[str, Any]) -> str:
        """Generate the DrawIO XML diagram from story graph."""
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
        
        epic_group = ET.SubElement(root_elem, 'mxCell', id='epic-group', value='', 
                     style='group', parent='1', vertex='1', connectable='0')
        epic_group_geom = ET.SubElement(epic_group, 'mxGeometry', x='0', y='0', width='1', height='1')
        epic_group_geom.set('as', 'geometry')
        
        x_pos = 20
        shown_users = set()  # Track which users have been shown globally
        
        for epic_idx, epic in enumerate(story_graph.get('epics', []), 1):
            features = epic.get('features', [])
            
            feature_x = x_pos + 10
            epic_width = 0
            
            feature_positions = []
            for feature in features:
                stories = feature.get('stories', [])
                
                # Group stories by sequential order
                # If sequential_order is not set, assign based on array index (1-based)
                stories_by_seq = {}
                for story_idx, story in enumerate(stories, 1):
                    seq_order = story.get('sequential_order', story_idx)
                    if seq_order not in stories_by_seq:
                        stories_by_seq[seq_order] = []
                    stories_by_seq[seq_order].append(story)
                
                # Calculate feature width: 
                # - Count unique sequential orders (horizontal positions for stories)
                # - Add space for users at feature level
                num_horizontal_positions = len(stories_by_seq) if stories_by_seq else 0
                story_width = max(num_horizontal_positions * self.STORY_SPACING_X, 100)
                
                # Account for users at feature level
                feature_users = feature.get('users', [])
                feature_users_count = sum(1 for u in feature_users if u not in shown_users)
                users_width = feature_users_count * self.USER_SPACING_X if feature_users_count > 0 else 0
                
                # Feature width should accommodate both stories and users
                feature_width = max(story_width, users_width) + 20
                
                feature_positions.append({
                    'feature': feature,
                    'x': feature_x,
                    'width': feature_width,
                    'stories_by_seq': stories_by_seq,
                    'users': feature_users
                })
                
                feature_x += feature_width + self.FEATURE_SPACING_X
                epic_width += feature_width + self.FEATURE_SPACING_X
            
            # Calculate epic width from all features
            epic_width = 0
            if feature_positions:
                last_feature = feature_positions[-1]
                epic_width = (last_feature['x'] - x_pos) + last_feature['width'] + 10
            
            # Show all users at epic level horizontally
            epic_users = epic.get('users', [])
            epic_user_x = x_pos + self.USER_LABEL_X_OFFSET
            epic_users_count = sum(1 for u in epic_users if u not in shown_users)
            # Ensure epic is wide enough for all users
            users_width = epic_users_count * self.USER_SPACING_X if epic_users_count > 0 else 0
            if users_width > epic_width:
                epic_width = users_width + 20
            
            for user in epic_users:
                if user not in shown_users:
                    user_label = ET.SubElement(root_elem, 'mxCell',
                                              id=f'user_epic{epic_idx}_{user}',
                                              value=user,
                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                              parent='1', vertex='1')
                    user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(epic_user_x), y=str(self.ACTOR_ROW_Y),
                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                    user_geom.set('as', 'geometry')
                    shown_users.add(user)
                    epic_user_x += self.USER_SPACING_X
            
            # Epic cell will be created after all features are placed to get accurate width
            epic_cell_id = f'epic{epic_idx}'
            
            for feat_idx, feat_data in enumerate(feature_positions, 1):
                feature = feat_data['feature']
                feat_x = feat_data['x']
                feat_width = feat_data['width']
                stories_by_seq = feat_data['stories_by_seq']
                feature_users = feat_data['users']
                
                # Count feature users before showing them (for width calculation)
                feature_users_to_show = [u for u in feature_users if u not in shown_users]
                feature_users_width = len(feature_users_to_show) * self.USER_SPACING_X if feature_users_to_show else 0
                
                # Show all users at feature level horizontally (if not already shown at epic)
                feature_user_x = feat_x + self.USER_LABEL_X_OFFSET
                for user in feature_users_to_show:
                    user_label = ET.SubElement(root_elem, 'mxCell',
                                              id=f'user_e{epic_idx}f{feat_idx}_{user}',
                                              value=user,
                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                              parent='1', vertex='1')
                    user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(feature_user_x), y=str(self.ACTOR_ROW_Y),
                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                    user_geom.set('as', 'geometry')
                    shown_users.add(user)
                    feature_user_x += self.USER_SPACING_X
                
                # Will recalculate feature width after placing all stories
                
                # If story_count exists, always show estimate (even if some stories are enumerated - partial enumeration)
                # If no story_count but stories are enumerated, don't show count (all stories are known)
                # If no story_count and no stories, show nothing
                if 'story_count' in feature and feature['story_count']:
                    # Estimated stories - show the estimate (even if some stories are already enumerated)
                    story_count_text = f"<br><i style=\"border-color: rgb(218, 220, 224); font-size: 8px;\"><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">{feature['story_count']}&nbsp;</span><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">stories</span></i>"
                elif feature.get('stories') and len(feature.get('stories', [])) > 0:
                    # Stories are fully enumerated (no story_count) - don't show count in feature label
                    story_count_text = ""
                else:
                    # No stories and no estimate - show nothing
                    story_count_text = ""
                feature_cell = ET.SubElement(root_elem, 'mxCell', 
                                             id=f'e{epic_idx}f{feat_idx}',
                                             value=f"{feature['name']}{story_count_text}",
                                             style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                             parent='1', vertex='1')
                feature_geom = ET.SubElement(feature_cell, 'mxGeometry', x=str(feat_x), y=str(self.FEATURE_Y),
                             width=str(feat_width), height=str(self.FEATURE_HEIGHT))
                feature_geom.set('as', 'geometry')
                
                # Arrange stories horizontally by sequential order
                # Stories with same seq_order are alternatives and stack vertically
                story_idx = 1
                story_x = feat_x + 2
                story_y_base = self.STORY_START_Y
                max_story_x = story_x  # Track the rightmost story position
                
                for seq_order in sorted(stories_by_seq.keys()):
                    stories_in_seq = stories_by_seq[seq_order]
                    
                    # If multiple stories in same seq_order, they're alternatives - arrange vertically
                    if len(stories_in_seq) > 1:
                        # Alternatives: arrange vertically below each other
                        for alt_idx, story in enumerate(stories_in_seq):
                            story_y = story_y_base + alt_idx * self.STORY_SPACING_Y
                            
                            # Show all users for this story horizontally on the actor row
                            story_users = story.get('users', [])
                            story_user_x = story_x + self.USER_LABEL_X_OFFSET
                            for user in story_users:
                                if user not in shown_users:
                                    user_label = ET.SubElement(root_elem, 'mxCell',
                                                              id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                              value=user,
                                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                              parent='1', vertex='1')
                                    user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(story_user_x), y=str(self.ACTOR_ROW_Y),
                                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    user_geom.set('as', 'geometry')
                                    shown_users.add(user)
                                    story_user_x += self.USER_SPACING_X
                            
                            # Remove actor names from story name since actors are shown separately
                            story_users_list = story.get('users', [])
                            story_display_name = self._remove_actor_from_story_name(story['name'], story_users_list)
                            
                            story_cell = ET.SubElement(root_elem, 'mxCell',
                                                       id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                       value=story_display_name,
                                                       style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;',
                                                       parent='1', vertex='1')
                            story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            story_geom.set('as', 'geometry')
                            story_idx += 1
                    else:
                        # Single story: place horizontally
                        story = stories_in_seq[0]
                        story_y = story_y_base
                        
                        # Show all users for this story horizontally on the actor row
                        story_users = story.get('users', [])
                        story_user_x = story_x + self.USER_LABEL_X_OFFSET
                        for user in story_users:
                            if user not in shown_users:
                                user_label = ET.SubElement(root_elem, 'mxCell',
                                                          id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                          value=user,
                                                          style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                          parent='1', vertex='1')
                                user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(story_user_x), y=str(self.ACTOR_ROW_Y),
                                                         width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                user_geom.set('as', 'geometry')
                                shown_users.add(user)
                                story_user_x += self.USER_SPACING_X
                        
                        # Remove actor names from story name since actors are shown separately
                        story_users_list = story.get('users', [])
                        story_display_name = self._remove_actor_from_story_name(story['name'], story_users_list)
                        
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story_display_name,
                                                   style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;',
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        story_idx += 1
                    
                    # Track rightmost position
                    max_story_x = max(max_story_x, story_x + self.STORY_WIDTH)
                    # Move to next horizontal position
                    story_x += self.STORY_SPACING_X
                
                # Recalculate feature width after placing all stories and users
                actual_content_width = max_story_x - feat_x + 2
                
                # Check story users (count before they're shown)
                max_story_users = 0
                for stories_in_seq in stories_by_seq.values():
                    for story in stories_in_seq:
                        story_users = story.get('users', [])
                        story_users_count = sum(1 for u in story_users if u not in shown_users)
                        max_story_users = max(max_story_users, story_users_count)
                story_users_width = max_story_users * self.USER_SPACING_X if max_story_users > 0 else 0
                
                # Update feature width to accommodate all content
                feat_width = max(actual_content_width, feature_users_width, story_users_width) + 20
                
                # Update feature cell width
                feature_geom.set('width', str(feat_width))
                
                # Update epic width if this feature extends beyond current epic width
                feature_right_edge = feat_x + feat_width
                epic_right_edge = x_pos + epic_width
                if feature_right_edge > epic_right_edge:
                    epic_width = feature_right_edge - x_pos + 10
            
            # Create epic cell with final calculated width
            epic_cell = ET.SubElement(root_elem, 'mxCell', id=epic_cell_id, 
                                     value=epic['name'],
                                     style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                     parent='epic-group', vertex='1')
            epic_geom = ET.SubElement(epic_cell, 'mxGeometry', x=str(x_pos), y=str(self.EPIC_Y), width=str(epic_width), 
                         height='60')
            epic_geom.set('as', 'geometry')
            
            x_pos += epic_width + 20
        
        # Calculate total map width (rightmost position)
        total_map_width = x_pos - 20  # Subtract the last spacing
        map_start_x = 20  # Starting X position of the story map
        
        # Add increment lines that span the full width of the map
        # Increment labels on the left (outside the map), dashed lines spanning the map
        increment_label_x = 0  # Far left, outside the map
        increment_line_start_x = map_start_x  # Start of dashed lines at map start
        increment_line_y_positions = [
            self.STORY_START_Y + 100,  # Below first row of stories
            self.STORY_START_Y + 250,  # Further down
            self.STORY_START_Y + 400,  # Even further
            self.STORY_START_Y + 550   # Bottom
        ]
        
        for inc_idx, inc_y in enumerate(increment_line_y_positions, 1):
            # Add increment label (positioned to the left of the map)
            increment_label = ET.SubElement(root_elem, 'mxCell',
                                           id=f'increment_{inc_idx}',
                                           value=f'Increment {inc_idx}',
                                           style='whiteSpace=wrap;html=1;aspect=fixed;strokeColor=#f8f7f7;',
                                           parent='1', vertex='1')
            label_geom = ET.SubElement(increment_label, 'mxGeometry',
                                      x=str(increment_label_x), y=str(inc_y - 40),
                                      width='80', height='80')
            label_geom.set('as', 'geometry')
            
            # Add dashed horizontal line spanning the map (from map start to map end)
            increment_line = ET.SubElement(root_elem, 'mxCell',
                                          id=f'increment_line_{inc_idx}',
                                          value='',
                                          style='endArrow=none;dashed=1;html=1;',
                                          edge='1', parent='1')
            line_geom = ET.SubElement(increment_line, 'mxGeometry',
                                     width='50', height='50', relative='1')
            line_geom.set('as', 'geometry')
            source_point = ET.SubElement(line_geom, 'mxPoint',
                                        x=str(increment_line_start_x), y=str(inc_y))
            source_point.set('as', 'sourcePoint')
            target_point = ET.SubElement(line_geom, 'mxPoint',
                                        x=str(total_map_width), y=str(inc_y))
            target_point.set('as', 'targetPoint')
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='    ')


def build_story_map_drawio(config_json_path: Path, project_path: Path) -> Dict[str, Any]:
    """
    Build DrawIO story map for a project.
    
    Pattern: template/config (story_map_drawio.json) → builder → project output (story-map.drawio)
    
    Args:
        config_json_path: Path to the builder config JSON (e.g., story_map_drawio.json)
        project_path: Path to the project directory (e.g., base_bot)
        
    Returns:
        Dictionary with output_path and summary
    """
    config_json_path = Path(config_json_path)
    project_path = Path(project_path)
    
    # Load builder configuration from story_map_drawio.json
    with open(config_json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Input comes from the project's story_graph.json (generated by build_knowledge action)
    # Standard location: project_path/docs/stories/story_graph.json
    story_graph_json_path = project_path / "docs" / "stories" / "story_graph.json"
    
    # Output path from config: project_path/{path}/{output}
    output_path = project_path / config.get("path", "docs/stories/map") / config.get("output", "story-map.drawio")
    
    builder = DrawIOStoryShapeBuilder(story_graph_json_path, output_path)
    return builder.build(output_path)


if __name__ == "__main__":
    """Command-line interface for building story map DrawIO diagrams."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build DrawIO story map from JSON')
    parser.add_argument('config_json', type=Path, help='Path to builder config JSON (e.g., story_map_drawio.json)')
    parser.add_argument('project_path', type=Path, help='Path to project directory (e.g., agile_bot/bots/base_bot)')
    
    args = parser.parse_args()
    
    try:
        result = build_story_map_drawio(args.config_json, args.project_path)
        print(f"Successfully generated story map diagram: {result['output_path']}")
        print(f"Epics: {result['summary']['epics']}")
    except Exception as e:
        print(f"Error building story map: {e}", file=sys.stderr)
        sys.exit(1)

