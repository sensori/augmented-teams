# Developer Overview: AI-Assisted Development Approach

## Table of Contents

1. [Overview](#1-overview)
2. [AI-Assisted Documentation Flow](#2-ai-assisted-documentation-flow)
   - 2.1 Global Documentation Strategy
   - 2.2 User-Specific Use Cases
   - 2.3 Markdown-First Approach
3. [Test-Driven Development](#3-test-driven-development)
   - 3.1 Test Structure
   - 3.2 Example Use Case
4. [Project Rules](#4-project-rules)
   - 4.1 Command Execution Rules
   - 4.2 Domain-Oriented Design Principles
5. [MCP Servers](#5-mcp-servers)
6. [Commands](#6-commands)
   - 6.1 Pipeline Commands
   - 6.2 Build & Test Commands
   - 6.3 Example Workflows

---

## 1. Overview

This project uses an **AI-assisted, test-driven development approach** with:

- **Feature-first architecture** - Each feature is self-contained
- **Two-tier testing** - Plain Python tests + HTTP integration tests
- **AI-assisted workflows** - AI generates code, tests, and documentation
- **MCP (Model Context Protocol) integration** - Tool-based AI assistance
- **Domain-oriented design** - Features are localized, self-contained domains

The workflow combines:
1. **Automated code execution** (fast, deterministic operations)
2. **AI-powered judgment** (context-aware, adaptive decision-making)
3. **Human-in-the-loop reviews** (approval gates for AI suggestions)

---

## 2. AI-Assisted Documentation Flow

### 2.1 Global Documentation Strategy

**Approach**: Generate comprehensive Markdown documentation that serves both global understanding and specific use cases.

**Workflow**:

1. **Global Overview First**
   - High-level architecture documentation
   - System-wide patterns and principles
   - Shared workflows and conventions

2. **User-Specific Use Cases**
   - 1-2 concrete examples per feature
   - Step-by-step guides with actual commands
   - Real-world scenarios

3. **Markdown-First**
   - All documentation in `.md` files
   - Structured with clear Table of Contents
   - Hierarchical section numbering (1, 1.1, 1.1.1)
   - Behavior-oriented section headers

**Documentation Structure**:

```markdown
# Feature Name

## TABLE OF CONTENTS
// 1. MAJOR FEATURE
//   1.1 Sub-Feature
//     1.1.1 Specific behavior

## 1. MAJOR FEATURE

### 1.1 Sub-Feature

#### 1.1.1 Specific behavior when user action
```

**Example Location**: `features/containerization/README.md`, `features/vector-search/README.md`

### 2.2 User-Specific Use Cases

Documentation includes 1-2 concrete use cases showing:

- **Problem statement** - What are we solving?
- **Setup steps** - Prerequisites and installation
- **Example workflow** - Actual commands to run
- **Expected output** - What success looks like
- **Troubleshooting** - Common issues and fixes

**Example from Vector Search**:

```markdown
## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Index Documents
```bash
python vector_search.py index
```

### Step 3: Start Server
```bash
python -m uvicorn api:app --reload --port 8000
```
```

### 2.3 Markdown-First Approach

**Why Markdown**:
- Portable across platforms
- Easy version control
- Renders well in GitHub, Cursor, IDEs
- Supports code blocks, tables, lists
- AI can easily parse and generate

**Tools for Documentation**:
- AI-assisted generation (AI suggests structure, human reviews)
- Pattern-based templates (README.md templates per feature type)
- Automated updates (sync with code changes)

---

## 3. Test-Driven Development

### 3.1 Test Structure

**Two-Tier Testing Approach**:

1. **`test.py` - Plain Python Unit Tests**
   - Imports functions directly from `main.py`
   - Tests business logic without service layer
   - Fast execution, no dependencies
   - Run: `python test.py`

2. **`service-test.py` - HTTP Integration Tests**
   - Tests FastAPI endpoints
   - Supports multiple modes: `SERVICE`, `CONTAINER`, `AZURE`
   - Tests full request/response cycle
   - Run: `python service-test.py SERVICE`

**Test-Driven Workflow**:

1. Write test first (`test.py`)
2. Run test (expected to fail)
3. Implement code (`main.py`) to pass test
4. Generate service layer (`service.py`)
5. Generate service tests (`service-test.py`)
6. Iterate until all tests pass

### 3.2 Example Use Case

**Feature**: Containerization Provisioner

**Test File**: `features/containerization/test.py`

```python
#!/usr/bin/env python3
"""
Test containerization - plain Python tests
Tests the actual functions from main.py
"""

from main import provision_feature, start_feature, get_test_url

def test_provision_feature():
    """Test provision_feature function"""
    result = provision_feature("test-feature", "SERVICE", always=True)
    assert result["success"] in [True, False], f"Expected success boolean, got {result.get('success')}"
    print("✅ test_provision_feature passed")

def test_get_test_url():
    """Test get_test_url function"""
    result = get_test_url("test-feature", "SERVICE")
    assert result["success"] in [True, False], f"Expected success boolean, got {result.get('success')}"
    print("✅ test_get_test_url passed")

if __name__ == "__main__":
    test_provision_feature()
    test_get_test_url()
    print("✅ All tests passed")
```

**Running Tests**:

```bash
# Plain Python tests (no service)
python features/containerization/test.py

# HTTP integration tests (with service)
python features/containerization/service-test.py SERVICE
python features/containerization/service-test.py CONTAINER
python features/containerization/service-test.py AZURE
```

**Expected Output**:
```
✅ test_provision_feature passed
✅ test_get_test_url passed
✅ All tests passed
```

---

## 4. Project Rules

### 4.1 Command Execution Rules

**CRITICAL: COMMAND EXECUTION SPEED**

#### QUICK COMMANDS (Interrupt after 2-3 seconds):
- Directory changes (`cd`, `pwd`, `ls`)
- File operations (`mv`, `cp`, `rm`, `mkdir`)
- Simple checks (`netstat`, `ps`, `find`)
- Quick status checks
- **DO NOT WAIT** - these hang forever if you wait
- **ALWAYS SAY "CUTTING OFF COMMAND"** when interrupting

#### LONG COMMANDS (Let complete naturally):
- Python scripts (`python script.py`)
- Tests (`python test-service.py`)
- Build processes
- Service startups
- **WAIT FOR COMPLETION** - these need to finish to show results

#### GENERAL RULES:
- Run commands in parallel batches using multiple tool calls
- Use background processes for long-running services
- Use PowerShell syntax correctly (`;` not `&&`)
- Execute next command immediately without waiting for response
- Batch operations instead of sequential one-by-one execution

### 4.2 Domain-Oriented Design Principles

#### Feature Localization
- **Keep everything local to the feature** - All files, classes, functions, and configurations for a specific domain should be in their feature folder
- **Domain boundaries** - Each feature (`src/features/`) and integration (`src/integration/`) is a self-contained domain
- **5-7 file rule** - Each feature should contain 5-7 core files that cover the complete topic:
  - README.md (overview)
  - Main configuration file
  - Primary functionality script
  - Automation/workflow file
  - Architecture documentation
  - Deployment guide
  - Setup instructions

#### Class and Function Organization
- **Domain-specific classes** - All classes stay within their feature domain
- **Feature-specific functions** - No cross-feature dependencies unless explicitly needed
- **Local utilities** - Helper functions belong to the feature that uses them
- **Clear interfaces** - If other features need functionality, expose through clean APIs

#### Configuration Management
- **Feature configs** - All feature-specific configuration in the feature folder
- **No global configs** - Avoid putting feature-specific configs in root `config/`
- **Self-contained** - Each feature should work independently with its own config

#### Code Documentation Standards

**All code files must maintain hierarchical feature documentation**:

1. **Table of Contents** - Must be at the top of every major file
   - Hierarchical numbered sections (1, 1.1, 1.1.1, etc.)
   - Shows all major features and sub-features at a glance

2. **Section Headers** - Use consistent formatting:
   - `// 1. MAJOR FEATURE   <Subject Area>` (e.g., ATTACKS)
   - `// 1.1 Sub-Feature  <Verb Noun>` (e.g., Create Attacks)
   - `// 1.1.1 Specific behavior when user action`

3. **Behavior-Oriented Naming** - Describe WHAT happens WHEN:
   - ✅ "Show/hide action buttons using animation when hovering over token"
   - ✅ "Create attacks from powers when clicking 'Convert Powers' button"
   - ❌ "Token hover handler" (too vague)
   - ❌ "Attack creation logic" (too abstract)

4. **Function Placement** - Align code at the LOWEST applicable feature level:
   - If function serves ONE specific behavior → place under that behavior (e.g., 2.1.3)
   - If function serves multiple behaviors in a sub-feature → place under sub-feature (e.g., 2.1)
   - If function serves multiple sub-features → place under major feature (e.g., 2)
   - If function used across ALL features → place in COMMON/SHARED

---

## 5. MCP Servers

**MCP (Model Context Protocol)** servers provide tool-based AI assistance. This project uses:

### 5.1 TDD Pipeline MCP Server

**Location**: `features/test-driven-development-mcp/mcp_server.py`

**Purpose**: Manages test-driven development pipeline state and workflow.

**Available Tools**:
- `get_current_step` - Get current pipeline step and status
- `start_next_step` - Execute the next step in pipeline
- `repeat_current_step` - Retry current step
- `get_workflow_status` - Show all phases and status
- `resume_pipeline` - Resume from human activity
- `reset_pipeline` - Reset to beginning
- `skip_to_step` - Jump to any step by name
- `list_workflow_phases` - List all phases
- `get_phase_details` - Get specific phase info

**Configuration**: `.cursor/mcp.json` or `mcp.json`

```json
{
  "mcpServers": {
    "tdd-pipeline": {
      "command": "python",
      "args": [
        "features/test-driven-development-mcp/mcp_server.py"
      ]
    }
  }
}
```

### 5.2 Byterover MCP Server

**Purpose**: Knowledge storage and retrieval for code patterns and solutions.

**Available Tools**:
- `byterover-retrieve-knowledge` - Retrieve learned patterns and solutions
- `byterover-store-knowledge` - Store new patterns and techniques

**When to Use**:
- **Retrieve**: Starting new tasks, debugging issues, making architectural decisions
- **Store**: Completing significant tasks, learning new patterns, finding reusable solutions

### 5.3 GitHub MCP Server

**Purpose**: Git operations and repository management.

**Available Tools**:
- Repository operations
- Commit management
- Branch workflows

**Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=...",
        "ghcr.io/github/github-mcp-server"
      ]
    }
  }
}
```

---

## 6. Commands

### 6.1 Pipeline Commands

#### `/delivery-init <feature-name>`

Initialize a new feature directory structure.

**Example**:
```bash
/delivery-init user-api
/delivery-init payment processing
```

**What it does**:
1. Creates feature directory structure
2. Generates `feature-config.yaml`
3. Creates code scaffolds (`main.py`, `test.py`)
4. Initializes state file (`.deployment-state.json`)

**Behind the scenes**:
```bash
python features/test-driven-development-mcp/delivery_pipeline.py --feature user-api
```

#### `/delivery-start <feature-name>`

Start development phase with feature requirements.

**Example**:
```bash
/delivery-start user-api
```

**What it does**:
1. Records feature requirements in pipeline state
2. Moves to `CREATE_STRUCTURE` step
3. Prepares for AI-assisted structure generation

**Pipeline Steps**:
1. `START_FEATURE` - Creates feature directory
2. `CREATE_STRUCTURE` - AI suggests directory structure
3. `BUILD_SCAFFOLDING` - AI generates code scaffolds
4. `DEVELOP_TEST` - AI generates tests
5. `WRITE_CODE` - AI generates implementation
6. `REFACTOR` - AI suggests improvements

#### `/delivery-approve <feature-name>`

Approve current step and continue to next phase.

**Example**:
```bash
/delivery-approve user-api
```

**What it does**:
- Approves the current human-in-the-loop step
- Moves pipeline to next phase
- Continues execution

### 6.2 Build & Test Commands

#### Run Plain Python Tests

```bash
# From feature directory
cd features/containerization
python test.py
```

**What it tests**: Business logic from `main.py` without service layer.

#### Run HTTP Integration Tests

```bash
# SERVICE mode (local FastAPI)
python service-test.py SERVICE

# CONTAINER mode (local Docker)
python service-test.py CONTAINER

# AZURE mode (production)
python service-test.py AZURE
```

**What it tests**: Full HTTP request/response cycle through FastAPI service.

#### Provision and Start Service

```bash
# Provision in SERVICE mode
python config/provision-service.py SERVICE

# Provision and start
python main.py provision-and-start containerization SERVICE
```

#### Generate Service Tests

```bash
# Generate service-test.py from test.py
python generate-service-test.py
```

This analyzes `test.py` and generates corresponding HTTP tests in `service-test.py`.

### 6.3 Example Workflows

#### Complete Feature Development Workflow

```bash
# 1. Initialize feature
/delivery-init payment-api

# 2. Start development
/delivery-start payment-api

# 3. Review AI suggestions (in CREATE_STRUCTURE step)
# ... review generated structure ...

# 4. Approve and continue
/delivery-approve payment-api

# 5. Repeat approval for each step until complete
# ... BUILD_SCAFFOLDING, DEVELOP_TEST, WRITE_CODE, REFACTOR ...

# 6. Run tests
cd features/payment-api
python test.py
python service-test.py SERVICE

# 7. Deploy (if needed)
python config/provision-service.py AZURE
```

#### Test-Driven Development Workflow

```bash
# 1. Write test first
# Edit features/my-feature/test.py
def test_calculate_total():
    result = calculate_total([10, 20, 30])
    assert result == 60

# 2. Run test (expected to fail)
python features/my-feature/test.py

# 3. Implement function in main.py
# ... AI generates code or you write it ...

# 4. Run test again (should pass)
python features/my-feature/test.py

# 5. Generate service layer
# ... AI generates service.py ...

# 6. Generate service tests
python generate-service-test.py

# 7. Test service layer
python service-test.py SERVICE
```

#### AI-Assisted Deployment

```bash
# Full AI-assisted deployment with code generation
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "payment-api" \
  --requirements "Create REST API for payment processing" \
  --mode AZURE

# Skip code regeneration (deploy existing code)
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "existing-feature" \
  --no-regenerate

# Local testing only
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "test-feature" \
  --mode CONTAINER
```

#### Quick Status Check

```bash
# Check pipeline status
# Use MCP tool: get_current_step <feature-name>
# Or check state file
cat features/apples/.deployment-state.json
```

---

## 7. Getting Started

### For New Developers

1. **Understand the Architecture**:
   - Read `features/containerization/README.md`
   - Read `features/containerization/feature_deployment_architecture.md`

2. **Set Up MCP Servers**:
   - Configure `mcp.json` with available MCP servers
   - Test with: `get_current_step test-feature`

3. **Try a Simple Feature**:
   ```bash
   /delivery-init hello-world
   /delivery-start hello-world
   # Review AI suggestions
   /delivery-approve hello-world
   ```

4. **Write Your First Test**:
   ```bash
   cd features/hello-world
   # Edit test.py
   python test.py
   ```

5. **Generate Documentation**:
   - Use AI to generate README.md
   - Follow the global → use case structure
   - Include 1-2 concrete examples

### For Contributors

1. **Follow Domain-Oriented Design**:
   - Keep feature code localized
   - Use the 5-7 file rule
   - Document with hierarchical structure

2. **Use Two-Tier Testing**:
   - Write `test.py` first (plain Python)
   - Generate `service-test.py` for HTTP tests
   - Test in multiple modes (SERVICE, CONTAINER, AZURE)

3. **Leverage AI Assistance**:
   - Use MCP tools for pipeline management
   - Use AI for code generation (with human review)
   - Store patterns in Byterover knowledge base

4. **Document Thoroughly**:
   - Include Table of Contents
   - Use behavior-oriented section names
   - Provide 1-2 concrete use cases

---

## 8. Resources

### Key Files

- `.cursorrules` - Project rules and conventions
- `mcp.json` - MCP server configuration
- `features/*/README.md` - Feature documentation
- `features/*/test.py` - Plain Python tests
- `features/*/service-test.py` - HTTP integration tests
- `features/*/.deployment-state.json` - Pipeline state

### Documentation Examples

- **Architecture**: `features/containerization/feature_deployment_architecture.md`
- **AI Workflow**: `features/containerization/ai-assisted-deployment/ai_assisted_delivery_pipeline.md`
- **Quick Start**: `features/vector-search/README.md`

### Command Reference

- **Pipeline**: `.cursor/commands/delivery-init.md`, `delivery-start.md`, `approve.md`
- **Testing**: See section 6.2
- **MCP Tools**: See section 5

---

## 9. Troubleshooting

### Pipeline Stuck

```bash
# Check current step
# Use MCP: get_current_step <feature-name>

# Reset if needed
# Use MCP: reset_pipeline <feature-name>

# Skip to specific step
# Use MCP: skip_to_step <feature-name> <step-name>
```

### Tests Failing

```bash
# Run with verbose output
python test.py -v

# Check service is running (for service-test.py)
python config/provision-service.py SERVICE

# Check logs
cat features/<feature>/logs/*.log
```

### MCP Server Issues

1. Check MCP logs: View → Output → MCP
2. Verify server configuration in `mcp.json`
3. Restart Cursor
4. Test server: `Cmd+Shift+P` → "MCP: List Servers"

---

## 10. Summary

This development approach combines:

- ✅ **Test-driven development** - Write tests first, then code
- ✅ **AI-assisted workflows** - AI generates, human reviews
- ✅ **Feature-first architecture** - Self-contained, localized features
- ✅ **Markdown documentation** - Global overview + use cases
- ✅ **MCP tooling** - Pipeline management and knowledge storage
- ✅ **Domain-oriented design** - Clear boundaries and interfaces

**Start small**: Create a simple feature, write a test, let AI help generate code, and document your approach. The system learns and improves with each feature!

