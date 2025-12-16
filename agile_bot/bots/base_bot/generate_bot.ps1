# Generate Bot CLI and MCP Server
# Usage: .\generate_bot.ps1 <bot_name> [options]
#
# Examples:
#   .\generate_bot.ps1 story_bot           # Generate both CLI and MCP
#   .\generate_bot.ps1 story_bot -cli      # Generate CLI only
#   .\generate_bot.ps1 story_bot -mcp      # Generate MCP only
#   .\generate_bot.ps1 story_bot -awareness # Generate awareness files only

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$BotName,
    
    [switch]$cli,
    [switch]$mcp,
    [switch]$awareness,
    [switch]$all
)

# If no specific flags, default to all
if (-not $cli -and -not $mcp -and -not $awareness) {
    $all = $true
}

# Find workspace root (where agile_bot folder exists)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspace = (Get-Item $scriptDir).Parent.Parent.Parent.FullName

# If running from workspace root, use current dir
if (Test-Path "agile_bot/bots") {
    $workspace = (Get-Location).Path
}

$botPath = "agile_bot/bots/$BotName"

# Verify bot exists
$fullBotPath = Join-Path $workspace $botPath
if (-not (Test-Path $fullBotPath)) {
    Write-Host "Error: Bot not found at $botPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available bots:" -ForegroundColor Yellow
    $botsDir = Join-Path $workspace "agile_bot/bots"
    Get-ChildItem $botsDir -Directory | Where-Object { $_.Name -ne "base_bot" -and $_.Name -ne "registry.json" } | ForEach-Object { Write-Host "  - $($_.Name)" }
    exit 1
}

# Change to workspace root for Python imports
Push-Location $workspace

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Generating artifacts for: $BotName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generate CLI
if ($all -or $cli) {
    Write-Host "[CLI] Generating CLI scripts and Cursor commands..." -ForegroundColor Yellow
    
    $cliScript = @"
from agile_bot.bots.base_bot.src.cli.cli_generator import CliGenerator
from pathlib import Path

gen = CliGenerator(Path.cwd(), '$botPath')
result = gen.generate_cli_code()

print('  [OK] Python CLI:', result.get('cli_python', 'N/A'))
print('  [OK] Shell script:', result.get('cli_script', 'N/A'))
print('  [OK] PowerShell:', result.get('cli_powershell', 'N/A'))
print('  [OK] Cursor commands:', len(result.get('cursor_commands', [])), 'commands')
print('  [OK] Registry updated')
"@
    
    python -c $cliScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] CLI generation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Generate MCP
if ($all -or $mcp) {
    Write-Host "[MCP] Generating MCP server..." -ForegroundColor Yellow
    
    $mcpScript = @"
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
from pathlib import Path
import json

gen = MCPServerGenerator(Path.cwd() / '$botPath')
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
"@
    
    python -c $mcpScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] MCP generation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Generate Awareness Files
if ($all -or $awareness) {
    Write-Host "[AWARENESS] Generating awareness files..." -ForegroundColor Yellow
    
    $awarenessScript = @"
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator
from pathlib import Path

gen = MCPServerGenerator(Path.cwd() / '$botPath')
result = gen.generate_awareness_files()

print('  [OK] Awareness files generated')
if result:
    for key, path in result.items():
        print(f'  [OK] {key}: {path}')
"@
    
    python -c $awarenessScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Awareness generation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Green
Write-Host " Generation complete for: $BotName" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart Cursor to reload MCP server"
Write-Host "  2. Use /$BotName commands in Cursor"
Write-Host ""

# Restore original directory
Pop-Location

