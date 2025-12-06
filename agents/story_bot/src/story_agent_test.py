import pytest
import json
import sys
from pathlib import Path
from xml.etree.ElementTree import fromstring

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

base_agent_path = Path(__file__).parent.parent.parent / "base" / "src"
if str(base_agent_path) not in sys.path:
    sys.path.insert(0, str(base_agent_path))

from agent import DrawIOBuilder
from agents.story_bot.src.story_agent import (
    DrawIOStoryBuilder,
    DrawIOStoryShapeBuilder,
    story_agent_build_drawio_story_shape
)


@pytest.fixture
def temp_project(tmp_path):
    project = tmp_path / "test_project"
    project.mkdir()
    (project / "docs" / "stories").mkdir(parents=True)
    return project


@pytest.fixture
def sample_story_graph():
    return {
        "solution": {
            "name": "Test Solution",
            "purpose": "Test purpose"
        },
        "epics": [
            {
                "name": "Epic One",
                "purpose": "First epic",
                "features": [
                    {
                        "name": "Feature One",
                        "purpose": "First feature",
                        "story_count": "3",
                        "domain_ac": {
                            "concepts": [],
                            "behaviors": []
                        },
                        "stories": [
                            {
                                "name": "Story 1.1",
                                "description": "First story",
                                "optional": False,
                                "sequential_order": 1,
                                "vertical_order": None,
                                "behavioral_ac": ["As a user, I can do X"],
                                "scenarios": []
                            },
                            {
                                "name": "Story 1.2",
                                "description": "Second story",
                                "optional": True,
                                "sequential_order": 1,
                                "vertical_order": 1,
                                "behavioral_ac": ["As a user, I can do Y"],
                                "scenarios": []
                            },
                            {
                                "name": "Story 1.3",
                                "description": "Third story",
                                "optional": False,
                                "sequential_order": 2,
                                "vertical_order": None,
                                "behavioral_ac": ["As a user, I can do Z"],
                                "scenarios": []
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def structured_json_file(temp_project, sample_story_graph):
    structured_path = temp_project / "docs" / "stories" / "structured.json"
    structured_path.write_text(json.dumps(sample_story_graph), encoding='utf-8')
    return structured_path


class TestDrawIOBuilder:
    def test_init_with_structured_path(self, temp_project, structured_json_file):
        builder = DrawIOBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        assert builder.project_path == temp_project
        assert builder.structured_content_path == structured_json_file
    
    def test_init_auto_find_structured(self, temp_project, structured_json_file):
        builder = DrawIOBuilder(project_path=temp_project)
        assert builder.structured_content_path == structured_json_file
    
    def test_load_story_graph(self, temp_project, structured_json_file, sample_story_graph):
        builder = DrawIOBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        graph = builder._load_story_graph()
        assert graph == sample_story_graph
    
    def test_load_story_graph_not_found(self, temp_project):
        builder = DrawIOBuilder(project_path=temp_project)
        with pytest.raises(FileNotFoundError):
            builder._load_story_graph()


class TestDrawIOStoryBuilder:
    def test_find_template(self, temp_project, structured_json_file):
        builder = DrawIOStoryBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        template_path = builder._find_template()
        assert template_path is None or isinstance(template_path, Path)


class TestDrawIOStoryShapeBuilder:
    def test_build_creates_output_file(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        result = builder.build(output_path=output_path)
        
        assert result["output_path"] == str(output_path)
        assert output_path.exists()
        assert result["summary"]["diagram_generated"] is True
    
    def test_build_default_output_path(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        default_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        result = builder.build()
        
        assert result["output_path"] == str(default_path)
        assert default_path.exists()
    
    def test_build_generates_valid_xml(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        assert root.tag == 'mxfile'
    
    def test_build_creates_epic_cells(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        epic_cells = root.findall(".//mxCell[@id='epic1']")
        assert len(epic_cells) > 0
        assert epic_cells[0].get('value') == 'Epic One'
    
    def test_build_creates_feature_cells(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        feature_cells = root.findall(".//mxCell[@id='e1f1']")
        assert len(feature_cells) > 0
        assert 'Feature One' in feature_cells[0].get('value', '')
    
    def test_build_positions_mandatory_stories_horizontally(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        story1 = root.find(".//mxCell[@id='e1f1s1']")
        story3 = root.find(".//mxCell[@id='e1f1s3']")
        
        assert story1 is not None
        assert story3 is not None
        
        geom1 = story1.find('mxGeometry')
        geom3 = story3.find('mxGeometry')
        
        assert geom1 is not None
        assert geom3 is not None
        
        y1 = float(geom1.get('y', 0))
        y3 = float(geom3.get('y', 0))
        x1 = float(geom1.get('x', 0))
        x3 = float(geom3.get('x', 0))
        
        assert y1 == y3
        assert x3 > x1
    
    def test_build_positions_optional_stories_vertically(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        story1 = root.find(".//mxCell[@id='e1f1s1']")
        story2 = root.find(".//mxCell[@id='e1f1s2']")
        
        assert story1 is not None
        assert story2 is not None
        
        geom1 = story1.find('mxGeometry')
        geom2 = story2.find('mxGeometry')
        
        assert geom1 is not None
        assert geom2 is not None
        
        x1 = float(geom1.get('x', 0))
        x2 = float(geom2.get('x', 0))
        y1 = float(geom1.get('y', 0))
        y2 = float(geom2.get('y', 0))
        
        assert x1 == x2
        assert y2 > y1
    
    def test_build_calculates_feature_width(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        feature = root.find(".//mxCell[@id='e1f1']")
        assert feature is not None
        
        geom = feature.find('mxGeometry')
        assert geom is not None
        
        width = float(geom.get('width', 0))
        assert width >= 2 * builder.STORY_SPACING_X
    
    def test_build_calculates_epic_width(self, temp_project, structured_json_file):
        builder = DrawIOStoryShapeBuilder(
            project_path=temp_project,
            structured_content_path=structured_json_file
        )
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        builder.build(output_path=output_path)
        
        xml_content = output_path.read_text(encoding='utf-8')
        root = fromstring(xml_content)
        
        epic = root.find(".//mxCell[@id='epic1']")
        assert epic is not None
        
        geom = epic.find('mxGeometry')
        assert geom is not None
        
        width = float(geom.get('width', 0))
        assert width > 0


class TestStoryAgentBuildDrawIOStoryShape:
    def test_function_creates_diagram(self, temp_project, structured_json_file):
        output_path = temp_project / "docs" / "stories" / "story-map.drawio"
        
        result = story_agent_build_drawio_story_shape(
            project_path=str(temp_project),
            structured_content_path=str(structured_json_file),
            output_path=str(output_path)
        )
        
        assert result["output_path"] == str(output_path)
        assert output_path.exists()
        assert result["summary"]["diagram_generated"] is True
    
    def test_function_with_defaults(self, temp_project, structured_json_file):
        result = story_agent_build_drawio_story_shape(
            project_path=str(temp_project)
        )
        
        default_path = temp_project / "docs" / "stories" / "story-map.drawio"
        assert result["output_path"] == str(default_path)
        assert default_path.exists()
    
    def test_function_handles_missing_structured_json(self, temp_project):
        with pytest.raises(FileNotFoundError):
            story_agent_build_drawio_story_shape(
                project_path=str(temp_project)
            )

