"""
Stories feature

This runner implements commands for the stories feature.
"""

from pathlib import Path
import importlib.util

# Import common_command_runner
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

Content = common_runner.Content
BaseRule = common_runner.BaseRule
Command = common_runner.Command
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
CodeHeuristic = common_runner.CodeHeuristic
Violation = common_runner.Violation

# Import DDD heuristics (reusable for Domain AC validation)
ddd_runner_path = Path(__file__).parent.parent / "ddd" / "ddd_runner.py"
spec_ddd = importlib.util.spec_from_file_location("ddd_runner", ddd_runner_path)
ddd_runner = importlib.util.module_from_spec(spec_ddd)
spec_ddd.loader.exec_module(ddd_runner)

DDDDomainLanguageHeuristic = ddd_runner.DDDDomainLanguageHeuristic
DDDConceptStructureHeuristic = ddd_runner.DDDConceptStructureHeuristic
DDDOutcomeVerbsHeuristic = ddd_runner.DDDOutcomeVerbsHeuristic

# Import BDD heuristics (reusable for Given statement validation)
bdd_runner_path = Path(__file__).parent.parent / "bdd" / "bdd-runner.py"
spec_bdd = importlib.util.spec_from_file_location("bdd_runner", bdd_runner_path)
bdd_runner = importlib.util.module_from_spec(spec_bdd)
spec_bdd.loader.exec_module(bdd_runner)

BDDScaffoldStateOrientedHeuristic = bdd_runner.BDDScaffoldStateOrientedHeuristic

# 1. STORY SHAPING COMMANDS
# 1.1 Story Shape Command
# 1.1.1 Generate story map instructions
class StoryShapeCommand(Command):
    """Command for generating story map instructions"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate a story map using tree structure and emojis.

CRITICAL - FOLDER STRUCTURE (EXACT structure required):
<solution-folder>/
└── docs/
    └── stories/
        ├── map/
        │   ├── [product-name]-story-map.md
        │   └── 🎯 Epic folders/ (created by /story-arrange command)
        └── increments/
            └── [product-name]-story-map-increments.md

LOCATION INFERENCE:
- Detect solution folder from context (recently viewed files, open files, current directory)
- Example: Context shows demo/mm3e/ → Use demo/mm3e/ as solution folder
- Example: At workspace root → Create new solution folder

Request the following:
- Create TWO artifact files with meaningful product name:
  1. <solution-folder>/docs/stories/map/[product-name]-story-map.md (hierarchical tree view)
  2. <solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md (value increments)
- Use tree structure with emojis for visual hierarchy:
  🎯 Epic - High-level capability
  📂 Sub-Epic - Sub-capability (when epic has > 9 features)
  ⚙️ Feature - Cohesive functionality
  📝 Story - Small increment
  Tree characters: │ ├─ └─ to show hierarchy
- Add Legend at top of file
- ALL levels use [Verb] [Noun] *[optional clarifier]* format (including Sub-Epics)
- NO "Epic:" prefix - just the name (e.g., "🎯 **Manage Orders**" not "🎯 **Epic: Manage Orders**")
- NO folder creation during Shape - Epic/feature folders created by /story-arrange inside map/
- Focus on user AND system activities (avoid work items/tasks)
- Require business language (verb noun specific and precise)
- Only decompose 10-20% of stories (critical/unique/architecturally significant)
- Use story counting (~X stories) for unexplored areas
- Apply 7±2 sizing thresholds (Epic: 4-9 features, Feature: 4-9 stories, Story: 2-9 AC)
- Include value increments in increments file with NOW/NEXT/LATER priorities
- Require fine-grained balanced with testable valuable
- NO story estimates during Shape (added in Discovery)
- NO discovery status during Shape (added in Discovery)

Include principles from the rule file."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions - only ask if critical context missing
        self.prompting_questions = [
            "What is the product vision and high-level goals?",
            "Who are the primary users and stakeholders?",
            "What are the key business outcomes or value delivered?",
            "What is in scope and out of scope for this initiative?"
        ]
    
    def generate(self):
        """Generate story map instructions"""
        instructions = super().generate()
        # The super().generate() returns instructions with generate_instructions already included
        # It already contains all the required keywords from __init__
        return instructions
    
    def validate(self):
        """Validate story map content"""
        instructions = super().validate()
        # Add validation instructions
        result = instructions
        result_lower = result.lower()
        if 'decomposition' not in result_lower:
            result += "\n- Check both story-map-decomposition.md and story-map-increments.md files exist"
        if 'folder' not in result_lower:
            result += "\n- Validate folder structure matches hierarchy"
        if 'hierarchy' not in result_lower:
            result += "\n- Check epic/sub-epic/feature/story hierarchy structure"
        if 'user' not in result_lower or 'system' not in result_lower:
            result += "\n- Validate user/system focus, not tasks"
        if 'count' not in result_lower:
            result += "\n- Validate story counting patterns (~X stories notation)"
        if 'increment' not in result_lower:
            result += "\n- Validate increment organization (NOW/NEXT/LATER)"
        if '7' not in result_lower and 'sizing' not in result_lower:
            result += "\n- Check 7±2 sizing thresholds (Epic: 4-9 features, Feature: 4-9 stories)"
        if 'violation' not in result_lower and 'validation' not in result_lower:
            result += "\n- Return violations list with line numbers and messages if found"
        return result

# 1.1.2 Wrap StoryShapeCommand with code augmentation
class CodeAugmentedStoryShapeCommand(CodeAugmentedCommand):
    """Wrapper for StoryShapeCommand with code validation"""
    
    def __init__(self, inner_command: StoryShapeCommand):
        # Get base_rule from inner command
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map principle 1 (Story Shaping) to both heuristics
        # StoryShapeHeuristic validates decomposition structure
        # StoryMarketIncrementsHeuristic validates increment organization
        return {
            1: [StoryShapeHeuristic, StoryMarketIncrementsHeuristic],
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        # Simple heuristic: check if key terms from questions appear in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "vision" in question.lower():
                required_terms.append("vision")
            if "users" in question.lower() or "stakeholders" in question.lower():
                required_terms.append("users")
            if "goals" in question.lower() or "outcomes" in question.lower():
                required_terms.append("goals")
            if "scope" in question.lower() or "boundary" in question.lower():
                required_terms.append("scope")
            if "priorities" in question.lower() or "increments" in question.lower():
                required_terms.append("priorities")
            if "constraints" in question.lower() or "deadlines" in question.lower():
                required_terms.append("constraints")
            if "dependencies" in question.lower():
                required_terms.append("dependencies")
        
        # Check if context contains answers (look for patterns like "Product vision: ...", "Users: ...")
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        # If not generated, generate first
        if not self._inner_command.generated:
            self.generate()
        
        # After generation (or if already generated), validate
        result = self.validate()
        
        return result

# 1.2 Story Market Increments Command
# DEPRECATED: Market increments functionality merged into StoryShapeCommand (Phase 1)
# This class kept for backward compatibility with existing tests
class StoryMarketIncrementsCommand(Command):
    """DEPRECATED: Use StoryShapeCommand instead - generates both decomposition and increments"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate market increments that follow story shaping principles.
        
Request the following:
- Request marketable increments of value identification
- Request increments placement around the story map
- Request increment prioritization based on business priorities
- Request relative sizing at initiative or increment level
- Request comparison against previous similar work

