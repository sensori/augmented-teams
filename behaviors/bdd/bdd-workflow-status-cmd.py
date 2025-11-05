"""
BDD Workflow - Status Command

Check current run status and what's needed to proceed.
"""

import sys
import io
from pathlib import Path
from bdd_workflow_run_state import BDDRunState


def show_status(test_file: str):
    """
    Show current workflow status.
    
    Args:
        test_file: Path to test file
    """
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


if __name__ == "__main__":
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python bdd-workflow-status-cmd.py <test-file>")
        print("\nExample:")
        print("  python bdd-workflow-status-cmd.py test.mjs")
        sys.exit(1)
    
    test_file = sys.argv[1]
    show_status(test_file)


