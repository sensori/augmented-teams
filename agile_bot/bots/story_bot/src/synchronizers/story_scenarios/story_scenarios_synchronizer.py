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
        formatted.append(f"### Scenario: {name}\n\n**Steps:**\n```gherkin\n{steps}\n```")
    
    return "\n\n".join(formatted)


def build_folder_path_from_graph(epic_name, feature_name, story_graph_data):
    """
    Build folder path dynamically from story graph structure.
    Traverses the graph to find the actual epic and feature/sub_epic names.
    """
    # Find the epic in the graph
    for epic in story_graph_data.get('epics', []):
        if epic['name'] == epic_name:
            epic_folder = f"🎯 {epic_name}"
            
            # If feature_name matches the epic itself, it's a top-level feature
            if feature_name == epic_name:
                return epic_folder, epic_name
            
            # Otherwise, find the feature/sub_epic in the epic's sub_epics
            def find_feature_in_sub_epics(sub_epics, target_name):
                for sub_epic in sub_epics:
                    if sub_epic['name'] == target_name:
                        return f"⚙️ {target_name}"
                    # Recursively check nested sub_epics
                    if 'sub_epics' in sub_epic:
                        result = find_feature_in_sub_epics(sub_epic['sub_epics'], target_name)
                        if result:
                            return result
                return None
            
            feature_folder = find_feature_in_sub_epics(epic.get('sub_epics', []), feature_name)
            if feature_folder:
                return epic_folder, feature_folder
            
            # If not found in sub_epics, use the feature_name as-is
            return epic_folder, feature_name
    
    # Fallback: use names directly with emoji prefixes
    return f"🎯 {epic_name}", f"⚙️ {feature_name}" if feature_name != epic_name else feature_name


def create_story_content(story, epic_name, feature_name):
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
    
    content = f"""# 📝 {story_name}

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** {epic_name}  
**Feature:** {feature_name}

**User:** {user_str}  
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
    
    # Get stories from story_groups
    for group in epic.get('story_groups', []):
        for story in group.get('stories', []):
            users = story.get('users', [])
            story_type = story.get('story_type', 'user')
            
            # Filter: Only Bot/system stories, exclude Human/AI Chat
            is_bot_story = (
                any('Bot' in str(u) for u in users) or 
                story_type == 'system' or
                not users
            )
            is_human_ai = any(u in ['Human', 'AI Chat'] for u in users)
            
            if is_bot_story and not is_human_ai:
                # Store the actual names from the graph
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
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get existing story files to avoid duplicates
        existing_stories = set()
        if output_dir.exists():
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md') and file.startswith('📝'):
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
            story_dir = output_dir / epic_folder / feature_folder
            story_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file
            story_file = story_dir / f"📝 {story_name}.md"
            
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
        formatted.append(f"### Scenario: {name}\n\n**Steps:**\n```gherkin\n{steps}\n```")
    
    return "\n\n".join(formatted)


def build_folder_path_from_graph(epic_name, feature_name, story_graph_data):
    """
    Build folder path dynamically from story graph structure.
    Traverses the graph to find the actual epic and feature/sub_epic names.
    """
    # Find the epic in the graph
    for epic in story_graph_data.get('epics', []):
        if epic['name'] == epic_name:
            epic_folder = f"🎯 {epic_name}"
            
            # If feature_name matches the epic itself, it's a top-level feature
            if feature_name == epic_name:
                return epic_folder, epic_name
            
            # Otherwise, find the feature/sub_epic in the epic's sub_epics
            def find_feature_in_sub_epics(sub_epics, target_name):
                for sub_epic in sub_epics:
                    if sub_epic['name'] == target_name:
                        return f"⚙️ {target_name}"
                    # Recursively check nested sub_epics
                    if 'sub_epics' in sub_epic:
                        result = find_feature_in_sub_epics(sub_epic['sub_epics'], target_name)
                        if result:
                            return result
                return None
            
            feature_folder = find_feature_in_sub_epics(epic.get('sub_epics', []), feature_name)
            if feature_folder:
                return epic_folder, feature_folder
            
            # If not found in sub_epics, use the feature_name as-is
            return epic_folder, feature_name
    
    # Fallback: use names directly with emoji prefixes
    return f"🎯 {epic_name}", f"⚙️ {feature_name}" if feature_name != epic_name else feature_name


def create_story_content(story, epic_name, feature_name):
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
    
    content = f"""# 📝 {story_name}

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** {epic_name}  
**Feature:** {feature_name}

