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
    AI_HUMAN = 'ai_human'  # AI generates content, then human reviews/approves

@dataclass
class StepState:
    """State of a single step"""
    name: str
    status: str  # 'pending', 'completed'

@dataclass
class PipelineState:
    """Current state of the TDD pipeline"""
    feature_name: str
    pipeline_id: str
    current_step: Optional[str] = None
    status: str = 'pending'  # 'pending', 'completed'
    started_at: str = ""
    last_updated: str = ""
    steps: Dict[str, StepState] = field(default_factory=dict)
    
    def get_current_step_display(self) -> str:
        """Get human-readable current step"""
        return self.current_step or "No step active"
    
    def get_status_display(self) -> str:
        """Get human-readable status"""
        return self.status or "Unknown"
    
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
            steps=steps
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
    
    # Phases and Steps structure - Simple TDD workflow
    PHASES = [
        {
            'name': 'Develop',
            'steps': [
                {'name': 'START_FEATURE', 'type': StepType.AUTOMATED},  # Creates folder, no AI
                {'name': 'CREATE_STRUCTURE', 'type': StepType.AI_HUMAN},  # Code + AI + Human
                {'name': 'BUILD_SCAFFOLDING', 'type': StepType.AI_HUMAN},  # Code + AI + Human
                {'name': 'DEVELOP_TEST', 'type': StepType.AI_HUMAN},  # Code + AI + Human
                {'name': 'WRITE_CODE', 'type': StepType.AI_HUMAN},  # Code + AI + Human
                {'name': 'REFACTOR', 'type': StepType.AI_HUMAN}  # Code + AI + Human
            ]
        }
    ]
    
    def __init__(self, feature_name: str, feature_path: Path):
        self.feature_name = feature_name
        self.feature_path = Path(feature_path)
        self.state_mgr = PipelineStateManager(self.feature_path)
        
        # Load existing state or create new
        self.state = self.state_mgr.load_state()
        if self.state is None:
            pipeline_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.state = PipelineState(
                feature_name=feature_name,
                pipeline_id=pipeline_id,
                started_at=datetime.now().isoformat(),
                status='started'
            )
            # Initialize all steps from PHASES
            for phase in self.PHASES:
                for step_def in phase['steps']:
                    self.state.steps[step_def['name']] = StepState(
                        name=step_def['name'],
                        status='pending'
                    )
    
    def get_step_status(self, step_name: str) -> Optional[str]:
        """Get status of a specific step"""
        if step_name in self.state.steps:
            return self.state.steps[step_name].status
        return None
    
    def mark_step_started(self, step_name: str):
        """Mark a step as started"""
        if step_name not in self.state.steps:
            self.state.steps[step_name] = StepState(name=step_name, status='started')
        else:
            step = self.state.steps[step_name]
            step.status = 'started'
        self.state.current_step = step_name
        self.state.status = 'started'
        self.state_mgr.save_state(self.state)
    
    def mark_step_completed(self, step_name: str, outputs: Optional[Dict] = None):
        """Mark a step as completed"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'completed'
        self.state_mgr.save_state(self.state)
    
    def mark_step_failed(self, step_name: str, error: str):
        """Mark a step as failed"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'failed'
        self.state.status = 'failed'
        self.state_mgr.save_state(self.state)
    
    def mark_step_skipped(self, step_name: str):
        """Mark a step as skipped"""
        if step_name in self.state.steps:
            step = self.state.steps[step_name]
            step.status = 'skipped'
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
        
        self.state.status = 'started'
        self.state_mgr.save_state(self.state)
        safe_print(f"[RESUME] Resuming from step: {self.state.current_step}")
        return True
    
    def get_current_step(self) -> Optional[str]:
        """Get the current step name"""
        return self.state.current_step
    
    def skip_to_phase(self, phase_name: str):
        """Jump to a specific phase and set current step to first step in that phase"""
        skipped_steps = []
        
        for phase in self.PHASES:
            if phase['name'] == phase_name:
                if phase['steps']:
                    first_step_name = phase['steps'][0]['name']
                    return self._skip_to_step_internal(first_step_name, skipped_steps)
        return None
    
    def skip_to_step(self, step_name: str):
        """Jump to a specific step by name"""
        skipped_steps = []
        # Verify the step exists
        for phase in self.PHASES:
            for step_def in phase['steps']:
                if step_def['name'] == step_name:
                    return self._skip_to_step_internal(step_name, skipped_steps)
        return None
    
    def _skip_to_step_internal(self, target_step_name: str, skipped_steps: list):
        """Internal helper to skip to a step and mark previous steps as skipped"""
        target_reached = False
        
        # Mark all steps before the target as skipped
        for phase in self.PHASES:
            for step_def in phase['steps']:
                step_name = step_def['name']
                if step_name == target_step_name:
                    target_reached = True
                    break
                
                # Mark as skipped if not already completed
                if step_name in self.state.steps:
                    step_state = self.state.steps[step_name]
                    if step_state.status not in ['completed', 'failed']:
                        self.mark_step_skipped(step_name)
                        skipped_steps.append({
                            'name': step_name,
                            'type': step_def['type'],
                            'phase': phase['name']
                        })
            
            if target_reached:
                break
        
        if not target_reached:
            return None
        
        # Find the step definition and phase
        target_step_def = None
        target_phase = None
        for phase in self.PHASES:
            for step_def in phase['steps']:
                if step_def['name'] == target_step_name:
                    target_step_def = step_def
                    target_phase = phase['name']
                    break
            if target_step_def:
                break
        
        if not target_step_def:
            return None
        
        # Ensure step is marked as started (status='started') when it becomes current
        self.mark_step_started(target_step_name)
        
        step_obj = create_step(self, target_step_def, target_phase)
        # Store skipped steps info on the step object so execute() can include it
        step_obj._skipped_steps = skipped_steps
        
        return step_obj
    
    def get_next_step(self):
        """Get the next pending step to execute as a Step object"""
        for phase in self.PHASES:
            for step_def in phase['steps']:
                step_name = step_def['name']
                step_state = self.state.steps.get(step_name)
                
                # Skip if this is the current step (unless it's completed)
                if step_name == self.state.current_step:
                    if step_state and step_state.status == 'completed':
                        continue  # Move to next step after completed current step
                    else:
                        return None  # Current step is still active, not ready for next
                
                # Return first pending step
                if not step_state or step_state.status == 'pending':
                    return create_step(self, step_def, phase['name'])
        return None
    
    def complete_current_step(self):
        """Complete the current step if it exists and is started/pending"""
        current_step_name = self.state.current_step
        if current_step_name and current_step_name in self.state.steps:
            current_step_state = self.state.steps[current_step_name]
            if current_step_state.status in ['started', 'pending']:
                self.mark_step_completed(current_step_name)
    
    def start_next_step(self):
        """Complete current step (if any) and start the next step"""
        # Complete current step first
        self.complete_current_step()
        
        # Get and start the next step
        next_step = self.get_next_step()
        if not next_step:
            return None
        
        # Mark next step as started and execute it
        self.mark_step_started(next_step.name)
        result = next_step.execute()
        
        return {
            'step': next_step,
            'result': result
        }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        completed = sum(1 for s in self.state.steps.values() if s.status == 'completed')
        pending = sum(1 for s in self.state.steps.values() if s.status == 'pending')
        
        return {
            'status': self.state.status,
            'current_step': self.state.current_step,
            'total_steps': len(self.state.steps),
            'completed': completed,
            'pending': pending
        }
    

