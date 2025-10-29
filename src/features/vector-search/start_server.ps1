# Vector Search API Server Startup Script
# Usage: powershell -ExecutionPolicy Bypass -File start_server.ps1

Write-Host "Starting Vector Search API Server..." -ForegroundColor Green

# Navigate to script directory
cd $PSScriptRoot

# Set encoding for emoji support
$env:PYTHONIOENCODING = "utf-8"

# Start server
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn api:app --reload --port 8000


