; AgentForge NSIS installer — build on Windows after pack_portable.
;   python desktop\pack_portable.py --dest dist\AgentForge-portable
;   makensis /DPORTABLE_DIR=dist\AgentForge-portable desktop\windows\agentforge.nsi
; Silent install (NSIS /S): AgentForge-Setup-VERSION.exe /S /D=%LOCALAPPDATA%\AgentForge

!ifndef PORTABLE_DIR
  !define PORTABLE_DIR "..\..\dist\AgentForge-portable"
!endif

!define PRODUCT "AgentForge"
!define PRODUCT_FULL "AgentForge (AI Engineer OS)"
!define VERSION "0.4.90"
!define PUBLISHER "AgentForge"

Name "${PRODUCT_FULL}"
OutFile "..\..\dist\AgentForge-Setup-${VERSION}.exe"
InstallDir "$LOCALAPPDATA\AgentForge"
RequestExecutionLevel user
SetCompressor /SOLID lzma
Unicode true

Page directory
Page components
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "${PORTABLE_DIR}\*.*"

  CreateDirectory "$SMPROGRAMS\AgentForge"
  CreateShortCut "$SMPROGRAMS\AgentForge\AgentForge.lnk" "$INSTDIR\Start-AgentForge.bat" "" "$INSTDIR\Start-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Stop AgentForge.lnk" "$INSTDIR\Stop-AgentForge.bat" "" "$INSTDIR\Stop-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Doctor AgentForge.lnk" "$INSTDIR\Doctor-AgentForge.bat" "" "$INSTDIR\Doctor-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Self-Test AgentForge.lnk" "$INSTDIR\SelfTest-AgentForge.bat" "" "$INSTDIR\SelfTest-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Smoke AgentForge.lnk" "$INSTDIR\Smoke-AgentForge.bat" "" "$INSTDIR\Smoke-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\First Run AgentForge.lnk" "$INSTDIR\FirstRun-AgentForge.bat" "" "$INSTDIR\FirstRun-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Repair AgentForge.lnk" "$INSTDIR\Repair-AgentForge.bat" "" "$INSTDIR\Repair-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Collect Logs AgentForge.lnk" "$INSTDIR\Collect-Logs-AgentForge.bat" "" "$INSTDIR\Collect-Logs-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Ready AgentForge.lnk" "$INSTDIR\Ready-AgentForge.bat" "" "$INSTDIR\Ready-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Menu AgentForge.lnk" "$INSTDIR\Menu-AgentForge.bat" "" "$INSTDIR\Menu-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Welcome AgentForge.lnk" "$INSTDIR\Welcome-AgentForge.bat" "" "$INSTDIR\Welcome-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Open UI AgentForge.lnk" "$INSTDIR\Open-UI-AgentForge.bat" "" "$INSTDIR\Open-UI-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Guide AgentForge.lnk" "$INSTDIR\Guide-AgentForge.bat" "" "$INSTDIR\Guide-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Preflight AgentForge.lnk" "$INSTDIR\Preflight-AgentForge.bat" "" "$INSTDIR\Preflight-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Verify Install AgentForge.lnk" "$INSTDIR\VerifyInstall-AgentForge.bat" "" "$INSTDIR\VerifyInstall-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Handoff AgentForge.lnk" "$INSTDIR\Handoff-AgentForge.bat" "" "$INSTDIR\Handoff-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Signoff AgentForge.lnk" "$INSTDIR\Signoff-AgentForge.bat" "" "$INSTDIR\Signoff-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Accept AgentForge.lnk" "$INSTDIR\Accept-AgentForge.bat" "" "$INSTDIR\Accept-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Release AgentForge.lnk" "$INSTDIR\Release-AgentForge.bat" "" "$INSTDIR\Release-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Operator AgentForge.lnk" "$INSTDIR\Operator-AgentForge.bat" "" "$INSTDIR\Operator-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Closeout AgentForge.lnk" "$INSTDIR\Closeout-AgentForge.bat" "" "$INSTDIR\Closeout-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Gate AgentForge.lnk" "$INSTDIR\Gate-AgentForge.bat" "" "$INSTDIR\Gate-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Windows Smoke AgentForge.lnk" "$INSTDIR\WindowsSmoke-AgentForge.bat" "" "$INSTDIR\WindowsSmoke-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Onboard AgentForge.lnk" "$INSTDIR\Onboard-AgentForge.bat" "" "$INSTDIR\Onboard-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Windows Path AgentForge.lnk" "$INSTDIR\WindowsPath-AgentForge.bat" "" "$INSTDIR\WindowsPath-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Trigger AgentForge.lnk" "$INSTDIR\CiTrigger-AgentForge.bat" "" "$INSTDIR\CiTrigger-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Watch AgentForge.lnk" "$INSTDIR\CiWatch-AgentForge.bat" "" "$INSTDIR\CiWatch-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Pull AgentForge.lnk" "$INSTDIR\CiPull-AgentForge.bat" "" "$INSTDIR\CiPull-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Install AgentForge.lnk" "$INSTDIR\CiInstall-AgentForge.bat" "" "$INSTDIR\CiInstall-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Verify AgentForge.lnk" "$INSTDIR\CiVerify-AgentForge.bat" "" "$INSTDIR\CiVerify-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Go AgentForge.lnk" "$INSTDIR\CiGo-AgentForge.bat" "" "$INSTDIR\CiGo-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Windows Host AgentForge.lnk" "$INSTDIR\WindowsHost-AgentForge.bat" "" "$INSTDIR\WindowsHost-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Pack Check AgentForge.lnk" "$INSTDIR\PackCheck-AgentForge.bat" "" "$INSTDIR\PackCheck-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Artifacts AgentForge.lnk" "$INSTDIR\CiArtifacts-AgentForge.bat" "" "$INSTDIR\CiArtifacts-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Drop AgentForge.lnk" "$INSTDIR\CiDrop-AgentForge.bat" "" "$INSTDIR\CiDrop-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Apply AgentForge.lnk" "$INSTDIR\CiApply-AgentForge.bat" "" "$INSTDIR\CiApply-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Finish AgentForge.lnk" "$INSTDIR\CiFinish-AgentForge.bat" "" "$INSTDIR\CiFinish-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Live AgentForge.lnk" "$INSTDIR\CiLive-AgentForge.bat" "" "$INSTDIR\CiLive-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Boot AgentForge.lnk" "$INSTDIR\CiBoot-AgentForge.bat" "" "$INSTDIR\CiBoot-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Seal AgentForge.lnk" "$INSTDIR\CiSeal-AgentForge.bat" "" "$INSTDIR\CiSeal-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\CI Exit AgentForge.lnk" "$INSTDIR\CiExit-AgentForge.bat" "" "$INSTDIR\CiExit-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Remain AgentForge.lnk" "$INSTDIR\Remain-AgentForge.bat" "" "$INSTDIR\Remain-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Block AgentForge.lnk" "$INSTDIR\HostBlock-AgentForge.bat" "" "$INSTDIR\HostBlock-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Next AgentForge.lnk" "$INSTDIR\HostNext-AgentForge.bat" "" "$INSTDIR\HostNext-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Copy AgentForge.lnk" "$INSTDIR\HostCopy-AgentForge.bat" "" "$INSTDIR\HostCopy-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Brief AgentForge.lnk" "$INSTDIR\HostBrief-AgentForge.bat" "" "$INSTDIR\HostBrief-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Line AgentForge.lnk" "$INSTDIR\HostLine-AgentForge.bat" "" "$INSTDIR\HostLine-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Now AgentForge.lnk" "$INSTDIR\HostNow-AgentForge.bat" "" "$INSTDIR\HostNow-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Pin AgentForge.lnk" "$INSTDIR\HostPin-AgentForge.bat" "" "$INSTDIR\HostPin-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Go AgentForge.lnk" "$INSTDIR\HostGo-AgentForge.bat" "" "$INSTDIR\HostGo-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Run AgentForge.lnk" "$INSTDIR\HostRun-AgentForge.bat" "" "$INSTDIR\HostRun-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Watch AgentForge.lnk" "$INSTDIR\HostWatch-AgentForge.bat" "" "$INSTDIR\HostWatch-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Pull AgentForge.lnk" "$INSTDIR\HostPull-AgentForge.bat" "" "$INSTDIR\HostPull-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Hold AgentForge.lnk" "$INSTDIR\HostHold-AgentForge.bat" "" "$INSTDIR\HostHold-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Wait AgentForge.lnk" "$INSTDIR\HostWait-AgentForge.bat" "" "$INSTDIR\HostWait-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Stay AgentForge.lnk" "$INSTDIR\HostStay-AgentForge.bat" "" "$INSTDIR\HostStay-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Keep AgentForge.lnk" "$INSTDIR\HostKeep-AgentForge.bat" "" "$INSTDIR\HostKeep-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Sync AgentForge.lnk" "$INSTDIR\HostSync-AgentForge.bat" "" "$INSTDIR\HostSync-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Lock AgentForge.lnk" "$INSTDIR\HostLock-AgentForge.bat" "" "$INSTDIR\HostLock-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Echo AgentForge.lnk" "$INSTDIR\HostEcho-AgentForge.bat" "" "$INSTDIR\HostEcho-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Mark AgentForge.lnk" "$INSTDIR\HostMark-AgentForge.bat" "" "$INSTDIR\HostMark-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Stamp AgentForge.lnk" "$INSTDIR\HostStamp-AgentForge.bat" "" "$INSTDIR\HostStamp-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Ack AgentForge.lnk" "$INSTDIR\HostAck-AgentForge.bat" "" "$INSTDIR\HostAck-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Note AgentForge.lnk" "$INSTDIR\HostNote-AgentForge.bat" "" "$INSTDIR\HostNote-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Flag AgentForge.lnk" "$INSTDIR\HostFlag-AgentForge.bat" "" "$INSTDIR\HostFlag-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Seal AgentForge.lnk" "$INSTDIR\HostSeal-AgentForge.bat" "" "$INSTDIR\HostSeal-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Sign AgentForge.lnk" "$INSTDIR\HostSign-AgentForge.bat" "" "$INSTDIR\HostSign-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Ok AgentForge.lnk" "$INSTDIR\HostOk-AgentForge.bat" "" "$INSTDIR\HostOk-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Fit AgentForge.lnk" "$INSTDIR\HostFit-AgentForge.bat" "" "$INSTDIR\HostFit-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Cue AgentForge.lnk" "$INSTDIR\HostCue-AgentForge.bat" "" "$INSTDIR\HostCue-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Tap AgentForge.lnk" "$INSTDIR\HostTap-AgentForge.bat" "" "$INSTDIR\HostTap-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Aim AgentForge.lnk" "$INSTDIR\HostAim-AgentForge.bat" "" "$INSTDIR\HostAim-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Fix AgentForge.lnk" "$INSTDIR\HostFix-AgentForge.bat" "" "$INSTDIR\HostFix-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Set AgentForge.lnk" "$INSTDIR\HostSet-AgentForge.bat" "" "$INSTDIR\HostSet-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Map AgentForge.lnk" "$INSTDIR\HostMap-AgentForge.bat" "" "$INSTDIR\HostMap-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Row AgentForge.lnk" "$INSTDIR\HostRow-AgentForge.bat" "" "$INSTDIR\HostRow-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Key AgentForge.lnk" "$INSTDIR\HostKey-AgentForge.bat" "" "$INSTDIR\HostKey-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Pad AgentForge.lnk" "$INSTDIR\HostPad-AgentForge.bat" "" "$INSTDIR\HostPad-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Tab AgentForge.lnk" "$INSTDIR\HostTab-AgentForge.bat" "" "$INSTDIR\HostTab-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Bar AgentForge.lnk" "$INSTDIR\HostBar-AgentForge.bat" "" "$INSTDIR\HostBar-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Dot AgentForge.lnk" "$INSTDIR\HostDot-AgentForge.bat" "" "$INSTDIR\HostDot-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Cap AgentForge.lnk" "$INSTDIR\HostCap-AgentForge.bat" "" "$INSTDIR\HostCap-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Hub AgentForge.lnk" "$INSTDIR\HostHub-AgentForge.bat" "" "$INSTDIR\HostHub-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Lab AgentForge.lnk" "$INSTDIR\HostLab-AgentForge.bat" "" "$INSTDIR\HostLab-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Net AgentForge.lnk" "$INSTDIR\HostNet-AgentForge.bat" "" "$INSTDIR\HostNet-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Bus AgentForge.lnk" "$INSTDIR\HostBus-AgentForge.bat" "" "$INSTDIR\HostBus-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Way AgentForge.lnk" "$INSTDIR\HostWay-AgentForge.bat" "" "$INSTDIR\HostWay-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Arc AgentForge.lnk" "$INSTDIR\HostArc-AgentForge.bat" "" "$INSTDIR\HostArc-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Rim AgentForge.lnk" "$INSTDIR\HostRim-AgentForge.bat" "" "$INSTDIR\HostRim-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Oak AgentForge.lnk" "$INSTDIR\HostOak-AgentForge.bat" "" "$INSTDIR\HostOak-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Elm AgentForge.lnk" "$INSTDIR\HostElm-AgentForge.bat" "" "$INSTDIR\HostElm-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Host Ash AgentForge.lnk" "$INSTDIR\HostAsh-AgentForge.bat" "" "$INSTDIR\HostAsh-AgentForge.bat" 0
  CreateShortCut "$DESKTOP\AgentForge.lnk" "$INSTDIR\Start-AgentForge.bat" "" "$INSTDIR\Start-AgentForge.bat" 0

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge" "DisplayName" "${PRODUCT_FULL}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge" "Publisher" "${PUBLISHER}"
SectionEnd

