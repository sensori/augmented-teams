"""
Clean up duplicate scenario folders, keeping the full names.
"""

import shutil
from pathlib import Path

def cleanup_duplicates():
    """Remove duplicate scenario folders, keeping full names."""
    acceptance_dir = Path(__file__).parent
    scenarios_dir = acceptance_dir / "scenarios"
    
    # Map of short names to full names (keep full names)
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
    
    print("Cleaning up duplicate scenarios...")
    
    for short_name in duplicates_to_remove:
        short_path = scenarios_dir / short_name
        if short_path.exists():
            shutil.rmtree(short_path)
            print(f"  [REMOVED] {short_name}/")
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    cleanup_duplicates()




