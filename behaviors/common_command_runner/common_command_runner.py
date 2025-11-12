

from pathlib import Path
import re
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================

class RunStatus(Enum):
    
    STARTED = "started"              # Work began, not verified
    AI_VERIFIED = "ai_verified"      # AI ran validation, passed
    HUMAN_APPROVED = "human_approved"  # Human reviewed and approved
    COMPLETED = "completed"          # Fully complete
    ABANDONED = "abandoned"          # Run was abandoned


class StepType(Enum):
    
    # New modular workflow steps
    DOMAIN_SCAFFOLD = "domain_scaffold"  # Stage 0: Hierarchy generation
    SIGNATURES = "signatures"             # Stage 1: Add "it should..." statements
    RED = "red"                           # Stage 2: Failing tests
    GREEN = "green"                       # Stage 3: Minimal implementation
    REFACTOR = "refactor"                 # Stage 4: Code improvements
    
    # Legacy step types (for backward compatibility)
    SAMPLE = "sample"                     # Any sample (Phase 0) - actual name in context
    EXPAND = "expand"                     # Expand to full scope (Phase 0)
    RED_BATCH = "red_batch"               # RED phase batch
    GREEN_BATCH = "green_batch"           # GREEN phase batch
    REFACTOR_SUGGEST = "refactor_suggest"     # REFACTOR suggest
    REFACTOR_IMPLEMENT = "refactor_implement" # REFACTOR implement


# ============================================================================
# COMMON DOMAIN MODEL
# ============================================================================

class Content:
    
    def __init__(self, file_path='test.py', file_extension='.py', content_lines=None):
        self.file_path = file_path
        self.file_extension = file_extension
        self.violations = []
        self._content_lines = content_lines  # Optional: pre-loaded content lines
    
    def get_code_snippet(self, line_number: int, context_lines: int = 3) -> Optional[str]:
        
        if not self._ensure_content_loaded():
            return None
        
        start_line, end_line = self._calculate_snippet_bounds(line_number, context_lines)
        return self._build_snippet_with_line_numbers(start_line, end_line, line_number)
    
    def _ensure_content_loaded(self):
        
        if self._content_lines is None:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return False
        
        return bool(self._content_lines)
    
    def _calculate_snippet_bounds(self, line_number, context_lines):
        
        start_line = max(1, line_number - context_lines)
        end_line = min(len(self._content_lines), line_number + context_lines)
        return start_line, end_line
    
    def _build_snippet_with_line_numbers(self, start_line: int, end_line: int, violation_line: int) -> str:
        
        snippet_lines = []
        for i in range(start_line - 1, end_line):
            line_num = i + 1
            marker = ">>>" if line_num == violation_line else "   "
            snippet_lines.append(f"{marker} {line_num:4d} | {self._content_lines[i].rstrip()}")
        return "\n".join(snippet_lines)
    
    def apply_fixes(self):
        
        self.violations = []


