#!/usr/bin/env python3
"""
Delivery Pipeline - State-Managed Deployment Orchestration

TABLE OF CONTENTS:
1. DELIVERY PIPELINE ORCHESTRATION
   1.1 Pipeline State Management
   1.2 Step Execution Control
   1.3 State Persistence
2. PROVISIONER INTEGRATION
   2.1 Multi-Mode Support
   2.2 Conditional Provisioning
3. INTERACTIVE CONTROLS
   3.1 Pause/Resume Functionality
   3.2 Manual Step Approval
"""

import json
import sys
import subprocess
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime

# Exit status
class ExitStatus:
    SUCCESS = 0
    FAILURE = 1
    NEEDS_HUMAN_ACTIVITY = 98  # Step requires human activity (approval, review, configure)
    NEEDS_HUMAN_INTERVENTION = 99  # Error requires human intervention to fix
    
    @classmethod
    def is_success(cls, status: int) -> bool:
        """Check if exit status is success"""
        return status == cls.SUCCESS
    
    @classmethod
    def is_failure(cls, status: int) -> bool:
        """Check if exit status is failure"""
        return status == cls.FAILURE
    
    @classmethod
    def needs_human_activity(cls, status: int) -> bool:
        """Check if exit status needs human activity"""
        return status == cls.NEEDS_HUMAN_ACTIVITY
    
    @classmethod
    def needs_human_intervention(cls, status: int) -> bool:
        """Check if exit status needs human intervention"""
        return status == cls.NEEDS_HUMAN_INTERVENTION

# Windows-safe print function
def safe_print(message: str):
    """Print with automatic Unicode handling for Windows"""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        import re
        clean_message = re.sub(r'[\U0001F300-\U0001F9FF]', '', message)
        try:
            print(clean_message, flush=True)
        except:
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)

# Step types
class StepType:
    AUTOMATED = 'automated'  # Fully automated, no human needed
    AI = 'ai'  # AI generates content, then human reviews
    HUMAN_ACTIVITY = 'human-activity'  # Human activity required (approval, review, configure)
    HUMAN_INTERVENTION = 'human-intervention'  # Human intervention required (error needs fixing)

