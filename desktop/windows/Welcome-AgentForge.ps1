$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $Root "desktop\launch_engine.py")) {
  $Repo = $Root
} else {
  $Repo = Resolve-Path (Join-Path $Root "..\..")
}
$py = $env:AGENTFORGE_PYTHON
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$Repo;$env:PYTHONPATH"
& $py (Join-Path $Repo "desktop\launch_engine.py") --welcome --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\welcome.txt"
