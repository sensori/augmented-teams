#!/usr/bin/env python3
"""
Vector search system for semantic search across all repository documents.
Uses OpenAI embeddings + ChromaDB for storage and retrieval.

ChromaDB chosen for zero-config setup, file-based persistence, and no monthly costs.
Perfect for single-user scale with smooth local-to-production deployment.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import logging

import chromadb
from chromadb.config import Settings
import openai
import tiktoken
from dotenv import load_dotenv

from document_parsers import DocumentParser

# Load environment variables from .env file (override=True prioritizes .env over system vars)
load_dotenv(override=True)

# Configuration
REPO_PATH = Path(__file__).resolve().parents[3]  # augmented-teams/
VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", Path(__file__).parent / ".vector_db"))
EMBEDDING_MODEL = "text-embedding-3-small"  # Latest efficient model, cost-effective
CHUNK_SIZE = 1024  # tokens - increased for better context preservation
CHUNK_OVERLAP = 100  # tokens - increased for better continuity
MAX_RESULTS = 10  # Increased to return more context

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VectorSearchSystem:
    """Manages document indexing and semantic search"""
    
    def __init__(self):
        """Initialize ChromaDB and OpenAI client"""
        # Ensure vector DB directory exists
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_PATH),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name="augmented_teams_knowledge",
            metadata={"description": "All repository content for semantic search"}
        )
        
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Create OpenAI client instance (v1.0+ style)
        self.openai_client = openai.OpenAI(api_key=api_key)
        
    def index_repository(self, force_reindex: bool = False):
        """
        Index all supported documents in the repository.
        
        Args:
            force_reindex: If True, re-index all documents even if unchanged
        """
        logger.info("🔍 Scanning repository for documents...")
        
        # Directories to index
        search_paths = [
            REPO_PATH / "instructions",
            REPO_PATH / "config",
            REPO_PATH / "assets",
            REPO_PATH / "src"
        ]
        
        # Collect all supported files
        files_to_index = []
        for search_path in search_paths:
            if not search_path.exists():
                logger.warning(f"Path does not exist: {search_path}")
                continue
            for ext in DocumentParser.SUPPORTED_EXTENSIONS.keys():
                files_to_index.extend(search_path.rglob(f"*{ext}"))
        
        logger.info(f"Found {len(files_to_index)} documents")
        
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        for file_path in files_to_index:
            try:
                if self._should_index_file(file_path, force_reindex):
                    self._index_document(file_path)
                    indexed_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                error_count += 1
        
        logger.info(f"✅ Indexed {indexed_count} documents, skipped {skipped_count}, errors {error_count}")
        
        return {
            "indexed": indexed_count,
            "skipped": skipped_count,
            "errors": error_count,
            "total": len(files_to_index)
        }
    
    def _should_index_file(self, file_path: Path, force: bool) -> bool:
        """Check if file needs indexing based on modification time"""
        if force:
            return True
        
        file_id = self._get_file_id(file_path)
        
        # Check if file exists in collection
        try:
            results = self.collection.get(
                ids=[f"{file_id}_chunk_0"],
                include=["metadatas"]
            )
        except Exception:
            return True
        
        if not results['ids']:
            return True
        
        # Check if file was modified since last index
        stored_mtime = results['metadatas'][0].get('modified_time', '0')
        current_mtime = file_path.stat().st_mtime
        
        return current_mtime > float(stored_mtime)
    
    def _index_document(self, file_path: Path):
        """Extract, chunk, embed, and store a document"""
        logger.info(f"  📄 Indexing: {file_path.relative_to(REPO_PATH)}")
        
        # Extract text
        doc_data = DocumentParser.extract_text(file_path)
        
        if not doc_data['text']:
            logger.warning(f"    ⚠️  No text extracted")
            return
        
        # Chunk text
        chunks = self._chunk_text(doc_data['text'])
        
        if not chunks:
            logger.warning(f"    ⚠️  No chunks created")
            return
        
        # Generate embeddings
        embeddings = self._get_embeddings([chunk['text'] for chunk in chunks])
        
        # Prepare for storage
        file_id_base = self._get_file_id(file_path)
        ids = [f"{file_id_base}_chunk_{i}" for i in range(len(chunks))]
        
        metadatas = [
            {
                'file_path': str(file_path.relative_to(REPO_PATH)),
                'file_type': doc_data['file_type'],
                'chunk_index': i,
                'total_chunks': len(chunks),
                'modified_time': str(file_path.stat().st_mtime),
                **doc_data['metadata'],
                **chunk['metadata']
            }
            for i, chunk in enumerate(chunks)
        ]
        
        documents = [chunk['text'] for chunk in chunks]
        
        # Store in ChromaDB
        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"    ✅ Stored {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"    ❌ Failed to store: {e}")
    
    def _chunk_text(self, text: str) -> List[Dict]:
        """
        Split text into overlapping chunks based on token count.
        
        Returns:
            List of dicts with 'text' and 'metadata' keys
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + CHUNK_SIZE, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'token_count': len(chunk_tokens),
                    'char_count': len(chunk_text)
                }
            })
            
            # Move start with overlap
            start = end - CHUNK_OVERLAP if end < len(tokens) else end
        
        return chunks
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def _get_file_id(self, file_path: Path) -> str:
        """Generate consistent ID for a file"""
        relative_path = str(file_path.relative_to(REPO_PATH))
        return hashlib.md5(relative_path.encode()).hexdigest()
    
    def search(
        self,
        query: str,
        topic: Optional[str] = None,
        file_type: Optional[str] = None,
        max_results: int = MAX_RESULTS
    ) -> List[Dict]:
        """
        Semantic search across indexed documents.
        
        Args:
            query: Natural language search query
            topic: Optional filter by topic/directory (e.g., 'instructions', 'assets')
            file_type: Optional filter by file type (e.g., 'word', 'pdf', 'markdown')
            max_results: Maximum number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        logger.info(f"🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Build where clause for filtering
        where_clause = {}
        if topic:
            where_clause['file_path'] = {'$contains': topic}
        if file_type:
            where_clause['file_type'] = file_type
        
        # Search
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'file_path': results['metadatas'][0][i]['file_path'],
                    'file_type': results['metadatas'][0][i]['file_type'],
                    'chunk_index': results['metadatas'][0][i]['chunk_index'],
                    'relevance_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i]
                })
        
        logger.info(f"✅ Found {len(formatted_results)} results")
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get statistics about the indexed content"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "vector_db_path": str(VECTOR_DB_PATH)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def cleanup_deleted_files(self):
        """Remove index entries for files that no longer exist"""
        logger.info("🧹 Cleaning up deleted files...")
        
        # Get all indexed files
        all_data = self.collection.get(include=["metadatas"])
        
        if not all_data['ids']:
            logger.info("No indexed files found")
            return {"deleted": 0}
        
        # Check which files still exist
        deleted_ids = []
        deleted_files = set()
        
        for i, metadata in enumerate(all_data['metadatas']):
            file_path = REPO_PATH / metadata['file_path']
            
            if not file_path.exists():
                deleted_ids.append(all_data['ids'][i])
                deleted_files.add(metadata['file_path'])
        
        # Delete entries for non-existent files
        if deleted_ids:
            self.collection.delete(ids=deleted_ids)
            logger.info(f"✅ Removed {len(deleted_ids)} chunks from {len(deleted_files)} deleted files:")
            for file_path in sorted(deleted_files):
                logger.info(f"   - {file_path}")
        else:
            logger.info("✅ No deleted files found")
        
        return {
            "deleted_chunks": len(deleted_ids),
            "deleted_files": list(deleted_files)
        }
    
    def view_index(self) -> Dict:
        """Get a summary of all indexed files and chunks"""
        logger.info("📋 Retrieving index contents...")
        
        # Get all indexed data
        all_data = self.collection.get(include=["metadatas"])
        
        if not all_data['ids']:
            return {
                "total_files": 0,
                "total_chunks": 0,
                "files": []
            }
        
        # Group chunks by file
        files_dict = {}
        for metadata in all_data['metadatas']:
            file_path = metadata['file_path']
            if file_path not in files_dict:
                files_dict[file_path] = {
                    "file_path": file_path,
                    "file_type": metadata['file_type'],
                    "chunks": 0,
                    "exists": (REPO_PATH / file_path).exists()
                }
            files_dict[file_path]["chunks"] += 1
        
        # Sort by file path
        files_list = sorted(files_dict.values(), key=lambda x: x['file_path'])
        
        return {
            "total_files": len(files_list),
            "total_chunks": len(all_data['ids']),
            "files": files_list
        }
    
    def get_files_by_path(self, path_prefix: str = "") -> List[Dict]:
        """
        Get files matching a path prefix.
        
        Args:
            path_prefix: Path prefix to filter by (e.g., 'assets', 'instructions')
        
        Returns:
            List of file info dicts
        """
        all_data = self.collection.get(include=["metadatas"])
        
        if not all_data['ids']:
            return []
        
        # Group chunks by file and filter by prefix
        files_dict = {}
        for metadata in all_data['metadatas']:
            file_path = metadata['file_path']
            
            # Normalize path separators
            normalized_path = file_path.replace('\\', '/')
            normalized_prefix = path_prefix.replace('\\', '/')
            
            # Filter by prefix
            if normalized_prefix and not normalized_path.startswith(normalized_prefix):
                continue
            
            if file_path not in files_dict:
                files_dict[file_path] = {
                    "file_path": file_path,
                    "file_type": metadata['file_type'],
                    "chunks": 0,
                    "exists": (REPO_PATH / file_path).exists()
                }
            files_dict[file_path]["chunks"] += 1
        
        return sorted(files_dict.values(), key=lambda x: x['file_path'])
    
    def get_file_details(self, file_path: str) -> Optional[Dict]:
        """
        Get detailed information about a specific file and its chunks.
        
        Args:
            file_path: Path to the file (relative to repo root)
        
        Returns:
            Dict with file info and all chunks, or None if not found
        """
        # Normalize path
        normalized_path = file_path.replace('\\', '/')
        
        # Get all chunks for this file
        all_data = self.collection.get(include=["metadatas", "documents"])
        
        if not all_data['ids']:
            return None
        
        # Find chunks for this file
        chunks = []
        file_info = None
        
        for i, metadata in enumerate(all_data['metadatas']):
            meta_path = metadata['file_path'].replace('\\', '/')
            
            if meta_path == normalized_path or metadata['file_path'] == file_path:
                if file_info is None:
                    file_info = {
                        "file_path": metadata['file_path'],
                        "file_type": metadata['file_type'],
                        "exists": (REPO_PATH / metadata['file_path']).exists(),
                        "modified_time": metadata.get('modified_time'),
                        "total_chunks": metadata.get('total_chunks', 0)
                    }
                
                chunks.append({
                    "chunk_index": metadata.get('chunk_index', 0),
                    "content": all_data['documents'][i],
                    "token_count": metadata.get('token_count', 0),
                    "char_count": metadata.get('char_count', 0)
                })
        
        if not file_info:
            return None
        
        # Sort chunks by index
        chunks.sort(key=lambda x: x['chunk_index'])
        file_info['chunks'] = chunks
        
        return file_info


# CLI Interface
if __name__ == "__main__":
    import sys
    
    vs = VectorSearchSystem()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python vector_search.py index [--force]")
        print("  python vector_search.py search 'your query here' [--topic=instructions] [--type=markdown]")
        print("  python vector_search.py stats")
        print("  python vector_search.py cleanup")
        print("  python vector_search.py view")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "index":
        force = "--force" in sys.argv
        result = vs.index_repository(force_reindex=force)
        print(f"\n📊 Indexing complete:")
        print(f"  - Indexed: {result['indexed']}")
        print(f"  - Skipped: {result['skipped']}")
        print(f"  - Errors: {result['errors']}")
        print(f"  - Total: {result['total']}")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search query")
            sys.exit(1)
        
        query = sys.argv[2]
        
        # Parse optional arguments
        topic = None
        file_type = None
        for arg in sys.argv[3:]:
            if arg.startswith("--topic="):
                topic = arg.split("=")[1]
            elif arg.startswith("--type="):
                file_type = arg.split("=")[1]
        
        results = vs.search(query, topic=topic, file_type=file_type)
        
        print(f"\n🔍 Search results for: '{query}'")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['file_path']} (chunk {result['chunk_index']})")
            print(f"   Relevance: {result['relevance_score']:.3f} | Type: {result['file_type']}")
            print(f"   {result['content'][:200]}...")
    
    elif command == "stats":
        stats = vs.get_stats()
        print("\n📊 Vector Database Statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
    
    elif command == "cleanup":
        result = vs.cleanup_deleted_files()
        print(f"\n🧹 Cleanup complete:")
        print(f"  - Deleted chunks: {result['deleted_chunks']}")
        print(f"  - Deleted files: {len(result['deleted_files'])}")
        if result['deleted_files']:
            print("\nRemoved files:")
            for file_path in result['deleted_files']:
                print(f"  - {file_path}")
    
    elif command == "view":
        result = vs.view_index()
        print(f"\n📋 Indexed Files:")
        print(f"  Total Files: {result['total_files']}")
        print(f"  Total Chunks: {result['total_chunks']}")
        print("\nFiles:")
        for file_info in result['files']:
            status = "✅" if file_info['exists'] else "❌ MISSING"
            print(f"  {status} {file_info['file_path']}")
            print(f"     Type: {file_info['file_type']}, Chunks: {file_info['chunks']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

