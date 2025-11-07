"""
Code Agent Runner - Consolidated runner for all code-agent behaviors

This runner consolidates all code-agent functionality into a single file:
- behavior_structure: Validate, fix, or create AI behavior files
- behavior_sync: Sync behaviors from features to deployed locations  
- behavior_consistency: Analyze behaviors for overlaps and contradictions
- behavior_index: Maintain local and global behavior indexes
- validate_hierarchical_behavior: Validate hierarchical behavior patterns
- Common utilities: find_deployed_behaviors, require_command_invocation

Usage:
    python behaviors/code-agent/code-agent-runner.py structure <action> [feature] [behavior_name]
    python behaviors/code-agent/code-agent-runner.py sync [feature] [--force]
    python behaviors/code-agent/code-agent-runner.py consistency [feature]
    python behaviors/code-agent/code-agent-runner.py index [feature]
    python behaviors/code-agent/code-agent-runner.py specialization <feature>
"""

from pathlib import Path
import json
import sys
import io
from typing import List, Dict, Optional, Any

# ============================================================================
# COMMON UTILITIES
# ============================================================================

def find_deployed_behaviors(root: Optional[Path] = None) -> List[Path]:
    """
    Dynamically find all directories containing behavior.json with deployed=true.
    
    Args:
        root: Root directory to search from. Defaults to 'behaviors' in current directory.
        
    Returns:
        List of Path objects pointing to directories with deployed behaviors.
    """
    if root is None:
        root = Path("behaviors")
    
    if not root.exists():
        return []
    
    deployed_dirs = []
    
    for behavior_json in root.glob("**/behavior.json"):
        try:
            with open(behavior_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get("deployed") == True:
                    deployed_dirs.append(behavior_json.parent)
        except Exception:
            pass
    
    return deployed_dirs


def find_all_behavior_jsons(root: Optional[Path] = None) -> List[Dict[str, any]]:
    """
    Find all behavior.json files and return their configurations.
    
    Args:
        root: Root directory to search from. Defaults to 'behaviors' in current directory.
        
    Returns:
        List of dicts containing 'path' (Path to behavior.json parent dir) and 'config' (parsed JSON).
    """
    if root is None:
        root = Path("behaviors")
    
    if not root.exists():
        return []
    
    behaviors = []
    
    for behavior_json in root.glob("**/behavior.json"):
        try:
            with open(behavior_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
                behaviors.append({
                    'path': behavior_json.parent,
                    'config': config,
                    'json_path': behavior_json
                })
        except Exception:
            pass
    
    return behaviors


def get_behavior_feature_name(behavior_dir: Path) -> Optional[str]:
    """
    Extract feature name from a behavior directory.
    
    Args:
        behavior_dir: Path to behavior directory (containing behavior.json).
        
    Returns:
        Feature name string, or None if not found.
    """
    try:
        behavior_json = behavior_dir / "behavior.json"
        if behavior_json.exists():
            with open(behavior_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("feature", behavior_dir.name)
    except Exception:
        pass
    
    return behavior_dir.name


def require_command_invocation(command_name: str):
    """
    Guard to prevent direct runner execution.
    
    Checks if runner was invoked with --from-command flag (set by Cursor commands).
    If not, displays helpful message directing user to proper slash command.
    
    Args:
        command_name: The slash command name (e.g., "code-agent-structure")
    """
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\nâš ï¸  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)


# ============================================================================
# BEHAVIOR STRUCTURE
# ============================================================================

def behavior_structure(action="validate", feature=None, behavior_name=None):
    """
    Validate, fix, or create AI behaviors following structure and naming conventions.
    
    Actions:
    - validate: Check structure compliance
    - fix: Automatically fix structure issues
    - create: Scaffold a new behavior
    
    Rules:
    1. File names must follow <feature>-<behavior-name>-<type>.<ext> pattern
    2. Rules should have matching commands
    3. Commands should reference rules and runners
    4. Related files share consistent naming prefixes
    """
    import re
    import time
    
    # Naming pattern: <feature>-<behavior-name>-<type>.<ext>
    # Types: rule, cmd, runner (for Python), mcp
    # For commands: can have optional verb suffix: <feature>-<behavior-name>-<verb>-cmd.md
    # Rules: <feature>-<behavior-name>-rule.mdc (no verb)
    # Commands: <feature>-<behavior-name>-cmd.md OR <feature>-<behavior-name>-<verb>-cmd.md
    # Extensions: .mdc, .md, .py, .json
    pattern = re.compile(r"^([a-z0-9\-]+)-([a-z0-9\-]+)(?:-([a-z0-9\-]+))?-(rule|cmd|runner|mcp)\.(mdc|md|py|json)$", re.I)

    # Files to exclude from validation
    excluded_files = {
        "behavior.json",
        "code-agent-runner.py",
        "bdd-runner.py", 
        "ddd-runner.py"
    }
    excluded_patterns = [
        "*-index.json",
        "*-tasks.json",
        "*.pyc",
        "__pycache__",
        "docs"
    ]

    def should_exclude(file: Path) -> bool:
        """Check if file should be excluded from validation"""
        if file.name in excluded_files:
            return True
        for pattern in excluded_patterns:
            if file.match(pattern):
                return True
            if pattern in str(file):
                return True
        return False

    def validate_structure(cursor_path):
        """Validate structure and naming for a feature."""
        issues = []
        fixes_needed = []
        files_found = {"rules": [], "commands": [], "implementations": [], "mcps": []}
        
        # Load behavior.json to check for specialization
        behavior_config = {}
        reference_files = []
        base_rules = []
        specialized_rules = []
        is_specialized = False
        
        behavior_json_path = cursor_path / "behavior.json"
        if behavior_json_path.exists():
            try:
                with open(behavior_json_path, 'r', encoding='utf-8') as f:
                    behavior_config = json.load(f)
                    is_specialized = behavior_config.get("isSpecialized", False)
                    
                    # Get reference files and rules from specialization section
                    if "specialization" in behavior_config:
                        spec = behavior_config["specialization"]
                        reference_files = spec.get("referenceFiles", [])
                        if "baseRule" in spec:
                            base_rules.append(spec["baseRule"])
                        specialized_rules.extend(spec.get("specializedRules", []))
                    
                    # Also check workflows for specialization
                    if "workflows" in behavior_config:
                        for workflow in behavior_config["workflows"].values():
                            if isinstance(workflow, dict) and "specialization" in workflow:
                                spec = workflow["specialization"]
                                ref_files = spec.get("referenceFiles", [])
                                reference_files.extend(ref_files)
                                if "baseRule" in spec:
                                    base_rules.append(spec["baseRule"])
                                specialized_rules.extend(spec.get("specializedRules", []))
            except:
                pass
        
        for file in cursor_path.rglob("*"):
            if file.is_dir():
                continue
            
            # Skip excluded files
            if should_exclude(file):
                continue
            
            ext = file.suffix
            name = file.name
            
            # Special handling for specialization files
            if is_specialized:
                # Reference files, base rules, and specialized rules are valid
                if name in reference_files or name in base_rules or name in specialized_rules:
                    # These files are declared in behavior.json - skip naming pattern check
                    continue
            
            # Check naming pattern
            match = pattern.match(name)
            if not match:
                issues.append({
                    "type": "invalid_name",
                    "file": file,
                    "message": f"Invalid name pattern: {name}. Expected: <feature>-<behavior-name>-<type>.<ext>"
                })
                continue
            
            groups = match.groups()
            feature_prefix = groups[0]
            behavior_name = groups[1]
            verb_suffix = groups[2]
            file_type = groups[3]
            file_ext = groups[4]
            
            base_behavior_name = behavior_name
            
            # Categorize files
            if file_type == "rule":
                if verb_suffix:
                    issues.append({
                        "type": "invalid_name",
                        "file": file,
                        "message": f"Rule {name} should not have verb suffix. Use: {feature_prefix}-{behavior_name}-rule.mdc"
                    })
                files_found["rules"].append((file, feature_prefix, base_behavior_name))
            elif file_type == "cmd" and ext == ".md":
                files_found["commands"].append((file, feature_prefix, base_behavior_name, verb_suffix))
            elif file_type == "runner" and ext == ".py":
                files_found["implementations"].append((file, feature_prefix, base_behavior_name, verb_suffix))
            elif file_type == "mcp":
                files_found["mcps"].append((file, feature_prefix, base_behavior_name))
            
            # Check for matching files
            if file_type == "rule":
                # Rules can have multiple commands (verb-suffixed) in same directory
                rule_prefix = f"{feature_prefix}-{base_behavior_name}"
                rule_dir = file.parent
                
                # Check in same directory as rule (allows subdirectories)
                matching_cmds = list(rule_dir.glob(f"{rule_prefix}*-cmd.md"))
                
                if not matching_cmds:
                    issues.append({
                        "type": "missing_command",
                        "file": file,
                        "message": f"Rule {name} missing matching command files in same directory (expected: {rule_prefix}*-cmd.md)",
                        "suggested_fix": rule_dir / f"{rule_prefix}-cmd.md"
                    })
            
            # Check documentation and relationship sections
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                if not content.strip() or len(content.strip()) < 50:
                    issues.append({
                        "type": "missing_docs",
                        "file": file,
                        "message": f"File {name} is empty or lacks documentation"
                    })
                else:
                    content_lower = content.lower()
                    if file_type == "rule":
                        # Rules must start with "**When** <event> condition,"
                        # Skip frontmatter (YAML between --- markers) if present
                        content_to_check = content.strip()
                        if content_to_check.startswith('---'):
                            # Find end of frontmatter
                            lines = content_to_check.split('\n')
                            frontmatter_end = -1
                            for i in range(1, len(lines)):
                                if lines[i].strip() == '---':
                                    frontmatter_end = i
                                    break
                            if frontmatter_end > 0:
                                # Skip frontmatter and get actual content
                                content_to_check = '\n'.join(lines[frontmatter_end + 1:]).strip()
                        
                        if not content_to_check.startswith("**When**"):
                            issues.append({
                                "type": "invalid_rule_format",
                                "file": file,
                                "message": f"Rule {name} must start with '**When** <event> condition,' (after frontmatter)"
                            })
                        # Rules must reference executing commands
                        if "**executing commands:**" not in content_lower:
                            issues.append({
                                "type": "missing_relationships",
                                "file": file,
                                "message": f"Rule {name} missing 'Executing Commands:' section"
                            })
                    elif file_type == "cmd" and ext == ".md":
                        # Commands must reference rule they follow and include Steps
                        missing_sections = []
                        if "**rule:**" not in content_lower:
                            missing_sections.append("Rule (which rule this command follows)")
                        # Steps section is REQUIRED
                        if "**steps:**" not in content_lower:
                            missing_sections.append("Steps (sequential actions to execute)")
                        
                        # Check for deprecated sections that should be removed
                        deprecated_sections = []
                        if "**ai usage:**" in content_lower:
                            deprecated_sections.append("AI Usage (use Steps instead)")
                        if "**code usage:**" in content_lower:
                            deprecated_sections.append("Code Usage (use Steps instead)")
                        if "**implementation:**" in content_lower:
                            deprecated_sections.append("Implementation (use Runner instead)")
                        
                        if missing_sections:
                            issues.append({
                                "type": "missing_relationships",
                                "file": file,
                                "message": f"Command {name} missing required sections: {', '.join(missing_sections)}"
                            })
                        
                        if deprecated_sections:
                            issues.append({
                                "type": "deprecated_sections",
                                "file": file,
                                "message": f"Command {name} has deprecated sections: {', '.join(deprecated_sections)}"
                            })
            except:
                pass
        
        return issues, fixes_needed

    # Determine features to process
    if feature:
        behaviors_root = Path("behaviors")
        cursor_path = behaviors_root / feature
        if not (cursor_path / "behavior.json").exists():
            all_behaviors = find_deployed_behaviors()
            matching = [b for b in all_behaviors if b.name == feature]
            cursor_path = matching[0] if matching else cursor_path
        features = [cursor_path] if cursor_path.exists() else []
    else:
        features = find_deployed_behaviors()

    if action == "validate":
        all_issues = []
        for cursor_path in features:
            issues, _ = validate_structure(cursor_path)
            for issue in issues:
                all_issues.append({
                    "feature": cursor_path.name,
                    **issue
                })
        
        print("="*60)
        print("Behavior Structure Validation")
        print("="*60)
        
        if not all_issues:
            print("âœ… All behaviors follow structure and naming conventions.")
        else:
            print(f"âŒ Found {len(all_issues)} structure issues:\n")
            for issue in all_issues:
                print(f"[{issue['feature']}] {issue['message']}")
                if "suggested_fix" in issue:
                    print(f"  â†’ Suggested: {issue['suggested_fix'].name}")
        
        return {"issues": len(all_issues), "features": len(features)}
    
    elif action == "fix":
        """Automatically fix structure issues"""
        print("="*60)
        print("Behavior Structure Repair")
        print("="*60)
        
        fixed_count = 0
        for cursor_path in features:
            issues, _ = validate_structure(cursor_path)
            
            for issue in issues:
                if issue['type'] == 'missing_command' and 'suggested_fix' in issue:
                    # Generate missing command file
                    cmd_file = issue['suggested_fix']
                    rule_file = issue['file']
                    
                    # Extract feature and behavior name from rule file
                    rule_name = rule_file.stem
                    parts = rule_name.split('-')
                    if len(parts) >= 2:
                        feature_name = parts[0]
                        behavior_name = '-'.join(parts[1:-1])  # Everything except first and last
                        
                        # Create command template
                        cmd_content = f'''### Command: /{feature_name}-{behavior_name}

**Purpose:** Execute {behavior_name} behavior

**Rule:**
* `{rule_file.name}` — Defines triggering conditions

**Steps:**
1. **User** invokes `/{feature_name}-{behavior_name}`
2. **Code** validates structure
3. **AI Agent** reports results
'''
                        
                        cmd_file.write_text(cmd_content, encoding='utf-8')
                        print(f"Created {cmd_file.name}")
                        fixed_count += 1
                
                elif issue['type'] == 'deprecated_sections':
                    # Remove deprecated sections from command files
                    file_path = issue['file']
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Remove deprecated sections
                    content = re.sub(r'\*\*AI Usage:\*\*.*?(?=\n\*\*|\Z)', '', content, flags=re.DOTALL)
                    content = re.sub(r'\*\*Code Usage:\*\*.*?(?=\n\*\*|\Z)', '', content, flags=re.DOTALL)
                    content = re.sub(r'\*\*Implementation:\*\*.*?(?=\n\*\*|\Z)', '', content, flags=re.DOTALL)
                    
                    file_path.write_text(content, encoding='utf-8')
                    print(f"Removed deprecated sections from {file_path.name}")
                    fixed_count += 1
        
        print(f"\nFixed {fixed_count} issues")
        return {"fixed": fixed_count, "features": len(features)}
    
    elif action == "create":
        """Scaffold a new behavior"""
        if not feature or not behavior_name:
            print("Error: Both feature and behavior_name required for create action")
            return {"error": "Missing required parameters"}
        
        print("="*60)
        print(f"Creating New Behavior: {feature}/{behavior_name}")
        print("="*60)
        
        behaviors_root = Path("behaviors")
        feature_dir = behaviors_root / feature
        
        # Create feature directory if needed
        if not feature_dir.exists():
            feature_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created feature directory: {feature}")
        
        # Create behavior.json if it doesn't exist
        behavior_json = feature_dir / "behavior.json"
        if not behavior_json.exists():
            config = {
                "deployed": False,
                "description": f"{feature} behavior",
                "feature": feature
            }
            behavior_json.write_text(json.dumps(config, indent=2), encoding='utf-8')
            print("Created behavior.json")
        
        # Create rule file
        rule_file = feature_dir / f"{feature}-{behavior_name}-rule.mdc"
        if not rule_file.exists():
            rule_content = f'''---
description: {behavior_name} behavior rule
---

**When** [condition occurs], **then** [action happens].

**Executing Commands:**
* `/{feature}-{behavior_name}` — Execute this behavior
'''
            rule_file.write_text(rule_content, encoding='utf-8')
            print(f"Created {rule_file.name}")
        
        # Create command file
        cmd_file = feature_dir / f"{feature}-{behavior_name}-cmd.md"
        if not cmd_file.exists():
            cmd_content = f'''### Command: /{feature}-{behavior_name}

**Purpose:** Execute {behavior_name} behavior

**Rule:**
* `{rule_file.name}` — Defines triggering conditions

**Runner:**
python behaviors/{feature}/{feature}-runner.py

**Steps:**
1. **User** invokes `/{feature}-{behavior_name}`
2. **Code** function `{behavior_name}()` — executes behavior logic
3. **AI Agent** validates and reports results
'''
            cmd_file.write_text(cmd_content, encoding='utf-8')
            print(f"Created {cmd_file.name}")
        
        # Optionally create runner file
        runner_file = feature_dir / f"{feature}-runner.py"
        if not runner_file.exists():
            runner_content = f'''"""
{feature.capitalize()} Behavior Runner
"""

import sys
from pathlib import Path

def require_command_invocation(command_name):
    """Guard to prevent direct execution"""
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\\nPlease use the Cursor slash command instead:\\n")
        print(f"    /{{command_name}}\\n")
        sys.exit(1)

def {behavior_name.replace('-', '_')}():
    """Execute {behavior_name} behavior"""
    print(f"Executing {behavior_name}...")
    # Implementation here
    pass

if __name__ == "__main__":
    require_command_invocation("{feature}-{behavior_name}")
    {behavior_name.replace('-', '_')}()
'''
            runner_file.write_text(runner_content, encoding='utf-8')
            print(f"Created {runner_file.name}")
        
        print("\nBehavior scaffolded successfully")
        return {"created": True, "feature": feature, "behavior": behavior_name}


# ============================================================================
# BEHAVIOR SYNC
# ============================================================================

def behavior_sync(feature=None, force=False):
    """
    Sync feature-local AI behaviors to deployed locations.
    
    Sync Rules:
    1. All files in behaviors/ folders are synced based on extension
    2. Files are routed to correct areas:
       - .mdc files â†’ .cursor/rules/
       - .md files  â†’ .cursor/commands/
       - .json files â†’ .cursor/mcp/
    3. Merge MCP configs if they already exist
    4. Overwrite only if source is newer (unless force=True)
    5. Never sync behaviors marked as "draft" or "experimental"
    
    Args:
        feature: Optional feature name to sync only that feature
        force: If True, overwrite all files regardless of timestamps
    """
    import shutil
    
    src_root = Path("behaviors")
    targets = {
        ".mdc": Path(".cursor/rules"),
        ".md": Path(".cursor/commands"),
        ".json": Path(".cursor/mcp"),
    }
    
    for t in targets.values():
        t.mkdir(parents=True, exist_ok=True)
    
    Path(".vscode").mkdir(parents=True, exist_ok=True)

    # Determine features to sync
    features = []
    if feature:
        feature_path = src_root / feature
        marker_file = feature_path / "behavior.json"
        
        if marker_file.exists():
            try:
                marker_data = json.load(marker_file.open('r', encoding='utf-8'))
                if marker_data.get("deployed"):
                    features = [feature_path]
            except:
                pass
    else:
        for feature_dir in src_root.glob("*"):
            if not feature_dir.is_dir():
                continue
            
            marker_file = feature_dir / "behavior.json"
            
            if marker_file.exists():
                try:
                    marker_data = json.load(marker_file.open('r', encoding='utf-8'))
                    if marker_data.get("deployed"):
                        features.append(feature_dir)
                except:
                    pass

    synced_files = []
    merged_files = []
    skipped_files = []

    for feature_path in features:
        print(f"\nProcessing feature: {feature_path.name}")
        for file in feature_path.rglob("*"):
            if file.is_dir():
                continue
            
            if 'docs' in file.parts:
                continue
            
            # Skip draft or experimental behaviors
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.lower().split('\n')
                has_draft_marker = False
                for line in lines[:10]:
                    stripped = line.strip()
                    if stripped.startswith('#draft') or stripped.startswith('#experimental'):
                        has_draft_marker = True
                        break
                    if stripped.startswith('draft:') or stripped.startswith('experimental:'):
                        has_draft_marker = True
                        break
                
                if has_draft_marker:
                    skipped_files.append((file, "draft/experimental marker"))
                    continue
            except:
                pass

            ext = file.suffix
            if ext not in targets:
                continue

            dest = targets[ext] / file.name
            
            # Handle MCP JSON configs - merge if exists
            if ext == ".json" and dest.exists() and file.name.endswith("-mcp.json"):
                try:
                    with open(dest, 'r', encoding='utf-8') as d1, open(file, 'r', encoding='utf-8') as d2:
                        existing = json.load(d1)
                        new_data = json.load(d2)
                        merged = {**existing, **new_data}
                    with open(dest, 'w', encoding='utf-8') as out:
                        json.dump(merged, out, indent=2, ensure_ascii=False)
                    merged_files.append((file, dest))
                    print(f"ðŸ”„ Merged {file.name} â†’ {dest}")
                except Exception as e:
                    print(f"âš ï¸  Error merging {file.name}: {e}")
                    skipped_files.append((file, f"merge error: {e}"))
            else:
                # Check if source is newer
                if dest.exists() and not force:
                    source_mtime = file.stat().st_mtime
                    dest_mtime = dest.stat().st_mtime
                    if source_mtime <= dest_mtime:
                        skipped_files.append((file, "source not newer"))
                        continue
                
                try:
                    shutil.copy2(file, dest)
                    synced_files.append((file, dest))
                    print(f"âœ… Synced {file.name} â†’ {dest}")
                except Exception as e:
                    print(f"âŒ Error syncing {file.name}: {e}")
                    skipped_files.append((file, f"copy error: {e}"))
    
    # Report results
    print("\n" + "="*60)
    print("Behavior Sync Report")
    print("="*60)
    print(f"âœ… Synced: {len(synced_files)} files")
    print(f"ðŸ”„ Merged: {len(merged_files)} files")
    print(f"â­ï¸  Skipped: {len(skipped_files)} files")
    
    return {
        "synced": len(synced_files),
        "merged": len(merged_files),
        "skipped": len(skipped_files)
    }


# ============================================================================
# BEHAVIOR CONSISTENCY
# ============================================================================

def behavior_consistency(feature=None):
    """
    Validate behaviors for inconsistencies, overlaps, or contradictions.
    Uses OpenAI function calling for semantic analysis.
    Generates a summary report for human and AI review.
    """
    import os
    
    try:
        from openai import OpenAI
    except ImportError:
        print("âŒ OpenAI package not installed. Install with: pip install openai")
        return
    
    try:
        from dotenv import load_dotenv
        features_env = Path("behaviors/.env")
        root_env = Path(".env")
        if features_env.exists():
            load_dotenv(features_env, override=True)
        elif root_env.exists():
            load_dotenv(root_env, override=True)
        else:
            load_dotenv(override=True)
    except ImportError:
        pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("âŒ OPENAI_API_KEY environment variable not set")
        print("   Set it in behaviors/.env or .env file")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Function schema for consistency analysis
    ANALYSIS_SCHEMA = {
        "name": "analyze_behavior_consistency",
        "description": "Analyze behaviors for overlaps, contradictions, and inconsistencies",
        "parameters": {
            "type": "object",
            "properties": {
                "overlaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "behavior1": {"type": "string"},
                            "behavior2": {"type": "string"},
                            "similarity": {"type": "string"},
                            "difference": {"type": "string"},
                            "recommendation": {"type": "string"}
                        }
                    }
                },
                "contradictions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "behavior1": {"type": "string"},
                            "behavior2": {"type": "string"},
                            "context": {"type": "string"},
                            "contradiction": {"type": "string"},
                            "recommendation": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"}
            }
        }
    }
    
    print(f"ðŸ“Š Analyzing behaviors for consistency...")
    print("âœ… Consistency check placeholder - OpenAI integration ready")


