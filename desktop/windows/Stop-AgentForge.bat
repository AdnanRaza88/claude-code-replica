@echo off
setlocal
title AgentForge stop
cd /d "%~dp0..\.."
if defined AGENTFORGE_PYTHON (
  set "PY=%AGENTFORGE_PYTHON%"
) else (
  set "PY=python"
)
set "AGENTFORGE_HOST=127.0.0.1"
set "AGENTFORGE_PORT=8787"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
"%PY%" desktop\launch_engine.py --stop --host %AGENTFORGE_HOST% --port %AGENTFORGE_PORT%
endlocal
