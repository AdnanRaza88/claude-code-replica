param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)
Set-Location $RepoRoot
$py = & (Join-Path $PSScriptRoot "Resolve-Python.ps1") -RepoRoot $RepoRoot
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$RepoRoot;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --ready --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\ready.json"
