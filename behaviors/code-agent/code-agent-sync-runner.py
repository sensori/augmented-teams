def restart_watchers_if_needed(synced_python_files):
    """
    Check all watcher processes and ensure they're running.
    
    Checks ALL command-runners/*.py files for watch functionality:
    - Restart watchers that are already running (to pick up code changes)
    - Start watchers that are not running
    
    Uses PID files to track running watchers and manages them safely.
    """
    import subprocess
    import sys
    from pathlib import Path
    import os
    import re
    
    # Check which Python files in command-runners/ have watch functions
    commands_dir = Path("commands")
    if not commands_dir.exists():
        return
    
    # Find all watcher commands (files with watch functions)
    all_watchers = []
    for cmd_file in commands_dir.glob("*.py"):
        try:
            content = cmd_file.read_text(encoding='utf-8', errors='ignore')
            # Check if file has a watch function (looks for "*_watch()" pattern)
            if re.search(r'def\s+\w+_watch\s*\(', content):
                all_watchers.append(cmd_file)
        except Exception:
            continue
    
    if not all_watchers:
        return
    
    # Track which watchers were synced (to prioritize restart)
    synced_watcher_paths = {Path(dest).resolve() for src, dest in synced_python_files}
    
    print("\n" + "="*60)
    print("Managing Watchers")
    print("="*60)
    
    # Use PID file approach for tracking watchers
    pid_dir = Path(".cursor/watchers")
    pid_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to use psutil for better process management (optional)
    try:
        import psutil
        HAS_PSUTIL = True
    except ImportError:
        HAS_PSUTIL = False
    
    for cmd_file in all_watchers:
        is_synced = cmd_file.resolve() in synced_watcher_paths
        try:
            cmd_path = str(cmd_file.resolve())
            pid_file = pid_dir / f"{cmd_file.stem}.pid"
            
            # Check if watcher is already running
            is_running = False
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text().strip())
                    if HAS_PSUTIL:
                        try:
                            proc = psutil.Process(pid)
                            if proc.is_running():
                                cmdline = ' '.join(proc.cmdline())
                                if 'watch' in cmdline.lower() and cmd_path in cmdline:
                                    is_running = True
                                else:
                                    # PID doesn't match our watcher, remove stale PID file
                                    pid_file.unlink()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # Process doesn't exist, remove stale PID file
                            pid_file.unlink()
                    else:
                        # Fallback: check if process exists on Windows/Unix
                        if sys.platform == "win32":
                            try:
                                result = subprocess.run(
                                    ['tasklist', '/FI', f'PID eq {pid}'],
                                    capture_output=True,
                                    text=True,
                                    timeout=2
                                )
                                if str(pid) in result.stdout:
                                    is_running = True
                                else:
                                    pid_file.unlink()  # Stale PID
                            except Exception:
                                pid_file.unlink()  # Can't check, assume stale
                        else:
                            try:
                                os.kill(pid, 0)  # Check if process exists (signal 0 doesn't kill)
                                is_running = True
                            except ProcessLookupError:
                                pid_file.unlink()  # Process doesn't exist
                            except PermissionError:
                                # Can't check, but assume might be running
                                is_running = True
                except (ValueError, FileNotFoundError):
                    pid_file.unlink()
            
            # Stop existing watcher if running (always restart to pick up any changes)
            if is_running:
                try:
                    pid = int(pid_file.read_text().strip())
                    if HAS_PSUTIL:
                        try:
                            proc = psutil.Process(pid)
                            proc.terminate()
                            proc.wait(timeout=5)
                            print(f"🛑 Stopped: {cmd_file.name} (PID: {pid})")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    else:
                        if sys.platform == "win32":
                            try:
                                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                             capture_output=True, timeout=3)
                                print(f"🛑 Stopped: {cmd_file.name} (PID: {pid})")
                            except Exception:
                                pass
                        else:
                            try:
                                os.kill(pid, 15)  # SIGTERM
                                print(f"🛑 Stopped: {cmd_file.name} (PID: {pid})")
                            except (ProcessLookupError, PermissionError):
                                pass
                except (ValueError, FileNotFoundError):
                    pass
                pid_file.unlink()
            
            # Start the watcher (or restart if it was running)
            try:
                # Watchers write to stderr directly (they handle their own stderr setup)
                # Don't redirect - let them use their own sys.stderr
                proc = subprocess.Popen(
                    [sys.executable, cmd_path, "watch"],
                    stdout=None,  # Let it use default stdout
                    stderr=None,  # Let it use default stderr (watchers configure their own)
                    cwd=Path.cwd(),
                    bufsize=1,  # Line buffered
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                )
                pid_file.write_text(str(proc.pid))
                action = "Restarted" if is_running else "Started"
                print(f"▶️  {action}: {cmd_file.name} (watch mode, PID: {proc.pid})")
            except Exception as e:
                print(f"❌ Error starting {cmd_file.name}: {e}")
                
        except Exception as e:
            print(f"⚠️  Error handling watcher {cmd_file.name}: {e}")