class RuleParser:
    
    def read_file_content(self, file_path: str) -> Optional[str]:
        rule_path = Path(file_path)
        if not rule_path.exists():
            return None
        
        with open(rule_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def find_principle_matches(self, content: str):
        pattern = r'^##\s+(\d+)(?:\.\d+)*\.\s+(.+)$'
        return list(re.finditer(pattern, content, re.MULTILINE))
    
    def extract_principle_content(self, content: str, match, matches: list, index: int) -> str:
        start_pos = match.end()
        if index + 1 < len(matches):
            end_pos = matches[index + 1].start()
        else:
            end_pos = len(content)
        return content[start_pos:end_pos].strip()
    
    def extract_do_example(self, section_content: str):
        do_pattern = r'\*\*✅\s+DO:\*\*|\*\*\[DO\]:\*\*|✅\s+DO:|\[DO\]:'
        do_match = re.search(do_pattern, section_content, re.IGNORECASE)
        if not do_match:
            return None, None
        
        text_start = do_match.end()
        code_block_match = re.search(r'```', section_content[text_start:], re.DOTALL)
        if code_block_match:
            text_content = section_content[text_start:text_start + code_block_match.start()].strip()
        else:
            text_content = ""
        
        code_content = self.extract_code_block(section_content[do_match.end():])
        
        return text_content, code_content
    
    def extract_dont_example(self, section_content: str):
        dont_pattern = r'\*\*❌\s+DON\'T:\*\*|\*\*\[DON\'T\]:\*\*|❌\s+DON\'T:|\[DON\'T\]:'
        dont_match = re.search(dont_pattern, section_content, re.IGNORECASE)
        if not dont_match:
            return None, None
        
        text_start = dont_match.end()
        code_block_match = re.search(r'```', section_content[text_start:], re.DOTALL)
        if code_block_match:
            text_content = section_content[text_start:text_start + code_block_match.start()].strip()
        else:
            text_content = ""
        
        code_content = self.extract_code_block(section_content[dont_match.end():])
        
        return text_content, code_content
    
    def extract_code_block(self, content_after_marker: str) -> Optional[str]:
        code_block_match = re.search(r'```[\w]*\n(.*?)```', content_after_marker, re.DOTALL)
        if not code_block_match:
            return None
        return code_block_match.group(1).strip()
    
    def load_examples_from_content(self, section_content: str, principle) -> list:
        examples = []
        try:
            do_text, do_code = self.extract_do_example(section_content)
            dont_text, dont_code = self.extract_dont_example(section_content)
            
            if do_code or dont_code:
                example = Example(
                    principle=principle,
                    do_text=do_text or "",
                    do_code=do_code or "",
                    dont_text=dont_text or "",
                    dont_code=dont_code or ""
                )
                examples.append(example)
        
        except (ValueError, AttributeError, IndexError) as e:
            logger.warning(f"Failed to extract examples from content: {e}")
            raise
        
        return examples
    
    def create_principle_from_match(self, content: str, match, matches: list, index: int):
        principle_number = int(match.group(1))
        principle_name = match.group(2).strip()
        principle_content = self.extract_principle_content(content, match, matches, index)
        
        principle = Principle(
            principle_number=principle_number,
            principle_name=principle_name,
            content=principle_content
        )
        
        examples = self.load_examples_from_content(principle_content, principle)
        principle.examples = examples
        
        return principle
    
    def load_principles_from_file(self, rule_file_name: str) -> list:
        principles = []
        try:
            content = self.read_file_content(rule_file_name)
            if not content:
                return principles
            
            matches = self.find_principle_matches(content)
            for i, match in enumerate(matches):
                principle = self.create_principle_from_match(content, match, matches, i)
                if principle:
                    principles.append(principle)
        
        except (FileNotFoundError, IOError, UnicodeDecodeError) as e:
            logger.error(f"Failed to load principles from {rule_file_name}: {e}")
            raise
        
        return principles


class BaseRule:
    
    def __init__(self, rule_file_name, parser: Optional[RuleParser] = None):
        self.rule_file_name = rule_file_name
        self.principles = []
        self._parser = parser or RuleParser()
        self._load_principles()
    
    def _load_principles(self):
        self.principles = self._parser.load_principles_from_file(self.rule_file_name)
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        return self._parser.read_file_content(file_path)
    
    def _load_examples_from_content(self, section_content: str, principle) -> list:
        return self._parser.load_examples_from_content(section_content, principle)


@dataclass
class FeatureInfo:
    """Information about a deployed feature"""
    name: str
    path: Path
    deployed: bool


class CodeAgentRule(BaseRule):
    """Common rule class for code-agent commands with shared business logic methods"""
    
    DEFAULT_ENCODING = 'utf-8'
    HEADER_LINES_TO_CHECK = 10
    
    def __init__(self, rule_file_name: str = "code-agent-rule.mdc"):
        super().__init__(rule_file_name)
    
    def discover_deployed_features(self, target_dirs: List[Path]) -> List[FeatureInfo]:
        """Scans directories for behavior.json with deployed: true"""
        features = []
        for target_dir in target_dirs:
            if not target_dir.exists():
                continue
            for behavior_json_path in target_dir.rglob("behavior.json"):
                feature_info = self._parse_behavior_json(behavior_json_path)
                if feature_info:
                    features.append(feature_info)
        return features
    
    def _parse_behavior_json(self, behavior_json_path: Path) -> Optional[FeatureInfo]:
        """Parse behavior.json and return FeatureInfo if deployed, None otherwise"""
        try:
            with open(behavior_json_path, 'r', encoding=self.DEFAULT_ENCODING) as f:
                config = json.load(f)
                if config.get("deployed") == True:
                    feature_name = config.get("feature", behavior_json_path.parent.name)
                    return FeatureInfo(
                        name=feature_name,
                        path=behavior_json_path.parent,
                        deployed=True
                    )
        except (json.JSONDecodeError, IOError):
            pass
        return None
    
    def should_exclude_file(self, file_path: Path, exclude_runner_py: bool = False) -> bool:
        """Checks if file should be excluded (docs/, .py files, etc.)"""
        if 'docs' in file_path.parts:
            return True
        if file_path.suffix == '.py':
            if exclude_runner_py and file_path.name.endswith('-runner.py'):
                return True
            elif not exclude_runner_py:
                return True
        if file_path.name == 'behavior.json':
            return True
        if file_path.name.endswith('-index.json'):
            return True
        if '__pycache__' in file_path.parts:
            return True
        return self.is_draft_or_experimental(file_path)
    
    def is_draft_or_experimental(self, file_path: Path) -> bool:
        """Checks file header for draft/experimental markers"""
        try:
            with open(file_path, 'r', encoding=self.DEFAULT_ENCODING) as f:
                first_lines = ''.join(f.readline() for _ in range(self.HEADER_LINES_TO_CHECK))
                return 'draft' in first_lines.lower() or 'experimental' in first_lines.lower()
        except IOError:
            return False
    
    def resolve_target_directories(self, target_dirs: Optional[List[str]], workspace_root: Optional[Path] = None) -> List[Path]:
        """Resolves target directories to absolute paths"""
        if workspace_root is None:
            # Default to behaviors directory relative to common_command_runner location
            workspace_root = Path(__file__).parent.parent
        if target_dirs:
            return [workspace_root / Path(d) if not Path(d).is_absolute() else Path(d) for d in target_dirs]
        return [workspace_root / "behaviors"]


class SpecializingRule:
    
    def __init__(self, base_rule_file_name):
        
        self.base_rule = BaseRule(base_rule_file_name)
        self.base_rule_file_name = base_rule_file_name
        self.specialized_rules = {}
        self._discover_and_load_specialized_rules()
    
    def _read_file_content(self, file_path):
        
        return self.base_rule._read_file_content(file_path)
    
    def _discover_and_load_specialized_rules(self):
        
        base_dir, base_stem = self._get_base_path_info()
        
        for file_path in base_dir.glob(f"{base_stem}-*.mdc"):
            if self._is_specialized_rule_file(file_path, base_stem):
                self._load_specialized_rule(file_path, base_stem)
    
    def _get_base_path_info(self):
        
        base_path = Path(self.base_rule_file_name)
        base_dir = self._get_base_directory(base_path)
        base_stem = base_path.stem
        return base_dir, base_stem
    
    def _get_base_directory(self, base_path):
        
        if base_path.parent != Path('.'):
            return base_path.parent
        return Path('.')
    
    def _is_specialized_rule_file(self, file_path, base_stem):
        
        base_path = Path(self.base_rule_file_name)
        return file_path.name != base_path.name
    
    def _load_specialized_rule(self, file_path, base_stem):
        
        match_key = self._extract_match_key_from_filename(file_path.name, base_stem)
        if not match_key:
            return
        
        specialized_rule = SpecializedRule(rule_file_name=str(file_path), parent=self)
        self.specialized_rules[match_key] = specialized_rule
    
    def _extract_match_key_from_filename(self, filename, base_stem):
        
        # Default: remove base-stem- prefix and .mdc suffix
        if filename.startswith(f"{base_stem}-") and filename.endswith('.mdc'):
            return filename[len(f"{base_stem}-"):-len('.mdc')]
        return None
    
    def get_specialized_rule(self, content):
        
        match_key = self.extract_match_key(content)
        return self.specialized_rules.get(match_key) if match_key else None
    
    def extract_match_key(self, content):
        
        raise NotImplementedError("Subclasses must implement extract_match_key")


class FrameworkSpecializingRule(SpecializingRule):
    
    def extract_match_key(self, content):
        
        if content.file_extension == '.py':
            return 'mamba'
        elif content.file_extension in ['.js', '.ts', '.jsx', '.tsx', '.mjs']:
            return 'jest'
        return None


class SpecializedPrinciple:
    
    def __init__(self, base_principle):
        
        self._base_principle = base_principle
        self.examples = []
        self._specialized_content = None  # Will be set by SpecializedRule when loading from file
    
    @property
    def principle_number(self):
        
        return self._base_principle.principle_number
    
    @property
    def principle_name(self):
        
        return self._base_principle.principle_name
    
    @property
    def content(self):
        
        if self._specialized_content is not None:
            return self._specialized_content
        return self._base_principle.content
    
    @property
    def heuristics(self):
        
        return self._base_principle.heuristics


class SpecializedRule:
    
    def __init__(self, rule_file_name=None, parent=None):
        
        self.parent = parent
        self.examples = []
        self.principles = []
        if rule_file_name and parent:
            self._load_from_file(rule_file_name)
    
    def _load_from_file(self, rule_file_name):
        
        # Get base principles from parent specializing rule
        base_principles = self._get_base_principles()
        
        # Load specialized file content once
        specialized_content = self._read_file_content(rule_file_name)
        if not specialized_content:
            return
        
        # Wrap each base principle and load examples from the specialized rule file
        for base_principle in base_principles:
            specialized_principle = SpecializedPrinciple(base_principle)
            # Extract specialized content for this principle
            specialized_principle._specialized_content = self._extract_principle_content(specialized_content, specialized_principle)
            # Examples are in the specialized rule file itself, not separate files
            examples = self._load_examples(rule_file_name, specialized_principle)
            specialized_principle.examples = examples
            self.principles.append(specialized_principle)
    
    def _extract_principle_content(self, content, specialized_principle):
        
        section_content = self._extract_principle_section_content(content, specialized_principle)
        if not section_content:
            return None
        
        # Find the first example marker (DO or DON'T)
        first_example_pattern = r'\*\*✅\s+DO:\*\*|\*\*\[DO\]:\*\*|✅\s+DO:|\[DO\]:|\*\*❌\s+DON\'T:\*\*|\*\*\[DON\'T\]:\*\*|❌\s+DON\'T:|\[DON\'T\]:'
        first_example_match = re.search(first_example_pattern, section_content, re.IGNORECASE)
        
        if first_example_match:
            # Content is everything before the first example
            content_text = section_content[:first_example_match.start()].strip()
        else:
            # No examples found, use entire section content
            content_text = section_content.strip()
        
        return content_text if content_text else None
    
    def _get_base_principles(self):
        
        if not self.parent:
            return []
        # Return base principles from parent's base rule
        return self.parent.base_rule.principles
    
    def _read_file_content(self, file_path):
        if self.parent:
            return self.parent._read_file_content(file_path)
        return None
    
    def _load_examples(self, specialized_file_name, specialized_principle):
        content = self._read_file_content(specialized_file_name)
        if not content:
            return []
        
        section_content = self._extract_principle_section_content(content, specialized_principle)
        if not section_content:
            return []
        
        if not self.parent or not self.parent.base_rule:
            return []
        
        return self.parent.base_rule._load_examples_from_content(section_content, specialized_principle._base_principle)
    
    def _extract_principle_section_content(self, content, specialized_principle):
        
        principle_match = self._find_principle_match(content, specialized_principle)
        if not principle_match:
            return None
        
        section_start = principle_match.end()
        section_end = self._find_section_end(content, section_start)
        return content[section_start:section_end]
    
    def _find_principle_match(self, content, specialized_principle):
        
        principle_pattern = rf'^##\s+{specialized_principle.principle_number}\.\s+{re.escape(specialized_principle.principle_name)}'
        return re.search(principle_pattern, content, re.MULTILINE)
    
    def _find_section_end(self, content, section_start):
        
        next_principle_match = re.search(r'^##\s+\d+\.\s+', content[section_start:], re.MULTILINE)
        if next_principle_match:
            return section_start + next_principle_match.start()
        return len(content)
    
    
    def _get_specialized_file_name(self, base_file_name, principle_name):
        
        return f"{base_file_name}-{principle_name.lower().replace(' ', '-')}.mdc"


class Principle:
    
    def __init__(self, principle_number=1, principle_name="Test Principle", content=""):
        self.principle_number = principle_number
        self.principle_name = principle_name
        self.content = content
        self.heuristics = []
        self.examples = []
    
    @property
    def number(self):
        
        return self.principle_number
    
    @property
    def name(self):
        
        return self.principle_name


class Example:
    
    def __init__(self, principle=None, do_text="", do_code="", dont_text="", dont_code=""):
        self.principle = principle
        self.do_text = do_text  # Text description for DO
        self.do_code = do_code  # Code example for DO
        self.dont_text = dont_text  # Text description for DON'T
        self.dont_code = dont_code  # Code example for DON'T


class CodeHeuristic:
    
    def __init__(self, detection_pattern="test_pattern"):
        self.detection_pattern = detection_pattern
        self.violations = []
    
    def scan_content(self, content):
        
        if not hasattr(content, 'file_path'):
            return []
        
        detected_violations = self.detect_violations(content)
        return self._normalize_violations(detected_violations)
    
    def _normalize_violations(self, detected_violations):
        
        if not detected_violations:
            return []
        
        if isinstance(detected_violations, list):
            return detected_violations
        else:
            return [detected_violations]
    
    def detect_violations(self, content):
        
        raise NotImplementedError("Subclasses must implement detect_violations()")


class Violation:
    
    def __init__(self, line_number=10, message="Test violation", principle=None, code_snippet=None, severity=None):
        self.line_number = line_number
        self.message = message
        self.principle = principle  # Principle object that this violation relates to
        self.code_snippet = code_snippet  # Offending code snippet
        self.severity = severity  # Severity level if available
        
        # Convenience properties for principle info
        if principle:
            self.principle_number = principle.principle_number if hasattr(principle, 'principle_number') else None
            self.principle_name = principle.principle_name if hasattr(principle, 'principle_name') else None
        else:
            self.principle_number = None
            self.principle_name = None


class ViolationReport:
    
    def __init__(self, violations=None, principles=None, report_format='CHECKLIST'):
        self.violations = violations or []
        self.principles = principles or []
        self.report_format = report_format


class RunState:
    
    def __init__(self, status: str = RunStatus.STARTED.value):
        self.status = status
    
    @property
    def completed(self) -> bool:
        return self.status == RunStatus.COMPLETED.value
    
    @property
    def abandoned(self) -> bool:
        return self.status == RunStatus.ABANDONED.value
    
    @property
    def finished(self) -> bool:
        return self.status in [RunStatus.COMPLETED.value, RunStatus.ABANDONED.value]
    
    @property
    def started(self) -> bool:
        return self.status == RunStatus.STARTED.value
    
    @property
    def ai_verified(self) -> bool:
        return self.status == RunStatus.AI_VERIFIED.value
    
    @property
    def human_approved(self) -> bool:
        return self.status == RunStatus.HUMAN_APPROVED.value


class Run:
    
    def __init__(self, run_number=1, status: str = RunStatus.STARTED.value):
        self.run_number = run_number
        self.state = RunState(status)
        self.completed_at = None
        self.snapshot_before_run = None
        self.sample_size = None
        # BDD-specific fields (optional)
        self.run_id = None
        self.step_type = None
        self.started_at = None
        self.ai_verified_at = None
        self.human_approved_at = None
        self.validation_results = None
        self.human_feedback = None
        self.context = {}
        # Operation tracking
        self.generated_at = None
        self.validated_at = None
    
    def has_been_generated(self) -> bool:
        
        return self.generated_at is not None
    
    def has_been_validated(self) -> bool:
        
        return self.validated_at is not None
    
    def can_proceed_to_next_step(self) -> tuple[bool, str]:
        
        if self.state.completed:
            return (True, "Current run complete")
        
        if self.state.started:
            return (False, "AI must verify before proceeding")
        
        if self.state.ai_verified:
            return (False, "Human must review and approve before proceeding")
        
        if self.state.human_approved:
            return (False, "Run approved but not marked complete. Call complete()")
        
        return (False, f"Unknown status: {self.state.status}")
    
    def verify_ai(self, validation_results: Dict[str, Any] = None):
        
        if not self.state.started:
            raise RuntimeError(
                f"Run {self.run_id} not in STARTED status. "
                f"Current status: {self.state.status}"
            )
        
        if validation_results is None:
            validation_results = {}
        
        self.state.status = RunStatus.AI_VERIFIED.value
        self.ai_verified_at = datetime.now().isoformat()
        self.validation_results = validation_results
    
    def approve(self, feedback: Optional[str] = None):
        
        if not self.state.ai_verified:
            raise RuntimeError(
                f"Run {self.run_id} not AI verified. "
                f"Current status: {self.state.status}. "
                f"AI must verify before human approval."
            )
        
        self.state.status = RunStatus.HUMAN_APPROVED.value
        self.human_approved_at = datetime.now().isoformat()
        self.human_feedback = feedback
    
    def reject(self, feedback: Optional[str] = None):
        
        if not self.state.ai_verified:
            raise RuntimeError(
                f"Run {self.run_id} not AI verified. "
                f"Current status: {self.state.status}. "
                f"AI must verify before rejection."
            )
        
        self.state.status = RunStatus.STARTED.value
        self.ai_verified_at = None
        self.validation_results = None
        self.human_feedback = feedback
    
    def complete(self):
        
        self.state.status = RunStatus.COMPLETED.value
        self.completed_at = datetime.now().isoformat()
    
    def abandon(self, reason: str):
        
        self.state.status = RunStatus.ABANDONED.value
        self.completed_at = datetime.now().isoformat()
        self.human_feedback = reason
    
    def repeat(self, run_history: 'RunHistory') -> 'Run':
        
        next_run_number = (self.run_number + 1) if run_history.runs else 1
        new_run = Run(next_run_number, self.state.status)
        new_run.step_type = self.step_type
        new_run.context = self.context.copy() if self.context else {}
        return new_run
    
    def start(self, step_type: str, context: Dict[str, Any] = None) -> str:
        
        if context is None:
            context = {}
        
        run_id = f"{step_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_id = run_id
        self.step_type = step_type
        self.started_at = datetime.now().isoformat()
        self.context = context
        self.state.status = RunStatus.STARTED.value
        return run_id
    
    def track_execution_timestamps(self, timestamp_attr: Optional[str] = None, generated: bool = False, validated: bool = False) -> None:
        if timestamp_attr:
            if not getattr(self, timestamp_attr, None):
                setattr(self, timestamp_attr, datetime.now().isoformat())
            return
        
        if generated and not self.generated_at:
            self.generated_at = datetime.now().isoformat()
        if validated and not self.validated_at:
            self.validated_at = datetime.now().isoformat()
    
    def get_user_options(self) -> list[str]:
        return ['repeat', 'next', 'abandon', 'expand']
    
    def serialize(self) -> Dict[str, Any]:
        data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        data['status'] = self.state.status
        del data['state']
        return data
    
    @classmethod
    def deserialize(cls, run_data: Dict[str, Any]) -> 'Run':
        status = run_data.get("status", RunStatus.STARTED.value)
        run = cls(run_data.get("run_number", 1), status)
        for key, value in run_data.items():
            if key not in ['run_number', 'status'] and hasattr(run, key) and not key.startswith('_'):
                setattr(run, key, value)
        return run


class RunHistory:
    
    def __init__(self):
        self.runs = []
    
    def find_by_number(self, run_number: int) -> Optional['Run']:
        
        for run in self.runs:
            if run.run_number == run_number:
                return run
        return None
    
    def find_by_id(self, run_id: str) -> Optional['Run']:
        
        for run in self.runs:
            if run.run_id == run_id:
                return run
        return None
    
    def get_completed_count(self) -> int:
        
        return len([r for r in self.runs if r.state.completed])
    
    def get_recent_runs(self, limit: int = 5) -> list['Run']:
        
        return self.runs[-limit:] if self.runs else []
    
    def extract_lessons(self):
        
        return []  # Return empty list for now - would analyze runs and extract lessons


class CommandParams:
    
    def __init__(self, content, base_rule, validate_instructions=None, generate_instructions=None):
        self.content = content
        self.base_rule = base_rule
        self.validate_instructions = validate_instructions or """YOU MUST actively validate the content against ALL principles specified in the rules.

DO NOT only review the code heuristic violations - those are just automated checks.

YOUR VALIDATION MUST:
1. Read and understand ALL principles in the rules
2. Check if the content follows EACH principle
3. Identify violations that code heuristics might have missed
4. Validate meaning, flow, and context - not just syntax
5. Report ALL violations you find, even if not in the heuristic report

The heuristics provide initial findings. YOU must validate comprehensively against the full principles."""
        self.generate_instructions = generate_instructions or "Please generate content according to the rules"


class Command:
    
    def __init__(self, content=None, base_rule=None, validate_instructions=None, generate_instructions=None, params=None):
        
        if params:
            self.content = params.content
            self.base_rule = params.base_rule
            self.validate_instructions = params.validate_instructions
            self.generate_instructions = params.generate_instructions
        else:
            self.content = content
            self.base_rule = base_rule
            self.validate_instructions = validate_instructions or """YOU MUST actively validate the content against ALL principles specified in the rules.

DO NOT only review the code heuristic violations - those are just automated checks.

YOUR VALIDATION MUST:
1. Read and understand ALL principles in the rules
2. Check if the content follows EACH principle
3. Identify violations that code heuristics might have missed
4. Validate meaning, flow, and context - not just syntax
5. Report ALL violations you find, even if not in the heuristic report

The heuristics provide initial findings. YOU must validate comprehensively against the full principles."""
            self.generate_instructions = generate_instructions or "Please generate content according to the rules"
        
        # Track execution state
        self.generated = False
        self.validated = False
        self.corrected = False
    
    def load_template(self, template_path: str) -> str:
        """Load template file content"""
        from pathlib import Path
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_file.read_text(encoding='utf-8')
    
    def fill_template(self, template_content: str, **kwargs) -> str:
        """Fill template placeholders with values using str.format()"""
        return template_content.format(**kwargs)
    
    def load_and_fill_template(self, template_path: str, **kwargs) -> str:
        """Load template and fill placeholders in one step"""
        template_content = self.load_template(template_path)
        return self.fill_template(template_content, **kwargs)
    
    @property
    def principles(self):
        
        return self.base_rule.principles
    
    def generate(self):
        
        instructions = self._build_instructions(self.generate_instructions)
        # Handle Unicode encoding for Windows console
        try:
            print(instructions)
        except UnicodeEncodeError:
            # Fallback: print without emojis/special characters
            print(instructions.encode('ascii', 'ignore').decode('ascii'))
        self.generated = True
        return instructions
    
    def validate(self):
        
        instructions = self._build_instructions(self.validate_instructions)
        # Handle Unicode encoding for Windows console
        try:
            print(instructions)
        except UnicodeEncodeError:
            # Fallback: print without emojis/special characters
            print(instructions.encode('ascii', 'ignore').decode('ascii'))
        self.validated = True
        return instructions
    
    def execute(self):
        
        if not self.generated:
            return self.generate()
        elif not self.validated:
            return self.validate()
        else:
            return self.validate()
    
    def plan(self, plan_template_name: Optional[str] = None, **template_kwargs) -> Optional[str]:
        """
        Optional method to generate an implementation plan.
        
        Subclasses can override this to provide command-specific planning.
        If plan_template_name is provided, this will attempt to load and fill the template.
        Returns None by default if not implemented or if template loading fails.
        """
        return None
    
    def correct(self, chat_context: str) -> str:
        self.corrected = True
        
        next_principle_number = len(self.base_rule.principles) + 1
        content_file = self.content.file_path if self.content else 'Not specified'
        
        # Detect if this is a specializing rule
        rule_type_info = ""
        rule_file_name = getattr(self.base_rule, 'rule_file_name', 'unknown')
        
        # Check for common specializing rule patterns
        if 'bdd-rule' in rule_file_name or 'clean-code-rule' in rule_file_name:
            # Detect framework from content file
            framework = None
            if content_file.endswith('.py'):
                framework = 'Python/Mamba'
                specialized_file = rule_file_name.replace('.mdc', '-mamba.mdc')
            elif content_file.endswith(('.js', '.ts', '.jsx', '.tsx', '.mjs')):
                framework = 'JavaScript/Jest'
                specialized_file = rule_file_name.replace('.mdc', '-jest.mdc')
            
            if framework:
                rule_type_info = f"""
**RULE TYPE: SPECIALIZING RULE**

The base rule '{rule_file_name}' is a specializing rule with framework-specific versions.

**Where to Place Changes:**
- **Base rule** ({rule_file_name}): Add/update principle content (framework-agnostic text only, NO code examples)
- **Specialized rule** ({specialized_file}): Add framework-specific DO/DON'T code examples

**For this correction:**
1. Detected framework: {framework} (from file extension)
2. Principle content goes in: {rule_file_name}
3. Code examples go in: {specialized_file}
4. DO NOT put code examples in the base rule - they belong in specialized rules only

---
"""
        
        instructions = f"""You are correcting the rule file based on an error or pattern observed in chat.
{rule_type_info}
**CONTEXT:**
{chat_context}

**CONTENT FILE:** {content_file}

---

**YOUR TASK: Analyze and Propose Rule Changes**

**Step 1: Check Existing Principles**
Review the current principles and examples below. Determine:
- Do we already have a principle that SHOULD have caught this error?
- Is there an existing example that's similar but didn't prevent the error?
- Is this a completely new pattern not covered by any principle?

**Step 2: Decide Action and Propose**

IF an existing principle should have caught this error:
→ **IMPROVE EXISTING PRINCIPLE**
  1. Identify which principle (by number and name)
  2. Explain why it didn't catch this error
  3. If principle text is unclear, propose improved wording
  4. Propose new or improved example:
     - DON'T: The actual error from the context (show exactly what went wrong)
     - DO: The correct approach (show exactly what should have been done)

IF this is a new pattern not covered by any principle:
→ **ADD NEW PRINCIPLE**
  1. Use principle number: {next_principle_number}
  2. Propose clear, specific principle name
  3. Write principle content explaining the rule
  4. Create example from context:
     - DON'T: The actual error from the context
     - DO: The correct approach

**Step 3: Reverse Engineer Examples from Context**

CRITICAL: Extract examples directly from the context:

A. **For DON'T Example:**
   - Find the ACTUAL error code/text in the context above
   - Copy it EXACTLY as it appeared (don't make up a generic version)
   - If it's a description, convert it to concrete code showing the error
   - Example: If context says "user put unicode in test", show actual test with unicode

B. **For DO Example:**
   - Take the DON'T example and CORRECT it
   - Show the EXACT fix that would prevent the error
   - Don't create an unrelated good example - fix the specific error
   - Example: If DON'T has unicode, DO shows same test without unicode

C. **Follow Existing Format:**
   - Look at examples in the current rule below
   - Match their code style (language, patterns, level of detail)
   - If rule has short examples (1-3 lines), keep yours short
   - If rule has detailed examples (5-10 lines), make yours detailed
   - If rule uses specific naming patterns, use the same patterns
   - Preserve the formatting style: comments, indentation, code structure

**Step 4: Validate Your Proposal**
Before presenting:
1. Check if DO example follows ALL principles in the rule below
2. Check if DON'T example violates ONLY the target principle
3. If examples violate other principles, FIX THEM immediately
4. Repeat until examples are clean

**Step 5: Present Formatted Proposal**

Format as:

**PROPOSAL: [Improve Principle X / Add New Principle {next_principle_number}]**

**Principle:** ## N. Principle Name
[Principle content explaining the rule]

**Example:**
**[DON'T]:**
[Explanation of why this is wrong]
```
[actual error code from context]
```

**[DO]:**
[Explanation of correct approach]
```
[corrected code]
```

**Rationale:** [Explain why this change will prevent future errors]

**Validation:** [Confirm DO follows all principles, DON'T violates only target]

**Optional Heuristic:** [If automated detection makes sense, propose detection pattern]

---

**CURRENT RULE FILE - ANALYZE THESE PRINCIPLES:**

"""
        
        for principle in self.principles:
            instructions += self._format_principle(principle)
            instructions += self._format_examples(principle.examples)
        
        return instructions
    
    def _build_instructions(self, base_instructions):
        
        instructions = f"{base_instructions}. Here are the rules and their examples:\n\n"
        
        for principle in self.principles:
            instructions += self._format_principle(principle)
            instructions += self._format_examples(principle.examples)
        
        return instructions
    
    def _format_principle(self, principle):
        
        return f"## {principle.principle_number}. {principle.principle_name}\n{principle.content}\n\n"
    
    def _format_examples(self, examples):
        
        result = ""
        for example in examples:
            if example.do_code:
                do_text_part = f"{example.do_text}\n" if example.do_text else ""
                result += f"**DO:**\n{do_text_part}```\n{example.do_code}\n```\n\n"
            if example.dont_code:
                dont_text_part = f"{example.dont_text}\n" if example.dont_text else ""
                result += f"**DON'T:**\n{dont_text_part}```\n{example.dont_code}\n```\n\n"
        return result


class CodeAugmentedCommand:
    
    def __init__(self, inner_command, base_rule):
        
        self._inner_command = inner_command
        self.base_rule = base_rule
        self._violations = []
        self._load_heuristics()
    
    def _load_heuristics(self):
        heuristic_map = self._get_heuristic_map()
        if heuristic_map:
            for principle in self.base_rule.principles:
                heuristic_class_or_list = heuristic_map.get(principle.principle_number)
                if heuristic_class_or_list:
                    # Handle both single heuristic and list of heuristics
                    if isinstance(heuristic_class_or_list, list):
                        principle.heuristics = [heuristic_class() for heuristic_class in heuristic_class_or_list]
                    else:
                        principle.heuristics = [heuristic_class_or_list()]
    
    def _get_heuristic_map(self):
        return None
    
    @property
    def content(self):
        
        return self._inner_command.content
    
    @property
    def principles(self):
        
        return self.base_rule.principles
    
    @property
    def violations(self):
        
        return self._violations
    
    def generate(self):
        
        # Call inner command's generate to get instructions with principles/examples
        # Generation doesn't scan for violations - that's only for validation
        return self._inner_command.generate()
    
    def validate(self, report_format='CHECKLIST'):
        
        instructions = self._inner_command.validate()
        self._scan_for_violations()
        
        if self._violations:
            violations_section = self._format_violations(report_format)
            instructions += violations_section
        
        return instructions
    
    def execute(self):
        
        return self._inner_command.execute()
    
    def _scan_for_violations(self):
        
        # CRITICAL: Ensure content is loaded before scanning for violations
        if hasattr(self.content, '_ensure_content_loaded'):
            self.content._ensure_content_loaded()
        
        # DEBUG: Check content loading
        if hasattr(self.content, '_content_lines'):
            print(f"[DEBUG] Content loaded: {len(self.content._content_lines) if self.content._content_lines else 0} lines")
        else:
            print("[DEBUG] Content has no _content_lines attribute")
        
        # DEBUG: Check principles
        print(f"[DEBUG] Scanning {len(self.principles)} principles")
        
        self._violations = []
        for principle in self.principles:
            print(f"[DEBUG] Principle {principle.principle_number}: {len(principle.heuristics) if hasattr(principle, 'heuristics') and principle.heuristics else 0} heuristics")
            if not hasattr(principle, 'heuristics') or not principle.heuristics:
                continue
            for heuristic in principle.heuristics:
                heuristic_name = getattr(heuristic, 'name', type(heuristic).__name__)
                print(f"[DEBUG] Running heuristic: {heuristic_name}")
                heuristic_violations = heuristic.scan_content(self.content)
                print(f"[DEBUG]   Found {len(heuristic_violations)} violations")
                # Enhance violations with principle info and code snippets
                for violation in heuristic_violations:
                    # Attach principle to violation
                    violation.principle = principle
                    violation.principle_number = principle.principle_number if hasattr(principle, 'principle_number') else None
                    violation.principle_name = principle.principle_name if hasattr(principle, 'principle_name') else None
                    # Get code snippet for violation
                    if not violation.code_snippet:
                        violation.code_snippet = self.content.get_code_snippet(violation.line_number) if hasattr(self.content, 'get_code_snippet') else None
                    self._violations.append(violation)
        
        print(f"[DEBUG] Total violations collected: {len(self._violations)}")
    
    def _format_violations(self, report_format):
        
        if report_format == 'CHECKLIST':
            return self._format_violations_as_checklist()
        else:
            return self._format_violations_as_detailed()
    
    def _format_violations_as_checklist(self):
        
        result = "\n\n**Violations Checklist:**\n"
        for violation in self._violations:
            result += f"- [ ] **Line {violation.line_number}:** {violation.message}\n"
            result += self._format_code_snippet(violation.line_number, indent="  ")
        return result
    
    def _format_violations_as_detailed(self):
        
        result = "\n\n**Violations Found:**\n"
        for violation in self._violations:
            result += f"\n**Line {violation.line_number}:** {violation.message}\n"
            result += self._format_code_snippet(violation.line_number, indent="")
        return result
    
    def _format_code_snippet(self, line_number, indent=""):
        
        code_snippet = self.content.get_code_snippet(line_number)
        if not code_snippet:
            return ""
        return f"{indent}```\n{indent}{code_snippet}\n{indent}```\n"
    
    def apply_fixes(self):
        
        # Not implemented yet - placeholder for future AI interaction
        pass
    
    def plan(self, plan_template_name: Optional[str] = None, **template_kwargs) -> Optional[str]:
        """
        Delegate plan generation to inner command.
        If inner command has plan() method, call it; otherwise return None.
        """
        if hasattr(self._inner_command, 'plan'):
            return self._inner_command.plan(plan_template_name, **template_kwargs)
        return None
    
    def __getattr__(self, name):
        
        return getattr(self._inner_command, name)


class SpecializingRuleCommand(Command):
    
    def __init__(self, content, base_rule, specializing_rule, validate_instructions=None, generate_instructions=None):
        
        super().__init__(content, base_rule, validate_instructions, generate_instructions)
        self.specializing_rule = specializing_rule
    
    @property
    def specialized_rule(self):
        
        return self.specializing_rule.get_specialized_rule(self.content)
    
    @property
    def principles(self):
        
        specialized = self.specialized_rule
        if specialized:
            return specialized.principles
        # Fallback to base rule's principles if no specialized rule found
        return self.base_rule.principles
    
    def execute(self):
        
        return super().execute()


# Constants
DEFAULT_MAX_SAMPLE_SIZE = 18
EXPAND_SAMPLE_SIZE = 90
ALL_WORK_COMPLETE_UNITS = 100


class IncrementalCommand:
    
    def __init__(self, inner_command, base_rule, max_sample_size=DEFAULT_MAX_SAMPLE_SIZE, command_file_path: Optional[str] = None):
        
        self._inner_command = inner_command
        self.base_rule = base_rule
        self.max_sample_size = max_sample_size
        self.current_run = None
        self.run_history = RunHistory()
        # Get command file path from content if not provided
        if not command_file_path and hasattr(inner_command, 'content') and hasattr(inner_command.content, 'file_path'):
            command_file_path = inner_command.content.file_path
        self.state = IncrementalState(command_file_path)
        self.completed_work_units = 0
        self._all_work_complete = False
        self._has_more_work = True
        # Load persisted state
        self.current_run = self.state.load(self.run_history)
    
    @property
    def content(self):
        
        return self._inner_command.content
    
    @property
    def sample_size(self) -> Optional[int]:
        
        if self.current_run:
            return self.current_run.sample_size
        return None
    
    def _inject_sample_size(self):
        
        sample_size = self.sample_size
        if not sample_size:
            return
        
        sample_note = f"\n\nNote: Process a sample of {sample_size} items."
        self._inject_instruction_note(sample_note)
    
    def _inject_instruction_note(self, note: str):
        if not hasattr(self._inner_command, '_original_generate_instructions'):
            self._inner_command._original_generate_instructions = self._inner_command.generate_instructions
        if not hasattr(self._inner_command, '_original_validate_instructions'):
            self._inner_command._original_validate_instructions = self._inner_command.validate_instructions
        
        self._inner_command.generate_instructions = self._inner_command.generate_instructions + note
        self._inner_command.validate_instructions = self._inner_command.validate_instructions + note
    
    def _restore_instructions(self):
        
        if hasattr(self._inner_command, '_original_generate_instructions'):
            self._inner_command.generate_instructions = self._inner_command._original_generate_instructions
        if hasattr(self._inner_command, '_original_validate_instructions'):
            self._inner_command.validate_instructions = self._inner_command._original_validate_instructions
    
    def _execute_with_run_tracking(self, command_method_name: str, timestamp_attr: Optional[str] = None):
        
        # Ensure run exists
        if not self.current_run:
            self._ensure_run_exists()
        
        # Inject sample size into instructions
        self._inject_sample_size()
        
        try:
            # Call the inner command method
            method = getattr(self._inner_command, command_method_name)
            result = method()
        finally:
            self._restore_instructions()
        
        if self.current_run:
            self.current_run.track_execution_timestamps(
                timestamp_attr,
                generated=self._inner_command.generated,
                validated=self._inner_command.validated
            )
        
        self.state.save(self.run_history, self.current_run)
        
        return result
    
    def generate(self):
        
        return self._execute_with_run_tracking('generate', 'generated_at')
    
    def execute(self):
        return self._execute_with_run_tracking('execute')
    
    def _create_new_run(self):
        if self.current_run:
            self.current_run.complete()
        
        next_run_number = (self.current_run.run_number + 1) if self.current_run else 1
        self.current_run = Run(next_run_number, RunStatus.STARTED.value)
        if self.sample_size:
            self.current_run.sample_size = self.sample_size
        self.run_history.runs.append(self.current_run)
    
    def _ensure_run_exists(self):
        if not self.current_run:
            self._create_new_run()
    
    def validate(self):
        
        return self._execute_with_run_tracking('validate', 'validated_at')
    
    def expand_to_all_work(self):
        if not self.current_run:
            self._ensure_run_exists()
        self.current_run.sample_size = EXPAND_SAMPLE_SIZE
        self.completed_work_units = ALL_WORK_COMPLETE_UNITS
        
        finish_note = "\n\nPlease finish all remaining work."
        self._inject_instruction_note(finish_note)
        
        try:
            return self._execute_with_run_tracking('execute')
        finally:
            self._restore_instructions()
    
    def is_complete(self):
        
        return not self._has_more_work
    
    def has_more_work_remaining(self):
        
        return self._has_more_work
    
    def proceed_to_next_run(self):
        
        self._create_new_run()
        self.state.save(self.run_history, self.current_run)
    
    def __getattr__(self, name):
        
        return getattr(self._inner_command, name)


class Workflow:
    
    def __init__(self):
        self.phases = []
        self.current_phase_number = 0
        self.can_execute_phase = type('MockCallable', (), {'called': False})()  # Mock callable for testing
    
    def get_current_phase_status(self):
        
        current_phase = self._get_current_phase()
        if not current_phase:
            return None
        
        return self._create_status_report(current_phase)
    
    def _get_current_phase(self):
        
        if not self.phases or self.current_phase_number >= len(self.phases):
            return None
        return self.phases[self.current_phase_number]
    
    def _create_status_report(self, phase):
        
        return type('StatusReport', (), {
            'phase_name': phase.phase_name,
            'phase_number': phase.phase_number
        })()
    
    def mark_phase_complete(self, phase_number):
        
        phase = self._get_phase_by_number(phase_number)
        if phase:
            self._complete_phase(phase, phase_number)
    
    def _get_phase_by_number(self, phase_number):
        
        if phase_number < len(self.phases):
            return self.phases[phase_number]
        return None
    
    def _complete_phase(self, phase, phase_number):
        
        # Don't override APPROVED status - preserve it
        if phase.phase_state.phase_status != "APPROVED":
            phase.phase_state.phase_status = "COMPLETE"
        self.current_phase_number = phase_number + 1
    
    def start_next_phase(self):
        
        next_phase = self._get_next_phase()
        if next_phase:
            next_phase.start()
    
    def _get_next_phase(self):
        
        if self.current_phase_number < len(self.phases):
            return self.phases[self.current_phase_number]
        return None

    def generate(self):
        
        current_phase = self._get_current_phase()
        if current_phase:
            return current_phase.generate()
        return None
    
    def validate(self, report_format='CHECKLIST'):
        
        current_phase = self._get_current_phase()
        if current_phase:
            return current_phase.validate(report_format=report_format)
        return None


class PhaseState:
    
    def __init__(self, phase_number=0, phase_status="STARTING"):
        self.phase_number = phase_number
        self.phase_status = phase_status
        self.persisted_at = None
    
    @classmethod
    def load_from_disk(cls, file_path):
        
        # Simplified - would actually load from file
        return cls(phase_number=0, phase_status="STARTING")
    
    def persist_to_disk(self):
        
        self.persisted_at = "now"  # Simplified - would save to actual file
    
    def determine_next_action(self):
        
        if self.phase_status == "COMPLETE":
            return "PROCEED_TO_NEXT_PHASE"
        return "CONTINUE"


class WorkflowPhaseCommandParams:
    
    def __init__(self, inner_command, workflow, phase_number, phase_name):
        self.inner_command = inner_command
        self.workflow = workflow
        self.phase_number = phase_number
        self.phase_name = phase_name


class WorkflowPhaseCommand:
    
    def __init__(self, inner_command=None, workflow=None, phase_number=None, phase_name=None, params=None):
        
        if params:
            self._inner_command = params.inner_command
            self.workflow = params.workflow
            self.phase_number = params.phase_number
            self.phase_name = params.phase_name
        else:
            self._inner_command = inner_command
            self.workflow = workflow
            self.phase_number = phase_number
            self.phase_name = phase_name
        self.phase_state = PhaseState(self.phase_number, "STARTING")
        self.can_execute = True
        self._start_called = False
    
    @property
    def content(self):
        
        return self._inner_command.content
    
    @property
    def name(self):
        
        if hasattr(self._inner_command, 'name'):
            return self._inner_command.name
        return self.phase_name
    
    @property
    def current_phase(self):
        
        return self.phase_number
    
    def start(self):
        
        self._execute_phase_callback()
        self.phase_state.phase_status = "IN_PROGRESS"
        self._start_called = True
    
    def approve(self):
        
        self.phase_state.phase_status = "APPROVED"
        self.workflow.mark_phase_complete(self.phase_number)
    
    def proceed_to_next_phase(self):
        
        if self._has_next_phase():
            self._advance_to_next_phase()
    
    def block_execution(self, reason):
        
        self.can_execute = False
        self.phase_state.phase_status = "BLOCKED"
    
    def _has_next_phase(self):
        
        return self.phase_number + 1 < len(self.workflow.phases)
    
    def _advance_to_next_phase(self):
        
        self.workflow.current_phase_number = self.phase_number + 1
        self.workflow.start_next_phase()
    
    def _execute_phase_callback(self):
        
        if not self.workflow.can_execute_phase:
            return
        
        if hasattr(self.workflow.can_execute_phase, '__call__'):
            self.workflow.can_execute_phase(self.phase_number)
        elif hasattr(self.workflow.can_execute_phase, 'called'):
            self.workflow.can_execute_phase.called = True
    
    def resume_from_phase(self):
        
        # Load state from disk (simplified)
        # In real implementation, would load from file
        self._start_called = True
    
    def __getattr__(self, name):
        
        return getattr(self._inner_command, name)


class IncrementalState:
    
    def __init__(self, command_file_path: Optional[str] = None):
        self.command_file_path = command_file_path
        self.persisted_at = None
    
    def get_state_file_path(self) -> Optional[Path]:
        
        if not self.command_file_path:
            return None
        
        command_path = Path(self.command_file_path)
        state_dir = command_path.parent / ".incremental-state"
        state_dir.mkdir(exist_ok=True)
        return state_dir / f"{command_path.stem}.state.json"
    
    def load(self, run_history: 'RunHistory') -> Optional['Run']:
        
        state_file = self.get_state_file_path()
        if not state_file or not state_file.exists():
            return None
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            
            run_history.runs = []
            for run_data in state_data.get("runs", []):
                run = Run.deserialize(run_data)
                run_history.runs.append(run)
            
            current_run_id = state_data.get("current_run_id")
            if current_run_id:
                return run_history.find_by_id(current_run_id)
        except (FileNotFoundError, IOError, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to load state from {state_file}: {e}")
            raise
        
        return None
    
    def save(self, run_history: 'RunHistory', current_run: Optional['Run']) -> None:
        state_file = self.get_state_file_path()
        if not state_file:
            return
        
        try:
            runs_data = [run.serialize() for run in run_history.runs]
            
            state_data = {
                "runs": runs_data,
                "current_run_id": current_run.run_id if current_run else None,
                "created_at": datetime.now().isoformat()
            }
            
            state_file.write_text(
                json.dumps(state_data, indent=2),
                encoding='utf-8'
            )
            self.persisted_at = datetime.now().isoformat()
        except (IOError, OSError, TypeError) as e:
            logger.error(f"Failed to save state to {state_file}: {e}")
            raise
