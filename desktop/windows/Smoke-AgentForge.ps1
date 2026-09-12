param(
  [string]$RepoRoot = "",
  [switch]$Live
)
$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
  $here = Split-Path -Parent $MyInvocation.MyCommand.Path
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
$args = @("desktop\launch_engine.py", "--smoke", "--host", "127.0.0.1", "--port", "8787")
if ($Live) { $args += "--self-test-live" }
& $py @args
exit $LASTEXITCODE
