$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root "desktop\launch_engine.py"))) {
    $Root = $PSScriptRoot
    if (-not (Test-Path (Join-Path $Root "launch_engine.py"))) {
        $Root = Split-Path -Parent $PSScriptRoot
    } else {
        $Root = Split-Path -Parent $PSScriptRoot
    }
}
Set-Location (Split-Path -Parent $PSScriptRoot)
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "$Root;$env:PYTHONPATH"
$Py = "python"
& $Py "desktop\launch_engine.py" --host-arc --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\host_arc.txt"
