#!/usr/bin/env python3
"""
FastAPI application for vector search semantic API.

FastAPI chosen for automatic OpenAPI schema generation (required for GPT Actions),
native async support for concurrent requests, and production-grade performance.
Auto-generates interactive API docs at /docs.
"""

import os
import logging
from typing import Optional, List, Dict
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from vector_search import VectorSearchSystem

# Load environment variables from .env file (override=True prioritizes .env over system vars)
load_dotenv(override=True)

# Configuration
API_KEY = os.getenv("API_KEY", "dev-key-change-in-production")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Augmented Teams Vector Search API",
    description="Semantic search across all repository documents using vector embeddings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector search system (lazy loading)
_vector_search: Optional[VectorSearchSystem] = None


def get_vector_search() -> VectorSearchSystem:
    """Get or create vector search instance"""
    global _vector_search
    if _vector_search is None:
        try:
            _vector_search = VectorSearchSystem()
            logger.info("✅ Vector search system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector search: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize search system: {str(e)}")
    return _vector_search


def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    """Verify API key from Authorization header"""
    if authorization is None:
        return False
    
    # Expected format: "Bearer <api_key>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return False
        return token == API_KEY
    except ValueError:
        return False


# Pydantic Models
class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    results: List[Dict]
    count: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class IndexResponse(BaseModel):
    """Index response model"""
    status: str
    indexed: int
    skipped: int
    errors: int
    total: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class StatsResponse(BaseModel):
    """Stats response model"""
    total_chunks: int
    collection_name: str
    vector_db_path: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Routes

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information"""
    return HealthResponse(
        status="ok",
        message="Augmented Teams Vector Search API is running. Visit /docs for interactive documentation."
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        vs = get_vector_search()
        stats = vs.get_stats()
        
        return HealthResponse(
            status="healthy",
            message=f"API is healthy. {stats.get('total_chunks', 0)} chunks indexed."
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"API is unhealthy: {str(e)}"
        )


@app.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., description="Natural language search query"),
    topic: Optional[str] = Query(None, description="Filter by topic/directory (e.g., 'instructions', 'assets')"),
    file_type: Optional[str] = Query(None, description="Filter by file type (e.g., 'word', 'pdf', 'markdown')"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results to return"),
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    Semantic search across all indexed documents.
    
    This endpoint is designed to be called by GPT Actions for intelligent document retrieval.
    """
    try:
        logger.info(f"Search request: query='{query}', topic={topic}, file_type={file_type}")
        
        results = vs.search(
            query=query,
            topic=topic,
            file_type=file_type,
            max_results=max_results
        )
        
        return SearchResponse(
            query=query,
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/index", response_model=IndexResponse)
async def trigger_index(
    force: bool = Query(False, description="Force re-index all documents"),
    authorization: Optional[str] = Header(None),
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    Trigger re-indexing of all repository documents.
    
    Requires API key authentication via Authorization header.
    Called automatically by GitHub Actions when content changes.
    """
    # Verify API key
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    try:
        logger.info(f"Index request: force={force}")
        
        result = vs.index_repository(force_reindex=force)
        
        return IndexResponse(
            status="completed",
            indexed=result["indexed"],
            skipped=result["skipped"],
            errors=result["errors"],
            total=result["total"]
        )
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """Get statistics about the indexed content"""
    try:
        stats = vs.get_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return StatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/cleanup")
async def cleanup_deleted_files(
    authorization: Optional[str] = Header(None),
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    Remove index entries for deleted files.
    
    Requires API key authentication via Authorization header.
    """
    # Verify API key
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    try:
        logger.info("Cleanup request received")
        
        result = vs.cleanup_deleted_files()
        
        return {
            "status": "completed",
            "deleted_chunks": result["deleted_chunks"],
            "deleted_files": result["deleted_files"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@app.get("/view")
async def view_index(
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    View all indexed files and their chunk counts.
    
    Returns a summary of what's in the vector database.
    (Legacy endpoint - use GET /files instead)
    """
    try:
        result = vs.view_index()
        
        return {
            "total_files": result["total_files"],
            "total_chunks": result["total_chunks"],
            "files": result["files"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to view index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to view index: {str(e)}")


@app.get("/files")
async def list_files(
    path: Optional[str] = Query(None, description="Filter by path prefix (e.g., 'assets', 'instructions')"),
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    List all indexed files, optionally filtered by path prefix.
    
    Examples:
    - GET /files → All files
    - GET /files?path=assets → Files in assets/
    - GET /files?path=instructions → Files in instructions/
    """
    try:
        if path:
            files = vs.get_files_by_path(path)
        else:
            result = vs.view_index()
            files = result["files"]
        
        return {
            "path_filter": path or "/",
            "total_files": len(files),
            "files": files,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    Get detailed information about a specific file including all its chunks.
    
    Examples:
    - GET /files/instructions/PURPOSE.md
    - GET /files/assets/AI Workforce Enablement Proposal/AI Transformation Slides.pptx
    
    Returns file metadata and all chunk contents.
    """
    try:
        file_info = vs.get_file_details(file_path)
        
        if not file_info:
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        return {
            **file_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file details: {str(e)}")


@app.get("/chunks/{file_path:path}")
async def get_file_chunks(
    file_path: str,
    vs: VectorSearchSystem = Depends(get_vector_search)
):
    """
    Get just the chunks for a specific file (without full metadata).
    
    Examples:
    - GET /chunks/instructions/PURPOSE.md
    - GET /chunks/assets/AI Workforce Enablement Proposal/AI Transformation Slides.pptx
    
    Returns only the chunk contents.
    """
    try:
        file_info = vs.get_file_details(file_path)
        
        if not file_info:
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        return {
            "file_path": file_info["file_path"],
            "file_type": file_info["file_type"],
            "total_chunks": len(file_info["chunks"]),
            "chunks": file_info["chunks"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


# Error handlers

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found. Visit /docs for API documentation.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error. Check logs for details.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Main execution
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting Augmented Teams Vector Search API on {HOST}:{PORT}")
    logger.info(f"📚 Documentation available at http://{HOST}:{PORT}/docs")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

