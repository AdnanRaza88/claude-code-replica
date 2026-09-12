$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $Root "desktop\launch_engine.py")) {
  $Repo = $Root
} else {
  $Repo = Resolve-Path (Join-Path $Root "..\..")
}
$py = $env:AGENTFORGE_PYTHON
if (-not $py) { $py = "python" }
$env:PYTHONPATH = "$Repo;$env:PYTHONPATH"
$out = & $py (Join-Path $Repo "desktop\launch_engine.py") --open-ui --host 127.0.0.1 --port 8787
$out
if ($LASTEXITCODE -ne 0) {
  Write-Host "Engine is not up. Run Start-AgentForge.bat first."
  exit 2
}
$url = ($out | Select-String -Pattern "http").Line
if ($url) { Start-Process $url.Trim() }
