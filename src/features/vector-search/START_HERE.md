# Quick Start - Vector Search API

## Start the Server

### Windows - Double Click:
```
start.bat
```
Just double-click `start.bat` in File Explorer!

### Windows - PowerShell:
```powershell
.\start_server.ps1
```

### Manual Command (Any OS):
```bash
python -m uvicorn api:app --reload --port 8000
```

## Access the API

Once started, visit:
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

## Before First Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API key** in `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-your-key
   API_KEY=your-random-key
   ```

3. **Index documents**:
   ```bash
   python vector_search.py index
   ```

## All Commands

```bash
# Index/re-index documents
python vector_search.py index
python vector_search.py index --force

# Search
python vector_search.py search "your query"

# View what's indexed
python vector_search.py view

# Clean up deleted files
python vector_search.py cleanup

# Get stats
python vector_search.py stats

# Start API server
python -m uvicorn api:app --reload --port 8000
```

## API Endpoints (Resource-Oriented)

### List Files
```
GET /files                    → All indexed files
GET /files?path=assets        → Files in assets/ folder
GET /files?path=instructions  → Files in instructions/ folder
```

### Get File Details
```
GET /files/instructions/PURPOSE.md
GET /files/assets/AI Workforce Enablement Proposal/AI Transformation Slides.pptx
```
Returns file info + all chunks with content

### Get Chunks Only
```
GET /chunks/instructions/PURPOSE.md
```
Returns just the chunk contents

### Search
```
GET /search?query=your+query&max_results=5
GET /search?query=principles&topic=instructions
GET /search?query=delivery&file_type=powerpoint
```

### Management
```
GET  /stats                   → Database statistics
GET  /view                    → View all files (legacy)
POST /index                   → Re-index all documents (requires auth)
POST /cleanup                 → Remove deleted files (requires auth)
```

## Test It Works

```bash
# Test search
curl "http://127.0.0.1:8000/search?query=augmented+teams"

# List all files
curl "http://127.0.0.1:8000/files"

# Get specific file
curl "http://127.0.0.1:8000/files/instructions/PURPOSE.md"
```

---

**Ready to go!** Just run `start.bat` or `python -m uvicorn api:app --reload --port 8000`



