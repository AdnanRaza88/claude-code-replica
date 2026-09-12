@echo off
setlocal
title AgentForge self-test
cd /d "%~dp0..\.."
if exist "%~dp0Resolve-Python.ps1" (
  for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
)
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --self-test --host 127.0.0.1 --port 8787
echo.
pause
endlocal
