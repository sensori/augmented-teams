# TDD Pipeline MCP Server

## How to Test

After restarting Cursor, try these phrases in chat:

1. **Get Current Step:**
   - "Get the current step for test-feature"
   - "What step am I on?"
   - "get_current_step test-feature"

2. **Execute Next Step:**
   - "Execute the next step for test-feature"
   - "continue pipeline for test-feature"
   - "execute_next_step test-feature"

## Troubleshooting

If tools don't work:
1. Check MCP logs: View → Output → MCP
2. Look for errors in the logs
3. Verify the server is running: Cmd+Shift+P → "MCP: List Servers"

## Current Tools

- `get_current_step` - Get current pipeline step and status
- `execute_next_step` - Execute the next pipeline step