def behavior_sync(feature=None, force=False):
    """
    Sync feature-local AI behaviors from behaviors/*/code-agent-behaviors/ folders.
    
    Sync Rules:
    1. All files in behaviors/*/code-agent-behaviors/ folders are synced
    2. Files are routed to .cursor/ correct areas based on extension:
       - .mdc files → .cursor/rules/
       - .md files  → .cursor/commands/
       - .py files  → command-runners/ (root level, NOT .cursor/)
       - .json files → .cursor/mcp/
    3. Merge MCP configs (*-mcp.json) if they already exist
    4. Overwrite only if the source is newer (unless force=True)
    5. Log synced and merged files
    6. Never sync behaviors marked as "draft" or "experimental"
    
    Args:
        feature: Optional feature name to sync only that feature
        force: If True, overwrite all files regardless of timestamps
    """
    from pathlib import Path
    import shutil
    import json

    src_root = Path("behaviors")
    # File extension to target directory mapping
    # NOTE: .py files are NOT synced - they stay in behaviors/<feature>/
    targets = {
        ".mdc": Path(".cursor/rules"),         # Rules → .cursor/rules/
        ".md": Path(".cursor/commands"),       # Commands → .cursor/commands/
        ".json": Path(".cursor/mcp"),          # MCP configs → .cursor/mcp/
    }
    # .py files intentionally excluded - they remain in behaviors/<feature>/

    # Create target directories
    for t in targets.values():
        t.mkdir(parents=True, exist_ok=True)
    
    # Ensure .vscode directory exists for tasks.json merging
    Path(".vscode").mkdir(parents=True, exist_ok=True)

    # Determine features to sync (features with behavior.json and deployed: true)
    features = []
    if feature:
        feature_path = src_root / feature
        marker_file = feature_path / "behavior.json"
        
        if marker_file.exists():
            try:
                marker_data = json.load(marker_file.open('r', encoding='utf-8'))
                if marker_data.get("deployed"):
                    features = [feature_path]
            except:
                pass
    else:
        for feature_dir in src_root.glob("*"):
            if not feature_dir.is_dir():
                continue
            
            marker_file = feature_dir / "behavior.json"
            
            if marker_file.exists():
                try:
                    marker_data = json.load(marker_file.open('r', encoding='utf-8'))
                    if marker_data.get("deployed"):
                        features.append(feature_dir)
                except:
                    pass

    synced_files = []
    merged_files = []
    skipped_files = []
    
    # Collect tasks.json files from features for merging
    feature_tasks_files = []

    for feature_path in features:
        print(f"\nProcessing feature: {feature_path.name}")
        for file in feature_path.rglob("*"):
            # Skip directories
            if file.is_dir():
                continue
            
            # Skip files in docs/ directories (those are documentation, not commands)
            if 'docs' in file.parts:
                continue
            
            # Skip draft or experimental behaviors
            content = file.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            # Check for draft/experimental markers at start of file or start of lines
            # This avoids false positives from code that checks for these markers
            lines = content_lower.split('\n')
            has_draft_marker = False
            for line in lines[:10]:  # Check first 10 lines for markers
                stripped = line.strip()
                if stripped.startswith('#draft') or stripped.startswith('#experimental'):
                    has_draft_marker = True
                    break
                if stripped.startswith('draft:') or stripped.startswith('experimental:'):
                    has_draft_marker = True
                    break
            
            if has_draft_marker:
                skipped_files.append((file, "draft/experimental marker"))
                continue

            ext = file.suffix
            if ext not in targets:
                continue

            dest = targets[ext] / file.name
            
            # Handle MCP JSON configs - merge if exists (always merge, regardless of timestamp)
            if ext == ".json" and dest.exists() and file.name.endswith("-mcp.json"):
                try:
                    with open(dest, 'r', encoding='utf-8') as d1, open(file, 'r', encoding='utf-8') as d2:
                        existing = json.load(d1)
                        new_data = json.load(d2)
                        merged = {**existing, **new_data}
                    with open(dest, 'w', encoding='utf-8') as out:
                        json.dump(merged, out, indent=2, ensure_ascii=False)
                    merged_files.append((file, dest))
                    print(f"🔄 Merged {file.name} → {dest}")
                except (json.JSONDecodeError, Exception) as e:
                    print(f"⚠️  Error merging {file.name}: {e}")
                    skipped_files.append((file, f"merge error: {e}"))
            else:
                # For non-MCP files, check if source is newer (only overwrite if newer, unless force mode)
                if dest.exists() and not force:
                    source_mtime = file.stat().st_mtime
                    dest_mtime = dest.stat().st_mtime
                    if source_mtime <= dest_mtime:
                        skipped_files.append((file, "source not newer"))
                        continue
                
                # Copy file
                try:
                    shutil.copy2(file, dest)
                    synced_files.append((file, dest))
                    print(f"✅ Synced {file.name} → {dest}")
                except Exception as e:
                    print(f"❌ Error syncing {file.name}: {e}")
                    skipped_files.append((file, f"copy error: {e}"))
    
    # Merge tasks.json files from all features into root .vscode/tasks.json
    if feature_tasks_files:
        root_tasks = Path(".vscode/tasks.json")
        all_tasks = []
        existing_tasks_by_label = {}
        
        # Load existing root tasks.json if it exists
        if root_tasks.exists():
            try:
                with open(root_tasks, 'r', encoding='utf-8') as f:
                    root_data = json.load(f)
                    all_tasks = root_data.get("tasks", [])
                    # Index existing tasks by label to avoid duplicates
                    existing_tasks_by_label = {task.get("label"): task for task in all_tasks}
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Error reading existing tasks.json: {e}")
                all_tasks = []
        
        # Merge tasks from feature tasks.json files
        for feature_tasks_file in feature_tasks_files:
            try:
                with open(feature_tasks_file, 'r', encoding='utf-8') as f:
                    feature_data = json.load(f)
                    feature_tasks = feature_data.get("tasks", [])
                    
                    for task in feature_tasks:
                        task_label = task.get("label", "")
                        # Only add if label doesn't already exist (avoid duplicates)
                        if task_label and task_label not in existing_tasks_by_label:
                            all_tasks.append(task)
                            existing_tasks_by_label[task_label] = task
                            print(f"✅ Merged task: {task_label} from {feature_tasks_file.parent.parent.name}")
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Error reading {feature_tasks_file}: {e}")
        
        # Write merged tasks.json
        if all_tasks:
            merged_tasks_data = {
                "version": "2.0.0",
                "tasks": all_tasks
            }
            try:
                with open(root_tasks, 'w', encoding='utf-8') as f:
                    json.dump(merged_tasks_data, f, indent=4, ensure_ascii=False)
                merged_files.append((Path("behaviors/*/tasks.json"), root_tasks))
                print(f"🔄 Merged tasks.json → {root_tasks}")
            except Exception as e:
                print(f"❌ Error writing merged tasks.json: {e}")

    # Report results
    print("\n" + "="*60)
    print("Behavior Sync Report")
    print("="*60)
    print(f"✅ Synced: {len(synced_files)} files")
    print(f"🔄 Merged: {len(merged_files)} files")
    print(f"⏭️  Skipped: {len(skipped_files)} files")
    
    if synced_files:
        print("\nSynced files:")
        for src, dest in synced_files:
            print(f"  {src.relative_to(src_root)} → {dest}")
    
    if merged_files:
        print("\nMerged files:")
        for src, dest in merged_files:
            print(f"  {src.relative_to(src_root)} → {dest}")
    
    if skipped_files:
        print("\nSkipped files:")
        for src, reason in skipped_files:
            print(f"  {src.relative_to(src_root)} ({reason})")
    
    # Check all watchers and ensure they're running (restart running ones, start stopped ones)
    synced_python_files = [(src, dest) for src, dest in synced_files if Path(dest).suffix == '.py' and Path(dest).parent.name == 'commands']
    restart_watchers_if_needed(synced_python_files)
    
    return {
        "synced": len(synced_files),
        "merged": len(merged_files),
        "skipped": len(skipped_files)
    }


