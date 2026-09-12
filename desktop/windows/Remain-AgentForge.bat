@echo off
setlocal
title AgentForge remain
cd /d "%~dp0\..\.."
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --remain --host 127.0.0.1 --port 8787
echo.
echo Report: .agentforge\logs\remain.txt
pause
endlocal
