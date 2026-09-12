@echo off
setlocal
title AgentForge ci-trigger
cd /d "%~dp0"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%~dp0"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --ci-trigger --host 127.0.0.1 --port 8787
echo.
echo Report: .agentforge\logs\ci_trigger.txt
pause
endlocal
