$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Root "desktop\launch_engine.py"))) {
  $Root = Split-Path -Parent $PSScriptRoot
}
Set-Location $Root
$env:PYTHONPATH = "$Root;$env:PYTHONPATH"
$Py = & (Join-Path $PSScriptRoot "Resolve-Python.ps1") -RepoRoot $Root
if (-not $Py) { $Py = "python" }
& $Py desktop\launch_engine.py --host-line --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\host_line.txt"
