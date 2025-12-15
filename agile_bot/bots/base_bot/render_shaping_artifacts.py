#!/usr/bin/env python3
"""
Render all shaping artifacts from story-graph.json.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

def format_actor(users):
    """Format users array into actor string"""
    if not users:
        return ""
    if len(users) == 1:
        return f"{users[0]} --> "
    return f"{', '.join(users)} --> "

def find_story_by_name_in_all(stories_list, name, visited=None):
    """Find a story by name across all stories (avoiding circular references)"""
    if visited is None:
        visited = set()
    
    if name in visited:
        return None
    
    visited.add(name)
    
    for story in stories_list:
        if story.get('name') == name:
            return story
    
    return None

def render_story(story, indent_level, is_first_in_sequence=False, all_stories_in_context=None, rendered_stories=None):
    """Render a single story"""
    if rendered_stories is None:
        rendered_stories = set()
    
    story_name = story.get('name', '')
    if story_name in rendered_stories:
        return []
    
    rendered_stories.add(story_name)
    
    indent = "    " * indent_level
    connector = story.get('connector')
    if connector is None or connector == 'and':
        connector_str = "" if is_first_in_sequence else ""
    else:
        connector_str = "" if is_first_in_sequence else f"{connector} "
    
    actor = format_actor(story.get('users', []))
    
    lines = [f"{indent}{connector_str}(S) {actor}{story_name}"]
    
    # Handle acceptance criteria
    acceptance_criteria = story.get('acceptance_criteria', [])
    for ac in acceptance_criteria:
        ac_actor = format_actor(story.get('users', []))
        lines.append(f"{indent}    (AC) {ac_actor}{ac}")
    
    # Handle workflow_children (nested stories)
    workflow_children_names = story.get('workflow_children', [])
    if workflow_children_names and all_stories_in_context:
        nested_stories = []
        for child_name in workflow_children_names:
            child_story = find_story_by_name_in_all(all_stories_in_context, child_name)
            if child_story and child_story.get('name') not in rendered_stories:
                nested_stories.append(child_story)
        
        if nested_stories:
            for j, nested in enumerate(nested_stories):
                nested_lines = render_story(nested, indent_level + 1, j == 0, all_stories_in_context, rendered_stories)
                lines.extend(nested_lines)
    
    return lines

def render_story_group(story_group, indent_level, all_stories_in_epic, rendered_stories=None):
    """Render a story group"""
    if rendered_stories is None:
        rendered_stories = set()
    
    lines = []
    stories = story_group.get('stories', [])
    group_connector = story_group.get('connector')
    
    for i, story in enumerate(stories):
        is_first = (i == 0)
        story_lines = render_story(story, indent_level, is_first, all_stories_in_epic, rendered_stories)
        lines.extend(story_lines)
    
    return lines

def collect_all_stories_in_epic(epic):
    """Collect all stories from an epic and its sub-epics recursively"""
    all_stories = []
    
    # Add stories from story groups
    for story_group in epic.get('story_groups', []):
        all_stories.extend(story_group.get('stories', []))
    
    # Add direct stories (if any)
    all_stories.extend(epic.get('stories', []))
    
    # Add stories from sub-epics
    for sub_epic in epic.get('sub_epics', []):
        all_stories.extend(collect_all_stories_in_epic(sub_epic))
    
    return all_stories

def render_sub_epic(sub_epic, indent_level, is_first_in_sequence=False, all_stories_in_epic=None):
    """Render a sub-epic"""
    indent = "    " * indent_level
    connector = sub_epic.get('connector')
    if connector is None or connector == 'and':
        connector_str = "" if is_first_in_sequence else ""
    else:
        connector_str = "" if is_first_in_sequence else f"{connector} "
    
    lines = [f"{indent}{connector_str}(E) {sub_epic.get('name', '')}"]
    
    # Render nested sub-epics
    nested_sub_epics = sub_epic.get('sub_epics', [])
    if nested_sub_epics:
        for i, nested in enumerate(nested_sub_epics):
            nested_lines = render_sub_epic(nested, indent_level + 1, i == 0, all_stories_in_epic)
            lines.extend(nested_lines)
    
    # Render story groups
    story_groups = sub_epic.get('story_groups', [])
    if story_groups:
        for i, story_group in enumerate(story_groups):
            group_connector = story_group.get('connector')
            if group_connector and i > 0:
                lines.append(f"{indent}{group_connector}")
            story_lines = render_story_group(story_group, indent_level + 1, all_stories_in_epic or [], set())
            lines.extend(story_lines)
    
    # Render direct stories (if any)
    stories = sub_epic.get('stories', [])
    if stories:
        story_lines = render_story_group({'stories': stories, 'connector': None}, indent_level + 1, all_stories_in_epic or stories, set())
        lines.extend(story_lines)
    
    return lines

def render_epic(epic, indent_level, is_first_in_sequence=False):
    """Render an epic"""
    indent = "    " * indent_level
    connector = epic.get('connector')
    if connector is None or connector == 'and':
        connector_str = "" if is_first_in_sequence else ""
    else:
        connector_str = "" if is_first_in_sequence else f"{connector} "
    
    lines = [f"{indent}{connector_str}(E) {epic.get('name', '')}"]
    
    # Collect all stories in this epic for workflow_children lookup
    all_stories_in_epic = collect_all_stories_in_epic(epic)
    
    # Render sub-epics
    sub_epics = epic.get('sub_epics', [])
    if sub_epics:
        for i, sub_epic in enumerate(sub_epics):
            sub_epic_lines = render_sub_epic(sub_epic, indent_level + 1, i == 0, all_stories_in_epic)
            lines.extend(sub_epic_lines)
    
    # Render story groups
    story_groups = epic.get('story_groups', [])
    if story_groups:
        for i, story_group in enumerate(story_groups):
            group_connector = story_group.get('connector')
            if group_connector and i > 0:
                lines.append(f"{indent}{group_connector}")
            story_lines = render_story_group(story_group, indent_level + 1, all_stories_in_epic or [], set())
            lines.extend(story_lines)
    
    # Render direct stories (if any)
    stories = epic.get('stories', [])
    if stories:
        story_lines = render_story_group({'stories': stories, 'connector': None}, indent_level + 1, all_stories_in_epic or stories, set())
        lines.extend(story_lines)
    
    return lines

def render_story_map(story_graph):
    """Render entire story graph to story map format"""
    lines = []
    
    epics = story_graph.get('epics', [])
    for i, epic in enumerate(epics):
        epic_lines = render_epic(epic, 0, i == 0)
        lines.extend(epic_lines)
    
    return "\n".join(lines)

def extract_domain_concepts(story_graph):
    """Extract all domain concepts from story graph"""
    domain_concepts = {}
    
    for epic in story_graph.get('epics', []):
        for concept in epic.get('domain_concepts', []):
            concept_name = concept.get('name', '')
            if concept_name and concept_name not in domain_concepts:
                domain_concepts[concept_name] = concept
        
        for sub_epic in epic.get('sub_epics', []):
            for concept in sub_epic.get('domain_concepts', []):
                concept_name = concept.get('name', '')
                if concept_name and concept_name not in domain_concepts:
                    domain_concepts[concept_name] = concept
    
    return domain_concepts

def render_domain_model_description(domain_concepts, solution_name="Base Bot"):
    """Render domain model description"""
    solution_name_slug = solution_name.lower().replace(' ', '-')
    
    descriptions = []
    for concept_name, concept in domain_concepts.items():
        descriptions.append(f"### {concept_name}")
        descriptions.append("")
        
        responsibilities = concept.get('responsibilities', [])
        if responsibilities:
            descriptions.append("**Responsibilities:**")
            for resp in responsibilities:
                resp_name = resp.get('name', '')
                collaborators = resp.get('collaborators', [])
                if collaborators:
                    collab_str = ", ".join(collaborators)
                    descriptions.append(f"- {resp_name} (collaborates with: {collab_str})")
                else:
                    descriptions.append(f"- {resp_name}")
            descriptions.append("")
    
    domain_model_text = "\n".join(descriptions)
    
    template = f"""# Domain Model Description: {solution_name}

