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
    return result.stdout.strip()

def ensure_latest():
    print("Fetching latest changes...")
    run_cmd(["git", "fetch", REMOTE_NAME])
    run_cmd(["git", "checkout", BRANCH])
    run_cmd(["git", "pull", REMOTE_NAME, BRANCH])
    print("Repository is up to date.")

def save_code(content: str, filename: str, subdir: str="src/misc"):
    dest_folder = REPO_PATH / subdir
    dest_folder.mkdir(parents=True, exist_ok=True)
    file_path = dest_folder / filename
    with open(file_path, "w") as f:
        f.write(content)
    print(f"✅ Saved generated file to {file_path}")
    return file_path

def commit_and_push(commit_msg: str=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (commit_msg or DEFAULT_COMMIT_MSG).format(timestamp=timestamp)
    print("🔄 Committing and pushing changes...")
    run_cmd(["git", "add", "."])
    try:
        run_cmd(["git", "commit", "-m", msg])
    except Exception:
        print("No changes to commit.")
        return
    run_cmd(["git", "push", REMOTE_NAME, BRANCH])
    print(f"✅ Changes pushed successfully: {msg}")

if __name__ == "__main__":
    ensure_latest()
    commit_and_push()
