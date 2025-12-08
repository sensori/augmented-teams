"""
Story Scenarios Synchronizer

Renders story markdown files from story graph JSON.
Follows the same pattern as DrawIOSynchronizer.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import json
import os
import re


def format_acceptance_criteria(ac_list):
    """Format acceptance criteria list into markdown"""
    if not ac_list:
        return ""
    
    formatted = []
    for ac in ac_list:
        # Clean up (AC) prefix if present
        ac_text = ac.replace("(AC) ", "").strip()
        if ac_text.startswith("WHEN") or ac_text.startswith("AND") or ac_text.startswith("THEN"):
            formatted.append(f"- **{ac_text}**")
        else:
            formatted.append(f"- **WHEN** {ac_text}")
    
    return "\n".join(formatted)


def format_scenarios(scenarios_list):
    """Format scenarios list into markdown"""
    if not scenarios_list:
        return ""
    
    formatted = []
    for scenario in scenarios_list:
        name = scenario.get('name', 'Unnamed Scenario')
        steps = scenario.get('steps', '')

        # Normalize steps into multi-line text:
        # - If provided as a list, join with newlines.
        # - If provided as a string that includes literal "\n", convert to real newlines.
        if isinstance(steps, list):
            steps_text = "\n".join(steps)
        else:
            steps_text = str(steps).replace("\\n", "\n")

        examples_block = ""
        examples_data = scenario.get('examples')
        if isinstance(examples_data, list) and examples_data:
            if all(isinstance(row, dict) for row in examples_data):
                # Build a single table using all keys across rows (preserve first-seen order)
                columns = []
                for row in examples_data:
                    for key in row.keys():
                        if key not in columns:
                            columns.append(key)
                header = "| " + " | ".join(columns) + " |"
                separator = "| " + " | ".join(["---"] * len(columns)) + " |"
                rows = []
                for row in examples_data:
                    rows.append("| " + " | ".join(str(row.get(col, "")).strip() for col in columns) + " |")
                table = "\n".join([header, separator] + rows)
                examples_block = f"\n**Examples:**\n{table}\n"
            elif all(isinstance(row, str) for row in examples_data):
                rows = "\n".join([f"| {row} |  |" for row in examples_data])
                examples_block = (
                    "\n**Examples:**\n"
                    "| variable | value |\n"
                    "| --- | --- |\n"
                    f"{rows}\n"
                )

        formatted.append(
            f"### Scenario: {name}\n\n**Steps:**\n```gherkin\n{steps_text}\n```\n{examples_block}"
        )
    
    return "\n\n".join(formatted)


def build_folder_path_from_graph(epic_name, sub_epic_name, story_graph_data):
    """
    Build folder path dynamically from story graph structure.
    Traverses the graph to find the actual epic and sub_epic names.
    """
    # Find the epic in the graph
    for epic in story_graph_data.get('epics', []):
        if epic['name'] == epic_name:
            epic_folder = f"[Epic] {epic_name}"
            
            # If sub_epic_name matches the epic itself, it's a top-level epic
            if sub_epic_name == epic_name:
                return epic_folder, epic_name
            
            # Otherwise, find the sub_epic in the epic's sub_epics
            def find_sub_epic(sub_epics, target_name):
                for sub_epic in sub_epics:
                    if sub_epic['name'] == target_name:
                        return f"[Sub Epic] {target_name}"
                    # Recursively check nested sub_epics
                    if 'sub_epics' in sub_epic:
                        result = find_sub_epic(sub_epic['sub_epics'], target_name)
                        if result:
                            return result
                return None
            
            sub_epic_folder = find_sub_epic(epic.get('sub_epics', []), sub_epic_name)
            if sub_epic_folder:
                return epic_folder, sub_epic_folder
            
            # If not found in sub_epics, use the provided name with sub-epic prefix
            return epic_folder, f"[Sub Epic] {sub_epic_name}" if sub_epic_name != epic_name else epic_name
    
    # Fallback: use names directly with readable prefixes
    fallback_epic = f"[Epic] {epic_name}"
    fallback_sub_epic = f"[Sub Epic] {sub_epic_name}" if sub_epic_name != epic_name else epic_name
    return fallback_epic, fallback_sub_epic


def create_story_content(story, epic_name, sub_epic_name):
    """Create markdown content for a story"""
    story_name = story['name']
    users = story.get('users', [])
    user_str = ', '.join(users) if users else '[]'
    story_type = story.get('story_type', 'user')
    sequential_order = story.get('sequential_order', 1)
    
    ac_list = story.get('acceptance_criteria', [])
    ac_formatted = format_acceptance_criteria(ac_list)
    
    scenarios_list = story.get('scenarios', [])
    scenarios_formatted = format_scenarios(scenarios_list)
    
    # Default description if not provided
    description = story.get('description', f'{story_name} functionality for the bot system.')
    
    # Default acceptance criteria if not provided
    if not ac_formatted:
        ac_formatted = "- **WHEN** action executes\n- **THEN** action completes successfully"
    
    # Default scenario if not provided
    if not scenarios_formatted:
        scenarios_formatted = f"""### Scenario: {story_name}

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```"""
    
    sub_epic_line = ""
    if sub_epic_name != epic_name:
        sub_epic_line = f"**Sub Epic:** {sub_epic_name}\n"
    
    content = f"""# [Story] {story_name}

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** {epic_name}  
{sub_epic_line}**User:** {user_str}  
**Sequential Order:** {sequential_order}  
**Story Type:** {story_type}

## Story Description

{description}

## Acceptance Criteria

### Behavioral Acceptance Criteria

{ac_formatted}

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

{scenarios_formatted}

"""
    return content


def extract_stories_from_graph(epic, epic_path="", feature_path="", parent_is_epic=True):
    """
    Extract all stories from story graph recursively.
    Dynamically builds folder structure from the graph itself.
    """
    stories = []
    current_epic_path = epic['name'] if not epic_path else f"{epic_path}/{epic['name']}"
    current_is_epic = parent_is_epic and not feature_path
    
    # Get stories from story_groups (include all stories; no user-type filtering)
    for group in epic.get('story_groups', []):
        for story in group.get('stories', []):
            story['epic_path'] = current_epic_path
            story['feature_path'] = feature_path if feature_path else epic['name']
            story['epic_name'] = current_epic_path.split('/')[0] if '/' in current_epic_path else current_epic_path
            story['feature_name'] = feature_path if feature_path else epic['name']
            story['is_epic'] = current_is_epic
            story['is_feature'] = not current_is_epic
            stories.append(story)
    
    # Get stories from sub_epics (these become features)
    for sub_epic in epic.get('sub_epics', []):
        current_feature_path = sub_epic['name']
        # When we go into sub_epics, we're now in feature territory
        stories.extend(extract_stories_from_graph(sub_epic, current_epic_path, current_feature_path, parent_is_epic=False))
    
    return stories


class StoryScenariosSynchronizer:
    """Synchronizer for rendering story markdown files from story graph JSON."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render story markdown files from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path to output directory for story files
            renderer_command: Optional command variant (unused for now)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with output_path, summary, and created files
        """
        input_path = Path(input_path)
        output_dir = Path(output_path)
        base_dir = output_dir / 'map'
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get existing story files to avoid duplicates
        existing_stories = set()
        if base_dir.exists():
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.md') and file.startswith('[Story] '):
                        name = file[2:].replace('.md', '')
                        existing_stories.add(name)
        
        # Extract all stories
        all_stories = []
        for epic in data['epics']:
            all_stories.extend(extract_stories_from_graph(epic))
        
        # Create story files
        created_files = []
        updated_files = []
        
        for story in all_stories:
            story_name = story['name']
            # Build folder path dynamically from story graph structure
            epic_folder, feature_folder = build_folder_path_from_graph(
                story['epic_name'], 
                story['feature_name'],
                data
            )
            
            # Create directory structure using names from the graph
            story_dir = base_dir / epic_folder / feature_folder
            story_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file
            story_file = story_dir / f"[Story] {story_name}.md"
            
            # Generate content
            content = create_story_content(story, story['epic_name'], story['feature_name'])
            
            # Check if file exists
            if story_file.exists():
                updated_files.append(str(story_file.relative_to(output_dir)))
            else:
                created_files.append(str(story_file.relative_to(output_dir)))
            
            # Write file
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'output_path': str(output_dir),
            'summary': {
                'total_stories': len(all_stories),
                'created_files': len(created_files),
                'updated_files': len(updated_files)
            },
            'created_files': created_files,
            'updated_files': updated_files
        }

