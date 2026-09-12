$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $Root "desktop\launch_engine.py")) {
    $Repo = $Root
} else {
    $Repo = Split-Path -Parent $Root
}
Set-Location $Repo
$py = & (Join-Path $Root "Resolve-Python.ps1") -RepoRoot $Repo
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$Repo;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --release --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\release.txt"
