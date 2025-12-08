"""Create story markdown files in map directory from story-graph.json."""
import json
from pathlib import Path


def format_acceptance_criteria(ac_list):
    """Format acceptance criteria list into markdown"""
    if not ac_list:
        return ""
    
    formatted = []
    for ac in ac_list:
        ac_text = ac.strip()
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


def create_story_content(story, epic_name, feature_name):
    """Create markdown content for a story"""
    story_name = story['name']
    users = story.get('users', [])
    user_str = ', '.join(users) if users else 'System'
    story_type = story.get('story_type', 'user')
    sequential_order = story.get('sequential_order', 1)
    
    ac_list = story.get('acceptance_criteria', [])
    ac_formatted = format_acceptance_criteria(ac_list)
    
    scenarios_list = story.get('scenarios', [])
    scenarios_formatted = format_scenarios(scenarios_list)
    
    # Default description
    description = story.get('description', f'{story_name} functionality.')
    
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


def create_story_files():
    """Create story markdown files in map directory structure."""
    story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
    map_base_path = Path('agile_bot/bots/base_bot/docs/stories/map')
    
    # Read story graph
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    epics = data.get('epics', [])
    print(f"Found {len(epics)} epics\n")
    
    created_count = 0
    
    # Iterate through epics and sub_epics
    for epic in epics:
        epic_name = epic.get('name', '')
        if not epic_name:
            continue
        
        epic_folder = map_base_path / f"🎯 {epic_name}"
        epic_folder.mkdir(parents=True, exist_ok=True)
        
        # Get sub_epics (features)
        sub_epics = epic.get('sub_epics', []) or epic.get('features', [])
        
        for sub_epic in sub_epics:
            sub_epic_name = sub_epic.get('name', '')
            if not sub_epic_name:
                continue
            
            sub_epic_folder = epic_folder / f"⚙️ {sub_epic_name}"
            sub_epic_folder.mkdir(parents=True, exist_ok=True)
            
            # Get stories from story_groups
            story_groups = sub_epic.get('story_groups', [])
            for story_group in story_groups:
                stories = story_group.get('stories', [])
                
                for story in stories:
                    story_name = story.get('name', '')
                    if not story_name:
                        continue
                    
                    # Create story markdown file
                    story_file = sub_epic_folder / f"📝 {story_name}.md"
                    content = create_story_content(story, epic_name, sub_epic_name)
                    
                    with open(story_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Created: {epic_name} / {sub_epic_name} / {story_name}.md")
                    created_count += 1
    
    print(f"\n✅ Created {created_count} story files")
    print(f"📁 Base path: {map_base_path.resolve()}")


if __name__ == '__main__':
    create_story_files()
