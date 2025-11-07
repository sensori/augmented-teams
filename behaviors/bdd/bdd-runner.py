"""
BDD Workflow - Red-Green-Refactor Cycle
Guides developers through true BDD (Behavior-Driven Development) with Red-Green-Refactor cycle.

Division of Labor:
- Code: Parse files, run tests, track state, identify relationships, ENFORCE workflow
- AI Agent: 
  * Identify SAMPLE SIZE (lowest-level describe block, ~18 tests)
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

# ============================================================================
# STATE MANAGEMENT CLASSES
# ============================================================================

class RunStatus(Enum):
    """Run lifecycle status"""
    STARTED = "started"              # Work began, not verified
    AI_VERIFIED = "ai_verified"      # AI ran validation, passed
    HUMAN_APPROVED = "human_approved"  # Human reviewed and approved
    COMPLETED = "completed"          # Fully complete


class StepType(Enum):
    """Workflow step types"""
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


class BDDRunState:
    """Tracks and enforces BDD workflow run state"""
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.state_file = self._get_state_file_path()
        self.state = self._load_state()
    
    def _get_state_file_path(self) -> Path:
        """Get run state file path"""
        test_path = Path(self.test_file)
        state_dir = test_path.parent / ".bdd-workflow"
        state_dir.mkdir(exist_ok=True)
        return state_dir / f"{test_path.stem}.run-state.json"
    
    def _load_state(self) -> Dict[str, Any]:
        """Load run state from file"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding='utf-8'))
        
        # Initialize new run state
        return {
            "runs": [],  # List of all runs
            "current_run_id": None,
            "phase": "signatures",
            "scope": "describe",
            "created_at": datetime.now().isoformat()
        }
    
    def save(self):
        """Save run state to file"""
        self.state_file.write_text(
            json.dumps(self.state, indent=2), 
            encoding='utf-8'
        )
    
    def start_run(self, step_type: StepType, context: Dict[str, Any] = None) -> str:
        """
        Start a new run.
        
        Returns: run_id
        Raises: RuntimeError if previous run not complete
        """
        if context is None:
            context = {}
            
        # Check if previous run is complete
        if self.state["current_run_id"]:
            prev_run = self._get_run(self.state["current_run_id"])
            if prev_run and prev_run["status"] != RunStatus.COMPLETED.value:
                raise RuntimeError(
                    f"Previous run {self.state['current_run_id']} not complete. "
                    f"Status: {prev_run['status']}. "
                    f"Complete or abandon previous run before starting new one."
                )
        
        # Create new run
        run_id = f"{step_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        new_run = {
            "run_id": run_id,
            "step_type": step_type.value,
            "status": RunStatus.STARTED.value,
            "context": context,
            "started_at": datetime.now().isoformat(),
            "ai_verified_at": None,
            "human_approved_at": None,
            "completed_at": None,
            "validation_results": None,
            "human_feedback": None
        }
        
        self.state["runs"].append(new_run)
        self.state["current_run_id"] = run_id
        self.save()
        
        return run_id
    
    def _get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run by ID"""
        for run in self.state["runs"]:
            if run["run_id"] == run_id:
                return run
        return None
    
    def get_current_run(self) -> Optional[Dict[str, Any]]:
        """Get current active run"""
        if not self.state["current_run_id"]:
            return None
        return self._get_run(self.state["current_run_id"])
    
    def record_ai_verification(self, validation_results: Dict[str, Any] = None):
        """Record that AI verified the work"""
        if validation_results is None:
            validation_results = {}
            
        current_run = self.get_current_run()
        if not current_run:
            raise RuntimeError("No current run to verify")
        
        run_id = current_run['run_id']
        run = self._get_run(run_id)
        
        if run["status"] != RunStatus.STARTED.value:
            raise RuntimeError(
                f"Run {run_id} not in STARTED status. "
                f"Current status: {run['status']}"
            )
        
        run["status"] = RunStatus.AI_VERIFIED.value
        run["ai_verified_at"] = datetime.now().isoformat()
        run["validation_results"] = validation_results
        self.save()
    
    def record_human_approval(
        self, 
        run_id: str, 
        approved: bool,
        feedback: Optional[str] = None
    ):
        """Record human review and approval"""
        run = self._get_run(run_id)
        if not run:
            raise RuntimeError(f"Run {run_id} not found")
        
        if run["status"] != RunStatus.AI_VERIFIED.value:
            raise RuntimeError(
                f"Run {run_id} not AI verified. "
                f"Current status: {run['status']}. "
                f"AI must verify before human approval."
            )
        
        if approved:
            run["status"] = RunStatus.HUMAN_APPROVED.value
            run["human_approved_at"] = datetime.now().isoformat()
        else:
            # Rejected - back to STARTED
            run["status"] = RunStatus.STARTED.value
            run["ai_verified_at"] = None
            run["validation_results"] = None
        
        run["human_feedback"] = feedback
        self.save()
    
    def complete_run(self, run_id: str):
        """Mark run as completed"""
        run = self._get_run(run_id)
        if not run:
            raise RuntimeError(f"Run {run_id} not found")
        
        if run["status"] != RunStatus.HUMAN_APPROVED.value:
            raise RuntimeError(
                f"Run {run_id} not human approved. "
                f"Current status: {run['status']}. "
                f"Human must approve before completion."
            )
        
        run["status"] = RunStatus.COMPLETED.value
        run["completed_at"] = datetime.now().isoformat()
        
        # Clear current run
        self.state["current_run_id"] = None
        self.save()
    
    def abandon_run(self, run_id: str, reason: str):
        """Abandon a run (for error recovery)"""
        run = self._get_run(run_id)
        if run:
            run["status"] = "abandoned"
            run["abandon_reason"] = reason
            run["abandoned_at"] = datetime.now().isoformat()
            
            if self.state["current_run_id"] == run_id:
                self.state["current_run_id"] = None
            
            self.save()
    
    def can_start_run(self) -> bool:
        """Check if can start a new run"""
        current_run = self.get_current_run()
        if not current_run:
            return True
        return current_run["status"] == RunStatus.COMPLETED.value
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get human-readable status summary"""
        current_run = self.get_current_run()
        can_proceed, reason = self._can_proceed_to_next_step()
        
        return {
            "current_run": current_run["run_id"] if current_run else None,
            "status": current_run["status"] if current_run else "no_active_run",
            "step_type": current_run["step_type"] if current_run else None,
            "can_proceed": can_proceed,
            "next_action": reason,
            "total_runs": len(self.state["runs"]),
            "completed_runs": len([r for r in self.state["runs"] 
                                   if r["status"] == RunStatus.COMPLETED.value])
        }
    
    def _can_proceed_to_next_step(self) -> tuple[bool, str]:
        """Check if can proceed to next workflow step"""
        current_run = self.get_current_run()
        
        if not current_run:
            return (True, "No active run, can start new one")
        
        status = current_run["status"]
        
        if status == RunStatus.COMPLETED.value:
            return (True, "Current run complete")
        
        if status == RunStatus.STARTED.value:
            return (False, "AI must verify before proceeding")
        
        if status == RunStatus.AI_VERIFIED.value:
            return (False, "Human must review and approve before proceeding")
        
        if status == RunStatus.HUMAN_APPROVED.value:
            return (False, "Run approved but not marked complete. Call complete_run()")
        
        return (False, f"Unknown status: {status}")


# ============================================================================
# EXECUTOR CLASSES
# ============================================================================


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


