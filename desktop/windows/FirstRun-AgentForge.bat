@echo off
setlocal
title AgentForge first-run
cd /d "%~dp0..\.."
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --first-run --host 127.0.0.1 --port 8787
if errorlevel 1 (
  echo.
  echo First-run failed. See .agentforge\logs\last_error.txt
  pause
  exit /b 1
)
echo.
echo First-run ok. Starting AgentForge...
call "%~dp0Start-AgentForge.bat"
endlocal
