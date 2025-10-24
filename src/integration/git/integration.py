
#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import datetime

# Locate repository root (assumes this file is in src/integration/git/)
REPO_PATH = Path(__file__).resolve().parents[3]  # repo root
REMOTE_NAME = "origin"
BRANCH = "main"
DEFAULT_COMMIT_MSG = "update: synced changes from GPT session at {timestamp}"

def run_cmd(cmd, cwd=REPO_PATH):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(result.stderr)
        raise Exception("Git command failed")
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def ensure_latest():
    print("Fetching latest changes...")
    run_cmd(["git", "fetch", REMOTE_NAME])[0]
    run_cmd(["git", "checkout", BRANCH])[0]
    run_cmd(["git", "pull", REMOTE_NAME, BRANCH])[0]
    print("Repository is up to date.")

def save_code(content: str, filename: str, subdir: str="src/misc"):
    dest_folder = REPO_PATH / subdir
    dest_folder.mkdir(parents=True, exist_ok=True)
    file_path = dest_folder / filename
    with open(file_path, "w") as f:
        f.write(content)
    print(f" Saved generated file to {file_path}")
    return file_path

def commit_and_push(commit_msg: str=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (commit_msg or DEFAULT_COMMIT_MSG).format(timestamp=timestamp)
    print("Committing and pushing changes...")
    
    # Copy workflow files to .github/workflows/ before committing
    copy_workflow_files()
    
    run_cmd(["git", "add", "."])[0]
    try:
        run_cmd(["git", "commit", "-m", msg])[0]
    except Exception:
        print("No changes to commit.")
        return
    run_cmd(["git", "push", REMOTE_NAME, BRANCH])[0]
    print(f"[OK] Changes pushed successfully: {msg}")

def copy_workflow_files():
    """Copy workflow files from feature folders to .github/workflows/"""
    try:
        workflows_dir = REPO_PATH / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy auto-commit.yml from git integration
        auto_commit_source = REPO_PATH / "src" / "integration" / "git" / "auto-commit.yml"
        auto_commit_dest = workflows_dir / "auto-commit.yml"
        if auto_commit_source.exists():
            import shutil
            shutil.copy2(auto_commit_source, auto_commit_dest)
            print(f"[OK] Copied auto-commit.yml to .github/workflows/")
        
        # Copy update_gpt_instructions.yml from update_gpt_instructions_from_git feature
        gpt_sync_source = REPO_PATH / "src" / "features" / "update_gpt_instructions_from_git" / "update_gpt_instructions.yml"
        gpt_sync_dest = workflows_dir / "update_gpt_instructions.yml"
        if gpt_sync_source.exists():
            import shutil
            shutil.copy2(gpt_sync_source, gpt_sync_dest)
            print(f"[OK] Copied update_gpt_instructions.yml to .github/workflows/")
            
    except Exception as e:
        print(f"[WARNING] Could not copy workflow files: {e}")

def get_repository_tree(path: str = "."):
    """
    Get the entire repository tree structure
    
    Args:
        path: Path to get tree for (default: root)
        
    Returns:
        List of files and directories with their status
    """
    try:
        stdout, stderr, returncode = run_cmd(["git", "ls-tree", "-r", "--name-only", "HEAD"])
        if returncode != 0:
            raise Exception(f"Failed to get tree: {stderr}")
        
        files = stdout.split('\n') if stdout else []
        return {
            "path": path,
            "files": [f for f in files if f.strip()],
            "total_files": len([f for f in files if f.strip()])
        }
    except Exception as e:
        print(f"❌ Failed to get repository tree: {e}")
        raise

def get_folder_content(folder_path: str):
    """
    Get all content in a specific folder
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        List of files in the folder with their details
    """
    try:
        folder_path = folder_path.rstrip('/')
        stdout, stderr, returncode = run_cmd(["git", "ls-tree", "-r", "--name-only", "HEAD"])
        if returncode != 0:
            raise Exception(f"Failed to get folder content: {stderr}")
        
        files = stdout.split('\n') if stdout else []
        folder_files = [f for f in files if f.startswith(folder_path + '/') and f.strip()]
        
        # Get file details
        file_details = []
        for file_path in folder_files:
            stdout, stderr, returncode = run_cmd(["git", "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--", file_path])
            if returncode == 0 and stdout:
                commit_hash, author, date, message = stdout.split('|', 3)
                file_details.append({
                    "file_path": file_path,
                    "last_commit": commit_hash,
                    "author": author,
                    "date": date,
                    "message": message
                })
            else:
                file_details.append({
                    "file_path": file_path,
                    "last_commit": None,
                    "author": None,
                    "date": None,
                    "message": None
                })
        
        return {
            "folder_path": folder_path,
            "files": file_details,
            "total_files": len(file_details)
        }
    except Exception as e:
        print(f" Failed to get folder content: {e}")
        raise

def search_git_content(query: str, file_pattern: str = "*"):
    """
    Search Git repository for files containing specific content using native git functionality
    
    Args:
        query: Text to search for
        file_pattern: File pattern to search in (e.g., "*.md", "*.py")
        
    Returns:
        List of files containing the query with context
    """
    try:
        # Use git grep for fast searching
        stdout, stderr, returncode = run_cmd(["git", "grep", "-n", "-i", query, "--", file_pattern])
        
        results = []
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_path, line_num, content = parts[0], parts[1], parts[2]
                        results.append({
                            "file_path": file_path,
                            "line_number": int(line_num),
                            "content": content.strip(),
                            "query": query
                        })
        
        return {
            "query": query,
            "file_pattern": file_pattern,
            "results": results,
            "total_matches": len(results)
        }
    except Exception as e:
        print(f" Failed to search git content: {e}")
        raise

def search_git_files(filename_pattern: str):
    """
    Search for files by name pattern using git ls-files
    
    Args:
        filename_pattern: Pattern to match filenames (supports wildcards)
        
    Returns:
        List of matching files
    """
    try:
        stdout, stderr, returncode = run_cmd(["git", "ls-files", filename_pattern])
        if returncode != 0:
            raise Exception(f"Failed to search files: {stderr}")
        
        files = stdout.split('\n') if stdout else []
        return {
            "pattern": filename_pattern,
            "files": [f for f in files if f.strip()],
            "total_files": len([f for f in files if f.strip()])
        }
    except Exception as e:
        print(f"❌ Failed to search git files: {e}")
        raise

def get_file_content(file_path: str):
    """
    Get the content of a specific file from git
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content and metadata
    """
    try:
        stdout, stderr, returncode = run_cmd(["git", "show", f"HEAD:{file_path}"])
        if returncode != 0:
            raise Exception(f"Failed to get file content: {stderr}")
        
        # Get file metadata
        stdout_meta, stderr_meta, returncode_meta = run_cmd(["git", "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--", file_path])
        metadata = {}
        if returncode_meta == 0 and stdout_meta:
            commit_hash, author, date, message = stdout_meta.split('|', 3)
            metadata = {
                "last_commit": commit_hash,
                "author": author,
                "date": date,
                "message": message
            }
        
        return {
            "file_path": file_path,
            "content": stdout,
            "metadata": metadata
        }
    except Exception as e:
        print(f"❌ Failed to get file content: {e}")
        raise

if __name__ == "__main__":
    ensure_latest()
    commit_and_push()
