@echo off
setlocal
title AgentForge menu
cd /d "%~dp0"
echo AgentForge (AI Engineer OS)
echo.
echo  1 Start
echo  2 Stop
echo  3 Doctor
echo  4 Self-test
echo  5 Smoke
echo  6 First run
echo  7 Repair
echo  8 Collect logs
echo  9 Ready check
echo  ok Host ok packet
echo  W Welcome
echo  G Guide
echo  P Preflight
echo  V Verify install
echo  H Handoff packet
echo  S Phase-4 signoff
echo  A Accept Windows /ui
echo  R Release packet
echo  O Operator runbook
echo  C Phase-4 closeout
echo  T Phase-4 gate
echo  U Open UI
echo  0 Quit
echo.
set /p CHOICE=Select:
if "%CHOICE%"=="1" call "%~dp0Start-AgentForge.bat" & goto :eof
if "%CHOICE%"=="2" call "%~dp0Stop-AgentForge.bat" & goto :eof
if "%CHOICE%"=="3" call "%~dp0Doctor-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="ore" call "%~dp0HostOre-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="tin" call "%~dp0HostTin-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="U" call "%~dp0Open-UI-AgentForge.bat" & goto :eof
endlocal
