
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
        
        print("📚 Indexing knowledge base...")
        vs = VectorSearchSystem()
        result = vs.index_repository(force_reindex=force)
        
        print(f"✅ Knowledge base indexed:")
        print(f"   - Indexed: {result['indexed']}")
        print(f"   - Skipped: {result['skipped']}")
        print(f"   - Errors: {result['errors']}")
        
        return result
    except Exception as e:
        print(f"❌ Failed to index knowledge base: {e}")
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

if __name__ == "__main__":
    ensure_latest()
    commit_and_push()
