@echo off
setlocal
title AgentForge
cd /d "%~dp0..\.."
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "AGENTFORGE_HOST=127.0.0.1"
set "AGENTFORGE_PORT=8787"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --ensure-deps
start "AgentForge engine" /min "%PY%" desktop\launch_engine.py --host %AGENTFORGE_HOST% --port %AGENTFORGE_PORT%
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Wait-And-Open.ps1" -HostName %AGENTFORGE_HOST% -Port %AGENTFORGE_PORT%
endlocal
