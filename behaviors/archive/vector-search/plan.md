# Vector Search API Integration Plan

## Overview

This plan implements a production-grade semantic search system that allows your custom GPT to search across all repository documents (markdown, Word, Excel, PowerPoint, PDFs) using vector embeddings.

### Deployment Strategy

**Development**: Codespace for building and testing
- Auto-deploys when `src/` code changes (GitHub Actions)
- Free tier usage
- Same environment as production

**Production**: Railway for always-on API hosting
- Manual deployment only (after Codespace testing)
- Persistent vector database storage
- $0-5/month cost

### Auto-Deployment Rules

| Change Type | Trigger | Action |
|------------|---------|--------|
| Code changes in `src/` | Auto | Update Codespace dev environment |
| Content changes in `assets/`, `instructions/`, `config/` | Auto | Re-index vector database via API call |
| Ready for production | Manual | Deploy to Railway (manual approval) |

**Why Manual Railway Deploy**: Prevents untested code from reaching production. Always test in Codespace first.

---

## Phase 1: Local Development & Testing

### 1.1 Create Core Components

Create all files in `src/behaviors/vector-search/`:

**document_parsers.py** - Multi-format document extraction

Libraries chosen are official/most-maintained parsers for each format (python-docx, openpyxl, python-pptx, pypdf). Provides comprehensive coverage of business document types while maintaining a unified interface.

- Support for .docx, .xlsx, .pptx, .pdf, .md, .txt
- Extract text from complex documents (tables, slides, sheets)
- Return structured data with metadata

**vector_search.py** - Vector search system

- ChromaDB for local vector storage (`.vector_db/` folder) - Chosen for zero-config setup, file-based persistence, and no monthly costs. Perfect for single-user scale with smooth local-to-production deployment.
- OpenAI text-embedding-3-small for embeddings - Latest efficient model with strong performance and lower cost than text-embedding-3-large. Produces 1536-dimensional vectors optimized for semantic search.
- Chunking strategy: 512 tokens with 50 token overlap - Balances context preservation with retrieval precision. Overlap ensures important content at chunk boundaries isn't lost.
- Index documents from `instructions/`, `config/`, `assets/`, `src/`
- Search with optional filters (topic, file_type)

**api.py** - FastAPI application

FastAPI chosen for automatic OpenAPI schema generation (required for GPT Actions), native async support for concurrent requests, and production-grade performance. Auto-generates interactive API docs at `/docs`.

```python
# Key endpoints:
POST /index - Trigger full re-index
GET /search?query=...&topic=...&file_type=...&max_results=5
GET /health - Health check
GET /stats - Index statistics
```

**requirements.txt** - Dependencies

```
fastapi>=0.104.0              # Modern API framework with auto-generated OpenAPI schemas
uvicorn[standard]>=0.24.0     # High-performance ASGI server
python-docx>=1.0.0            # Word document extraction
openpyxl>=3.1.0               # Excel spreadsheet parsing
python-pptx>=0.6.23           # PowerPoint slide extraction
pypdf>=3.17.0                 # PDF text extraction
chromadb>=0.4.18              # Embedded vector database
openai>=1.3.0                 # Embeddings API
tiktoken>=0.5.0               # Token counting for smart chunking
```

### 1.2 Update git_sync.py

Add integration functions:

- `index_knowledge_base()` - Wrapper for vector indexing
- `search_knowledge()` - Wrapper for search functionality

### 1.3 Local Testing in Codespace

```bash
# Setup
pip install -r src/behaviors/vector-search/requirements.txt
export OPENAI_API_KEY=<your-key>

# Index repository
python src/behaviors/vector-search/vector_search.py index

# Test search
python src/behaviors/vector-search/vector_search.py search "augmented teams principles"

# Run API locally
cd src/behaviors/vector-search
uvicorn api:app --reload --port 8000

# Test API
curl "http://localhost:8000/search?query=operating+model&max_results=3"
```

## Phase 2: GitHub Integration & Auto-Deployment

### 2.1 Resolve Git Conflict

Resolve `.github/workflows/git-sync.yml` merge conflict:

- Choose the version that runs git_sync.py (not the placeholder)
- Keep the git commit and push functionality

### 2.2 Create Codespace Auto-Deploy Workflow

Create `.github/workflows/deploy-codespace.yml`:

**Purpose**: Auto-deploy to Codespace when src/ code changes (not for content changes in assets/ or instructions/)

```yaml
name: Deploy to Codespace
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - '.github/workflows/deploy-codespace.yml'
  workflow_dispatch:

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Codespace Rebuild
        # Codespace will auto-sync on next start
      - name: Notify
        run: echo "Code changes detected. Codespace will update on next start."
```

**Why**: Keeps development environment in sync with latest code changes. Content changes (assets/instructions) trigger re-indexing via separate workflow.

