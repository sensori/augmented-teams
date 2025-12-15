"""Scanner for validating scenarios are in story-graph.json."""

from typing import List, Dict, Any, Optional, Set
from .story_scanner import StoryScanner
from .story_map import StoryNode, Story, StoryMap
from .violation import Violation


def _get_story_names_from_scope(knowledge_graph: Dict[str, Any]) -> Set[str]:
    """Extract story names based on scope configuration.
    
    Scope can be defined in multiple ways:
    1. _validation_scope.story_names - explicit list of story names
    2. _validation_scope.increment_priorities - list of increment priorities (e.g., [1, 2])
    3. _validation_scope.epic_names - list of epic names (e.g., ["Epic A", "Epic B"])
    4. _validation_scope.all - validate all stories (no filtering)
    
    Multiple scope types can be combined (union of all matches).
    
    Returns a set of story names that are in scope for validation.
    If scope is 'all' or not specified, returns None (meaning validate all).
    """
    scope_config = knowledge_graph.get('_validation_scope', {})
    
    # If 'all' is True, validate everything
    if scope_config.get('all') is True:
        return None
    
    story_names = set()
    
    # Explicit story names list
    if 'story_names' in scope_config:
        story_names_list = scope_config['story_names']
        if isinstance(story_names_list, list):
            story_names.update(story_names_list)
        elif isinstance(story_names_list, str):
            story_names.add(story_names_list)
    
    # Multiple increment priorities
    if 'increment_priorities' in scope_config:
        priorities = scope_config['increment_priorities']
        if isinstance(priorities, list):
            for priority in priorities:
                increment_stories = _get_increment_story_names(knowledge_graph, priority)
                story_names.update(increment_stories)
        elif isinstance(priorities, (int, str)):
            # Single priority (convert to list)
            increment_stories = _get_increment_story_names(knowledge_graph, priorities)
            story_names.update(increment_stories)
    
    # Multiple epic names
    if 'epic_names' in scope_config:
        epic_names_list = scope_config['epic_names']
        if isinstance(epic_names_list, list):
            for epic_name in epic_names_list:
                epic_stories = _get_epic_story_names(knowledge_graph, epic_name)
                story_names.update(epic_stories)
        elif isinstance(epic_names_list, str):
            epic_stories = _get_epic_story_names(knowledge_graph, epic_names_list)
            story_names.update(epic_stories)
    
    # If no scope specified, validate all (return None means validate all)
    if not story_names and not scope_config:
        return None
    
    # Return None if empty (means validate all), otherwise return set
    return story_names if story_names else None


def _get_increment_story_names(knowledge_graph: Dict[str, Any], priority: int) -> Set[str]:
    """Extract all story names from increment with specified priority."""
    story_names = set()
    increments = knowledge_graph.get('increments', [])
    
    # Find increment with matching priority
    for increment in increments:
        inc_priority = increment.get('priority', 999)
        # Handle both int and string priorities
        if isinstance(inc_priority, str):
            priority_map = {'NOW': 1, 'LATER': 2, 'SOON': 1, 'NEXT': 2}
            inc_priority = priority_map.get(inc_priority.upper(), 999)
        
        if inc_priority == priority:
            # Recursively extract all story names from this increment
            _extract_story_names_from_increment(increment, story_names)
            break  # Only process matching increment
    
    return story_names


def _get_epic_story_names(knowledge_graph: Dict[str, Any], epic_name: str) -> Set[str]:
    """Extract all story names from epic with specified name."""
    story_names = set()
    epics = knowledge_graph.get('epics', [])
    
    # Find epic with matching name
    for epic in epics:
        if epic.get('name') == epic_name:
            # Recursively extract all story names from this epic
            _extract_story_names_from_epic(epic, story_names)
            break  # Only process matching epic
    
    return story_names


def _extract_story_names_from_increment(increment_data: Dict[str, Any], story_names: Set[str]) -> None:
    """Recursively extract story names from increment structure."""
    # Extract stories directly in increment
    for story in increment_data.get('stories', []):
        if isinstance(story, dict) and 'name' in story:
            story_names.add(story['name'])
        elif isinstance(story, str):
            story_names.add(story)
    
    # Extract stories from epics
    for epic in increment_data.get('epics', []):
        _extract_story_names_from_epic(epic, story_names)


def _extract_story_names_from_epic(epic_data: Dict[str, Any], story_names: Set[str]) -> None:
    """Recursively extract story names from epic/sub_epic structure."""
    # Extract stories directly in epic
    for story in epic_data.get('stories', []):
        if isinstance(story, dict) and 'name' in story:
            story_names.add(story['name'])
        elif isinstance(story, str):
            story_names.add(story)
    
    # Extract stories from story_groups (new format)
    for story_group in epic_data.get('story_groups', []):
        for story in story_group.get('stories', []):
            if isinstance(story, dict) and 'name' in story:
                story_names.add(story['name'])
            elif isinstance(story, str):
                story_names.add(story)
    
    # Extract stories from sub_epics (recursive)
    for sub_epic in epic_data.get('sub_epics', []):
        _extract_story_names_from_epic(sub_epic, story_names)


class ScenariosOnStoryDocsScanner(StoryScanner):
    """Validates scenarios are in story-graph.json (scenarios or scenario_outlines fields).
    
    Only validates stories in scope. Scope is determined by _validation_scope in knowledge_graph:
    - story_names: explicit list of story names to validate
    - increment_priorities: list of increment priorities (e.g., [1, 2]) - validates stories in those increments
    - epic_names: list of epic names (e.g., ["Epic A", "Epic B"]) - validates stories in those epics
    - all: validate all stories (if scope is 'all' or not specified)
    
    Multiple scope types can be combined (union of all matches).
    """
    
    def __init__(self):
        super().__init__()
        self._in_scope_story_names: Optional[Set[str]] = None
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Override scan to determine scope."""
        # Determine in-scope story names
        self._in_scope_story_names = _get_story_names_from_scope(knowledge_graph)
        
        # Call parent scan method (pass through test_files and code_files)
        return super().scan(knowledge_graph, rule_obj, test_files=test_files, code_files=code_files)
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            # Skip stories not in scope (if scope is defined)
            if self._in_scope_story_names is not None:
                if node.name not in self._in_scope_story_names:
                    # Story is out of scope, skip validation
                    return violations
            
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            scenario_outlines = story_data.get('scenario_outlines', [])
            
            # Check if story has scenarios OR scenario_outlines in JSON
            # Story is valid if it has EITHER scenarios OR scenario_outlines (not requiring both)
            has_scenarios = scenarios and len(scenarios) > 0
            has_scenario_outlines = scenario_outlines and len(scenario_outlines) > 0
            
            if not has_scenarios and not has_scenario_outlines:
                location = node.map_location()
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Story "{node.name}" has no scenarios or scenario_outlines in story-graph.json - scenarios should be in JSON (scenarios or scenario_outlines fields)',
                    location=location,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
