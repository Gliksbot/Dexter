@echo off
echo 🚀 Starting Dexter Local System...

REM Set environment variable
set DEXTER_AGENT_KEY=dexter-local-agent-key-2025

REM Start Agent API in background
echo 🤖 Starting Agent API...
start /b python dexter_agent_api.py

REM Wait for API to start
timeout /t 3 /nobreak >nul

REM Start Dexter UI
echo 🖥️ Starting Dexter UI...
python start_dexter.py

pause