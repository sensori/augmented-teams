"""
Clean up duplicate output folders in scenario_tests to match cleaned scenario structure.
"""

import shutil
from pathlib import Path

def cleanup_output_duplicates():
    """Remove duplicate output folders, keeping only the full-named versions."""
    acceptance_dir = Path(__file__).parent
    outputs_dir = acceptance_dir / "outputs" / "scenario_tests"
    
    # Map of short names to remove (keep the full-named versions)
    duplicates_to_remove = [
        "different_story_types",  # Keep different_story_types_story_graph
        "incomplete_with_estimates",  # Keep incomplete_with_estimates_story_graph
        "multiple_users",  # Keep multiple_users_story_graph
        "optional_vs_sequential",  # Keep optional_vs_sequential_story_graph
        "simple",  # Keep simple_story_graph
        "single_epic",  # Keep single_epic_story_graph
        "with_acceptance_criteria",  # Keep with_acceptance_criteria_story_graph
        "with_increments",  # Keep with_increments_story_graph
    ]
    
    print("Cleaning up duplicate output folders...")
    
    if not outputs_dir.exists():
        print(f"  [SKIP] {outputs_dir} not found")
        return
    
    for short_name in duplicates_to_remove:
        short_path = outputs_dir / short_name
        if short_path.exists():
            try:
                shutil.rmtree(short_path)
                print(f"  [REMOVED] {short_name}/")
            except Exception as e:
                print(f"  [WARN] Could not remove {short_name}/: {e}")
    
    print("\nCleanup complete!")
    print(f"\nOutput folders now match scenario structure in: {acceptance_dir / 'scenarios'}")

if __name__ == "__main__":
    cleanup_output_duplicates()




