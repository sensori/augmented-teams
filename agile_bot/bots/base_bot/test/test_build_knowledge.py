"""
Build Knowledge Tests

Tests for all stories in the 'Build Knowledge' sub-epic:
- Track Activity for Build Knowledge Action
- Proceed To Render Output
- Load Story Graph Into Memory
"""
import pytest
from pathlib import Path
import json
from agile_bot.bots.base_bot.src.bot.build_knowledge_action import BuildKnowledgeAction
from agile_bot.bots.base_bot.src.scanners.story_map import (
    StoryMap, Epic, SubEpic, StoryGroup, Story, Scenario, ScenarioOutline
)
from agile_bot.bots.base_bot.test.test_helpers import (
    bootstrap_env,
    verify_action_tracks_start,
    verify_action_tracks_completion,
    verify_workflow_transition,
    verify_workflow_saves_completed_action,
    create_knowledge_graph_template,
    get_bot_dir
)

# Use fixtures from conftest.py (bot_directory, workspace_directory)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_story_graph():
    return {
        "epics": [
            {
                "name": "Build Knowledge",
                "sequential_order": 1,
                "sub_epics": [
                    {
                        "name": "Load Story Graph",
                        "sequential_order": 1,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [
                                    {
                                        "name": "Load Story Graph Into Memory",
                                        "sequential_order": 1,
                                        "connector": None,
                                        "users": ["Story Bot"],
                                        "story_type": "user",
                                        "sizing": "5 days",
                                        "scenarios": [
                                            {
                                                "name": "Story graph file exists",
                                                "type": "happy_path",
                                                "background": ["Given story graph file exists"],
                                                "steps": [
                                                    "When story graph is loaded",
                                                    "Then story map is created with epics"
                                                ]
                                            },
                                            {
                                                "name": "Story graph file missing",
                                                "type": "error_case",
                                                "background": [],
                                                "steps": [
                                                    "When story graph file does not exist",
                                                    "Then FileNotFoundError is raised"
                                                ]
                                            }
                                        ],
                                        "scenario_outlines": [
                                            {
                                                "name": "Load story graph with different formats",
                                                "type": "happy_path",
                                                "background": ["Given story graph file exists"],
                                                "steps": [
                                                    "When story graph is loaded from \"<file_path>\"",
                                                    "Then story map contains \"<expected_epics>\" epics"
                                                ],
                                                "examples": {
                                                    "columns": ["file_path", "expected_epics"],
                                                    "rows": [
                                                        ["story-graph.json", "2"],
                                                        ["story-graph-v2.json", "3"]
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "story_groups": []
            }
        ]
    }


@pytest.fixture
def story_map(simple_story_graph):
    return StoryMap(simple_story_graph)


# ============================================================================
# STORY: Track Activity for Build Knowledge Action
# ============================================================================

class TestTrackActivityForBuildKnowledgeAction:
    """Story: Track Activity for Build Knowledge Action - Tests activity tracking for build_knowledge."""

    def test_track_activity_when_build_knowledge_action_starts(self, bot_directory, workspace_directory):
        verify_action_tracks_start(bot_directory, workspace_directory, BuildKnowledgeAction, 'build_knowledge')

    def test_track_activity_when_build_knowledge_action_completes(self, bot_directory, workspace_directory):
        verify_action_tracks_completion(
            bot_directory,
            workspace_directory,
            BuildKnowledgeAction,
            'build_knowledge',
            outputs={'knowledge_items_count': 12, 'file_path': 'knowledge.json'},
            duration=420
        )


# ============================================================================
# STORY: Proceed To Render Output
# ============================================================================

class TestProceedToRenderOutput:
    """Story: Proceed To Render Output - Tests transition to render_output action."""

    def test_seamless_transition_from_build_knowledge_to_validate_rules(self, bot_directory, workspace_directory):
        verify_workflow_transition(bot_directory, workspace_directory, 'build_knowledge', 'validate_rules')

    def test_workflow_state_captures_build_knowledge_completion(self, bot_directory, workspace_directory):
        verify_workflow_saves_completed_action(bot_directory, workspace_directory, 'build_knowledge')


# ============================================================================
# STORY: Inject Knowledge Graph Template for Build Knowledge
# ============================================================================

class TestInjectKnowledgeGraphTemplateForBuildKnowledge:
    """Story: Inject Knowledge Graph Template for Build Knowledge - Tests template injection."""

    def test_action_injects_knowledge_graph_template(self, bot_directory, workspace_directory):
        bot_name = 'story_bot'  # Match fixture
        behavior = 'exploration'
        template_name = 'story-graph-explored-outline.json'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create knowledge graph directory structure
        behavior_dir = bot_directory / 'behaviors' / behavior
        kg_dir = behavior_dir / 'content' / 'knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config file that references the template
        config_file = kg_dir / 'build_story_graph_outline.json'
        config_file.write_text(json.dumps({'template': template_name}), encoding='utf-8')
        
        # Create the actual template file
        template_file = kg_dir / template_name
        template_file.write_text(json.dumps({'template': 'knowledge_graph', 'structure': {}}), encoding='utf-8')
        
        action_obj = BuildKnowledgeAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_knowledge_graph_template()
        
        assert 'knowledge_graph_template' in instructions
        assert 'template_path' in instructions
        assert template_name in instructions['template_path']
        assert Path(instructions['template_path']).exists()

    def test_action_raises_error_when_template_missing(self, bot_directory, workspace_directory):
        bot_name = 'story_bot'  # Match fixture
        behavior = 'exploration'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        behavior_dir = bot_directory / 'behaviors' / behavior
        behavior_dir.mkdir(parents=True, exist_ok=True)
        
        action_obj = BuildKnowledgeAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            action_obj.inject_knowledge_graph_template()
        
        error_msg = str(exc_info.value).lower()
        assert 'knowledge graph' in error_msg

    def test_action_loads_and_merges_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action loads and merges instructions for shape build_knowledge
        GIVEN: Base and behavior-specific instructions exist
        WHEN: Action method is invoked
        THEN: Instructions are loaded from both locations and merged
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        # Given: Both instruction files exist
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'build_knowledge'
        
        # Use actual base instructions (copy from base_bot/base_actions)
        from agile_bot.bots.base_bot.test.test_helpers import get_base_actions_dir
        import shutil
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        actual_base_actions_dir = get_base_actions_dir(repo_root)
        actual_instructions_file = actual_base_actions_dir / '3_build_knowledge' / 'instructions.json'
        
        # Create base_actions structure in bot_directory
        bot_base_actions_dir = bot_directory / 'base_actions' / '3_build_knowledge'
        bot_base_actions_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy actual instructions file
        bot_instructions_file = bot_base_actions_dir / 'instructions.json'
        shutil.copy2(actual_instructions_file, bot_instructions_file)
        
        # Create behavior-specific instructions in correct location
        # For build_knowledge, behavior-specific instructions are in:
        # behaviors/{behavior}/2_content/1_knowledge_graph/instructions.json
        behavior_dir = bot_directory / 'behaviors' / behavior
        kg_dir = behavior_dir / '2_content' / '1_knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        behavior_instructions_file = kg_dir / 'instructions.json'
        behavior_instructions_file.write_text(
            json.dumps({
                'behaviorName': behavior,
                'instructions': [f'{behavior}.{action} specific instructions']
            }),
            encoding='utf-8'
        )
        
        # Also create knowledge graph config and template (required for build_knowledge)
        config_file = kg_dir / 'build_story_graph_outline.json'
        config_file.write_text(
            json.dumps({
                'name': 'build_story_graph_outline',
                'path': 'docs/stories/',
                'template': 'story-graph-outline.json',
                'output': 'story-graph.json'
            }),
            encoding='utf-8'
        )
        
        template_file = kg_dir / 'story-graph-outline.json'
        template_file.write_text(
            json.dumps({
                '_explanation': {},
                'epics': []
            }),
            encoding='utf-8'
        )
        
        # When: Call REAL BuildKnowledgeAction API
        action_obj = BuildKnowledgeAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        merged_instructions = action_obj.load_and_merge_instructions()
        
        # Then: Instructions merged from both sources
        assert 'base_instructions' in merged_instructions
        assert 'behavior_instructions' in merged_instructions
        assert merged_instructions['action'] == action
        assert merged_instructions['behavior'] == behavior
        
        # Verify base instructions are present
        base_instructions_list = merged_instructions['base_instructions']
        assert isinstance(base_instructions_list, list)
        assert len(base_instructions_list) > 0
        base_instructions_text = ' '.join(base_instructions_list).lower()
        assert 'build knowledge graph' in base_instructions_text or 'knowledge graph' in base_instructions_text
        
        # Verify behavior-specific instructions are present
        behavior_instructions_list = merged_instructions['behavior_instructions']
        assert isinstance(behavior_instructions_list, list)
        assert len(behavior_instructions_list) > 0
        assert f'{behavior}.{action}' in ' '.join(behavior_instructions_list).lower()

    def test_action_uses_base_instructions_when_behavior_instructions_missing(self, bot_directory, workspace_directory):
        """
        SCENARIO: Action uses base instructions when behavior-specific instructions are missing
        GIVEN: Base instructions exist but behavior-specific instructions do not
        WHEN: Action method is invoked
        THEN: Only base instructions are returned (no behavior_instructions key)
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'build_knowledge'
        
        # Use actual base instructions (copy from base_bot/base_actions)
        from agile_bot.bots.base_bot.test.test_helpers import get_base_actions_dir
        import shutil
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        actual_base_actions_dir = get_base_actions_dir(repo_root)
        actual_instructions_file = actual_base_actions_dir / '3_build_knowledge' / 'instructions.json'
        
        # Create base_actions structure in bot_directory
        bot_base_actions_dir = bot_directory / 'base_actions' / '3_build_knowledge'
        bot_base_actions_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy actual instructions file
        bot_instructions_file = bot_base_actions_dir / 'instructions.json'
        shutil.copy2(actual_instructions_file, bot_instructions_file)
        
        # Create knowledge graph config and template (required for build_knowledge)
        behavior_dir = bot_directory / 'behaviors' / behavior
        kg_dir = behavior_dir / '2_content' / '1_knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = kg_dir / 'build_story_graph_outline.json'
        config_file.write_text(
            json.dumps({
                'name': 'build_story_graph_outline',
                'path': 'docs/stories/',
                'template': 'story-graph-outline.json',
                'output': 'story-graph.json'
            }),
            encoding='utf-8'
        )
        
        template_file = kg_dir / 'story-graph-outline.json'
        template_file.write_text(
            json.dumps({
                '_explanation': {},
                'epics': []
            }),
            encoding='utf-8'
        )
        
        # Do NOT create behavior-specific instructions file
        
        # When: Call BuildKnowledgeAction API
        action_obj = BuildKnowledgeAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        merged_instructions = action_obj.load_and_merge_instructions()
        
        # Then: Only base instructions are present
        assert 'base_instructions' in merged_instructions
        assert 'behavior_instructions' not in merged_instructions
        assert merged_instructions['action'] == action
        assert merged_instructions['behavior'] == behavior

    def test_all_template_variables_are_replaced_in_instructions(self, bot_directory, workspace_directory):
        """
        SCENARIO: All template variables are replaced in final instructions
        GIVEN: Base instructions with {{rules}}, {{schema}}, {{description}}, {{instructions}} placeholders
        WHEN: Action loads and merges instructions with all injections
        THEN: All template variables are replaced with actual content
        """
        # Bootstrap
        bootstrap_env(bot_directory, workspace_directory)
        
        bot_name = 'test_bot'
        behavior = 'shape'
        action = 'build_knowledge'
        
        # Create base instructions with template variables (copy from actual base_actions)
        from agile_bot.bots.base_bot.test.test_helpers import get_base_actions_dir
        import shutil
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        actual_base_actions_dir = get_base_actions_dir(repo_root)
        actual_instructions_file = actual_base_actions_dir / '3_build_knowledge' / 'instructions.json'
        
        # Create base_actions structure in bot_directory
        bot_base_actions_dir = bot_directory / 'base_actions' / '3_build_knowledge'
        bot_base_actions_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy actual instructions file with template variables
        bot_instructions_file = bot_base_actions_dir / 'instructions.json'
        shutil.copy2(actual_instructions_file, bot_instructions_file)
        
        # Create behavior-specific instructions
        behavior_dir = bot_directory / 'behaviors' / behavior
        kg_dir = behavior_dir / '2_content' / '1_knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        behavior_instructions_file = kg_dir / 'instructions.json'
        behavior_instructions_file.write_text(
            json.dumps({
                'behaviorName': behavior,
                'instructions': ['Use verb-noun format', 'Follow INVEST principles']
            }),
            encoding='utf-8'
        )
        
        # Create behavior instructions.json with description and goal
        behavior_instructions_dir = behavior_dir
        behavior_main_instructions_file = behavior_instructions_dir / 'instructions.json'
        behavior_main_instructions_file.write_text(
            json.dumps({
                'description': 'Shape the story map',
                'goal': 'Create initial story structure'
            }),
            encoding='utf-8'
        )
        
        # Create knowledge graph config and template with schema
        config_file = kg_dir / 'build_story_graph_outline.json'
        config_file.write_text(
            json.dumps({
                'name': 'build_story_graph_outline',
                'path': 'docs/stories/',
                'template': 'story-graph-outline.json',
                'output': 'story-graph.json'
            }),
            encoding='utf-8'
        )
        
        template_file = kg_dir / 'story-graph-outline.json'
        template_content = {
            '_explanation': {
                'epics': 'Top-level features',
                'sub_epics': 'Feature breakdowns'
            },
            'epics': []
        }
        template_file.write_text(json.dumps(template_content), encoding='utf-8')
        
        # Create validation rules
        validation_rules_dir = bot_directory / 'validation_rules'
        validation_rules_dir.mkdir(parents=True, exist_ok=True)
        verb_noun_rule = validation_rules_dir / 'verb-noun-format.json'
        verb_noun_rule.write_text(
            json.dumps({
                'name': 'verb-noun-format',
                'description': 'Stories must use verb-noun format',
                'examples': ['Create user account', 'Update profile']
            }),
            encoding='utf-8'
        )
        
        # When: Call BuildKnowledgeAction and get final instructions
        action_obj = BuildKnowledgeAction(
            bot_name=bot_name,
            behavior=behavior,
            bot_directory=bot_directory
        )
        
        # Execute the full instruction loading and injection process
        instructions = action_obj.load_and_merge_instructions()
        kg_data = action_obj.inject_knowledge_graph_template()
        instructions.update(kg_data)
        action_obj.inject_schema_description_instructions(instructions)
        action_obj.inject_rules(instructions)
        
        # Then: All template variables should be replaced
        base_instructions_text = '\n'.join(instructions.get('base_instructions', []))
        
        # Verify {{rules}} is replaced (should not appear as placeholder)
        assert '{{rules}}' not in base_instructions_text
        assert 'verb-noun format' in base_instructions_text or 'verb-noun-format' in base_instructions_text
        
        # Verify {{schema}} is replaced
        assert '{{schema}}' not in base_instructions_text
        assert 'epics' in base_instructions_text or 'Top-level features' in base_instructions_text
        
        # Verify {{description}} is replaced
        assert '{{description}}' not in base_instructions_text
        assert 'Shape the story map' in base_instructions_text or 'Create initial story structure' in base_instructions_text
        
        # Verify {{instructions}} is replaced
        assert '{{instructions}}' not in base_instructions_text
        assert 'Use verb-noun format' in base_instructions_text or 'Follow INVEST principles' in base_instructions_text


# ============================================================================
# STORY: Update Existing Knowledge Graph Instead of Creating New File
# ============================================================================

class TestUpdateExistingKnowledgeGraph:
    """Story: Update Existing Knowledge Graph - Tests that build_knowledge updates existing story-graph.json instead of creating a new file."""

    def test_prioritization_updates_existing_story_graph_json(self, bot_directory, workspace_directory):
        """
        Test that prioritization behavior updates existing story-graph.json by adding increments array,
        rather than creating a separate story-graph-increments.json file.
        """
        bot_name = 'story_bot'
        behavior = 'prioritization'
        
        # Bootstrap environment
        bootstrap_env(bot_directory, workspace_directory)
        
        # Create existing story-graph.json with epics (from shape behavior)
        stories_dir = workspace_directory / 'docs' / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        
        existing_story_graph = {
            "epics": [
                {
                    "name": "Manage Mobs",
                    "sequential_order": 1,
                    "estimated_stories": 6,
                    "domain_concepts": [
                        {
                            "name": "Mob",
                            "responsibilities": [
                                {
                                    "name": "Groups minions together for coordinated action",
                                    "collaborators": ["Minion"]
                                }
                            ]
                        }
                    ],
                    "sub_epics": []
                }
            ]
        }
        
        story_graph_path = stories_dir / 'story-graph.json'
        story_graph_path.write_text(json.dumps(existing_story_graph, indent=2), encoding='utf-8')
        
        # Create knowledge graph config for prioritization
        behavior_dir = bot_directory / 'behaviors' / behavior
        kg_dir = behavior_dir / 'content' / '1_knowledge_graph'
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = kg_dir / 'build_story_graph_increments.json'
        config_data = {
            "name": "build_story_graph_outline",
            "path": "docs/stories",
            "template": "story_graph_increments.json",
            "output": "story-graph.json"
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        
        # Create template file
        template_file = kg_dir / 'story_graph_increments.json'
        template_content = {
            "_explanation": {},
            "epics": [],
            "increments": []
        }
        template_file.write_text(json.dumps(template_content), encoding='utf-8')
        
        # Create action and get instructions
        action_obj = BuildKnowledgeAction(bot_name=bot_name, behavior=behavior, bot_directory=bot_directory)
        instructions = action_obj.inject_knowledge_graph_template()
        
        # Verify instructions include update guidance
        assert 'knowledge_graph_config' in instructions
        assert instructions['knowledge_graph_config']['output'] == 'story-graph.json'
        
        # Verify that instructions should indicate updating existing file
        # The instructions should guide the LLM to load existing story-graph.json and add increments
        assert 'template_path' in instructions
        
        # Verify existing file still exists and wasn't replaced
        assert story_graph_path.exists()
        
        # Verify that the config specifies the same output file (not a new file)
        config = instructions['knowledge_graph_config']
        assert config['output'] == 'story-graph.json'
        assert config['path'] == 'docs/stories'
        
        # The actual update logic should be in the instructions passed to LLM
        # This test verifies the action provides the correct guidance


# ============================================================================
# STORY: Load Story Graph Into Memory
# ============================================================================

class TestLoadStoryGraphIntoMemory:
    """Story: Load Story Graph Into Memory - Tests loading story graph and creating StoryMap object model."""
    
    def test_story_map_loads_epics(self, story_map):
        epics = story_map.epics()
        assert len(epics) == 1
        assert isinstance(epics[0], Epic)
        assert epics[0].name == "Build Knowledge"
    
    def test_epic_has_sub_epics(self, story_map):
        epics = story_map.epics()
        epic = epics[0]
        children = epic.children
        
        assert len(children) == 1
        assert isinstance(children[0], SubEpic)
        assert children[0].name == "Load Story Graph"
    
    def test_sub_epic_has_story_groups(self, story_map):
        epics = story_map.epics()
        epic = epics[0]
        sub_epic = epic.children[0]
        children = sub_epic.children
        
        assert len(children) == 1
        assert isinstance(children[0], StoryGroup)
    
    def test_story_group_has_stories(self, story_map):
        epics = story_map.epics()
        epic = epics[0]
        sub_epic = epic.children[0]
        story_group = sub_epic.children[0]
        stories = story_group.children
        
        assert len(stories) == 1
        assert isinstance(stories[0], Story)
        assert stories[0].name == "Load Story Graph Into Memory"
    
    def test_story_has_properties(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        
        assert story.name == "Load Story Graph Into Memory"
        assert story.users == ["Story Bot"]
        assert story.story_type == "user"
        assert story.sizing == "5 days"
        assert story.sequential_order == 1
        assert story.connector is None
    
    def test_story_has_scenarios(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenarios = story.scenarios
        
        assert len(scenarios) == 2
        assert isinstance(scenarios[0], Scenario)
        assert scenarios[0].name == "Story graph file exists"
        assert scenarios[0].type == "happy_path"
        assert scenarios[1].name == "Story graph file missing"
        assert scenarios[1].type == "error_case"
    
    def test_scenario_has_properties(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario = story.scenarios[0]
        
        assert scenario.name == "Story graph file exists"
        assert scenario.type == "happy_path"
        assert len(scenario.background) == 1
        assert len(scenario.steps) == 2
        assert scenario.background[0] == "Given story graph file exists"
        assert scenario.steps[0] == "When story graph is loaded"
    
    def test_scenario_default_test_method(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario = story.scenarios[0]
        
        assert scenario.default_test_method == "test_story_graph_file_exists"
    
    def test_story_has_scenario_outlines(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario_outlines = story.scenario_outlines
        
        assert len(scenario_outlines) == 1
        assert isinstance(scenario_outlines[0], ScenarioOutline)
        assert scenario_outlines[0].name == "Load story graph with different formats"
    
    def test_scenario_outline_has_examples(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario_outline = story.scenario_outlines[0]
        
        assert len(scenario_outline.examples_columns) == 2
        assert scenario_outline.examples_columns == ["file_path", "expected_epics"]
        assert len(scenario_outline.examples_rows) == 2
        assert scenario_outline.examples_rows[0] == ["story-graph.json", "2"]
    
    def test_story_default_test_class(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        
        assert story.default_test_class == "TestLoadStoryGraphIntoMemory"
    
    def test_story_map_walk_traverses_all_nodes(self, story_map):
        epics = story_map.epics()
        epic = epics[0]
        
        nodes = list(story_map.walk(epic))
        
        assert len(nodes) == 4
        assert isinstance(nodes[0], Epic)
        assert nodes[0].name == "Build Knowledge"
        assert isinstance(nodes[1], SubEpic)
        assert nodes[1].name == "Load Story Graph"
        assert isinstance(nodes[2], StoryGroup)
        assert isinstance(nodes[3], Story)
        assert nodes[3].name == "Load Story Graph Into Memory"
    
    def test_map_location_for_epic(self, story_map):
        epics = story_map.epics()
        epic = epics[0]
        
        assert epic.map_location() == "epics[0].name"
        assert epic.map_location('sequential_order') == "epics[0].sequential_order"
    
    def test_map_location_for_sub_epic(self, story_map):
        epics = story_map.epics()
        sub_epic = epics[0].children[0]
        
        assert sub_epic.map_location() == "epics[0].sub_epics[0].name"
    
    def test_map_location_for_story(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        
        assert story.map_location() == "epics[0].sub_epics[0].story_groups[0].stories[0].name"
        assert story.map_location('sizing') == "epics[0].sub_epics[0].story_groups[0].stories[0].sizing"
    
    def test_scenario_map_location(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario = story.scenarios[0]
        
        assert scenario.map_location() == "epics[0].sub_epics[0].story_groups[0].stories[0].scenarios[0].name"
    
    def test_scenario_outline_map_location(self, story_map):
        epics = story_map.epics()
        story = epics[0].children[0].children[0].children[0]
        scenario_outline = story.scenario_outlines[0]
        
        assert scenario_outline.map_location() == "epics[0].sub_epics[0].story_groups[0].stories[0].scenario_outlines[0].name"
    
    def test_from_bot_loads_story_graph(self, tmp_path):
        bot_directory = tmp_path / "test_bot"
        bot_directory.mkdir()
        docs_dir = bot_directory / "docs" / "stories"
        docs_dir.mkdir(parents=True)
        
        story_graph = {
            "epics": [
                {
                    "name": "Test Epic",
                    "sequential_order": 1,
                    "sub_epics": [],
                    "story_groups": []
                }
            ]
        }
        
        story_graph_path = docs_dir / "story-graph.json"
        story_graph_path.write_text(json.dumps(story_graph), encoding='utf-8')
        
        class MockBot:
            def __init__(self, bot_directory):
                self.bot_directory = bot_directory
        
        bot = MockBot(bot_directory)
        story_map = StoryMap.from_bot(bot)
        
        assert len(story_map.epics()) == 1
        assert story_map.epics()[0].name == "Test Epic"
    
    def test_from_bot_with_path(self, tmp_path):
        bot_directory = tmp_path / "test_bot"
        bot_directory.mkdir()
        docs_dir = bot_directory / "docs" / "stories"
        docs_dir.mkdir(parents=True)
        
        story_graph = {
            "epics": [
                {
                    "name": "Test Epic",
                    "sequential_order": 1,
                    "sub_epics": [],
                    "story_groups": []
                }
            ]
        }
        
        story_graph_path = docs_dir / "story-graph.json"
        story_graph_path.write_text(json.dumps(story_graph), encoding='utf-8')
        
        story_map = StoryMap.from_bot(bot_directory)
        
        assert len(story_map.epics()) == 1
        assert story_map.epics()[0].name == "Test Epic"
    
    def test_from_bot_raises_when_file_not_found(self, tmp_path):
        bot_directory = tmp_path / "test_bot"
        bot_directory.mkdir()
        
        class MockBot:
            def __init__(self, bot_directory):
                self.bot_directory = bot_directory
        
        bot = MockBot(bot_directory)
        
        with pytest.raises(FileNotFoundError):
            StoryMap.from_bot(bot)
