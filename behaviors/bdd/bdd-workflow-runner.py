"""
BDD Workflow - Red-Green-Refactor Cycle
Guides developers through true BDD (Behavior-Driven Development) with Red-Green-Refactor cycle.

Division of Labor:
- Code: Parse files, run tests, track state, identify relationships, ENFORCE workflow
- AI Agent: 
  * Identify SAMPLE SIZE (lowest-level describe block, no more than 6 tests)
  * Write test signatures/implementations
  * Run /bdd-validate after EVERY step
  * Fix ALL violations before proceeding
  * Learn from violations and iterate

CODE ENFORCEMENT:
- Check run state before/after every step
- Block if run not complete (started → ai_verified → human_approved → completed)
- Validate AI ran /bdd-validate
- Require human approval
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Import run state enforcement (module has hyphens in name)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bdd_workflow_run_state",
    Path(__file__).parent / "bdd-workflow-run-state.py"
)
bdd_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bdd_module)
BDDRunState = bdd_module.BDDRunState
StepType = bdd_module.StepType
RunStatus = bdd_module.RunStatus


class BDDPhase(Enum):
    """BDD workflow phases"""
    SIGNATURES = "signatures"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    IMPLEMENT = "implement"


class TestStatus(Enum):
    """Test implementation status"""
    SIGNATURE = "signature"  # Test signature created, not implemented
    RED = "red"              # Test written, failing
    GREEN = "green"          # Test passing
    REFACTOR = "refactor"    # Ready for refactoring
    IMPLEMENTED = "implemented"  # Fully implemented and refactored


class BDDWorkflowState:
    """Tracks BDD workflow state"""
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.state_file = self._get_state_file_path()
        self.state = self._load_state()
    
    def _get_state_file_path(self) -> Path:
        """Get state file path for test file"""
        test_path = Path(self.test_file)
        state_dir = test_path.parent / ".bdd-workflow"
        state_dir.mkdir(exist_ok=True)
        return state_dir / f"{test_path.stem}.state.json"
    
    def _load_state(self) -> Dict[str, Any]:
        """Load workflow state from file"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding='utf-8'))
        return {
            "phase": BDDPhase.SIGNATURES.value,
            "scope": "describe",
            "current_test_index": 0,
            "tests": [],
            "completed_refactorings": []
        }
    
    def save(self):
        """Save workflow state to file"""
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
    
    def update_phase(self, phase: BDDPhase):
        """Update current phase"""
        self.state["phase"] = phase.value
        self.save()
    
    def update_test_status(self, test_index: int, status: TestStatus):
        """Update status of specific test"""
        if test_index < len(self.state["tests"]):
            self.state["tests"][test_index]["status"] = status.value
            self.save()
    
    def add_test(self, test_info: Dict[str, Any]):
        """Add test to state"""
        self.state["tests"].append(test_info)
        self.save()
    
    def get_next_test(self) -> Optional[Tuple[int, Dict[str, Any]]]:
        """Get next unimplemented test"""
        for i, test in enumerate(self.state["tests"]):
            if test["status"] in [TestStatus.SIGNATURE.value, TestStatus.RED.value]:
                return (i, test)
        return None


# Step 1: Detect framework (reuse from bdd-behavior-validate-cmd.py)
def detect_framework_from_file(file_path: str) -> Optional[str]:
    """
    Match file path against rule glob patterns to determine framework.
    Returns: 'jest', 'mamba', or None
    """
    file_path_lower = file_path.lower()
    
    # Jest patterns
    jest_patterns = ['.test.js', '.spec.js', '.test.ts', '.spec.ts', 
                     '.test.jsx', '.spec.jsx', '.test.tsx', '.spec.tsx',
                     '.test.mjs', '.spec.mjs']
    
    # Mamba patterns  
    mamba_patterns = ['_test.py', 'test_', '_spec.py', 'spec_', 
                      '_test.pyi', 'test_.pyi', '_spec.pyi', 'spec_.pyi']
    
    for pattern in jest_patterns:
        if file_path_lower.endswith(pattern):
            return 'jest'
    
    for pattern in mamba_patterns:
        if pattern in file_path_lower:
            return 'mamba'
    
    return None