### 2.3 Create Content Re-indexing Workflow

Create `.github/workflows/reindex-vector-db.yml`:

**Purpose**: Trigger vector database re-indexing when content files change

```yaml
name: Reindex Vector Database
on:
  push:
    branches: [main]
    paths:
      - 'instructions/**'
      - 'config/**'
      - 'assets/**'
  workflow_dispatch:

jobs:
  reindex:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Reindex
        run: |
          # Calls deployed API /index endpoint
          curl -X POST ${{ secrets.API_URL }}/index \
               -H "Authorization: Bearer ${{ secrets.API_KEY }}"
```

**Why**: Keeps vector search index fresh when documents change. Separates code deployment from content indexing.

## Phase 3: Production Deployment (Manual Trigger Only)

**Important**: Railway deployment is MANUAL only. Do not auto-deploy on every commit. Deploy after testing in Codespace.

### 3.1 Set Up Railway Account

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub account
   - Verify email

2. **Install Railway CLI** (optional, for local management)
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Connect GitHub Repository**
   - In Railway dashboard: New Project → Deploy from GitHub repo
   - Select `augmented-teams` repository
   - Grant Railway access to the repo

### 3.2 Prepare Deployment Files

Create in `src/behaviors/vector-search/`:

**Procfile** (for Railway)

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

**railway.json** - Railway-specific configuration

Railway chosen for free tier ($5 credit/month), automatic GitHub integration, persistent storage volumes (500MB free), and zero DevOps overhead. Provides production-ready hosting without managing servers.

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**.dockerignore** (optional, improves build performance)
```
.git
.vector_db
__pycache__
*.pyc
.env
*.md
```

### 3.3 Configure Railway Project

1. **Set Root Directory**
   - In Railway project settings → Service → Root Directory
   - Set to: `src/behaviors/vector-search`

2. **Add Environment Variables**
   - `OPENAI_API_KEY` = your OpenAI API key
   - `VECTOR_DB_PATH` = `/app/.vector_db` (optional, uses default if not set)
   - `API_KEY` = (generate secure key for GPT Action authentication)

3. **Configure Persistent Storage**
   - Add volume: `/app/.vector_db` → Mounts persistent disk
   - Size: 1GB (more than enough for your use case)

### 3.4 Manual Deployment Process

**When to Deploy:**
- After testing in Codespace
- After verifying all endpoints work
- When ready to update production

**How to Deploy:**

**Option A: Railway Dashboard**
1. Go to Railway project
2. Click "Deploy" button
3. Monitor build logs
4. Wait for deployment to complete (~2-3 minutes)

**Option B: Railway CLI**
```bash
cd src/behaviors/vector-search
railway up
```

**Option C: GitHub Manual Workflow** (create this)

Create `.github/workflows/deploy-railway.yml`:
```yaml
name: Deploy to Railway (Manual)
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'production'
        
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: |
          curl -f -X POST https://api.railway.app/project/${{ secrets.RAILWAY_PROJECT_ID }}/service/${{ secrets.RAILWAY_SERVICE_ID }}/deploy
```

### 3.5 Initial Deployment & Testing

1. **Deploy to Railway** (using one of the methods above)

2. **Get Production URL**
   - Railway auto-generates: `https://your-service.railway.app`
   - Copy this URL for GPT Action configuration

3. **Initial Indexing**
   ```bash
   # Trigger initial index via API
   curl -X POST "https://your-service.railway.app/index" \
        -H "Authorization: Bearer YOUR_API_KEY"
   ```

4. **Test Production API**
   ```bash
   # Health check
   curl "https://your-service.railway.app/health"
   
   # Test search
   curl "https://your-service.railway.app/search?query=augmented+teams+principles&max_results=3"
   
   # Check stats
   curl "https://your-service.railway.app/stats"
   ```

5. **Monitor Deployment**
   - Check Railway logs for any errors
   - Verify vector database was created
   - Confirm API responds within 2 seconds

## Phase 4: GPT Action Configuration

### 4.1 Create OpenAPI Schema

Create `src/behaviors/vector-search/openapi.yaml`:

- Define `/search` endpoint schema
- Include authentication (API key header)
- Document all parameters and responses

### 4.2 Update GPT Action

In ChatGPT GPT Builder:

1. Add new action using the OpenAPI schema
2. Set server URL to production API
3. Configure authentication (API key)
4. Test search from GPT interface
5. Update instructions to use search for relevant queries

### 4.3 Add API Authentication

Update `api.py`:

- Add API key middleware for securing endpoints
- Generate and store API key for GPT to use
- Allow public access to `/health` and `/docs`

## Phase 5: Documentation & Cleanup

### 5.1 Update Documentation

**src/behaviors/vector-search/README.md** - Create comprehensive documentation for the vector search system

**instructions/TOOLS.md** - Document new semantic search capability

