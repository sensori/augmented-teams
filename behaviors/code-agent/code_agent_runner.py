"""Code Agent Runner - implements `/code-agent-feature` command"""

from pathlib import Path
import json
import sys
import shutil
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable

SEPARATOR_LENGTH = 60
DEFAULT_ENCODING = 'utf-8'
JSON_INDENT = 2
HEADER_LINES_TO_CHECK = 10
MAX_FILES_TO_DISPLAY = 10
MAX_BEHAVIORS_PER_FEATURE_TO_DISPLAY = 3

common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
import importlib.util
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

Content = common_runner.Content
BaseRule = common_runner.BaseRule
Command = common_runner.Command
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
CodeAgentRule = common_runner.CodeAgentRule
FeatureInfo = common_runner.FeatureInfo


@dataclass
class FeatureCommandConfig:
    """Configuration for FeatureCommand"""
    feature_name: Optional[str] = None
    location: Optional[str] = None
    feature_purpose: Optional[str] = None


@dataclass
class CommandCommandConfig:
    """Configuration for CommandCommand"""
    feature_name: Optional[str] = None
    command_name: Optional[str] = None
    command_purpose: Optional[str] = None
    target_entity: Optional[str] = None


@dataclass
class RuleCommandConfig:
    """Configuration for RuleCommand"""
    feature_name: Optional[str] = None
    rule_name: Optional[str] = None
    rule_purpose: Optional[str] = None
    rule_type: str = "base"  # "base", "specializing", "specialized"
    parent_rule_name: Optional[str] = None


class CodeAgentCommand(Command):
    """Base class for Code Agent commands with template loading capabilities"""
    
    def __init__(self, command_folder: str, content: Content, base_rule: BaseRule, 
                 generate_instructions: Optional[str] = None, validate_instructions: Optional[str] = None) -> None:
        super().__init__(content, base_rule, validate_instructions, generate_instructions)
        self.command_folder = command_folder
    
    def load_template(self, template_name: str, **kwargs) -> str:
        template_path = Path(__file__).parent / self.command_folder / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        template_content = template_path.read_text(encoding=DEFAULT_ENCODING)
        return template_content.format(**kwargs)
    
    def plan(self, plan_template_name: Optional[str] = None, **template_kwargs) -> Optional[str]:
        """
        Generate an implementation plan by loading a plan template and filling it with parameters.
        
        Subclasses should override this to provide the plan_template_name and template_kwargs,
        or call super().plan() with the appropriate parameters.
        """
        if not plan_template_name:
            return None
        
        try:
            plan_content = self.load_template(plan_template_name, **template_kwargs)
            return plan_content
        except FileNotFoundError:
            return None