# Step 2: Parse test file structure
def parse_test_structure(test_file_path: str, framework: str) -> List[Dict[str, Any]]:
    """
    Parse test file and extract describe/it blocks with status.
    
    Returns: [{"line": int, "type": "describe|it", "text": str, "indent": int, 
               "status": TestStatus, "has_implementation": bool}]
    """
    content = Path(test_file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    blocks = []
    for i, line in enumerate(lines, 1):
        indent = len(line) - len(line.lstrip())
        
        if framework == 'jest':
            # Extract describe blocks
            if 'describe(' in line:
                match = re.search(r"describe\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "describe",
                        "text": match.group(1),
                        "indent": indent,
                        "status": None,  # describe blocks don't have status
                        "has_implementation": True  # describes are containers
                    })
            
            # Extract it/test blocks
            elif 'it(' in line or 'test(' in line:
                match = re.search(r"(?:it|test)\(['\"]([^'\"]+)['\"]", line)
                if match:
                    # Detect if test has implementation (not just TODO or empty)
                    has_impl = detect_test_implementation(lines, i, framework)
                    status = TestStatus.IMPLEMENTED if has_impl else TestStatus.SIGNATURE
                    
                    blocks.append({
                        "line": i,
                        "type": "it",
                        "text": match.group(1),
                        "indent": indent,
                        "status": status.value,
                        "has_implementation": has_impl
                    })
        
        elif framework == 'mamba':
            # Extract describe blocks
            if 'with description(' in line or 'with describe(' in line:
                match = re.search(r"with (?:description|describe)\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "describe",
                        "text": match.group(1),
                        "indent": indent,
                        "status": None,
                        "has_implementation": True
                    })
            
            # Extract it blocks
            elif 'with it(' in line:
                match = re.search(r"with it\(['\"]([^'\"]+)['\"]", line)
                if match:
                    has_impl = detect_test_implementation(lines, i, framework)
                    status = TestStatus.IMPLEMENTED if has_impl else TestStatus.SIGNATURE
                    
                    blocks.append({
                        "line": i,
                        "type": "it",
                        "text": match.group(1),
                        "indent": indent,
                        "status": status.value,
                        "has_implementation": has_impl
                    })
    
    return blocks


def detect_test_implementation(lines: List[str], test_line_index: int, framework: str) -> bool:
    """
    Detect if test has actual implementation or just TODO/empty body.
    
    Args:
        lines: All file lines
        test_line_index: Line number of test (1-indexed)
        framework: 'jest' or 'mamba'
    
    Returns: True if test has implementation, False if signature only
    """
    # Look ahead ~20 lines for test body
    start = test_line_index  # Already 1-indexed, but we need 0-indexed
    end = min(start + 20, len(lines))
    
    test_body_lines = lines[start:end]
    
    # Check for TODO markers
    for line in test_body_lines[:5]:  # Check first few lines
        if 'TODO' in line or 'FIXME' in line or 'BDD: SIGNATURE' in line:
            return False
    
    # Check for empty body (just braces/pass)
    non_empty_lines = [l.strip() for l in test_body_lines if l.strip() and not l.strip().startswith('//')]
    
    if framework == 'jest':
        # Jest: look for actual test code (expect, assertions, etc.)
        has_code = any('expect(' in l or 'assert' in l or 'const ' in l or 'let ' in l 
                       for l in non_empty_lines)
        return has_code
    
    elif framework == 'mamba':
        # Mamba: look for actual test code (expect, assertions, etc.)
        has_code = any('expect(' in l or 'assert' in l or '=' in l 
                       for l in non_empty_lines if not l.startswith('pass'))
        return has_code
    
    return False


