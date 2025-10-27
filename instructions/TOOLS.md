# 🧰 Tools — Augmented Teams GPT

This GPT integrates several internal tools to extend reasoning and collaboration.

## 1. 🧱 Notion Lookup
**Purpose:** Retrieve structured content or frameworks from a connected Notion workspace.  
**Function:** `notion_lookup(query, parent_id=None)`  
Used to: summarize, ground responses, or cross-reference knowledge.

## 2. 🧮 Python Interpreter
**Purpose:** Perform reasoning, analysis, or visualizations.  
**Usage:** Support structured decision making or data storytelling.  
**Output:** Always summarized in plain language.

## 3. 🧰 Canvas (Canmore)
**Purpose:** A live collaborative environment for code and document drafting.  
**Stored in Git:** Anything co-created in Canvas can be exported to `/tools/canmore`.

## 4. 🔍 Document Search (Vector Search)
**Purpose:** Semantic search across all repository documents including markdown, Word, Excel, PowerPoint, and PDF files.  
**Function:** `searchKnowledge(query, topic=None, file_type=None, max_results=5)`  
**Enhanced Function:** `searchDetailed(query, topic=None, file_type=None, max_results=10)`  
**Usage:** 
- Find relevant content without knowing exact filenames
- Get document context and action suggestions
- Browse files by topic or type
- Retrieve complete documents with structure preserved

**Available Topics:** `instructions`, `config`, `assets`, `src`  
**Available File Types:** `word`, `excel`, `powerpoint`, `pdf`, `markdown`, `text`

## 5. 🧩 Web Access
**Purpose:** Retrieve up-to-date info or niche details.  
**Guideline:** Use only when freshness or accuracy demands it.

---

# 🔧 Development Environment Tools

Required external tools for working with this project:

## Azure Tools

### Azure CLI (`az`)
**Purpose:** Deploy and manage Azure Container Apps  
**Installation:** [Install Azure CLI](https://aka.ms/installazurecliwindows)  
**Usage:**
```bash
# Login to Azure
az login

# Deploy container apps
az containerapp create --name <app-name> --resource-group <rg-name> ...
```
**Version:** Latest (check with `az --version`)

## Docker

### Docker
**Purpose:** Build and test containers locally  
**Installation:** [Install Docker Desktop](https://www.docker.com/products/docker-desktop)  
**Usage:**
```bash
# Build container
docker build -t <image-name> .

# Run container
docker run -p 8000:8000 <image-name>
```

## Python Tools

### Python 3.12+
**Purpose:** Core runtime for all features  
**Installation:** [Install Python](https://www.python.org/downloads/)  
**Version:** 3.12 or higher

### pip
**Purpose:** Install Python dependencies  
**Included:** Comes with Python

## Git

### Git
**Purpose:** Version control  
**Installation:** [Install Git](https://git-scm.com/downloads)  
**Usage:** Standard git commands for clone, commit, push, etc.

## GitHub

### GitHub CLI (optional)
**Purpose:** Manage GitHub from command line  
**Installation:** [Install GitHub CLI](https://cli.github.com/)  
**Usage:**
```bash
gh auth login
gh repo clone <repo>
```

---

## Quick Setup Checklist

- [ ] Install Azure CLI
- [ ] Install Docker Desktop
- [ ] Install Python 3.12+
- [ ] Install Git
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Login to Azure: `az login`
- [ ] Set ACR password environment variable: `$env:ACR_PASSWORD="your-password"`

## Environment Variables

Required for local Azure deployments:
- `ACR_PASSWORD`: Azure Container Registry password
- `OPENAI_API_KEY`: For GPT-assisted assertion generation (optional)

