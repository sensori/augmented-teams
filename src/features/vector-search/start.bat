@echo off
REM Start Vector Search API Server
cd /d %~dp0
set PYTHONIOENCODING=utf-8
python -m uvicorn api:app --reload --port 8000



