$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "$Root;$env:PYTHONPATH"
$Py = "python"
$Resolve = Join-Path $PSScriptRoot "Resolve-Python.ps1"
if (Test-Path $Resolve) {
    $Found = & $Resolve -RepoRoot $Root
    if ($Found) { $Py = $Found }
}
& $Py "desktop\launch_engine.py" --host-fix --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\host_fix.txt"
