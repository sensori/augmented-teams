# PowerShell script to run test with unbuffered output
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"

$testScript = Join-Path $PSScriptRoot "test_render_sync_render_round_trip.py"

Write-Host "Running test: $testScript" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

python -u $testScript

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "`nTest PASSED!" -ForegroundColor Green
} else {
    Write-Host "`nTest FAILED with exit code: $exitCode" -ForegroundColor Red
}

exit $exitCode





