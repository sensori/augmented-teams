# Run Acceptance Tests - Story IO
# Double-click this file to run all acceptance test scenarios

# Get script directory and navigate to workspace root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AcceptanceDir = $ScriptDir

# Navigate up to workspace root (same pattern as other scripts)
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path

# Change to workspace root
Set-Location $WorkspaceRoot

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Story IO Acceptance Tests" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Find the test script
$TestScript = Join-Path $AcceptanceDir "test_acceptance.py"

if (-not (Test-Path $TestScript)) {
    Write-Host "Error: Test script not found at: $TestScript" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Running acceptance tests..." -ForegroundColor Yellow
Write-Host "Test script: $TestScript" -ForegroundColor Gray
Write-Host ""

# Run the Python test script
try {
    python $TestScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "="*80 -ForegroundColor Green
        Write-Host "Acceptance tests completed successfully!" -ForegroundColor Green
        Write-Host "="*80 -ForegroundColor Green
        Write-Host ""
        Write-Host "Check the output files in: $($AcceptanceDir)\outputs\" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host ""
        Write-Host "="*80 -ForegroundColor Red
        Write-Host "Acceptance tests failed or encountered errors." -ForegroundColor Red
        Write-Host "="*80 -ForegroundColor Red
        Write-Host ""
        Write-Host "Check the output files in: $($AcceptanceDir)\outputs\" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "Error running acceptance tests: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

