$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$py = & (Join-Path $PSScriptRoot "Resolve-Python.ps1") -RepoRoot (Get-Location)
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --ci-artifacts --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\ci_artifacts.txt"
