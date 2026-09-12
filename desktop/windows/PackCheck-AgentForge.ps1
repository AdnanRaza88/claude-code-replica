$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$py = & (Join-Path $PSScriptRoot "Resolve-Python.ps1") -RepoRoot (Get-Location)
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --pack-check --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\pack_check.txt"
