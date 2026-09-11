$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$resolve = Join-Path $PSScriptRoot "Resolve-Python.ps1"
$py = if (Test-Path $resolve) { & $resolve -RepoRoot $PSScriptRoot } else { $null }
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --gate --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\gate.txt"
