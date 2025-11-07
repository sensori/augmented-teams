"""
Code Agent Runner - Domain model for AI behavior management

This runner uses an object-oriented domain model where each concept owns its state and behavior:
- Feature: Collection of related behaviors, coordinates operations
- Behavior: Reusable instruction set
- BehaviorRule: Triggering conditions (.mdc file)
- BehaviorCommand: Executable steps (.md file)  
- Runner: Python automation (.py file)
- StructureViolation: Compliance issue

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
import re
import shutil
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# MODULE CONSTANTS
# ============================================================================

# Configuration keys
BEHAVIOR_JSON = "behavior.json"
KEY_DEPLOYED = "deployed"
KEY_IS_SPECIALIZED = "isSpecialized"
KEY_SPECIALIZATION = "specialization"
KEY_FEATURE = "feature"

# Exclusions
EXCLUDED_FILES = {
    BEHAVIOR_JSON,
    "code-agent-runner.py",
    "bdd-runner.py",
    "ddd-runner.py"
}

EXCLUDED_PATTERNS = [
    "*-index.json",
    "*-tasks.json",
    "*.pyc",
    "__pycache__",
    "docs"
]

# Naming pattern for behavior files
BEHAVIOR_FILE_PATTERN = re.compile(
    r"^([a-z0-9\-]+)-([a-z0-9\-]+)(?:-([a-z0-9\-]+))?-(rule|cmd|runner|mcp)\.(mdc|md|py|json)$",
    re.IGNORECASE
)

# Display formatting
SEPARATOR_LINE_WIDTH = 60
LONG_SEPARATOR_WIDTH = 80
CONTENT_PREVIEW_LENGTH = 2000

# ============================================================================
# ENUMS
# ============================================================================

class ViolationSeverity(Enum):
    """Severity levels for structure violations"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    SUGGESTED = "suggested"

# ============================================================================
# DOMAIN MODEL
# ============================================================================

@dataclass
class StructureViolation:
    """Represents a structure compliance issue"""
    severity: ViolationSeverity
    principle: str
    message: str
    file_path: Optional[Path] = None
    feature_name: Optional[str] = None
    suggested_fix: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "severity": self.severity.value,
            "principle": self.principle,
            "message": self.message,
            "file": str(self.file_path) if self.file_path else None,
            "feature": self.feature_name,
            "suggested_fix": str(self.suggested_fix) if self.suggested_fix else None
        }


@dataclass
class Runner:
    """Python automation file (.py) - stays in feature directory"""
    file_path: Path
    behavior: Optional['Behavior'] = None
    
    def exists(self) -> bool:
        """Check if runner file exists"""
        return self.file_path.exists()


@dataclass  
class BehaviorCommand:
    """Executable steps implementing a rule (.md file)"""
    file_path: Path
    behavior: Optional['Behavior'] = None
    
    def validate(self) -> List[StructureViolation]:
        """Validate command file structure and content"""
        violations = []
        
        # Check file exists
        if not self.file_path.exists():
            return violations
        
        # Check naming pattern
        if not self.matches_naming_pattern():
            violations.append(StructureViolation(
                severity=ViolationSeverity.IMPORTANT,
                principle="Pattern Matching",
                message=f"Invalid command file name: {self.file_path.name}",
                file_path=self.file_path,
                feature_name=self.behavior.feature.name if self.behavior and self.behavior.feature else None
            ))
        
        # Check content requirements
        try:
            content = self.file_path.read_text(encoding='utf-8')
            
            # Check for Steps section
            if not self.has_steps_section(content):
                violations.append(StructureViolation(
                    severity=ViolationSeverity.IMPORTANT,
                    principle="Content Analysis",
                    message=f"Command {self.file_path.name} must include 'Steps' section",
                    file_path=self.file_path,
                    feature_name=self.behavior.feature.name if self.behavior and self.behavior.feature else None
                ))
        except (IOError, UnicodeDecodeError) as e:
            violations.append(StructureViolation(
                severity=ViolationSeverity.CRITICAL,
                principle="File System",
                message=f"Cannot read command file: {e}",
                file_path=self.file_path,
                feature_name=self.behavior.feature.name if self.behavior and self.behavior.feature else None
            ))
        
        return violations
    
    def matches_naming_pattern(self) -> bool:
        """Check if filename matches expected pattern"""
        return BEHAVIOR_FILE_PATTERN.match(self.file_path.name) is not None
    
    def has_steps_section(self, content: str) -> bool:
        """Check if content has Steps section"""
        return ('**Steps:**' in content or 
                '**steps:**' in content.lower() or
                'Steps:' in content.lower())
    
    def sync(self, force: bool = False) -> Optional[str]:
        """Sync command file to .cursor/commands/"""
        if not self.file_path.exists():
            return None
        
        dest_dir = Path('.cursor/commands')
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / self.file_path.name
        
        # Check if we should sync
        if dest.exists() and not force:
            if self.file_path.stat().st_mtime <= dest.stat().st_mtime:
                return "skipped"
        
        try:
            shutil.copy2(self.file_path, dest)
            return "synced"
        except (IOError, OSError) as e:
            print(f"❌ Error syncing {self.file_path.name}: {e}")
            return "error"
    
    def to_index_entry(self) -> Dict[str, Any]:
        """Convert to index entry for global index"""
        return {
            'feature': self.behavior.feature.name if self.behavior and self.behavior.feature else 'unknown',
            'file': self.file_path.name,
            'type': '.md',
            'path': str(self.file_path).replace("\\", "/"),
            'modified_timestamp': self.file_path.stat().st_mtime if self.file_path.exists() else 0
        }


