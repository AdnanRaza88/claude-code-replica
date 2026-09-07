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
echo  K Windows smoke checklist
echo  N Onboard card
echo  X Windows path
echo  I CI trigger (gh workflow run)
echo  J CI watch (gh run list/watch/download)
echo  L CI pull (download Setup.exe / portable zip)
echo  M CI install (Setup.exe /S or portable unzip)
echo  Y CI verify (/health after install, then Accept)
echo  Z CI go (full trigger-to-closeout card)
echo  B Windows host (three remaining host-only steps)
echo  Q Pack check (required source files)
echo  F CI artifacts (Setup.exe + portable zip names)
echo  D CI drop (scan downloads/agentforge-ci)
echo  E CI apply (Setup.exe /S or unzip from drop folder)
echo  # CI finish (FirstRun, Accept, Signoff, Closeout)
echo  * CI live (one next command from drop folder)
echo  @ CI boot (Start /health /ui then Accept)
echo  ! CI seal (Accept Signoff Closeout after /ui)
echo  $ CI exit (three remaining Phase-4 host steps)
echo  %% Remain (copy-paste host commands)
echo  & Host block (why exit_met is false)
echo  + Host next (one command + why)
echo  = Host copy (one-line command + host_copy.cmd)
echo  ~ Host brief (three remaining Windows steps)
echo  ^| Host line (pipe-ready command)
echo  ? Host now (NOW: command + why)
echo  ^> Host pin (PIN version + command)
echo  { Host go (GO version + command)
echo  ( Host wait (poll /health after Setup)
echo  _ Host stay (Accept Signoff Closeout on Windows)
echo  - Host keep (Start then Accept Signoff Closeout)
echo  U Open UI
echo  0 Quit
echo.
set /p CHOICE=Select:
if "%CHOICE%"=="1" call "%~dp0Start-AgentForge.bat" & goto :eof
if "%CHOICE%"=="2" call "%~dp0Stop-AgentForge.bat" & goto :eof
if "%CHOICE%"=="3" call "%~dp0Doctor-AgentForge.bat" & goto :eof
if "%CHOICE%"=="4" call "%~dp0SelfTest-AgentForge.bat" & goto :eof
if "%CHOICE%"=="5" call "%~dp0Smoke-AgentForge.bat" & goto :eof
if "%CHOICE%"=="6" call "%~dp0FirstRun-AgentForge.bat" & goto :eof
if "%CHOICE%"=="7" call "%~dp0Repair-AgentForge.bat" & goto :eof
if "%CHOICE%"=="8" call "%~dp0Collect-Logs-AgentForge.bat" & goto :eof
if "%CHOICE%"=="9" call "%~dp0Ready-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="W" call "%~dp0Welcome-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="G" call "%~dp0Guide-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="P" call "%~dp0Preflight-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="V" call "%~dp0VerifyInstall-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="H" call "%~dp0Handoff-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="S" call "%~dp0Signoff-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="A" call "%~dp0Accept-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="R" call "%~dp0Release-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="O" call "%~dp0Operator-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="C" call "%~dp0Closeout-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="T" call "%~dp0Gate-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="K" call "%~dp0WindowsSmoke-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="N" call "%~dp0Onboard-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="X" call "%~dp0WindowsPath-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="I" call "%~dp0CiTrigger-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="J" call "%~dp0CiWatch-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="L" call "%~dp0CiPull-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="M" call "%~dp0CiInstall-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="Y" call "%~dp0CiVerify-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="Z" call "%~dp0CiGo-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="B" call "%~dp0WindowsHost-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="Q" call "%~dp0PackCheck-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="F" call "%~dp0CiArtifacts-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="D" call "%~dp0CiDrop-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="E" call "%~dp0CiApply-AgentForge.bat" & goto :eof
if "%CHOICE%"=="#" call "%~dp0CiFinish-AgentForge.bat" & goto :eof
if "%CHOICE%"=="*" call "%~dp0CiLive-AgentForge.bat" & goto :eof
if "%CHOICE%"=="@" call "%~dp0CiBoot-AgentForge.bat" & goto :eof
if "%CHOICE%"=="!" call "%~dp0CiSeal-AgentForge.bat" & goto :eof
if "%CHOICE%"=="$" call "%~dp0CiExit-AgentForge.bat" & goto :eof
if "%CHOICE%"=="%" call "%~dp0Remain-AgentForge.bat" & goto :eof
if "%CHOICE%"=="&" call "%~dp0HostBlock-AgentForge.bat" & goto :eof
if "%CHOICE%"=="+" call "%~dp0HostNext-AgentForge.bat" & goto :eof
if "%CHOICE%"=="=" call "%~dp0HostCopy-AgentForge.bat" & goto :eof
if "%CHOICE%"=="~" call "%~dp0HostBrief-AgentForge.bat" & goto :eof
if "%CHOICE%"=="|" call "%~dp0HostLine-AgentForge.bat" & goto :eof
if "%CHOICE%"=="?" call "%~dp0HostNow-AgentForge.bat" & goto :eof
if "%CHOICE%"==">" call "%~dp0HostPin-AgentForge.bat" & goto :eof
if "%CHOICE%"=="{" call "%~dp0HostGo-AgentForge.bat" & goto :eof
if "%CHOICE%"=="}" call "%~dp0HostRun-AgentForge.bat" & goto :eof
if "%CHOICE%"=="[" call "%~dp0HostWatch-AgentForge.bat" & goto :eof
if "%CHOICE%"=="]" call "%~dp0HostPull-AgentForge.bat" & goto :eof
if "%CHOICE%"==")" call "%~dp0HostHold-AgentForge.bat" & goto :eof
if "%CHOICE%"=="(" call "%~dp0HostWait-AgentForge.bat" & goto :eof
if "%CHOICE%"=="_" call "%~dp0HostStay-AgentForge.bat" & goto :eof
if "%CHOICE%"=="-" call "%~dp0HostKeep-AgentForge.bat" & goto :eof
if /I "%CHOICE%"=="U" call "%~dp0Open-UI-AgentForge.bat" & goto :eof
endlocal