Section /o "Start AgentForge when I sign in"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "AgentForge" '"$INSTDIR\Start-AgentForge.bat"'
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\AgentForge\AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Ack AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Seal AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Sign AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Ok AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Fit AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Cue AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Way AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Arc AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Rim AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Oak AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Elm AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Ash AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Tap AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Aim AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Fix AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Set AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Map AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Row AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Key AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Pad AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Tab AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Bar AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Dot AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Cap AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Hub AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Lab AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Net AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Stop AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Doctor AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Self-Test AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Smoke AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\First Run AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Repair AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Collect Logs AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Ready AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Menu AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Welcome AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Open UI AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Guide AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Preflight AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Verify Install AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Handoff AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Signoff AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Accept AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Release AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Operator AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Closeout AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Gate AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Windows Smoke AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Onboard AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Windows Path AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Trigger AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Watch AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Pull AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Install AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Verify AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Go AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Windows Host AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Pack Check AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Artifacts AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Drop AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Apply AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Finish AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Live AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Boot AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Seal AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\CI Exit AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Remain AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Block AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Next AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Copy AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Brief AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Line AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Now AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Pin AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Go AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Run AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Watch AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Pull AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Hold AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Wait AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Stay AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Keep AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Sync AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Host Lock AgentForge.lnk"
  RMDir "$SMPROGRAMS\AgentForge"
  Delete "$DESKTOP\AgentForge.lnk"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "AgentForge"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge"
  RMDir /r "$INSTDIR"
SectionEnd