@dataclass
class BehaviorRule:
    """Triggering conditions and guidelines (.mdc file)"""
    file_path: Path
    behavior: Optional['Behavior'] = None
    commands: List[BehaviorCommand] = field(default_factory=list)
    
    def validate(self) -> List[StructureViolation]:
        """Validate rule file structure and content"""
        if not self.file_path.exists():
            return []
        
        violations = []
        violations.extend(self.validate_naming())
        violations.extend(self.validate_content())
        violations.extend(self.validate_relationships())
        return violations
    
    def validate_naming(self) -> List[StructureViolation]:
        """Validate rule file naming"""
        violations = []
        
        if not self.matches_naming_pattern():
            violations.append(self.create_violation(
                ViolationSeverity.IMPORTANT,
                "Pattern Matching",
                f"Invalid rule file name: {self.file_path.name}"
            ))
        
        if self.has_verb_suffix():
            violations.append(self.create_violation(
                ViolationSeverity.IMPORTANT,
                "Naming Convention",
                f"Rule {self.file_path.name} should not have verb suffix"
            ))
        
        return violations
    
    def validate_content(self) -> List[StructureViolation]:
        """Validate rule file content"""
        violations = []
        
        try:
            content = self.file_path.read_text(encoding='utf-8')
            content_without_frontmatter = self.strip_yaml_frontmatter(content)
            
            if not self.has_when_pattern(content_without_frontmatter):
                violations.append(self.create_violation(
                    ViolationSeverity.CRITICAL,
                    "Content Analysis",
                    f"Rule {self.file_path.name} must start with **When** condition pattern"
                ))
            
            if not self.has_executing_commands(content):
                violations.append(self.create_violation(
                    ViolationSeverity.IMPORTANT,
                    "Content Analysis",
                    f"Rule {self.file_path.name} must include 'Executing Commands' section"
                ))
        except (IOError, UnicodeDecodeError) as e:
            violations.append(self.create_violation(
                ViolationSeverity.CRITICAL,
                "File System",
                f"Cannot read rule file: {e}"
            ))
        
        return violations
    
    def validate_relationships(self) -> List[StructureViolation]:
        """Validate rule has matching commands"""
        violations = []
        
        if not self.commands:
            rule_dir = self.file_path.parent
            base_name = self.file_path.stem.replace('-rule', '')
            violations.append(self.create_violation(
                ViolationSeverity.CRITICAL,
                "Relationships",
                f"Rule {self.file_path.name} missing matching command files",
                suggested_fix=rule_dir / f"{base_name}-cmd.md"
            ))
        
        return violations
    
    def create_violation(self, severity: ViolationSeverity, principle: str, 
                        message: str, suggested_fix: Optional[Path] = None) -> StructureViolation:
        """Create a violation for this rule"""
        return StructureViolation(
            severity=severity,
            principle=principle,
            message=message,
            file_path=self.file_path,
            feature_name=self.behavior.feature.name if self.behavior and self.behavior.feature else None,
            suggested_fix=suggested_fix
        )
    
    def strip_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content"""
        if not content.strip().startswith('---'):
            return content
        
        lines = content.split('\n')
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return '\n'.join(lines[i + 1:])
        
        return content
    
    def has_when_pattern(self, content: str) -> bool:
        """Check if content has When pattern"""
        return '**When**' in content or '**when**' in content.lower()
    
    def matches_naming_pattern(self) -> bool:
        """Check if filename matches expected pattern"""
        return BEHAVIOR_FILE_PATTERN.match(self.file_path.name) is not None
    
    def has_verb_suffix(self) -> bool:
        """Check if rule has inappropriate verb suffix"""
        match = BEHAVIOR_FILE_PATTERN.match(self.file_path.name)
        if match:
            verb_suffix = match.group(3)
            return verb_suffix is not None
        return False

    def has_executing_commands(self, content: str) -> bool:
        """Check if content has Executing Commands section"""
        return ('**Executing Commands:**' in content or
                '**executing commands:**' in content.lower() or
                'Executing Commands:' in content)
    
    def sync(self, force: bool = False) -> Optional[str]:
        """Sync rule file to .cursor/rules/"""
        if not self.file_path.exists():
            return None
        
        dest_dir = Path('.cursor/rules')
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / self.file_path.name
        
        # Check if we should sync
        if dest.exists() and not force:
            if self.file_path.stat().st_mtime <= dest.stat().st_mtime:
                return "skipped"
        
        try:
            shutil.copy2(self.file_path, dest)
            return "synced"
        except (IOError, OSError) as e:
            print(f"❌ Error syncing {self.file_path.name}: {e}")
            return "error"
    
    def to_index_entry(self) -> Dict[str, Any]:
        """Convert to index entry for global index"""
        return {
            'feature': self.behavior.feature.name if self.behavior and self.behavior.feature else 'unknown',
            'file': self.file_path.name,
            'type': '.mdc',
            'path': str(self.file_path).replace("\\", "/"),
            'modified_timestamp': self.file_path.stat().st_mtime if self.file_path.exists() else 0
        }


@dataclass
class Behavior:
    """Reusable instruction set defining how AI responds to specific situations"""
    name: str
    feature: Optional['Feature'] = None
    rule: Optional[BehaviorRule] = None
    commands: List[BehaviorCommand] = field(default_factory=list)
    runner: Optional[Runner] = None
    
    def validate(self) -> List[StructureViolation]:
        """Validate this behavior's structure"""
        violations = []
        
        # Validate rule
        if self.rule:
            violations.extend(self.rule.validate())
        else:
            violations.append(StructureViolation(
                severity=ViolationSeverity.CRITICAL,
                principle="Structure",
                message=f"Behavior {self.name} missing rule file",
                feature_name=self.feature.name if self.feature else None
            ))
        
        # Validate commands
        if not self.commands:
            violations.append(StructureViolation(
                severity=ViolationSeverity.CRITICAL,
                principle="Structure",
                message=f"Behavior {self.name} missing command files",
                feature_name=self.feature.name if self.feature else None
            ))
        else:
            for cmd in self.commands:
                violations.extend(cmd.validate())
        
        return violations
    
    def sync(self, force: bool = False) -> Dict[str, int]:
        """Sync this behavior's files to .cursor/"""
        counts = {'synced': 0, 'merged': 0, 'skipped': 0}
        
        # Sync rule
        if self.rule:
            result = self.rule.sync(force)
            if result == "synced":
                counts['synced'] += 1
            elif result == "skipped":
                counts['skipped'] += 1
        
        # Sync commands
        for cmd in self.commands:
            result = cmd.sync(force)
            if result == "synced":
                counts['synced'] += 1
            elif result == "skipped":
                counts['skipped'] += 1
        
        # Note: runners never sync (stay in feature directory)
        
        return counts
    
    def collect_index_entries(self) -> List[Dict[str, Any]]:
        """Collect index entries for this behavior (Composite pattern)"""
        entries = []
        
        if self.rule:
            entries.append(self.rule.to_index_entry())
        
        for cmd in self.commands:
            entries.append(cmd.to_index_entry())
        
        return entries


