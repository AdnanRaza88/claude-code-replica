@echo off
setlocal
title AgentForge menu
cd /d "%~dp0"
echo AgentForge (AI Engineer OS)
echo.
echo  brook Host brook packet
echo  U Open UI
echo  0 Quit
set /p CHOICE=Select:
if /I "%CHOICE%"=="brook" call "%~dp0HostBrook-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="U" call "%~dp0Open-UI-AgentForge.bat" & goto :eof
endlocal
