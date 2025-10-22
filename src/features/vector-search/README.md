# Vector Search System

Semantic search across all repository documents using OpenAI embeddings and ChromaDB.

## Overview

This system enables your custom GPT to intelligently search through all repository content including:
- Markdown files (`.md`)
- Word documents (`.docx`)
- Excel spreadsheets (`.xlsx`)
- PowerPoint presentations (`.pptx`)
- PDF files (`.pdf`)
- Text files (`.txt`)

## Architecture

- **Document Parsers**: Extract text from multiple file formats
- **Vector Database**: ChromaDB for local/production storage
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunking**: 512 tokens with 50 token overlap
- **API**: FastAPI with automatic OpenAPI schema generation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
API_KEY=your_secure_api_key_for_authentication
```

Or export them:

```bash
export OPENAI_API_KEY="your_key_here"
export API_KEY="your_secure_key_here"
```

### 3. Index Repository

```bash
# Index all documents
python vector_search.py index

# Force re-index everything
python vector_search.py index --force
```

### 4. Test Search

```bash
# Basic search
python vector_search.py search "augmented teams principles"

# Search with topic filter
python vector_search.py search "operating model" --topic=instructions

# Search with file type filter
python vector_search.py search "collaboration" --type=markdown
```

### 5. Start API Server

```bash
# Development
uvicorn api:app --reload --port 8000

# Production
uvicorn api:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Endpoints

### GET /health
Health check endpoint

```bash
curl http://localhost:8000/health
```

### GET /search
Semantic search

```bash
curl "http://localhost:8000/search?query=augmented+teams&max_results=3"
```

Parameters:
- `query` (required): Natural language search query
- `topic` (optional): Filter by directory (e.g., "instructions", "assets")
- `file_type` (optional): Filter by type (e.g., "markdown", "word", "pdf")
- `max_results` (optional): Max results (1-20, default 5)

### POST /index
Trigger re-indexing (requires API key)

```bash
curl -X POST http://localhost:8000/index \
     -H "Authorization: Bearer your_api_key_here"
```

### GET /stats
Get index statistics

```bash
curl http://localhost:8000/stats
```

## Deployment

### Local Development (Codespace)

1. Open Codespace
2. Install dependencies
3. Set environment variables
4. Run `python vector_search.py index`
5. Start API with `uvicorn api:app --reload`

### Production (Railway)

See `plan.md` Phase 3 for complete Railway deployment instructions.

Key steps:
1. Create Railway account
2. Connect GitHub repository
3. Set environment variables
4. Configure persistent storage
5. Deploy

## Integration with git_sync.py

The vector search system integrates with the existing git sync workflow:

```python
from src.integration.git.git_sync import index_knowledge_base, search_knowledge

# Index documents
index_knowledge_base(force=False)

# Search documents
results = search_knowledge(
    query="augmented teams operating model",
    topic="instructions",
    max_results=5
)
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Set the environment variable or add to `.env` file

### Issue: No results returned
**Solution**: Run `python vector_search.py index` to index documents first

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: ChromaDB permission errors
**Solution**: Check that `.vector_db/` directory is writable

## Performance

- **Indexing**: ~1-2 seconds per document
- **Search**: <500ms per query
- **Storage**: ~100KB per 1000 chunks

## Files

- `document_parsers.py` - Multi-format document extraction
- `vector_search.py` - Vector database and search logic
- `api.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `plan.md` - Complete implementation plan
- `README.md` - This file

## Next Steps

1. ✅ Test locally in Codespace
2. ⏳ Deploy to Railway
3. ⏳ Configure GPT Action
4. ⏳ Set up auto re-indexing workflow

For detailed implementation plan, see `plan.md`.