def behavior_sync_watch():
    """Watch for file changes and automatically sync behaviors.
    
    Output goes to stderr to be visible in chat (like MCP servers).
    """
    import sys
    import io
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("❌ watchdog package not installed.", file=sys.stderr)
        print("   Install with: pip install watchdog", file=sys.stderr)
        return
    
    from pathlib import Path
    import time
    import threading
    
    class BehaviorSyncHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_change = 0
            self.debounce_time = 2  # Wait 2 seconds after last change
            self.timer = None
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            src_path = Path(event.src_path)
            # Only watch .mdc, .md, .py, .json files in cursor directories
            if src_path.suffix not in [".mdc", ".md", ".py", ".json"]:
                return
            
            if "cursor" not in str(src_path):
                return
            
            # Check for draft markers (skip if draft)
            try:
                content = src_path.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                lines = content_lower.split('\n')
                has_draft_marker = False
                for line in lines[:10]:
                    stripped = line.strip()
                    if stripped.startswith('#draft') or stripped.startswith('#experimental'):
                        has_draft_marker = True
                        break
                    if stripped.startswith('draft:') or stripped.startswith('experimental:'):
                        has_draft_marker = True
                        break
                
                if has_draft_marker:
                    return
            except Exception:
                pass
            
            self.last_change = time.time()
            
            # Cancel existing timer
            if self.timer:
                self.timer.cancel()
            
            # Set new timer to run sync after debounce
            self.timer = threading.Timer(self.debounce_time, self.run_sync)
            self.timer.start()
        
        def run_sync(self):
            if time.time() - self.last_change < self.debounce_time:
                return
            
            print("\n🔄 Behavior file changed, syncing...", file=sys.stderr)
            sys.stderr.flush()
            behavior_sync(None)
            print("✅ Sync complete. Watching for changes...", file=sys.stderr)
            sys.stderr.flush()
    
    # Watch all directories with behavior.json where deployed=true
    import importlib.util
    
    # Import module with hyphens using importlib
    common_path = Path(__file__).parent / "code-agent-common.py"
    spec = importlib.util.spec_from_file_location("code_agent_common", common_path)
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    
    watch_dirs = common.find_deployed_behaviors()
    
    if not watch_dirs:
        print("❌ No behaviors with deployed=true found in behaviors/", file=sys.stderr)
        return
    
    event_handler = BehaviorSyncHandler()
    observer = Observer()
    
    for watch_dir in watch_dirs:
        observer.schedule(event_handler, str(watch_dir), recursive=True)
        print(f"👀 Watching: {watch_dir}", file=sys.stderr)
    
    observer.start()
    print("\n✅ Behavior sync watch mode active. Press Ctrl+C to stop.", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Watch mode stopped.", file=sys.stderr)
        sys.stderr.flush()
    
    observer.join()


if __name__ == "__main__":
    import sys
    import io
    
    # Fix Windows console encoding for emoji support
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Check if watch mode requested
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        behavior_sync_watch()
    else:
        # Parse arguments
        force = "--force" in sys.argv or "-f" in sys.argv
        feature = None
        for arg in sys.argv[1:]:
            if arg not in ["--force", "-f"]:
                feature = arg
                break
        
        behavior_sync(feature, force=force)