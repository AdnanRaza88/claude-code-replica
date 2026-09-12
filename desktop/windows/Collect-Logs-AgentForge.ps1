param(
  [string]$RepoRoot = ""
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) {
  $RepoRoot = (Resolve-Path (Join-Path $here "..\..")).Path
}
Set-Location $RepoRoot
$resolve = Join-Path $here "Resolve-Python.ps1"
if (-not (Test-Path $resolve)) {
  $resolve = Join-Path $RepoRoot "Resolve-Python.ps1"
}
$py = "python"
if (Test-Path $resolve) {
  $found = & powershell -NoProfile -ExecutionPolicy Bypass -File $resolve -RepoRoot $RepoRoot
  if ($found) { $py = $found }
}
$env:PYTHONPATH = "$RepoRoot;$env:PYTHONPATH"
& $py "desktop\launch_engine.py" --bundle --host 127.0.0.1 --port 8787
if ($LASTEXITCODE -ne 0) {
  Write-Host "Bundle failed."
  exit $LASTEXITCODE
}
Write-Host "Bundle ok. See .agentforge\logs\bundle.json"
exit 0
