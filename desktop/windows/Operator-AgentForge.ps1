$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = & "$PSScriptRoot\Resolve-Python.ps1" -RepoRoot $PSScriptRoot
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --operator --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\operator.txt"
