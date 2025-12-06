@echo off
setlocal
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"
echo Running test: test_render_sync_render_round_trip.py
echo ================================================================================

python -u test_render_sync_render_round_trip.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Test PASSED!
) else (
    echo.
    echo Test FAILED with exit code: %ERRORLEVEL%
)

endlocal
exit /b %ERRORLEVEL%
