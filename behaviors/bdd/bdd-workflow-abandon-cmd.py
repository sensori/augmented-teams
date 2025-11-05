"""
BDD Workflow - Abandon Run Command

Abandon a stuck or errored run to allow starting fresh.
"""

import sys
import io
import importlib.util
from pathlib import Path

# Import from hyphenated module name
spec = importlib.util.spec_from_file_location("bdd_workflow_run_state", Path(__file__).parent / "bdd-workflow-run-state.py")
bdd_workflow_run_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bdd_workflow_run_state)
BDDRunState = bdd_workflow_run_state.BDDRunState


def abandon_run(test_file: str, reason: str):
    """
    Abandon the current run.
    
    Args:
        test_file: Path to test file
        reason: Reason for abandoning
    """
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


if __name__ == "__main__":
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 3:
        print("Usage: python bdd-workflow-abandon-cmd.py <test-file> <reason>")
        print("\nExample:")
        print("  python bdd-workflow-abandon-cmd.py test.mjs 'Started wrong phase'")
        sys.exit(1)
    
    test_file = sys.argv[1]
    reason = sys.argv[2]
    
    success = abandon_run(test_file, reason)
    sys.exit(0 if success else 1)


