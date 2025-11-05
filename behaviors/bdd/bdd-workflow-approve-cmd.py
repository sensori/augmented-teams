"""
BDD Workflow - Approve Run Command

Human approval of AI work after validation.
"""

import sys
import io
from pathlib import Path
from bdd_workflow_run_state import BDDRunState


def approve_run(test_file: str, feedback: str = None):
    """
    Approve the current run after reviewing AI work.
    
    Args:
        test_file: Path to test file
        feedback: Optional human feedback
    """
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


def reject_run(test_file: str, feedback: str):
    """
    Reject the current run and send back to AI for fixes.
    
    Args:
        test_file: Path to test file
        feedback: Required feedback explaining what to fix
    """
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


if __name__ == "__main__":
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python bdd-workflow-approve-cmd.py <test-file> [feedback]")
        print("  python bdd-workflow-approve-cmd.py <test-file> --reject 'reason'")
        print("\nExamples:")
        print("  python bdd-workflow-approve-cmd.py test.mjs")
        print("  python bdd-workflow-approve-cmd.py test.mjs 'Good work'")
        print("  python bdd-workflow-approve-cmd.py test.mjs --reject 'Fix naming'")
        sys.exit(1)
    
    test_file = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == '--reject':
        if len(sys.argv) < 4:
            print("❌ Rejection requires feedback")
            sys.exit(1)
        feedback = sys.argv[3]
        success = reject_run(test_file, feedback)
    else:
        feedback = sys.argv[2] if len(sys.argv) > 2 else None
        success = approve_run(test_file, feedback)
    
    sys.exit(0 if success else 1)


