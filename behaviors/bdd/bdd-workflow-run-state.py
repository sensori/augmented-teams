"""
BDD Workflow RUN State Machine

Enforces strict workflow progression:
- Code checks state before/after every step
- AI must verify (run /bdd-validate)
- Human must approve before proceeding
- Cannot skip or bypass steps

A RUN is a session from start to completion of a workflow step.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from enum import Enum


class RunStatus(Enum):
    """Run lifecycle status"""
    STARTED = "started"              # Work began, not verified
    AI_VERIFIED = "ai_verified"      # AI ran validation, passed
    HUMAN_APPROVED = "human_approved"  # Human reviewed and approved
    COMPLETED = "completed"          # Fully complete


class StepType(Enum):
    """Workflow step types"""
    SAMPLE = "sample"                 # Any sample (Phase 0) - actual name in context
    EXPAND = "expand"                 # Expand to full scope (Phase 0)
    RED_BATCH = "red_batch"           # RED phase batch
    GREEN_BATCH = "green_batch"       # GREEN phase batch
    REFACTOR_SUGGEST = "refactor_suggest"  # REFACTOR suggest
    REFACTOR_IMPLEMENT = "refactor_implement"  # REFACTOR implement


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
    
    def start_run(self, step_type: StepType, context: Dict[str, Any]) -> str:
        """
        Start a new run.
        
        Returns: run_id
        Raises: RuntimeError if previous run not complete
        """
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
    
    def record_ai_verification(
        self, 
        run_id: str, 
        validation_results: Dict[str, Any]
    ):
        """
        Record that AI verified the work (ran /bdd-validate).
        
        Args:
            run_id: Run ID
            validation_results: Results from /bdd-validate
        
        Raises: RuntimeError if run not in STARTED status
        """
        run = self._get_run(run_id)
        if not run:
            raise RuntimeError(f"Run {run_id} not found")
        
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
        """
        Record human review and approval.
        
        Args:
            run_id: Run ID
            approved: True if approved, False if rejected
            feedback: Optional human feedback
        
        Raises: RuntimeError if run not AI_VERIFIED
        """
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
        """
        Mark run as completed.
        
        Raises: RuntimeError if run not HUMAN_APPROVED
        """
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
    
    def can_proceed_to_next_step(self) -> tuple[bool, str]:
        """
        Check if can proceed to next workflow step.
        
        Returns: (can_proceed, reason)
        """
        current_run = self.get_current_run()
        
        if not current_run:
            return (True, "No active run, can start new one")
        
        status = current_run["status"]
        
        if status == RunStatus.COMPLETED.value:
            return (True, "Current run complete")
        
        if status == RunStatus.STARTED.value:
            return (False, "AI must verify (run /bdd-validate) before proceeding")
        
        if status == RunStatus.AI_VERIFIED.value:
            return (False, "Human must review and approve before proceeding")
        
        if status == RunStatus.HUMAN_APPROVED.value:
            return (False, "Run approved but not marked complete. Call complete_run()")
        
        return (False, f"Unknown status: {status}")
    
    def enforce_can_proceed(self):
        """
        Enforce that workflow can proceed.
        
        Raises: RuntimeError with clear message if cannot proceed
        """
        can_proceed, reason = self.can_proceed_to_next_step()
        if not can_proceed:
            current_run = self.get_current_run()
            raise RuntimeError(
                f"Cannot proceed to next step.\n"
                f"Reason: {reason}\n"
                f"Current run: {current_run['run_id']}\n"
                f"Status: {current_run['status']}\n"
                f"Step type: {current_run['step_type']}"
            )
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get human-readable status summary"""
        current_run = self.get_current_run()
        can_proceed, reason = self.can_proceed_to_next_step()
        
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