@dataclass
class StepState:
    """State of a single deployment step"""
    name: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'skipped'
    step_type: str = StepType.AUTOMATED  # automated, ai, hitl-a, hitl-i
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineState:
    """Current state of the deployment pipeline"""
    feature_name: str
    pipeline_id: str
    current_step: Optional[str] = None
    current_phase: Optional[str] = None
    status: str = 'pending'  # 'pending', 'running', 'paused', 'completed', 'failed'
    started_at: str = ""
    last_updated: str = ""
    steps: Dict[str, StepState] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    commit_sha: Optional[str] = None
    github_run_id: Optional[str] = None
    human_activity_type: Optional[str] = None  # 'activity', 'intervention', None
    human_activity_reason: Optional[str] = None
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        data = asdict(self)
        data['steps'] = {k: asdict(v) for k, v in self.steps.items()}
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dict"""
        steps = {k: StepState(**v) for k, v in data.get('steps', {}).items()}
        return cls(
            feature_name=data['feature_name'],
            pipeline_id=data['pipeline_id'],
            current_step=data.get('current_step'),
            status=data.get('status', 'pending'),
            started_at=data.get('started_at', ''),
            last_updated=data.get('last_updated', ''),
            steps=steps,
            config=data.get('config', {})
        )


class PipelineStateManager:
    """
    1. DELIVERY PIPELINE ORCHESTRATION
    1.1 Pipeline State Management - Load and save state files
    """
    
    STATE_FILE = ".deployment-state.json"
    
    def __init__(self, feature_path: Path):
        self.feature_path = feature_path
        self.state_file = feature_path / self.STATE_FILE
        
    def load_state(self) -> Optional[PipelineState]:
        """Load pipeline state from feature directory"""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            return PipelineState.from_dict(data)
        except Exception as e:
            safe_print(f"[WARN] Failed to load state: {e}")
            return None
    
    def save_state(self, state: PipelineState) -> bool:
        """Save pipeline state to feature directory"""
        try:
            state.last_updated = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            safe_print(f"[WARN] Failed to save state: {e}")
            return False
    
    def clear_state(self) -> bool:
        """Clear pipeline state"""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            return True
        except Exception as e:
            safe_print(f"[WARN] Failed to clear state: {e}")
            return False


class DeliveryPipeline:
    """
    1. DELIVERY PIPELINE ORCHESTRATION
    Main orchestration engine for feature deployment
    
    1.2 Step Execution Control - Execute steps with pause/resume
    1.3 State Persistence - Track progress in feature directory
    """
    
    # Phases and Steps structure - TDD workflow
    PHASES = [
        {
            'name': 'Initiate Feature',
            'steps': [
                {'name': 'PROMPT_CREATE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'Human describes feature requirements'}
            ]
        },
        {
            'name': 'Setup',
            'steps': [
                {'name': 'STRUCTURE_CREATE', 'type': StepType.AUTOMATED},
                {'name': 'CONFIG_GENERATE', 'type': StepType.AUTOMATED}
            ]
        },
        {
            'name': 'Test Scaffolding',
            'steps': [
                {'name': 'SCAFFOLD_SUGGEST', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI suggests test scaffolds, human reviews'},
                {'name': 'SCAFFOLD_BUILD', 'type': StepType.AUTOMATED}
            ]
        },
        {
            'name': 'Test Red',
            'steps': [
                {'name': 'TEST_GENERATE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI generates test code for first test'},
                {'name': 'TEST_REFINE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'Human reviews and refines test'},
                {'name': 'TEST_RUN_FAIL', 'type': StepType.AUTOMATED}  # Expect to fail
            ]
        },
        {
            'name': 'Code Green',
            'steps': [
                {'name': 'CODE_GENERATE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI generates code to pass test'},
                {'name': 'CODE_REFINE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'Human reviews generated code'},
                {'name': 'CODE_TEST_PASS', 'type': StepType.AUTOMATED},
                {'name': 'CODE_RETRY', 'type': StepType.AUTOMATED}  # Max retries (default 5)
            ]
        },
        {
            'name': 'Refactor',
            'steps': [
                {'name': 'REVIEW_DUPLICATION', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI reviews for duplication, bad design'},
                {'name': 'GENERATE_FIX', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI generates refactored code'},
                {'name': 'REVIEW_REFACTOR', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'Human reviews refactoring'}
            ]
        },
        {
            'name': 'Commit',
            'steps': [
                {'name': 'COMMIT_GENERATE', 'type': StepType.HUMAN_ACTIVITY, 'reason': 'AI generates commit message and tag'}
            ]
        }
    ]
    
    def __init__(self, feature_name: str, feature_path: Path, provision_mode: str = "AZURE", config=None):
        self.feature_name = feature_name
        self.feature_path = Path(feature_path)
        self.provision_mode = provision_mode
        self.config = config or {}
        self.state_mgr = PipelineStateManager(self.feature_path)
        
        # Load existing state or create new
        self.state = self.state_mgr.load_state()
        if self.state is None:
            pipeline_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.state = PipelineState(
                feature_name=feature_name,
                pipeline_id=pipeline_id,
                started_at=datetime.now().isoformat(),
                status='running',
                config={'provision_mode': provision_mode, **self.config}
            )
            # Initialize all steps from PHASES
            for phase in self.PHASES:
                for step_def in phase['steps']:
                    self.state.steps[step_def['name']] = StepState(
                        name=step_def['name'],
                        status='pending',
                        step_type=step_def['type']
                    )
    
    def get_step_status(self, step_name: str) -> Optional[str]:
        """Get status of a specific step"""
        if step_name in self.state.steps:
            return self.state.steps[step_name].status
        return None
    
    def mark_step_started(self, step_name: str):
        """Mark a step as started"""
        if step_name not in self.state.steps:
            self.state.steps[step_name] = StepState(name=step_name, status='running')
        else:
            step = self.state.steps[step_name]
            step.status = 'running'
            step.started_at = datetime.now().isoformat()
            step.attempts += 1
        self.state.current_step = step_name
        self.state.status = 'running'
        self.state_mgr.save_state(self.state)
    
    def mark_step_completed(self, step_name: str, outputs: Optional[Dict] = None):
        """Mark a step as completed"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'completed'
            step.completed_at = datetime.now().isoformat()
            if outputs:
                step.outputs.update(outputs)
        self.state_mgr.save_state(self.state)
    
    def mark_step_failed(self, step_name: str, error: str):
        """Mark a step as failed"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'failed'
            step.completed_at = datetime.now().isoformat()
            step.error = error
        self.state.status = 'failed'
        self.state_mgr.save_state(self.state)
    
    def mark_step_skipped(self, step_name: str):
        """Mark a step as skipped"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'skipped'
            step.completed_at = datetime.now().isoformat()
        self.state_mgr.save_state(self.state)
    
    def pause(self, reason: str = ""):
        """
        3. INTERACTIVE CONTROLS
        3.1 Pause/Resume Functionality - Allow manual intervention
        """
        self.state.status = 'paused'
        self.state_mgr.save_state(self.state)
        safe_print(f"\n[PAUSED] Pipeline paused: {reason}")
        safe_print(f"[INFO] Current step: {self.state.current_step}")
        safe_print(f"[INFO] To resume, run: python delivery-pipeline.py resume {self.feature_name}")
    
    def resume(self) -> bool:
        """Resume a paused pipeline"""
        if self.state.status != 'paused':
            safe_print(f"[ERROR] Pipeline is not paused (status: {self.state.status})")
            return False
        
        self.state.status = 'running'
        self.state_mgr.save_state(self.state)
        safe_print(f"[RESUME] Resuming from step: {self.state.current_step}")
        return True
    
    def get_current_step(self) -> Optional[str]:
        """Get the current step name"""
        return self.state.current_step
    
    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """Get the next pending step to execute"""
        for phase in self.PHASES:
            for step_def in phase['steps']:
                step_name = step_def['name']
                step = self.state.steps.get(step_name)
                if not step or step.status == 'pending':
                    return {
                        'name': step_name,
                        'phase': phase['name'],
                        'type': step_def['type'],
                        'func': lambda: {'success': True}  # Placeholder
                    }
        return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        completed = sum(1 for s in self.state.steps.values() if s.status == 'completed')
        failed = sum(1 for s in self.state.steps.values() if s.status == 'failed')
        pending = sum(1 for s in self.state.steps.values() if s.status in ['pending', 'running'])
        
        return {
            'status': self.state.status,
            'current_step': self.state.current_step,
            'total_steps': len(self.state.steps),
            'completed': completed,
            'failed': failed,
            'pending': pending
        }
    
    def require_human_activity(self, reason: str):
        """Require human activity (approval, review, configure)"""
        if not self.config.get('hitl_enabled', True):
            safe_print(f"[HUMAN] Activity gate skipped (--no-hitl): {reason}")
            return
        
        self.state.human_activity_type = 'activity'
        self.state.human_activity_reason = reason
        self.pause(f"Human activity required: {reason}")
        safe_print(f"\n[HUMAN-ACTIVITY] Human activity required for step: {self.state.current_step}")
        safe_print(f"[HUMAN-ACTIVITY] Reason: {reason}")
        safe_print(f"[HUMAN-ACTIVITY] To approve: python delivery-pipeline.py approve --feature {self.feature_name}")
        safe_print(f"[HUMAN-ACTIVITY] To reject: python delivery-pipeline.py reject --feature {self.feature_name}")
        self.state_mgr.save_state(self.state)
        sys.exit(ExitStatus.NEEDS_HUMAN_ACTIVITY)
    
    def require_human_intervention(self, error: str):
        """Require human intervention (error needs fixing)"""
        self.state.human_activity_type = 'intervention'
        self.state.human_activity_reason = error
        self.pause(f"Error in {self.state.current_step}: {error}")
        safe_print(f"\n[HUMAN-INTERVENTION] Human intervention required for step: {self.state.current_step}")
        safe_print(f"[HUMAN-INTERVENTION] Error: {error}")
        safe_print(f"[HUMAN-INTERVENTION] Fix issue, then: python delivery-pipeline.py resume --feature {self.feature_name}")
        self.state_mgr.save_state(self.state)
        sys.exit(ExitStatus.NEEDS_HUMAN_INTERVENTION)
    
    def execute_step(self, step_name: str, step_func) -> bool:
        """
        1.2 Step Execution Control - Execute steps with state tracking and HITL gates
        """
        # Check if step requires human activity
        step = self.state.steps.get(step_name)
        if step and step.step_type == StepType.HUMAN_ACTIVITY:
            # Find reason from step definition
            for phase in self.PHASES:
                for step_def in phase['steps']:
                    if step_def['name'] == step_name and 'reason' in step_def:
                        self.require_human_activity(step_def['reason'])
                        break
        
        self.mark_step_started(step_name)
        
        try:
            result = step_func()
            if result.get('success', False):
                self.mark_step_completed(step_name, result.get('outputs'))
                return True
            else:
                error = result.get('error', 'Unknown error')
                self.mark_step_failed(step_name, error)
                # Human interventions for errors are NOT skipped
                self.require_human_intervention(error)
                return False
        except Exception as e:
            self.mark_step_failed(step_name, str(e))
            self.require_human_intervention(str(e))
            raise
    
    def finalize(self, success: bool):
        """Mark pipeline as completed or failed"""
        if success:
            self.state.status = 'completed'
        else:
            self.state.status = 'failed'
        self.state_mgr.save_state(self.state)
    
    def show_summary(self):
        """Display pipeline status summary"""
        summary = self.get_status_summary()
        safe_print(f"\n[SUMMARY] Pipeline Status for {self.feature_name}")
        safe_print(f"  Status: {summary['status']}")
        safe_print(f"  Current Step: {summary['current_step']}")
        safe_print(f"  Completed: {summary['completed']}/{summary['total_steps']}")
        safe_print(f"  Failed: {summary['failed']}")
        safe_print(f"  Pending: {summary['pending']}")
        
        # Show step details
        for step_name, step in self.state.steps.items():
            emoji = {
                'completed': 'Γ£à',
                'failed': 'Γ¥î',
                'running': 'ΓÅ│',
                'paused': 'ΓÅ╕∩╕Å',
                'pending': 'ΓÅ¡∩╕Å',
                'skipped': 'ΓÅ¡∩╕Å'
            }.get(step.status, 'Γ¥ô')
            safe_print(f"  {emoji} {step_name}: {step.status}")


