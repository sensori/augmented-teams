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

# HELPER FUNCTIONS
# Helper function to connect story maps to story documents via hyperlinks
def connect_story_maps_to_documents(story_map_path: Path, verbose=True):
    """
    Automatically add markdown hyperlinks from story map/increment files to actual documents.
    
    Converts:
        🎯 **Epic Name** → [🎯 **Epic Name**](./🎯 Epic Name/🎯 Epic Name - Epic Overview.md)
        ⚙️ **Feature Name** → [⚙️ **Feature Name**](./🎯 Epic/⚙️ Feature Name/⚙️ Feature Name - Feature Overview.md)
        📝 Story Name → [📝 Story Name](./🎯 Epic/⚙️ Feature/📝 Story Name.md)
    
    Args:
        story_map_path: Path to story map file (story-map.md or increments.md)
        verbose: Print status messages
    
    Returns:
        Tuple of (epic_links, feature_links, story_links)
    """
    import re
    
    if not story_map_path.exists():
        if verbose:
            print(f"Story map not found: {story_map_path}")
        return (0, 0, 0)
    
    # Read story map content
    with open(story_map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Determine base path for relative links
    # If this is an increments file, links go up one level then to map/
    # If this is a story-map file, links are relative to same directory
    is_increments = 'increments' in story_map_path.name or 'increments' in str(story_map_path.parent)
    
    if is_increments:
        # increments/file.md -> ../map/
        map_base = story_map_path.parent.parent / "map"
        link_prefix = "../map/"
    else:
        # map/file.md -> ./
        map_base = story_map_path.parent
        link_prefix = "./"
    
    # Patterns to match different hierarchy levels
    epic_pattern = r'^(\s*[│├└─\s]*)(🎯\s+)(\*\*)([^\*\[]+)(\*\*)'
    feature_pattern = r'^(\s*[│├└─\s]*)(⚙️\s+)(\*\*)([^\*\[]+)(\*\*)'
    story_pattern = r'^(\s*[│├└─\s]*)(📝\s+)([^\[\n]+?)(\s*$)'
    
    lines = content.split('\n')
    modified_lines = []
    epic_links = 0
    feature_links = 0
    story_links = 0
    
    # Track current epic and feature from context
    current_epic = None
    current_feature = None
    
    for line in lines:
        # Check for EPIC line (🎯 **Epic Name**)
        epic_match = re.match(epic_pattern, line)
        if epic_match:
            indent = epic_match.group(1)
            emoji = epic_match.group(2)  # 🎯 
            star1 = epic_match.group(3)  # **
            epic_name_raw = epic_match.group(4).strip()
            star2 = epic_match.group(5)  # **
            
            # Remove parenthetical info like (8 features, ~75 stories) or (PARTIAL - 4 of 8 features)
            epic_name = re.sub(r'\s*\([^)]*\)', '', epic_name_raw).strip()
            current_epic = epic_name
            current_feature = None
            
            # Check if already a link
            if '[🎯' in line:
                modified_lines.append(line)
                continue
            
            # Check if Epic Overview exists
            epic_folder = map_base / f"🎯 {epic_name}"
            epic_overview_file = epic_folder / f"🎯 {epic_name} - Epic Overview.md"
            
            if epic_overview_file.exists():
                # Build relative path
                if is_increments:
                    relative_path = f"{link_prefix}🎯 {epic_name}/🎯 {epic_name} - Epic Overview.md"
                else:
                    relative_path = f"{link_prefix}🎯 {epic_name}/🎯 {epic_name} - Epic Overview.md"
                
                # URL-encode
                import urllib.parse
                encoded_path = urllib.parse.quote(relative_path, safe='/.#-_')
                
                # Create link: [🎯 **Epic Name**](path) with two trailing spaces for markdown line breaks
                linked_epic = f"{indent}[{emoji}{star1}{epic_name}{star2}]({encoded_path}) {epic_name_raw.replace(epic_name, '').strip()}  "
                modified_lines.append(linked_epic)
                epic_links += 1
            else:
                modified_lines.append(line)
            continue
        
        # Check for FEATURE line (⚙️ **Feature Name**)
        feature_match = re.match(feature_pattern, line)
        if feature_match:
            indent = feature_match.group(1)
            emoji = feature_match.group(2)  # ⚙️ 
            star1 = feature_match.group(3)  # **
            feature_name_raw = feature_match.group(4).strip()
            star2 = feature_match.group(5)  # **
            
            # Remove parenthetical info like (5 stories) or (~8 stories)
            feature_name = re.sub(r'\s*\([^)]*\)', '', feature_name_raw).strip()
            current_feature = feature_name
            
            # Check if already a link
            if '[⚙️' in line:
                modified_lines.append(line)
                continue
            
            # Check if Feature Overview exists
            if current_epic:
                feature_folder = map_base / f"🎯 {current_epic}" / f"⚙️ {feature_name}"
                feature_overview_file = feature_folder / f"⚙️ {feature_name} - Feature Overview.md"
                
                if feature_overview_file.exists():
                    # Build relative path
                    if is_increments:
                        relative_path = f"{link_prefix}🎯 {current_epic}/⚙️ {feature_name}/⚙️ {feature_name} - Feature Overview.md"
                    else:
                        relative_path = f"{link_prefix}🎯 {current_epic}/⚙️ {feature_name}/⚙️ {feature_name} - Feature Overview.md"
                    
                    # URL-encode
                    import urllib.parse
                    encoded_path = urllib.parse.quote(relative_path, safe='/.#-_')
                    
                    # Create link: [⚙️ **Feature Name**](path) with two trailing spaces for markdown line breaks
                    linked_feature = f"{indent}[{emoji}{star1}{feature_name}{star2}]({encoded_path}) {feature_name_raw.replace(feature_name, '').strip()}  "
                    modified_lines.append(linked_feature)
                    feature_links += 1
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)
            continue
        
        # Check for STORY line (📝 Story Name)
        story_match = re.match(story_pattern, line)
        
        if story_match and current_epic and current_feature:
            indent = story_match.group(1)  # Preserve indentation and tree chars
            emoji = story_match.group(2)   # 📝 
            story_name = story_match.group(3).strip()  # Story Name
            
            # Check if already a link
            if story_name.startswith('['):
                modified_lines.append(line)
                continue
            
            # Build path to story file
            story_filename = f"📝 {story_name}.md"
            story_path = map_base / f"🎯 {current_epic}" / f"⚙️ {current_feature}" / story_filename
            
            # Check if story file exists
            if story_path.exists():
                # Build relative path from story map to story file
                if is_increments:
                    relative_path = f"{link_prefix}🎯 {current_epic}/⚙️ {current_feature}/{story_filename}"
                else:
                    relative_path = f"{link_prefix}🎯 {current_epic}/⚙️ {current_feature}/{story_filename}"
                
                # URL-encode the path for markdown compatibility (handles emojis and spaces)
                import urllib.parse
                encoded_path = urllib.parse.quote(relative_path, safe='/.#-_')
                
                # Create markdown link with encoded path and preserve two trailing spaces for markdown line breaks
                linked_story = f"[{emoji}{story_name}]({encoded_path})"
                modified_line = f"{indent}{linked_story}  "
                modified_lines.append(modified_line)
                story_links += 1
            else:
                # Story file doesn't exist yet, keep original
                modified_lines.append(line)
        else:
            # Not an epic/feature/story line, keep original
            modified_lines.append(line)
    
    # Write back modified content
    total_links = epic_links + feature_links + story_links
    if total_links > 0:
        modified_content = '\n'.join(modified_lines)
        with open(story_map_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        if verbose:
            link_summary = []
            if epic_links > 0:
                link_summary.append(f"{epic_links} epic")
            if feature_links > 0:
                link_summary.append(f"{feature_links} feature")
            if story_links > 0:
                link_summary.append(f"{story_links} story")
            print(f"✅ Connected {', '.join(link_summary)} links in {story_map_path.name}")
    
    return (epic_links, feature_links, story_links)


def sync_stories_from_increments_to_map(solution_dir: Path, verbose=True):
    """
    Copy story lines from increments to map, replacing ~X with actual stories. Avoid duplicates.
    
    Simple algorithm:
    1. Find features in increments with detailed stories (no ~X)
    2. In map, replace (~X stories) placeholder lines with actual story lines from increments
    3. Use text comparison to avoid adding duplicates
    
    Args:
        solution_dir: Path to solution directory
        verbose: Print status messages
    
    Returns:
        Number of features updated
    """
    import re
    
    stories_dir = solution_dir / "docs" / "stories"
    map_file = None
    inc_file = None
    
    for f in (stories_dir / "map").glob("*story-map.md"):
        if "increments" not in f.name and "shaping" not in f.name and "discovery" not in f.name:
            map_file = f
            break
    
    for f in (stories_dir / "increments").glob("*increments.md"):
        if "shaping" not in f.name and "discovery" not in f.name:
            inc_file = f
            break
    
    if not map_file or not inc_file:
        return 0
    
    # Read both files as lines
    with open(inc_file, 'r', encoding='utf-8') as f:
        inc_lines = f.readlines()
    with open(map_file, 'r', encoding='utf-8') as f:
        map_lines = f.readlines()
    
    # Build map of feature → story lines from increments (where stories are detailed, not ~X)
    inc_features = {}  # {(epic, feature): [story_lines]}
    current_epic = None
    current_feature = None
    collecting = False
    buffer = []
    
    for line in inc_lines:
        if '🎯' in line and '**' in line:
            m = re.search(r'🎯\s+\*\*([^*]+)\*\*', line)
            if m:
                current_epic = re.sub(r'\s*\([^)]*\)', '', m.group(1)).strip()
                current_feature = None
                collecting = False
        elif '⚙️' in line and '**' in line and current_epic:
            m = re.search(r'⚙️\s+\*\*([^*]+)\*\*', line)
            if m:
                # Save previous buffer
                if current_feature and buffer and '~' not in ''.join(buffer):
                    inc_features[(current_epic, current_feature)] = buffer[:]
                
                current_feature = re.sub(r'\s*\([^)]*\)', '', m.group(1)).strip()
                buffer = []
                collecting = True
        elif collecting and '📝' in line and '~' not in line:
            buffer.append(line.rstrip())
    
    # Save last buffer
    if current_feature and buffer and '~' not in ''.join(buffer):
        inc_features[(current_epic, current_feature)] = buffer[:]
    
    # Update map: replace ~X story sections with actual stories from increments
    new_lines = []
    current_epic = None
    current_feature = None
    skip_until_next_feature = False
    features_synced = 0
    i = 0
    
    while i < len(map_lines):
        line = map_lines[i]
        
        if '🎯' in line and '**' in line:
            m = re.search(r'🎯\s+\*\*([^*]+)\*\*', line)
            if m:
                current_epic = re.sub(r'\s*\([^)]*\)', '', m.group(1)).strip()
                current_feature = None
                skip_until_next_feature = False
        
        elif '⚙️' in line and '**' in line and current_epic:
            m = re.search(r'⚙️\s+\*\*([^*]+)\*\*', line)
            if m:
                current_feature = re.sub(r'\s*\([^)]*\)', '', m.group(1)).strip()
                skip_until_next_feature = False
                
                # Do we have detailed stories for this feature?
                key = (current_epic, current_feature)
                if key in inc_features:
                    # Update count and add two trailing spaces for markdown line break
                    count = len(inc_features[key])
                    line = re.sub(r'\(~?\d+\s+stories?\)', f'({count} stories)', line.rstrip()) + '  \n'
                    new_lines.append(line)
                    
                    # Skip old stories (lines with 📝 and ~X placeholder)
                    i += 1
                    while i < len(map_lines) and ('📝' in map_lines[i] or (map_lines[i].strip() and '│' in map_lines[i] and not '⚙️' in map_lines[i] and not '🎯' in map_lines[i])):
                        i += 1
                    
                    # Add stories from increments
                    for story_line in inc_features[key]:
                        new_lines.append(story_line + '  \n')
                    
                    # Add tree spacer
                    new_lines.append(re.match(r'^(\s*[│├└─\s]*)', line).group(1) + '│  \n')
                    
                    features_synced += 1
                    if verbose:
                        print(f"  ✓ {current_feature}: {count} stories")
                    continue
        
        new_lines.append(line)
        i += 1
    
    # Write if changed
    if features_synced > 0:
        with open(map_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        if verbose:
            print(f"✅ Synced {features_synced} features")
    
    return features_synced


def sync_story_counts_to_main_map(story_map_path: Path, verbose=True):
    """
    Sync actual story counts from detailed decomposition back to main story map.
    
    When features are fully decomposed (no ~X notation), update the main story map
    to show actual story count instead of estimate.
    
    Args:
        story_map_path: Path to main story map file
        verbose: Print status messages
    
    Returns:
        Number of features updated with actual counts
    """
    import re
    
    if not story_map_path.exists():
        if verbose:
            print(f"Story map not found: {story_map_path}")
        return 0
    
    # Read story map
    with open(story_map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified_lines = []
    updates_made = 0
    
    current_epic = None
    current_feature = None
    feature_story_count = 0
    counting_stories = False
    feature_line_index = None
    
    epic_pattern = r'🎯\s+\*\*(.+?)\*\*'
    feature_pattern = r'(^\s*[│├└─\s]*)(⚙️\s+\*\*)(.+?)(\*\*)(\s*\(~?\d+\s+stories?\))?(.*)$'
    story_pattern = r'^\s*[│├└─\s]*📝\s+'
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Track current epic
        epic_match = re.search(epic_pattern, line)
        if epic_match:
            epic_name = epic_match.group(1)
            # Remove parenthetical info
            epic_name = re.sub(r'\s*\([^)]*\)', '', epic_name).strip()
            if epic_name not in ['Epic', 'Feature', 'Story', 'Sub-Epic']:
                current_epic = epic_name
                current_feature = None
                feature_story_count = 0
                counting_stories = False
        
        # Check for feature line
        feature_match = re.match(feature_pattern, line)
        if feature_match and current_epic:
            indent = feature_match.group(1)
            emoji_stars = feature_match.group(2)  # ⚙️ **
            feature_name_raw = feature_match.group(3)
            end_stars = feature_match.group(4)  # **
            count_part = feature_match.group(5)  # (~X stories) or None
            rest = feature_match.group(6)  # any remaining text
            
            # Remove parenthetical from name
            feature_name = re.sub(r'\s*\([^)]*\)', '', feature_name_raw).strip()
            
            # Skip placeholders
            if not (feature_name.startswith('~') or 'more features' in feature_name.lower()):
                current_feature = feature_name
                feature_line_index = i
                feature_story_count = 0
                counting_stories = True
                
                # Continue to next line to start counting
                modified_lines.append(line)
                i += 1
                continue
        
        # Count stories under current feature
        if counting_stories and current_feature:
            story_match = re.match(story_pattern, line)
            
            if story_match:
                # This is a story line
                story_text = line.strip()
                # Skip placeholder stories
                if not (story_text.startswith('~') or 'more stories' in story_text.lower()):
                    feature_story_count += 1
            elif line.strip().startswith('⚙️') or line.strip().startswith('🎯'):
                # Hit next feature/epic, update previous feature if needed
                if feature_story_count > 0 and feature_line_index is not None:
                    # Update the feature line with actual count
                    old_feature_line = modified_lines[feature_line_index]
                    old_match = re.match(feature_pattern, old_feature_line)
                    
                    if old_match:
                        indent = old_match.group(1)
                        emoji_stars = old_match.group(2)
                        feature_name_raw = old_match.group(3)
                        end_stars = old_match.group(4)
                        old_count = old_match.group(5)  # (~X stories) or (X stories)
                        rest = old_match.group(6)
                        
                        # Check if it was an estimate (~X) or if count changed
                        if old_count and '~' in old_count:
                            # Was an estimate, replace with actual
                            new_count = f" ({feature_story_count} {'story' if feature_story_count == 1 else 'stories'})"
                            new_feature_line = f"{indent}{emoji_stars}{feature_name_raw}{end_stars}{new_count}{rest}"
                            modified_lines[feature_line_index] = new_feature_line
                            updates_made += 1
                            if verbose:
                                print(f"  ✓ Updated {current_feature}: ~X → {feature_story_count} stories")
                
                # Reset for next feature
                counting_stories = False
                current_feature = None
                feature_story_count = 0
                feature_line_index = None
        
        modified_lines.append(line)
        i += 1
    
    # Handle last feature if at end of file
    if counting_stories and feature_story_count > 0 and feature_line_index is not None:
        old_feature_line = modified_lines[feature_line_index]
        old_match = re.match(feature_pattern, old_feature_line)
        
        if old_match:
            indent = old_match.group(1)
            emoji_stars = old_match.group(2)
            feature_name_raw = old_match.group(3)
            end_stars = old_match.group(4)
            old_count = old_match.group(5)
            rest = old_match.group(6)
            
            if old_count and '~' in old_count:
                new_count = f" ({feature_story_count} {'story' if feature_story_count == 1 else 'stories'})"
                new_feature_line = f"{indent}{emoji_stars}{feature_name_raw}{end_stars}{new_count}{rest}"
                modified_lines[feature_line_index] = new_feature_line
                updates_made += 1
                if verbose:
                    print(f"  ✓ Updated {current_feature}: ~X → {feature_story_count} stories")
    
    # Write back if changes made
    if updates_made > 0:
        modified_content = '\n'.join(modified_lines)
        with open(story_map_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        if verbose:
            print(f"✅ Updated {updates_made} features with actual story counts in main story map")
    elif verbose:
        print("✅ Story map already has actual counts (no ~X estimates found)")
    
    return updates_made


def validate_story_map_links(story_map_path: Path, verbose=True):
    """
    Validate that all markdown links in story map point to existing files.
    
    Args:
        story_map_path: Path to story map file (story-map.md or increments.md)
        verbose: Print status messages
    
    Returns:
        List of tuples (line_number, link_text, expected_path, issue_description)
    """
    import re
    
    if not story_map_path.exists():
        if verbose:
            print(f"Story map not found: {story_map_path}")
        return []
    
    # Read story map content
    with open(story_map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    broken_links = []
    
    # Pattern to match markdown links: [text](path)
    link_pattern = r'\[(📝[^\]]+)\]\(([^)]+)\)'
    
    for line_num, line in enumerate(lines, start=1):
        # Find all markdown links in line
        for match in re.finditer(link_pattern, line):
            link_text = match.group(1)  # The display text
            link_path = match.group(2)  # The file path
            
            # Resolve relative path from story map location
            absolute_path = (story_map_path.parent / link_path).resolve()
            
            # Check if file exists
            if not absolute_path.exists():
                broken_links.append((
                    line_num,
                    link_text,
                    str(absolute_path),
                    f"Link target does not exist: {link_path}"
                ))
    
    if verbose and broken_links:
        print(f"⚠️  Found {len(broken_links)} broken links in {story_map_path.name}")
        for line_num, text, path, issue in broken_links:
            print(f"  Line {line_num}: {text} -> {issue}")
    elif verbose:
        print(f"✅ All story links valid in {story_map_path.name}")
    
    return broken_links


def correct_story_map_links(story_map_path: Path, verbose=True):
    """
    Correct broken links in story map by finding the actual story files.
    
    This function:
    1. Detects broken links
    2. Searches for the story file in the expected location or nearby
    3. Updates the link with the correct path
    
    Args:
        story_map_path: Path to story map file (story-map.md or increments.md)
        verbose: Print status messages
    
    Returns:
        Number of links corrected
    """
    import re
    
    if not story_map_path.exists():
        if verbose:
            print(f"Story map not found: {story_map_path}")
        return 0
    
    # First validate to find broken links
    broken_links = validate_story_map_links(story_map_path, verbose=False)
    
    if not broken_links:
        if verbose:
            print(f"✅ No broken links to correct in {story_map_path.name}")
        return 0
    
    # Read story map content
    with open(story_map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    corrections_made = 0
    
    # Determine base path for links
    is_increments = 'increments' in story_map_path.name or 'increments' in str(story_map_path.parent)
    
    if is_increments:
        map_base = story_map_path.parent.parent / "map"
        link_prefix = "../map/"
    else:
        map_base = story_map_path.parent
        link_prefix = "./"
    
    # Track current epic and feature from context
    current_epic = None
    current_feature = None
    
    # Pattern to match markdown links: [text](path)
    link_pattern = r'\[(📝\s+[^\]]+)\]\(([^)]+)\)'
    
    modified_lines = []
    
    for line_num, line in enumerate(lines, start=1):
        # Track epic context
        epic_match = re.match(r'.*🎯\s+\*\*([^*]+)\*\*', line)
        if epic_match:
            current_epic = epic_match.group(1).strip()
            current_feature = None
        
        # Track feature context
        feature_match = re.match(r'.*⚙️\s+\*\*([^*]+)\*\*', line)
        if feature_match:
            current_feature = feature_match.group(1).strip()
        
        # Check if this line has any broken links from our validation
        line_has_broken_link = any(bl[0] == line_num for bl in broken_links)
        
        if line_has_broken_link and current_epic and current_feature:
            # Try to fix the link
            def replace_broken_link(match):
                nonlocal corrections_made
                link_text = match.group(1)  # [📝 Story Name]
                old_path = match.group(2)   # (old/path.md)
                
                # Extract story name from link text
                story_name_match = re.search(r'📝\s+(.+)', link_text)
                if story_name_match:
                    story_name = story_name_match.group(1).strip()
                    
                    # Build expected path
                    story_filename = f"📝 {story_name}.md"
                    expected_path = map_base / f"🎯 {current_epic}" / f"⚙️ {current_feature}" / story_filename
                    
                    # Check if file exists at expected location
                    if expected_path.exists():
                        # Build correct relative path
                        if is_increments:
                            correct_path = f"{link_prefix}🎯 {current_epic}/⚙️ {current_feature}/{story_filename}"
                        else:
                            correct_path = f"{link_prefix}🎯 {current_epic}/⚙️ {current_feature}/{story_filename}"
                        
                        # URL-encode the path for markdown compatibility (handles emojis and spaces)
                        import urllib.parse
                        encoded_path = urllib.parse.quote(correct_path, safe='/.#-_')
                        
                        corrections_made += 1
                        if verbose:
                            print(f"  ✅ Fixed: Line {line_num}: {story_name}")
                        return f"[{link_text}]({encoded_path})"
                
                # If we can't fix it, return original
                return match.group(0)
            
            # Replace broken links in this line
            modified_line = re.sub(link_pattern, replace_broken_link, line)
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)
    
    # Write back corrected content
    if corrections_made > 0:
        corrected_content = '\n'.join(modified_lines)
        with open(story_map_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        if verbose:
            print(f"✅ Corrected {corrections_made} broken links in {story_map_path.name}")
    
    return corrections_made


def add_navigation_breadcrumbs_to_story_maps(solution_dir: Path, verbose=True):
    """
    Add navigation breadcrumbs to story map and increments files.
    
    Story Map gets: **Navigation:** [📊 Increments](../increments/increments.md)
    Increments gets: **Navigation:** [📋 Story Map](../map/story-map.md)
    
    Args:
        solution_dir: Path to solution directory (e.g., demo/mm3e/)
        verbose: Print status messages
    
    Returns:
        Number of files updated
    """
    import urllib.parse
    
    stories_dir = solution_dir / "docs" / "stories"
    if not stories_dir.exists():
        if verbose:
            print(f"Stories directory not found: {stories_dir}")
        return 0
    
    files_updated = 0
    
    # Find main story map and increments files (exclude shaping/discovery versions)
    map_dir = stories_dir / "map"
    increments_dir = stories_dir / "increments"
    
    story_map_file = None
    increments_file = None
    
    if map_dir.exists():
        for candidate in map_dir.glob("*story-map.md"):
            if "increments" not in candidate.name and "shaping" not in candidate.name and "discovery" not in candidate.name:
                story_map_file = candidate
                break
    
    if increments_dir.exists():
        for candidate in increments_dir.glob("*increments.md"):
            if "shaping" not in candidate.name and "discovery" not in candidate.name:
                increments_file = candidate
                break
    
    # Add navigation to story map file
    if story_map_file and increments_file:
        with open(story_map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '**Navigation:**' not in content:
            # Build navigation line
            encoded_inc_path = urllib.parse.quote(f"../increments/{increments_file.name}", safe='/.#-_')
            nav_line = f"**Navigation:** [📊 Increments]({encoded_inc_path})"
            
            # Insert after title
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# Story Map:') or line.startswith('# Story Map -'):
                    lines.insert(i + 1, '')
                    lines.insert(i + 2, nav_line)
                    break
            
            with open(story_map_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            files_updated += 1
            if verbose:
                print(f"  ✓ Added navigation to: {story_map_file.name}")
    
    # Add navigation to increments file
    if increments_file and story_map_file:
        with open(increments_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '**Navigation:**' not in content:
            # Build navigation line
            encoded_map_path = urllib.parse.quote(f"../map/{story_map_file.name}", safe='/.#-_')
            nav_line = f"**Navigation:** [📋 Story Map]({encoded_map_path})"
            
            # Insert after title
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# Story Map Increments:') or line.startswith('# Story Map Increments -'):
                    lines.insert(i + 1, '')
                    lines.insert(i + 2, nav_line)
                    break
            
            with open(increments_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            files_updated += 1
            if verbose:
                print(f"  ✓ Added navigation to: {increments_file.name}")
    
    if verbose and files_updated > 0:
        print(f"✅ Added navigation breadcrumbs to {files_updated} story map files")
    elif verbose:
        print("Story map files already have navigation breadcrumbs")
    
    return files_updated


def add_navigation_breadcrumbs_to_feature_overviews(solution_dir: Path, verbose=True):
    """
    Add navigation breadcrumbs to all Feature Overview files that don't have them.
    
    Adds at top of file:
    **Navigation:** [📋 Story Map](../../story-map.md) | [📊 Increments](../../../increments/increments.md)
    
    Args:
        solution_dir: Path to solution directory (e.g., demo/mm3e/)
        verbose: Print status messages
    
    Returns:
        Number of files updated
    """
    import urllib.parse
    
    stories_dir = solution_dir / "docs" / "stories"
    map_dir = stories_dir / "map"
    
    if not map_dir.exists():
        if verbose:
            print(f"Stories map directory not found: {map_dir}")
        return 0
    
    # Find story map and increments filenames
    story_map_file = None
    increments_file = None
    
    for candidate in map_dir.glob("*story-map.md"):
        if "increments" not in candidate.name and "shaping" not in candidate.name and "discovery" not in candidate.name:
            story_map_file = candidate.name
            break
    
    increments_dir = stories_dir / "increments"
    if increments_dir.exists():
        for candidate in increments_dir.glob("*increments.md"):
            if "shaping" not in candidate.name and "discovery" not in candidate.name:
                increments_file = candidate.name
                break
    
    if not story_map_file:
        story_map_file = "story-map.md"  # fallback
    if not increments_file:
        increments_file = "story-map-increments.md"  # fallback
    
    files_updated = 0
    
    # Process all Feature Overview files
    for epic_dir in map_dir.iterdir():
        if not epic_dir.is_dir() or not (epic_dir.name.startswith('🎯') or epic_dir.name.startswith('epic-')):
            continue
        
        for feature_dir in epic_dir.iterdir():
            if not feature_dir.is_dir() or not (feature_dir.name.startswith('⚙️') or feature_dir.name.startswith('feature-')):
                continue
            
            # Find Feature Overview file
            for feature_file in feature_dir.glob("*Feature Overview*.md"):
                # Read file
                with open(feature_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if navigation breadcrumbs already exist
                if '**Navigation:**' in content:
                    continue
                
                # Build navigation line with URL-encoded paths
                encoded_map_path = urllib.parse.quote(f"../../{story_map_file}", safe='/.#-_')
                encoded_inc_path = urllib.parse.quote(f"../../../increments/{increments_file}", safe='/.#-_')
                nav_line = f"**Navigation:** [📋 Story Map]({encoded_map_path}) | [📊 Increments]({encoded_inc_path})"
                
                # Find the title line (starts with # ⚙️)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# ⚙️'):
                        # Insert navigation after title and blank line
                        lines.insert(i + 1, '')
                        lines.insert(i + 2, nav_line)
                        break
                
                # Write back
                new_content = '\n'.join(lines)
                with open(feature_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                files_updated += 1
                if verbose:
                    print(f"  ✓ Added navigation to: {feature_file.name}")
    
    if verbose and files_updated > 0:
        print(f"✅ Added navigation breadcrumbs to {files_updated} feature overview files")
    elif verbose:
        print("All feature overview files already have navigation breadcrumbs")
    
    return files_updated


def fix_continuation_line_spacing(file_path: Path) -> int:
    """
    Replace regular spaces with &nbsp; in continuation lines for markdown preview.
    
    Continuation lines are any lines that:
    - Have tree characters (│├└) or just spaces at start
    - Have a dash (- ) in them
    - DON'T have a story emoji (📝)
    
    Args:
        file_path: Path to story map or increments file
    
    Returns:
        Number of lines fixed
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    fixed_count = 0
    
    for line in lines:
        # Skip story lines (have 📝)
        if '📝' in line:
            new_lines.append(line)
            continue
        
        # Check if this line has a dash and could be a continuation
        if ' - ' in line or line.lstrip().startswith('- '):
            # Skip if already has &nbsp;
            if '&nbsp;' in line:
                new_lines.append(line)
                continue
            
            # This is a continuation line - fix the spacing
            # Find where the dash is
            dash_pos = line.find(' - ')
            if dash_pos == -1:
                dash_pos = line.find('- ')
            
            if dash_pos > 0:
                # Get prefix (everything before dash)
                prefix = line[:dash_pos]
                suffix = line[dash_pos:]
                
                # Find last non-space character in prefix
                last_nonspace = -1
                for i, char in enumerate(prefix):
                    if char not in ' ':
                        last_nonspace = i
                
                if last_nonspace >= 0:
                    # Split into: tree chars + spaces
                    before_spaces = prefix[:last_nonspace + 1]
                    spaces = prefix[last_nonspace + 1:]
                    space_count = len(spaces)
                    
                    # Replace with nbsp (keep 1 regular space)
                    if space_count > 1:
                        new_prefix = before_spaces + ' ' + '&nbsp;' * (space_count - 1)
                        line = new_prefix + suffix
                        fixed_count += 1
        
        new_lines.append(line)
    
    # Write back
    new_content = '\n'.join(new_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return fixed_count


def fix_all_story_maps_in_solution(solution_dir: Path, verbose=True) -> int:
    """
    Fix continuation line spacing in all story maps in a solution.
    
    Markdown preview collapses multiple regular spaces into one.
    This function replaces regular spaces with &nbsp; entities in
    continuation lines (lines with dashes after story lines) to
    preserve visual indentation alignment.
    
    Args:
        solution_dir: Path to solution directory (e.g., demo/mm3e/)
        verbose: Print status messages
    
    Returns:
        Total number of lines fixed across all files
    """
    stories_dir = solution_dir / "docs" / "stories"
    
    if not stories_dir.exists():
        if verbose:
            print(f"Stories directory not found: {stories_dir}")
        return 0
    
    total_fixed = 0
    
    # Fix story map
    map_dir = stories_dir / "map"
    for map_file in map_dir.glob("*story-map.md"):
        if "increments" not in map_file.name:
            fixed = fix_continuation_line_spacing(map_file)
            total_fixed += fixed
            if verbose and fixed > 0:
                print(f"  ✓ Fixed {fixed} continuation lines in {map_file.name}")
    
    # Fix increments
    inc_dir = stories_dir / "increments"
    for inc_file in inc_dir.glob("*increments.md"):
        fixed = fix_continuation_line_spacing(inc_file)
        total_fixed += fixed
        if verbose and fixed > 0:
            print(f"  ✓ Fixed {fixed} continuation lines in {inc_file.name}")
    
    if verbose and total_fixed > 0:
        print(f"✅ Fixed {total_fixed} total continuation lines")
    elif verbose:
        print("All continuation lines already properly formatted")
    
    return total_fixed


def add_navigation_breadcrumbs_to_stories(solution_dir: Path, verbose=True):
    """
    Add navigation breadcrumbs to all story files that don't have them.
    
    Adds at top of file:
    **Navigation:** [📋 Story Map](../../story-map.md) | [⚙️ Feature Overview](./feature-overview.md)
    
    Args:
        solution_dir: Path to solution directory (e.g., demo/mm3e/)
        verbose: Print status messages
    
    Returns:
        Number of files updated
    """
    import re
    import urllib.parse
    
    stories_dir = solution_dir / "docs" / "stories"
    map_dir = stories_dir / "map"
    
    if not map_dir.exists():
        if verbose:
            print(f"Stories map directory not found: {map_dir}")
        return 0
    
    # Find story map filename
    story_map_file = None
    for candidate in map_dir.glob("*story-map.md"):
        if "increments" not in candidate.name and "shaping" not in candidate.name and "discovery" not in candidate.name:
            story_map_file = candidate.name
            break
    
    if not story_map_file:
        story_map_file = "story-map.md"  # fallback
    
    files_updated = 0
    
    # Process all story files
    for epic_dir in map_dir.iterdir():
        if not epic_dir.is_dir() or not (epic_dir.name.startswith('🎯') or epic_dir.name.startswith('epic-')):
            continue
        
        for feature_dir in epic_dir.iterdir():
            if not feature_dir.is_dir() or not (feature_dir.name.startswith('⚙️') or feature_dir.name.startswith('feature-')):
                continue
            
            # Find feature overview file
            feature_overview_file = None
            for candidate in feature_dir.glob("*Feature Overview*.md"):
                feature_overview_file = candidate.name
                break
            
            if not feature_overview_file:
                feature_overview_file = f"{feature_dir.name} - Feature Overview.md"
            
            # Process each story file
            for story_file in feature_dir.glob("📝*.md"):
                if "Feature Overview" in story_file.name:
                    continue
                
                # Read file
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if navigation breadcrumbs already exist
                if '**Navigation:**' in content:
                    continue
                
                # Build navigation line with URL-encoded paths
                encoded_map_path = urllib.parse.quote(f"../../{story_map_file}", safe='/.#-_')
                encoded_feature_path = urllib.parse.quote(f"./{feature_overview_file}", safe='/.#-_')
                nav_line = f"\n**Navigation:** [📋 Story Map]({encoded_map_path}) | [⚙️ Feature Overview]({encoded_feature_path})\n"
                
                # Find the title line (starts with # 📝)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# 📝'):
                        # Insert navigation after title and blank line
                        lines.insert(i + 1, '')
                        lines.insert(i + 2, nav_line.strip())
                        break
                
                # Write back
                new_content = '\n'.join(lines)
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                files_updated += 1
                if verbose:
                    print(f"  ✓ Added navigation to: {story_file.name}")
    
    if verbose and files_updated > 0:
        print(f"✅ Added navigation breadcrumbs to {files_updated} story files")
    elif verbose:
        print("All story files already have navigation breadcrumbs")
    
    return files_updated


def connect_all_story_maps_in_solution(solution_dir: Path, verbose=True):
    """
    Find and connect links in all story map files within a solution directory.
    
    This is a convenience function that:
    1. Finds all story map files (map/*story-map*.md)
    2. Finds all increment files (increments/*increments*.md)
    3. Calls connect_story_maps_to_documents() on each
    
    Args:
        solution_dir: Path to solution directory (e.g., demo/mm3e/)
        verbose: Print status messages
    
    Returns:
        Total number of links created across all files
    """
    if not solution_dir.exists():
        if verbose:
            print(f"Solution directory not found: {solution_dir}")
        return 0
    
    total_epic_links = 0
    total_feature_links = 0
    total_story_links = 0
    
    # Find stories directory
    stories_dir = solution_dir / "docs" / "stories"
    if not stories_dir.exists():
        if verbose:
            print(f"Stories directory not found: {stories_dir}")
        return 0
    
    # Link main story map files
    map_dir = stories_dir / "map"
    if map_dir.exists():
        for story_map_file in map_dir.glob("*story-map*.md"):
            if verbose:
                print(f"Processing: {story_map_file.name}")
            epic_links, feature_links, story_links = connect_story_maps_to_documents(story_map_file, verbose=verbose)
            total_epic_links += epic_links
            total_feature_links += feature_links
            total_story_links += story_links
    
    # Link increments files
    increments_dir = stories_dir / "increments"
    if increments_dir.exists():
        for increments_file in increments_dir.glob("*increments*.md"):
            if verbose:
                print(f"Processing: {increments_file.name}")
            epic_links, feature_links, story_links = connect_story_maps_to_documents(increments_file, verbose=verbose)
            total_epic_links += epic_links
            total_feature_links += feature_links
            total_story_links += story_links
    
    total_links = total_epic_links + total_feature_links + total_story_links
    
    if verbose and total_links > 0:
        print(f"✅ Total links connected: {total_links} (epics: {total_epic_links}, features: {total_feature_links}, stories: {total_story_links})")
    elif verbose:
        print("No new links created (all items already linked or don't exist yet)")
    
    return total_links

# 1. STORY SHAPING COMMANDS
# 1.1 Story Shape Command
# 1.1.1 Generate story map instructions
class StoryShapeCommand(Command):
    """Command for generating story map instructions"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate story map using templates.

TEMPLATES TO LOAD:
- behaviors/stories/templates/story-map-decomposition-template.md
- behaviors/stories/templates/story-map-increments-template.md

LOCATION INFERENCE:
- Detect solution folder from context (recently viewed files, open files, current directory)
- Example: Context shows demo/mm3e/ → Use demo/mm3e/ as solution folder
- Example: At workspace root → Create new solution folder

PLACEHOLDERS TO FILL:
- {product_name}: Product name (infer from context or ask)
- {product_name_slug}: Slugified product name for filename
- {solution_folder}: Detected solution folder path
- {system_purpose}: High-level purpose and user goals
- {epic_hierarchy}: Build epic/feature/story tree structure
- {increments_organized}: Identify value increments with NOW/NEXT/LATER priorities
- {source_material}: Track source document sections used

APPLY PRINCIPLES (for {epic_hierarchy} and {increments_organized}):
- §1.1 Story Map Hierarchy (4 levels: Epic/Sub-Epic/Feature/Story)
- §1.2 Business Language ([Verb] [Noun] format, NO "Epic:" prefix)
- §1.3 User AND System Activities (both perspectives required)
- §1.4 Story Counting (~X stories for unexplored areas, 10-20% identified)
- §1.5 7±2 Sizing (Epic: 4-9 features, Feature: 4-9 stories)
- §1.5 Marketable Increments (NOW/NEXT/LATER priorities)
- §1.6 Relative Sizing (compare to previous work)

CRITICAL MARKDOWN FORMATTING:
- **TWO SPACES at end of EVERY tree structure line** (│, ├─, └─, etc.) - MANDATORY for proper line breaks
- Without two spaces, markdown wraps lines together into one long unreadable line
- Example: "│  ├─ ⚙️ **Feature Name**  " (note two spaces after last **)
- Example: "│  │  ├─ 📝 Story name  " (note two spaces after story name)
- EVERY line in tree structure hierarchy needs two trailing spaces

CRITICAL:
- NO folder creation during Shape - folders created by /story-arrange
- NO story estimates during Shape - added in Discovery
- NO discovery status during Shape - added in Discovery

AFTER GENERATION:
- Call connect_all_story_maps_in_solution(solution_dir) to add hyperlinks from story names to story files
- This automatically finds and processes all story-map.md and increments.md files
- Converts story references like "📝 Story Name" to clickable markdown links "[📝 Story Name](path/to/story.md)"
- Links are only added for stories where the actual .md file exists
- Note: Links may not be created during Shape since story files don't exist yet - that's fine, they'll be created during Arrange

Templates define structure and formatting.
YOU define content following principles."""
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
        if 'link' not in result_lower:
            result += "\n- Call validate_story_map_links() to check all story hyperlinks point to existing files"
            result += "\n- Report any broken links found (link text, target path, issue)"
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

# 1.2 Story Arrange Command
# 1.2.1 Arrange folder structure to match story map
class StoryArrangeCommand(Command):
    """Command for arranging folder structure to match story map"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate folder structure matching story map hierarchy.
        
Request the following:
- Parse story map document to extract epic and feature names
- Create epic-[name]/feature-[name]/ folder structure
- Create story files from template with navigation breadcrumbs (links back to story map and feature overview)
- URL-encode all navigation paths for markdown compatibility (emojis and spaces)
- Archive obsolete folders to archive/[timestamp]/ (NEVER delete)
- Move existing files to new locations if hierarchy changed
- Detect merge candidates (multiple files for same entity)
- Generate merge-list.md with AI prompts for merging
- Report folders created, moved, archived, and merges needed

AFTER GENERATION:
- Call sync_stories_from_increments_to_map(solution_dir) to sync detailed stories from increments to main story map (both files must match exactly)
- Call add_navigation_breadcrumbs_to_feature_overviews() to add breadcrumbs to feature overview files
- Call connect_all_story_maps_in_solution() to create/update hyperlinks in story maps
- Call fix_all_story_maps_in_solution() to fix continuation line spacing (&nbsp; for markdown preview)
- NOTE: Story stub files NOT created during arrange (deferred to /story-specification phase)

CORRECTION ACTION:
- When correct is called, run sync_stories_from_increments_to_map() to sync story lists
- Run add_navigation_breadcrumbs_to_stories() to fix missing breadcrumbs
- Run connect_all_story_maps_in_solution() to reconnect any broken links
- Apply any other corrections from chat context

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
        
        # Sync stories from increments FIRST (before parsing map for file operations)
        base_dir = story_map_path.parent
        solution_dir = base_dir.parent.parent.parent
        
        print("\n" + "="*60)
        print("SYNC: Increments → Story Map")
        print("="*60)
        features_synced = sync_stories_from_increments_to_map(solution_dir, verbose=True)
        
        print("\n" + "="*60)
        print("ARRANGE: Create Folder Structure")
        print("="*60)
        
        # Read story map content
        with open(story_map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract epic, feature, and story names from story map
        # Format: 🎯 **Epic Name** or ⚙️ **Feature Name** or 📝 Story Name (may have markdown links)
        epic_pattern = r'🎯\s+\*\*(.+?)\*\*'
        feature_pattern = r'⚙️\s+\*\*(.+?)\*\*'
        # Match either [📝 Story Name](...) or just 📝 Story Name
        story_pattern = r'(?:\[📝\s+([^\]]+)\]|📝\s+([^\n\[\(]+?))\s*(?:$|\(|\[)'
        
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
                # Pattern has two groups: group(1) for [📝 Story] links, group(2) for plain 📝 Story
                story_name = (story_match.group(1) or story_match.group(2) or "").strip()
                
                # Skip single-word entries like "Story" from legend
                if story_name in ['Epic', 'Feature', 'Story', 'Sub-Epic']:
                    continue
                # Skip placeholder stories (e.g., "~X more stories")
                if story_name.startswith('~') or 'more stories' in story_name.lower() or 'more features' in story_name.lower():
                    continue
                # Skip empty
                if not story_name:
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
        print(f"\nStory Map: {story_map_path}")
        print(f"Base Directory: {base_dir}")
        print(f"\nFound {len(epics)} epics with features")
        
        # Debug: show what was parsed
        for epic_name, features in epics.items():
            print(f"  Epic: {epic_name}")
            for feature_name, stories in features.items():
                print(f"    Feature: {feature_name} ({len(stories)} stories)")
                for story in stories[:3]:  # Show first 3
                    print(f"      - {story}")
                if len(stories) > 3:
                    print(f"      ... and {len(stories) - 3} more")
        
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
                    
                    # STORY FILE CREATION DISABLED
                    # Story stub files are not needed until specification stage
                    # They create noise and clutter during discovery/exploration phases
                    # Feature Overview files contain all AC - that's what matters
                    # Story files will be created during /story-specification when scenarios are written
                    # 
                    # Commented out story file creation:
                    # if not story_path.exists():
                    #     ... create story stub file ...
        
        # DISABLED: Archiving logic is too aggressive and archives valid files
        # TODO: Fix orphan detection to not archive files that should exist
        # For now, only archive if explicitly obsolete epic folders exist
        
        # # Find and archive orphaned story files (stories in folders not in map)
        # for epic_path in base_dir.iterdir():
        #     if not epic_path.is_dir():
        #         continue
        #     if epic_path.name in ['z_archive']:
        #         continue
        #     if not (epic_path.name.startswith('🎯') or epic_path.name.startswith('epic-')):
        #         continue
        #         
        #     for feature_path in epic_path.iterdir():
        #         if not feature_path.is_dir():
        #             continue
        #         if not (feature_path.name.startswith('⚙️') or feature_path.name.startswith('feature-')):
        #             continue
        #         
        #         # Check all markdown files in feature folder
        #         for story_file in feature_path.glob('*.md'):
        #             story_filename = story_file.name
        #             
        #             # If story not in map, it's orphaned
        #             if story_filename not in map_story_files:
        #                 # Create archive directory if needed
        #                 if not archive_dir.exists():
        #                     archive_dir.mkdir(parents=True, exist_ok=True)
        #                 
        #                 # Create same epic/feature structure in archive
        #                 archive_epic_path = archive_dir / epic_path.name
        #                 archive_feature_path = archive_epic_path / feature_path.name
        #                 archive_feature_path.mkdir(parents=True, exist_ok=True)
        #                 
        #                 # Move story to archive
        #                 archive_story_path = archive_feature_path / story_filename
        #                 shutil.move(str(story_file), str(archive_story_path))
        #                 archived_stories.append(f"{story_filename} -> z_archive/{timestamp}/{epic_path.name}/{feature_path.name}/")
        #             
        #             # Check if story moved to different feature
        #             elif map_story_files[story_filename] != (epic_path, feature_path):
        #                 target_epic_path, target_feature_path = map_story_files[story_filename]
        #                 target_story_path = target_feature_path / story_filename
        #                 
        #                 # Move story to new location
        #                 shutil.move(str(story_file), str(target_story_path))
        #                 moved_stories.append(f"{story_filename}: {epic_path.name}/{feature_path.name}/ -> {target_epic_path.name}/{target_feature_path.name}/")
        
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
        else:
            print(f"\n[*] Story stub files not created (created during /story-specification phase)")
        
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
        
        # Calculate solution directory
        solution_dir = base_dir.parent.parent.parent
        
        print("\nAdding navigation breadcrumbs...")
        map_breadcrumbs = add_navigation_breadcrumbs_to_story_maps(solution_dir, verbose=True)
        feature_breadcrumbs = add_navigation_breadcrumbs_to_feature_overviews(solution_dir, verbose=True)
        story_breadcrumbs = add_navigation_breadcrumbs_to_stories(solution_dir, verbose=True)
        total_breadcrumbs = map_breadcrumbs + feature_breadcrumbs + story_breadcrumbs
        
        # Connect story map links after folder/file creation
        print("\nConnecting story map links...")
        total_links = connect_all_story_maps_in_solution(solution_dir, verbose=True)
        
        # Fix continuation line spacing for markdown preview
        print("\nFixing continuation line spacing...")
        fix_all_story_maps_in_solution(solution_dir, verbose=True)
        
        # Mark as generated
        self.generated = True
        
        result = f"""
Folder structure generation complete!

Created: {len(created_folders)} folders, {len(created_stories)} story files
Existing: {len(existing_folders)} epics (unchanged)
Moved: {len(moved_stories)} stories
Archived: {len(archived_folders)} obsolete folders, {len(archived_stories)} orphaned stories
Navigation: {total_breadcrumbs} files updated with breadcrumbs (maps: {map_breadcrumbs}, features: {feature_breadcrumbs}, stories: {story_breadcrumbs})
Story links: {total_links} hyperlinks connected

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
        if 'breadcrumb' not in result_lower and 'navigation' not in result_lower:
            result += "\n- Check that all story files have navigation breadcrumbs at top"
            result += "\n- Validate breadcrumbs link to story map and feature overview"
        if 'link' not in result_lower:
            result += "\n- Call validate_story_map_links() to check all hyperlinks are valid"
        return result

# 1.2.2 Wrap StoryArrangeCommand with code augmentation
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

# 1.3 Story Discovery Command
# 1.3.1 Refine increments and groom stories for next increment
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

CRITICAL MARKDOWN FORMATTING:
- **TWO SPACES at end of EVERY tree structure line** (│, ├─, └─, etc.) - MANDATORY for proper line breaks
- Without two spaces, markdown wraps lines together into one long unreadable line
- Example: "│  ├─ ⚙️ **Feature Name**  " (note two spaces after last **)
- Example: "│  │  ├─ 📝 Story name  " (note two spaces after story name)
- EVERY line in tree structure hierarchy needs two trailing spaces

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

AFTER GENERATION/CORRECTION:
- Call sync_stories_from_increments_to_map(solution_dir) to sync detailed story enumeration from increments file to main story map
- This ensures both files match exactly - if stories are enumerated in increments, they must be enumerated identically in story map

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

# 1.3.2 Wrap StoryDiscoveryCommand with code augmentation
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
    
    def correct(self, chat_context: str = ""):
        """Correct story map based on validation results and sync from increments"""
        from pathlib import Path
        
        # Get solution directory from content path
        content_path = Path(self._inner_command.content.file_path)
        
        if content_path.name.endswith('-story-map.md'):
            # This is the main story map in map/ folder
            # Path structure: <solution>/docs/stories/map/story-map.md
            # So go up 4 levels: file -> map -> stories -> docs -> solution
            solution_dir = content_path.parent.parent.parent.parent
        else:
            # Try to find solution dir
            solution_dir = content_path.parent
            while solution_dir.name != 'stories' and solution_dir.parent != solution_dir:
                solution_dir = solution_dir.parent
            if solution_dir.name == 'stories':
                solution_dir = solution_dir.parent.parent
        
        # NOTE: Automated sync is complex and fragile due to tree structure parsing.
        # AI Agent is better suited for this task as it understands context and intent.
        # 
        # Commented out automated sync - AI agent will handle manually:
        # features_synced = sync_stories_from_increments_to_map(solution_dir, verbose=True)
        
        # Return prompt for AI agent to manually sync
        map_file = solution_dir / "docs" / "stories" / "map"
        inc_file = solution_dir / "docs" / "stories" / "increments"
        
        # Find the actual files
        map_path = None
        inc_path = None
        for f in map_file.glob("*story-map.md"):
            if "increments" not in f.name:
                map_path = f
                break
        for f in inc_file.glob("*increments.md"):
            inc_path = f
            break
        
        prompt = f"""
================================================================================
STORY DISCOVERY CORRECTION - Manual Sync Required
================================================================================

The discovery phase has generated exhaustive story decomposition in the increments 
document. Both documents need to be IN SYNC for the increment(s) in focus.

FILES TO SYNC:
1. Story Map (hierarchical): {map_path}
2. Increments (value-organized): {inc_path}

TASK FOR AI AGENT:
Update the STORY MAP document to match the INCREMENTS document for all features 
in the increment(s) marked with "EXHAUSTIVE" or "100% identified":

1. READ both documents
2. IDENTIFY features in increments marked as "EXHAUSTIVE" or with explicit story lists
3. UPDATE story map to replace (~X more stories) with actual enumerated stories
4. ENSURE both documents have identical story lists for exhaustive features
5. PRESERVE (~X stories) notation for features NOT in focus (other increments)
6. UPDATE "Source Material" section with Discovery Refinements (if not present)
7. ADD consolidation decisions to Source Material section

CONSOLIDATION RULES:
- Same logic/formula/algorithm → Consolidate into ONE story
- Different logic/rules/state → Keep as SEPARATE stories
- Use domain expert confirmation for unclear cases

CRITICAL:
- Both documents must list identical stories for exhaustive features
- Story map shows ALL epics/features (hierarchical view)
- Increments show only increment-organized view (subset by value increment)
- Maintain tree structure formatting (│ ├─ └─ with two trailing spaces)
- Preserve "and system..." continuation lines

{chat_context if chat_context else ""}
================================================================================
"""
        print(prompt)
        return prompt

# 1.4 Story Exploration Command
# 1.4.1 Write acceptance criteria for stories with exhaustive AC decomposition
class StoryExploreCommand(Command):
    """Command for exploration - writing acceptance criteria with Domain AC and Behavioral AC"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Write acceptance criteria using Feature Overview template.

TEMPLATE TO LOAD:
- behaviors/stories/templates/feature-overview-template.md

CRITICAL - SOURCE TRACEABILITY:
1. READ "Source Material" section from story map (Discovery Refinements)
2. Check for domain map at <solution-folder>/<system-name>-domain-map.txt (if exists, load)
3. Check for domain interactions at <solution-folder>/<system-name>-domain-interactions.txt (if available)
4. AUTOMATICALLY load source material into context

PLACEHOLDERS TO FILL:
- {feature_name}: Feature being explored
- {epic_name}: Parent epic name
- {feature_purpose}: Extract from story descriptions
- {story_count}: Number of stories in feature
- {domain_concepts}: Write Core Domain Concepts (feature-scoped perspective)
- {domain_behaviors}: Write Domain Behaviors (operations on concepts)
- {domain_rules}: Write Domain Rules (formulas, constraints, validation patterns)
- {stories_with_ac}: Write AC for each story (When/Then format, NO Given)
- {consolidation_decisions}: Document consolidate/separate decisions with reasoning
- {domain_rules_referenced}: Extract formulas/rules from source material
- {source_material}: Inherit from story map, add exploration details

APPLY PRINCIPLES:
- §3.1 Feature-Scoped Domain Perspective (only facets THIS feature operates on)
- §3.1a Domain AC format (Concepts → Behaviors → Rules)
- §3.1b Behavioral AC format (When/Then, NO Given)
- §3.2 Consolidation Review (present questions to user BEFORE finalizing)

CRITICAL - CONSOLIDATION REVIEW:
Present consolidation matrix to user with questions about same/different logic.
Document assumptions about consolidation decisions.
WAIT for user answers before finalizing.

CRITICAL - CONTENT PLACEMENT:
- ALL AC in feature documents (NOT in story documents)
- Update story documents to reference feature document
- All notes, consolidation decisions, rules BELOW all acceptance criteria

Templates define structure. YOU define content following principles."""
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

# 1.4.2 Wrap StoryExploreCommand with code augmentation
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

# 1.5 Story Specification Command
# 1.5.1 Create specifications with scenarios and examples
class StorySpecificationCommand(Command):
    """Command for creating story specifications with Given/When/Then scenarios and examples"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Create story specification scenarios with Given/When/Then structure.

Fill in Scenarios section of story documents with detailed Given/When/Then scenarios.
Use Background for repeated Given steps. Use Scenario Outline for parameterized scenarios.
Cover happy path, edge cases, and error cases. Use proper Gherkin keywords: Given/When/Then/And/But.

See prompts file for detailed scope detection and generation instructions.
Include principles from the rule file (Section 4: Specification Scenarios Principles)."""
        
        # Load prompts from file
        prompts_file = Path(__file__).parent / "specification" / "story-specification-prompts.md"
        
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

# 1.5.2 Wrap StorySpecificationCommand with code augmentation
class CodeAugmentedStorySpecificationCommand(CodeAugmentedCommand):
    """Wrapper for StorySpecificationCommand with code validation"""
    
    def __init__(self, inner_command: StorySpecificationCommand):
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
        print("Commands: story-shape, story-arrange, story-discovery, story-explore, story-specification")
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
    elif command_type == "story-specification-scenarios" or command_type == "story-specification":
        inner_command = StorySpecificationCommand(content, base_rule)
        command = CodeAugmentedStorySpecificationCommand(inner_command)
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
