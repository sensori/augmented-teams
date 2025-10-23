
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
    print("Committing and pushing changes...")
    
    # Copy workflow files to .github/workflows/ before committing
    copy_workflow_files()
    
    run_cmd(["git", "add", "."])
    try:
        run_cmd(["git", "commit", "-m", msg])
    except Exception:
        print("No changes to commit.")
        return
    run_cmd(["git", "push", REMOTE_NAME, BRANCH])
    print(f"[OK] Changes pushed successfully: {msg}")

def copy_workflow_files():
    """Copy workflow files from feature folders to .github/workflows/"""
    try:
        workflows_dir = REPO_PATH / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy git-sync.yml from git integration
        git_sync_source = REPO_PATH / "src" / "integration" / "git" / "git-sync.yml"
        git_sync_dest = workflows_dir / "git-sync.yml"
        if git_sync_source.exists():
            import shutil
            shutil.copy2(git_sync_source, git_sync_dest)
            print(f"[OK] Copied git-sync.yml to .github/workflows/")
        
        # Copy sync-gpt-builder.yml from update_gpt_instructions_from_git feature
        gpt_sync_source = REPO_PATH / "src" / "features" / "update_gpt_instructions_from_git" / "sync-gpt-builder.yml"
        gpt_sync_dest = workflows_dir / "sync-gpt-builder.yml"
        if gpt_sync_source.exists():
            import shutil
            shutil.copy2(gpt_sync_source, gpt_sync_dest)
            print(f"[OK] Copied sync-gpt-builder.yml to .github/workflows/")
            
    except Exception as e:
        print(f"[WARNING] Could not copy workflow files: {e}")

# Vector Search Integration Functions
def index_knowledge_base(force: bool = False):
    """
    Index all repository documents for semantic search.
    
    This wrapper function calls the vector search system to index
    all markdown, Word, Excel, PowerPoint, PDF, and text files.
    
    Args:
        force: If True, re-index all documents even if unchanged
    """
    try:
        import sys
        sys.path.insert(0, str(REPO_PATH / "src" / "features" / "vector-search"))
        from vector_search import VectorSearchSystem
        
        print("Indexing knowledge base...")
        vs = VectorSearchSystem()
        result = vs.index_repository(force_reindex=force)
        
        print(f"Knowledge base indexed:")
        print(f"   - Indexed: {result['indexed']}")
        print(f"   - Skipped: {result['skipped']}")
        print(f"   - Errors: {result['errors']}")
        
        return result
    except Exception as e:
        print(f"Failed to index knowledge base: {e}")
        raise

def search_knowledge(query: str, topic: str = None, file_type: str = None, max_results: int = 5):
    """
    Semantic search across all repository content.
    
    This function is designed to be called by GPT Actions for intelligent
    document retrieval based on natural language queries.
    
    Args:
        query: Natural language search query
        topic: Optional filter by topic/directory (e.g., 'instructions', 'assets')
        file_type: Optional filter by file type (e.g., 'word', 'pdf', 'markdown')
        max_results: Maximum number of results to return
        
    Returns:
        Dict with query, results, and count
    """
    try:
        import sys
        sys.path.insert(0, str(REPO_PATH / "src" / "features" / "vector-search"))
        from vector_search import VectorSearchSystem
        
        vs = VectorSearchSystem()
        results = vs.search(query, topic=topic, file_type=file_type, max_results=max_results)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        print(f"❌ Search failed: {e}")
        raise

def reindex_after_content_changes():
    """
    Reindex the vector database after content changes.
    
    This function should be called after any content changes to ensure
    the vector search system has the latest documents indexed.
    """
    try:
        print("Content changed - reindexing vector database...")
        result = index_knowledge_base(force=True)
        
        print(f"Vector database reindexed after content changes:")
        print(f"   - Total indexed: {result['indexed']}")
        print(f"   - Total skipped: {result['skipped']}")
        print(f"   - Total errors: {result['errors']}")
        
        return result
    except Exception as e:
        print(f"Failed to reindex after content changes: {e}")
        raise

def sync_and_reindex(content_changes: bool = False):
    """
    Complete sync workflow: git operations + vector reindexing if needed.
    
    Args:
        content_changes: If True, reindex the vector database after sync
    """
    try:
        print("🔄 Starting complete sync workflow...")
        
        # Ensure latest code
        ensure_latest()
        
        # Reindex if content changed
        if content_changes:
            reindex_after_content_changes()
        
        print("✅ Complete sync workflow finished!")
        
    except Exception as e:
        print(f"❌ Sync workflow failed: {e}")
        raise

if __name__ == "__main__":
    ensure_latest()
    commit_and_push()
