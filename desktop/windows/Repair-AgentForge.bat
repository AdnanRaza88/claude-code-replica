@echo off
setlocal
title AgentForge repair
cd /d "%~dp0"
if exist "%~dp0..\..\desktop\launch_engine.py" cd /d "%~dp0..\.."
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%CD%"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --repair --host 127.0.0.1 --port 8787
if errorlevel 1 (
  echo.
  echo Repair failed. See .agentforge\logs\last_error.txt
  pause
  exit /b 1
)
echo.
echo Repair ok. See .agentforge\logs\repair.json
pause
endlocal
