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
echo  sound Host sound packet
echo  U Open UI
echo  0 Quit
echo.
set /p CHOICE=Select:
if "%CHOICE%"=="1" call "%~dp0Start-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="sound" call "%~dp0HostSound-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="U" call "%~dp0Open-UI-AgentForge.bat" & goto :eof
endlocal