# Step 3: Determine scope
def determine_test_scope(blocks: List[Dict[str, Any]], scope_option: str, cursor_line: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Determine which tests to work on based on scope option.
    
    Args:
        blocks: All test blocks from parse_test_structure
        scope_option: 'describe', 'next:N', 'all', or 'line:N'
        cursor_line: Current cursor position (for 'describe' scope)
    
    Returns: Filtered list of test blocks in scope
    """
    tests_only = [b for b in blocks if b["type"] == "it"]
    
    if scope_option == "all":
        return tests_only
    
    elif scope_option.startswith("next:"):
        count = int(scope_option.split(":")[1])
        # Find first unimplemented test
        for i, test in enumerate(tests_only):
            if test["status"] == TestStatus.SIGNATURE.value:
                return tests_only[i:i+count]
        return []
    
    elif scope_option.startswith("line:"):
        line_num = int(scope_option.split(":")[1])
        return [t for t in tests_only if t["line"] == line_num]
    
    elif scope_option == "describe":
        if cursor_line is None:
            # No cursor position, use first describe block
            return tests_only
        
        # Find describe block containing cursor
        current_describe = None
        for block in blocks:
            if block["type"] == "describe" and block["line"] <= cursor_line:
                current_describe = block
            elif block["type"] == "describe" and block["line"] > cursor_line:
                break
        
        if not current_describe:
            return tests_only
        
        # Find all tests within this describe block
        describe_indent = current_describe["indent"]
        start_line = current_describe["line"]
        
        # Find end of describe block (next describe at same or lower indent)
        end_line = float('inf')
        for block in blocks:
            if (block["line"] > start_line and 
                block["type"] == "describe" and 
                block["indent"] <= describe_indent):
                end_line = block["line"]
                break
        
        return [t for t in tests_only if start_line < t["line"] < end_line]
    
    return tests_only


# Step 4: Run tests
def run_tests(test_file_path: str, framework: str, single_test_line: Optional[int] = None) -> Dict[str, Any]:
    """
    Run tests and capture results.
    
    Args:
        test_file_path: Path to test file
        framework: 'jest' or 'mamba'
        single_test_line: If provided, run only test at this line
    
    Returns: {"success": bool, "output": str, "passed": int, "failed": int, "error": Optional[str]}
    """
    try:
        if framework == 'jest':
            cmd = ['npm', 'test', '--', test_file_path]
            if single_test_line:
                # Jest can run specific test by line number
                cmd.extend(['-t', str(single_test_line)])
        
        elif framework == 'mamba':
            cmd = ['mamba', test_file_path]
            if single_test_line:
                # Mamba runs specific test by line
                cmd.extend(['--line', str(single_test_line)])
        
        else:
            return {"success": False, "error": f"Unknown framework: {framework}"}
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Parse output for pass/fail counts
        output = result.stdout + result.stderr
        passed = len(re.findall(r'✓|PASS|passed', output, re.IGNORECASE))
        failed = len(re.findall(r'✗|FAIL|failed', output, re.IGNORECASE))
        
        return {
            "success": result.returncode == 0,
            "output": output,
            "passed": passed,
            "failed": failed,
            "error": None if result.returncode == 0 else "Tests failed"
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Test execution timed out", "output": "", "passed": 0, "failed": 0}
    except Exception as e:
        return {"success": False, "error": str(e), "output": "", "passed": 0, "failed": 0}


# Step 5: Identify code relationships
def identify_code_relationships(test_file_path: str) -> Dict[str, List[str]]:
    """
    Identify code under test and other test files related to this test.
    
    Returns: {"code_under_test_files": [...], "related_tests": [...]}
    """
    test_path = Path(test_file_path)
    test_content = test_path.read_text(encoding='utf-8')
    
    # Extract imports
    imports = re.findall(r"import .+ from ['\"]([^'\"]+)['\"]", test_content)
    imports += re.findall(r"require\(['\"]([^'\"]+)['\"]\)", test_content)
    
    code_under_test_files = []
    related_tests = []
    
    for imp in imports:
        # Skip node_modules
        if imp.startswith('.'):
            # Relative import
            resolved = (test_path.parent / imp).resolve()
            
            # Try common extensions
            for ext in ['.js', '.ts', '.mjs', '.jsx', '.tsx', '.py']:
                candidate = Path(str(resolved) + ext)
                if candidate.exists():
                    if any(pattern in candidate.name for pattern in ['test', 'spec', '_test', 'test_']):
                        related_tests.append(str(candidate))
                    else:
                        code_under_test_files.append(str(candidate))
                    break
    
    return {
        "code_under_test_files": code_under_test_files,
        "related_tests": related_tests
    }


# ============================================================================
# RUN STATE ENFORCEMENT FUNCTIONS
# ============================================================================

def check_can_start_run(run_state: BDDRunState) -> None:
    """
    Enforce that a new run can be started.
    Raises RuntimeError if previous run not complete.
    """
    try:
        run_state.enforce_can_proceed()
    except RuntimeError as e:
        print("\n" + "="*60)
        print("❌ CANNOT START NEW RUN")
        print("="*60)
        print(str(e))
        print("\nTo fix:")
        print("1. If AI hasn't verified: Run /bdd-validate")
        print("2. If AI verified: Type 'proceed' to approve")
        print("3. If stuck: Call abandon_run() to reset")
        print("="*60)
        raise


def record_validation_results(
    run_state: BDDRunState,
    validation_output: str,
    passed: bool
) -> None:
    """
    Record that AI ran /bdd-validate.
    """
    current_run = run_state.get_current_run()
    if not current_run:
        raise RuntimeError("No active run to record validation for")
    
    validation_results = {
        "passed": passed,
        "output": validation_output,
        "timestamp": datetime.now().isoformat()
    }
    
    run_state.record_ai_verification(
        current_run["run_id"],
        validation_results
    )
    
    print(f"\n✅ AI verification recorded for run {current_run['run_id']}")


def wait_for_human_approval(run_state: BDDRunState) -> None:
    """
    Wait for human to approve the run.
    Blocks until 'proceed' or 'reject' received.
    """
    current_run = run_state.get_current_run()
    if not current_run:
        raise RuntimeError("No active run waiting for approval")
    
    status = current_run["status"]
    
    if status != RunStatus.AI_VERIFIED.value:
        raise RuntimeError(
            f"Run not ready for approval. Status: {status}. "
            f"AI must verify first."
        )
    
    print("\n" + "="*60)
    print("🛑 WAITING FOR HUMAN APPROVAL")
    print("="*60)
    print(f"Run ID: {current_run['run_id']}")
    print(f"Step: {current_run['step_type']}")
    print("\nType 'proceed' to approve and continue")
    print("Type 'reject' to send back to AI for fixes")
    print("="*60)
    
    # This function signals that human input is needed
    # Actual approval is recorded via separate command


# Main BDD workflow orchestrator
def bdd_workflow(
    file_path: str,
    scope: str = "describe",
    phase: Optional[str] = None,
    cursor_line: Optional[int] = None,
    auto: bool = False
) -> Dict[str, Any]:
    """
    Main BDD workflow function.
    
    Args:
        file_path: Path to test file
        scope: 'describe', 'next:N', 'all', 'line:N'
        phase: Optional phase to jump to ('signatures', 'red', 'green', 'refactor')
        cursor_line: Current cursor position (for 'describe' scope)
        auto: Automatic mode (no prompts)
    
    Returns: Workflow data for AI Agent to process
    """
    print("\n=== BDD Workflow Starting ===")
    
    # Step 1: Validate file
    test_path = Path(file_path)
    if not test_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    print(f"✅ File: {test_path.name}")
    
    # Step 2: Detect framework
    framework = detect_framework_from_file(file_path)
    if not framework:
        return {"error": f"Not a valid BDD test file: {file_path}"}
    
    print(f"✅ Framework: {framework.upper()}")
    
    # Step 3: Load or initialize workflow state AND run state
    workflow_state = BDDWorkflowState(file_path)
    run_state = BDDRunState(file_path)
    
    # Step 3a: CHECK RUN STATE - Can we proceed?
    try:
        check_can_start_run(run_state)
    except RuntimeError:
        # Cannot proceed - return error with status
        return {
            "error": "Cannot proceed - previous run not complete",
            "run_status": run_state.get_status_summary()
        }
    
    # Step 4: Parse test structure
    print("Parsing test structure...")
    blocks = parse_test_structure(file_path, framework)
    tests = [b for b in blocks if b["type"] == "it"]
    
    print(f"✅ Found {len(tests)} tests")
    
    # Step 5: Determine scope
    scoped_tests = determine_test_scope(blocks, scope, cursor_line)
    implemented = len([t for t in scoped_tests if t["has_implementation"]])
    signatures = len([t for t in scoped_tests if not t["has_implementation"]])
    
    print(f"✅ Scope: {scope}")
    print(f"   {len(scoped_tests)} tests in scope ({implemented} implemented, {signatures} signatures)")
    
    # Step 6: Determine current phase
    if phase:
        current_phase = BDDPhase(phase)
    else:
        current_phase = BDDPhase(workflow_state.state["phase"])
    
    print(f"✅ Phase: {current_phase.value.upper()}")
    
    # Step 7: Identify code relationships
    print("Identifying code relationships...")
    relationships = identify_code_relationships(file_path)
    print(f"   {len(relationships['code_under_test_files'])} code under test files")
    print(f"   {len(relationships['related_tests'])} related test files")
    
    # Step 8: Get next test to work on
    next_test = None
    if current_phase in [BDDPhase.RED, BDDPhase.GREEN, BDDPhase.REFACTOR]:
        for i, test in enumerate(scoped_tests):
            if not test["has_implementation"]:
                next_test = (i, test)
                break
    
    # Step 9: Prepare data for AI Agent
    workflow_data = {
        "file_path": file_path,
        "framework": framework,
        "phase": current_phase.value,
        "scope": scope,
        "auto_mode": auto,
        "test_structure": {
            "all_blocks": blocks,
            "scoped_tests": scoped_tests,
            "next_test": next_test
        },
        "state": workflow_state.state,
        "relationships": relationships,
        "commands": {
            "run_all_tests": f"python -c \"import bdd_workflow_runner; print(bdd_workflow_runner.run_tests('{file_path}', '{framework}'))\"",
            "run_single_test": f"python -c \"import bdd_workflow_runner; print(bdd_workflow_runner.run_tests('{file_path}', '{framework}', {{line}}))\""
        }
    }
    
    print("\n" + "="*60)
    print("READY FOR AI AGENT")
    print("="*60)
    print(f"Phase: {current_phase.value.upper()}")
    if current_phase == BDDPhase.SIGNATURES:
        print("\nAI Agent TODO:")
        print("1. Identify SAMPLE SIZE (lowest-level describe, max 6 tests)")
        print("2. Create sample test signatures")
        print("3. Run /bdd-validate")
        print("4. Fix violations, learn, iterate")
    if next_test:
        print(f"\nNext Test: Line {next_test[1]['line']} - '{next_test[1]['text']}'")
    print("="*60)
    
    return workflow_data


if __name__ == "__main__":
    import sys
    import io
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python behaviors/bdd/bdd-workflow-runner.py <test-file-path> [step-type] [options]")
        print("\nStep Types (optional, defaults to sample_1):")
        print("  sample_N   - Behavioral example (any number: sample_1, sample_2, sample_3, ...)")
        print("  expand     - Expand to full test coverage")
        print("  red        - RED phase (write failing tests)")
        print("  green      - GREEN phase (implement code)")
        print("  refactor   - REFACTOR phase")
        print("\nOptions:")
        print("  --scope describe|next:N|all|line:N  (default: describe)")
        print("  --phase signatures|red|green|refactor")
        print("  --line N                             Cursor line number")
        print("  --auto                               Automatic mode")
        print("\nExamples:")
        print("  python behaviors/bdd/bdd-workflow-runner.py test.mjs sample_1")
        print("  python behaviors/bdd/bdd-workflow-runner.py test.mjs sample_2")
        print("  python behaviors/bdd/bdd-workflow-runner.py test.mjs sample_5")
        print("  python behaviors/bdd/bdd-workflow-runner.py test.mjs expand --scope all")
        print("  python behaviors/bdd/bdd-workflow-runner.py src/auth/Auth.test.js --scope next:3")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Parse options
    scope = "describe"
    phase = None
    cursor_line = None
    auto = False
    step_type = None
    
    i = 2
    # Check if second argument is a step type (no dashes)
    if i < len(sys.argv) and not sys.argv[i].startswith('--'):
        step_type_arg = sys.argv[i]
        # Accept any sample_N pattern or fixed step types
        if (step_type_arg.startswith('sample_') or 
            step_type_arg in ['expand', 'red', 'green', 'refactor']):
            step_type = step_type_arg
            i += 1
    
    while i < len(sys.argv):
        if sys.argv[i] == "--scope" and i + 1 < len(sys.argv):
            scope = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--phase" and i + 1 < len(sys.argv):
            phase = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--line" and i + 1 < len(sys.argv):
            cursor_line = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--auto":
            auto = True
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)
    
    try:
        # Check if test file is empty - clean up workflow state if needed
        test_path = Path(file_path)
        if test_path.exists():
            content = test_path.read_text(encoding='utf-8').strip()
            if not content:
                print("\nTest file is empty - cleaning up workflow state")
                workflow_dir = test_path.parent / ".bdd-workflow"
                if workflow_dir.exists():
                    import shutil
                    try:
                        shutil.rmtree(workflow_dir)
                        print(f"Removed {workflow_dir}")
                    except PermissionError:
                        # Try to remove files individually
                        for file in workflow_dir.glob('*'):
                            try:
                                file.unlink()
                            except:
                                pass
                        try:
                            workflow_dir.rmdir()
                        except:
                            print(f"Warning: Could not fully remove {workflow_dir}")
        
        # If step_type provided, start a new run
        if step_type:
            run_state = BDDRunState(file_path)
            
            # Map step_type to StepType enum
            if step_type.startswith('sample_'):
                step_enum = StepType.SAMPLE
            else:
                step_map = {
                    'expand': StepType.EXPAND,
                    'red': StepType.RED_BATCH,
                    'green': StepType.GREEN_BATCH,
                    'refactor': StepType.REFACTOR_SUGGEST
                }
                step_enum = step_map.get(step_type)
            
            if step_enum:
                try:
                    run_id = run_state.start_run(step_enum, {
                        'scope': scope,
                        'phase': phase or 'signatures',
                        'step_name': step_type  # Store actual step name
                    })
                    print(f"\nStarted run: {run_id}")
                    print(f"   Step: {step_type}")
                    print(f"   Scope: {scope}")
                    print("\nAI Agent: Create test signatures following BDD principles")
                    print("   Then run: /bdd-validate")
                    # Exit here - don't call bdd_workflow, just start the run
                    sys.exit(0)
                except RuntimeError as e:
                    print(f"\nCannot start run: {e}")
                    sys.exit(1)
        
        workflow_data = bdd_workflow(file_path, scope, phase, cursor_line, auto)
        
        if "error" in workflow_data:
            print(f"\nError: {workflow_data['error']}")
            sys.exit(1)
        
        # Print summary
        print("\nWorkflow Data Ready:")
        print(f"  Phase: {workflow_data['phase']}")
        print(f"  Scope: {workflow_data['scope']}")
        print(f"  Tests in scope: {len(workflow_data['test_structure']['scoped_tests'])}")
        
        if workflow_data['test_structure']['next_test']:
            test = workflow_data['test_structure']['next_test'][1]
            print(f"  Next test: Line {test['line']} - {test['text']}")
        
        print(f"\nCode under test files ({len(workflow_data['relationships']['code_under_test_files'])}):")
        for f in workflow_data['relationships']['code_under_test_files']:
            print(f"  - {f}")
        
        print(f"\nRelated tests ({len(workflow_data['relationships']['related_tests'])}):")
        for f in workflow_data['relationships']['related_tests']:
            print(f"  - {f}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

