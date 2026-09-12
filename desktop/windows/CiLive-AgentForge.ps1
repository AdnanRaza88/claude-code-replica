$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
Set-Location $root
$py = & (Join-Path $PSScriptRoot "Resolve-Python.ps1") -RepoRoot $root
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$root;$env:PYTHONPATH"
& $py desktop\launch_engine.py --ci-live --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\ci_live.txt"
