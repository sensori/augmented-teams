# Quick Start Guide

Get the vector search system running in 5 minutes.

## Prerequisites

- Python 3.11+
- OpenAI API key
- Git repository cloned

## Step 1: Install Dependencies (2 min)

```bash
cd src/features/vector-search
pip install -r requirements.txt
```

## Step 2: Set Environment Variables (1 min)

```bash
# Option A: Export directly
export OPENAI_API_KEY="sk-your-key-here"
export API_KEY="my-secure-api-key"

# Option B: Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "API_KEY=my-secure-api-key" >> .env
```

## Step 3: Test Setup (30 sec)

```bash
python test_setup.py
```

This will verify:
- ✅ All packages installed
- ✅ Environment variables set
- ✅ Document parser working
- ✅ Vector database accessible
- ✅ API initialized

## Step 4: Index Documents (1 min)

```bash
python vector_search.py index
```

Expected output:
```
🔍 Scanning repository for documents...
Found X documents
  📄 Indexing: instructions/PURPOSE.md
    ✅ Stored 3 chunks
  📄 Indexing: instructions/OPERATING_MODEL.md
    ✅ Stored 5 chunks
...
✅ Indexed X documents
```

## Step 5: Test Search (30 sec)

```bash
python vector_search.py search "augmented teams principles"
```

Expected output:
```
🔍 Search results for: 'augmented teams principles'
============================================================

1. instructions/PURPOSE.md (chunk 0)
   Relevance: 0.856 | Type: markdown
   # 🎯 Purpose — Augmented Teams GPT...
```

## Step 6: Start API Server (30 sec)

```bash
uvicorn api:app --reload --port 8000
```

Visit: http://localhost:8000/docs

## Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Search
curl "http://localhost:8000/search?query=operating+model&max_results=3"

# Stats
curl http://localhost:8000/stats
```

## Troubleshooting

### Import Error: No module named 'X'
```bash
pip install -r requirements.txt
```

### OPENAI_API_KEY not set
```bash
export OPENAI_API_KEY="your-key-here"
```

### No search results
```bash
# Re-index with force flag
python vector_search.py index --force
```

### Port already in use
```bash
# Use different port
uvicorn api:app --port 8001
```

## Next Steps

1. ✅ System is running locally
2. ⏳ Deploy to Railway (see `plan.md` Phase 3)
3. ⏳ Configure GPT Action (see `plan.md` Phase 4)
4. ⏳ Set up GitHub Actions workflows

## Common Commands

```bash
# Index with force
python vector_search.py index --force

# Search with filters
python vector_search.py search "query" --topic=instructions --type=markdown

# Start API in production mode
uvicorn api:app --host 0.0.0.0 --port 8000

# View API documentation
# Visit: http://localhost:8000/docs
```

## Architecture Overview

```
Repository Files
    ↓
Document Parsers (Word, Excel, PPT, PDF, MD)
    ↓
Text Chunking (512 tokens, 50 overlap)
    ↓
OpenAI Embeddings (text-embedding-3-small)
    ↓
ChromaDB Storage (.vector_db/)
    ↓
FastAPI Endpoints (/search, /index, /health)
    ↓
GPT Action Integration
```

Ready to test? Run `python test_setup.py` now!

