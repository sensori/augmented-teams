# Run all Story IO tests using Mamba
# Usage: Run from workspace root: .\agile_bot\bots\story_bot\src\story_io\test\run-all-tests.ps1
#        Or from test directory: .\run-all-tests.ps1

$ErrorActionPreference = "Stop"

# Get the script directory (where this script lives)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$testDir = $scriptDir

# Get the src directory (parent of story_io) - this needs to be in PYTHONPATH
$srcDir = $scriptDir | Split-Path -Parent | Split-Path -Parent

# Get workspace root (go up from test/ -> story_io/ -> src/ -> story_bot/ -> bots/ -> agile_bot/ -> root)
$workspaceRoot = $testDir | Split-Path -Parent | Split-Path -Parent | Split-Path -Parent | Split-Path -Parent | Split-Path -Parent | Split-Path -Parent

# Get all test files (excluding __init__.py and this script)
$testFiles = Get-ChildItem -Path $testDir -Filter "test_*.py" | ForEach-Object { $_.FullName }

if ($testFiles.Count -eq 0) {
    Write-Host "[ERROR] No test files found!" -ForegroundColor Red
    exit 1
}

Write-Host "Running all Story IO tests..." -ForegroundColor Cyan
Write-Host "Test directory: $testDir" -ForegroundColor Gray
Write-Host "Workspace root: $workspaceRoot" -ForegroundColor Gray
Write-Host "Found $($testFiles.Count) test file(s):" -ForegroundColor Gray
Get-ChildItem -Path $testDir -Filter "test_*.py" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
Write-Host ""

# Set PYTHONPATH to include src directory so Python can find story_io module
$env:PYTHONPATH = $srcDir
if ($env:PYTHONPATH_ORIGINAL) {
    $env:PYTHONPATH = "$env:PYTHONPATH_ORIGINAL;$srcDir"
}

# Change to workspace root (some tests have hardcoded paths relative to workspace root)
Push-Location $workspaceRoot
try {
    # Convert test file paths to relative paths from workspace root
    $relativeTestFiles = $testFiles | ForEach-Object { 
        $_.Replace($workspaceRoot, "").Replace("\", "/").TrimStart("/")
    }
    
    # Run mamba on all test files by passing them as relative paths
    python -m mamba.cli $relativeTestFiles
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Host "[ERROR] Failed to run tests: $_" -ForegroundColor Red
    $exitCode = 1
}
finally {
    Pop-Location
}

if ($exitCode -eq 0) {
    Write-Host "`n[OK] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] Some tests failed (exit code: $exitCode)" -ForegroundColor Red
}

exit $exitCode

