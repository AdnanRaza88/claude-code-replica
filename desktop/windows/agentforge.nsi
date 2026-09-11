; AgentForge NSIS installer — build on Windows after pack_portable.
;   python desktop\pack_portable.py --dest dist\AgentForge-portable
;   makensis /DPORTABLE_DIR=dist\AgentForge-portable desktop\windows\agentforge.nsi
; Silent install: AgentForge-Setup-VERSION.exe /S /D=%LOCALAPPDATA%\AgentForge

!ifndef PORTABLE_DIR
  !define PORTABLE_DIR "..\..\dist\AgentForge-portable"
!endif

!define PRODUCT "AgentForge"
!define PRODUCT_FULL "AgentForge (AI Engineer OS)"
!define VERSION "0.5.56"
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
  CreateShortCut "$SMPROGRAMS\AgentForge\Menu AgentForge.lnk" "$INSTDIR\Menu-AgentForge.bat" "" "$INSTDIR\Menu-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\First Run AgentForge.lnk" "$INSTDIR\FirstRun-AgentForge.bat" "" "$INSTDIR\FirstRun-AgentForge.bat" 0
  CreateShortCut "$SMPROGRAMS\AgentForge\Doctor AgentForge.lnk" "$INSTDIR\Doctor-AgentForge.bat" "" "$INSTDIR\Doctor-AgentForge.bat" 0
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
  Delete "$SMPROGRAMS\AgentForge\Stop AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Menu AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\First Run AgentForge.lnk"
  Delete "$SMPROGRAMS\AgentForge\Doctor AgentForge.lnk"
  RMDir "$SMPROGRAMS\AgentForge"
  Delete "$DESKTOP\AgentForge.lnk"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "AgentForge"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\AgentForge"
  RMDir /r "$INSTDIR"
SectionEnd