def run_command(command: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run shell command"""
    return subprocess.run(
        command.split(),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Delivery Pipeline - State-Managed Deployment')
    parser.add_argument('action', choices=['run', 'status', 'resume', 'pause', 'approve', 'reject', 'clear'], 
                       help='Pipeline action')
    parser.add_argument('--feature', required=True, help='Feature name')
    parser.add_argument('--mode', choices=['SERVICE', 'CONTAINER', 'AZURE'], default='AZURE',
                       help='Provision mode')
    parser.add_argument('--no-hitl', action='store_true', 
                       help='Disable human activity gates (fully automated)')
    parser.add_argument('--commit-sha', help='Git commit SHA for version tracking')
    parser.add_argument('--github-run-id', help='GitHub Actions run ID')
    
    args = parser.parse_args()
    
    feature_path = Path("features") / args.feature
    
    if args.action == 'status':
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode)
        pipeline.show_summary()
    
    elif args.action == 'resume':
        config = {'hitl_enabled': not args.no_hitl}
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode, config)
        if pipeline.resume():
            safe_print("[RUN] Resuming pipeline execution...")
            # TODO: Continue execution from current step
        else:
            sys.exit(1)
    
    elif args.action == 'approve':
        config = {'hitl_enabled': not args.no_hitl}
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode, config)
        if pipeline.state.human_activity_type != 'activity':
            safe_print("[ERROR] No human activity pending")
            sys.exit(1)
        safe_print(f"[APPROVED] Human approved step: {pipeline.state.current_step}")
        pipeline.resume()
        # TODO: Continue execution
    
    elif args.action == 'reject':
        config = {'hitl_enabled': not args.no_hitl}
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode, config)
        if pipeline.state.human_activity_type != 'activity':
            safe_print("[ERROR] No human activity pending")
            sys.exit(1)
        safe_print(f"[REJECTED] Human rejected step: {pipeline.state.current_step}")
        pipeline.finalize(False)
        sys.exit(1)
    
    elif args.action == 'pause':
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode)
        pipeline.pause("Manual pause requested")
    
    elif args.action == 'clear':
        state_mgr = PipelineStateManager(feature_path)
        if state_mgr.clear_state():
            safe_print(f"[SUCCESS] Cleared state for {args.feature}")
        else:
            safe_print(f"[ERROR] Failed to clear state")
            sys.exit(1)
    
    elif args.action == 'run':
        config = {'hitl_enabled': not args.no_hitl}
        if args.commit_sha:
            config['commit_sha'] = args.commit_sha
        if args.github_run_id:
            config['github_run_id'] = args.github_run_id
        
        pipeline = DeliveryPipeline(args.feature, feature_path, args.mode, config)
        
        # Store commit SHA and run ID in state
        if args.commit_sha:
            pipeline.state.commit_sha = args.commit_sha
        if args.github_run_id:
            pipeline.state.github_run_id = args.github_run_id
        pipeline.state_mgr.save_state(pipeline.state)
        
        safe_print(f"[RUN] Starting pipeline for {args.feature}")
        if args.no_hitl:
            safe_print("[INFO] HITL activity gates disabled (--no-hitl)")
        
        # Import provisioner
        sys.path.insert(0, str(Path(__file__).parent))
        from provisioner import Provisioner
        
        # Step 1: Structure check
        if pipeline.get_step_status('STRUCTURE_CHECK') != 'completed':
            def check_structure():
                safe_print("[STEP] Checking feature structure...")
                if (feature_path / "main.py").exists() and (feature_path / "service.py").exists():
                    return {'success': True}
                return {'success': False, 'error': 'Missing required files'}
            
            pipeline.execute_step('STRUCTURE_CHECK', check_structure)
        
        # Step 2: Provision
        if args.mode == 'AZURE':
            if pipeline.get_step_status('PROVISION_AZURE') != 'completed':
                def provision():
                    safe_print("[STEP] Provisioning to Azure...")
                    result = run_command(f"python {feature_path}/config/provision-service.py AZURE --always",
                                        cwd=Path(__file__).parent.parent)
                    if result.returncode == 0:
                        return {'success': True}
                    return {'success': False, 'error': result.stderr}
                
                pipeline.execute_step('PROVISION_AZURE', provision)
        
        # Finalize
        summary = pipeline.get_status_summary()
        if summary['failed'] == 0:
            pipeline.finalize(True)
            safe_print(f"[SUCCESS] Pipeline completed: {summary}")
        else:
            pipeline.finalize(False)
            safe_print(f"[FAILED] Pipeline failed: {summary}")
            sys.exit(1)


if __name__ == "__main__":
    main()