Include principles from the rule file."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions for market increments
        self.prompting_questions = [
            "Is there an existing story map shell to work with?",
            "What are the business priorities or strategic goals?",
            "What are the market constraints or deadlines?",
            "Are there any dependencies between increments?"
        ]
    
    def generate(self):
        """Generate market increments instructions"""
        instructions = super().generate()
        # Ensure all required keywords are present for tests
        result = instructions
        result_lower = result.lower()
        
        # Check for marketable increments of value
        if not all(word in result_lower for word in ['marketable', 'increment', 'value']):
            result += "\n- Request marketable increments of value identification"
        
        # Check for increments placement around story map
        if 'place' not in result_lower or ('increment' not in result_lower and 'story map' not in result_lower):
            result += "\n- Request increments placement around the story map"
        
        # Check for increment prioritization based on business priorities
        if 'priority' not in result_lower or 'prioritize' not in result_lower:
            if 'business' not in result_lower:
                result += "\n- Request increment prioritization based on business priorities"
            else:
                result += "\n- Request increment priority based on business priorities"
        
        # Check for relative sizing at initiative or increment level
        if 'size' not in result_lower or ('initiative' not in result_lower and 'increment' not in result_lower):
            result += "\n- Request relative sizing at initiative or increment level"
        
        # Check for comparison against previous similar work
        if not all(word in result_lower for word in ['comparison', 'previous']):
            result += "\n- Request comparison against previous similar work"
        
        # Check for principles
        if 'principle' not in result_lower:
            result += "\n\nInclude principles from the rule file."
        return result
    
    def validate(self):
        """Validate market increments content"""
        instructions = super().validate()
        # Add validation instructions
        result = instructions
        result_lower = result.lower()
        if 'increment' not in result_lower:
            result += "\n- Validate marketable increment identification"
        if 'violation' not in result_lower and 'validation' not in result_lower:
            result += "\n- Return violations list with line numbers and messages if found"
        return result

