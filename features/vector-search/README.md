# Vector Search System

Semantic search across all repository documents using OpenAI embeddings and ChromaDB.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- OpenAI API key
- Git repository cloned

### Step 1: Install Dependencies
```bash
cd src/features/vector-search
pip install -r requirements.txt
```

### Step 2: Set Environment Variables
```bash
# Option A: Export directly
export OPENAI_API_KEY="sk-your-key-here"
export API_KEY="my-secure-api-key"

# Option B: Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "API_KEY=my-secure-api-key" >> .env
```

### Step 3: Test Setup
```bash
python test_setup.py
```

This verifies:
- ✅ All packages installed
- ✅ Environment variables set
- ✅ Document parser working
- ✅ Vector database accessible
- ✅ API initialized

### Step 4: Index Documents
```bash
python vector_search.py index
```

Expected output:
```
INFO:__main__:🔍 Scanning repository for documents...
INFO:__main__:Found 17 documents
INFO:__main__:  📄 Indexing: instructions\EXAMPLES.md
INFO:__main__:  📄 Indexing: instructions\PURPOSE.md
...
INFO:__main__:✅ Indexed 17 documents, skipped 0, errors 0
```

### Step 5: Start Server
```bash
python -m uvicorn api:app --reload --port 8000
```

### Step 6: Access API
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Search Test**: http://127.0.0.1:8000/search?query=test

## 📋 Overview

This system enables your custom GPT to intelligently search through all repository content including:
- Markdown files (`.md`)
- Word documents (`.docx`)
- Excel spreadsheets (`.xlsx`)
- PowerPoint presentations (`.pptx`)
- PDF files (`.pdf`)
- Text files (`.txt`)

## 🏗️ Architecture

- **Document Parsers**: Extract text from multiple file formats
- **Vector Database**: ChromaDB for local/production storage
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunking**: 1024 tokens with 100 token overlap (improved for better context)
- **API**: FastAPI with automatic OpenAPI schema generation

## 🎯 Cursor Commands

### Global Commands (from anywhere):
- **`@deploy`** - Complete system deployment
- **`@complete-workflow`** - Git sync + deploy + start server
- **`@quick-test`** - Run quick system tests

### Vector Search Commands (in `src/features/vector-search/`):
- **`@test-vector-search`** - Run tests
- **`@index-db`** - Index database
- **`@start-server`** - Start server
- **`@deploy-local`** - Local deployment

### Git Integration Commands (in `src/integration/git/`):
- **`@git-sync`** - Basic git sync
- **`@git-sync-reindex`** - Git sync + reindex
- **`@ensure-latest`** - Pull latest code
- **`@commit-push`** - Commit and push

## 🔧 API Endpoints

### Search Endpoints
- **`GET /search`** - Basic semantic search
- **`GET /search-detailed`** - Enhanced search with document context and action suggestions

### File Management
- **`GET /files`** - List all indexed files
- **`GET /files?path=assets`** - Filter by path prefix
- **`GET /files/{file_path}`** - Get complete document with all chunks
- **`GET /chunks/{file_path}`** - Get just chunks for a file

### System
- **`GET /health`** - Health check
- **`GET /stats`** - Database statistics
- **`POST /index`** - Trigger reindexing
- **`POST /cleanup`** - Remove deleted files from index

## 🚀 Deployment

### Local Development
```bash
# Complete workflow
@complete-workflow

# Or step by step
@ensure-latest
@deploy
@start-server
```

### GitHub Actions
- **Auto-deploy** on code commits
- **Auto-reindex** on content changes
- **Manual Railway deployment** available

### Production (Railway)
1. Set up Railway account
2. Connect GitHub repository
3. Configure environment variables
4. Run manual deployment workflow

## 🔍 Usage Examples

### Search for Content
```bash
# Basic search
curl "http://localhost:8000/search?query=augmented teams"

# Enhanced search with context
curl "http://localhost:8000/search-detailed?query=AI transformation"

# Filter by topic
curl "http://localhost:8000/search?query=agile&topic=assets"
```

### Browse Files
```bash
# List all files
curl "http://localhost:8000/files"

# List assets files
curl "http://localhost:8000/files?path=assets"

# Get complete document
curl "http://localhost:8000/files/instructions/PURPOSE.md"
```

## 🔧 Configuration

### Environment Variables
- **`OPENAI_API_KEY`** - Your OpenAI API key (required)
- **`API_KEY`** - Secure API key for authentication (optional, defaults to 'dev-key-change-in-production')
- **`VECTOR_DB_PATH`** - Path to vector database (optional, defaults to `.vector_db` in feature folder)

### Chunking Settings
- **`CHUNK_SIZE`** - 1024 tokens (increased for better context)
- **`CHUNK_OVERLAP`** - 100 tokens (increased for continuity)
- **`MAX_RESULTS`** - 10 results (increased for more context)

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill existing processes
taskkill /F /IM python.exe
```

**Search returns empty results:**
```bash
# Reindex the database
python vector_search.py index

# Check database stats
curl "http://localhost:8000/stats"
```

**API key errors:**
```bash
# Verify environment variables
python -c "import os; print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY', 'NOT SET'))"
```

### Logs
- Server logs: Check terminal output
- Indexing logs: Check `python vector_search.py index` output
- Test logs: Check `python test_setup.py` output

## 📚 GPT Action Integration

### OpenAPI Schema
The system provides an OpenAPI schema at `/docs` that can be used to configure GPT Actions.

### Enhanced Search Workflow
1. **Search for documents**: Use `/search-detailed` to find relevant content
2. **Get complete documents**: Use `/files/{file_path}` to retrieve full documents
3. **Browse by topic**: Use `/files?path=topic` to explore specific areas

### Example GPT Action Usage
- "Search for information about augmented teams principles"
- "Find documents containing 'AI transformation'"
- "Show me all files in the assets folder"
- "Get the complete PURPOSE.md document"

## 🔄 Maintenance

### Regular Tasks
- **Reindex after content changes**: `@git-sync-reindex`
- **Clean up deleted files**: `POST /cleanup`
- **Monitor database stats**: `GET /stats`

### Updates
- **Update dependencies**: `pip install -r requirements.txt --upgrade`
- **Reindex after updates**: `python vector_search.py index`

## 📖 Additional Resources

- **Plan**: `plan.md` - Detailed implementation plan
- **Git Integration**: `src/integration/git/` - Git sync with vector search
- **GitHub Actions**: `.github/workflows/` - Automated deployment
- **Cursor Commands**: `.cursorrules` - Development shortcuts