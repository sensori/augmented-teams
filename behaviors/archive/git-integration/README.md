# Git Integration Service

A FastAPI service that wraps git_integration.py functions for REST API access.

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
.\start_service.ps1
```

### Python
```bash
python start_service.py
```

### Manual
```bash
pip install -r requirements.txt
python git_service.py
```

## 📡 API Endpoints

### Health & Status
- **GET** `/` - Health check
- **GET** `/status` - Repository status

### Git Operations
- **POST** `/commit/text` - Commit text content
- **POST** `/commit/document` - Commit uploaded file
- **POST** `/push` - Push changes
- **POST** `/sync` - Pull latest changes

### Repository Navigation
- **GET** `/tree` - Get repository tree
- **GET** `/folder/{path}` - Get folder content
- **GET** `/file/{path}` - Get file content

### Search Operations
- **POST** `/search/content` - Search file contents (git grep)
- **GET** `/search/files?pattern=*` - Search filenames

### Workflow Management
- **POST** `/workflows/copy` - Copy workflow files

## 📋 Usage Examples

### Commit Text Content
```bash
curl -X POST "http://localhost:8001/commit/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# New Document\nThis is new content",
    "file_path": "docs/new-file.md",
    "commit_message": "feat: add new documentation"
  }'
```

### Search Content
```bash
curl -X POST "http://localhost:8001/search/content" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "function",
    "file_pattern": "*.py"
  }'
```

### Get Repository Tree
```bash
curl "http://localhost:8001/tree"
```

### Get Folder Content
```bash
curl "http://localhost:8001/folder/src/features"
```

## 🔧 Configuration

- **Port**: 8001
- **Backend**: Uses git_integration.py functions
- **Git Commands**: Native git operations (git grep, git ls-tree, etc.)

## 🎯 Features

- ✅ **Native Git Operations** - Uses git commands directly
- ✅ **Fast Search** - git grep for content, git ls-files for filenames
- ✅ **Repository Navigation** - Tree structure and folder browsing
- ✅ **File Operations** - Read, commit, push
- ✅ **Workflow Management** - Copy workflow files
- ✅ **Clean REST API** - Simple HTTP endpoints

## 🔄 Integration

This service works alongside:
- **Vector Search Service** (port 8000) - Semantic search
- **Git Integration Service** (port 8001) - Git operations

**Two focused services, no duplication!** 🚀