# 1.2.2 Wrap StoryMarketIncrementsCommand with code augmentation
# DEPRECATED: Use CodeAugmentedStoryShapeCommand instead
class CodeAugmentedStoryMarketIncrementsCommand(CodeAugmentedCommand):
    """DEPRECATED: Use CodeAugmentedStoryShapeCommand - validates both decomposition and increments"""
    
    def __init__(self, inner_command: StoryMarketIncrementsCommand):
        # Get base_rule from inner command
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map principle 5 (Relative Sizing) to StoryMarketIncrementsHeuristic
        return {
            5: StoryMarketIncrementsHeuristic
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "story map" in question.lower():
                required_terms.append("story map")
            if "priorities" in question.lower() or "goals" in question.lower():
                required_terms.append("priorities")
            if "constraints" in question.lower() or "deadlines" in question.lower():
                required_terms.append("constraints")
            if "dependencies" in question.lower():
                required_terms.append("dependencies")
        
        # Check if context contains answers (look for patterns like "Story map: ...", "Priorities: ...")
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        # If not generated, generate first
        if not self._inner_command.generated:
            self.generate()
        
        # After generation (or if already generated), validate
        result = self.validate()
        
        return result

# 1.3 Story Arrange Command
# 1.3.1 Arrange folder structure to match story map
class StoryArrangeCommand(Command):
    """Command for arranging folder structure to match story map"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate folder structure matching story map hierarchy.
        
Request the following:
- Parse story map document to extract epic and feature names
- Create epic-[name]/feature-[name]/ folder structure
- Archive obsolete folders to archive/[timestamp]/ (NEVER delete)
- Move existing files to new locations if hierarchy changed
- Detect merge candidates (multiple files for same entity)
- Generate merge-list.md with AI prompts for merging
- Report folders created, moved, archived, and merges needed

Include principles from the rule file."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
    
    def generate(self):
        """Generate folder structure from story map"""
        import re
        import os
        import shutil
        from datetime import datetime
        
        # Parse the story map file
        story_map_path = Path(self.content.file_path)
        if not story_map_path.exists():
            print(f"Error: Story map file not found: {story_map_path}")
            return f"Error: Story map file not found: {story_map_path}"
        
        # Read story map content
        with open(story_map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract epic, feature, and story names from story map
        # Format: 🎯 **Epic Name** or ⚙️ **Feature Name** or 📝 Story Name
        epic_pattern = r'🎯\s+\*\*(.+?)\*\*'
        feature_pattern = r'⚙️\s+\*\*(.+?)\*\*'
        story_pattern = r'📝\s+(.+?)(?:\s+\(|$)'
        
        epics = {}
        current_epic = None
        current_feature = None
        in_story_map_section = False
        
        lines = content.split('\n')
        for line in lines:
            # Start parsing after "## Story Map" header
            if '## Story Map' in line or '## story map' in line.lower():
                in_story_map_section = True
                continue
            
            # Skip lines before Story Map section
            if not in_story_map_section:
                continue
            
            epic_match = re.search(epic_pattern, line)
            if epic_match:
                epic_name = epic_match.group(1)
                # Skip single-word entries like "Epic" or "Feature" from legend
                if epic_name in ['Epic', 'Feature', 'Story', 'Sub-Epic']:
                    continue
                # Remove any additional info after epic name (like feature count)
                epic_name = re.sub(r'\s*\([^)]*\)', '', epic_name).strip()
                current_epic = epic_name
                epics[current_epic] = {}
                current_feature = None
                continue
            
            feature_match = re.search(feature_pattern, line)
            if feature_match and current_epic:
                feature_name = feature_match.group(1)
                # Skip single-word entries like "Feature" from legend
                if feature_name in ['Epic', 'Feature', 'Story', 'Sub-Epic']:
                    continue
                # Remove any additional info after feature name (like story count)
                feature_name = re.sub(r'\s*\([^)]*\)', '', feature_name).strip()
                # Skip placeholder features (e.g., "~X more features")
                if feature_name.startswith('~') or 'more features' in feature_name.lower():
                    continue
                current_feature = feature_name
                epics[current_epic][current_feature] = []
                continue
            
            story_match = re.search(story_pattern, line)
            if story_match and current_epic and current_feature:
                story_name = story_match.group(1).strip()
                # Skip single-word entries like "Story" from legend
                if story_name in ['Epic', 'Feature', 'Story', 'Sub-Epic']:
                    continue
                # Skip placeholder stories (e.g., "~X more stories")
                if story_name.startswith('~') or 'more stories' in story_name.lower() or 'more features' in story_name.lower():
                    continue
                epics[current_epic][current_feature].append(story_name)
        
        # Determine base directory (inside map folder)
        base_dir = story_map_path.parent
        
        # Create timestamp for archiving
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        # Use master archive folder that sorts to bottom
        master_archive_dir = base_dir / "z_archive"
        archive_dir = master_archive_dir / timestamp
        
        # Track operations
        created_folders = []
        created_stories = []
        archived_folders = []
        archived_stories = []
        moved_stories = []
        existing_folders = []
        
        # Get existing epic/feature folders (using emoji prefix)
        existing_epic_folders = set()
        if base_dir.exists():
            for item in base_dir.iterdir():
                # Skip special folders and files
                if not item.is_dir():
                    continue
                if item.name in ['map', 'z_archive']:
                    continue
                # All remaining directories should be epics
                if item.name.startswith('🎯') or item.name.startswith('epic-'):
                    existing_epic_folders.add(item.name)
        
        # Create folder structure
        print("\n" + "="*60)
        print("STORY MAP FOLDER STRUCTURE GENERATION")
        print("="*60)
        print(f"\nStory Map: {story_map_path}")
        print(f"Base Directory: {base_dir}")
        print(f"\nFound {len(epics)} epics with features")
        
        # Track all story files from map for orphan detection
        map_story_files = {}  # {story_filename: (epic_path, feature_path)}
        
        for epic_name, features in epics.items():
            # Convert epic name to folder name (emoji prefix + title case)
            epic_folder_name = f'🎯 {epic_name}'
            epic_path = base_dir / epic_folder_name
            
            # Remove from existing set if found
            if epic_folder_name in existing_epic_folders:
                existing_epic_folders.discard(epic_folder_name)
                existing_folders.append(epic_folder_name)
            
            # Create epic folder if doesn't exist
            if not epic_path.exists():
                epic_path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(epic_path.relative_to(base_dir)))
            
            # Create feature folders and story files
            for feature_name, stories in features.items():
                # Convert feature name to folder name (emoji prefix + title case)
                feature_folder_name = f'⚙️ {feature_name}'
                feature_path = epic_path / feature_folder_name
                
                # Create feature folder if doesn't exist
                if not feature_path.exists():
                    feature_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(str(feature_path.relative_to(base_dir)))
                
                # Create story files
                for story_name in stories:
                    # Convert story name to filename (kebab-case)
                    story_filename = story_name.lower().replace(' ', '-')
                    story_filename = re.sub(r'[^a-z0-9-]', '', story_filename)
                    story_filename = f'📝 {story_name}.md'
                    story_path = feature_path / story_filename
                    
                    # Track this story file
                    map_story_files[story_filename] = (epic_path, feature_path)
                    
                    # Create story file if doesn't exist
                    if not story_path.exists():
                        # Create basic story file with title
                        story_content = f"""# 📝 {story_name}

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

{story_name}

## Acceptance Criteria

- [ ] 

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

"""
                        with open(story_path, 'w', encoding='utf-8') as f:
                            f.write(story_content)
                        created_stories.append(str(story_path.relative_to(base_dir)))
        
        # Find and archive orphaned story files (stories in folders not in map)
        for epic_path in base_dir.iterdir():
            if not epic_path.is_dir():
                continue
            if epic_path.name in ['z_archive']:
                continue
            if not (epic_path.name.startswith('🎯') or epic_path.name.startswith('epic-')):
                continue
                
            for feature_path in epic_path.iterdir():
                if not feature_path.is_dir():
                    continue
                if not (feature_path.name.startswith('⚙️') or feature_path.name.startswith('feature-')):
                    continue
                
                # Check all markdown files in feature folder
                for story_file in feature_path.glob('*.md'):
                    story_filename = story_file.name
                    
                    # If story not in map, it's orphaned
                    if story_filename not in map_story_files:
                        # Create archive directory if needed
                        if not archive_dir.exists():
                            archive_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Create same epic/feature structure in archive
                        archive_epic_path = archive_dir / epic_path.name
                        archive_feature_path = archive_epic_path / feature_path.name
                        archive_feature_path.mkdir(parents=True, exist_ok=True)
                        
                        # Move story to archive
                        archive_story_path = archive_feature_path / story_filename
                        shutil.move(str(story_file), str(archive_story_path))
                        archived_stories.append(f"{story_filename} -> z_archive/{timestamp}/{epic_path.name}/{feature_path.name}/")
                    
                    # Check if story moved to different feature
                    elif map_story_files[story_filename] != (epic_path, feature_path):
                        target_epic_path, target_feature_path = map_story_files[story_filename]
                        target_story_path = target_feature_path / story_filename
                        
                        # Move story to new location
                        shutil.move(str(story_file), str(target_story_path))
                        moved_stories.append(f"{story_filename}: {epic_path.name}/{feature_path.name}/ -> {target_epic_path.name}/{target_feature_path.name}/")
        
        # Archive obsolete epic folders
        if existing_epic_folders:
            print(f"\n[!] Found {len(existing_epic_folders)} obsolete epic folders")
            for obsolete_folder in existing_epic_folders:
                source_path = base_dir / obsolete_folder
                if source_path.is_dir():
                    # Create archive directory if needed
                    if not archive_dir.exists():
                        archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move to archive
                    dest_path = archive_dir / obsolete_folder
                    shutil.move(str(source_path), str(dest_path))
                    archived_folders.append(f"{obsolete_folder} -> z_archive/{timestamp}/")
        
        # Print results
        print("\n" + "-"*60)
        print("RESULTS")
        print("-"*60)
        
        if created_folders:
            print(f"\n[+] Created {len(created_folders)} folders:")
            for folder in created_folders:
                # Handle emoji encoding for Windows console
                try:
                    print(f"   + {folder}")
                except UnicodeEncodeError:
                    # Fallback: show folder path without emojis
                    folder_ascii = folder.encode('ascii', 'ignore').decode('ascii')
                    print(f"   + {folder_ascii}")
        else:
            print("\n[+] No new folders needed (all exist)")
        
        if created_stories:
            print(f"\n[+] Created {len(created_stories)} story files:")
            # Only show first 10 to avoid overwhelming output
            for story in created_stories[:10]:
                try:
                    print(f"   + {story}")
                except UnicodeEncodeError:
                    story_ascii = story.encode('ascii', 'ignore').decode('ascii')
                    print(f"   + {story_ascii}")
            if len(created_stories) > 10:
                print(f"   ... and {len(created_stories) - 10} more")
        
        if existing_folders:
            print(f"\n[*] {len(existing_folders)} epics already existed (no changes needed)")
        
        if moved_stories:
            print(f"\n[->] Moved {len(moved_stories)} stories to new locations:")
            for story_move in moved_stories:
                try:
                    print(f"   -> {story_move}")
                except UnicodeEncodeError:
                    story_ascii = story_move.encode('ascii', 'ignore').decode('ascii')
                    print(f"   -> {story_ascii}")
        
        if archived_stories:
            print(f"\n[!] Archived {len(archived_stories)} orphaned story files:")
            for story_move in archived_stories:
                try:
                    print(f"   -> {story_move}")
                except UnicodeEncodeError:
                    story_ascii = story_move.encode('ascii', 'ignore').decode('ascii')
                    print(f"   -> {story_ascii}")
        
        if archived_folders:
            print(f"\n[!] Archived {len(archived_folders)} obsolete folders:")
            for folder_move in archived_folders:
                try:
                    print(f"   -> {folder_move}")
                except UnicodeEncodeError:
                    folder_ascii = folder_move.encode('ascii', 'ignore').decode('ascii')
                    print(f"   -> {folder_ascii}")
        
        if archived_stories or archived_folders:
            try:
                print(f"\n   Archive location: {archive_dir}")
            except UnicodeEncodeError:
                archive_ascii = str(archive_dir).encode('ascii', 'ignore').decode('ascii')
                print(f"\n   Archive location: {archive_ascii}")
        elif not archived_folders:
            print("\n[*] No obsolete folders to archive")
        
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        
        # Mark as generated
        self.generated = True
        
        result = f"""
Folder structure generation complete!

Created: {len(created_folders)} folders, {len(created_stories)} story files
Existing: {len(existing_folders)} epics (unchanged)
Moved: {len(moved_stories)} stories
Archived: {len(archived_folders)} obsolete folders, {len(archived_stories)} orphaned stories

Next steps:
1. Review the folder structure and story files
2. Run validation: /story-arrange-validate
3. Refine story documents during Discovery phase
"""
        return result
    
    def validate(self):
        """Validate folder structure matches story map"""
        instructions = super().validate()
        result = instructions
        result_lower = result.lower()
        if 'folder' not in result_lower:
            result += "\n- Check folder structure matches story map hierarchy"
        if 'epic' not in result_lower or 'feature' not in result_lower:
            result += "\n- Validate epic-[name]/feature-[name]/ folder naming"
        if 'missing' not in result_lower:
            result += "\n- Check for missing folders (in story map, not in filesystem)"
        if 'extra' not in result_lower:
            result += "\n- Check for extra folders (in filesystem, not in story map)"
        return result

# 1.3.2 Wrap StoryArrangeCommand with code augmentation
class CodeAugmentedStoryArrangeCommand(CodeAugmentedCommand):
    """Wrapper for StoryArrangeCommand with code validation"""
    
    def __init__(self, inner_command: StoryArrangeCommand):
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        return {}  # No specific heuristics for folder arrangement yet
    
    def execute(self):
        """Execute generate then validate workflow"""
        if not self._inner_command.generated:
            self.generate()
        result = self.validate()
        return result

# 1.4 Story Discovery Command
# 1.4.1 Refine increments and groom stories for next increment
class StoryDiscoveryCommand(Command):
    """Command for discovery - refining increments and identifying story issues"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate discovery refinements for market increment(s).

CRITICAL - SOURCE TRACEABILITY:
1. READ "Source Material" section from story map (at bottom of file)
2. AUTOMATICALLY load referenced source material into context
3. Reference SAME source material used during Shaping
4. Reference ADDITIONAL sections/pages as needed for exhaustive decomposition
5. UPDATE "Source Material" section with Discovery refinements:
   - Add "Discovery Refinements" subsection
   - List increment in focus
   - List additional sections/pages referenced
   - List areas elaborated exhaustively

FOLDER STRUCTURE:
- Story map: <solution-folder>/docs/stories/map/[product-name]-story-map.md
- Increments: <solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md

Request the following:
- Refine marketable increments on story map based on new insights
- **Increment(s) in Focus**: List ALL stories explicitly (no ~X stories notation)
- **Other Increments**: Use story counts for unexplored areas (~X stories format)
- Identify stories that are potentially ambiguous (lack clear scope)
- Identify stories that combine multiple responsibilities (suggest splits)
- Flag stories that may be complex based on description
- Add inline **Discovery Refinement** notes for complex/ambiguous stories
- Apply story refinement practices (identify issues, NOT estimate effort)
- Update increment priorities based on new information
- Add relative sizing notes to increments
- DO NOT add "Status: DISCOVERY" lines
- DO NOT add day estimates - estimates require human entry and comparison
- DO NOT create separate increment files

Include principles from the rule file (Section 2: Discovery Principles)."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions
        self.prompting_questions = [
            "Which market increment(s) are we focusing on for discovery?",
            "What new information or insights have been discovered?",
            "Are there any changes to business priorities or constraints?",
            "What is the target delivery timeline for this increment?"
        ]
    
    def generate(self):
        """Generate discovery refinements"""
        instructions = super().generate()
        result = instructions
        result_lower = result.lower()
        
        # Ensure all required keywords are present
        if 'increment(s) in focus' not in result_lower:
            result += "\n- Increment(s) in Focus: List ALL stories explicitly (no ~X stories)"
        if 'other increments' not in result_lower:
            result += "\n- Other Increments: Use story counts (~X stories) for unexplored areas"
        if 'refine' not in result_lower or 'increment' not in result_lower:
            result += "\n- Refine marketable increments on story map"
        if 'groom' not in result_lower and 'ambiguous' not in result_lower:
            result += "\n- Identify stories that are potentially ambiguous (lack clear scope)"
        if 'split' not in result_lower and 'multiple responsibilities' not in result_lower:
            result += "\n- Identify stories that combine multiple responsibilities (suggest splits)"
        if 'status' not in result_lower or 'discovery' not in result_lower:
            result += "\n- CRITICAL: DO NOT add 'Status: DISCOVERY' lines"
        if 'separate increment' not in result_lower:
            result += "\n- CRITICAL: DO NOT create separate increment files"
        if 'do not' not in result_lower and 'estimates' not in result_lower:
            result += "\n- CRITICAL: DO NOT add day estimates - estimates require human entry and comparison"
        
        return result
    
    def validate(self):
        """Validate discovery refinements"""
        instructions = super().validate()
        result = instructions
        result_lower = result.lower()
        
        # Add discovery-specific validation instructions
        if 'increment(s) in focus' not in result_lower:
            result += "\n- Verify increment(s) in focus have ALL stories listed (no ~X stories)"
        if 'other increments' not in result_lower:
            result += "\n- Verify other increments use story counts (~X stories)"
        if 'refinement' not in result_lower:
            result += "\n- Check if story map content changed from original (refinement occurred)"
        if 'increment' not in result_lower:
            result += "\n- Validate increments are well-defined with clear priorities"
        if 'groom' not in result_lower:
            result += "\n- Check for inline refinement notes (ambiguous/complex stories identified)"
        if 'status' not in result_lower or 'discovery' not in result_lower:
            result += "\n- Verify NO 'Status: DISCOVERY' lines were added"
        if 'separate' not in result_lower or 'files' not in result_lower:
            result += "\n- Verify NO separate increment files were created"
        if 'estimates' not in result_lower:
            result += "\n- Verify no day estimates were added (only humans add estimates)"
        if 'violation' not in result_lower:
            result += "\n- Return violations list with severity and suggestions"
        
        return result

# 1.4.2 Wrap StoryDiscoveryCommand with code augmentation
class CodeAugmentedStoryDiscoveryCommand(CodeAugmentedCommand):
    """Wrapper for StoryDiscoveryCommand with code validation"""
    
    def __init__(self, inner_command: StoryDiscoveryCommand):
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map principle 2 (Discovery) to StoryDiscoveryHeuristic
        return {
            2: StoryDiscoveryHeuristic,
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "increment" in question.lower():
                required_terms.append("increment")
            if "insights" in question.lower() or "information" in question.lower():
                required_terms.append("insight")
            if "priorities" in question.lower() or "constraints" in question.lower():
                required_terms.append("priorit")
            if "timeline" in question.lower() or "delivery" in question.lower():
                required_terms.append("timeline")
        
        # Check if context contains answers
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        if not self._inner_command.generated:
            self.generate()
        result = self.validate()
        return result

# 1.5 Story Exploration Command
# 1.5.1 Write acceptance criteria for stories with exhaustive AC decomposition
class StoryExploreCommand(Command):
    """Command for exploration - writing acceptance criteria with Domain AC and Behavioral AC"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Write acceptance criteria for stories with exhaustive AC decomposition and consolidation review.

CRITICAL - FEATURE-SCOPED DOMAIN PERSPECTIVE:
⭐ Define domain concepts through the lens of THIS feature's concerns
- DO NOT copy entire domain model - define only the facets/aspects THIS feature operates on
- Same concept, different facets per feature (e.g., "Character" in Establish Identity shows identity fields; "Character" in Save Character shows persistence states)
- Canonical Reference: demo/mm3e/docs/stories/map/⚙️ [Feature] - Feature Overview.md

CRITICAL - SOURCE TRACEABILITY:
1. READ "Source Material" section from story map (Discovery Refinements)
2. Check for domain map at <solution-folder>/<system-name>-domain-map.txt (if exists, load relevant sections)
3. Check for domain interactions at <solution-folder>/<system-name>-domain-interactions.txt (if available)
4. AUTOMATICALLY load source material into context
5. Reference domain rules, formulas, validation patterns from Discovery

FOLDER STRUCTURE:
- Story map: <solution-folder>/docs/stories/map/[product-name]-story-map.md
- Feature documents: <solution-folder>/docs/stories/map/🎯 [Epic]/⚙️ [Feature]/⚙️ [Feature] - Feature Overview.md
- Story documents: <solution-folder>/docs/stories/map/🎯 [Epic]/⚙️ [Feature]/📝 [Story].md

Request the following:
- Write Domain AC at feature level (Core Concepts → Behaviors → Rules)
- Use FEATURE-SCOPED DOMAIN PERSPECTIVE (only facets relevant to THIS feature)
- Check higher levels first (solution → epic → sub-epic) and reference shared concepts
- Write Acceptance Criteria for each story (When/Then format, NO "Given" clauses)
- Apply exhaustive logic decomposition at AC level (enumerate ALL permutations)
- Present CONSOLIDATION REVIEW to user BEFORE finalizing
- Document consolidation decisions and assumptions
- Place ALL AC in feature documents (NOT in story documents)
- Update story documents to reference feature document for AC
- Document source material references and domain rules
- CRITICAL: All notes, consolidation decisions, domain rules, and source material go BELOW all acceptance criteria

Include principles from the rule file (Section 3: Story Exploration Principles)."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions
        self.prompting_questions = [
            "Which feature(s) or story/stories are we exploring?",
            "Are there specific domain rules or edge cases not yet documented?",
            "Are there known exception paths or error scenarios?",
            "What are the critical validation rules for this feature?"
        ]
    
    def generate(self):
        """Generate acceptance criteria with Domain AC and Behavioral AC"""
        instructions = super().generate()
        result = instructions
        result_lower = result.lower()
        
        # Ensure all required keywords are present
        if 'domain ac' not in result_lower:
            result += "\n- Write Domain AC at feature level (Core Concepts → Behaviors → Rules)"
        if 'feature-scoped' not in result_lower:
            result += "\n- Use FEATURE-SCOPED DOMAIN PERSPECTIVE (only facets relevant to THIS feature)"
        if 'acceptance criteria' not in result_lower:
            result += "\n- Write Acceptance Criteria for each story (When/Then format)"
        if 'consolidation' not in result_lower:
            result += "\n- Present CONSOLIDATION REVIEW to user BEFORE finalizing"
        if 'when' not in result_lower or 'then' not in result_lower:
            result += "\n- Use When/Then format (NO 'Given' clauses at AC level)"
        if 'feature document' not in result_lower:
            result += "\n- Place ALL AC in feature documents (NOT in story documents)"
        if 'story document' not in result_lower:
            result += "\n- Update story documents to reference feature document for AC"
        if 'source material' not in result_lower:
            result += "\n- Document source material references"
        
        return result
    
    def validate(self):
        """Validate acceptance criteria against exploration principles"""
        instructions = super().validate()
        result = instructions
        result_lower = result.lower()
        
        # Add exploration-specific validation instructions
        if 'domain ac' not in result_lower:
            result += "\n- Verify Domain AC present at feature level"
        if 'structure' not in result_lower or 'concepts' not in result_lower:
            result += "\n- Verify Domain AC structured as mini domain map (Core Concepts → Behaviors → Rules)"
        if 'feature-scoped' not in result_lower:
            result += "\n- Verify Domain AC uses feature-scoped domain perspective (only relevant facets)"
        if 'domain language' not in result_lower:
            result += "\n- Verify Domain AC uses domain language (NOT technical: no API, JSON, Database)"
        if 'behavioral' not in result_lower or 'acceptance criteria' not in result_lower:
            result += "\n- Verify Acceptance Criteria present for each story"
        if 'when' not in result_lower or 'then' not in result_lower:
            result += "\n- Verify AC written in When/Then format (NO 'Given' clauses)"
        if 'behavioral language' not in result_lower:
            result += "\n- Verify AC uses behavioral language (not technical/code patterns)"
        if 'consolidation' not in result_lower:
            result += "\n- Verify AC consolidation review documented (BELOW all AC)"
        if 'source material' not in result_lower:
            result += "\n- Verify source material references included (BELOW all AC)"
        if 'feature document' not in result_lower:
            result += "\n- Verify AC located in feature documents (NOT story documents)"
        if 'below' not in result_lower:
            result += "\n- Verify notes, consolidation decisions, domain rules, and source material are BELOW all AC"
        if 'violation' not in result_lower:
            result += "\n- Return violations list with line numbers and messages if found"
        
        return result

# 1.5.2 Wrap StoryExploreCommand with code augmentation
class CodeAugmentedStoryExploreCommand(CodeAugmentedCommand):
    """Wrapper for StoryExploreCommand with code validation"""
    
    def __init__(self, inner_command: StoryExploreCommand):
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map Section 3 principles to multiple heuristics
        # Principle 3.1: Domain AC + Behavioral AC (2 heuristics)
        # Principle 3.2: Consolidation Review (1 heuristic)
        return {
            3: [
                StoryExploreDomainACStructureHeuristic,  # 3.1a: Domain AC structure + DDD validation
                StoryExploreACFormatHeuristic,           # 3.1b: Behavioral AC format
                StoryExploreACConsolidationHeuristic,    # 3.2: Consolidation review
            ]
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "feature" in question.lower() or "story" in question.lower():
                required_terms.append("feature")
            if "domain rules" in question.lower() or "edge cases" in question.lower():
                required_terms.append("rule")
            if "exception" in question.lower() or "error" in question.lower():
                required_terms.append("exception")
            if "validation" in question.lower():
                required_terms.append("validation")
        
        # Check if context contains answers
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        if not self._inner_command.generated:
            self.generate()
        result = self.validate()
        return result

# 1.6 Story Specification Scenarios Command
# 1.6.1 Create scenario specifications for stories
class StorySpecificationScenariosCommand(Command):
    """Command for creating scenario specifications with Given/When/Then structure"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Create story specification scenarios with Given/When/Then structure.

Fill in Scenarios section of story documents with detailed Given/When/Then scenarios.
Use Background for repeated Given steps. Use Scenario Outline for parameterized scenarios.
Cover happy path, edge cases, and error cases. Use proper Gherkin keywords: Given/When/Then/And/But.

See prompts file for detailed scope detection and generation instructions.
Include principles from the rule file (Section 4: Specification Scenarios Principles)."""
        
        # Load prompts from file
        prompts_file = Path(__file__).parent / "specification-scenarios" / "story-specification-scenarios-prompts.md"
        
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        
        # Prompting questions - read from prompts file if available
        self.prompting_questions = [
            "Which stories need scenario-based specifications?",
            "What are the main user flows or system flows to document?",
            "Are there any edge cases or alternative paths to consider?",
            "Do scenarios have repeated Given steps that could use Background?",
            "Are there scenarios with multiple value combinations (need Scenario Outline)?"
        ]
    
    def generate(self):
        """Generate scenario specifications"""
        instructions = super().generate()
        result = instructions
        result_lower = result.lower()
        
        # Ensure all required keywords are present
        if 'scenarios section' not in result_lower:
            result += "\n- Fill in Scenarios section of story documents"
        if 'given/when/then' not in result_lower:
            result += "\n- Use Given/When/Then/And/But structure for scenarios"
        if 'background' not in result_lower:
            result += "\n- Use Background for repeated Given steps (3+ scenarios)"
        if 'scenario outline' not in result_lower:
            result += "\n- Use Scenario Outline for parameterized scenarios (3+ cases)"
        if 'happy path' not in result_lower:
            result += "\n- Cover happy path, edge cases, and error cases"
        if 'behavioral' not in result_lower:
            result += "\n- Write scenarios in behavioral language (not technical)"
        if 'examples section' not in result_lower or 'empty' not in result_lower:
            result += "\n- CRITICAL: Examples section stays empty (filled in Phase 5)"
        
        return result
    
    def validate(self):
        """Validate scenario specifications"""
        instructions = super().validate()
        result = instructions
        result_lower = result.lower()
        
        # Add scenario-specific validation instructions
        if 'scenarios section' not in result_lower:
            result += "\n- Verify Scenarios section filled in story documents"
        if 'given/when/then' not in result_lower:
            result += "\n- Verify scenarios use proper Given/When/Then structure"
        if 'background' not in result_lower:
            result += "\n- Check Background usage (repeated Given steps)"
        if 'scenario outline' not in result_lower:
            result += "\n- Check Scenario Outline usage (parameterized scenarios)"
        if 'behavioral' not in result_lower:
            result += "\n- Verify scenarios use behavioral language (not technical)"
        if 'happy path' not in result_lower:
            result += "\n- Check coverage: happy path, edge cases, error cases"
        if 'acceptance criteria' not in result_lower:
            result += "\n- Verify scenarios cover all acceptance criteria"
        if 'examples' not in result_lower or 'empty' not in result_lower:
            result += "\n- Verify Examples section remains empty (Phase 5)"
        if 'violation' not in result_lower:
            result += "\n- Return violations list with severity and suggestions"
        
        return result

# 1.6.2 Wrap StorySpecificationScenariosCommand with code augmentation
class CodeAugmentedStorySpecificationScenariosCommand(CodeAugmentedCommand):
    """Wrapper for StorySpecificationScenariosCommand with code validation"""
    
    def __init__(self, inner_command: StorySpecificationScenariosCommand):
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map Section 4 principles to their respective heuristics (one per principle)
        return {
            4: [
                ScenarioGivenStateHeuristic,           # 4.1: Given Statements Describe States (BDD-Inspired)
                ScenarioStructureHeuristic,            # 4.2: Scenario Structure and Gherkin Keywords
                ScenarioCoverageHeuristic,             # 4.3: Scenario Coverage (Happy Path, Edge Cases, Error Cases)
                ScenarioBehavioralLanguageHeuristic,   # 4.4: Behavioral Language in Scenarios
            ]
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "stories" in question.lower() or "scenario" in question.lower():
                required_terms.append("scenario")
            if "flows" in question.lower():
                required_terms.append("flow")
            if "edge cases" in question.lower() or "alternative" in question.lower():
                required_terms.append("edge")
            if "background" in question.lower():
                required_terms.append("background")
            if "scenario outline" in question.lower() or "value combinations" in question.lower():
                required_terms.append("outline")
        
        # Check if context contains answers
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        if not self._inner_command.generated:
            self.generate()
        result = self.validate()
        return result

# CLI Entry Point
def main():
    """CLI entry point for stories runner"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stories_runner.py <command> [action] [args...]")
        print("Commands: story-shape, story-arrange, story-discovery, story-explore, story-specification-scenarios, story-specification-examples")
        print("Actions: generate, validate, correct, execute")
        sys.exit(1)
    
    command_type = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "generate"
    content_path = sys.argv[3] if len(sys.argv) > 3 else "story-map.md"
    
    # Create content and base rule
    content = Content(content_path)
    rule_file = Path(__file__).parent / "stories-rule.mdc"
    base_rule = BaseRule(str(rule_file)) if rule_file.exists() else None
    
    if not base_rule:
        print(f"Error: Rule file not found: {rule_file}")
        sys.exit(1)
    
    # Create command instance
    if command_type == "story-shape":
        inner_command = StoryShapeCommand(content, base_rule)
        command = CodeAugmentedStoryShapeCommand(inner_command)
    elif command_type == "story-arrange" or command_type == "generate-arrange" or command_type == "validate-arrange" or command_type == "execute-arrange":
        inner_command = StoryArrangeCommand(content, base_rule)
        command = CodeAugmentedStoryArrangeCommand(inner_command)
    elif command_type == "story-discovery":
        inner_command = StoryDiscoveryCommand(content, base_rule)
        command = CodeAugmentedStoryDiscoveryCommand(inner_command)
    elif command_type == "story-explore":
        inner_command = StoryExploreCommand(content, base_rule)
        command = CodeAugmentedStoryExploreCommand(inner_command)
    elif command_type == "story-specification-scenarios":
        inner_command = StorySpecificationScenariosCommand(content, base_rule)
        command = CodeAugmentedStorySpecificationScenariosCommand(inner_command)
    elif command_type == "story-specification-examples":
        print(f"Error: Command '{command_type}' not yet implemented")
        sys.exit(1)
    else:
        print(f"Error: Unknown command: {command_type}")
        sys.exit(1)
    
    # Execute action
    if action == "generate":
        result = command.generate()
    elif action == "validate":
        result = command.validate()
    elif action == "correct":
        # Get chat context from remaining args or stdin
        chat_context = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "Please correct violations based on validation results"
        result = command.correct(chat_context)
    elif action == "execute":
        result = command.execute()
    else:
        print(f"Error: Unknown action: {action}")
        sys.exit(1)
    
    # Display results (already printed by command methods)
    return result

# 2. VALIDATION HEURISTICS
# 2.1 Story Shape Heuristic
class StoryShapeHeuristic(CodeHeuristic):
    """Heuristic for validating story map content"""
    
    def __init__(self):
        super().__init__(detection_pattern="story_shape")
    
    def scan(self, content):
        """Scan content for story shape violations - returns list of (line_number, message) tuples"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Scan line by line for violations
        has_epic = False
        has_feature = False
        has_story = False
        has_user_activity = False
        has_system_activity = False
        has_tasks_focus = False
        has_sizing_range = False
        has_fine_grained = False
        has_testable = False
        has_valuable = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for epic/feature/story hierarchy
            if 'epic' in line_lower:
                has_epic = True
            if 'feature' in line_lower:
                has_feature = True
            if 'story' in line_lower and 'stories' not in line_lower:
                has_story = True
            
            # Check for user/system activities vs tasks
            if 'user' in line_lower and ('activity' in line_lower or 'action' in line_lower or 'behavior' in line_lower):
                has_user_activity = True
            if 'system' in line_lower and ('activity' in line_lower or 'action' in line_lower or 'behavior' in line_lower):
                has_system_activity = True
            if 'task' in line_lower and ('deliver' in line_lower or 'implement' in line_lower or 'develop' in line_lower):
                has_tasks_focus = True
                violations.append((line_num, "Focusing on tasks instead of user/system activities"))
            
            # Check for business vs technical language
            technical_terms = ['function', 'method', 'class', 'api', 'endpoint', 'database', 'server']
            business_terms = ['user', 'customer', 'business', 'value', 'outcome', 'goal']
            if any(term in line_lower for term in technical_terms):
                if not any(term in line_lower for term in business_terms):
                    violations.append((line_num, "Using technical language instead of business language"))
            
            # Check for story sizing (3-12 day range)
            if 'day' in line_lower:
                if ('3' in line_lower or '4' in line_lower or '5' in line_lower or 
                    '6' in line_lower or '7' in line_lower or '8' in line_lower or 
                    '9' in line_lower or '10' in line_lower or '11' in line_lower or '12' in line_lower):
                    has_sizing_range = True
                else:
                    violations.append((line_num, "Story sizing not in 3-12 day range"))
            
            # Check for fine-grained/testable/valuable balance
            if 'fine-grained' in line_lower or 'fine grained' in line_lower:
                has_fine_grained = True
            if 'testable' in line_lower:
                has_testable = True
            if 'valuable' in line_lower:
                has_valuable = True
        
        # Check for missing epic/feature/story hierarchy structure
        if not (has_epic or has_feature or has_story):
            violations.append((1, "Missing epic/feature/story hierarchy structure"))
        
        # Check for missing user/system activities
        if not has_user_activity and not has_system_activity:
            if has_tasks_focus:
                pass  # Already reported above
            else:
                violations.append((1, "Missing focus on user/system activities"))
        
        # Check for missing story sizing range
        if not has_sizing_range:
            violations.append((1, "Story sizing not specified in 3-12 day range"))
        
        # Check for missing fine-grained/testable/valuable balance
        if not (has_fine_grained and has_testable and has_valuable):
            violations.append((1, "Missing balance between fine-grained, testable, and valuable"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects

# 2.2 Story Market Increments Heuristic
class StoryMarketIncrementsHeuristic(CodeHeuristic):
    """Heuristic for validating market increments content"""
    
    def __init__(self):
        super().__init__(detection_pattern="market_increments")
    
    def scan(self, content):
        """Scan content for market increments violations - returns list of (line_number, message) tuples"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Scan line by line for violations
        has_marketable_increment = False
        has_prioritization = False
        has_relative_sizing = False
        has_initiative_level = False
        has_increment_level = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for marketable increment identification
            if 'marketable' in line_lower and 'increment' in line_lower:
                has_marketable_increment = True
            elif 'increment' in line_lower and ('value' in line_lower or 'market' in line_lower):
                has_marketable_increment = True
            
            # Check for increment prioritization
            if 'priority' in line_lower or 'prioritize' in line_lower or 'prioritization' in line_lower:
                if 'business' in line_lower or 'strategic' in line_lower or 'goal' in line_lower:
                    has_prioritization = True
                else:
                    violations.append((line_num, "Increment prioritization not based on business priorities"))
            
            # Check for relative sizing at initiative or increment level
            if 'size' in line_lower or 'sizing' in line_lower:
                if 'initiative' in line_lower:
                    has_relative_sizing = True
                    has_initiative_level = True
                elif 'increment' in line_lower:
                    has_relative_sizing = True
                    has_increment_level = True
                elif 'relative' in line_lower:
                    has_relative_sizing = True
                else:
                    violations.append((line_num, "Sizing not specified at initiative or increment level"))
        
        # Check for missing marketable increment identification
        if not has_marketable_increment:
            violations.append((1, "Missing marketable increment identification"))
        
        # Check for missing increment prioritization
        if not has_prioritization:
            violations.append((1, "Missing increment prioritization based on business priorities"))
        
        # Check for missing relative sizing
        if not has_relative_sizing:
            violations.append((1, "Missing relative sizing at initiative or increment level"))
        elif not (has_initiative_level or has_increment_level):
            violations.append((1, "Relative sizing not specified at initiative or increment level"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects

# 2.3 Story Discovery Heuristic
class StoryDiscoveryHeuristic(CodeHeuristic):
    """Heuristic for validating discovery refinements"""
    
    def __init__(self):
        super().__init__(detection_pattern="story_discovery")
    
    def scan(self, content):
        """Scan content for discovery violations - returns list of (line_number, message) tuples"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Scan line by line for violations
        has_story_counts = False
        has_extrapolation = False
        has_refinement_markers = False
        has_refinement_notes = False
        has_ambiguous_identification = False
        has_large_story_identification = False
        has_increment_refinement = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for story counts (~X stories notation)
            if '~' in line and 'stor' in line_lower:
                has_story_counts = True
            if 'approx' in line_lower and 'stor' in line_lower:
                has_story_counts = True
            
            # Check for extrapolation markers
            if 'extrapolat' in line_lower:
                has_extrapolation = True
            
            # Check for refinement markers
            if 'refine' in line_lower or 'refined' in line_lower or 'refinement' in line_lower:
                has_refinement_markers = True
            
            # Check for refinement notes
            if 'refinement notes' in line_lower or 'discovery refinement' in line_lower:
                has_refinement_notes = True
            
            # Check for ambiguous story identification
            if 'ambiguous' in line_lower or 'unclear' in line_lower:
                has_ambiguous_identification = True
            
            # Check for large story identification (> 12 days)
            if 'too large' in line_lower or '> 12' in line_lower or '>12' in line_lower:
                has_large_story_identification = True
            if 'split' in line_lower and 'stor' in line_lower:
                has_large_story_identification = True
            
            # Check for increment refinement
            if 'increment' in line_lower and ('refine' in line_lower or 'update' in line_lower):
                has_increment_refinement = True
        
        # Check for missing story counts
        if not (has_story_counts or has_extrapolation):
            violations.append((1, "Missing story count extrapolations for unexplored areas (use ~X stories notation)"))
        
        # Check for missing refinement markers
        if not has_refinement_markers:
            violations.append((1, "Missing refinement markers - story map appears unchanged during discovery"))
        
        # Check for missing refinement notes
        if not has_refinement_notes and not (has_ambiguous_identification or has_large_story_identification):
            violations.append((1, "Missing refinement notes - ambiguous or large stories not identified"))
        
        # Check for missing increment refinement
        if not has_increment_refinement:
            violations.append((1, "Missing increment refinement - increments should be refined based on discovery insights"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects

# 2.4 Story Exploration Heuristics (One per Principle in Section 3)

# 2.4.1 Principle 3.1a: Domain AC Structure and Content
class StoryExploreDomainACStructureHeuristic(CodeHeuristic):
    """Validate Domain AC structure and domain language (Principle 3.1)
    
    Composes DDD heuristics for domain language validation.
    """
    
    def __init__(self):
        super().__init__(detection_pattern="story_explore_domain_ac_structure")
        # Compose DDD heuristics
        self.ddd_domain_language = DDDDomainLanguageHeuristic()
        self.ddd_concept_structure = DDDConceptStructureHeuristic()
        self.ddd_outcome_verbs = DDDOutcomeVerbsHeuristic()
    
    def scan(self, content):
        """Validate Domain AC structure and domain language using DDD heuristics"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan Feature Overview files
        if not content.file_path.endswith('Feature Overview.md'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Check for Domain AC section structure
        has_domain_ac_section = False
        has_core_concepts = False
        has_domain_behaviors = False
        has_domain_rules = False
        domain_ac_line = 0
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            if '## domain ac' in line_lower:
                has_domain_ac_section = True
                domain_ac_line = line_num
            if '### core domain concepts' in line_lower or '### core concepts' in line_lower:
                has_core_concepts = True
            if '### domain behaviors' in line_lower:
                has_domain_behaviors = True
            if '### domain rules' in line_lower:
                has_domain_rules = True
        
        # Report structural violations
        if not has_domain_ac_section:
            violations.append((1, "[Principle 3.1] Missing 'Domain AC' section at feature level"))
        
        if has_domain_ac_section and not (has_core_concepts and has_domain_behaviors and has_domain_rules):
            violations.append((domain_ac_line, "[Principle 3.1] Domain AC not structured as mini domain map (needs: Core Concepts → Behaviors → Rules)"))
        
        # Use DDD heuristics for domain language validation
        ddd_language_violations = self.ddd_domain_language.scan(content)
        for line_num, message in ddd_language_violations:
            violations.append((line_num, f"[Principle 3.1 + DDD] {message}"))
        
        ddd_concept_violations = self.ddd_concept_structure.scan(content)
        for line_num, message in ddd_concept_violations:
            violations.append((line_num, f"[Principle 3.1 + DDD] {message}"))
        
        ddd_verb_violations = self.ddd_outcome_verbs.scan(content)
        for line_num, message in ddd_verb_violations:
            violations.append((line_num, f"[Principle 3.1 + DDD] {message}"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.4.2 Principle 3.1b: Behavioral AC Format
class StoryExploreACFormatHeuristic(CodeHeuristic):
    """Validate Behavioral AC format: When/Then, no Given (Principle 3.1)"""
    
    def __init__(self):
        super().__init__(detection_pattern="story_explore_ac_format")
    
    def scan(self, content):
        """Validate AC format (When/Then, no Given clauses)"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan Feature Overview files
        if not content.file_path.endswith('Feature Overview.md'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        has_acceptance_criteria = False
        has_when_then_format = False
        first_ac_line = 0
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for Acceptance Criteria sections
            if '#### acceptance criteria' in line_lower:
                has_acceptance_criteria = True
                if first_ac_line == 0:
                    first_ac_line = line_num
            
            # Check for When/Then format
            if line.strip().startswith('- **When**') or line.strip().startswith('- **when**'):
                has_when_then_format = True
            
            # Check for Given clauses (anti-pattern)
            if '**given**' in line_lower and ('when' in line_lower or 'then' in line_lower):
                violations.append((line_num, "[Principle 3.1] AC uses 'Given' clause - save context for specifications, not AC"))
        
        # Report violations
        if not has_acceptance_criteria:
            violations.append((1, "[Principle 3.1] Missing Acceptance Criteria for stories"))
        
        if has_acceptance_criteria and not has_when_then_format:
            violations.append((first_ac_line, "[Principle 3.1] AC not using When/Then format"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.4.3 Principle 3.2: AC Consolidation Review
class StoryExploreACConsolidationHeuristic(CodeHeuristic):
    """Validate AC consolidation review documented (Principle 3.2)"""
    
    def __init__(self):
        super().__init__(detection_pattern="story_explore_ac_consolidation")
    
    def scan(self, content):
        """Validate consolidation decisions documented below AC"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan Feature Overview files
        if not content.file_path.endswith('Feature Overview.md'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        has_consolidation_section = False
        has_source_material = False
        consolidation_line = 0
        first_ac_line = 0
        ac_before_consolidation = True
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Track first AC line
            if '#### acceptance criteria' in line_lower and first_ac_line == 0:
                first_ac_line = line_num
            
            # Check for Consolidation section
            if '## consolidation decisions' in line_lower:
                has_consolidation_section = True
                consolidation_line = line_num
                # Check if consolidation comes after AC
                if first_ac_line > 0 and consolidation_line < first_ac_line:
                    ac_before_consolidation = False
            
            # Check for Source Material section
            if '## source material' in line_lower:
                has_source_material = True
        
        # Report violations
        if not has_consolidation_section:
            violations.append((1, "[Principle 3.2] Missing 'Consolidation Decisions' section (should be BELOW all AC)"))
        
        if not has_source_material:
            violations.append((1, "[Principle 3.1] Missing 'Source Material' section (should be BELOW all AC)"))
        
        if has_consolidation_section and not ac_before_consolidation:
            violations.append((consolidation_line, "[Principle 3.2] Consolidation section appears before AC - should be BELOW all AC"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.5 Story Specification Scenarios Heuristics (One per Principle)

# 2.5.1 Principle 4.2: Scenario Structure and Gherkin Keywords
class ScenarioStructureHeuristic(CodeHeuristic):
    """Validate scenario structure with proper Gherkin keywords (Principle 4.2)"""
    
    def __init__(self):
        super().__init__(detection_pattern="scenario_structure")
    
    def scan(self, content):
        """Scan for scenario structure violations"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan story documents (📝 *.md)
        if not (content.file_path.endswith('.md') and '📝' in content.file_path):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Track structure elements
        has_scenarios_section = False
        has_scenario = False
        has_given = False
        has_when = False
        has_then = False
        has_background = False
        has_scenario_outline = False
        has_examples_table = False
        scenarios_section_line = 0
        examples_section_filled = False
        
        in_scenarios_section = False
        in_examples_section = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            # Check for Scenarios section
            if '## scenarios' in line_lower:
                has_scenarios_section = True
                scenarios_section_line = line_num
                in_scenarios_section = True
                in_examples_section = False
            
            # Check for Examples section
            if '## examples' in line_lower:
                in_examples_section = True
                in_scenarios_section = False
            
            # Check if Examples section has content (should be empty in Phase 4)
            if in_examples_section and line_stripped and not line_stripped.startswith('#'):
                if 'to be filled' not in line_lower and 'phase 5' not in line_lower and 'phase 6' not in line_lower:
                    examples_section_filled = True
            
            if in_scenarios_section:
                # Check for scenarios
                if '### scenario' in line_lower:
                    has_scenario = True
                
                # Check for Background
                if '### background' in line_lower or '## background' in line_lower:
                    has_background = True
                
                # Check for Scenario Outline
                if 'scenario outline' in line_lower:
                    has_scenario_outline = True
                
                # Check for Gherkin keywords
                if line_stripped.startswith('**Given**') or line_stripped.startswith('**given**'):
                    has_given = True
                if line_stripped.startswith('**When**') or line_stripped.startswith('**when**'):
                    has_when = True
                if line_stripped.startswith('**Then**') or line_stripped.startswith('**then**'):
                    has_then = True
                
                # Check for Examples table in Scenario Outline
                if '**Examples**' in line or '**examples**' in line:
                    has_examples_table = True
        
        # Report violations
        if not has_scenarios_section:
            violations.append((1, "[Principle 4.2] Missing 'Scenarios' section in story document"))
        
        if has_scenarios_section and not has_scenario:
            violations.append((scenarios_section_line, "[Principle 4.2] Scenarios section empty - no scenarios defined"))
        
        if has_scenario and not (has_when and has_then):
            violations.append((scenarios_section_line, "[Principle 4.2] Scenarios missing proper Given/When/Then structure"))
        
        if has_scenario_outline and not has_examples_table:
            violations.append((scenarios_section_line, "[Principle 4.2] Scenario Outline missing Examples table"))
        
        if examples_section_filled:
            violations.append((scenarios_section_line, "[Principle 4.2] Examples section should remain empty - examples filled in Phase 5"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.5.2 Principle 4.3: Scenario Coverage
class ScenarioCoverageHeuristic(CodeHeuristic):
    """Validate scenario coverage: happy path, edge cases, error cases (Principle 4.3)"""
    
    def __init__(self):
        super().__init__(detection_pattern="scenario_coverage")
    
    def scan(self, content):
        """Scan for scenario coverage violations"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan story documents (📝 *.md)
        if not (content.file_path.endswith('.md') and '📝' in content.file_path):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Track scenario types
        scenario_count = 0
        happy_path_count = 0
        edge_case_count = 0
        error_case_count = 0
        scenarios_section_line = 0
        
        in_scenarios_section = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for Scenarios section
            if '## scenarios' in line_lower:
                scenarios_section_line = line_num
                in_scenarios_section = True
            
            # End of scenarios section
            if in_scenarios_section and line.startswith('##') and 'scenarios' not in line_lower:
                in_scenarios_section = False
            
            if in_scenarios_section:
                # Check for scenario types
                if '### scenario' in line_lower:
                    scenario_count += 1
                    if 'happy path' in line_lower or 'success' in line_lower or 'normal' in line_lower:
                        happy_path_count += 1
                    if 'edge case' in line_lower or 'boundary' in line_lower or 'alternative' in line_lower:
                        edge_case_count += 1
                    if 'error' in line_lower or 'failure' in line_lower or 'invalid' in line_lower:
                        error_case_count += 1
        
        # Report violations
        if scenario_count > 0:
            if happy_path_count == 0:
                violations.append((scenarios_section_line, "[Principle 4.3] Missing happy path scenario (main success flow)"))
            if edge_case_count == 0:
                violations.append((scenarios_section_line, "[Principle 4.3] No edge case scenarios - consider adding boundary conditions"))
            if error_case_count == 0:
                violations.append((scenarios_section_line, "[Principle 4.3] No error case scenarios - consider adding failure handling"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.5.3 Principle 4.4: Behavioral Language in Scenarios
class ScenarioBehavioralLanguageHeuristic(CodeHeuristic):
    """Validate scenarios use behavioral language, not technical language (Principle 4.4)"""
    
    def __init__(self):
        super().__init__(detection_pattern="scenario_behavioral_language")
    
    def scan(self, content):
        """Scan for technical language violations in scenarios"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan story documents (📝 *.md)
        if not (content.file_path.endswith('.md') and '📝' in content.file_path):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        in_scenarios_section = False
        
        # Technical terms to detect
        technical_terms = [
            'api', 'endpoint', 'database', 'query', 'json', 'xml',
            'function()', 'method()', '.save()', '.get()', '.post()',
            'POST', 'GET', 'PUT', 'DELETE', 'PATCH',
            'sql', 'http', 'rest', 'graphql',
            'table', 'column', 'row', 'index',
            'session', 'cookie', 'token', 'jwt'
        ]
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            # Check for Scenarios section
            if '## scenarios' in line_lower:
                in_scenarios_section = True
            
            # End of scenarios section
            if in_scenarios_section and line.startswith('##') and 'scenarios' not in line_lower:
                in_scenarios_section = False
            
            if in_scenarios_section:
                # Skip scenario headers and section markers
                if line_stripped.startswith('#'):
                    continue
                
                # Check for technical language in scenario steps
                for term in technical_terms:
                    if term in line_lower:
                        violations.append((line_num, f"[Principle 4.4] Scenario contains technical language '{term}': {line.strip()[:60]}..."))
                        break  # Only report first technical term per line
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


# 2.5.4 Principle 4.1: Given Statements Describe States (BDD-Inspired)
class ScenarioGivenStateHeuristic(CodeHeuristic):
    """Validate Given statements use state-oriented language (Principle 4.1) - Reuses BDD state heuristic patterns"""
    
    def __init__(self):
        super().__init__(detection_pattern="scenario_given_state")
    
    def scan(self, content):
        """Scan for action-oriented Given statements (should be state-oriented)"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Only scan story documents (📝 *.md)
        if not (content.file_path.endswith('.md') and '📝' in content.file_path):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Action-oriented patterns in Given statements (should be state-oriented instead)
        # Same patterns as BDD heuristic but applied to Given statements
        import re
        action_patterns = [
            (r'\bis\s+on\s+the\b', "implies navigation action", " - Try: 'screen is displayed' instead of 'user is on screen'"),
            (r'\bwent\s+to\b', "navigation action", " - Try: 'page is displayed' instead of 'went to page'"),
            (r'\bclicked\b', "action verb", " - Try: state after click (e.g., 'button has been activated')"),
            (r'\bnavigated\b', "action verb", " - Try: 'page is displayed' instead of 'navigated to page'"),
            (r'\blogged\s+in\b', "action phrase", " - Try: 'user is authenticated' instead of 'user logged in'"),
            (r'\bsubmitted\b', "action verb", " - Try: state after submission (e.g., 'form has been submitted')"),
            (r'\bentered\b', "action verb", " - Try: state after entry (e.g., 'data is entered' or 'field contains value')"),
            (r'\bselected\b', "action verb", " - Try: state after selection (e.g., 'option is selected')"),
        ]
        
        # Valid state patterns (from BDD Section 2) - for reference
        # "that has been [past participle]" - completed states (e.g., "character has been created")
        # "that is being [verb]" - ongoing states (e.g., "character is being edited")
        # "that is [adjective/noun]" - current states (e.g., "screen is displayed", "user is authenticated")
        # "that has [noun]" - possession states (e.g., "character has invalid data")
        
        in_scenarios_section = False
        in_given_context = False  # Track if we're in Given context (before When/Then/But)
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            # Check if we're in Scenarios section
            if '## scenarios' in line_lower or '## background' in line_lower:
                in_scenarios_section = True
                in_given_context = False
            elif line_stripped.startswith('##') and 'scenario' not in line_lower and 'background' not in line_lower:
                in_scenarios_section = False
                in_given_context = False
            
            if in_scenarios_section:
                # Track context: Given starts Given context, When/Then/But ends it
                if line_stripped.startswith('**Given**') or line_stripped.startswith('**given**'):
                    in_given_context = True
                elif (line_stripped.startswith('**When**') or line_stripped.startswith('**when**') or
                      line_stripped.startswith('**Then**') or line_stripped.startswith('**then**') or
                      line_stripped.startswith('**But**') or line_stripped.startswith('**but**')):
                    in_given_context = False
                
                # Only check Given statements and And statements in Given context
                if line_stripped.startswith('**Given**') or line_stripped.startswith('**given**'):
                    # This is a Given - always check it
                    for pattern, description, suggestion in action_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append((line_num, f"[Principle 4.1] Given statement uses {description} - should use state-oriented language (e.g., 'character is being edited', 'screen is displayed', 'user is authenticated'){suggestion}"))
                            break  # Only report first violation per line
                elif (line_stripped.startswith('**And**') or line_stripped.startswith('**and**')) and in_given_context:
                    # This is an And following a Given - check it
                    for pattern, description, suggestion in action_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append((line_num, f"[Principle 4.1] Given statement (And) uses {description} - should use state-oriented language (e.g., 'character is being edited', 'screen is displayed', 'user is authenticated'){suggestion}"))
                            break  # Only report first violation per line
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


if __name__ == "__main__":
    main()
