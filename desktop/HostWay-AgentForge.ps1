$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path }
Set-Location (Join-Path $PSScriptRoot "..")
$Repo = Get-Location
$env:PYTHONPATH = "$Repo;$env:PYTHONPATH"
$Py = "python"
$Resolve = Join-Path $PSScriptRoot "windows\Resolve-Python.ps1"
if (Test-Path $Resolve) {
    $Found = & $Resolve -RepoRoot $Repo
    if ($Found) { $Py = $Found }
}
& $Py "desktop\launch_engine.py" --host-way --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\host_way.txt"