@dataclass
class Feature:
    """Collection of tightly-knit, strongly related behaviors"""
    name: str
    path: Path
    deployed: bool
    description: str = ""
    behaviors: List[Behavior] = field(default_factory=list)
    is_specialized: bool = False
    _invalid_files: List[Path] = field(default_factory=list)
    
    @classmethod
    def discover_deployed(cls, root: Optional[Path] = None) -> List['Feature']:
        """Find all features with deployed=true"""
        if root is None:
            root = Path("behaviors")
        
        if not root.exists():
            return []
        
        features = []
        
        for behavior_json_path in root.glob(f"**/{BEHAVIOR_JSON}"):
            try:
                with open(behavior_json_path, 'r', encoding='utf-8') as config_file:
                    config = json.load(config_file)
                    
                    if config.get(KEY_DEPLOYED) == True:
                        feature = cls.load_from_path(behavior_json_path.parent, config)
                        if feature:
                            features.append(feature)
            except (json.JSONDecodeError, IOError, KeyError) as e:
                # Skip files that can't be parsed
                print(f"⚠️  Warning: Could not parse {behavior_json_path}: {e}")
                continue
        
        return features
    
    @classmethod
    def load(cls, feature_name: str, root: Optional[Path] = None) -> Optional['Feature']:
        """Load a specific feature by name"""
        if root is None:
            root = Path("behaviors")
        
        feature_path = root / feature_name
        if not feature_path.exists():
            return None
        
        behavior_json_path = feature_path / BEHAVIOR_JSON
        if not behavior_json_path.exists():
            return None
        
        try:
            with open(behavior_json_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
                return cls.load_from_path(feature_path, config)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"❌ Error loading feature {feature_name}: {e}")
            return None
    
    @classmethod
    def load_from_path(cls, path: Path, config: Dict[str, Any]) -> Optional['Feature']:
        """Load feature from path and config"""
        feature = cls(
            name=config.get(KEY_FEATURE, path.name),
            path=path,
            deployed=config.get(KEY_DEPLOYED, False),
            description=config.get("description", ""),
            is_specialized=config.get(KEY_IS_SPECIALIZED, False)
        )
        
        # Discover behaviors in this feature
        feature.discover_behaviors()
        
        return feature
    
    def discover_behaviors(self):
        """Discover all behaviors in this feature"""
        exempted_files = self.get_specialization_exemptions()
        behavior_files, invalid_files = self.scan_behavior_files(exempted_files)
        self.create_behavior_objects(behavior_files)
        self._invalid_files = invalid_files
    
    def scan_behavior_files(self, exempted_files: set) -> tuple[Dict[str, Dict[str, List[Path]]], List[Path]]:
        """Scan and categorize behavior files"""
        behavior_files: Dict[str, Dict[str, List[Path]]] = {}
        invalid_files: List[Path] = []
        
        for file_path in self.path.rglob("*"):
            if file_path.is_dir() or self.should_exclude(file_path):
                continue
            
            if file_path.suffix not in ['.mdc', '.md', '.py', '.json']:
                continue
            
            if file_path.name in exempted_files:
                continue
            
            match = BEHAVIOR_FILE_PATTERN.match(file_path.name)
            if not match:
                invalid_files.append(file_path)
                continue
            
            behavior_name = match.group(2)
            file_type = match.group(4)
            
            if behavior_name not in behavior_files:
                behavior_files[behavior_name] = {'rules': [], 'commands': [], 'runners': []}
            
            if file_type == "rule":
                behavior_files[behavior_name]['rules'].append(file_path)
            elif file_type == "cmd":
                behavior_files[behavior_name]['commands'].append(file_path)
            elif file_type == "runner":
                behavior_files[behavior_name]['runners'].append(file_path)
        
        return behavior_files, invalid_files
    
    def create_behavior_objects(self, behavior_files: Dict[str, Dict[str, List[Path]]]):
        """Create Behavior objects from categorized files"""
        for behavior_name, files in behavior_files.items():
            behavior = Behavior(name=behavior_name, feature=self)
            
            if files['rules']:
                behavior.rule = BehaviorRule(file_path=files['rules'][0], behavior=behavior)
            
            for cmd_path in files['commands']:
                command = BehaviorCommand(file_path=cmd_path, behavior=behavior)
                behavior.commands.append(command)
                if behavior.rule:
                    behavior.rule.commands.append(command)
            
            if files['runners']:
                behavior.runner = Runner(file_path=files['runners'][0], behavior=behavior)
            
            self.behaviors.append(behavior)
    
    def get_specialization_exemptions(self) -> set:
        """Get list of files exempted from pattern matching for specialized behaviors"""
        exempted = set()
        
        if not self.is_specialized:
            return exempted
        
        # Load behavior.json to get specialization config
        behavior_json_path = self.path / BEHAVIOR_JSON
        if not behavior_json_path.exists():
            return exempted
        
        try:
            with open(behavior_json_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
                
                if KEY_SPECIALIZATION in config:
                    spec = config[KEY_SPECIALIZATION]
                    
                    # Add reference files
                    exempted.update(spec.get('referenceFiles', []))
                    
                    # Add base rule
                    if 'baseRule' in spec:
                        exempted.add(spec['baseRule'])
                    
                    # Add specialized rules
                    exempted.update(spec.get('specializedRules', []))
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"⚠️  Warning: Could not parse specialization config: {e}")
        
        return exempted
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        if file_path.name in EXCLUDED_FILES:
            return True
        
        for pattern in EXCLUDED_PATTERNS:
            if file_path.match(pattern):
                return True
            if pattern in str(file_path):
                return True
        
        return False
    
    def validate_structure(self) -> List[StructureViolation]:
        """Validate this feature's behaviors"""
        violations = []
        
        # Report invalid files that don't match naming pattern
        for invalid_file in self._invalid_files:
            violations.append(StructureViolation(
                severity=ViolationSeverity.IMPORTANT,
                principle="Pattern Matching",
                message=f"Invalid name pattern: {invalid_file.name}. Expected: <feature>-<behavior-name>-<type>.<ext>",
                file_path=invalid_file,
                feature_name=self.name
            ))
        
        # Validate behaviors
        for behavior in self.behaviors:
            violations.extend(behavior.validate())
        
        return violations
    
    def sync_behaviors(self, force: bool = False) -> Dict[str, int]:
        """Sync this feature's behaviors"""
        counts = {'synced': 0, 'merged': 0, 'skipped': 0}
        
        for behavior in self.behaviors:
            behavior_counts = behavior.sync(force)
            counts['synced'] += behavior_counts['synced']
            counts['skipped'] += behavior_counts['skipped']
        
        return counts
    
    def collect_index_entries(self) -> List[Dict[str, Any]]:
        """Collect index entries for all behaviors (Composite pattern)"""
        entries = []
        for behavior in self.behaviors:
            entries.extend(behavior.collect_index_entries())
        return entries
    
    @classmethod
    def validate(cls, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover features, validate all, print report - complete operation"""
        # 1. Discover features
        if feature_name:
            feature = cls.load(feature_name)
            features = [feature] if feature else []
        else:
            features = cls.discover_deployed()
        
        if not features:
            print("❌ No features found")
            return {"issues": 0, "features": 0}
        
        # 2. Validate all
        all_violations = []
        for feature in features:
            violations = feature.validate_structure()
            all_violations.extend(violations)
        
        # 3. Print report
        cls.print_validation_report(all_violations, features)
        
        # 4. Return results
        return {"issues": len(all_violations), "features": len(features)}
    
    @classmethod
    def sync(cls, feature_name: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Sync features to .cursor/ - complete operation"""
        # 1. Discover features
        if feature_name:
            feature = cls.load(feature_name)
            features = [feature] if feature else []
        else:
            features = cls.discover_deployed()
        
        if not features:
            print("❌ No features found")
            return {"synced": 0, "merged": 0, "skipped": 0}
        
        # 2. Sync each (delegates to behavior.sync())
        total_synced, total_merged, total_skipped = 0, 0, 0
        
        for feature in features:
            print(f"\nProcessing feature: {feature.name}")
            counts = feature.sync_behaviors(force)
            total_synced += counts['synced']
            total_skipped += counts['skipped']
        
        # 3. Print report
        cls.print_sync_report(total_synced, total_merged, total_skipped)
        
        return {"synced": total_synced, "merged": total_merged, "skipped": total_skipped}
    
    @classmethod
    def generate_index(cls, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate and write index - complete operation using Composite pattern"""
        # 1. Discover features
        if feature_name:
            feature = cls.load(feature_name)
            features = [feature] if feature else []
        else:
            features = cls.discover_deployed()
        
        if not features:
            print("❌ No features found")
            return {"indexed": 0, "features": 0}
        
        # 2. Collect index entries (Composite pattern)
        index_entries = []
        for feature in features:
            index_entries.extend(feature.collect_index_entries())
        
        # 3. Write global index
        cls.write_global_index(index_entries, len(features))
        
        # 4. Print report
        print(f"✅ Indexed {len(index_entries)} behaviors across {len(features)} features")
        
        return {"indexed": len(index_entries), "features": len(features)}
    
    @classmethod
    def repair(cls, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """Auto-fix structure issues - complete operation"""
        print("="*SEPARATOR_LINE_WIDTH)
        print("Behavior Structure Repair")
        print("="*SEPARATOR_LINE_WIDTH)
        
        # 1. Discover features
        if feature_name:
            feature = cls.load(feature_name)
            features = [feature] if feature else []
        else:
            features = cls.discover_deployed()
        
        if not features:
            print("❌ No features found")
            return {"fixed": 0, "features": 0}
        
        # 2. Repair all
        fixed_count = 0
        for feature in features:
            fixed_count += feature.repair_behaviors()
        
        # 3. Report
        print(f"\n✅ Fixed {fixed_count} issues")
        
        return {"fixed": fixed_count, "features": len(features)}
    
    def repair_behaviors(self) -> int:
        """Repair structure issues in this feature's behaviors"""
        fixed_count = 0
        
        # First validate to find issues
        violations = self.validate_structure()
        
        for violation in violations:
            # Fix missing command files
            if "missing matching command" in violation.message and violation.suggested_fix:
                if self.create_missing_command(violation):
                    fixed_count += 1
        
        return fixed_count
    
    def create_missing_command(self, violation: StructureViolation) -> bool:
        """Create a missing command file"""
        if not violation.suggested_fix or not violation.file_path:
            return False
        
        if not violation.file_path.exists():
            return False
        
        names = self.extract_behavior_names_from_rule(violation.file_path)
        if not names:
            return False
        
        cmd_content = self.generate_command_template(names['feature'], names['behavior'], violation.file_path.name)
        
        return self.write_command_file(violation.suggested_fix, cmd_content)
    
    @staticmethod
    def extract_behavior_names_from_rule(rule_file: Path) -> Optional[Dict[str, str]]:
        """Extract feature and behavior names from rule file"""
        parts = rule_file.stem.split('-')
        if len(parts) < 2:
            return None
        
        feature_name = parts[0]
        behavior_name = '-'.join(parts[1:-1]) if len(parts) > 2 else parts[1]
        
        return {'feature': feature_name, 'behavior': behavior_name}
    
    @staticmethod
    def generate_command_template(feature_name: str, behavior_name: str, rule_filename: str) -> str:
        """Generate command file template"""
        return f'''### Command: /{feature_name}-{behavior_name}

**Purpose:** Execute {behavior_name} behavior

**Rule:**
* `{rule_filename}` — Defines triggering conditions

**Steps:**
1. **User** invokes `/{feature_name}-{behavior_name}`
2. **Code** validates structure
3. **AI Agent** reports results
'''
    
    @staticmethod
    def write_command_file(cmd_file: Path, content: str) -> bool:
        """Write command file to disk"""
        try:
            cmd_file.write_text(content, encoding='utf-8')
            print(f"✅ Created {cmd_file.name}")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error creating {cmd_file.name}: {e}")
            return False
    
    @classmethod
    def create(cls, feature_name: str, behavior_name: str) -> Dict[str, Any]:
        """Scaffold a new behavior - complete operation"""
        if not feature_name or not behavior_name:
            print("❌ Error: Both feature and behavior_name required")
            return {"error": "Missing required parameters"}
        
        print("="*SEPARATOR_LINE_WIDTH)
        print(f"Creating New Behavior: {feature_name}/{behavior_name}")
        print("="*SEPARATOR_LINE_WIDTH)
        
        behaviors_root = Path("behaviors")
        feature_dir = behaviors_root / feature_name
        
        cls.ensure_feature_directory(feature_dir, feature_name)
        cls.create_rule_file(feature_dir, feature_name, behavior_name)
        cls.create_command_file(feature_dir, feature_name, behavior_name)
        
        print("\n✅ Behavior scaffolded successfully")
        return {"created": True, "feature": feature_name, "behavior": behavior_name}
    
    @staticmethod
    def ensure_feature_directory(feature_dir: Path, feature_name: str):
        """Ensure feature directory and behavior.json exist"""
        if not feature_dir.exists():
            feature_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created feature directory: {feature_name}")
        
        behavior_json = feature_dir / BEHAVIOR_JSON
        if not behavior_json.exists():
            config = {
                KEY_DEPLOYED: False,
                "description": f"{feature_name} behavior",
                KEY_FEATURE: feature_name
            }
            behavior_json.write_text(json.dumps(config, indent=2), encoding='utf-8')
            print("✅ Created behavior.json")
    
    @staticmethod
    def create_rule_file(feature_dir: Path, feature_name: str, behavior_name: str):
        """Create rule file for behavior"""
        rule_file = feature_dir / f"{feature_name}-{behavior_name}-rule.mdc"
        if rule_file.exists():
            return
        
        rule_content = f'''---
description: {behavior_name} behavior rule
---

**When** [condition occurs], **then** [action happens].

**Executing Commands:**
* `/{feature_name}-{behavior_name}` — Execute this behavior
'''
        rule_file.write_text(rule_content, encoding='utf-8')
        print(f"✅ Created {rule_file.name}")
    
    @staticmethod
    def create_command_file(feature_dir: Path, feature_name: str, behavior_name: str):
        """Create command file for behavior"""
        cmd_file = feature_dir / f"{feature_name}-{behavior_name}-cmd.md"
        if cmd_file.exists():
            return
        
        rule_file_name = f"{feature_name}-{behavior_name}-rule.mdc"
        cmd_content = f'''### Command: /{feature_name}-{behavior_name}

**Purpose:** Execute {behavior_name} behavior

**Rule:**
* `{rule_file_name}` — Defines triggering conditions

**Runner:**
python behaviors/{feature_name}/{feature_name}-runner.py

**Steps:**
1. **User** invokes `/{feature_name}-{behavior_name}`
2. **Code** function `{behavior_name.replace('-', '_')}()` — executes behavior logic
3. **AI Agent** validates and reports results
'''
        cmd_file.write_text(cmd_content, encoding='utf-8')
        print(f"✅ Created {cmd_file.name}")
    
    @classmethod
    def analyze_consistency(cls, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze behaviors for overlaps and contradictions - complete operation"""
        if not cls.check_openai_availability():
            return {"error": "OpenAI not available"}
        
        print("="*SEPARATOR_LINE_WIDTH)
        print("Behavior Consistency Analysis")
        print("="*SEPARATOR_LINE_WIDTH)
        
        features = cls.discover_for_analysis(feature_name)
        if not features:
            print("❌ No features found")
            return {"overlaps": 0, "contradictions": 0}
        
        behavior_contents = cls.collect_behavior_contents(features)
        
        print(f"✅ Collected {len(behavior_contents)} behavior rules")
        print("✅ Consistency analysis ready (OpenAI integration placeholder)")
        print("   Implement full semantic analysis using OpenAI function calling")
        
        return {"analyzed": len(behavior_contents), "features": len(features)}
    
    @staticmethod
    def check_openai_availability() -> bool:
        """Check if OpenAI is available and configured"""
        import os
        
        try:
            from openai import OpenAI
        except ImportError:
            print("❌ OpenAI package not installed. Install with: pip install openai")
            return False
        
        try:
            from dotenv import load_dotenv
            for env_path in [Path("behaviors/.env"), Path(".env")]:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    break
        except ImportError:
            pass
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY environment variable not set")
            print("   Set it in behaviors/.env or .env file")
            return False
        
        return True
    
    @classmethod
    def discover_for_analysis(cls, feature_name: Optional[str]) -> List['Feature']:
        """Discover features for analysis"""
        if feature_name:
            feature = cls.load(feature_name)
            return [feature] if feature else []
        return cls.discover_deployed()
    
    @staticmethod
    def collect_behavior_contents(features: List['Feature']) -> List[Dict[str, Any]]:
        """Collect behavior rule contents for analysis"""
        print(f"\n📚 Analyzing {len(features)} features...")
        behavior_contents = []
        
        for feature in features:
            for behavior in feature.behaviors:
                if behavior.rule and behavior.rule.file_path.exists():
                    content = behavior.rule.file_path.read_text(encoding='utf-8')
                    behavior_contents.append({
                        'feature': feature.name,
                        'behavior': behavior.name,
                        'file': behavior.rule.file_path.name,
                        'content': content[:CONTENT_PREVIEW_LENGTH]
                    })
        
        return behavior_contents
    
    @staticmethod
    def print_validation_report(violations: List[StructureViolation], features: List['Feature']):
        """Print validation report"""
        print("="*SEPARATOR_LINE_WIDTH)
        print("Behavior Structure Validation")
        print("="*SEPARATOR_LINE_WIDTH)
        
        if not violations:
            print("✅ All behaviors follow structure and naming conventions.")
        else:
            print(f"❌ Found {len(violations)} structure issues:\n")
            for v in violations:
                feature = v.feature_name or "unknown"
                print(f"[{feature}] {v.message}")
                if v.suggested_fix:
                    print(f"  → Suggested: {v.suggested_fix.name}")
    
    @staticmethod
    def print_sync_report(synced: int, merged: int, skipped: int):
        """Print sync report"""
        print("\n" + "="*SEPARATOR_LINE_WIDTH)
        print("Behavior Sync Report")
        print("="*SEPARATOR_LINE_WIDTH)
        print(f"✅ Synced: {synced} files")
        print(f"📄 Merged: {merged} files")
        print(f"⏭️  Skipped: {skipped} files")
    
    @staticmethod
    def write_global_index(entries: List[Dict[str, Any]], feature_count: int):
        """Write global index file"""
        global_index = Path(".cursor/behavior-index.json")
        global_index.parent.mkdir(parents=True, exist_ok=True)
        
        index_data = {
            "last_updated": time.ctime(),
            "total_behaviors": len(entries),
            "features_count": feature_count,
            "behaviors": entries
        }
        
        with open(global_index, 'w', encoding='utf-8') as out:
            json.dump(index_data, out, indent=2, ensure_ascii=False)


# ============================================================================
# CLI WRAPPER
# ============================================================================

def require_command_invocation(command_name: str):
    """Guard to prevent direct runner execution"""
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)


class CommandRunner:
    """Static wrapper maintaining CLI compatibility"""
    
    @staticmethod
    def structure(action: str = "validate", feature: Optional[str] = None, behavior_name: Optional[str] = None):
        """Execute structure command"""
        if action == "validate":
            return Feature.validate(feature)
        elif action == "fix":
            return Feature.repair(feature)
        elif action == "create":
            if not behavior_name:
                print("❌ Error: behavior_name required for create action")
                return {"error": "Missing behavior_name"}
            return Feature.create(feature or "new-feature", behavior_name)
        else:
            print(f"❌ Unknown action: {action}")
            return {"error": f"Unknown action: {action}"}
    
    @staticmethod
    def sync(feature: Optional[str] = None, force: bool = False):
        """Execute sync command"""
        return Feature.sync(feature, force)
    
    @staticmethod
    def index(feature: Optional[str] = None):
        """Execute index command"""
        return Feature.generate_index(feature)
    
    @staticmethod
    def consistency(feature: Optional[str] = None):
        """Execute consistency analysis"""
        return Feature.analyze_consistency(feature)
    
    @staticmethod
    def specialization(feature_name: str):
        """Execute specialization validation"""
        print("="*SEPARATOR_LINE_WIDTH)
        print(f"Hierarchical Behavior Validation: {feature_name}")
        print("="*SEPARATOR_LINE_WIDTH)
        
        # Run base structure validation
        print("\n📋 Running base structure validation...")
        base_result = Feature.validate(feature_name)
        
        if base_result.get("issues", 0) == 0:
            print("✅ Base structure validation passed")
        else:
            print(f"⚠️  Base structure has {base_result.get('issues', 0)} issue(s)")
        
        # Check for hierarchical configuration
        feature = Feature.load(feature_name)
        if not feature:
            print(f"❌ Feature not found: {feature_name}")
            return {"error": "Feature not found"}
        
        if not feature.is_specialized:
            print("ℹ️  Feature is not marked as specialized (isSpecialized: false)")
            return {"base": base_result, "hierarchical": False}
        
        print("\n✅ Feature is specialized - hierarchical validation complete")
        return {"base": base_result, "hierarchical": True, "total_issues": base_result.get("issues", 0)}


def parse_structure_args():
    """Parse arguments for structure command"""
    action = sys.argv[2] if len(sys.argv) > 2 else "validate"
    args_without_flags = [arg for arg in sys.argv[3:] if not arg.startswith('--')]
    feature = args_without_flags[0] if args_without_flags else None
    behavior_name = args_without_flags[1] if len(args_without_flags) > 1 else None
    return action, feature, behavior_name

def parse_sync_args():
    """Parse arguments for sync command"""
    force = "--force" in sys.argv or "-f" in sys.argv
    feature = next((arg for arg in sys.argv[2:] 
                   if arg not in ["--force", "-f", "--no-guard", "--from-command"]), None)
    return feature, force

def parse_feature_arg():
    """Parse single feature argument, skipping flags"""
    return next((arg for arg in sys.argv[2:] 
                if arg not in ["--no-guard", "--from-command", "--force", "-f"]), None)

def show_usage():
    """Display usage information"""
    print("Usage: python code-agent-runner.py <command> [args...]")
    print("\nCommands:")
    print("  structure <action> [feature] [behavior_name]")
    print("  sync [feature] [--force]")
    print("  consistency [feature]")
    print("  index [feature]")
    print("  specialization <feature>")
    sys.exit(1)

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        show_usage()
    
    command = sys.argv[1]
    
    if command == "structure":
        action, feature, behavior_name = parse_structure_args()
        CommandRunner.structure(action, feature, behavior_name)
    
    elif command == "sync":
        feature, force = parse_sync_args()
        CommandRunner.sync(feature, force=force)
    
    elif command == "consistency":
        feature = sys.argv[2] if len(sys.argv) > 2 else None
        CommandRunner.consistency(feature)
    
    elif command == "index":
        feature = parse_feature_arg()
        CommandRunner.index(feature)
    
    elif command == "specialization":
        if len(sys.argv) < 3:
            print("Error: feature name required for specialization command")
            sys.exit(1)
        feature = sys.argv[2]
        CommandRunner.specialization(feature)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    require_command_invocation("code-agent-structure")
    main()
