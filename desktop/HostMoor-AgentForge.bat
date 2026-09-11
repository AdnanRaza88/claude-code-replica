@echo off
setlocal
title AgentForge host-moor
cd /d "%~dp0.."
if exist "%~dp0windows\Resolve-Python.ps1" (
  for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
)
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --host-moor --host 127.0.0.1 --port 8787
echo.
echo Report: .agentforge\logs\host_moor.txt
pause
endlocal
