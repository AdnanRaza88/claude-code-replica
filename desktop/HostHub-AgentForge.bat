@echo off
setlocal
title AgentForge host-hub
cd /d "%~dp0"
if exist "%~dp0windows\Resolve-Python.ps1" (
  for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\Resolve-Python.ps1" -RepoRoot "%~dp0."`) do set "PY=%%I"
)
if not defined PY set "PY=python"
cd /d "%~dp0.."
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --host-hub --host 127.0.0.1 --port 8787
echo.
echo Report: .agentforge\logs\host_hub.txt
pause
endlocal