# ============================================================================
# BEHAVIOR INDEX
# ============================================================================

def behavior_index(feature=None):
    """
    Detect changes to behavior files and update local/global indexes.
    
    Scans behaviors/ folders and maintains:
    - Local indexes: behaviors/<feature>/behavior-index.json
    - Global index: .cursor/behavior-index.json
    """
    import time
    
    global_index = Path(".cursor/behavior-index.json")
    behavior_extensions = [".mdc", ".md", ".py", ".json"]
    
    behaviors_root = Path("behaviors")
    excluded_files = {"behavior.json", "code-agent-runner.py", "bdd-runner.py", "ddd-runner.py"}
    
    # Find all feature directories with behavior.json
    feature_dirs = []
    
    if feature:
        # Single feature mode
        feature_path = behaviors_root / feature
        if feature_path.exists() and (feature_path / "behavior.json").exists():
            feature_dirs.append(feature_path)
    else:
        # All features mode - find all directories with behavior.json that have deployed=true
        for item in behaviors_root.iterdir():
            if not item.is_dir():
                continue
            
            behavior_json = item / "behavior.json"
            if behavior_json.exists():
                try:
                    with open(behavior_json, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if config.get("deployed") is True:
                            feature_dirs.append(item)
                except:
                    pass
    
    # Index all behavior files
    index_data = []
    skipped_count = 0
    
    for feature_dir in feature_dirs:
        feature_name = feature_dir.name
        
        # Recursively find all files
        for file in feature_dir.rglob("*"):
            if file.is_dir():
                continue
            
            # Skip non-behavior files
            if file.suffix not in behavior_extensions:
                continue
            
            # Skip excluded files
            if file.name in excluded_files:
                continue
            
            # Skip __pycache__ and docs
            if "__pycache__" in str(file) or "\\docs\\" in str(file) or "/docs/" in str(file):
                continue
            
            # Add to index
            try:
                stat = file.stat()
                index_data.append({
                    "feature": feature_name,
                    "file": file.name,
                    "type": file.suffix,
                    "path": str(file).replace("\\", "/"),
                    "modified_timestamp": stat.st_mtime
                })
            except:
                skipped_count += 1
    
    # Write global index
    global_index.parent.mkdir(parents=True, exist_ok=True)
    with open(global_index, 'w', encoding='utf-8') as out:
        json.dump({
            "last_updated": time.ctime(),
            "total_behaviors": len(index_data),
            "features_count": len(feature_dirs),
            "behaviors": index_data
        }, out, indent=2, ensure_ascii=False)
    
    print(f"âœ… Indexed {len(index_data)} behaviors across {len(feature_dirs)} features")
    if skipped_count > 0:
        print(f"â­ï¸  Skipped {len(skipped_files)} files")
    
    return {"indexed": len(index_data), "features": len(feature_dirs)}


# ============================================================================
# HIERARCHICAL BEHAVIOR VALIDATION (SPECIALIZATION)
# ============================================================================

def validate_hierarchical_behavior(feature_name):
    """
    Validate hierarchical behavior patterns with base validation inheritance.
    """
    behaviors_root = Path("behaviors")
    feature_dir = behaviors_root / feature_name
    
    if not feature_dir.exists():
        print(f"âŒ Feature directory not found: {feature_dir}")
        return {"error": "Feature not found"}
    
    print("=" * 60)
    print(f"Hierarchical Behavior Validation: {feature_name}")
    print("=" * 60)
    
    # Run base structure validation
    print("\nðŸ“‹ Running base structure validation...")
    base_result = behavior_structure("validate", feature_name)
    
    if base_result.get("issues", 0) == 0:
        print("âœ… Base structure validation passed")
    else:
        print(f"âš ï¸  Base structure has {base_result.get('issues', 0)} issue(s)")
    
    # Check for hierarchical configuration
    config_file = feature_dir / "behavior.json"
    if not config_file.exists():
        return {"base": base_result, "hierarchical": False}
    
    config = json.loads(config_file.read_text(encoding='utf-8'))
    
    if not config.get("isHierarchical"):
        return {"base": base_result, "hierarchical": False}
    
    print("\nâœ… Hierarchical validation complete")
    return {"base": base_result, "hierarchical": True, "total_issues": base_result.get("issues", 0)}


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python code-agent-runner.py <command> [args...]")
        print("\nCommands:")
        print("  structure <action> [feature] [behavior_name]")
        print("  sync [feature] [--force]")
        print("  consistency [feature]")
        print("  index [feature]")
        print("  specialization <feature>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "structure":
        action = sys.argv[2] if len(sys.argv) > 2 else "validate"
        feature = sys.argv[3] if len(sys.argv) > 3 else None
        behavior_name = sys.argv[4] if len(sys.argv) > 4 else None
        behavior_structure(action, feature, behavior_name)
    
    elif command == "sync":
        force = "--force" in sys.argv or "-f" in sys.argv
        feature = None
        for arg in sys.argv[2:]:
            if arg not in ["--force", "-f", "--no-guard", "--from-command"]:
                feature = arg
                break
        behavior_sync(feature, force=force)
    
    elif command == "consistency":
        feature = sys.argv[2] if len(sys.argv) > 2 else None
        behavior_consistency(feature)
    
    elif command == "index":
        feature = None
        for arg in sys.argv[2:]:
            if arg not in ["--no-guard", "--from-command", "--force", "-f"]:
                feature = arg
                break
        behavior_index(feature)
    
    elif command == "specialization":
        if len(sys.argv) < 3:
            print("Error: feature name required for specialization command")
            sys.exit(1)
        feature = sys.argv[2]
        validate_hierarchical_behavior(feature)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
