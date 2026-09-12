param(
    [string]$Root = ""
)

if (-not $Root) {
    $here = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (Test-Path (Join-Path $here "Start-AgentForge.bat")) {
        $Root = $here
    } else {
        $Root = Resolve-Path (Join-Path $here "..\..")
    }
}

$bat = Join-Path $Root "Start-AgentForge.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $Root "desktop\windows\Start-AgentForge.bat"
}
if (-not (Test-Path $bat)) {
    Write-Error "Start-AgentForge.bat not found under $Root"
    exit 1
}

$startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\AgentForge"
New-Item -ItemType Directory -Force -Path $startMenu | Out-Null
$desktop = [Environment]::GetFolderPath("Desktop")

$w = New-Object -ComObject WScript.Shell
foreach ($dir in @($startMenu, $desktop)) {
    $lnk = $w.CreateShortcut((Join-Path $dir "AgentForge.lnk"))
    $lnk.TargetPath = $bat
    $lnk.WorkingDirectory = (Split-Path -Parent $bat)
    $lnk.WindowStyle = 7
    $lnk.Description = "AgentForge (AI Engineer OS)"
    $lnk.Save()
}

Write-Host "Shortcuts created:"
Write-Host "  $startMenu\AgentForge.lnk"
Write-Host "  $desktop\AgentForge.lnk"
exit 0