**File Name**: `{solution_name_slug}-domain-model-description.md`
**Location**: `docs/stories/{solution_name_slug}-domain-model-description.md`

## Solution Purpose
This document describes the domain model for {solution_name}, capturing the key concepts, their responsibilities, and relationships.

---

## Domain Model Descriptions

{domain_model_text}

---

## Source Material

- Source: story-graph.json
- Generated from domain_concepts in epics and sub-epics
"""
    return template

def render_domain_model_diagram(domain_concepts, solution_name="Base Bot"):
    """Render domain model diagram as Mermaid"""
    solution_name_slug = solution_name.lower().replace(' ', '-')
    
    mermaid_lines = ["classDiagram"]
    
    for concept_name, concept in domain_concepts.items():
        responsibilities = concept.get('responsibilities', [])
        mermaid_lines.append(f"    class {concept_name} {{")
        for resp in responsibilities[:5]:  # Limit to 5 responsibilities for readability
            resp_name = resp.get('name', '').replace(' ', '_')
            mermaid_lines.append(f"        +{resp_name}()")
        mermaid_lines.append("    }")
        mermaid_lines.append("")
        
        # Add relationships based on collaborators
        for resp in responsibilities:
            collaborators = resp.get('collaborators', [])
            for collab in collaborators:
                if collab in domain_concepts:
                    mermaid_lines.append(f"    {concept_name} --> {collab} : uses")
    
    mermaid_diagram = "\n".join(mermaid_lines)
    
    template = f"""# Domain Model Diagram: {solution_name}

