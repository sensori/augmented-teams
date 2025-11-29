"""
Remove old input and output files after migration to scenario-based format.
"""

import shutil
from pathlib import Path

def remove_old_files():
    """Remove old input and output directories."""
    acceptance_dir = Path(__file__).parent
    old_input_dir = acceptance_dir / "input"
    old_outputs_dir = acceptance_dir / "outputs"
    
    print("Removing old files...")
    
    # Remove old input directory (remove files first, then directory)
    if old_input_dir.exists():
        print(f"  Removing: {old_input_dir}")
        try:
            # Remove all files first
            for item in old_input_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    print(f"    [REMOVED] {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"    [REMOVED] {item.name}/")
            # Then remove the directory
            old_input_dir.rmdir()
            print(f"  [OK] Removed input/ directory")
        except PermissionError as e:
            print(f"  [WARN] Could not remove input/ directory: {e}")
            print(f"  [INFO] You may need to close any files open in this directory")
        except Exception as e:
            print(f"  [ERROR] Error removing input/ directory: {e}")
    else:
        print(f"  [SKIP] input/ directory not found")
    
    # Remove old outputs directory (but keep scenario_tests subdirectory)
    if old_outputs_dir.exists():
        # List what's in outputs
        items = list(old_outputs_dir.iterdir())
        print(f"\n  Found {len(items)} items in outputs/")
        
        # Keep scenario_tests directory
        scenario_tests_dir = old_outputs_dir / "scenario_tests"
        if scenario_tests_dir.exists():
            print(f"  [KEEP] Keeping scenario_tests/ directory")
        
        # Remove everything except scenario_tests
        for item in items:
            if item.name == "scenario_tests":
                continue
            try:
                if item.is_file():
                    item.unlink()
                    print(f"  [REMOVED] {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"  [REMOVED] {item.name}/")
            except PermissionError as e:
                print(f"  [WARN] Could not remove {item.name}: {e}")
            except Exception as e:
                print(f"  [WARN] Error removing {item.name}: {e}")
        
        print(f"\n  [OK] Cleaned outputs/ directory (kept scenario_tests/)")
    else:
        print(f"  [SKIP] outputs/ directory not found")
    
    print("\nCleanup complete!")
    print("\nAll test files are now in the scenario-based format:")
    print(f"  {acceptance_dir / 'scenarios'}/")

if __name__ == "__main__":
    remove_old_files()

