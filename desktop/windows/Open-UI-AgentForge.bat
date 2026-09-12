@echo off
setlocal
title AgentForge open UI
cd /d "%~dp0"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Resolve-Python.ps1" -RepoRoot "%~dp0"`) do set "PY=%%I"
if not defined PY set "PY=python"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --open-ui --host 127.0.0.1 --port 8787
if errorlevel 1 (
  echo Engine is not up. Run Start-AgentForge.bat first.
  pause
  exit /b 1
)
for /f "tokens=*" %%U in ('"%PY%" desktop\launch_engine.py --open-ui --host 127.0.0.1 --port 8787 2^>nul ^| findstr /i "http"') do (
  start "" "%%U"
  goto :done
)
:done
endlocal
