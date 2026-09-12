$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$py = & "$here\Resolve-Python.ps1" -RepoRoot $here
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$here;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --guide --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\guide.txt"