class WorkflowStepTemplate:
    """
    Template pattern for workflow steps with 3-method iteration pattern.
    
    Pattern:
    1. start_step() - Initialize step, output instructions, exit
    2. repeat_step() - Re-output instructions for iteration, exit  
    3. verify_step() - Record AI verification, exit
    
    Each method is a separate command invocation (Python process starts, outputs, exits).
    State persists in run-state.json between calls.
    """
    
    def __init__(self, test_file: str, run_state: 'BDDRunState'):
        self.test_file = test_file
        self.run_state = run_state
    
    def start_step(self, step_type: StepType, work_function):
        """
        First call - Initialize step and output instructions to AI.
        
        Args:
            step_type: Type of step (DOMAIN_SCAFFOLD, SIGNATURES, RED, etc.)
            work_function: Callable that outputs instructions to chat
        """
        # COMMON: Start run (will raise error if previous run not complete)
        try:
            run_id = self.run_state.start_run(step_type, {'scope': 'describe'})
            print(f"\n▶ Starting {step_type.value} (Run ID: {run_id})")
        except RuntimeError as e:
            print(f"\n❌ {e}")
            current_run = self.run_state.get_current_run()
            if current_run:
                print(f"\n   Current run: {current_run['step_type']}")
                print(f"   Status: {current_run['status']}")
                print(f"\n   Complete previous run first:")
                print(f"   - Run phase-specific verify command")
                print(f"   - /bdd-workflow-approve (if ready)")
                print(f"   - /bdd-workflow-abandon (if need to restart)")
            raise
        
        # VARIABLE: The actual work (outputs instructions)
        try:
            work_function()
        except Exception as e:
            print(f"\n❌ Error during {step_type.value}: {e}")
            raise
        
        # COMMON: Instructions for next steps
        print(f"\n⏸  Next steps:")
        print(f"   - Run same command again to iterate")
        print(f"   - Run phase-specific verify command when done")
        print(f"   - Run /bdd-workflow-status to check state")
        
        # State remains STARTED - waiting for AI work
    
    def repeat_step(self, work_function):
        """
        Middle calls - Re-output instructions for iteration.
        Does NOT change state, allows unlimited iteration.
        
        Args:
            work_function: Callable that outputs instructions to chat
        """
        current_run = self.run_state.get_current_run()
        
        if not current_run or current_run['status'] != RunStatus.STARTED.value:
            print(f"\n❌ No active run to repeat")
            print(f"   Current status: {current_run['status'] if current_run else 'None'}")
            return
        
        print(f"\n🔄 Repeating {current_run['step_type']}...")
        
        # VARIABLE: Re-output instructions
        try:
            work_function()
        except Exception as e:
            print(f"\n❌ Error during repeat: {e}")
            raise
        
        print(f"\n⏸  Next steps:")
        print(f"   - Run same command again to iterate")
        print(f"   - Run phase-specific verify command when done")
        
        # State remains STARTED
    
    def verify_step(self, step_type: StepType, validation_instructions: str):
        """
        Final call - Record AI verification and prepare for approval.
        
        Args:
            step_type: Expected step type to verify
            validation_instructions: Instructions for which validation AI should have run
        """
        current_run = self.run_state.get_current_run()
        
        if not current_run or current_run['step_type'] != step_type.value:
            print(f"\n❌ Cannot verify - wrong step or no active run")
            print(f"   Expected: {step_type.value}")
            print(f"   Current: {current_run['step_type'] if current_run else 'None'}")
            return
        
        # Output validation expectations
        print(f"\n✅ Verifying {step_type.value}...")
        print(f"\n⚠️  AI Verification Requirements:")
        print(f"   {validation_instructions}")
        print(f"\n   AI should have reported violations to Human")
        print(f"   AI should have fixed violations per Human direction")
        
        # COMMON: Record AI verification in state
        validation_results = {
            'validated': True,
            'rules_checked': validation_instructions,
            'timestamp': datetime.now().isoformat()
        }
        self.run_state.record_ai_verification(current_run['run_id'], validation_results)
        
        print(f"\n✅ AI verification recorded")
        print(f"   Run /bdd-workflow-approve to proceed to next phase")
        print(f"   Run /bdd-workflow-status to see current state")
    


class DomainScaffolder:
    """
    Stage 0: Domain Scaffolding
    Generates natural language describe hierarchy from domain map.
    NO code, NO mocks, NO "it should" statements yet.
    """
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.test_dir = Path(test_file).parent
    
    def _load_hierarchy_patterns(self) -> str:
        """Load hierarchy patterns section from rule file"""
        rule_file = Path(__file__).parent / "stages" / "bdd-domain-scaffold-rule.mdc"
        if not rule_file.exists():
            return "⚠️ Rule file not found - using default patterns"
        
        try:
            content = rule_file.read_text(encoding='utf-8')
            
            # Extract from "## Hierarchy Patterns" to next "##" section
            start_marker = "## Hierarchy Patterns"
            end_marker = "## CRITICAL: Preserve Domain Map Hierarchy"
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if start_idx == -1:
                return "⚠️ Hierarchy Patterns section not found in rule file"
            
            if end_idx == -1:
                # Take until end of file if no next section
                patterns = content[start_idx:]
            else:
                patterns = content[start_idx:end_idx]
            
            return patterns.strip()
        except Exception as e:
            return f"⚠️ Error loading patterns: {e}"
    
    def output_instructions(self):
        """Output domain map and instructions for AI to generate hierarchy"""
        print("\n" + "="*60)
        print("STAGE 0: DOMAIN SCAFFOLDING")
        print("="*60)
        
        # Try to load domain map
        domain_map = self._load_domain_map()
        
        if not domain_map:
            print(f"\n❌ STOP: No domain map found")
            print(f"   Domain map is MANDATORY for correct hierarchy")
            print(f"   Run /ddd-analyze first to create domain map")
            print(f"   Then return to /bdd-domain-scaffold")
            return
        
        print(f"\n✅ Domain map found")
        print("\n" + "="*60)
        print("DOMAIN MAP HIERARCHY")
        print("="*60)
        print(domain_map)
        
        print("\n" + "="*60)
        print("⚠️  CRITICAL: PRESERVE THIS HIERARCHY")
        print("="*60)
        print("Domain map indentation → Test nesting depth")
        print("\nMapping:")
        print("  No indent (DOMAIN) → Top-level describe")
        print("  1 tab (Concept) → Nested under domain")
        print("  2 tabs (Sub) → Nested under concept")
        
        # Load and display hierarchy patterns from rule file
        print("\n" + "="*60)
        print("HIERARCHY PATTERNS (from bdd-domain-scaffold-rule.mdc)")
        print("="*60)
        patterns = self._load_hierarchy_patterns()
        print(patterns)
        
        # Determine text file path
        test_path = Path(self.test_file)
        hierarchy_file = test_path.parent / f"{test_path.stem}-hierarchy.txt"
        
        print("\n" + "="*60)
        print("CREATE PLAIN ENGLISH HIERARCHY TEXT FILE")
        print("="*60)
        print(f"Create text file: {hierarchy_file}")
        print("\nWrite plain English hierarchy following patterns above:")
        print("- NO code syntax (), =>, {} - just plain English text")
        print("- NEVER flatten - preserve ALL nesting from domain map")
        print("- Follow temporal lifecycle progression (created → played → edited → saved)")
        print("- Use complete end-to-end behaviors")
        print(f"\nFile to create: {hierarchy_file.name}")
        print("This is a TEXT file (.txt), separate from the test code file")
        print("\nRun /bdd-domain-scaffold-verify when ready")
    
    def _load_domain_map(self) -> Optional[str]:
        """Load domain map from test directory"""
        # Try common domain map names
        possible_names = [
            f"{self.test_dir.stem}-domain-map.txt",
            "domain-map.txt",
            f"{self.test_dir.stem}.domain-map.txt"
        ]
        
        for name in possible_names:
            map_file = self.test_dir / name
            if map_file.exists():
                return map_file.read_text(encoding='utf-8')
        
        return None


class SignatureGenerator:
    """
    Stage 1: Signature Generation
    Adds "it should..." statements to describe hierarchy from Stage 0.
    """
    
    def __init__(self, test_file: str, framework: str):
        self.test_file = test_file
        self.framework = framework
    
    def output_instructions(self):
        """Output instructions to create hierarchy from domain map and convert to code syntax"""
        print("\n" + "="*60)
        print("STAGE 1: CREATE TEST HIERARCHY & SIGNATURES")
        print("="*60)
        
        # Load domain map for reference
        domain_map = self._load_domain_map()
        
        if domain_map:
            print("\n" + "="*60)
            print("DOMAIN MAP REFERENCE")
            print("="*60)
            print(domain_map)
            
            print("\n" + "="*60)
            print("HIERARCHY MAPPING RULES")
            print("="*60)
            print("Domain map indentation → Test nesting depth")
            print("\nMapping:")
            print("  No indent (DOMAIN) → Top-level describe")
            print("  1 tab (Concept) → Nested under domain")
            print("  2 tabs (Sub) → Nested under concept")
            print("\nExample from YOUR domain map:")
            print("  POWER ACTIVATION ANIMATION (no indent)")
            print("      Power Item (1 tab)")
            print("      Movement-Triggered Animation (1 tab)")
            print("\n  BECOMES:")
            print("  describe('power activation animation', () => {")
            print("      describe('a power item', () => {")
            print("      describe('movement-triggered animation', () => {")
        
        print("\n" + "="*60)
        print("AI AGENT TODO")
        print("="*60)
        print("1. CREATE test hierarchy from domain map above:")
        print("   - Preserve ALL nesting levels from domain map")
        print("   - Top-level describes = DOMAINS from map")
        print("   - Nested describes = CONCEPTS under domain")
        print("   - Deep nesting = SUB-CONCEPTS under concept")
        print("2. Convert to proper code syntax:")
        print("   - describe('...', () => {})")
        print("   - it('should...', () => {})")
        print("3. Keep test bodies EMPTY - no mocks, no stubs, no helpers")
        print("4. Mark with // BDD: SIGNATURE comments")
        print("5. ~18 describe/it blocks for Sample 1")
        print("\n⚠️  CRITICAL: NEVER flatten hierarchy - preserve domain map depth!")
        print("\nRun /bdd-signature-verify when ready")
    
    def _load_domain_map(self) -> Optional[str]:
        """Load domain map from test directory"""
        test_path = Path(self.test_file)
        test_dir = test_path.parent
        
        # Try common domain map names
        possible_names = [
            f"{test_dir.stem}-domain-map.txt",
            "domain-map.txt",
            f"{test_dir.stem}.domain-map.txt"
        ]
        
        for name in possible_names:
            map_file = test_dir / name
            if map_file.exists():
                return map_file.read_text(encoding='utf-8')
        
        return None


