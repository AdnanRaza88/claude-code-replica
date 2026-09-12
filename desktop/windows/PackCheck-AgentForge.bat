@echo off
setlocal
title AgentForge pack-check
cd /d "%~dp0.."
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --pack-check --host 127.0.0.1 --port 8787
echo.
echo Report: .agentforge\logs\pack_check.txt
pause
endlocal
