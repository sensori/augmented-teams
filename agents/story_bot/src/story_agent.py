from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import shutil
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import re

base_agent_path = Path(__file__).parent.parent.parent / "base" / "src"
if str(base_agent_path) not in sys.path:
    sys.path.insert(0, str(base_agent_path))

from agent import (
    Diagnostic,
    VerbNounConsistencyDiagnostic,
    StoryShapeDiagnostic,
    MarketIncrementsDiagnostic,
    BaseBuilder,
    DrawIOBuilder
)

__all__ = [
    'Diagnostic',
    'VerbNounConsistencyDiagnostic',
    'StoryShapeDiagnostic',
    'MarketIncrementsDiagnostic',
    'StoryFolderStructureBuilder',
    'DrawIOStoryBuilder',
    'DrawIOStoryShapeBuilder',
    'DrawIOStoryExplorationBuilder',
    'StoryFeatureFileBuilder',
    'StoryTestFileBuilder',
    'StoryFeatureAnnotatorBuilder',
    'story_agent_build_folder_structure',
    'story_agent_build_drawio_story_shape',
    'story_agent_build_drawio_story_exploration',
    'story_agent_build_feature_file',
    'story_agent_build_test_file',
    'story_agent_annotate_feature_files'
]


class StoryFolderStructureBuilder(BaseBuilder):
    def build(self, create_story_files: bool = False) -> Dict[str, Any]:
        story_graph = self._load_story_graph()
        
        map_base = self.project_path / "docs" / "stories" / "map"
        map_base.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        archive_dir = map_base / "z_archive" / timestamp
        
        created_folders: List[str] = []
        created_stories: List[str] = []
        archived_folders: List[str] = []
        existing_folders: List[str] = []
        
        existing_epic_folders = set()
        if map_base.exists():
            for item in map_base.iterdir():
                if not item.is_dir():
                    continue
                if item.name in ['z_archive']:
                    continue
                if item.name.startswith('🎯') or item.name.startswith('epic-'):
                    existing_epic_folders.add(item.name)
        
        epics = story_graph.get("epics", [])
        
        for epic in epics:
            epic_name = epic.get("name", "").strip()
            if not epic_name:
                continue
            
            epic_folder_name = f'🎯 {epic_name}'
            epic_path = map_base / epic_folder_name
            
            if epic_folder_name in existing_epic_folders:
                existing_epic_folders.discard(epic_folder_name)
                existing_folders.append(epic_folder_name)
            
            if not epic_path.exists():
                epic_path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(epic_path.relative_to(map_base)))
            
            features = epic.get("features", [])
            for feature in features:
                feature_name = feature.get("name", "").strip()
                if not feature_name:
                    continue
                
                feature_folder_name = f'⚙️ {feature_name}'
                feature_path = epic_path / feature_folder_name
                
                if not feature_path.exists():
                    feature_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(str(feature_path.relative_to(map_base)))
                
                if create_story_files:
                    stories = feature.get("stories", [])
                    for story in stories:
                        story_name = story.get("name", "").strip()
                        if not story_name:
                            continue
                        
                        sanitized_name = story_name.replace('"', '').replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '')
                        story_filename = f'📝 {sanitized_name}.md'
                        story_path = feature_path / story_filename
                        
                        if not story_path.exists():
                            story_content = self._create_story_stub(story_name, epic_name, feature_name, map_base)
                            story_path.write_text(story_content, encoding='utf-8')
                            created_stories.append(str(story_path.relative_to(map_base)))
            
            sub_epics = epic.get("sub_epics", [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get("name", "").strip()
                if not sub_epic_name:
                    continue
                
                sub_epic_folder_name = f'🎯 {sub_epic_name}'
                sub_epic_path = epic_path / sub_epic_folder_name
                
                if not sub_epic_path.exists():
                    sub_epic_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(str(sub_epic_path.relative_to(map_base)))
                
                sub_features = sub_epic.get("features", [])
                for feature in sub_features:
                    feature_name = feature.get("name", "").strip()
                    if not feature_name:
                        continue
                    
                    feature_folder_name = f'⚙️ {feature_name}'
                    feature_path = sub_epic_path / feature_folder_name
                    
                    if not feature_path.exists():
                        feature_path.mkdir(parents=True, exist_ok=True)
                        created_folders.append(str(feature_path.relative_to(map_base)))
                    
                    if create_story_files:
                        stories = feature.get("stories", [])
                        for story in stories:
                            story_name = story.get("name", "").strip()
                            if not story_name:
                                continue
                            
                            story_filename = f'📝 {story_name}.md'
                            story_path = feature_path / story_filename
                            
                            if not story_path.exists():
                                story_content = self._create_story_stub(story_name, epic_name, feature_name, map_base)
                                story_path.write_text(story_content, encoding='utf-8')
                                created_stories.append(str(story_path.relative_to(map_base)))
        
        if existing_epic_folders:
            for obsolete_folder in existing_epic_folders:
                source_path = map_base / obsolete_folder
                if source_path.is_dir():
                    if not archive_dir.exists():
                        archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest_path = archive_dir / obsolete_folder
                    shutil.move(str(source_path), str(dest_path))
                    archived_folders.append(f"{obsolete_folder} -> z_archive/{timestamp}/")
        
        return {
            "created_folders": created_folders,
            "created_stories": created_stories,
            "archived_folders": archived_folders,
            "existing_folders": existing_folders,
            "summary": {
                "folders_created": len(created_folders),
                "stories_created": len(created_stories),
                "folders_archived": len(archived_folders),
                "folders_existing": len(existing_folders)
            }
        }
    
    def _create_story_stub(self, story_name: str, epic_name: str, feature_name: str, map_base: Path) -> str:
        import urllib.parse
        
        epic_folder = urllib.parse.quote(f'🎯 {epic_name}')
        feature_folder = urllib.parse.quote(f'⚙️ {feature_name}')
        story_file = urllib.parse.quote(f'📝 {story_name}.md')
        
        story_map_path = "../story-map.md"
        feature_path = f"../{epic_folder}/{feature_folder}/"
        
        return f"""# {story_name}

**Navigation:**
- [Story Map]({story_map_path})
- [Feature: {feature_name}]({feature_path})

## Story

{story_name}

## Acceptance Criteria

(To be added during exploration phase)

## Scenarios

(To be added during exploration phase)
"""


class DrawIOStoryBuilder(DrawIOBuilder):
    def _find_template(self) -> Optional[Path]:
        template_path = self.project_path / "agents" / "story_bot" / "templates" / "story-map-template.drawio"
        if template_path.exists():
            return template_path
        return None


class DrawIOStoryShapeBuilder(DrawIOStoryBuilder):
    STORY_WIDTH = 50
    STORY_HEIGHT = 50
    STORY_SPACING_X = 60
    STORY_SPACING_Y = 55
    FEATURE_HEIGHT = 60
    FEATURE_SPACING_X = 10
    EPIC_Y = 130
    FEATURE_Y = 200
    STORY_START_Y = 270
    USER_LABEL_OFFSET = 60  # Distance above element (accounts for 50px label height)
    USER_LABEL_X_OFFSET = 5  # Offset to the right from element x position
    
    def build(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        story_graph = self._load_story_graph()
        
        if output_path is None:
            output_path = self.project_path / "docs" / "stories" / "map" / "story-map.drawio"
        else:
            output_path = Path(output_path)
            # If path ends with drawio_story_shape.drawio, rename to story-map.drawio
            if output_path.name == "drawio_story_shape.drawio":
                output_path = output_path.parent / "story-map.drawio"
        
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
        shown_users = set()  # Track which users have been shown
        
        for epic_idx, epic in enumerate(story_graph.get('epics', []), 1):
            features = epic.get('features', [])
            
            feature_x = x_pos + 10
            epic_width = 0
            
            feature_positions = []
            for feature in features:
                stories = feature.get('stories', [])
                
                stories_by_seq = {}
                for story in stories:
                    seq_order = story.get('sequential_order', 1)
                    if seq_order not in stories_by_seq:
                        stories_by_seq[seq_order] = []
                    stories_by_seq[seq_order].append(story)
                
                max_seq = max(stories_by_seq.keys()) if stories_by_seq else 1
                feature_width = max_seq * self.STORY_SPACING_X + 20
                
                feature_positions.append({
                    'feature': feature,
                    'x': feature_x,
                    'width': feature_width,
                    'stories_by_seq': stories_by_seq
                })
                
                feature_x += feature_width + self.FEATURE_SPACING_X
                epic_width += feature_width + self.FEATURE_SPACING_X
            
            epic_width -= self.FEATURE_SPACING_X
            epic_width += 20
            
            # Check for users at epic level
            epic_users = epic.get('users', [])
            if epic_users:
                for user in epic_users:
                    if user not in shown_users:
                        user_label = ET.SubElement(root_elem, 'mxCell',
                                                  id=f'user_epic{epic_idx}_{user}',
                                                  value=user,
                                                  style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                  parent='1', vertex='1')
                        user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(x_pos + self.USER_LABEL_X_OFFSET), y=str(self.EPIC_Y - self.USER_LABEL_OFFSET),
                                                 width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        user_geom.set('as', 'geometry')
                        shown_users.add(user)
                        break  # Only show first user at epic level
            
            epic_cell = ET.SubElement(root_elem, 'mxCell', id=f'epic{epic_idx}', 
                                     value=epic['name'],
                                     style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                     parent='epic-group', vertex='1')
            epic_geom = ET.SubElement(epic_cell, 'mxGeometry', x=str(x_pos), y=str(self.EPIC_Y), width=str(epic_width), 
                         height='60')
            epic_geom.set('as', 'geometry')
            
            for feat_idx, feat_data in enumerate(feature_positions, 1):
                feature = feat_data['feature']
                feat_x = feat_data['x']
                feat_width = feat_data['width']
                stories_by_seq = feat_data['stories_by_seq']
                
                # Check for users at feature level (if not already shown at epic)
                feature_users = feature.get('users', [])
                if feature_users:
                    for user in feature_users:
                        if user not in shown_users:
                            user_label = ET.SubElement(root_elem, 'mxCell',
                                                      id=f'user_e{epic_idx}f{feat_idx}_{user}',
                                                      value=user,
                                                      style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                      parent='1', vertex='1')
                            user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(feat_x + self.USER_LABEL_X_OFFSET), y=str(self.FEATURE_Y - self.USER_LABEL_OFFSET),
                                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            user_geom.set('as', 'geometry')
                            shown_users.add(user)
                            break  # Only show first user at feature level
                
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
                
                story_idx = 1
                first_story_x = None
                for seq_order in sorted(stories_by_seq.keys()):
                    stories_in_seq = sorted(stories_by_seq[seq_order], 
                                           key=lambda s: s.get('vertical_order') or 0)
                    
                    story_x = feat_x + (seq_order - 1) * self.STORY_SPACING_X + 2
                    if first_story_x is None and stories_in_seq:
                        first_story_x = story_x
                    
                    for story in stories_in_seq:
                        is_optional = story.get('optional', False)
                        vertical_order = story.get('vertical_order')
                        
                        if is_optional and vertical_order:
                            story_y = self.STORY_START_Y + vertical_order * self.STORY_SPACING_Y
                        else:
                            story_y = self.STORY_START_Y
                        
                        # Check for users at story level (if not already shown at epic/feature)
                        story_users = story.get('users', [])
                        if story_users:
                            for user in story_users:
                                if user not in shown_users:
                                    if first_story_x is None:
                                        first_story_x = story_x
                                    user_label = ET.SubElement(root_elem, 'mxCell',
                                                              id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                              value=user,
                                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                              parent='1', vertex='1')
                                    user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(first_story_x + self.USER_LABEL_X_OFFSET), y=str(story_y - self.USER_LABEL_OFFSET),
                                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    user_geom.set('as', 'geometry')
                                    shown_users.add(user)
                                    break  # Only show first user at story level
                        
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story['name'],
                                                   style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;',
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        story_idx += 1
            
            x_pos += epic_width + 20
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='    ')


def story_agent_build_folder_structure(
    project_path: str,
    structured_content_path: Optional[str] = None,
    create_story_files: bool = False
) -> Dict[str, Any]:
    builder = StoryFolderStructureBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None
    )
    return builder.build(create_story_files=create_story_files)


def story_agent_build_drawio_story_shape(
    project_path: str,
    structured_content_path: Optional[str] = None,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    builder = DrawIOStoryShapeBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None,
        template_path=Path(template_path) if template_path else None
    )
    return builder.build(output_path=Path(output_path) if output_path else None)


class DrawIOStoryExplorationBuilder(DrawIOStoryShapeBuilder):
    """Builder for story map with acceptance criteria displayed below stories."""
    AC_WIDTH = 50
    AC_HEIGHT = 50
    AC_SPACING_Y = 60  # Spacing between AC boxes vertically
    
    def _find_template(self) -> Optional[Path]:
        template_path = self.project_path / "agents" / "story_bot" / "templates" / "story-map-template exploration.drawio"
        if template_path.exists():
            return template_path
        return None
    
    def build(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        story_graph = self._load_story_graph()
        
        if output_path is None:
            output_path = self.project_path / "docs" / "stories" / "map" / "story-map-exploration.drawio"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        xml_output = self._generate_diagram(story_graph)
        
        output_path.write_text(xml_output, encoding='utf-8')
        
        return {
            "output_path": str(output_path),
            "summary": {
                "epics": len(story_graph.get("epics", [])),
                "diagram_generated": True,
                "with_acceptance_criteria": True
            }
        }
    
    def _generate_diagram(self, story_graph: Dict[str, Any]) -> str:
        # Reuse parent's diagram generation but add AC boxes
        root = ET.Element('mxfile', host='65bd71144e')
        diagram = ET.SubElement(root, 'diagram', id='story-map-exploration', name='Story Map Exploration')
        graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                    dx='2656', dy='1035', grid='1', gridSize='10', 
                                    guides='1', tooltips='1', connect='1', arrows='1', 
                                    fold='1', page='1', pageScale='1', 
                                    pageWidth='4000', pageHeight='4000', math='0', shadow='0')
        root_elem = ET.SubElement(graph_model, 'root')
        ET.SubElement(root_elem, 'mxCell', id='0')
        ET.SubElement(root_elem, 'mxCell', id='1', parent='0')
        
        epic_group = ET.SubElement(root_elem, 'mxCell', id='epic-group', value='', 
                     style='group', parent='1', vertex='1', connectable='0')
        epic_group_geom = ET.SubElement(epic_group, 'mxGeometry', x='0', y='0', width='1', height='1')
        epic_group_geom.set('as', 'geometry')
        
        x_pos = 20
        shown_users = set()
        
        for epic_idx, epic in enumerate(story_graph.get('epics', []), 1):
            features = epic.get('features', [])
            
            feature_x = x_pos + 10
            epic_width = 0
            
            feature_positions = []
            for feature in features:
                stories = feature.get('stories', [])
                
                stories_by_seq = {}
                for story in stories:
                    seq_order = story.get('sequential_order', 1)
                    if seq_order not in stories_by_seq:
                        stories_by_seq[seq_order] = []
                    stories_by_seq[seq_order].append(story)
                
                max_seq = max(stories_by_seq.keys()) if stories_by_seq else 1
                feature_width = max_seq * self.STORY_SPACING_X + 20
                
                feature_positions.append({
                    'feature': feature,
                    'x': feature_x,
                    'width': feature_width,
                    'stories_by_seq': stories_by_seq
                })
                
                feature_x += feature_width + self.FEATURE_SPACING_X
                epic_width += feature_width + self.FEATURE_SPACING_X
            
            epic_width -= self.FEATURE_SPACING_X
            epic_width += 20
            
            # Check for users at epic level
            epic_users = epic.get('users', [])
            if epic_users:
                for user in epic_users:
                    if user not in shown_users:
                        user_label = ET.SubElement(root_elem, 'mxCell',
                                                  id=f'user_epic{epic_idx}_{user}',
                                                  value=user,
                                                  style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                  parent='1', vertex='1')
                        user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(x_pos + self.USER_LABEL_X_OFFSET), y=str(self.EPIC_Y - self.USER_LABEL_OFFSET),
                                                 width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        user_geom.set('as', 'geometry')
                        shown_users.add(user)
                        break
            
            epic_cell = ET.SubElement(root_elem, 'mxCell', id=f'epic{epic_idx}', 
                                     value=epic['name'],
                                     style='rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;',
                                     parent='epic-group', vertex='1')
            epic_geom = ET.SubElement(epic_cell, 'mxGeometry', x=str(x_pos), y=str(self.EPIC_Y), width=str(epic_width), 
                         height='60')
            epic_geom.set('as', 'geometry')
            
            for feat_idx, feat_data in enumerate(feature_positions, 1):
                feature = feat_data['feature']
                feat_x = feat_data['x']
                feat_width = feat_data['width']
                stories_by_seq = feat_data['stories_by_seq']
                
                # Check for users at feature level
                feature_users = feature.get('users', [])
                if feature_users:
                    for user in feature_users:
                        if user not in shown_users:
                            user_label = ET.SubElement(root_elem, 'mxCell',
                                                      id=f'user_e{epic_idx}f{feat_idx}_{user}',
                                                      value=user,
                                                      style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                      parent='1', vertex='1')
                            user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(feat_x + self.USER_LABEL_X_OFFSET), y=str(self.FEATURE_Y - self.USER_LABEL_OFFSET),
                                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                            user_geom.set('as', 'geometry')
                            shown_users.add(user)
                            break
                
                # Feature label with story count
                if 'story_count' in feature and feature['story_count']:
                    story_count_text = f"<br><i style=\"border-color: rgb(218, 220, 224); font-size: 8px;\"><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">{feature['story_count']}&nbsp;</span><span style=\"border-color: rgb(218, 220, 224); text-align: left;\">stories</span></i>"
                elif feature.get('stories') and len(feature.get('stories', [])) > 0:
                    story_count_text = ""
                else:
                    story_count_text = ""
                feature_cell = ET.SubElement(root_elem, 'mxCell', 
                                             id=f'e{epic_idx}f{feat_idx}',
                                             value=f"{feature['name']}{story_count_text}",
                                             style='rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;',
                                             parent='1', vertex='1')
                feature_geom = ET.SubElement(feature_cell, 'mxGeometry', x=str(feat_x), y=str(self.FEATURE_Y),
                             width=str(feat_width), height=str(self.FEATURE_HEIGHT))
                feature_geom.set('as', 'geometry')
                
                story_idx = 1
                first_story_x = None
                for seq_order in sorted(stories_by_seq.keys()):
                    stories_in_seq = sorted(stories_by_seq[seq_order], 
                                           key=lambda s: s.get('vertical_order') or 0)
                    
                    story_x = feat_x + (seq_order - 1) * self.STORY_SPACING_X + 2
                    if first_story_x is None and stories_in_seq:
                        first_story_x = story_x
                    
                    for story in stories_in_seq:
                        is_optional = story.get('optional', False)
                        vertical_order = story.get('vertical_order')
                        
                        if is_optional and vertical_order:
                            story_y = self.STORY_START_Y + vertical_order * self.STORY_SPACING_Y
                        else:
                            story_y = self.STORY_START_Y
                        
                        # Check for users at story level
                        story_users = story.get('users', [])
                        if story_users:
                            for user in story_users:
                                if user not in shown_users:
                                    if first_story_x is None:
                                        first_story_x = story_x
                                    user_label = ET.SubElement(root_elem, 'mxCell',
                                                              id=f'user_e{epic_idx}f{feat_idx}s{story_idx}_{user}',
                                                              value=user,
                                                              style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=8;',
                                                              parent='1', vertex='1')
                                    user_geom = ET.SubElement(user_label, 'mxGeometry', x=str(first_story_x + self.USER_LABEL_X_OFFSET), y=str(story_y - self.USER_LABEL_OFFSET),
                                                             width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                                    user_geom.set('as', 'geometry')
                                    shown_users.add(user)
                                    break
                        
                        # Story cell
                        story_cell = ET.SubElement(root_elem, 'mxCell',
                                                   id=f'e{epic_idx}f{feat_idx}s{story_idx}',
                                                   value=story['name'],
                                                   style='whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;',
                                                   parent='1', vertex='1')
                        story_geom = ET.SubElement(story_cell, 'mxGeometry', x=str(story_x), y=str(story_y),
                                     width=str(self.STORY_WIDTH), height=str(self.STORY_HEIGHT))
                        story_geom.set('as', 'geometry')
                        
                        # Add acceptance criteria boxes below the story
                        behavioral_ac = story.get('behavioral_ac', [])
                        if behavioral_ac:
                            ac_y = story_y + self.STORY_HEIGHT + 10  # Start below story
                            for ac_idx, ac_text in enumerate(behavioral_ac):
                                # Format AC text: extract When/Then parts
                                ac_display = self._format_ac_text(ac_text)
                                
                                ac_cell = ET.SubElement(root_elem, 'mxCell',
                                                       id=f'e{epic_idx}f{feat_idx}s{story_idx}ac{ac_idx + 1}',
                                                       value=ac_display,
                                                       style='rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFCC;align=left;fontSize=6;fontColor=#080808;',
                                                       parent='1', vertex='1')
                                ac_geom = ET.SubElement(ac_cell, 'mxGeometry', x=str(story_x), y=str(ac_y),
                                                         width=str(self.AC_WIDTH), height=str(self.AC_HEIGHT))
                                ac_geom.set('as', 'geometry')
                                ac_y += self.AC_SPACING_Y
                        
                        story_idx += 1
            
            x_pos += epic_width + 20
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='    ')
    
    def _format_ac_text(self, ac_text: str) -> str:
        """Format acceptance criteria text for display in DrawIO box with auto-sizing font."""
        # AC format is: "When ... then ..."
        # Shrink font size as needed to fit all text without truncation or wrapping
        
        # Try to find When and Then clauses
        when_pos = ac_text.lower().find('when ')
        then_pos = ac_text.lower().find('then ')
        
        if when_pos >= 0 and then_pos >= 0:
            when_part = ac_text[when_pos + 5:then_pos].strip()
            then_part = ac_text[then_pos + 5:].strip()
            
            # Calculate font size based on text length - shrink more aggressively to avoid edge touching
            # Box is 50px wide x 50px high, estimate characters that fit
            # Use smaller fonts to ensure text doesn't touch edges
            total_length = len(when_part) + len(then_part)
            
            if total_length > 100:
                font_size = 3
            elif total_length > 70:
                font_size = 4
            elif total_length > 50:
                font_size = 5
            else:
                font_size = 6
            
            # Keep full text, no truncation, no wrapping - just shrink font
            return f'<font color="#080808" style="font-size: {font_size}px;"><b style="font-size: {font_size}px;">When </b>{when_part}<br><b style="font-size: {font_size}px;">Then </b>{then_part}</font>'
        else:
            # Fallback: format entire text with auto-sizing - shrink more aggressively
            total_length = len(ac_text)
            if total_length > 100:
                font_size = 3
            elif total_length > 70:
                font_size = 4
            elif total_length > 50:
                font_size = 5
            else:
                font_size = 6
            
            return f'<font color="#080808" style="font-size: {font_size}px;">{ac_text}</font>'


def story_agent_build_drawio_story_exploration(
    project_path: str,
    structured_content_path: Optional[str] = None,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    builder = DrawIOStoryExplorationBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None,
        template_path=Path(template_path) if template_path else None
    )
    return builder.build(output_path=Path(output_path) if output_path else None)


class StoryFeatureFileBuilder(BaseBuilder):
    """Builder that generates Gherkin .feature files from structured.json."""
    
    def build(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate .feature files from structured.json for stories in scope.
        
        Only generates feature files for stories that have been rendered/updated
        in the current workflow session. Determines scope by checking which
        story markdown files exist and have been recently updated, or by checking
        the rendered content if available.
        """
        story_graph = self._load_story_graph()
        
        # Determine map_base path - try multiple possible locations
        possible_paths = [
            self.project_path / "docs" / "stories" / "map",
            self.project_path / "agents" / "story_bot" / "docs" / "stories" / "map",
        ]
        
        # Also check if structured_content_path gives us a hint
        if self.structured_content_path:
            structured_path = Path(self.structured_content_path)
            if structured_path.exists():
                # structured.json is at docs/stories/structured.json, so map is at docs/stories/map
                possible_paths.insert(0, structured_path.parent / "map")
        
        map_base = None
        for path in possible_paths:
            if path.exists():
                map_base = path
                break
        
        if not map_base:
            # If none exist, use the first one as default (will be created)
            map_base = possible_paths[0]
        
        map_base.mkdir(parents=True, exist_ok=True)
        
        # Find stories in scope - check for existing .md files (these are the ones being worked on)
        stories_in_scope = set()
        if map_base.exists():
            for md_file in map_base.rglob("📝 *.md"):
                # Extract story name from filename - remove emoji prefix
                story_name_from_file = md_file.stem
                if story_name_from_file.startswith("📝 "):
                    story_name_from_file = story_name_from_file[2:].strip()
                stories_in_scope.add(story_name_from_file)
        
        converted = []
        
        # Iterate through epics, features, and stories - only process those in scope
        for epic in story_graph.get("epics", []):
            epic_name = epic.get("name", "").strip()
            if not epic_name:
                continue
            
            epic_folder_name = f'🎯 {epic_name}'
            epic_path = map_base / epic_folder_name
            
            for feature in epic.get("features", []):
                feature_name = feature.get("name", "").strip()
                if not feature_name:
                    continue
                
                feature_folder_name = f'⚙️ {feature_name}'
                feature_path = epic_path / feature_folder_name
                
                for story in feature.get("stories", []):
                    story_name = story.get("name", "").strip()
                    if not story_name:
                        continue
                    
                    # Only process stories that are in scope (have .md files)
                    if story_name not in stories_in_scope:
                        continue
                    
                    # Check if story has scenarios
                    scenarios = story.get("scenarios", [])
                    if not scenarios:
                        continue
                    
                    try:
                        # Generate feature file from structured data (now with examples from markdown)
                        feature_content = self._generate_feature_from_structured(
                            story, epic_name, feature_name
                        )
                        
                        # Determine output path
                        sanitized_name = story_name.replace('"', '').replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '')
                        feature_filename = f'📝 {sanitized_name}.feature'
                        feature_file_path = feature_path / feature_filename
                        
                        # Write .feature file
                        feature_file_path.parent.mkdir(parents=True, exist_ok=True)
                        feature_file_path.write_text(feature_content, encoding='utf-8')
                        
                        converted.append({
                            "story_name": story_name,
                            "feature_file": str(feature_file_path),
                            "scenarios_count": len(scenarios)
                        })
                    except Exception as e:
                        converted.append({
                            "story_name": story_name,
                            "error": str(e)
                        })
        
        successful = [c for c in converted if "feature_file" in c]
        errors = [c for c in converted if "error" in c]
        
        return {
            "output_path": str(map_base),
            "converted_files": converted,
            "summary": {
                "feature_files_created": len(successful),
                "total_stories_processed": len(converted),
                "stories_in_scope": len(stories_in_scope),
                "errors": len(errors)
            }
        }
    
    def _generate_feature_from_structured(self, story: Dict[str, Any], epic_name: str, feature_name: str) -> str:
        """Generate .feature file content from structured.json story data."""
        lines = []
        
        story_name = story.get("name", "Story")
        story_description = story.get("description", "")
        
        # Add metadata as comments
        lines.append(f"# Epic: {epic_name}")
        lines.append(f"# Feature: {feature_name}")
        lines.append(f"# Story: {story_name}")
        
        if story_description:
            lines.append("#")
            lines.append("# Story Description:")
            # Wrap description if long
            if len(story_description) > 80:
                words = story_description.split()
                current_line = "#"
                for word in words:
                    if len(current_line) + len(word) + 1 > 80:
                        lines.append(current_line)
                        current_line = f"# {word}"
                    else:
                        current_line += f" {word}" if current_line != "#" else word
                if current_line != "#":
                    lines.append(current_line)
            else:
                lines.append(f"# {story_description}")
        
        lines.append("")
        
        # Feature header
        lines.append(f"Feature: {story_name}")
        lines.append("  As a developer")
        lines.append("  I want to test the story scenarios")
        lines.append("  So that the requirements are verified")
        lines.append("")
        
        # Extract common background from first scenario if it exists
        common_background = None
        scenarios = story.get("scenarios", [])
        if scenarios:
            first_scenario = scenarios[0]
            if "background" in first_scenario:
                common_background = first_scenario["background"]
        
        # Background
        if common_background:
            lines.append("  Background:")
            for step in common_background.get("steps", []):
                lines.append(f"    {step}")
            lines.append("")
        
        # Scenarios
        for scenario in scenarios:
            scenario_name = scenario.get("name", "")
            steps = scenario.get("steps", [])
            examples = scenario.get("examples", [])
            
            # Determine if it's a Scenario Outline (has examples or variables in steps)
            is_outline = bool(examples) or any("<" in step and ">" in step for step in steps)
            scenario_type = "Scenario Outline" if is_outline else "Scenario"
            
            lines.append(f"  {scenario_type}: {scenario_name}")
            
            # Add steps (skip background steps if they're in common background)
            scenario_background = scenario.get("background")
            if scenario_background and scenario_background != common_background:
                # Scenario-specific background steps
                for step in scenario_background.get("steps", []):
                    lines.append(f"    {step}")
            
            for step in steps:
                lines.append(f"    {step}")
            
            # Examples table for Scenario Outline
            if examples:
                lines.append("")
                lines.append("    Examples:")
                # Generate header row from first example keys
                if examples:
                    headers = list(examples[0].keys())
                    header_row = "      | " + " | ".join(headers) + " |"
                    lines.append(header_row)
                    # Generate data rows
                    for example in examples:
                        values = [str(example.get(header, "")) for header in headers]
                        data_row = "      | " + " | ".join(values) + " |"
                        lines.append(data_row)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _parse_story_markdown(self, content: str) -> Dict[str, Any]:
        """Parse markdown story file and extract Gherkin components."""
        parsed = {
            "story_name": "",
            "epic": "",
            "feature": "",
            "story_description": "",
            "background": [],
            "scenarios": []
        }
        
        # Extract story name from header
        story_name_match = re.search(r'^#\s*📝\s*(.+)$', content, re.MULTILINE)
        if story_name_match:
            parsed["story_name"] = story_name_match.group(1).strip()
        
        # Extract Epic and Feature
        epic_match = re.search(r'\*\*Epic:\*\*\s*(.+)$', content, re.MULTILINE)
        if epic_match:
            parsed["epic"] = epic_match.group(1).strip()
        
        feature_match = re.search(r'\*\*Feature:\*\*\s*(.+)$', content, re.MULTILINE)
        if feature_match:
            parsed["feature"] = feature_match.group(1).strip()
        
        # Extract story description
        desc_match = re.search(r'## Story Description\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if desc_match:
            parsed["story_description"] = desc_match.group(1).strip()
        
        # Extract Background
        background_match = re.search(r'## Background.*?```gherkin\s*\n(.*?)```', content, re.DOTALL)
        if background_match:
            background_steps = background_match.group(1).strip().split('\n')
            parsed["background"] = [step.strip() for step in background_steps if step.strip()]
        
        # Extract all scenarios
        scenario_pattern = r'### (Scenario(?: Outline)?):\s*(.+?)(?=\n### |\Z)'
        scenarios = re.finditer(scenario_pattern, content, re.DOTALL)
        
        for scenario_match in scenarios:
            scenario_type = scenario_match.group(1).strip()
            # Extract scenario name - stop at first newline
            scenario_name_raw = scenario_match.group(2).strip()
            scenario_name = scenario_name_raw.split('\n')[0].strip()
            scenario_content = scenario_match.group(0)
            
            # Extract steps from gherkin code block - look for **Steps:** followed by ```gherkin block
            steps_match = re.search(r'\*\*Steps:\*\*\s*\n\s*```gherkin\s*\n(.*?)```', scenario_content, re.DOTALL)
            steps = []
            if steps_match:
                gherkin_content = steps_match.group(1).strip()
                # Split by newlines and filter out empty lines
                steps = [step.strip() for step in gherkin_content.split('\n') if step.strip()]
            
            # Extract Examples table if Scenario Outline
            examples = []
            if "Outline" in scenario_type:
                # Find Examples section - look for **Examples:** followed by markdown table
                examples_match = re.search(r'\*\*Examples:\*\*\s*\n(.*?)(?=\n### |\n## |\Z)', scenario_content, re.DOTALL)
                if examples_match:
                    examples_table = examples_match.group(1).strip()
                    examples = self._parse_markdown_table(examples_table)
            
            parsed["scenarios"].append({
                "type": scenario_type,
                "name": scenario_name,
                "steps": steps,
                "examples": examples
            })
        
        return parsed
    
    def _parse_markdown_table(self, table_text: str) -> List[Dict[str, str]]:
        """Parse markdown table into list of dictionaries."""
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        if len(lines) < 2:
            return []
        
        # Find header row (first line with | that doesn't start with -)
        header_line_idx = None
        for i, line in enumerate(lines):
            if '|' in line and not line.strip().startswith('-') and not all(c in '-| ' for c in line):
                header_line_idx = i
                break
        
        if header_line_idx is None:
            return []
        
        # Extract headers
        headers = [col.strip() for col in lines[header_line_idx].split('|') if col.strip()]
        
        # Find separator line (line with dashes)
        separator_idx = header_line_idx + 1
        if separator_idx < len(lines) and all(c in '-| ' for c in lines[separator_idx]):
            start_data_idx = separator_idx + 1
        else:
            start_data_idx = header_line_idx + 1
        
        # Process data rows
        examples = []
        for line in lines[start_data_idx:]:
            if not line.strip() or all(c in '-| ' for c in line):
                continue
            cols = [col.strip() for col in line.split('|') if col.strip()]
            if len(cols) == len(headers):
                example = {headers[i]: cols[i] for i in range(len(headers))}
                examples.append(example)
        
        return examples
    
    def _generate_feature_file(self, parsed: Dict[str, Any]) -> str:
        """Generate .feature file content from parsed story data."""
        lines = []
        
        # Add metadata as comments
        if parsed.get("epic"):
            lines.append(f"# Epic: {parsed['epic']}")
        if parsed.get("feature"):
            lines.append(f"# Feature: {parsed['feature']}")
        if parsed.get("story_name"):
            lines.append(f"# Story: {parsed['story_name']}")
        
        if parsed.get("story_description"):
            lines.append("#")
            lines.append("# Story Description:")
            # Wrap description if long
            desc = parsed["story_description"]
            if len(desc) > 80:
                words = desc.split()
                current_line = "#"
                for word in words:
                    if len(current_line) + len(word) + 1 > 80:
                        lines.append(current_line)
                        current_line = f"# {word}"
                    else:
                        current_line += f" {word}" if current_line != "#" else word
                if current_line != "#":
                    lines.append(current_line)
            else:
                lines.append(f"# {desc}")
        
        lines.append("")
        
        # Feature header
        story_name = parsed.get("story_name", "Story")
        lines.append(f"Feature: {story_name}")
        lines.append("  As a developer")
        lines.append("  I want to test the story scenarios")
        lines.append("  So that the requirements are verified")
        lines.append("")
        
        # Background
        if parsed.get("background"):
            lines.append("  Background:")
            for step in parsed["background"]:
                lines.append(f"    {step}")
            lines.append("")
        
        # Scenarios
        for scenario in parsed.get("scenarios", []):
            scenario_type = scenario["type"]
            scenario_name = scenario["name"]
            steps = scenario["steps"]
            examples = scenario.get("examples", [])
            
            lines.append(f"  {scenario_type}: {scenario_name}")
            # Only add steps if we have them (filtered from code blocks)
            for step in steps:
                # Skip markdown formatting that might have been captured
                if step.startswith("**") or step.startswith("```"):
                    continue
                lines.append(f"    {step}")
            
            # Examples table for Scenario Outline
            if examples:
                lines.append("")
                lines.append("    Examples:")
                # Generate header row
                if examples:
                    headers = list(examples[0].keys())
                    header_row = "      | " + " | ".join(headers) + " |"
                    lines.append(header_row)
                    # Generate data rows
                    for example in examples:
                        values = [example.get(header, "") for header in headers]
                        data_row = "      | " + " | ".join(values) + " |"
                        lines.append(data_row)
            
            lines.append("")
        
        return "\n".join(lines)


def story_agent_build_feature_file(
    project_path: str,
    structured_content_path: Optional[str] = None,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Gherkin .feature files from structured.json.
    
    This builder reads structured.json and generates .feature files for all stories
    that have scenarios and are in scope (have corresponding .md files). This ensures 
    feature files come from the same source of truth as the markdown story files.
    
    Args:
        project_path: Path to project root (should be agents/story_bot directory)
        structured_content_path: Path to structured.json (used to load story data)
        output_path: Optional specific output path (not used, files go to story map)
        template_path: Optional template path (not used)
    
    Returns:
        Dictionary with summary of converted files
    """
    builder = StoryFeatureFileBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None
    )
    return builder.build()


class StoryTestFileBuilder(BaseBuilder):
    """
    Builder for generating pytest-bdd test code from feature files.
    
    This builder reads .feature files and generates pytest-bdd test code
    with step definitions, fixtures, and helpers in a single test file.
    """
    def build(self) -> Dict[str, Any]:
        """
        Generate pytest-bdd test code from feature files.
        
        Returns:
            Dictionary with summary of generated test code
        """
        # Find feature files
        map_base = self._find_map_directory()
        if not map_base:
            return {
                "status": "error",
                "message": "Could not find docs/stories/map directory",
                "test_file_path": str(self.project_path / "src" / "stories_acceptance_tests.py")
            }
        
        feature_files = list(map_base.rglob("*.feature"))
        if not feature_files:
            return {
                "status": "error",
                "message": "No .feature files found in docs/stories/map",
                "test_file_path": str(self.project_path / "src" / "stories_acceptance_tests.py")
            }
        
        # Parse all feature files
        parsed_features = []
        for feature_file in feature_files:
            parsed = self._parse_feature_file(feature_file)
            if parsed:
                parsed_features.append(parsed)
        
        # Generate test code
        test_code = self._generate_test_code(parsed_features)
        
        # Write test file
        test_file_path = self.project_path / "src" / "stories_acceptance_tests.py"
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path.write_text(test_code, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Generated test code from {len(parsed_features)} feature files",
            "test_file_path": str(test_file_path),
            "feature_files_processed": len(parsed_features)
        }
    
    def _find_map_directory(self) -> Optional[Path]:
        """Find the docs/stories/map directory."""
        possible_paths = [
            self.project_path / "docs" / "stories" / "map",
            self.project_path.parent / "story_bot" / "docs" / "stories" / "map",
        ]
        
        if self.structured_content_path:
            # Try to infer from structured.json location
            possible_paths.insert(0, self.structured_content_path.parent / "map")
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path
        
        return None
    
    def _parse_feature_file(self, feature_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a .feature file to extract scenarios, steps, and examples."""
        try:
            content = feature_file.read_text(encoding='utf-8')
        except Exception as e:
            return None
        
        lines = content.split('\n')
        
        # Extract feature name
        feature_name = None
        epic = None
        feature = None
        story_name = None
        story_description = None
        
        background_steps = []
        scenarios = []
        
        current_scenario = None
        in_background = False
        in_scenario = False
        in_examples = False
        examples_headers = []
        examples_data = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Extract metadata from comments
            if stripped.startswith('# Epic:'):
                epic = stripped.replace('# Epic:', '').strip()
            elif stripped.startswith('# Feature:'):
                feature = stripped.replace('# Feature:', '').strip()
            elif stripped.startswith('# Story:'):
                story_name = stripped.replace('# Story:', '').strip()
            elif stripped.startswith('#') and 'Story Description:' in stripped:
                # Story description might be on next lines
                desc_lines = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip().startswith('#'):
                        desc_lines.append(lines[j].strip().lstrip('#'))
                    elif lines[j].strip() and not lines[j].strip().startswith('#'):
                        break
                story_description = ' '.join(desc_lines).strip()
            
            # Feature declaration
            if stripped.startswith('Feature:'):
                feature_name = stripped.replace('Feature:', '').strip()
            
            # Background
            elif stripped == 'Background:' or stripped.startswith('Background:'):
                in_background = True
                in_scenario = False
                in_examples = False
            
            # Scenario
            elif stripped.startswith('Scenario:') or stripped.startswith('Scenario Outline:'):
                if current_scenario:
                    scenarios.append(current_scenario)
                
                scenario_type = 'Scenario Outline' if 'Outline' in stripped else 'Scenario'
                scenario_name = stripped.split(':', 1)[1].strip() if ':' in stripped else ''
                
                current_scenario = {
                    'type': scenario_type,
                    'name': scenario_name,
                    'steps': [],
                    'examples': []
                }
                in_background = False
                in_scenario = True
                in_examples = False
                examples_headers = []
                examples_data = []
            
            # Examples table
            elif stripped == 'Examples:' or stripped.startswith('Examples:'):
                in_examples = True
                examples_headers = []
                examples_data = []
            
            # Step (Given/When/Then/And/But)
            elif stripped and (stripped.startswith('Given ') or stripped.startswith('When ') or 
                              stripped.startswith('Then ') or stripped.startswith('And ') or 
                              stripped.startswith('But ')):
                step = stripped
                if in_background:
                    background_steps.append(step)
                elif in_scenario and current_scenario:
                    current_scenario['steps'].append(step)
            
            # Examples table data
            elif in_examples and stripped.startswith('|'):
                cols = [col.strip() for col in stripped.split('|') if col.strip()]
                if not examples_headers and cols:
                    examples_headers = cols
                elif examples_headers and len(cols) == len(examples_headers):
                    example_row = {examples_headers[j]: cols[j] for j in range(len(examples_headers))}
                    examples_data.append(example_row)
                    if current_scenario:
                        current_scenario['examples'] = examples_data
        
        # Add last scenario
        if current_scenario:
            scenarios.append(current_scenario)
        
        return {
            'feature_file': str(feature_file.relative_to(self._find_map_directory())),
            'feature_name': feature_name or story_name,
            'epic': epic,
            'feature': feature,
            'story_name': story_name,
            'story_description': story_description,
            'background': background_steps,
            'scenarios': scenarios
        }
    
    def _generate_test_code(self, parsed_features: List[Dict[str, Any]]) -> str:
        """Generate pytest-bdd test code from parsed feature files."""
        lines = []
        
        # Header
        lines.append('"""')
        lines.append('BDD Acceptance Tests: Story Agent')
        lines.append('')
        lines.append('This test file contains pytest-bdd test implementations for Story Agent,')
        lines.append('generated from Gherkin feature files.')
        lines.append('')
        lines.append('All step definitions match feature files exactly.')
        lines.append('"""')
        lines.append('')
        
        # Imports
        lines.append('import pytest')
        lines.append('from pathlib import Path')
        lines.append('import sys')
        lines.append('import json')
        lines.append('from typing import Dict, Any, Optional')
        lines.append('from pytest_bdd import given, when, then, parsers, scenario')
        lines.append('')
        lines.append('# Add workspace root to path')
        lines.append('workspace_root = Path(__file__).parent.parent.parent.parent')
        lines.append('if str(workspace_root) not in sys.path:')
        lines.append('    sys.path.insert(0, str(workspace_root))')
        lines.append('')
        lines.append('# Import production code')
        lines.append('from agents.base.src.agent import Agent')
        lines.append('from agents.base.src.agent_mcp_server import AgentStateManager')
        lines.append('')
        
        # Fixtures
        lines.append('# ============================================================================')
        lines.append('# FIXTURES')
        lines.append('# ============================================================================')
        lines.append('')
        lines.append('@pytest.fixture')
        lines.append('def workspace_root(tmp_path):')
        lines.append('    """Create temporary workspace for tests."""')
        lines.append('    workspace = tmp_path / "workspace"')
        lines.append('    workspace.mkdir()')
        lines.append('    return workspace')
        lines.append('')
        lines.append('@pytest.fixture')
        lines.append('def base_config_path(workspace_root):')
        lines.append('    """Create base agent.json in workspace."""')
        lines.append('    config_path = workspace_root / "agents" / "base" / "agent.json"')
        lines.append('    config_path.parent.mkdir(parents=True, exist_ok=True)')
        lines.append('    config_path.write_text(\'{"name": "base", "behaviors": []}\', encoding="utf-8")')
        lines.append('    return config_path')
        lines.append('')
        lines.append('@pytest.fixture')
        lines.append('def agent_config_path(workspace_root):')
        lines.append('    """Create story_bot agent.json in workspace."""')
        lines.append('    config_path = workspace_root / "agents" / "story_bot" / "agent.json"')
        lines.append('    config_path.parent.mkdir(parents=True, exist_ok=True)')
        lines.append('    config_path.write_text(\'{"name": "story_bot", "behaviors": []}\', encoding="utf-8")')
        lines.append('    return config_path')
        lines.append('')
        lines.append('@pytest.fixture')
        lines.append('def test_project_area(workspace_root):')
        lines.append('    """Create temporary project area for tests."""')
        lines.append('    project_area = workspace_root / "test_project"')
        lines.append('    project_area.mkdir(parents=True, exist_ok=True)')
        lines.append('    return project_area')
        lines.append('')
        
        # Factory Classes
        lines.append('# ============================================================================')
        lines.append('# FACTORY CLASSES')
        lines.append('# ============================================================================')
        lines.append('')
        lines.append('class AgentFactory:')
        lines.append('    """Factory for creating Agent instances in tests."""')
        lines.append('    ')
        lines.append('    @staticmethod')
        lines.append('    def create_agent(agent_name="story_bot", workspace_root=None, project_area=None):')
        lines.append('        """Create Agent instance for testing."""')
        lines.append('        if workspace_root is None:')
        lines.append('            workspace_root = Path("/test/workspace")')
        lines.append('        if project_area is None:')
        lines.append('            project_area = str(workspace_root / "test_project")')
        lines.append('        return Agent(agent_name=agent_name, workspace_root=workspace_root, project_area=project_area)')
        lines.append('')
        lines.append('class ProjectFactory:')
        lines.append('    """Factory for creating Project instances in tests."""')
        lines.append('    ')
        lines.append('    @staticmethod')
        lines.append('    def create_project(agent, **overrides):')
        lines.append('        """Create Project instance for testing."""')
        lines.append('        # Project is created by Agent, so we use Agent to create it')
        lines.append('        if not hasattr(agent, "project"):')
        lines.append('            # Initialize project through agent')
        lines.append('            pass  # Will be implemented based on actual Agent API')
        lines.append('        return agent.project')
        lines.append('')
        
        # Step Definition Classes
        lines.append('# ============================================================================')
        lines.append('# STEP DEFINITION CLASSES')
        lines.append('# ============================================================================')
        lines.append('')
        
        # Collect all unique steps from all features
        all_steps = set()
        for feature in parsed_features:
            for step in feature.get('background', []):
                all_steps.add(step)
            for scenario in feature.get('scenarios', []):
                for step in scenario.get('steps', []):
                    all_steps.add(step)
        
        # Generate step definitions for each unique step
        # Group steps by domain (Agent, Project, MCP, etc.)
        agent_steps = []
        project_steps = []
        mcp_steps = []
        workflow_steps = []
        other_steps = []
        
        for step in sorted(all_steps):
            step_lower = step.lower()
            if 'agent' in step_lower and 'mcp' not in step_lower:
                agent_steps.append(step)
            elif 'project' in step_lower:
                project_steps.append(step)
            elif 'mcp' in step_lower or 'agentstatemanager' in step_lower:
                mcp_steps.append(step)
            elif 'workflow' in step_lower:
                workflow_steps.append(step)
            else:
                other_steps.append(step)
        
        # Generate step definitions - we'll create a simplified version
        # that matches steps exactly
        lines.append('class AgentSteps:')
        lines.append('    """Agent-related step definitions."""')
        lines.append('    pass  # Step definitions will be registered as module-level functions')
        lines.append('')
        lines.append('class ProjectSteps:')
        lines.append('    """Project-related step definitions."""')
        lines.append('    pass')
        lines.append('')
        lines.append('class MCPSteps:')
        lines.append('    """MCP Server and AgentStateManager step definitions."""')
        lines.append('    pass')
        lines.append('')
        lines.append('class WorkflowSteps:')
        lines.append('    """Workflow-related step definitions."""')
        lines.append('    pass')
        lines.append('')
        
        # Module-level step definitions
        lines.append('# ============================================================================')
        lines.append('# MODULE-LEVEL STEP DEFINITIONS')
        lines.append('# ============================================================================')
        lines.append('')
        lines.append('# Step definitions are registered here to match feature files exactly')
        lines.append('# Each step from feature files must have a corresponding step definition')
        lines.append('')
        lines.append('# NOTE: This is a template. Actual step implementations need to be')
        lines.append('# added based on the specific steps found in feature files.')
        lines.append('# The builder has extracted all steps - they need to be implemented.')
        lines.append('')
        
        # Generate placeholder step definitions for a few key steps to show the pattern
        sample_steps = list(all_steps)[:5]  # First 5 as examples
        for step in sample_steps:
            # Convert step to function name and decorator
            step_text = step
            # Remove Given/When/Then/And/But prefix for function name
            func_name_base = step.split(' ', 1)[1] if ' ' in step else step
            func_name = 'step_' + re.sub(r'[^a-zA-Z0-9]', '_', func_name_base.lower())[:50]
            
            step_type = step.split(' ', 1)[0].lower()
            decorator = step_type
            
            lines.append(f'@{decorator}({repr(step_text)})')
            lines.append(f'def {func_name}(context):')
            lines.append(f'    """Step: {step_text}"""')
            lines.append(f'    # TODO: Implement step definition')
            lines.append(f'    pass')
            lines.append('')
        
        lines.append('# ... more step definitions for all steps in feature files ...')
        lines.append('')
        
        # Scenario mappings
        lines.append('# ============================================================================')
        lines.append('# SCENARIO MAPPINGS')
        lines.append('# ============================================================================')
        lines.append('')
        lines.append('# Scenario decorators map feature files to test functions')
        lines.append('# Example:')
        lines.append('# @scenario("path/to/feature.feature", "Scenario name")')
        lines.append('# def test_scenario_name():')
        lines.append('#     pass')
        lines.append('')
        
        for feature in parsed_features:
            feature_rel_path = feature['feature_file'].replace('\\', '/')
            for scenario in feature.get('scenarios', []):
                scenario_name = scenario['name']
                test_func_name = 'test_' + re.sub(r'[^a-zA-Z0-9]', '_', scenario_name.lower())[:50]
                lines.append(f'@scenario("{feature_rel_path}", "{scenario_name}")')
                lines.append(f'def {test_func_name}():')
                lines.append(f'    """Test: {scenario_name}"""')
                lines.append(f'    pass')
                lines.append('')
        
        return '\n'.join(lines)


def story_agent_build_test_file(
    project_path: str,
    structured_content_path: Optional[str] = None,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate pytest-bdd test code from feature files.
    
    This builder reads .feature files and generates pytest-bdd test code
    with step definitions, fixtures, and helpers. All step definitions
    must match feature files exactly.
    
    Args:
        project_path: Path to project root (should be agents/story_bot directory)
        structured_content_path: Optional path to structured.json (for reference)
        output_path: Optional specific output path (not used, file goes to src/)
        template_path: Optional template path (not used)
    
    Returns:
        Dictionary with summary of generated test code
    """
    builder = StoryTestFileBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None
    )
    return builder.build()


class StoryFeatureAnnotatorBuilder(BaseBuilder):
    """
    Builder for annotating markdown story files with navigation links to step definitions.
    
    This builder reads .md story files and the test file, then adds annotation
    comments linking each step (in gherkin code blocks) to its corresponding step definition function.
    """
    def build(self, test_file_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Annotate markdown story files with navigation links to step definitions.
        
        Args:
            test_file_path: Optional path to test file. Defaults to src/stories_acceptance_tests.py
        
        Returns:
            Dictionary with summary of annotated files
        """
        # Find markdown story files
        map_base = self._find_map_directory()
        if not map_base:
            return {
                "status": "error",
                "message": "Could not find docs/stories/map directory",
                "annotated_files": []
            }
        
        markdown_files = list(map_base.rglob("*.md"))
        if not markdown_files:
            return {
                "status": "error",
                "message": "No .md files found in docs/stories/map",
                "annotated_files": []
            }
        
        # Find test file
        if test_file_path is None:
            test_file_path = self.project_path / "src" / "stories_acceptance_tests.py"
        
        if not test_file_path.exists():
            return {
                "status": "error",
                "message": f"Test file not found: {test_file_path}",
                "annotated_files": []
            }
        
        # Parse test file to build step definition map
        step_definitions = self._parse_step_definitions(test_file_path)
        
        # Annotate each markdown file
        annotated_files = []
        for markdown_file in markdown_files:
            try:
                annotated = self._annotate_markdown_file(markdown_file, step_definitions, test_file_path)
                if annotated:
                    annotated_files.append(str(markdown_file.relative_to(map_base)))
            except Exception as e:
                # Continue with other files if one fails
                continue
        
        return {
            "status": "success",
            "message": f"Annotated {len(annotated_files)} markdown files",
            "annotated_files": annotated_files,
            "test_file_path": str(test_file_path)
        }
    
    def _find_map_directory(self) -> Optional[Path]:
        """Find the docs/stories/map directory."""
        possible_paths = [
            self.project_path / "docs" / "docs" / "stories" / "map",
            self.project_path / "docs" / "stories" / "map",
            self.project_path.parent / "stories" / "docs" / "stories" / "map",
        ]
        
        if self.structured_content_path:
            # Try to infer from structured.json location
            structured_parent = self.structured_content_path.parent
            possible_paths.insert(0, structured_parent / "map")
            # Also try docs/docs/stories/map if structured.json is in docs/stories
            if "stories" in structured_parent.parts:
                possible_paths.insert(0, structured_parent.parent.parent / "docs" / "stories" / "map")
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path
        
        return None
    
    def _parse_step_definitions(self, test_file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Parse test file to extract step definitions and their line numbers.
        
        Returns:
            Dictionary mapping step text to {line_number, function_name, decorator}
        """
        step_definitions = {}
        content = test_file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for step decorators
            if line.startswith('@given(') or line.startswith('@when(') or line.startswith('@then('):
                # Extract step text from decorator
                step_text_match = re.search(r'["\'](.+?)["\']', line)
                if step_text_match:
                    step_text = step_text_match.group(1)
                    line_number = i + 1  # 1-based line numbers
                    
                    # Find function name on next non-empty line
                    func_name = None
                    j = i + 1
                    while j < len(lines) and j < i + 5:
                        func_line = lines[j].strip()
                        func_match = re.match(r'def\s+(\w+)\s*\(', func_line)
                        if func_match:
                            func_name = func_match.group(1)
                            break
                        j += 1
                    
                    # Determine decorator type
                    decorator = 'given' if '@given' in line else ('when' if '@when' in line else 'then')
                    
                    step_definitions[step_text] = {
                        'line_number': line_number,
                        'function_name': func_name or 'unknown',
                        'decorator': decorator
                    }
            i += 1
        
        return step_definitions
    
    def _annotate_markdown_file(self, markdown_file: Path, step_definitions: Dict[str, Dict[str, Any]], 
                               test_file_path: Path) -> bool:
        """
        Annotate a markdown story file with navigation links to step definitions.
        
        Steps are found within ```gherkin code blocks and annotated with links.
        
        Args:
            markdown_file: Path to markdown file to annotate
            step_definitions: Map of step text to step definition info
            test_file_path: Path to test file for relative links
        
        Returns:
            True if file was modified, False otherwise
        """
        content = markdown_file.read_text(encoding='utf-8')
        
        # Calculate relative path from markdown file to test file
        # Markdown file is in docs/docs/stories/map/..., test file is in src/
        try:
            # Calculate depth of markdown file relative to project_path
            md_depth = len(markdown_file.parent.relative_to(self.project_path).parts)
            # Go up md_depth levels, then down to src/stories_acceptance_tests.py
            test_rel = '../' * md_depth + 'src/stories_acceptance_tests.py'
        except ValueError:
            # Fallback: use simple relative path calculation
            try:
                # Both paths relative to project_path
                md_rel = markdown_file.parent.relative_to(self.project_path)
                test_rel_file = test_file_path.relative_to(self.project_path)
                # Count how many levels up we need to go
                levels_up = len(md_rel.parts)
                test_rel = '../' * levels_up + str(test_rel_file).replace('\\', '/')
            except:
                test_rel = 'src/stories_acceptance_tests.py'
        
        lines = content.split('\n')
        new_lines = []
        modified = False
        in_gherkin_block = False
        gherkin_indent = 0
        prev_step_type = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect start of gherkin code block
            if re.match(r'^\s*```gherkin', line, re.IGNORECASE):
                in_gherkin_block = True
                gherkin_indent = len(line) - len(line.lstrip())
                new_lines.append(line)
                i += 1
                continue
            
            # Detect end of code block
            if in_gherkin_block and line.strip() == '```':
                in_gherkin_block = False
                prev_step_type = None
                new_lines.append(line)
                i += 1
                continue
            
            # If we're inside a gherkin block, look for steps
            if in_gherkin_block:
                # Remove old comment-style annotations (lines starting with # 🔗 →)
                if line.strip().startswith('#') and '🔗' in line and '[' not in line:
                    # Skip old comment-style annotations
                    modified = True
                    i += 1
                    continue
                
                # Skip old markdown link annotations (they'll be replaced when we process the step)
                if '🔗' in line and '[' in line and '](' in line:
                    # This is a markdown link annotation - skip it (will be replaced)
                    modified = True
                    i += 1
                    continue
                
                # Check if this line contains a step (Given/When/Then/And)
                step_match = re.match(r'^(\s*)(Given|When|Then|And)\s+(.+)', line, re.IGNORECASE)
                if step_match:
                    
                    indent = step_match.group(1)
                    step_type = step_match.group(2)
                    step_text = step_match.group(3).strip()
                    
                    # Remove trailing comments if any
                    if '#' in step_text and '🔗' not in step_text:
                        step_text = step_text.split('#')[0].strip()
                    
                    # For "And" steps, use previous step type
                    if step_type.upper() == 'AND':
                        if prev_step_type:
                            step_type = prev_step_type
                    else:
                        prev_step_type = step_type
                    
                    # Try to find matching step definition
                    step_key = step_text
                    matched = False
                    
                    if step_key in step_definitions:
                        step_info = step_definitions[step_key]
                        line_num = step_info['line_number']
                        func_name = step_info['function_name']
                        # Create markdown link format: just emoji as clickable link
                        annotation = f"{indent}  [🔗]({test_rel}#L{line_num})"
                        new_lines.append(line)
                        new_lines.append(annotation)
                        modified = True
                        matched = True
                    else:
                        # Try partial match (for parameterized steps)
                        for def_step, def_info in step_definitions.items():
                            # Check if step_text is contained in def_step or vice versa
                            if step_text in def_step or def_step in step_text:
                                line_num = def_info['line_number']
                                func_name = def_info['function_name']
                                # Create markdown link format: just emoji as clickable link
                                annotation = f"{indent}  [🔗]({test_rel}#L{line_num})"
                                new_lines.append(line)
                                new_lines.append(annotation)
                                modified = True
                                matched = True
                                break
                    
                    if not matched:
                        new_lines.append(line)
                else:
                    # Not a step line, just add it
                    new_lines.append(line)
                    # Reset prev_step_type if this is a blank line
                    if not line.strip():
                        prev_step_type = None
            else:
                # Outside gherkin block, just add the line
                new_lines.append(line)
            
            i += 1
        
        if modified:
            # Write back the annotated content
            markdown_file.write_text('\n'.join(new_lines), encoding='utf-8')
        
        return modified


def story_agent_annotate_feature_files(
    project_path: str,
    structured_content_path: Optional[str] = None,
    test_file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Annotate markdown story files with navigation links to step definitions.
    
    This builder reads .md story files and adds annotation comments linking
    each step (in gherkin code blocks) to its corresponding step definition function in the test file.
    
    Args:
        project_path: Path to project root (should be agents/story_bot directory)
        structured_content_path: Optional path to structured.json (for reference)
        test_file_path: Optional path to test file. Defaults to src/stories_acceptance_tests.py
    
    Returns:
        Dictionary with summary of annotated files
    """
    builder = StoryFeatureAnnotatorBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None
    )
    test_path = Path(test_file_path) if test_file_path else None
    return builder.build(test_file_path=test_path)