class RedExecutor:
    """
    Stage 2: RED Phase
    Implement failing tests with Arrange-Act-Assert.
    """
    
    def __init__(self, test_file: str, framework: str):
        self.test_file = test_file
        self.framework = framework
    
    def output_instructions(self):
        """Output RED phase instructions"""
        print("\n" + "="*60)
        print("STAGE 2: RED - Implement Failing Tests")
        print("="*60)
        
        print("\nAI AGENT TODO:")
        print("1. Implement ~18 test signatures with Arrange-Act-Assert")
        print("2. Add proper mocking and helpers following § 3 principles")
        print("3. Extract duplicate setup to beforeEach()")
        print("4. Create helper factories for repeated mocks")
        print("5. COMMENT OUT test code that calls production code:")
        print("   Example: // powerItem = new PowerItem(mockPower);")
        print("   Example: // expect(powerItem.descriptor).toBe('Fire');")
        print("6. COMMENT OUT or ensure production code doesn't exist")
        print("   Example: In production file, comment out class PowerItem")
        print("7. Tests should be ready to fail when uncommented")
        print("\nRun /bdd-red-verify when ready")


class GreenExecutor:
    """
    Stage 3: GREEN Phase
    Implement minimal code to make tests pass.
    """
    
    def __init__(self, test_file: str, framework: str):
        self.test_file = test_file
        self.framework = framework
    
    def output_instructions(self):
        """Output GREEN phase instructions"""
        print("\n" + "="*60)
        print("STAGE 3: GREEN - Implement Minimal Code")
        print("="*60)
        
        print("\nAI AGENT TODO:")
        print("1. UNCOMMENT test code from RED phase")
        print("2. Implement minimal production code for ~18 tests")
        print("3. Resist adding features no test demands")
        print("4. Verify tests now PASS")
        print("5. Check for regressions in existing tests")
        print("\nRun /bdd-green-verify when ready")


class RefactorExecutor:
    """
    Stage 4: REFACTOR Phase
    Improve code quality while keeping tests green.
    """
    
    def __init__(self, test_file: str, framework: str):
        self.test_file = test_file
        self.framework = framework
    
    def output_instructions(self):
        """Output REFACTOR phase instructions"""
        print("\n" + "="*60)
        print("STAGE 4: REFACTOR - Improve Code Quality")
        print("="*60)
        
        print("\nAI AGENT TODO:")
        print("1. Identify code smells")
        print("2. Suggest refactorings with trade-offs")
        print("3. Implement approved refactorings one at a time")
        print("4. Run tests after each refactoring")
        print("5. Stop if any test fails")
        print("\nRun /bdd-refactor-verify when ready")


class WorkflowOrchestrator:
    """
    Smart dispatcher - determines which command to run based on current phase.
    """
    
    def __init__(self, test_file: str, run_state: 'BDDRunState'):
        self.test_file = test_file
        self.run_state = run_state
    
    def determine_next_command(self) -> Optional[str]:
        """
        Determine which command should run next based on completed runs.
        
        Returns: Command name or None
        """
        current_run = self.run_state.get_current_run()
        
        # Active run - user should complete it first
        if current_run and current_run['status'] != RunStatus.COMPLETED.value:
            print(f"\n⚠️  Active run in progress: {current_run['step_type']}")
            print(f"   Status: {current_run['status']}")
            print(f"   Complete this run first before starting new phase")
            return None
        
        # Check which phases have been completed
        completed_runs = [
            run for run in self.run_state.state.get('runs', [])
            if run['status'] == RunStatus.COMPLETED.value
        ]
        
        completed_steps = {run['step_type'] for run in completed_runs}
        
        # Phase progression: domain-scaffold → signatures → red → green → refactor
        if StepType.DOMAIN_SCAFFOLD.value not in completed_steps:
            return 'domain-scaffold'
        elif StepType.SIGNATURES.value not in completed_steps:
            return 'signatures'
        elif StepType.RED.value not in completed_steps:
            return 'red'
        elif StepType.GREEN.value not in completed_steps:
            return 'green'
        elif StepType.REFACTOR.value not in completed_steps:
            return 'refactor'
        else:
            print(f"\n✅ All workflow phases complete!")
            return None
    
    def execute_workflow(self):
        """Execute appropriate command based on state"""
        next_cmd = self.determine_next_command()
        
        if not next_cmd:
            return
        
        print(f"\n▶ Dispatching to: {next_cmd}")
        print(f"   Run /bdd-{next_cmd} to continue")


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


# Step 2: Discover domain maps in test file's directory
def discover_domain_maps(test_file_path: str) -> Dict[str, Any]:
    """
    Look for domain maps in the same directory as the test file.
    Returns: {
        "found": bool,
        "domain_map": {"path": str, "content": str} or None,
        "interaction_map": {"path": str, "content": str} or None
    }
    """
    test_path = Path(test_file_path)
    test_dir = test_path.parent
    
    result = {
        "found": False,
        "domain_map": None,
        "interaction_map": None
    }
    
    # Look for domain map (*-domain-map.txt)
    domain_maps = list(test_dir.glob("*-domain-map.txt"))
    if domain_maps:
        domain_map_path = domain_maps[0]
        try:
            content = domain_map_path.read_text(encoding='utf-8')
            result["domain_map"] = {
                "path": str(domain_map_path),
                "content": content
            }
            result["found"] = True
        except Exception as e:
            pass
    
    # Look for interaction map (*-domain-interactions.txt)
    interaction_maps = list(test_dir.glob("*-domain-interactions.txt"))
    if interaction_maps:
        interaction_map_path = interaction_maps[0]
        try:
            content = interaction_map_path.read_text(encoding='utf-8')
            result["interaction_map"] = {
                "path": str(interaction_map_path),
                "content": content
            }
            result["found"] = True
        except Exception as e:
            pass
    
    return result


# Step 3: Load framework-specific rule file
def load_rule_file(framework: str) -> Dict[str, Any]:
    """
    Load the appropriate framework-specific rule file.
    Returns: {"rule_path": Path, "content": str, "framework": str}
    """
    rule_files = {
        'jest': 'bdd-jest-rule.mdc',
        'mamba': 'bdd-mamba-rule.mdc'
    }
    
    rule_file = rule_files.get(framework)
    if not rule_file:
        return None
    
    rule_path = Path("behaviors/bdd") / rule_file
    if not rule_path.exists():
        return None
    
    content = rule_path.read_text(encoding='utf-8')
    
    return {
        "rule_path": str(rule_path),
        "content": content,
        "framework": framework
    }


