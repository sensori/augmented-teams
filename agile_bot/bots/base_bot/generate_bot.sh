#!/bin/bash
# Generate Bot CLI and MCP Server
# Usage: ./generate_bot.sh <bot_name> [options]
#
# Examples:
#   ./generate_bot.sh story_bot           # Generate both CLI and MCP
#   ./generate_bot.sh story_bot --cli     # Generate CLI only
#   ./generate_bot.sh story_bot --mcp     # Generate MCP only
#   ./generate_bot.sh story_bot --awareness # Generate awareness files only

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
BOT_NAME=""
DO_CLI=false
DO_MCP=false
DO_AWARENESS=false
DO_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cli)
            DO_CLI=true
            shift
            ;;
        --mcp)
            DO_MCP=true
            shift
            ;;
        --awareness)
            DO_AWARENESS=true
            shift
            ;;
        --all)
            DO_ALL=true
            shift
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
        *)
            BOT_NAME="$1"
            shift
            ;;
    esac
done

# Validate bot name
if [ -z "$BOT_NAME" ]; then
    echo -e "${RED}Error: Bot name required${NC}"
    echo ""
    echo "Usage: ./generate_bot.sh <bot_name> [--cli] [--mcp] [--awareness]"
    exit 1
fi

# If no specific flags, default to all
if [ "$DO_CLI" = false ] && [ "$DO_MCP" = false ] && [ "$DO_AWARENESS" = false ]; then
    DO_ALL=true
fi

# Find workspace root (where agile_bot folder exists)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# If running from workspace root (agile_bot exists), use current dir
if [ -d "agile_bot/bots" ]; then
    WORKSPACE=$(pwd)
fi

BOT_PATH="agile_bot/bots/$BOT_NAME"

# Verify bot exists
if [ ! -d "$WORKSPACE/$BOT_PATH" ]; then
    echo -e "${RED}Error: Bot not found at $BOT_PATH${NC}"
    echo ""
    echo -e "${YELLOW}Available bots:${NC}"
    ls -d "$WORKSPACE/agile_bot/bots"/*/ 2>/dev/null | xargs -n1 basename | grep -v "base_bot" || true
    exit 1
fi

# Change to workspace root for Python imports
ORIGINAL_DIR=$(pwd)
cd "$WORKSPACE"

echo -e "${CYAN}========================================"
echo " Generating artifacts for: $BOT_NAME"
echo -e "========================================${NC}"
echo ""

# Generate CLI
if [ "$DO_ALL" = true ] || [ "$DO_CLI" = true ]; then
    echo -e "${YELLOW}[CLI] Generating CLI scripts and Cursor commands...${NC}"
    
    python3 -c "
from agile_bot.bots.base_bot.src.cli.cli_generator import CliGenerator
from pathlib import Path

gen = CliGenerator(Path.cwd(), '$BOT_PATH')
result = gen.generate_cli_code()

print('  [OK] Python CLI:', result.get('cli_python', 'N/A'))
print('  [OK] Shell script:', result.get('cli_script', 'N/A'))
print('  [OK] PowerShell:', result.get('cli_powershell', 'N/A'))
print('  [OK] Cursor commands:', len(result.get('cursor_commands', [])), 'commands')
print('  [OK] Registry updated')
"
    echo ""
fi

# Generate MCP
if [ "$DO_ALL" = true ] || [ "$DO_MCP" = true ]; then
    echo -e "${YELLOW}[MCP] Generating MCP server...${NC}"
    
    python3 -c "
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
from pathlib import Path
import json

gen = MCPServerGenerator(Path.cwd() / '$BOT_PATH')
result = gen.generate_server()

print('  [OK] Bot config:', result.get('bot_config', 'N/A'))
print('  [OK] Server entry:', result.get('server_entry', 'N/A'))

# Print MCP config for user
mcp_config = result.get('mcp_config', {})
if mcp_config:
    print('')
    print('  Add to ~/.cursor/mcp.json:')
    print('  ' + '-' * 50)
    for line in json.dumps(mcp_config, indent=2).split('\n'):
        print('  ' + line)
    print('  ' + '-' * 50)
"
    echo ""
fi

# Generate Awareness Files
if [ "$DO_ALL" = true ] || [ "$DO_AWARENESS" = true ]; then
    echo -e "${YELLOW}[AWARENESS] Generating awareness files...${NC}"
    
    python3 -c "
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
from pathlib import Path

gen = MCPServerGenerator(Path.cwd() / '$BOT_PATH')
result = gen.generate_awareness_files()

print('  [OK] Awareness files generated')
if result:
    for key, path in result.items():
        print(f'  [OK] {key}: {path}')
"
    echo ""
fi

echo -e "${GREEN}========================================"
echo " Generation complete for: $BOT_NAME"
echo -e "========================================${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "  1. Restart Cursor to reload MCP server"
echo "  2. Use /$BOT_NAME commands in Cursor"
echo ""

# Restore original directory
cd "$ORIGINAL_DIR"