class Step:
    """Base class for all pipeline steps"""
    
    def __init__(self, pipeline: DeliveryPipeline, name: str, phase: str, step_type: str, step_def: Dict):
        self.pipeline = pipeline
        self.name = name
        self.phase = phase
        self.type = step_type
        self.definition = step_def
        self.reason = step_def.get('reason', None)
    
    def execute(self) -> Dict[str, Any]:
        """Template method - sets current step and calls step-specific logic"""
        # Ensure step is marked as started (status='started') when it becomes current
        self.pipeline.mark_step_started(self.name)
        
        result = self._execute()
        
        # Include skipped steps info if this step was reached via skip_to_phase
        if hasattr(self, '_skipped_steps') and self._skipped_steps:
            result['skipped_steps'] = self._skipped_steps
        
        # Auto-complete automated steps
        if self.type == StepType.AUTOMATED:
            if self.name in self.pipeline.state.steps:
                self.pipeline.state.steps[self.name].status = 'completed'
            self.pipeline.state_mgr.save_state(self.pipeline.state)
        
        return result
    
    def _execute(self) -> Dict[str, Any]:
        """Override in subclasses - step-specific execution logic"""
        raise NotImplementedError("Subclasses must implement _execute()")


class AutoStep(Step):
    """Automated step - just runs code, no AI or human needed"""
    
    def _execute(self) -> Dict[str, Any]:
        """Execute automated code"""
        return {
            'success': True,
            'outputs': {'step': self.name, 'phase': self.phase}
        }


class StartStep(AutoStep):
    """Start feature step - creates folder"""
    
    def _execute(self) -> Dict[str, Any]:
        """Create feature folder"""
        # Resolve path to absolute to ensure it works regardless of working directory
        abs_path = self.pipeline.feature_path.resolve()
        abs_path.mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'outputs': {
                'step': self.name,
                'phase': self.phase,
                'folder_created': str(abs_path)
            }
        }


class AiHumanStep(Step):
    """AI + Human step - code runs, then AI, then human reviews"""
    
    def execute(self) -> Dict[str, Any]:
        """Template method for AI+Human workflow"""
        # Ensure step is marked as started (status='started') when it becomes current
        self.pipeline.mark_step_started(self.name)
        
        # Run pre-code logic
        self.preprocess_code()
        
        # Run AI generation
        ai_result = self.preprocess_ai()
        
        # Hand off to human (don't mark completed yet)
        result = {
            'success': True,
            'requires_ai': True,
            'requires_human': True,
            'step': self.name,
            'phase': self.phase,
            'ai_result': ai_result
        }
        
        # Include skipped steps info if this step was reached via skip_to_phase
        if hasattr(self, '_skipped_steps') and self._skipped_steps:
            result['skipped_steps'] = self._skipped_steps
        
        return result
    
    def preprocess_code(self) -> None:
        """Override to run code before AI - default no-op"""
        pass
    
    def preprocess_ai(self) -> Dict[str, Any]:
        """Override to run AI generation - default placeholder"""
        return {'status': 'ai_action_required'}
    
    def preprocess_human(self) -> Dict[str, Any]:
        """Override for human review/approval logic"""
        return {'status': 'human_review_required'}


# Helper function to create appropriate step class instance
def create_step(pipeline: DeliveryPipeline, step_def: Dict, phase_name: str) -> Step:
    """Create appropriate step class instance based on step definition"""
    step_name = step_def['name']
    step_type = step_def['type']
    
    if step_name == 'START_FEATURE':
        return StartStep(pipeline, step_name, phase_name, step_type, step_def)
    elif step_type == StepType.AI_HUMAN:
        return AiHumanStep(pipeline, step_name, phase_name, step_type, step_def)
    elif step_type == StepType.AUTOMATED:
        return AutoStep(pipeline, step_name, phase_name, step_type, step_def)
    else:
        return Step(pipeline, step_name, phase_name, step_type, step_def)


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