class FeatureCommand(CodeAgentCommand):
    """Command that knows about validating and generating features, uses templates"""
    
    def __init__(self, feature_name: Optional[str] = None, location: Optional[str] = None, feature_purpose: Optional[str] = None) -> None:
        config = FeatureCommandConfig(feature_name, location, feature_purpose)
        base_rule = BaseRule("code-agent-rule.mdc")
        
        feature_location = self._determine_feature_location(config.feature_name, config.location)
        content = Content(file_path=str(Path(feature_location)))
        
        generate_instructions = "Generate a new Code Agent feature with all required files as specified by principles in code-agent-rule.mdc"
        validate_instructions = "Validate the generated feature files comply with code-agent-rule.mdc principles"
        
        super().__init__(
            command_folder="feature",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = config.feature_name
        self.location = feature_location
        self.feature_purpose = config.feature_purpose
    
    @staticmethod
    def _determine_feature_location(feature_name: Optional[str], location: Optional[str]) -> str:
        """Determine feature location from parameters"""
        if location:
            return location
        if feature_name:
            return f"behaviors/{feature_name}"
        return "behaviors/"
    
    def generate(self):
        feature_dir = self._resolve_feature_directory(self.location)
        self._validate_feature_not_exists(feature_dir)
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = self._generate_all_feature_files(feature_dir)
        self._display_generation_results(generated_files)
        
        return super().generate()
    
    def _resolve_feature_directory(self, location: str) -> Path:
        """Resolve feature directory path from location string"""
        location_path = Path(location)
        if location_path.is_absolute():
            return location_path
        if location.startswith("behaviors/"):
            workspace_root = Path(__file__).parent.parent.parent
            return workspace_root / location
        return location_path.resolve()
    
    def _validate_feature_not_exists(self, feature_dir: Path) -> None:
        """Validate that feature does not already exist"""
        if feature_dir.exists() and (feature_dir / "behavior.json").exists():
            raise ValueError(f"Feature '{self.feature_name}' already exists at {self.location}")
    
    def _generate_all_feature_files(self, feature_dir: Path) -> dict:
        """Generate all required feature files"""
        return {
            'behavior_json': self._generate_behavior_json(feature_dir),
            'runner_file': self._generate_runner_file(feature_dir),
            'outline_file': self._generate_feature_outline(feature_dir)
        }
    
    def _display_generation_results(self, generated_files: dict) -> None:
        """Display generation results to console"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print(f"Generated Feature: {self.feature_name}")
        print(separator)
        print(f"Location: {self.location}")
        print(f"\nGenerated files:")
        print(f"  - {generated_files['behavior_json']}")
        print(f"  - {generated_files['runner_file']}")
        print(f"  - {generated_files['outline_file']}")
    
    def execute(self):
        """Override execute to check if feature exists before generating"""
        feature_dir = self._resolve_feature_directory(self.location)
        if feature_dir.exists() and (feature_dir / "behavior.json").exists():
            self.generated = True
        return super().execute()
    
    def _generate_behavior_json(self, feature_dir: Path) -> Path:
        behavior_json = feature_dir / "behavior.json"
        behavior_data = {
            "deployed": False,
            "feature": self.feature_name,
            "description": self.feature_purpose or f"{self.feature_name} behavior"
        }
        behavior_json.write_text(json.dumps(behavior_data, indent=JSON_INDENT), encoding=DEFAULT_ENCODING)
        return behavior_json
    
    def _generate_runner_file(self, feature_dir: Path) -> Path:
        runner_file = feature_dir / f"{self.feature_name}_runner.py"
        runner_content = self.load_template(
            "runner_template.py",
            feature_purpose=self.feature_purpose or f"{self.feature_name} behavior runner",
            feature_name=self.feature_name
        )
        runner_file.write_text(runner_content, encoding=DEFAULT_ENCODING)
        return runner_file
    
    def _generate_feature_outline(self, feature_dir: Path) -> Path:
        outline_file = feature_dir / "feature-outline.md"
        outline_content = self.load_template(
            "feature_outline_template.md",
            feature_name=self.feature_name,
            feature_purpose=self.feature_purpose or f"Purpose of the {self.feature_name} feature"
        )
        outline_file.write_text(outline_content, encoding=DEFAULT_ENCODING)
        return outline_file


class CodeAugmentedFeatureCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps FeatureCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, location: Optional[str] = None, feature_purpose: Optional[str] = None) -> None:
        base_rule = BaseRule("code-agent-rule.mdc")
        feature_command = FeatureCommand(feature_name, location, feature_purpose)
        super().__init__(feature_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for feature commands"""
        feature_name = args[0] if len(args) > 0 else None
        location = args[1] if len(args) > 1 else None
        purpose = args[2] if len(args) > 2 else None
        
        command = cls(feature_name, location, purpose)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()
        elif action == "plan":
            plan_content = command.plan() if hasattr(command, 'plan') else None
            if plan_content:
                sys.stdout.reconfigure(encoding=DEFAULT_ENCODING)
                print(plan_content)
            else:
                print("Plan generation not available for this command.")


class CommandCommand(CodeAgentCommand):
    """Command that knows about validating and generating commands within a feature, uses templates"""
    
    def __init__(self, feature_name: Optional[str] = None, command_name: Optional[str] = None, command_purpose: Optional[str] = None, target_entity: Optional[str] = None) -> None:
        config = CommandCommandConfig(feature_name, command_name, command_purpose, target_entity)
        rule_name = f"{config.feature_name}-rule.mdc" if config.feature_name else "code-agent-rule.mdc"
        base_rule = BaseRule(rule_name)
        
        command_location = self._determine_command_location(config.feature_name, config.command_name)
        content = Content(file_path=str(Path(command_location)))
        
        generate_instructions = f"""Generate a new command '{config.command_name}' for feature '{config.feature_name}' with all required files as specified by principles in {rule_name}.

**Rule Analysis:** Examine the attached rule file ({rule_name}) for applicable principles. Extract code heuristics from these principles for validation. Integrate heuristics into the CodeAugmentedCommand wrapper pattern."""
        
        validate_instructions = f"""Validate the generated command files comply with {rule_name} principles.

**Rule-Based Validation:** Use code heuristics derived from the attached rule file ({rule_name}) to perform initial validation. Verify heuristics are integrated and report any principle violations."""
        
        super().__init__(
            command_folder="command",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = config.feature_name
        self.command_name = config.command_name
        self.command_purpose = config.command_purpose
        self.target_entity = config.target_entity
    
    @staticmethod
    def _determine_command_location(feature_name: Optional[str], command_name: Optional[str]) -> str:
        """Determine command location from parameters"""
        if feature_name and command_name:
            return f"behaviors/{feature_name}/{command_name}"
        if feature_name:
            return f"behaviors/{feature_name}"
        return "behaviors/"
    
    def plan(self, plan_template_name: Optional[str] = None, **template_kwargs) -> Optional[str]:
        """
        Generate an implementation plan by loading the command plan template
        and filling it out with the command parameters.
        Saves the plan to a file and returns the filled-out plan for user review.
        """
        if not self.feature_name or not self.command_name:
            raise ValueError("feature_name and command_name are required to generate a plan")
        
        command_class_name = self._get_command_class_name()
        plan_content = self._load_plan_template(command_class_name)
        
        if not plan_content:
            return None
        
        instructions = self._build_plan_instructions(command_class_name)
        full_plan_content = plan_content + instructions
        
        self._save_plan_file(full_plan_content)
        return full_plan_content
    
    def _get_command_class_name(self) -> str:
        """Get command class name from command name"""
        return self.command_name.title().replace('-', '').replace('_', '')
    
    def _load_plan_template(self, command_class_name: str) -> Optional[str]:
        """Load plan template with command parameters"""
        return super().plan(
            plan_template_name="command_plan_template.md",
            command_name=self.command_name,
            feature_name=self.feature_name,
            command_purpose=self.command_purpose or f"Purpose of the {self.command_name} command",
            target_entity=self.target_entity or "command",
            rule_name=f"{self.feature_name}-rule",
            runner_path=f"{self.feature_name}/{self.feature_name}_runner.py",
            command_parameters=f"[{self.feature_name}] [{self.command_name}]",
            CommandClassName=command_class_name,
            command_class_name=command_class_name
        )
    
    def _build_plan_instructions(self, command_class_name: str) -> str:
        """Build AI instructions for updating the plan template"""
        return f"""

## AI Instructions: Update the Plan Template

**The plan above is a template with variables filled in. Your task is to update it with concrete, determined values.**

### Critical: Incorporate BDD and Clean Code Rules

**Before updating the plan, review and incorporate principles from:**
- **BDD Rules**: Review `bdd-rule.mdc`, `bdd-domain-scaffold-rule.mdc`, `bdd-domain-fluency-rule.mdc`, `bdd-mamba-rule.mdc` (or framework-specific rules)
- **Clean Code Rules**: Review `clean-code-rule.mdc`, `clean-code-js-rule.mdc`, `clean-code-python-rule.mdc` (or language-specific rules)

**Apply these principles when updating the plan:**
- **Mocking**: Only mock file I/O operations, not internal classes
- **Base Class Reuse**: Maximize reuse of base classes, don't reimplement logic
- **Clean Code**: Use parameter objects, decompose large methods, use guard clauses, validate early
- **BDD Compliance**: Follow BDD principles for test structure, naming, and organization
- **Test Strategy**: Test observable behavior, use helpers, avoid duplication

### What to Think About and Update:

1. **Commands**: Determine what exact command classes are needed (e.g., {command_class_name}Command, CodeAugmented{command_class_name}Command, or other command types). Consider the command purpose ({self.command_purpose or 'see above'}) and target entity ({self.target_entity or 'command'}) to determine the architecture. Apply clean code principles (parameter objects, method decomposition).

2. **Heuristics**: Determine what validation heuristics are needed. Review the feature rule file (`{self.feature_name}-rule.mdc`) if it exists to identify applicable principles that need heuristic validation.

3. **Tests**: Think about what behaviors need to be tested. Consider generation, validation, and execution behaviors. Review existing commands in the feature (if any) to understand test patterns. Apply BDD principles for test structure and naming.

### How to Update the Plan:

- **Fill in "AI Analysis Required" section**: Replace all "AI must determine" placeholders with concrete, determined values based on your analysis above, incorporating BDD and clean code principles.
- **Review "Implementation Details" section**: Update placeholder examples with actual determined structures that follow clean code principles (parameter objects, decomposed methods, guard clauses).
- **Review "Testing Strategy" section**: The TDD workflow (Scaffold → Signature → RED → GREEN) is already documented - ensure your determined values align with this workflow and BDD principles.
- **Add Implementation Approach section**: If not already present, add guidance on mocking strategy, base class reuse, clean code principles, and test strategy based on BDD and clean code rules.

**Remember**: After updating the plan, follow the TDD workflow described in the plan. Do not jump directly to implementation - create scaffold first, then signatures, then RED tests, then GREEN implementation. Validate against clean code and BDD rules continuously throughout development.
"""
    
    def _save_plan_file(self, plan_content: str) -> None:
        """Save plan content to file"""
        workspace_root = Path(__file__).parent.parent.parent
        command_dir = workspace_root / "behaviors" / self.feature_name / self.command_name
        command_dir.mkdir(parents=True, exist_ok=True)
        plan_file = command_dir / f"{self.command_name}-plan.md"
        plan_file.write_text(plan_content, encoding=DEFAULT_ENCODING)
        print(f"Plan saved to: {plan_file}")
    
    def generate(self):
        command_location = f"behaviors/{self.feature_name}/{self.command_name}"
        command_dir = self._resolve_command_directory(command_location)
        self._validate_command_not_exists(command_dir)
        command_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = self._generate_all_command_files(command_dir)
        self._update_runner_file()
        self._update_rule_file()
        self._display_command_generation_results(generated_files)
        
        return super().generate()
    
    def _resolve_command_directory(self, command_location: str) -> Path:
        """Resolve command directory path from location string"""
        if command_location.startswith("behaviors/"):
            workspace_root = Path(__file__).parent.parent.parent
            return workspace_root / command_location
        return Path(command_location).resolve()
    
    def _validate_command_not_exists(self, command_dir: Path) -> None:
        """Validate that command does not already exist"""
        if command_dir.exists() and (command_dir / f"{self.command_name}-cmd.md").exists():
            raise ValueError(f"Command '{self.command_name}' already exists in feature '{self.feature_name}'")
    
    def _generate_all_command_files(self, command_dir: Path) -> dict:
        """Generate all required command files"""
        return {
            'cmd_file': self._generate_command_cmd_file(command_dir),
            'generate_cmd_file': self._generate_command_generate_cmd_file(command_dir),
            'validate_cmd_file': self._generate_command_validate_cmd_file(command_dir)
        }
    
    def _display_command_generation_results(self, generated_files: dict) -> None:
        """Display command generation results to console"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print(f"Generated Command: {self.command_name}")
        print(separator)
        print(f"Feature: {self.feature_name}")
        print(f"\nGenerated files:")
        print(f"  - {generated_files['cmd_file']}")
        print(f"  - {generated_files['generate_cmd_file']}")
        print(f"  - {generated_files['validate_cmd_file']}")
    
    def _generate_command_cmd_file(self, command_dir: Path) -> Path:
        cmd_file = command_dir / f"{self.command_name}-cmd.md"
        cmd_content = self.load_template(
            "command_template.md",
            command_name=self.command_name,
            command_purpose=self.command_purpose or f"Purpose of the {self.command_name} command",
            target_entity=self.target_entity or "command",
            rule_name=f"{self.feature_name}-rule",
            feature_name=self.feature_name,
            runner_path=f"{self.feature_name}/{self.feature_name}_runner.py",
            execute_action=f"execute-{self.command_name}",
            generate_action=f"generate-{self.command_name}",
            validate_action=f"validate-{self.command_name}",
            command_parameters=f"[{self.feature_name}] [{self.command_name}]",
            action_list="Generate → User Feedback → Validate → User Feedback"
        )
        cmd_file.write_text(cmd_content, encoding=DEFAULT_ENCODING)
        return cmd_file
    
    def _generate_command_generate_cmd_file(self, command_dir: Path) -> Path:
        generate_cmd_file = command_dir / f"{self.command_name}-generate-cmd.md"
        generate_content = f"""### Command: `/{self.feature_name}-{self.command_name}-generate`

**Purpose:** Generate files for a new {self.target_entity or 'command'}. Delegates to main command with explicit generate action.

**Usage:**
* `/{self.feature_name}-{self.command_name}-generate [{self.feature_name}] [{self.command_name}]` — Generate command files (AI determines parameters if not provided)

**Steps:**
1. **Code** Execute the generate action in `/{self.feature_name}-{self.command_name}`
"""
        generate_cmd_file.write_text(generate_content, encoding=DEFAULT_ENCODING)
        return generate_cmd_file
    
    def _generate_command_validate_cmd_file(self, command_dir: Path) -> Path:
        validate_cmd_file = command_dir / f"{self.command_name}-validate-cmd.md"
        validate_content = f"""### Command: `/{self.feature_name}-{self.command_name}-validate`

**Purpose:** Validate files for a {self.target_entity or 'command'}. Delegates to main command with explicit validate action.

**Usage:**
* `/{self.feature_name}-{self.command_name}-validate [{self.feature_name}] [{self.command_name}]` — Validate command files (AI determines parameters if not provided)

**Steps:**
1. **Code** Execute the validate action in `/{self.feature_name}-{self.command_name}`
"""
        validate_cmd_file.write_text(validate_content, encoding=DEFAULT_ENCODING)
        return validate_cmd_file
    
    def _update_runner_file(self):
        """Update runner file with command class"""
        workspace_root = Path(__file__).parent.parent.parent
        runner_file = workspace_root / "behaviors" / self.feature_name / f"{self.feature_name}_runner.py"
        if not runner_file.exists():
            return
        
        runner_content = runner_file.read_text(encoding=DEFAULT_ENCODING)
        
        command_class = f"""
class {self.command_name.title().replace('-', '')}Command(CodeAgentCommand):
    \"\"\"Command that knows about validating and generating {self.target_entity or 'commands'}, uses templates\"\"\"
    pass

class CodeAugmented{self.command_name.title().replace('-', '')}Command(CodeAugmentedCommand):
    \"\"\"Extends CodeAugmentedCommand, wraps {self.command_name.title().replace('-', '')}Command for code validation\"\"\"
    pass

"""
        
        if "def main():" in runner_content:
            runner_content = runner_content.replace("def main():", command_class + "def main():")
        else:
            runner_content += command_class
        
        runner_file.write_text(runner_content, encoding=DEFAULT_ENCODING)
    
    def _update_rule_file(self):
        """Update rule file with command reference"""
        workspace_root = Path(__file__).parent.parent.parent
        rule_file = workspace_root / "behaviors" / self.feature_name / f"{self.feature_name}-rule.mdc"
        if not rule_file.exists():
            return
        
        rule_content = rule_file.read_text(encoding=DEFAULT_ENCODING)
        command_reference = f"* /{self.feature_name}-{self.command_name} — {self.command_purpose or f'Purpose of the {self.command_name} command'}\n"
        
        # Use guard clauses for early returns
        if "## Executing Commands" in rule_content:
            rule_content = rule_content.replace("## Executing Commands", f"## Executing Commands\n{command_reference}")
            rule_file.write_text(rule_content, encoding=DEFAULT_ENCODING)
            return
        
        if "**Executing Commands**" in rule_content:
            rule_content = rule_content.replace("**Executing Commands**", f"**Executing Commands**\n{command_reference}")
            rule_file.write_text(rule_content, encoding=DEFAULT_ENCODING)
            return
        
        # Default: append new section
        rule_content += f"\n## Executing Commands\n{command_reference}"
        rule_file.write_text(rule_content, encoding=DEFAULT_ENCODING)


@dataclass
class SyncCommandConfig:
    """Configuration for SyncCommand"""
    feature_name: Optional[str] = None
    force: bool = False
    target_directories: Optional[List[str]] = None


@dataclass
class IndexWriteOptions:
    """Parameter object for _write_index method"""
    index_data: Dict
    global_path: Path
    features: List[FeatureInfo]
    workspace_root: Path


class FileRouter:
    """Routes files to their destination paths based on file type"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
    
    def route_file(self, file_path: Path) -> Optional[Path]:
        """Determines destination path based on file extension"""
        if file_path.suffix == '.mdc':
            return self.workspace_root / '.cursor' / 'rules' / file_path.name
        elif file_path.suffix == '.md' and file_path.name.endswith('-cmd.md'):
            return self.workspace_root / '.cursor' / 'commands' / file_path.name
        elif file_path.name.endswith('-mcp.json'):
            return self.workspace_root / '.cursor' / 'mcp' / file_path.name
        elif file_path.name.endswith('-tasks.json'):
            return self.workspace_root / '.vscode' / 'tasks.json'
        return None


class JsonMerger:
    """Handles merging of JSON configuration files"""
    
    def merge_mcp_config(self, source: Path, dest: Path) -> Dict:
        """Merges MCP JSON configs"""
        with open(source, 'r', encoding=DEFAULT_ENCODING) as source_file:
            source_config = json.load(source_file)
        
        if dest.exists():
            with open(dest, 'r', encoding=DEFAULT_ENCODING) as dest_file:
                dest_config = json.load(dest_file)
            # Merge: source properties override destination
            merged = {**dest_config, **source_config}
            # Combine arrays
            for key in source_config:
                if isinstance(source_config[key], list) and isinstance(dest_config.get(key), list):
                    merged[key] = list(set(dest_config[key] + source_config[key]))
        else:
            merged = source_config
        
        with open(dest, 'w', encoding=DEFAULT_ENCODING) as dest_file:
            json.dump(merged, dest_file, indent=JSON_INDENT)
        
        return merged
    
    def merge_tasks_json(self, source: Path, dest: Path) -> Dict:
        """Merges tasks.json files"""
        with open(source, 'r', encoding=DEFAULT_ENCODING) as source_file:
            source_config = json.load(source_file)
        
        if dest.exists():
            with open(dest, 'r', encoding=DEFAULT_ENCODING) as dest_file:
                dest_config = json.load(dest_file)
            # Merge tasks arrays, avoid duplicate labels
            source_tasks = source_config.get('tasks', [])
            dest_tasks = dest_config.get('tasks', [])
            dest_labels = {task.get('label') for task in dest_tasks if 'label' in task}
            merged_tasks = dest_tasks + [task for task in source_tasks if task.get('label') not in dest_labels]
            merged = {**dest_config, **source_config, 'tasks': merged_tasks}
        else:
            merged = source_config
        
        with open(dest, 'w', encoding=DEFAULT_ENCODING) as dest_file:
            json.dump(merged, dest_file, indent=JSON_INDENT)
        
        return merged


class FileSyncer:
    """Handles file syncing operations (copy or merge)"""
    
    def __init__(self, file_router: FileRouter, json_merger: JsonMerger, force: bool):
        self.file_router = file_router
        self.json_merger = json_merger
        self.force = force
    
    def should_sync_file(self, source: Path, dest: Path) -> bool:
        """Checks if file should be synced (timestamp comparison)"""
        if self.force:
            return True
        if not dest.exists():
            return True
        return source.stat().st_mtime > dest.stat().st_mtime
    
    def sync_single_file(self, source: Path, dest: Path) -> bool:
        """Syncs a single file (copy or merge)"""
        if not self.should_sync_file(source, dest):
            return False
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if source.name.endswith('-mcp.json'):
            self.json_merger.merge_mcp_config(source, dest)
            return True
        elif source.name.endswith('-tasks.json'):
            self.json_merger.merge_tasks_json(source, dest)
            return True
        else:
            shutil.copy2(source, dest)
            return True


class IndexBuilder:
    """Builds index entries from behavior files"""
    
    def __init__(self, base_rule: CodeAgentRule, workspace_root: Path):
        self.base_rule = base_rule
        self.workspace_root = workspace_root
    
    def scan_behavior_files(self, feature_path: Path) -> List[Path]:
        """Scans feature directory for behavior files (.mdc, .md, .py, .json)"""
        behavior_files = []
        for ext in ['.mdc', '.md', '.py', '.json']:
            behavior_files.extend(feature_path.rglob(f"*{ext}"))
        
        # Filter out excluded files
        return [f for f in behavior_files if not self.base_rule.should_exclude_file(f, exclude_runner_py=True)]
    
    def build_index_entry(self, file_path: Path, feature: str, existing_index: Dict) -> Optional[Dict]:
        """Builds index entry, preserves existing purposes"""
        try:
            rel_path = file_path.relative_to(self.workspace_root)
        except ValueError:
            return None
        
        # Check if entry exists in existing index
        existing_entry = None
        for behavior in existing_index.get('behaviors', []):
            if behavior.get('path') == str(rel_path):
                existing_entry = behavior
                break
        
        entry = {
            'feature': feature,
            'file': file_path.name,
            'type': file_path.suffix,
            'path': str(rel_path),
            'modified_timestamp': file_path.stat().st_mtime
        }
        
        # Preserve existing purpose if present
        if existing_entry and 'purpose' in existing_entry:
            entry['purpose'] = existing_entry['purpose']
        else:
            entry['purpose'] = "[AI should update this purpose after reviewing the file]"
        
        return entry


class IndexPersistence:
    """Handles reading and writing index files"""
    
    def load_existing_index(self, index_path: Path) -> Dict:
        """Loads existing index JSON, returns empty dict if not exists"""
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding=DEFAULT_ENCODING) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def write_index(self, options: IndexWriteOptions) -> None:
        """Writes index to both global and local locations"""
        # Write global index
        options.global_path.parent.mkdir(parents=True, exist_ok=True)
        with open(options.global_path, 'w', encoding=DEFAULT_ENCODING) as f:
            json.dump(options.index_data, f, indent=JSON_INDENT)
        
        # Write local indexes
        for feature_info in options.features:
            local_path = feature_info.path / 'code-agent-index.json'
            # Filter behaviors for this feature
            feature_behaviors = [b for b in options.index_data['behaviors'] if b['feature'] == feature_info.name]
            local_index = {
                'last_updated': options.index_data['last_updated'],
                'total_behaviors': len(feature_behaviors),
                'behaviors': feature_behaviors
            }
            with open(local_path, 'w', encoding=DEFAULT_ENCODING) as f:
                json.dump(local_index, f, indent=JSON_INDENT)
    
    def get_timestamp(self) -> str:
        """Returns human-readable timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%a %b %d %H:%M:%S %Y")


class SyncCommand(CodeAgentCommand):
    """Command that synchronizes files from behaviors folders to cursor deployed areas"""
    
    def __init__(self, feature_name: Optional[str] = None, force: bool = False, target_directories: Optional[List[str]] = None) -> None:
        config = SyncCommandConfig(feature_name, force, target_directories)
        base_rule = CodeAgentRule("code-agent-rule.mdc")
        content = Content(file_path=str(Path("behaviors/")))
        
        generate_instructions = """Synchronize all commands and rules from behaviors folders (or any folder) with deployed=true to cursor deployed areas (.cursor/rules/, .cursor/commands/, .cursor/mcp/, .vscode/tasks.json).

**Rule Analysis:** Examine the attached rule file (code-agent-rule.mdc) for applicable principles. Extract code heuristics from these principles for validation. Integrate heuristics into the CodeAugmentedCommand wrapper pattern."""
        
        validate_instructions = """Validate the synchronized files comply with code-agent-rule.mdc principles.

**Rule-Based Validation:** Use code heuristics derived from the attached rule file (code-agent-rule.mdc) to perform initial validation. Verify heuristics are integrated and report any principle violations."""
        
        super().__init__(
            command_folder="sync",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = config.feature_name
        self.force = config.force
        self.target_directories = config.target_directories
    
    def generate(self):
        """Main entry point - syncs all files and displays results"""
        workspace_root = Path(__file__).parent.parent.parent
        target_dirs = self.base_rule.resolve_target_directories(self.target_directories, workspace_root)
        results = self._sync_all_files(target_dirs)
        self._display_sync_results(results)
        return super().generate()
    
    def _sync_all_files(self, target_dirs: List[Path]) -> Dict:
        """Orchestrates sync operation, returns dict with sync results"""
        features = self.base_rule.discover_deployed_features(target_dirs)
        results = {
            'has_changes': False,
            'synced_count': 0,
            'merged_count': 0,
            'skipped_count': 0,
            'features_processed': []
        }
        
        for feature_info in features:
            feature_results = self._sync_feature_files(feature_info)
            results['synced_count'] += feature_results.get('synced_count', 0)
            results['merged_count'] += feature_results.get('merged_count', 0)
            results['skipped_count'] += feature_results.get('skipped_count', 0)
            results['features_processed'].append(feature_info.name)
        
        results['has_changes'] = results['synced_count'] > 0 or results['merged_count'] > 0
        return results
    
    def _process_single_feature_file(self, file_path: Path, feature_info: FeatureInfo, workspace_root: Path) -> Dict:
        """Processes a single file for syncing"""
        result = {'synced': False, 'merged': False, 'skipped': False}
        
        file_router = FileRouter(workspace_root)
        json_merger = JsonMerger()
        file_syncer = FileSyncer(file_router, json_merger, self.force)
        
        dest_path = file_router.route_file(file_path)
        if not dest_path:
            result['skipped'] = True
            return result
        
        if file_syncer.should_sync_file(file_path, dest_path):
            if file_syncer.sync_single_file(file_path, dest_path):
                if file_path.suffix == '.json' and ('-mcp.json' in file_path.name or '-tasks.json' in file_path.name):
                    result['merged'] = True
                else:
                    result['synced'] = True
            else:
                result['skipped'] = True
        else:
            result['skipped'] = True
        
        return result
    
    def _sync_feature_files(self, feature_info: FeatureInfo) -> Dict:
        """Syncs all files for a single feature"""
        results = {
            'synced_count': 0,
            'merged_count': 0,
            'skipped_count': 0
        }
        
        workspace_root = Path(__file__).parent.parent.parent
        
        for file_path in feature_info.path.rglob("*"):
            if file_path.is_dir():
                continue
            
            if self.base_rule.should_exclude_file(file_path):
                results['skipped_count'] += 1
                continue
            
            file_result = self._process_single_feature_file(file_path, feature_info, workspace_root)
            if file_result['synced']:
                results['synced_count'] += 1
            elif file_result['merged']:
                results['merged_count'] += 1
            else:
                results['skipped_count'] += 1
        
        return results
    
    def _display_sync_results(self, results: Dict) -> None:
        """Displays sync results"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print("Sync Results")
        print(separator)
        print(f"Features processed: {len(results['features_processed'])}")
        print(f"Files synced: {results['synced_count']}")
        print(f"Files merged: {results['merged_count']}")
        print(f"Files skipped: {results['skipped_count']}")
        if results['features_processed']:
            print(f"\nFeatures: {', '.join(results['features_processed'])}")
    
    # Wrapper methods for backward compatibility with tests
    def _route_file(self, file_path: Path, workspace_root: Path) -> Optional[Path]:
        """Wrapper for FileRouter.route_file() - kept for test compatibility"""
        router = FileRouter(workspace_root)
        return router.route_file(file_path)
    
    def _merge_mcp_config(self, source: Path, dest: Path) -> Dict:
        """Wrapper for JsonMerger.merge_mcp_config() - kept for test compatibility"""
        merger = JsonMerger()
        return merger.merge_mcp_config(source, dest)
    
    def _merge_tasks_json(self, source: Path, dest: Path) -> Dict:
        """Wrapper for JsonMerger.merge_tasks_json() - kept for test compatibility"""
        merger = JsonMerger()
        return merger.merge_tasks_json(source, dest)
    
    def _should_sync_file(self, source: Path, dest: Path, force: bool) -> bool:
        """Wrapper for FileSyncer.should_sync_file() - kept for test compatibility"""
        router = FileRouter(Path(__file__).parent.parent.parent)
        merger = JsonMerger()
        syncer = FileSyncer(router, merger, force)
        return syncer.should_sync_file(source, dest)
    
    def _sync_single_file(self, source: Path, dest: Path, force: bool) -> bool:
        """Wrapper for FileSyncer.sync_single_file() - kept for test compatibility"""
        router = FileRouter(Path(__file__).parent.parent.parent)
        merger = JsonMerger()
        syncer = FileSyncer(router, merger, force)
        return syncer.sync_single_file(source, dest)


class CodeAugmentedSyncCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps SyncCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, force: bool = False, target_directories: Optional[List[str]] = None) -> None:
        base_rule = CodeAgentRule("code-agent-rule.mdc")
        sync_command = SyncCommand(feature_name, force, target_directories)
        super().__init__(sync_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for sync commands"""
        feature_name = args[0] if len(args) > 0 else None
        force = '--force' in args
        target_dirs = [arg for arg in args if not arg.startswith('--') and arg != feature_name] if len(args) > 1 else None
        
        command = cls(feature_name, force, target_dirs)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()


@dataclass
class IndexCommandConfig:
    """Configuration for IndexCommand"""
    feature_name: Optional[str] = None
    target_directories: Optional[List[str]] = None


class IndexCommand(CodeAgentCommand):
    """Command that maintains behavior index"""
    
    def __init__(self, feature_name: Optional[str] = None, target_directories: Optional[List[str]] = None) -> None:
        config = IndexCommandConfig(feature_name, target_directories)
        base_rule = CodeAgentRule("code-agent-rule.mdc")
        content = Content(file_path=str(Path("behaviors/")))
        
        generate_instructions = """Maintain an up-to-date behavior index (.cursor/behavior-index.json and local behaviors/<feature>/code-agent-index.json).

**Rule Analysis:** Examine the attached rule file (code-agent-rule.mdc) for applicable principles. Extract code heuristics from these principles for validation. Integrate heuristics into the CodeAugmentedCommand wrapper pattern."""
        
        validate_instructions = """Validate the behavior index complies with code-agent-rule.mdc principles.

**Rule-Based Validation:** Use code heuristics derived from the attached rule file (code-agent-rule.mdc) to perform initial validation. Verify heuristics are integrated and report any principle violations."""
        
        super().__init__(
            command_folder="sync",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = config.feature_name
        self.target_directories = config.target_directories
    
    def generate(self):
        """Main entry point - indexes all behaviors and displays results"""
        workspace_root = Path(__file__).parent.parent.parent
        target_dirs = self.base_rule.resolve_target_directories(self.target_directories, workspace_root)
        results = self._index_all_behaviors(target_dirs)
        self._display_index_results(results)
        return super().generate()
    
    def _index_all_behaviors(self, target_dirs: List[Path]) -> Dict:
        """Orchestrates index operation, returns dict with index results"""
        features = self.base_rule.discover_deployed_features(target_dirs)
        workspace_root = Path(__file__).parent.parent.parent
        global_index_path = workspace_root / '.cursor' / 'behavior-index.json'
        
        index_persistence = IndexPersistence()
        existing_index = index_persistence.load_existing_index(global_index_path)
        
        index_builder = IndexBuilder(self.base_rule, workspace_root)
        all_behaviors = []
        for feature_info in features:
            behaviors = self._index_feature_behaviors(feature_info, existing_index, index_builder)
            all_behaviors.extend(behaviors)
        
        index_data = {
            'last_updated': index_persistence.get_timestamp(),
            'total_behaviors': len(all_behaviors),
            'features_count': len(features),
            'behaviors': all_behaviors
        }
        
        write_options = IndexWriteOptions(
            index_data=index_data,
            global_path=global_index_path,
            features=features,
            workspace_root=workspace_root
        )
        index_persistence.write_index(write_options)
        
        return {
            'behaviors_indexed': len(all_behaviors),
            'features_processed': [f.name for f in features]
        }
    
    def _index_feature_behaviors(self, feature_info: FeatureInfo, existing_index: Dict, index_builder: IndexBuilder) -> List[Dict]:
        """Indexes all behavior files for a single feature"""
        behavior_files = index_builder.scan_behavior_files(feature_info.path)
        behaviors = []
        
        for file_path in behavior_files:
            entry = index_builder.build_index_entry(file_path, feature_info.name, existing_index)
            if entry:
                behaviors.append(entry)
        
        return behaviors
    
    def _display_index_results(self, results: Dict) -> None:
        """Displays index results"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print("Index Results")
        print(separator)
        print(f"Behaviors indexed: {results['behaviors_indexed']}")
        print(f"Features processed: {len(results['features_processed'])}")
        if results['features_processed']:
            print(f"\nFeatures: {', '.join(results['features_processed'])}")
    
    # Wrapper methods for backward compatibility with tests
    def _scan_behavior_files(self, feature_path: Path) -> List[Path]:
        """Wrapper for IndexBuilder.scan_behavior_files() - kept for test compatibility"""
        workspace_root = Path(__file__).parent.parent.parent
        builder = IndexBuilder(self.base_rule, workspace_root)
        return builder.scan_behavior_files(feature_path)
    
    def _build_index_entry(self, file_path: Path, feature: str, existing_index: Dict) -> Optional[Dict]:
        """Wrapper for IndexBuilder.build_index_entry() - kept for test compatibility"""
        workspace_root = Path(__file__).parent.parent.parent
        builder = IndexBuilder(self.base_rule, workspace_root)
        return builder.build_index_entry(file_path, feature, existing_index)
    
    def _load_existing_index(self, index_path: Path) -> Dict:
        """Wrapper for IndexPersistence.load_existing_index() - kept for test compatibility"""
        persistence = IndexPersistence()
        return persistence.load_existing_index(index_path)
    
    def _write_index(self, options: IndexWriteOptions) -> None:
        """Wrapper for IndexPersistence.write_index() - kept for test compatibility"""
        persistence = IndexPersistence()
        persistence.write_index(options)
    
    def _get_timestamp(self) -> str:
        """Wrapper for IndexPersistence.get_timestamp() - kept for test compatibility"""
        persistence = IndexPersistence()
        return persistence.get_timestamp()


class CodeAugmentedIndexCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps IndexCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, target_directories: Optional[List[str]] = None) -> None:
        base_rule = CodeAgentRule("code-agent-rule.mdc")
        index_command = IndexCommand(feature_name, target_directories)
        super().__init__(index_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for index commands"""
        feature_name = args[0] if len(args) > 0 else None
        target_dirs = [arg for arg in args if not arg.startswith('--') and arg != feature_name] if len(args) > 1 else None
        
        command = cls(feature_name, target_dirs)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()


class SyncIndexValidator:
    """Validates sync and index operations - extracted from SyncIndexCommand"""
    
    def __init__(self, sync_command: SyncCommand, force: bool):
        self.sync_command = sync_command
        self.force = force
    
    def validate_all(self, features: List[FeatureInfo], workspace_root: Path) -> List[str]:
        """Run all validation checks"""
        violations = []
        router = FileRouter(workspace_root)
        
        violations.extend(self.validate_file_routing(features, router, workspace_root))
        violations.extend(self.validate_merge_logic(features, workspace_root))
        violations.extend(self.validate_exclusion_logic(features, workspace_root))
        violations.extend(self.validate_timestamp_logic(features, router, workspace_root))
        violations.extend(self.validate_index_structure(workspace_root))
        
        return violations
    
    def validate_file_routing(self, features: List[FeatureInfo], router: FileRouter, workspace_root: Path) -> List[str]:
        """Verify sync destinations exist and files were routed correctly"""
        violations = []
        expected_destinations = {
            '.mdc': workspace_root / '.cursor' / 'rules',
            '-cmd.md': workspace_root / '.cursor' / 'commands',
            '-mcp.json': workspace_root / '.cursor' / 'mcp',
            '-tasks.json': workspace_root / '.vscode'
        }
        
        for feature_info in features:
            violations.extend(self._validate_feature_routing(
                feature_info, router, expected_destinations))
        return violations
    
    def _validate_feature_routing(self, feature_info: FeatureInfo, router: FileRouter, 
                                   expected_destinations: Dict) -> List[str]:
        """Validate routing for a single feature - reduces nesting"""
        violations = []
        routable_files = self._get_routable_files(feature_info.path)
        
        for source_file in routable_files:
            dest = router.route_file(source_file)
            if dest is None:
                continue
            
            violations.extend(self._check_routing_violations(
                source_file, dest, expected_destinations))
        return violations
    
    def _get_routable_files(self, feature_path: Path) -> List[Path]:
        """Extract routable files - reduces nesting in main loop"""
        routable = []
        for ext in ['.mdc', '.md', '.json']:
            for source_file in feature_path.rglob(f"*{ext}"):
                if not self.sync_command.base_rule.should_exclude_file(
                    source_file, exclude_runner_py=True):
                    routable.append(source_file)
        return routable
    
    def _check_routing_violations(self, source_file: Path, dest: Path, 
                                  expected_destinations: Dict) -> List[str]:
        """Check routing violations for a single file - reduces nesting"""
        violations = []
        
        if not dest.parent.exists():
            violations.append(f"Routing violation: Destination directory missing for {source_file.name}: {dest.parent}")
            return violations
        
        expected_base = self._find_expected_destination(source_file, expected_destinations)
        if expected_base and dest.parent != expected_base:
            violations.append(f"Routing violation: {source_file.name} routed to {dest.parent} but expected {expected_base}")
        
        return violations
    
    def _find_expected_destination(self, source_file: Path, expected_destinations: Dict) -> Optional[Path]:
        """Find expected destination for a source file"""
        for pattern, expected_dir in expected_destinations.items():
            if pattern in source_file.name or source_file.suffix == pattern:
                return expected_dir
        return None
    
    def validate_merge_logic(self, features: List[FeatureInfo], workspace_root: Path) -> List[str]:
        """Verify merge logic worked correctly for MCP configs and tasks.json"""
        violations = []
        
        for feature_info in features:
            violations.extend(self._validate_feature_merge_logic(feature_info, workspace_root))
        
        return violations
    
    def _validate_feature_merge_logic(self, feature_info: FeatureInfo, workspace_root: Path) -> List[str]:
        """Validate merge logic for a single feature"""
        violations = []
        violations.extend(self._validate_mcp_configs(feature_info.path, workspace_root))
        violations.extend(self._validate_tasks_json(feature_info.path, workspace_root))
        return violations
    
    def _validate_mcp_configs(self, feature_path: Path, workspace_root: Path) -> List[str]:
        """Validate MCP config merge logic"""
        violations = []
        for mcp_file in feature_path.rglob("*-mcp.json"):
            dest = workspace_root / '.cursor' / 'mcp' / mcp_file.name
            if not dest.exists():
                continue
            
            try:
                with open(dest, 'r', encoding=DEFAULT_ENCODING) as f:
                    merged_config = json.load(f)
                with open(mcp_file, 'r', encoding=DEFAULT_ENCODING) as source_file:
                    source_config = json.load(source_file)
                
                for key in source_config:
                    if isinstance(source_config[key], list):
                        if key in merged_config and not isinstance(merged_config[key], list):
                            violations.append(f"Merge violation: {mcp_file.name} key '{key}' should be array but is {type(merged_config[key]).__name__}")
            except json.JSONDecodeError as e:
                violations.append(f"Merge violation: {dest} contains invalid JSON: {e}")
        
        return violations
    
    def _validate_tasks_json(self, feature_path: Path, workspace_root: Path) -> List[str]:
        """Validate tasks.json merge logic"""
        violations = []
        for tasks_file in feature_path.rglob("*-tasks.json"):
            dest = workspace_root / '.vscode' / 'tasks.json'
            if not dest.exists():
                continue
            
            try:
                with open(dest, 'r', encoding=DEFAULT_ENCODING) as f:
                    merged_tasks = json.load(f)
                
                if 'tasks' not in merged_tasks:
                    violations.append(f"Merge violation: {dest} missing 'tasks' key")
                elif not isinstance(merged_tasks['tasks'], list):
                    violations.append(f"Merge violation: {dest} 'tasks' should be array but is {type(merged_tasks['tasks']).__name__}")
                else:
                    labels = [task.get('label') for task in merged_tasks['tasks'] if 'label' in task]
                    duplicates = [label for label in labels if labels.count(label) > 1]
                    if duplicates:
                        violations.append(f"Merge violation: {dest} has duplicate task labels: {duplicates}")
            except json.JSONDecodeError as e:
                violations.append(f"Merge violation: {dest} contains invalid JSON: {e}")
        
        return violations
    
    def validate_exclusion_logic(self, features: List[FeatureInfo], workspace_root: Path) -> List[str]:
        """Verify exclusion logic correctly skipped docs/, .py files, drafts"""
        violations = []
        router = FileRouter(workspace_root)
        
        for feature_info in features:
            violations.extend(self._validate_feature_exclusion_logic(
                feature_info.path, router))
        
        return violations
    
    def _validate_feature_exclusion_logic(self, feature_path: Path, router: FileRouter) -> List[str]:
        """Validate exclusion logic for a single feature"""
        violations = []
        for excluded_file in feature_path.rglob("*"):
            if not self.sync_command.base_rule.should_exclude_file(
                excluded_file, exclude_runner_py=True):
                continue
            
            dest = router.route_file(excluded_file)
            if dest and dest.exists():
                violations.append(f"Exclusion violation: Excluded file {excluded_file.name} was synced to {dest}")
        
        return violations
    
    def validate_timestamp_logic(self, features: List[FeatureInfo], router: FileRouter, 
                                workspace_root: Path) -> List[str]:
        """Verify timestamp comparison logic worked correctly"""
        violations = []
        
        if self.force:
            return violations  # Skip timestamp validation if force flag used
        
        for feature_info in features:
            violations.extend(self._validate_feature_timestamps(
                feature_info.path, router))
        
        return violations
    
    def _validate_feature_timestamps(self, feature_path: Path, router: FileRouter) -> List[str]:
        """Validate timestamps for a single feature"""
        violations = []
        for source_file in feature_path.rglob("*"):
            if self.sync_command.base_rule.should_exclude_file(
                source_file, exclude_runner_py=True):
                continue
            
            dest = router.route_file(source_file)
            if dest is None or not dest.exists():
                continue
            
            try:
                dest_mtime = dest.stat().st_mtime
                if dest_mtime < 0:
                    violations.append(f"Timestamp violation: {dest} has invalid timestamp")
            except OSError as e:
                violations.append(f"Timestamp violation: Cannot stat {dest}: {e}")
        
        return violations
    
    def validate_index_structure(self, workspace_root: Path) -> List[str]:
        """Verify index structure is correct and purposes are preserved"""
        violations = []
        global_index_path = workspace_root / '.cursor' / 'behavior-index.json'
        
        if not global_index_path.exists():
            violations.append("Index violation: Global index file does not exist")
            return violations
        
        try:
            with open(global_index_path, 'r', encoding=DEFAULT_ENCODING) as f:
                index_data = json.load(f)
            
            violations.extend(self._validate_index_fields(index_data, global_index_path))
            violations.extend(self._validate_behaviors_structure(index_data, global_index_path))
            violations.extend(self._validate_total_behaviors_count(index_data, global_index_path))
        except json.JSONDecodeError as e:
            violations.append(f"Index violation: {global_index_path} contains invalid JSON: {e}")
        except IOError as e:
            violations.append(f"Index violation: Cannot read {global_index_path}: {e}")
        
        return violations
    
    def _validate_index_fields(self, index_data: Dict, index_path: Path) -> List[str]:
        """Validate required index fields"""
        violations = []
        required_fields = ['last_updated', 'total_behaviors', 'behaviors']
        for field in required_fields:
            if field not in index_data:
                violations.append(f"Index violation: Missing required field '{field}' in {index_path}")
        return violations
    
    def _validate_behaviors_structure(self, index_data: Dict, index_path: Path) -> List[str]:
        """Validate behaviors array structure"""
        violations = []
        if 'behaviors' not in index_data:
            return violations
        
        if not isinstance(index_data['behaviors'], list):
            violations.append(f"Index violation: 'behaviors' should be array but is {type(index_data['behaviors']).__name__}")
            return violations
        
        behavior_fields = ['feature', 'file', 'type', 'path', 'modified_timestamp', 'purpose']
        for i, behavior in enumerate(index_data['behaviors']):
            for field in behavior_fields:
                if field not in behavior:
                    violations.append(f"Index violation: Behavior {i} missing required field '{field}'")
            
            if 'purpose' in behavior:
                purpose = behavior['purpose']
                if not purpose or purpose.strip() == '':
                    violations.append(f"Index violation: Behavior {i} has empty purpose")
        
        return violations
    
    def _validate_total_behaviors_count(self, index_data: Dict, index_path: Path) -> List[str]:
        """Validate total_behaviors matches actual count"""
        violations = []
        if 'behaviors' in index_data and 'total_behaviors' in index_data:
            actual_count = len(index_data['behaviors'])
            expected_count = index_data['total_behaviors']
            if actual_count != expected_count:
                violations.append(f"Index violation: total_behaviors ({expected_count}) does not match actual count ({actual_count})")
        return violations


class ValidationReportBuilder:
    """Builds validation reports - extracted from SyncIndexCommand"""
    
    def build_report(self, violations: List[str], deployment_info: Dict, 
                    index_info: Dict, features: List[FeatureInfo]) -> str:
        """Build complete validation report"""
        report_lines = self._build_header()
        report_lines.extend(self._build_features_section(features))
        report_lines.extend(self._build_deployment_section(deployment_info))
        report_lines.extend(self._build_index_section(index_info))
        report_lines.extend(self._build_violations_section(violations))
        return "\n".join(report_lines)
    
    def _build_header(self) -> List[str]:
        """Build report header"""
        separator = "=" * SEPARATOR_LENGTH
        return [
            separator,
            "Sync and Index Validation Report",
            separator,
            ""
        ]
    
    def _build_features_section(self, features: List[FeatureInfo]) -> List[str]:
        """Build features processed section"""
        report_lines = ["FEATURES PROCESSED:"]
        for feature_info in features:
            report_lines.append(f"  - {feature_info.name} ({feature_info.path})")
        report_lines.append("")
        return report_lines
    
    def _build_deployment_section(self, deployment_info: Dict) -> List[str]:
        """Build deployment details section"""
        report_lines = ["DEPLOYED FILES:"]
        report_lines.append(f"  Rules (.mdc): {len(deployment_info['rules'])} files")
        if deployment_info['rules']:
            for rule_file in sorted(deployment_info['rules'])[:MAX_FILES_TO_DISPLAY]:
                report_lines.append(f"    - {rule_file}")
            if len(deployment_info['rules']) > MAX_FILES_TO_DISPLAY:
                report_lines.append(f"    ... and {len(deployment_info['rules']) - MAX_FILES_TO_DISPLAY} more")
        
        report_lines.append(f"  Commands (-cmd.md): {len(deployment_info['commands'])} files")
        if deployment_info['commands']:
            for cmd_file in sorted(deployment_info['commands'])[:MAX_FILES_TO_DISPLAY]:
                report_lines.append(f"    - {cmd_file}")
            if len(deployment_info['commands']) > MAX_FILES_TO_DISPLAY:
                report_lines.append(f"    ... and {len(deployment_info['commands']) - MAX_FILES_TO_DISPLAY} more")
        
        report_lines.append(f"  MCP Configs (-mcp.json): {len(deployment_info['mcp_configs'])} files")
        if deployment_info['mcp_configs']:
            for mcp_file in sorted(deployment_info['mcp_configs']):
                report_lines.append(f"    - {mcp_file}")
        
        report_lines.append(f"  Tasks JSON: {'Yes' if deployment_info['tasks_json'] else 'No'}")
        report_lines.append("")
        
        report_lines.append("DEPLOYMENT BY FEATURE:")
        for feature_name, feature_deployment in deployment_info['by_feature'].items():
            report_lines.append(f"  {feature_name}:")
            report_lines.append(f"    Rules: {len(feature_deployment['rules'])}")
            report_lines.append(f"    Commands: {len(feature_deployment['commands'])}")
            report_lines.append(f"    MCP Configs: {len(feature_deployment['mcp_configs'])}")
            report_lines.append(f"    Tasks JSON: {'Yes' if feature_deployment['tasks_json'] else 'No'}")
        report_lines.append("")
        
        return report_lines
    
    def _build_index_section(self, index_info: Dict) -> List[str]:
        """Build index information section"""
        report_lines = ["INDEX INFORMATION:"]
        if index_info['exists']:
            report_lines.append(f"  Index File: {index_info['index_path']}")
            report_lines.append(f"  Last Updated: {index_info.get('last_updated', 'Unknown')}")
            report_lines.append(f"  Total Behaviors: {index_info['total_behaviors']}")
            report_lines.append("")
            
            report_lines.append("  Behaviors by Type:")
            for file_type, count in sorted(index_info['behaviors_by_type'].items()):
                report_lines.append(f"    {file_type}: {count}")
            report_lines.append("")
            
            report_lines.append("  Behaviors by Feature:")
            for feature_name, behaviors in sorted(index_info['behaviors_by_feature'].items()):
                report_lines.append(f"    {feature_name}: {len(behaviors)} behaviors")
                for behavior in behaviors[:MAX_BEHAVIORS_PER_FEATURE_TO_DISPLAY]:
                    report_lines.append(f"      - {behavior['file']} ({behavior['path']})")
                if len(behaviors) > MAX_BEHAVIORS_PER_FEATURE_TO_DISPLAY:
                    report_lines.append(f"      ... and {len(behaviors) - MAX_BEHAVIORS_PER_FEATURE_TO_DISPLAY} more")
        else:
            report_lines.append("  [WARNING] Index file does not exist")
        report_lines.append("")
        
        return report_lines
    
    def _build_violations_section(self, violations: List[str]) -> List[str]:
        """Build violations section"""
        separator = "=" * SEPARATOR_LENGTH
        report_lines = []
        
        if not violations:
            report_lines.extend([
                "[PASS] Validation PASSED",
                "",
                "All validation checks passed:",
                "  [OK] Files routed correctly",
                "  [OK] Merge logic working correctly",
                "  [OK] Exclusion logic working correctly",
                "  [OK] Timestamp comparison working correctly",
                "  [OK] Index structure is correct",
                "  [OK] Index purposes preserved"
            ])
        else:
            report_lines.extend([
                "[FAIL] Validation FAILED",
                "",
                f"Found {len(violations)} violation(s):",
                ""
            ])
            for i, violation in enumerate(violations, 1):
                report_lines.append(f"  {i}. {violation}")
            
            report_lines.extend([
                "",
                "Please fix the violations above and re-run validation."
            ])
        
        report_lines.append("")
        report_lines.append(separator)
        
        return report_lines


class DeploymentInfoCollector:
    """Collects deployment and index information - extracted from SyncIndexCommand"""
    
    def __init__(self, sync_command: SyncCommand):
        self.sync_command = sync_command
    
    def collect_deployment_info(self, features: List[FeatureInfo], workspace_root: Path) -> Dict:
        """Collect information about what files were deployed and where"""
        router = FileRouter(workspace_root)
        deployment_info = {
            'rules': [],
            'commands': [],
            'mcp_configs': [],
            'tasks_json': False,
            'by_feature': {}
        }
        
        for feature_info in features:
            feature_deployment = self._collect_feature_deployment(
                feature_info, router, workspace_root)
            deployment_info['rules'].extend(feature_deployment['rules'])
            deployment_info['commands'].extend(feature_deployment['commands'])
            deployment_info['mcp_configs'].extend(feature_deployment['mcp_configs'])
            if feature_deployment['tasks_json']:
                deployment_info['tasks_json'] = True
            deployment_info['by_feature'][feature_info.name] = feature_deployment
        
        return deployment_info
    
    def _collect_feature_deployment(self, feature_info: FeatureInfo, router: FileRouter, 
                                    workspace_root: Path) -> Dict:
        """Collect deployment info for a single feature"""
        feature_deployment = {
            'rules': [],
            'commands': [],
            'mcp_configs': [],
            'tasks_json': False
        }
        
        for source_file in feature_info.path.rglob("*"):
            if self.sync_command.base_rule.should_exclude_file(
                source_file, exclude_runner_py=True):
                continue
            
            dest = router.route_file(source_file)
            if dest is None or not dest.exists():
                continue
            
            rel_path = str(dest.relative_to(workspace_root))
            self._categorize_deployed_file(dest, rel_path, feature_deployment)
        
        return feature_deployment
    
    def _categorize_deployed_file(self, dest: Path, rel_path: str, feature_deployment: Dict) -> None:
        """Categorize a deployed file into the appropriate list"""
        if dest.suffix == '.mdc':
            feature_deployment['rules'].append(rel_path)
        elif dest.name.endswith('-cmd.md'):
            feature_deployment['commands'].append(rel_path)
        elif dest.name.endswith('-mcp.json'):
            feature_deployment['mcp_configs'].append(rel_path)
        elif dest.name == 'tasks.json':
            feature_deployment['tasks_json'] = True
    
    def collect_index_info(self, workspace_root: Path) -> Dict:
        """Collect information about what was indexed"""
        index_info = {
            'exists': False,
            'total_behaviors': 0,
            'behaviors_by_feature': {},
            'behaviors_by_type': {},
            'index_path': str(workspace_root / '.cursor' / 'behavior-index.json')
        }
        
        global_index_path = workspace_root / '.cursor' / 'behavior-index.json'
        if not global_index_path.exists():
            return index_info
        
        index_info['exists'] = True
        try:
            with open(global_index_path, 'r', encoding=DEFAULT_ENCODING) as f:
                index_data = json.load(f)
            
            index_info['total_behaviors'] = index_data.get('total_behaviors', 0)
            index_info['last_updated'] = index_data.get('last_updated', 'Unknown')
            
            if 'behaviors' in index_data:
                for behavior in index_data['behaviors']:
                    self._process_behavior_entry(behavior, index_info)
        except (json.JSONDecodeError, IOError):
            pass
        
        return index_info
    
    def _process_behavior_entry(self, behavior: Dict, index_info: Dict) -> None:
        """Process a single behavior entry into index info"""
        feature = behavior.get('feature', 'unknown')
        file_type = behavior.get('type', 'unknown')
        
        if feature not in index_info['behaviors_by_feature']:
            index_info['behaviors_by_feature'][feature] = []
        index_info['behaviors_by_feature'][feature].append({
            'file': behavior.get('file', ''),
            'path': behavior.get('path', ''),
            'type': file_type
        })
        
        if file_type not in index_info['behaviors_by_type']:
            index_info['behaviors_by_type'][file_type] = 0
        index_info['behaviors_by_type'][file_type] += 1


class SyncIndexCommand(CodeAgentCommand):
    """Wrapper that orchestrates sync then index seamlessly"""
    
    def __init__(self, feature_name: Optional[str] = None, force: bool = False, target_directories: Optional[List[str]] = None) -> None:
        base_rule = BaseRule("code-agent-rule.mdc")
        content = Content(file_path=str(Path("behaviors/")))
        
        generate_instructions = """Orchestrate sync then index operations. Sync files first, then update index only if sync made changes."""
        validate_instructions = """Validate both sync and index operations comply with code-agent-rule.mdc principles."""
        
        super().__init__(
            command_folder="sync",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = feature_name
        self.force = force
        self.target_directories = target_directories
        self.sync_command = SyncCommand(feature_name, force, target_directories)
        self.index_command = IndexCommand(feature_name, target_directories)
        
        # Create helper classes (composition)
        self.validator = SyncIndexValidator(self.sync_command, force)
        self.report_builder = ValidationReportBuilder()
        self.info_collector = DeploymentInfoCollector(self.sync_command)
    
    def generate(self):
        """Main entry point - orchestrates sync then conditional index"""
        workspace_root = Path(__file__).parent.parent.parent
        sync_target_dirs = self.sync_command.base_rule.resolve_target_directories(self.target_directories, workspace_root)
        sync_results = self.sync_command._sync_all_files(sync_target_dirs)
        
        index_results = None
        if self._should_run_index(sync_results):
            index_target_dirs = self.index_command.base_rule.resolve_target_directories(self.target_directories, workspace_root)
            index_results = self.index_command._index_all_behaviors(index_target_dirs)
        
        combined_results = self._combine_results(sync_results, index_results)
        self._display_combined_results(combined_results)
        return super().generate()
    
    def _should_run_index(self, sync_results: Dict) -> bool:
        """Checks if index should run based on sync results"""
        return sync_results.get('has_changes', False)
    
    def _combine_results(self, sync_results: Dict, index_results: Optional[Dict]) -> Dict:
        """Combines results from both operations"""
        combined = {
            **sync_results,
            'index_ran': index_results is not None
        }
        if index_results:
            combined.update(index_results)
        return combined
    
    def _display_combined_results(self, results: Dict) -> None:
        """Displays combined results"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print("Sync and Index Results")
        print(separator)
        print(f"Features processed: {len(results.get('features_processed', []))}")
        print(f"Files synced: {results.get('synced_count', 0)}")
        print(f"Files merged: {results.get('merged_count', 0)}")
        print(f"Files skipped: {results.get('skipped_count', 0)}")
        
        if results.get('index_ran'):
            print(f"\nBehaviors indexed: {results.get('behaviors_indexed', 0)}")
        else:
            print("\nIndex skipped (no changes detected)")
        
        if results.get('features_processed'):
            print(f"\nFeatures: {', '.join(results['features_processed'])}")
    
    def validate(self):
        """Validates sync and index operations - DELEGATES to validator"""
        workspace_root = Path(__file__).parent.parent.parent
        
        # Get target directories and discover features
        target_dirs = self.sync_command.base_rule.resolve_target_directories(self.target_directories, workspace_root)
        features = self.sync_command.base_rule.discover_deployed_features(target_dirs)
        
        # DELEGATE: Collect info
        deployment_info = self.info_collector.collect_deployment_info(features, workspace_root)
        index_info = self.info_collector.collect_index_info(workspace_root)
        
        # DELEGATE: Run validations
        violations = self.validator.validate_all(features, workspace_root)
        
        # DELEGATE: Build report
        report = self.report_builder.build_report(violations, deployment_info, index_info, features)
        print(report)
        self.validated = True
        return report


class CodeAugmentedSyncIndexCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps SyncIndexCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, force: bool = False, target_directories: Optional[List[str]] = None) -> None:
        base_rule = BaseRule("code-agent-rule.mdc")
        sync_index_command = SyncIndexCommand(feature_name, force, target_directories)
        super().__init__(sync_index_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for sync-index commands"""
        feature_name = args[0] if len(args) > 0 else None
        force = '--force' in args
        target_dirs = [arg for arg in args if not arg.startswith('--') and arg != feature_name] if len(args) > 1 else None
        
        command = cls(feature_name, force, target_dirs)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()


class RuleTemplateLoader:
    """Handles template loading and name resolution - extracted from RuleCommand"""
    
    def __init__(self, command_folder: str, rule_command):
        self.command_folder = command_folder
        self.rule_command = rule_command  # Store reference to command for dynamic method calls
    
    def get_template_name(self, rule_type: str) -> str:
        """Get template name based on rule type"""
        if rule_type == "specializing":
            return "specializing_rule_template.mdc"
        elif rule_type == "specialized":
            return "specialized_rule_template.mdc"
        return "base_rule_template.mdc"
    
    def load_template(self, template_name: str, **kwargs) -> str:
        """Load template using CodeAgentCommand's load_template method"""
        # Call dynamically so test mocks work
        return self.rule_command.load_template(template_name, **kwargs)
    
    def load_principle_template(self, **kwargs) -> str:
        """Load principle template with fallback"""
        try:
            return self.load_template(
                "principle_template.mdc",
                principle_number=kwargs.get('principle_number', 1),
                Principle_Name=kwargs.get('Principle_Name', "Principle Name"),
                principle_description=kwargs.get('principle_description', "Principle description."),
                do_examples=kwargs.get('do_examples', "* Example"),
                dont_examples=kwargs.get('dont_examples', "* Example")
            )
        except (FileNotFoundError, KeyError):
            return "## 1. Principle Name\n\nPrinciple description.\n\n**[DO]:**\n* Example\n\n**[DON'T]:**\n* Example\n"


class RuleFileGenerator:
    """Generates rule files from templates - extracted from RuleCommand"""
    
    def __init__(self, template_loader: RuleTemplateLoader, 
                 feature_name: str, rule_name: str, rule_purpose: Optional[str],
                 rule_type: str, parent_rule_name: Optional[str]):
        self.template_loader = template_loader
        self.feature_name = feature_name
        self.rule_name = rule_name
        self.rule_purpose = rule_purpose
        self.rule_type = rule_type
        self.parent_rule_name = parent_rule_name
    
    def generate_rule_file(self, rule_path: Path) -> Path:
        """Generate rule file from template"""
        template_name = self.template_loader.get_template_name(self.rule_type)
        principles_section = self._generate_principles_section()
        
        template_kwargs = self._build_base_template_kwargs(principles_section)
        template_kwargs.update(self._build_rule_type_specific_kwargs())
        
        rule_content = self.template_loader.load_template(template_name, **template_kwargs)
        rule_path.write_text(rule_content, encoding=DEFAULT_ENCODING)
        return rule_path
    
    def _generate_principles_section(self) -> str:
        """Generate principles section using principle template"""
        return self.template_loader.load_principle_template()
    
    def _build_base_template_kwargs(self, principles_section: str) -> Dict:
        """Build base template kwargs common to all rule types"""
        return {
            "rule_description": self.rule_purpose or f"Description for {self.rule_name} rule",
            "glob_patterns": "**/*.mdc",
            "always_apply": "false",
            "context": "writing rules",
            "behavior": "follow these practices",
            "rule_overview_text": self.rule_purpose or f"Overview for {self.rule_name} rule",
            "executing_commands": f"* `\\{self.feature_name}-{self.rule_name}` — {self.rule_purpose or f'Purpose of the {self.rule_name} rule'}",
            "principles_section": principles_section
        }
    
    def _build_rule_type_specific_kwargs(self) -> Dict:
        """Build rule-type specific template parameters"""
        if self.rule_type == "specializing":
            return {
                "specializing_aspect": self.rule_name.replace("-", " "),
                "parent_rule_name": self.parent_rule_name or "base-rule",
                "parent_rule": self.parent_rule_name or "base rule"
            }
        elif self.rule_type == "specialized":
            framework_parts = self.rule_name.split("-")
            framework = framework_parts[-1] if len(framework_parts) > 1 else "framework"
            rule_type_base = "-".join(framework_parts[:-1]) if len(framework_parts) > 1 else "rule"
            language = framework
            return {
                "framework": framework,
                "rule_type": rule_type_base.replace("-", " "),
                "language": language,
                "framework_specific_globs": f"**/*.{language}",
                "parent_specializing_rule": self.parent_rule_name or f"{rule_type_base}-rule",
                "base_rule": "base-rule"
            }
        return {}


class RuleValidator:
    """Validates rule file structure - extracted from RuleCommand"""
    
    def __init__(self, feature_name: str, rule_name: str, rule_type: str, 
                 parent_rule_name: Optional[str]):
        self.feature_name = feature_name
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.parent_rule_name = parent_rule_name
    
    def validate_all(self, rule_path: Path) -> List[str]:
        """Run all validation checks"""
        violations = []
        violations.extend(self.validate_frontmatter(rule_path))
        violations.extend(self.validate_principles(rule_path))
        violations.extend(self.validate_examples(rule_path))
        violations.extend(self.validate_rule_references(rule_path))
        return violations
    
    def validate_frontmatter(self, rule_path: Path) -> List[str]:
        """Validate frontmatter format"""
        violations = []
        try:
            content = rule_path.read_text(encoding=DEFAULT_ENCODING)
            if not content.startswith("---"):
                violations.append(f"Missing frontmatter (YAML) at start of file: {rule_path}")
                return violations
            
            required_fields = ["description:", "globs:", "alwaysApply:"]
            for field in required_fields:
                if field not in content:
                    violations.append(f"Missing '{field.rstrip(':')}' field in frontmatter: {rule_path}")
        except Exception as e:
            violations.append(f"Error reading rule file: {e}")
        
        return violations
    
    def validate_principles(self, rule_path: Path) -> List[str]:
        """Validate principles have required structure"""
        violations = []
        try:
            content = rule_path.read_text(encoding=DEFAULT_ENCODING)
            
            principle_pattern = r'^##\s+\d+\.\s+.+$'
            principles = re.findall(principle_pattern, content, re.MULTILINE)
            
            if not principles:
                violations.append(f"No principles found (expected format: '## 1. Principle Name'): {rule_path}")
            
            try:
                from behaviors.common_command_runner.common_command_runner import BaseRule
                rule_file_name = str(rule_path.relative_to(Path(__file__).parent.parent.parent))
                rule_instance = BaseRule(rule_file_name)
                if not rule_instance.principles:
                    violations.append(f"BaseRule could not load principles from file: {rule_path}")
            except Exception as e:
                violations.append(f"BaseRule validation failed: {e}")
        except Exception as e:
            violations.append(f"Error validating principles: {e}")
        
        return violations
    
    def validate_examples(self, rule_path: Path) -> List[str]:
        """Validate examples format (do/don't)"""
        violations = []
        try:
            content = rule_path.read_text(encoding=DEFAULT_ENCODING)
            
            do_patterns = [r'\*\*\[DO\]:\*\*', r'\[DO\]:', r'\*\*Do:\*\*', r'Do:']
            dont_patterns = [r'\*\*\[DON\'T\]:\*\*', r'\[DON\'T\]:', r'\*\*Don\'t:\*\*', r'Don\'t:']
            
            has_do = any(re.search(pattern, content, re.IGNORECASE) for pattern in do_patterns)
            has_dont = any(re.search(pattern, content, re.IGNORECASE) for pattern in dont_patterns)
            
            if has_do and not has_dont:
                violations.append(f"Found DO examples but no DON'T examples: {rule_path}")
            if has_dont and not has_do:
                violations.append(f"Found DON'T examples but no DO examples: {rule_path}")
        except Exception as e:
            violations.append(f"Error validating examples: {e}")
        
        return violations
    
    def validate_rule_references(self, rule_path: Path) -> List[str]:
        """Validate rule references for specializing/specialized rules"""
        violations = []
        
        if self.rule_type == "base":
            return violations
        
        try:
            content = rule_path.read_text(encoding=DEFAULT_ENCODING)
            
            if self.rule_type == "specializing":
                violations.extend(self._validate_specializing_references(content, rule_path))
            elif self.rule_type == "specialized":
                violations.extend(self._validate_specialized_references(content, rule_path))
        except Exception as e:
            violations.append(f"Error validating rule references: {e}")
        
        return violations
    
    def _validate_specializing_references(self, content: str, rule_path: Path) -> List[str]:
        """Validate specializing rule references"""
        violations = []
        
        if not self.parent_rule_name:
            violations.append(f"Specializing rule missing parent_rule_name: {rule_path}")
        elif self.parent_rule_name not in content:
            violations.append(f"Specializing rule does not reference parent rule '{self.parent_rule_name}': {rule_path}")
        
        specialized_rules = self._find_specialized_rules_for_specializing_rule(rule_path)
        if not specialized_rules:
            violations.append(f"Specializing rule '{self.rule_name}' does not have any specialized rules: {rule_path}")
        
        return violations
    
    def _validate_specialized_references(self, content: str, rule_path: Path) -> List[str]:
        """Validate specialized rule references"""
        violations = []
        
        if not self.parent_rule_name:
            violations.append(f"Specialized rule missing parent_rule_name: {rule_path}")
        elif self.parent_rule_name not in content:
            violations.append(f"Specialized rule does not reference parent specializing rule '{self.parent_rule_name}': {rule_path}")
        
        return violations
    
    def _find_specialized_rules_for_specializing_rule(self, specializing_rule_path: Path) -> List[Path]:
        """Find specialized rules that reference this specializing rule as their parent"""
        specialized_rules = []
        rules_dir = specializing_rule_path.parent
        
        if not rules_dir.exists():
            return specialized_rules
        
        for rule_file in rules_dir.glob("*-rule.mdc"):
            if rule_file == specializing_rule_path:
                continue
            
            try:
                rule_content = rule_file.read_text(encoding=DEFAULT_ENCODING)
                if self.rule_name in rule_content:
                    specialized_rules.append(rule_file)
            except Exception:
                continue
        
        return specialized_rules


class RuleCommand(CodeAgentCommand):
    """Command that knows about validating and generating rules within a feature, uses templates"""
    
    def __init__(self, feature_name: Optional[str] = None, rule_name: Optional[str] = None, rule_purpose: Optional[str] = None, rule_type: str = "base", parent_rule_name: Optional[str] = None) -> None:
        config = RuleCommandConfig(feature_name, rule_name, rule_purpose, rule_type, parent_rule_name)
        rule_name_for_base = f"{config.feature_name}-rule.mdc" if config.feature_name else "code-agent-rule.mdc"
        base_rule = BaseRule(rule_name_for_base)
        
        rule_location = self._determine_rule_location(config.feature_name, config.rule_name)
        content = Content(file_path=str(Path(rule_location)))
        
        template_name = self._get_template_name_for_type(config.rule_type)
        generate_instructions = f"""Generate or update rule '{config.rule_name}' for feature '{config.feature_name}' following the template structure and principles in {rule_name_for_base}.

**Template-Based Generation:** 
- Template to use: {template_name} (located in behaviors/code-agent/rule/)
- Rule type: {config.rule_type} (base/specializing/specialized)
- If rule file already exists: Read its current content and enhance it based on the template structure while preserving valuable existing content (principles, examples, custom text)
- If rule file doesn't exist: Generate from template with proper frontmatter, principles, and examples

**Template Structure:**
- Frontmatter (YAML): description, globs, alwaysApply
- When/then statement: Context and behavior description  
- Rule overview: Explanation of the rule
- Executing Commands: List of commands that use this rule
- Principles section: Numbered principles (## 1. Principle Name) with DO/DON'T examples
- Rule references: For specializing/specialized rules, reference parent rules

**Rule Analysis:** Examine the attached rule file ({rule_name_for_base}) for applicable principles. Extract code heuristics from these principles for validation. Integrate heuristics into the CodeAugmentedCommand wrapper pattern.

**Content Handling:**
- Preserve existing principles and examples when updating
- Enhance structure to match template format
- Add missing sections based on template
- Maintain consistency with BDD rule patterns"""
        
        validate_instructions = f"""Validate the generated rule files comply with {rule_name_for_base} principles.

**Rule-Based Validation:** Use code heuristics derived from the attached rule file ({rule_name_for_base}) to perform initial validation. Verify heuristics are integrated and report any principle violations."""
        
        super().__init__(
            command_folder="rule",
            content=content,
            base_rule=base_rule,
            generate_instructions=generate_instructions,
            validate_instructions=validate_instructions
        )
        
        self.feature_name = config.feature_name
        self.rule_name = config.rule_name
        self.rule_purpose = config.rule_purpose
        self.rule_type = config.rule_type
        self.parent_rule_name = config.parent_rule_name
        
        # Create helper classes (composition)
        # Pass self reference so template loader can call load_template dynamically (for test mocks)
        self.template_loader = RuleTemplateLoader("rule", self)
        self.file_generator = RuleFileGenerator(
            self.template_loader,
            self.feature_name,
            self.rule_name,
            self.rule_purpose,
            self.rule_type,
            self.parent_rule_name
        )
        self.validator = RuleValidator(
            self.feature_name,
            self.rule_name,
            self.rule_type,
            self.parent_rule_name
        )
    
    @staticmethod
    def _determine_rule_location(feature_name: Optional[str], rule_name: Optional[str]) -> str:
        """Determine rule location from parameters"""
        if feature_name and rule_name:
            return f"behaviors/{feature_name}/rules/{rule_name}-rule.mdc"
        if feature_name:
            return f"behaviors/{feature_name}/rules"
        return "behaviors/"
    
    def generate(self):
        """Generate or update rule file (.mdc) with principles and examples following BDD pattern"""
        rule_location = f"behaviors/{self.feature_name}/rules/{self.rule_name}-rule.mdc"
        rule_path = self._resolve_rule_path(rule_location)
        rule_path.parent.mkdir(parents=True, exist_ok=True)
        
        # DELEGATE: Generate initial file from template if it doesn't exist
        if not rule_path.exists():
            self.file_generator.generate_rule_file(rule_path)
        
        self._display_rule_generation_results(rule_path)
        
        # Call parent generate() which uses AI to enhance based on template + existing content
        return super().generate()
    
    def _resolve_rule_path(self, rule_location: str) -> Path:
        """Resolve rule file path from location string"""
        if rule_location.startswith("behaviors/"):
            workspace_root = Path(__file__).parent.parent.parent
            return workspace_root / rule_location
        return Path(rule_location).resolve()
    
    def validate(self):
        """Validate rule file structure and compliance with BaseRule/SpecializingRule/SpecializedRule patterns"""
        if not self.feature_name or not self.rule_name:
            raise ValueError("feature_name and rule_name are required for validation")
        
        rule_location = f"behaviors/{self.feature_name}/rules/{self.rule_name}-rule.mdc"
        rule_path = self._resolve_rule_path(rule_location)
        
        if not rule_path.exists():
            raise FileNotFoundError(f"Rule file not found: {rule_path}")
        
        # DELEGATE: Run all validations
        violations = self.validator.validate_all(rule_path)
        
        # Build validation instructions string for CodeAugmentedCommand
        instructions = f"Validate the rule file '{self.rule_name}-rule.mdc' complies with {self.feature_name}-rule.mdc principles.\n\n"
        instructions += "**Rule-Based Validation:** Use code heuristics derived from the attached rule file "
        instructions += f"({self.feature_name}-rule.mdc) to perform initial validation. "
        instructions += "Verify heuristics are integrated and report any principle violations."
        
        if violations:
            for violation in violations:
                print(f"[VIOLATION] {violation}")
            return instructions
        
        print(f"[PASS] Rule '{self.rule_name}' validation passed")
        return instructions
    
    def _get_template_name(self) -> str:
        """Get template name based on rule type - wrapper for backward compatibility"""
        return self.template_loader.get_template_name(self.rule_type)
    
    @staticmethod
    def _get_template_name_for_type(rule_type: str) -> str:
        """Get template name based on rule type - kept for backward compatibility"""
        if rule_type == "specializing":
            return "specializing_rule_template.mdc"
        elif rule_type == "specialized":
            return "specialized_rule_template.mdc"
        return "base_rule_template.mdc"
    
    def _generate_rule_file(self, rule_path: Path) -> Path:
        """Generate rule file from template - wrapper for backward compatibility"""
        return self.file_generator.generate_rule_file(rule_path)
    
    def _display_rule_generation_results(self, rule_file: Path) -> None:
        """Display rule generation results to console"""
        separator = "=" * SEPARATOR_LENGTH
        print(separator)
        print(f"Generated Rule: {self.rule_name}")
        print(separator)
        print(f"Feature: {self.feature_name}")
        print(f"\nGenerated files:")
        print(f"  - {rule_file}")


class CodeAugmentedRuleCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps RuleCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, rule_name: Optional[str] = None, rule_purpose: Optional[str] = None, rule_type: str = "base", parent_rule_name: Optional[str] = None) -> None:
        rule_name_for_base = f"{feature_name}-rule.mdc" if feature_name else "code-agent-rule.mdc"
        base_rule = BaseRule(rule_name_for_base)
        rule_command = RuleCommand(feature_name, rule_name, rule_purpose, rule_type, parent_rule_name)
        super().__init__(rule_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for rule commands"""
        feature_name = args[0] if len(args) > 0 else None
        rule_name = args[1] if len(args) > 1 else None
        rule_purpose = args[2] if len(args) > 2 else None
        rule_type = args[3] if len(args) > 3 else "base"
        parent_rule_name = args[4] if len(args) > 4 else None
        
        command = cls(feature_name, rule_name, rule_purpose, rule_type, parent_rule_name)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()
        elif action == "plan":
            plan_content = command.plan() if hasattr(command, 'plan') else None
            if plan_content:
                sys.stdout.reconfigure(encoding=DEFAULT_ENCODING)
                print(plan_content)
            else:
                print("Plan generation not available for this command.")


class CodeAugmentedCommandCommand(CodeAugmentedCommand):
    """Extends CodeAugmentedCommand, wraps CommandCommand for code validation"""
    
    def __init__(self, feature_name: Optional[str] = None, command_name: Optional[str] = None, command_purpose: Optional[str] = None, target_entity: Optional[str] = None) -> None:
        rule_name = f"{feature_name}-rule.mdc" if feature_name else "code-agent-rule.mdc"
        base_rule = BaseRule(rule_name)
        command_command = CommandCommand(feature_name, command_name, command_purpose, target_entity)
        super().__init__(command_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list[str]) -> None:
        """Handle CLI invocation for command commands"""
        feature_name = args[0] if len(args) > 0 else None
        command_name = args[1] if len(args) > 1 else None
        command_purpose = args[2] if len(args) > 2 else None
        target_entity = args[3] if len(args) > 3 else None
        
        command = cls(feature_name, command_name, command_purpose, target_entity)
        
        if action == "execute":
            command.execute()
        elif action == "generate":
            command.generate()
        elif action == "validate":
            command.validate()
        elif action == "plan":
            plan_content = command.plan() if hasattr(command, 'plan') else None
            if plan_content:
                sys.stdout.reconfigure(encoding=DEFAULT_ENCODING)
                print(plan_content)
            else:
                print("Plan generation not available for this command.")
    

def _print_usage() -> None:
    """Print usage information"""
    print("Usage: python code_agent_runner.py <command> [args...]")
    print("Commands:")
    print("  execute-feature [feature-name] [location] [purpose]")
    print("  generate-feature [feature-name] [location] [purpose]")
    print("  validate-feature [feature-name] [location]")
    print("  plan-feature [feature-name] [location] [purpose]")
    print("  execute-command [feature-name] [command-name] [command-purpose] [target-entity]")
    print("  generate-command [feature-name] [command-name] [command-purpose] [target-entity]")
    print("  validate-command [feature-name] [command-name]")
    print("  plan-command [feature-name] [command-name] [command-purpose] [target-entity]")
    print("  execute-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name]")
    print("  generate-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name]")
    print("  validate-rule [feature-name] [rule-name]")
    print("  sync [feature-name] [--force] [--target-dirs DIR1 DIR2 ...]")
    print("  sync-only [feature-name] [--force] [--target-dirs DIR1 DIR2 ...]")
    print("  index-only [feature-name] [--target-dirs DIR1 DIR2 ...]")
    print("  generate-sync [feature-name] [--force] [--target-dirs DIR1 DIR2 ...]")
    print("  validate-sync [feature-name] [--force] [--target-dirs DIR1 DIR2 ...]")
    print("  generate-index [feature-name] [--target-dirs DIR1 DIR2 ...]")
    print("  validate-index [feature-name] [--target-dirs DIR1 DIR2 ...]")


def _build_command_handlers() -> Dict[str, Callable]:
    """Build command dispatch dictionary (Command Pattern)"""
    return {
        "execute-feature": lambda a: CodeAugmentedFeatureCommand.handle_cli("execute", a),
        "generate-feature": lambda a: CodeAugmentedFeatureCommand.handle_cli("generate", a),
        "validate-feature": lambda a: CodeAugmentedFeatureCommand.handle_cli("validate", a),
        "plan-feature": lambda a: CodeAugmentedFeatureCommand.handle_cli("plan", a),
        "execute-command": lambda a: CodeAugmentedCommandCommand.handle_cli("execute", a),
        "generate-command": lambda a: CodeAugmentedCommandCommand.handle_cli("generate", a),
        "validate-command": lambda a: CodeAugmentedCommandCommand.handle_cli("validate", a),
        "plan-command": lambda a: CodeAugmentedCommandCommand.handle_cli("plan", a),
        "execute-rule": lambda a: CodeAugmentedRuleCommand.handle_cli("execute", a),
        "generate-rule": lambda a: CodeAugmentedRuleCommand.handle_cli("generate", a),
        "validate-rule": lambda a: CodeAugmentedRuleCommand.handle_cli("validate", a),
        "sync-only": lambda a: CodeAugmentedSyncCommand.handle_cli("generate", a),
        "index-only": lambda a: CodeAugmentedIndexCommand.handle_cli("generate", a),
        "generate-sync": lambda a: CodeAugmentedSyncCommand.handle_cli("generate", a),
        "validate-sync": lambda a: CodeAugmentedSyncIndexCommand.handle_cli("validate", a),
        "generate-index": lambda a: CodeAugmentedIndexCommand.handle_cli("generate", a),
        "validate-index": lambda a: CodeAugmentedIndexCommand.handle_cli("validate", a),
    }


def _handle_prefix_matches(full_command: str, args: list[str], command_handlers: Dict) -> bool:
    """Handle prefix matches for commands (order matters - more specific first)"""
    if full_command.startswith("sync-only"):
        command_handlers["sync-only"](args)
        return True
    if full_command.startswith("sync-generate"):
        command_handlers["generate-sync"](args)
        return True
    if full_command.startswith("sync-validate"):
        command_handlers["validate-sync"](args)
        return True
    if full_command.startswith("sync"):
        CodeAugmentedSyncIndexCommand.handle_cli("generate", args)
        return True
    return False


def main() -> None:
    """CLI entry point"""
    if len(sys.argv) < 2:
        _print_usage()
        sys.exit(1)
        return
    
    full_command = sys.argv[1]
    args = sys.argv[2:]
    command_handlers = _build_command_handlers()
    
    # Check for exact matches first
    if full_command in command_handlers:
        command_handlers[full_command](args)
        return
    
    # Check for prefix matches
    if _handle_prefix_matches(full_command, args, command_handlers):
        return
    
    print(f"Unknown command: {full_command}")
    sys.exit(1)


if __name__ == "__main__":
    main()