**User:** {user_str}  
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
    
    # Get stories from story_groups
    for group in epic.get('story_groups', []):
        for story in group.get('stories', []):
            users = story.get('users', [])
            story_type = story.get('story_type', 'user')
            
            # Filter: Only Bot/system stories, exclude Human/AI Chat
            is_bot_story = (
                any('Bot' in str(u) for u in users) or 
                story_type == 'system' or
                not users
            )
            is_human_ai = any(u in ['Human', 'AI Chat'] for u in users)
            
            if is_bot_story and not is_human_ai:
                # Store the actual names from the graph
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
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get existing story files to avoid duplicates
        existing_stories = set()
        if output_dir.exists():
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md') and file.startswith('📝'):
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
            story_dir = output_dir / epic_folder / feature_folder
            story_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file
            story_file = story_dir / f"📝 {story_name}.md"
            
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
        formatted.append(f"### Scenario: {name}\n\n**Steps:**\n```gherkin\n{steps}\n```")
    
    return "\n\n".join(formatted)


def build_folder_path_from_graph(epic_name, feature_name, story_graph_data):
    """
    Build folder path dynamically from story graph structure.
    Traverses the graph to find the actual epic and feature/sub_epic names.
    """
    # Find the epic in the graph
    for epic in story_graph_data.get('epics', []):
        if epic['name'] == epic_name:
            epic_folder = f"🎯 {epic_name}"
            
            # If feature_name matches the epic itself, it's a top-level feature
            if feature_name == epic_name:
                return epic_folder, epic_name
            
            # Otherwise, find the feature/sub_epic in the epic's sub_epics
            def find_feature_in_sub_epics(sub_epics, target_name):
                for sub_epic in sub_epics:
                    if sub_epic['name'] == target_name:
                        return f"⚙️ {target_name}"
                    # Recursively check nested sub_epics
                    if 'sub_epics' in sub_epic:
                        result = find_feature_in_sub_epics(sub_epic['sub_epics'], target_name)
                        if result:
                            return result
                return None
            
            feature_folder = find_feature_in_sub_epics(epic.get('sub_epics', []), feature_name)
            if feature_folder:
                return epic_folder, feature_folder
            
            # If not found in sub_epics, use the feature_name as-is
            return epic_folder, feature_name
    
    # Fallback: use names directly with emoji prefixes
    return f"🎯 {epic_name}", f"⚙️ {feature_name}" if feature_name != epic_name else feature_name


def create_story_content(story, epic_name, feature_name):
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
    
    content = f"""# 📝 {story_name}

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** {epic_name}  
**Feature:** {feature_name}

**User:** {user_str}  
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
    
    # Get stories from story_groups
    for group in epic.get('story_groups', []):
        for story in group.get('stories', []):
            users = story.get('users', [])
            story_type = story.get('story_type', 'user')
            
            # Filter: Only Bot/system stories, exclude Human/AI Chat
            is_bot_story = (
                any('Bot' in str(u) for u in users) or 
                story_type == 'system' or
                not users
            )
            is_human_ai = any(u in ['Human', 'AI Chat'] for u in users)
            
            if is_bot_story and not is_human_ai:
                # Store the actual names from the graph
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
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get existing story files to avoid duplicates
        existing_stories = set()
        if output_dir.exists():
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md') and file.startswith('📝'):
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
            story_dir = output_dir / epic_folder / feature_folder
            story_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file
            story_file = story_dir / f"📝 {story_name}.md"
            
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