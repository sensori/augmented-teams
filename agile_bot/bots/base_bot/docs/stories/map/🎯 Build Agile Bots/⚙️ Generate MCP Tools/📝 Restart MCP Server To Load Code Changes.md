# 📝 Restart MCP Server To Load Code Changes

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Build Agile Bots
**Feature:** Generate MCP Tools
**User:** MCP Server Generator
**Sequential Order:** 4
**Story Type:** user

## Story Description

Restart MCP Server To Load Code Changes functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot code changes are detected

  **then** MCP Server clears Python bytecode cache (__pycache__)

  **and** MCP Server restarts to load new code

  **and** Server restarts gracefully without losing state

  **and** Server re-registers with MCP Protocol Handler after restart

## Scenarios

### Scenario: Clear Python bytecode cache (happy_path)

**Steps:**
```gherkin
Given __pycache__ directories exist with .pyc files
When clear_python_cache is called
Then All __pycache__ directories are removed
And All .pyc files are deleted
And Cache is cleared before server restart
```