**File Name**: `{solution_name_slug}-domain-model-diagram.md`
**Location**: `docs/stories/{solution_name_slug}-domain-model-diagram.md`

## Solution Purpose
This document provides a visual representation of the domain model for {solution_name} using Mermaid diagrams.

---

## Domain Model Diagram

```mermaid
{mermaid_diagram}
```

**Diagram Notes:**
- Domain concepts are shown as classes with their responsibilities
- Responsibilities are listed as methods in the class (format: +{{responsibility}}())
- Relationships show dependencies and associations between concepts
- Associations show usage and collaboration (-->)

---

## Source Material

- Source: story-graph.json
- Generated from domain_concepts in epics and sub-epics
"""
    return template

def main():
    """Main rendering function"""
    workspace_root = Path(__file__).parent
    story_graph_path = workspace_root / 'docs' / 'stories' / 'story-graph.json'
    output_dir = workspace_root / 'docs' / 'stories'
    
    if not story_graph_path.exists():
        print(f"Error: story-graph.json not found at {story_graph_path}")
        sys.exit(1)
    
    print(f"Loading {story_graph_path}...")
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Extract solution name from story graph or use default
    solution_name = "Base Bot"  # Default
    if 'epics' in story_graph and story_graph['epics']:
        # Try to infer from first epic
        first_epic = story_graph['epics'][0]
        if 'name' in first_epic:
            solution_name = first_epic['name'].split()[0] + " Bot"  # e.g., "Build Agile Bots" -> "Build Bot"
    
    solution_name_slug = solution_name.lower().replace(' ', '-')
    
    # 1. Render story map markdown
    print("Rendering story-map.md...")
    story_map_md = render_story_map(story_graph)
    story_map_md_path = output_dir / 'story-map.md'
    with open(story_map_md_path, 'w', encoding='utf-8') as f:
        f.write(story_map_md)
    print(f"  Saved to {story_map_md_path}")
    
    # 2. Render story map text
    print("Rendering story-map.txt...")
    story_map_txt = render_story_map(story_graph)
    story_map_txt_path = output_dir / 'story-map.txt'
    with open(story_map_txt_path, 'w', encoding='utf-8') as f:
        f.write(story_map_txt)
    print(f"  Saved to {story_map_txt_path}")
    
    # 3. Extract and render domain model description
    print("Rendering domain model description...")
    domain_concepts = extract_domain_concepts(story_graph)
    domain_description = render_domain_model_description(domain_concepts, solution_name)
    domain_desc_path = output_dir / f'{solution_name_slug}-domain-model-description.md'
    with open(domain_desc_path, 'w', encoding='utf-8') as f:
        f.write(domain_description)
    print(f"  Saved to {domain_desc_path}")
    
    # 4. Render domain model diagram
    print("Rendering domain model diagram...")
    domain_diagram = render_domain_model_diagram(domain_concepts, solution_name)
    domain_diag_path = output_dir / f'{solution_name_slug}-domain-model-diagram.md'
    with open(domain_diag_path, 'w', encoding='utf-8') as f:
        f.write(domain_diagram)
    print(f"  Saved to {domain_diag_path}")
    
    print("\nDone! All shaping artifacts rendered.")

if __name__ == "__main__":
    main()