# Step 4: Extract DO and DON'T examples by section
def extract_dos_and_donts(rule_content: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Extract DO and DON'T examples from each section (§1-5) of the rule.
    Returns: {"section_name": {"dos": [...], "donts": [...]}}
    """
    sections = {}
    current_section = None
    
    lines = rule_content.split('\n')
    for i, line in enumerate(lines):
        section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
        if section_match:
            section_num = section_match.group(1)
            section_name = section_match.group(2).strip()
            current_section = f"{section_num}. {section_name}"
            sections[current_section] = {"dos": [], "donts": []}
        
        if '**✅ DO:**' in line or '**DO:**' in line:
            code_block = []
            in_code = False
            for j in range(i+1, min(i+50, len(lines))):
                if lines[j].strip().startswith('```') and not in_code:
                    in_code = True
                    continue
                elif lines[j].strip().startswith('```') and in_code:
                    break
                elif in_code:
                    code_block.append(lines[j])
            
            if code_block and current_section:
                sections[current_section]["dos"].append('\n'.join(code_block))
        
        if '**❌ DON\'T:**' in line or '**DON\'T:**' in line or "**DON'T:**" in line:
            code_block = []
            in_code = False
            for j in range(i+1, min(i+50, len(lines))):
                if lines[j].strip().startswith('```') and not in_code:
                    in_code = True
                    continue
                elif lines[j].strip().startswith('```') and in_code:
                    break
                elif in_code:
                    code_block.append(lines[j])
            
            if code_block and current_section:
                sections[current_section]["donts"].append('\n'.join(code_block))
    
    return sections


# Step 5: Extract test structure and chunk by describe blocks
def extract_test_structure_chunks(test_file_path: str, framework: str, max_chunk_size: int = 8000) -> List[Dict[str, Any]]:
    """
    Extract test structure and chunk by describe blocks for manageable AI processing.
    Returns: [{"start_line": int, "end_line": int, "context": str, "structure": str}]
    """
    content = Path(test_file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    blocks = []
    for i, line in enumerate(lines, 1):
        indent = len(line) - len(line.lstrip())
        
        if framework == 'jest':
            if 'describe(' in line:
                match = re.search(r"describe\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "describe",
                        "text": match.group(1),
                        "indent": indent,
                        "full_line": line
                    })
            elif 'it(' in line or 'test(' in line:
                match = re.search(r"(?:it|test)\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "it",
                        "text": match.group(1),
                        "indent": indent,
                        "full_line": line
                    })
        
        elif framework == 'mamba':
            # Extract description/context blocks
            if 'with description(' in line or 'with context(' in line:
                match = re.search(r"with (?:description|context)\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "describe",
                        "text": match.group(1),
                        "indent": indent,
                        "full_line": line
                    })
            # Extract it blocks
            elif 'with it(' in line:
                match = re.search(r"with it\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "it",
                        "text": match.group(1),
                        "indent": indent,
                        "full_line": line
                    })
    
    chunks = []
    current_chunk = []
    current_describes = []
    chunk_start_line = 1
    
    for block in blocks:
        while current_describes and block["indent"] <= current_describes[-1]["indent"]:
            current_describes.pop()
        
        if block["type"] == "describe":
            current_describes.append(block)
            
            if len(current_chunk) > 0 and block["indent"] == 0:
                chunk_text = '\n'.join([f"Line {b['line']}: {' ' * b['indent']}{b['type']}('{b['text']}', ...)" for b in current_chunk])
                if len(chunk_text) < max_chunk_size or len(chunks) == 0:
                    context = ' > '.join([d['text'] for d in current_describes[:-1]]) if len(current_describes) > 1 else ''
                    chunks.append({
                        "start_line": chunk_start_line,
                        "end_line": current_chunk[-1]["line"] if current_chunk else chunk_start_line,
                        "context": context,
                        "structure": chunk_text
                    })
                
                current_chunk = [block]
                chunk_start_line = block["line"]
            else:
                current_chunk.append(block)
        else:
            current_chunk.append(block)
    
    if current_chunk:
        chunk_text = '\n'.join([f"Line {b['line']}: {' ' * b['indent']}{b['type']}('{b['text']}', ...)" for b in current_chunk])
        context = ' > '.join([d['text'] for d in current_describes[:-1]]) if len(current_describes) > 1 else ''
        chunks.append({
            "start_line": chunk_start_line,
            "end_line": current_chunk[-1]["line"] if current_chunk else chunk_start_line,
            "context": context,
            "structure": chunk_text
        })
    
    return chunks


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
            # Extract describe blocks (description and context)
            if 'with description(' in line or 'with describe(' in line or 'with context(' in line:
                match = re.search(r"with (?:description|describe|context)\(['\"]([^'\"]+)['\"]", line)
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


# ============================================================================
# COMMAND LINE FUNCTIONS
# ============================================================================

def cmd_show_status(test_file: str):
    """Show current workflow status"""
    run_state = BDDRunState(test_file)
    status = run_state.get_status_summary()
    current_run = run_state.get_current_run()
    
    print("\n" + "="*60)
    print("BDD WORKFLOW STATUS")
    print("="*60)
    
    print(f"\nFile: {test_file}")
    print(f"Total runs: {status['total_runs']}")
    print(f"Completed: {status['completed_runs']}")
    
    if current_run:
        print(f"\n📍 CURRENT RUN")
        print(f"  ID: {current_run['run_id']}")
        print(f"  Step: {current_run['step_type']}")
        print(f"  Status: {current_run['status']}")
        print(f"  Started: {current_run['started_at']}")
        
        if current_run.get('ai_verified_at'):
            print(f"  AI Verified: {current_run['ai_verified_at']}")
            
        if current_run.get('human_approved_at'):
            print(f"  Human Approved: {current_run['human_approved_at']}")
            
        if current_run.get('validation_results'):
            val = current_run['validation_results']
            if 'passed' in val:
                print(f"\n  Validation: {'✅ PASSED' if val['passed'] else '❌ FAILED'}")
            
        if current_run.get('human_feedback'):
            print(f"\n  Feedback: {current_run['human_feedback']}")
    else:
        print(f"\n✅ No active run - ready to start new work")
    
    print(f"\n{'✅' if status['can_proceed'] else '⚠️'} Can proceed: {status['can_proceed']}")
    print(f"Next action: {status['next_action']}")
    
    # Show recent runs
    if run_state.state['runs']:
        print(f"\n📜 RECENT RUNS (last 5):")
        for run in run_state.state['runs'][-5:]:
            status_icon = {
                'completed': '✅',
                'ai_verified': '🔍',
                'human_approved': '👍',
                'started': '🚧',
                'abandoned': '❌'
            }.get(run['status'], '❓')
            
            print(f"  {status_icon} {run['step_type']:20} | {run['status']:15} | {run['run_id']}")
    
    print("="*60)


def cmd_approve_run(test_file: str, feedback: str = None):
    """Approve the current run after reviewing AI work"""
    run_state = BDDRunState(test_file)
    current_run = run_state.get_current_run()
    
    if not current_run:
        print("\n❌ No active run to approve")
        return False
    
    print(f"\n=== Approving Run: {current_run['run_id']} ===")
    print(f"Step: {current_run['step_type']}")
    print(f"Status: {current_run['status']}")
    
    if current_run['status'] != 'ai_verified':
        print(f"\n❌ Cannot approve - run not AI verified")
        print(f"Current status: {current_run['status']}")
        print("AI must run /bdd-validate first")
        return False
    
    # Record approval
    run_state.record_human_approval(
        current_run['run_id'],
        approved=True,
        feedback=feedback
    )
    
    # Mark as complete
    run_state.complete_run(current_run['run_id'])
    
    print(f"\n✅ Run approved and completed")
    if feedback:
        print(f"Feedback: {feedback}")
    
    print("\n🎯 Ready to proceed to next step")
    return True


def cmd_reject_run(test_file: str, feedback: str):
    """Reject the current run and send back to AI for fixes"""
    run_state = BDDRunState(test_file)
    current_run = run_state.get_current_run()
    
    if not current_run:
        print("\n❌ No active run to reject")
        return False
    
    print(f"\n=== Rejecting Run: {current_run['run_id']} ===")
    print(f"Step: {current_run['step_type']}")
    print(f"Reason: {feedback}")
    
    # Record rejection
    run_state.record_human_approval(
        current_run['run_id'],
        approved=False,
        feedback=feedback
    )
    
    print(f"\n⚠️ Run rejected - sent back to AI")
    print(f"AI must fix issues and re-validate")
    return True


def cmd_abandon_run(test_file: str, reason: str):
    """Abandon the current run"""
    run_state = BDDRunState(test_file)
    current_run = run_state.get_current_run()
    
    if not current_run:
        print("\n❌ No active run to abandon")
        return False
    
    print(f"\n=== Abandoning Run: {current_run['run_id']} ===")
    print(f"Step: {current_run['step_type']}")
    print(f"Status: {current_run['status']}")
    print(f"Reason: {reason}")
    
    # Confirm
    print("\n⚠️  This will abandon the current run and allow starting fresh.")
    print("Continue? (y/n): ", end='')
    response = input().strip().lower()
    
    if response != 'y':
        print("❌ Cancelled")
        return False
    
    # Abandon
    run_state.abandon_run(current_run['run_id'], reason)
    
    print(f"\n✅ Run abandoned")
    print(f"Ready to start new run")
    return True


# ============================================================================
# MAIN WORKFLOW ORCHESTRATOR
# ============================================================================

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
    
    # Step 8.5: For SIGNATURES phase, load and present DO/DON'T examples
    rule_examples = None
    if current_phase == BDDPhase.SIGNATURES:
        # Import the function from hyphenated module name
        import importlib.util
        validate_runner_path = Path(__file__).parent.parent / "validate" / "bdd-validate-runner.py"
        spec = importlib.util.spec_from_file_location("bdd_validate_runner", validate_runner_path)
        validate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate_module)
        load_rule_file = validate_module.load_rule_file
        extract_dos_and_donts = validate_module.extract_dos_and_donts
        
        # Load rule and extract examples
        rule_data = load_rule_file(framework)
        if rule_data:
            examples = extract_dos_and_donts(rule_data["content"])
            rule_examples = {
                "rule_file": rule_data["rule_path"],
                "examples": examples
            }
            
            # OUTPUT TO CHAT for AI Agent - Show ALL examples
            print("\n" + "="*60)
            print("DO/DON'T EXAMPLES FROM BDD RULES")
            print("="*60)
            for section, data in examples.items():
                print(f"\n### {section}")
                
                if data['dos']:
                    print("\n✅ DO:")
                    for i, example in enumerate(data['dos'], 1):  # Show ALL DO examples
                        print(f"\nExample {i}:")
                        print(example)
                
                if data['donts']:
                    print("\n❌ DON'T:")
                    for i, example in enumerate(data['donts'], 1):  # Show ALL DON'T examples
                        print(f"\nExample {i}:")
                        print(example)
            
            print("\n" + "="*60)
            print("AI Agent: Create tests aligning to these DO/DON'T examples")
            print("="*60 + "\n")
    
    # Step 9: Prepare data for AI Agent
    workflow_data = {
        "file_path": file_path,
        "framework": framework,
        "phase": current_phase.value,
        "scope": scope,
        "auto_mode": auto,
        "rule_examples": rule_examples,  # Include examples data
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
        print("1. Identify SAMPLE SIZE (lowest-level describe, ~18 tests)")
        print("2. Create sample test signatures")
        print("3. Run /bdd-validate")
        print("4. Fix violations, learn, iterate")
    if next_test:
        print(f"\nNext Test: Line {next_test[1]['line']} - '{next_test[1]['text']}'")
    print("="*60)
    
    return workflow_data


# ============================================================================
# ENHANCED VALIDATOR - Rule Parsing & Iterative Validation
# ============================================================================

class RuleParser:
    """Parse BDD rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, framework: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if framework in self._cache:
            return self._cache[framework]
        
        rule_data = load_rule_file(framework)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        self._cache[framework] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section['num']] = self._parse_section_content(
                        current_section['title'],
                        '\n'.join(current_content)
                    )
                current_section = {
                    'num': section_match.group(1),
                    'title': section_match.group(2).strip()
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section['num']] = self._parse_section_content(
                current_section['title'],
                '\n'.join(current_content)
            )
        
        return sections
    
    def _parse_section_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle, checks, and examples from section content"""
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line or line.startswith('##'):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        checks = self._generate_checks_from_donts(dont_examples, do_examples)
        
        return {
            'title': title,
            'principle': principle,
            'checks': checks,
            'dos': do_examples,
            'donts': dont_examples
        }
    
    def _extract_code_blocks(self, content: str, marker: str) -> List[str]:
        """Extract code blocks after a specific marker"""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            if marker in lines[i]:
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    i += 1
                    code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        code_lines.append(lines[i])
                        i += 1
                    
                    if code_lines:
                        blocks.append('\n'.join(code_lines))
            i += 1
        
        return blocks
    
    def _generate_checks_from_donts(self, dont_examples: List[str], do_examples: List[str]) -> List[Dict[str, Any]]:
        """Auto-generate validation checks from DON'T examples"""
        checks = []
        
        all_jargon = set()
        for dont in dont_examples:
            jargon = self._extract_jargon_keywords(dont)
            all_jargon.update(jargon)
        
        if all_jargon:
            checks.append({
                'question': 'Contains technical jargon?',
                'keywords': sorted(list(all_jargon)),
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        verbs = self._extract_action_verbs(dont_examples)
        if verbs:
            checks.append({
                'question': 'Uses nouns (not verbs)?',
                'keywords': verbs,
                'example_dont': next((d for d in dont_examples if any(v in d for v in verbs)), ''),
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if any('omit "should"' in d.lower() or 'missing "should"' in d.lower() for d in dont_examples):
            checks.append({
                'question': 'Starts with "should" (for it() blocks)?',
                'keywords': [],
                'example_dont': next((d for d in dont_examples if 'should' not in d.lower() and 'it(' in d), ''),
                'example_do': next((d for d in do_examples if 'should' in d.lower() and 'it(' in d), '')
            })
        
        return checks
    
    def _extract_jargon_keywords(self, code_example: str) -> List[str]:
        """Extract problematic technical words from code example"""
        jargon_words = []
        tech_verbs = ['extract', 'parse', 'serialize', 'deserialize', 'get', 'set',
                      'fetch', 'retrieve', 'call', 'return', 'handle', 'process']
        tech_nouns = ['flag', 'id', 'hook', 'handler', 'callback', 'listener',
                      'message', 'event', 'data', 'payload', 'api', 'endpoint',
                      'request', 'response', 'function', 'method', 'class', 'module']
        
        matches = re.findall(r"(?:describe|it)\(['\"]([^'\"]+)['\"]", code_example)
        
        for match in matches:
            words = match.split()
            for word in words:
                word_lower = word.lower().strip('(),;')
                if re.match(r'^[a-z]+[A-Z]', word):
                    jargon_words.append(word)
                elif word_lower in tech_verbs:
                    jargon_words.append(word_lower)
                elif word_lower in tech_nouns:
                    jargon_words.append(word_lower)
        
        paren_matches = re.findall(r'\(([^)]+)\)', code_example)
        for match in paren_matches:
            if 'don\'t' in code_example.lower()[:code_example.find(match)]:
                words = re.split(r'[,/\s]+', match)
                jargon_words.extend([w.strip().lower() for w in words if w.strip()])
        
        return list(set(jargon_words))
    
    def _extract_action_verbs(self, dont_examples: List[str]) -> List[str]:
        """Extract action verbs from DON'T examples"""
        verbs = set()
        common_verbs = ['when', 'calls', 'gets', 'sets', 'returns', 'fetches',
                        'creates', 'updates', 'deletes', 'handles', 'processes']
        
        for dont in dont_examples:
            matches = re.findall(r"describe\(['\"]([^'\"]+)['\"]", dont)
            for match in matches:
                first_word = match.split()[0].lower() if match.split() else ''
                if first_word in common_verbs:
                    verbs.add(first_word)
        
        return sorted(list(verbs))


# Global parser instance
_rule_parser = RuleParser()


def parse_structure_to_blocks(chunk: Dict[str, Any]) -> List[Dict[str, str]]:
    """Convert structure chunk to list of block dicts"""
    blocks = []
    structure_lines = chunk.get('structure', '').split('\n')
    for line in structure_lines:
        match = re.match(r'\s*Line (\d+):\s+(describe|it)\(["\']([^"\']+)', line)
        if match:
            blocks.append({
                'line': int(match.group(1)),
                'type': match.group(2),
                'text': match.group(3)
            })
    return blocks


def generate_section_prompt(block: Dict[str, str], section_num: str, 
                           section_rules: Dict[str, Any], domain_map: Optional[Dict] = None) -> str:
    """Generate structured prompt with mandatory checklist"""
    prompt = f"""
Block: Line {block['line']} - "{block['text']}"

VALIDATE AGAINST Section {section_num}: {section_rules['title']}

Principle: {section_rules['principle'][:200]}...

MANDATORY CHECKLIST (answer ALL):
"""
    
    for check in section_rules.get('checks', []):
        prompt += f"\n[] {check['question']}"
        if check.get('keywords'):
            keywords = check['keywords'][:8]
            prompt += f"\n  Keywords to avoid: {', '.join(keywords)}"
        
        if check.get('example_dont'):
            dont_snippet = check['example_dont'].replace('\n', ' ')[:120]
            prompt += f"\n  DON'T: {dont_snippet}..."
        
        if check.get('example_do'):
            do_snippet = check['example_do'].replace('\n', ' ')[:120]
            prompt += f"\n  DO: {do_snippet}..."
    
    if domain_map and domain_map.get('found'):
        if domain_map.get('domain_map'):
            map_content = domain_map['domain_map'].get('content', '')
            concepts = re.findall(r'^[A-Z][A-Za-z\s]+(?=:|\n)', map_content, re.MULTILINE)[:5]
            if concepts:
                prompt += f"\n\nDomain Terms Available: {', '.join(concepts)}"
    
    prompt += "\n\nRESPOND: violations: [list any found]"
    return prompt


def generate_cross_section_prompt(all_violations: List) -> str:
    """Generate final prompt for cross-section validation"""
    return f"""
FINAL CROSS-SECTION VALIDATION

You've validated across Sections 1-5.

Now check for issues that span MULTIPLE sections:

[] Do violations in different sections indicate systemic issues?
  (e.g., jargon in Section 1 + implementation details in Section 4 = not domain-focused)

[] Are there patterns across sections suggesting missing abstractions?
  (e.g., duplicate setup in Section 3 + testing internals in Section 2 = need helper)

[] Do Section 4 layer violations conflict with Section 1 readability?
  (e.g., "front-end" tests using business logic language)

RESPOND: cross_section_issues: [list any found]
"""


def validate_iterative_mode(test_file: str, framework: str, chunk_size: int = 10) -> List:
    """Iterative validation: section-by-section in chunks with AI feedback"""
    print("="*60)
    print("BDD VALIDATOR - ITERATIVE MODE")
    print("="*60)
    
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections with validation checklists")
    
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks")
    
    domain_map = discover_domain_maps(test_file)
    if domain_map.get('found'):
        print("[OK] Found domain maps for context")
    
    print(f"\nValidating against {len(rules)} sections")
    print(f"Chunk size: {chunk_size} blocks\n")
    
    all_violations = []
    
    for section_num in sorted(rules.keys()):
        violations = validate_section_iterative(
            all_blocks, section_num, rules[section_num], 
            chunk_size, domain_map
        )
        all_violations.extend(violations)
    
    print("\n" + "="*60)
    print("FINAL PASS: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    
    cross_prompt = generate_cross_section_prompt(all_violations)
    print(cross_prompt)
    print("\nAI: Review all violations above for cross-section issues\n")
    input("   Press ENTER when complete... ")
    
    print("\n" + "="*60)
    print("[COMPLETE] VALIDATION COMPLETE")
    print("="*60)
    return all_violations


def validate_section_iterative(blocks: List[Dict], section_num: str, 
                               section_rules: Dict, chunk_size: int,
                               domain_map: Dict) -> List:
    """Validate all blocks for one section in chunks"""
    print(f"\n{'='*60}")
    print(f"Section {section_num}: {section_rules['title']}")
    print(f"{'='*60}\n")
    
    violations = []
    total_chunks = (len(blocks) + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(total_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, len(blocks))
        chunk = blocks[start:end]
        
        print(f"\n[Chunk {chunk_idx+1}/{total_chunks}] {len(chunk)} blocks:\n")
        
        for i, block in enumerate(chunk, start=start+1):
            prompt = generate_section_prompt(block, section_num, section_rules, domain_map)
            print(f"Block {i}/{len(blocks)}: Line {block['line']}")
            print(prompt)
            print()
        
        print("-"*60)
        print(f"AI: Validate above {len(chunk)} blocks against Section {section_num}")
        print(f"    Report violations in chat")
        print("-"*60 + "\n")
        
        if chunk_idx < total_chunks - 1:
            input("   Press ENTER to continue to next chunk... ")
    
    print(f"\n[DONE] Section {section_num} Complete\n")
    return violations


def validate_batch_mode(test_file: str, framework: str) -> List:
    """Batch validation: all sections at once for quick overview"""
    print("="*60)
    print("BDD VALIDATOR - BATCH MODE")
    print("="*60)
    
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections")
    
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks\n")
    
    domain_map = discover_domain_maps(test_file)
    
    for section_num in sorted(rules.keys()):
        print(f"\n{'='*60}")
        print(f"Section {section_num}: {rules[section_num]['title']}")
        print(f"{'='*60}\n")
        
        for block in all_blocks:
            prompt = generate_section_prompt(block, section_num, rules[section_num], domain_map)
            print(prompt)
            print()
    
    print("\n" + "="*60)
    print("FINAL: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    print(generate_cross_section_prompt([]))
    
    print("\nAI: Validate all blocks against all sections above\n")
    
    return []


# ============================================================================
# BDD TEST FILE VALIDATION (Legacy - kept for backward compatibility)
# ============================================================================

# Note: Helper functions (detect_framework_from_file, discover_domain_maps, 
# load_rule_file, extract_dos_and_donts, extract_test_structure_chunks, etc.)
# are defined earlier in this file (around line 815+)

def bdd_validate_test_file(file_path: Optional[str] = None, thorough: bool = False, phase: str = 'signatures'):
    """
    Main function to validate a BDD test file.
    
    Args:
        file_path: Path to test file to validate
        thorough: Load detailed reference examples
        phase: 'signatures' (Phase 0) or 'implementation' (Phase 1+)
               - signatures: Only validate § 1 (Business Readable Language)
               - implementation: Validate all sections (§ 1-5)
    
    Steps:
    1. Get file path (from arg or current file)
    2. Detect framework from file path
    3. Load framework-specific rule
    4. Extract DO/DON'T examples by section (filtered by phase)
    5. Perform static checks
    6-9. AI evaluates test against each section's DO/DON'Ts
    10. Compile results
    11. Generate report
    12. Ask user for action
    """
    
    print("\n=== BDD Validation Starting ===")
    
    # Step 1: Get file path
    if not file_path:
        print("❌ No file path provided. Use: \\bdd-validate <file-path>")
        return {"error": "No file path provided"}
    
    print(f"Step 1: File path: {file_path}")
    
    test_path = Path(file_path)
    if not test_path.exists():
        print(f"❌ File not found: {file_path}")
        return {"error": "File not found"}
    
    print(f"✅ File exists: {test_path.name}")
    
    # Step 2: Detect framework
    print(f"Step 2: Detecting framework...")
    framework = detect_framework_from_file(file_path)
    if not framework:
        print(f"❌ File doesn't match BDD test patterns: {file_path}")
        print("   Expected: *.test.js, *.spec.ts, test_*.py, etc.")
        return {"error": "Not a BDD test file"}
    
    print(f"✅ Detected framework: {framework.upper()}")
    
    # Step 2.5: Discover domain maps
    print(f"Step 2.5: Discovering domain maps in test directory...")
    domain_maps = discover_domain_maps(file_path)
    
    if domain_maps["found"]:
        if domain_maps["domain_map"]:
            map_name = Path(domain_maps["domain_map"]["path"]).name
            print(f"✅ Found domain map: {map_name}")
        if domain_maps["interaction_map"]:
            map_name = Path(domain_maps["interaction_map"]["path"]).name
            print(f"✅ Found interaction map: {map_name}")
    else:
        print(f"⚠️  No domain maps found in {test_path.parent}")
        print(f"   Recommendation:")
        print(f"   1. Run: \\ddd-analyze <source-file>")
        print(f"   2. Run: \\ddd-interactions <source-file>")
        print(f"   Domain maps provide primary source for test structure and naming.")
    
    # Step 3: Load rule file
    print(f"Step 3: Loading {framework} rule file...")
    rule_data = load_rule_file(framework)
    if not rule_data:
        print(f"❌ Could not load rule file for {framework}")
        return {"error": "Rule file not found"}
    
    print(f"✅ Loaded rule: {rule_data['rule_path']}")
    
    # Step 4: Extract DO/DON'T examples - ALWAYS use ALL sections
    print("Step 4: Extracting DO/DON'T examples...")
    sections = extract_dos_and_donts(rule_data['content'])
    print(f"   Validating all sections (§ 1-5) - rules apply at all phases")
    
    total_dos = sum(len(s['dos']) for s in sections.values())
    total_donts = sum(len(s['donts']) for s in sections.values())
    print(f"✅ Extracted {total_dos} DO examples and {total_donts} DON'T examples from {len(sections)} sections")
    
    # Step 5: Extract test structure in manageable chunks
    print("Step 5: Extracting test structure (chunked by describe blocks)...")
    chunks = extract_test_structure_chunks(file_path, framework)
    total_blocks = sum(len(chunk['structure'].split('\n')) for chunk in chunks)
    print(f"   Extracted {total_blocks} test blocks in {len(chunks)} chunk(s)")
    
    # Step 5b: Static checks on all chunks
    print("Step 5b: Running static analysis...")
    static_issues = []
    for chunk in chunks:
        chunk_issues = perform_static_checks(chunk['structure'], framework)
        static_issues.extend(chunk_issues)
    
    if static_issues:
        print(f"   Found {len(static_issues)} static issues")
    else:
        print(f"   No static issues found")
    
    # Step 5c: Detect § 3 violations (duplicate code in siblings)
    print("Step 5c: Detecting § 3 violations (duplicate code in 3+ siblings)...")
    section3_violations = detect_section3_violations(file_path, framework)
    
    if section3_violations:
        print(f"   Found {len(section3_violations)} § 3 violation groups")
        # Convert to static issues format
        for v in section3_violations:
            violation_type = "Decorator Pattern" if v['type'] == 'decorator_pattern' else "Duplicate Arrange"
            static_issues.append({
                "line": v['parent_line'],
                "issue": f"{violation_type}: {v['sibling_count']} sibling {v['sibling_type']}() blocks with {v['similarity']:.0%} similar code (lines: {', '.join(map(str, v['sibling_lines']))})",
                "type": "error",
                "rule": "3. Balance Context Sharing with Localization",
                "details": v
            })
    else:
        print(f"   No § 3 violations found")
    
    # Step 6: Load reference examples if thorough mode
    reference_examples = {}
    if thorough:
        print("Step 6: Loading reference examples (THOROUGH MODE)...")
        reference_examples = load_relevant_reference_examples(framework, list(sections.keys()))
        print(f"   Loaded {len(reference_examples)} reference sections")
    
    # Step 7: Show static issues if found
    if static_issues:
        print("\n" + "="*80)
        print("STATIC VIOLATIONS DETECTED")
        print("="*80)
        for issue in static_issues:
            print(f"Line {issue['line']}: {issue['issue']}")
            print(f"   Rule: {issue['rule']}")
        print("="*80)
    
    # Step 8: Print FULL RULE FILE for AI Agent
    print("\n" + "="*80)
    print("FULL BDD RULE FILE - READ THIS")
    print("="*80)
    print(f"Phase: {phase.upper()}")
    print(f"Framework: {framework.upper()}")
    print(f"Rule File: {rule_data['rule_path']}")
    print("="*80)
    print(rule_data['content'])
    print("="*80)
    
    # Show domain maps if found
    if domain_maps["found"]:
        print("\n" + "="*80)
        print("DOMAIN MAPS FOUND - USE AS PRIMARY SOURCE")
        print("="*80)
        if domain_maps["domain_map"]:
            print("\nDOMAIN MAP:")
            print("-" * 80)
            print(domain_maps["domain_map"]["content"])
        if domain_maps["interaction_map"]:
            print("\nINTERACTION MAP:")
            print("-" * 80)
            print(domain_maps["interaction_map"]["content"])
        print("="*80)
    
    # Show test code to validate
    print("\n" + "="*80)
    print("YOUR TEST CODE TO VALIDATE")
    print("="*80)
    for chunk in chunks:
        if chunk.get('context'):
            print(f"\nContext: {chunk['context']}")
        print(chunk['structure'])
    
    # Simple instruction
    print("\n" + "="*80)
    print("AI AGENT: VALIDATE ALL TESTS WITH THESE RULES AND EXAMPLES!")
    print("="*80)
    print("1. Compare every describe/it against the DO/DON'T examples in rule")
    if domain_maps["found"]:
        print("2. Verify test structure aligns with domain map hierarchy")
        print("3. Check test names use domain concept terminology")
        print("4. Validate helpers/mocks align with domain concepts")
        print("5. Find violations")
        print("6. Fix violations")
        print("7. Re-run until zero violations")
    else:
        print("2. Find violations")
        print("3. Fix violations")
        print("4. Re-run until zero violations")
    print("="*80)
    
    # Return data for AI Agent to analyze
    validation_data = {
        "test_file": file_path,
        "framework": framework,
        "phase": phase,
        "rule_content": rule_data['content'],
        "test_chunks": chunks,
        "total_blocks": total_blocks,
        "static_issues": static_issues,
        "domain_maps": domain_maps  # Include discovered domain maps
    }
    
    return validation_data


# ============================================================================
# ENHANCED VALIDATOR - Rule Parsing & Iterative Validation
# ============================================================================

class RuleParser:
    """Parse BDD rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, framework: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if framework in self._cache:
            return self._cache[framework]
        
        rule_data = load_rule_file(framework)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        self._cache[framework] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section['num']] = self._parse_section_content(
                        current_section['title'],
                        '\n'.join(current_content)
                    )
                current_section = {
                    'num': section_match.group(1),
                    'title': section_match.group(2).strip()
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section['num']] = self._parse_section_content(
                current_section['title'],
                '\n'.join(current_content)
            )
        
        return sections
    
    def _parse_section_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle, checks, and examples from section content"""
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line or line.startswith('##'):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        checks = self._generate_checks_from_donts(dont_examples, do_examples)
        
        return {
            'title': title,
            'principle': principle,
            'checks': checks,
            'dos': do_examples,
            'donts': dont_examples
        }
    
    def _extract_code_blocks(self, content: str, marker: str) -> List[str]:
        """Extract code blocks after a specific marker"""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            if marker in lines[i]:
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    i += 1
                    code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        code_lines.append(lines[i])
                        i += 1
                    
                    if code_lines:
                        blocks.append('\n'.join(code_lines))
            i += 1
        
        return blocks
    
    def _generate_checks_from_donts(self, dont_examples: List[str], do_examples: List[str]) -> List[Dict[str, Any]]:
        """Auto-generate validation checks from DON'T examples"""
        checks = []
        
        all_jargon = set()
        for dont in dont_examples:
            jargon = self._extract_jargon_keywords(dont)
            all_jargon.update(jargon)
        
        if all_jargon:
            checks.append({
                'question': 'Contains technical jargon?',
                'keywords': sorted(list(all_jargon)),
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        verbs = self._extract_action_verbs(dont_examples)
        if verbs:
            checks.append({
                'question': 'Uses nouns (not verbs)?',
                'keywords': verbs,
                'example_dont': next((d for d in dont_examples if any(v in d for v in verbs)), ''),
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if any('omit "should"' in d.lower() or 'missing "should"' in d.lower() for d in dont_examples):
            checks.append({
                'question': 'Starts with "should" (for it() blocks)?',
                'keywords': [],
                'example_dont': next((d for d in dont_examples if 'should' not in d.lower() and 'it(' in d), ''),
                'example_do': next((d for d in do_examples if 'should' in d.lower() and 'it(' in d), '')
            })
        
        return checks
    
    def _extract_jargon_keywords(self, code_example: str) -> List[str]:
        """Extract problematic technical words from code example"""
        jargon_words = []
        tech_verbs = ['extract', 'parse', 'serialize', 'deserialize', 'get', 'set',
                      'fetch', 'retrieve', 'call', 'return', 'handle', 'process']
        tech_nouns = ['flag', 'id', 'hook', 'handler', 'callback', 'listener',
                      'message', 'event', 'data', 'payload', 'api', 'endpoint',
                      'request', 'response', 'function', 'method', 'class', 'module']
        
        matches = re.findall(r"(?:describe|it)\(['\"]([^'\"]+)['\"]", code_example)
        
        for match in matches:
            words = match.split()
            for word in words:
                word_lower = word.lower().strip('(),;')
                if re.match(r'^[a-z]+[A-Z]', word):
                    jargon_words.append(word)
                elif word_lower in tech_verbs:
                    jargon_words.append(word_lower)
                elif word_lower in tech_nouns:
                    jargon_words.append(word_lower)
        
        paren_matches = re.findall(r'\(([^)]+)\)', code_example)
        for match in paren_matches:
            if 'don\'t' in code_example.lower()[:code_example.find(match)]:
                words = re.split(r'[,/\s]+', match)
                jargon_words.extend([w.strip().lower() for w in words if w.strip()])
        
        return list(set(jargon_words))
    
    def _extract_action_verbs(self, dont_examples: List[str]) -> List[str]:
        """Extract action verbs from DON'T examples"""
        verbs = set()
        common_verbs = ['when', 'calls', 'gets', 'sets', 'returns', 'fetches',
                        'creates', 'updates', 'deletes', 'handles', 'processes']
        
        for dont in dont_examples:
            matches = re.findall(r"describe\(['\"]([^'\"]+)['\"]", dont)
            for match in matches:
                first_word = match.split()[0].lower() if match.split() else ''
                if first_word in common_verbs:
                    verbs.add(first_word)
        
        return sorted(list(verbs))


# Global parser instance
_rule_parser = RuleParser()


def parse_structure_to_blocks(chunk: Dict[str, Any]) -> List[Dict[str, str]]:
    """Convert structure chunk to list of block dicts"""
    blocks = []
    structure_lines = chunk.get('structure', '').split('\n')
    for line in structure_lines:
        match = re.match(r'\s*Line (\d+):\s+(describe|it)\(["\']([^"\']+)', line)
        if match:
            blocks.append({
                'line': int(match.group(1)),
                'type': match.group(2),
                'text': match.group(3)
            })
    return blocks


def generate_section_prompt(block: Dict[str, str], section_num: str, 
                           section_rules: Dict[str, Any], domain_map: Optional[Dict] = None) -> str:
    """Generate structured prompt with mandatory checklist"""
    prompt = f"""
Block: Line {block['line']} - "{block['text']}"

VALIDATE AGAINST Section {section_num}: {section_rules['title']}

Principle: {section_rules['principle'][:200]}...

MANDATORY CHECKLIST (answer ALL):
"""
    
    for check in section_rules.get('checks', []):
        prompt += f"\n[] {check['question']}"
        if check.get('keywords'):
            keywords = check['keywords'][:8]
            prompt += f"\n  Keywords to avoid: {', '.join(keywords)}"
        
        if check.get('example_dont'):
            dont_snippet = check['example_dont'].replace('\n', ' ')[:120]
            prompt += f"\n  DON'T: {dont_snippet}..."
        
        if check.get('example_do'):
            do_snippet = check['example_do'].replace('\n', ' ')[:120]
            prompt += f"\n  DO: {do_snippet}..."
    
    if domain_map and domain_map.get('found'):
        if domain_map.get('domain_map'):
            map_content = domain_map['domain_map'].get('content', '')
            concepts = re.findall(r'^[A-Z][A-Za-z\s]+(?=:|\n)', map_content, re.MULTILINE)[:5]
            if concepts:
                prompt += f"\n\nDomain Terms Available: {', '.join(concepts)}"
    
    prompt += "\n\nRESPOND: violations: [list any found]"
    return prompt


def generate_cross_section_prompt(all_violations: List) -> str:
    """Generate final prompt for cross-section validation"""
    return f"""
FINAL CROSS-SECTION VALIDATION

You've validated across Sections 1-5.

Now check for issues that span MULTIPLE sections:

[] Do violations in different sections indicate systemic issues?
  (e.g., jargon in Section 1 + implementation details in Section 4 = not domain-focused)

[] Are there patterns across sections suggesting missing abstractions?
  (e.g., duplicate setup in Section 3 + testing internals in Section 2 = need helper)

[] Do Section 4 layer violations conflict with Section 1 readability?
  (e.g., "front-end" tests using business logic language)

RESPOND: cross_section_issues: [list any found]
"""


def validate_iterative_mode(test_file: str, framework: str, chunk_size: int = 10) -> List:
    """Iterative validation: section-by-section in chunks with AI feedback"""
    print("="*60)
    print("BDD VALIDATOR - ITERATIVE MODE")
    print("="*60)
    
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections with validation checklists")
    
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks")
    
    domain_map = discover_domain_maps(test_file)
    if domain_map.get('found'):
        print("[OK] Found domain maps for context")
    
    print(f"\nValidating against {len(rules)} sections")
    print(f"Chunk size: {chunk_size} blocks\n")
    
    all_violations = []
    
    for section_num in sorted(rules.keys()):
        violations = validate_section_iterative(
            all_blocks, section_num, rules[section_num], 
            chunk_size, domain_map
        )
        all_violations.extend(violations)
    
    print("\n" + "="*60)
    print("FINAL PASS: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    
    cross_prompt = generate_cross_section_prompt(all_violations)
    print(cross_prompt)
    print("\nAI: Review all violations above for cross-section issues\n")
    input("   Press ENTER when complete... ")
    
    print("\n" + "="*60)
    print("[COMPLETE] VALIDATION COMPLETE")
    print("="*60)
    return all_violations


def validate_section_iterative(blocks: List[Dict], section_num: str, 
                               section_rules: Dict, chunk_size: int,
                               domain_map: Dict) -> List:
    """Validate all blocks for one section in chunks"""
    print(f"\n{'='*60}")
    print(f"Section {section_num}: {section_rules['title']}")
    print(f"{'='*60}\n")
    
    violations = []
    total_chunks = (len(blocks) + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(total_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, len(blocks))
        chunk = blocks[start:end]
        
        print(f"\n[Chunk {chunk_idx+1}/{total_chunks}] {len(chunk)} blocks:\n")
        
        for i, block in enumerate(chunk, start=start+1):
            prompt = generate_section_prompt(block, section_num, section_rules, domain_map)
            print(f"Block {i}/{len(blocks)}: Line {block['line']}")
            print(prompt)
            print()
        
        print("-"*60)
        print(f"AI: Validate above {len(chunk)} blocks against Section {section_num}")
        print(f"    Report violations in chat")
        print("-"*60 + "\n")
        
        if chunk_idx < total_chunks - 1:
            input("   Press ENTER to continue to next chunk... ")
    
    print(f"\n[DONE] Section {section_num} Complete\n")
    return violations


def validate_batch_mode(test_file: str, framework: str) -> List:
    """Batch validation: all sections at once for quick overview"""
    print("="*60)
    print("BDD VALIDATOR - BATCH MODE")
    print("="*60)
    
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections")
    
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks\n")
    
    domain_map = discover_domain_maps(test_file)
    
    for section_num in sorted(rules.keys()):
        print(f"\n{'='*60}")
        print(f"Section {section_num}: {rules[section_num]['title']}")
        print(f"{'='*60}\n")
        
        for block in all_blocks:
            prompt = generate_section_prompt(block, section_num, rules[section_num], domain_map)
            print(prompt)
            print()
    
    print("\n" + "="*60)
    print("FINAL: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    print(generate_cross_section_prompt([]))
    
    print("\nAI: Validate all blocks against all sections above\n")
    
    return []


# ============================================================================
# RUNNER GUARD UTILITY
# ============================================================================

def require_command_invocation(command_name: str):
    """
    Guard to prevent direct runner execution.
    
    Checks if runner was invoked with --from-command flag (set by Cursor commands).
    If not, displays helpful message directing user to proper slash command.
    
    Args:
        command_name: The slash command name (e.g., "bdd-validate")
    """
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT - Dispatcher for all BDD commands
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python bdd-runner.py <command> [args...]")
        print("\nCommands:")
        print("  workflow <file_path> [scope] [phase] [cursor_line] [--auto]")
        print("  validate <file_path> [--thorough] [--phase=<phase>]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "workflow":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-workflow")
        
        # Parse workflow arguments
        if len(sys.argv) < 3:
            print("Error: file_path required for workflow command")
            sys.exit(1)
        
        file_path = sys.argv[2]
        scope = sys.argv[3] if len(sys.argv) > 3 else "describe"
        phase = sys.argv[4] if len(sys.argv) > 4 else None
        cursor_line = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else None
        auto = "--auto" in sys.argv
        
        try:
            workflow_data = bdd_workflow(file_path, scope, phase, cursor_line, auto)
            
            if "error" in workflow_data:
                print(f"\nError: {workflow_data['error']}")
                sys.exit(1)
            
            print("\nWorkflow Data Ready:")
            print(f"  Phase: {workflow_data['phase']}")
            print(f"  Scope: {workflow_data['scope']}")
            print(f"  Tests in scope: {len(workflow_data['test_structure']['scoped_tests'])}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "validate":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-validate")
        
        print("BDD Enhanced Validator Starting...")
        
        # Parse validate arguments
        if len(sys.argv) < 3:
            print("Usage: python bdd-runner.py validate <test-file-path> [options]")
            print("\nOptions:")
            print("  --batch              Batch mode (all sections at once)")
            print("  --chunk-size N       Blocks per chunk in iterative mode (default: 10)")
            print("  --no-guard           Skip command invocation guard")
            print("\nModes:")
            print("  Default: Iterative validation (section-by-section in chunks)")
            print("  --batch: Batch validation (all sections at once)")
            sys.exit(1)
        
        file_path = sys.argv[2]
        batch_mode = '--batch' in sys.argv
        chunk_size = 10
        
        # Check for --chunk-size flag
        for arg in sys.argv:
            if arg.startswith('--chunk-size='):
                chunk_size = int(arg.split('=')[1])
            elif arg.startswith('--chunk-size'):
                idx = sys.argv.index(arg)
                if idx + 1 < len(sys.argv):
                    chunk_size = int(sys.argv[idx + 1])
        
        # Check file exists
        if not Path(file_path).exists():
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(1)
        
        # Detect framework
        print(f"Analyzing {file_path}...")
        framework = detect_framework_from_file(file_path)
        
        if not framework:
            print(f"[ERROR] Could not detect test framework from file path")
            print(f"        Expected Jest (.test.js, .spec.js, etc.) or Mamba (_test.py, test_*.py)")
            sys.exit(1)
        
        print(f"[OK] Detected framework: {framework}\n")
        
        try:
            # Run enhanced validation in selected mode
            if batch_mode:
                validate_batch_mode(file_path, framework)
            else:
                validate_iterative_mode(file_path, framework, chunk_size)
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