**README.md** - Update project overview with vector search feature

### 5.2 Add .gitignore Entries

```
.vector_db/
*.pyc
__pycache__/
.env
```

### 5.3 Create Usage Examples

Add to documentation:

- Example queries and responses
- How to re-index manually
- How to add new document types
- Troubleshooting guide

## Key Files to Create/Modify

**New Files:**

- `src/behaviors/vector-search/document_parsers.py` (~250 lines)
- `src/behaviors/vector-search/vector_search.py` (~300 lines)
- `src/behaviors/vector-search/api.py` (~150 lines)
- `src/behaviors/vector-search/requirements.txt` (~15 lines)
- `src/behaviors/vector-search/openapi.yaml` (~100 lines)
- `src/behaviors/vector-search/Procfile` (1 line)
- `src/behaviors/vector-search/railway.json` (~20 lines)
- `src/behaviors/vector-search/.dockerignore` (~10 lines)
- `.github/workflows/deploy-codespace.yml` (~15 lines)
- `.github/workflows/reindex-vector-db.yml` (~20 lines)
- `.github/workflows/deploy-railway.yml` (~15 lines, optional manual trigger)

**Modified Files:**

- `src/integration/git/git_sync.py` (add 2 wrapper functions that call vector-search)
- `.github/workflows/git-sync.yml` (resolve conflict, add indexing step)
- `.gitignore` (add vector DB and Python artifacts)
- `src/behaviors/vector-search/README.md` (new file, vector search documentation)
- `instructions/TOOLS.md` (add semantic search tool)

## Architecture Diagram

### Production Flow

```
┌─────────────────┐
│  Custom GPT     │
│  (ChatGPT)      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────┐
│  FastAPI on Railway (Production)    │
│  - GET /search                      │
│  - POST /index                      │
│  - ChromaDB (persistent volume)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│  GitHub Repository                   │
│  - instructions/*.md                 │
│  - assets/**/*.{docx,xlsx,pptx,pdf} │
│  - config/**/*                       │
└──────────────┬───────────────────────┘
               │ Webhook on push
               ▼
┌──────────────────────────────────────┐
│  GitHub Actions                      │
│  - Content changes → /index webhook  │
│  - Code changes → Codespace update   │
│  - Manual trigger → Railway deploy   │
└──────────────────────────────────────┘
```

### Development Flow

```
┌─────────────────────────┐
│  Developer (You)        │
│  - Edit code in src/    │
│  - Add docs in assets/  │
└────────┬────────────────┘
         │ git push
         ▼
┌─────────────────────────┐
│  GitHub Repository      │
└────────┬────────────────┘
         │
         ├──> src/ changed? ──> Update Codespace (auto)
         │
         ├──> content changed? ──> Reindex via webhook (auto)
         │
         └──> Manual trigger ──> Deploy to Railway (manual approval)
```

## Success Criteria

- ✅ Local search works in Codespace
- ✅ API deployed and accessible via HTTPS
- ✅ GPT can search all document types semantically
- ✅ Auto re-indexing on content updates
- ✅ Sub-2 second search response time
- ✅ Proper error handling and logging
- ✅ Complete documentation for showcase

## Implementation Checklist

### Phase 1: Local Development
- [ ] Create document_parsers.py with multi-format extraction support
- [ ] Create vector_search.py with ChromaDB and OpenAI embeddings
- [ ] Create api.py FastAPI application with search endpoints
- [ ] Create requirements.txt with all dependencies
- [ ] Update git_sync.py with integration functions
- [ ] Test indexing and search locally in Codespace

### Phase 2: GitHub Integration
- [ ] Resolve git-sync.yml merge conflict
- [ ] Create deploy-codespace.yml workflow (auto-trigger on src/ changes)
- [ ] Create reindex-vector-db.yml workflow (auto-trigger on content changes)
- [ ] Create deploy-railway.yml workflow (manual trigger only)

### Phase 3: Railway Setup & Deployment
- [ ] Create Railway account and connect GitHub repo
- [ ] Create Procfile for Railway
- [ ] Create railway.json configuration
- [ ] Create .dockerignore file
- [ ] Configure Railway environment variables (OPENAI_API_KEY, API_KEY)
- [ ] Set up persistent storage volume for vector database
- [ ] Manual deploy to Railway
- [ ] Run initial indexing on production
- [ ] Test production API endpoints

### Phase 4: GPT Action Integration
- [ ] Create OpenAPI schema for GPT Action configuration
- [ ] Update GPT Action with new search capability
- [ ] Test search from GPT interface
- [ ] Verify authentication works

### Phase 5: Documentation
- [ ] Create src/behaviors/vector-search/README.md
- [ ] Update instructions/TOOLS.md with semantic search capability
- [ ] Update main README.md with vector search feature
- [ ] Add .gitignore entries for vector DB and Python artifacts

