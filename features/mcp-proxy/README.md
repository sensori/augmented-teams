# MCP Proxy Feature

HTTP API proxy for MCP server operations - exposes MCP functionality as HTTP endpoints for GPT Actions.

## Files

- `main.py` - Core business logic (MCP proxy functions)
- `service.py` - FastAPI service that wraps main.py functions
- `test.py` - Plain Python unit tests
- `service-test.py` - HTTP integration tests

## Usage

```bash
# Test locally
python test.py
python service-test.py SERVICE

# Deploy to Azure
python config/provision-service.py AZURE
```

