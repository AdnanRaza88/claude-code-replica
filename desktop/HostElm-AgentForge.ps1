$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $PSScriptRoot "launch_engine.py"))) {
    $Root = $PSScriptRoot
}
Set-Location $Root
$env:PYTHONPATH = "$Root;$env:PYTHONPATH"
$Py = "python"
$Resolve = Join-Path $Root "desktop\windows\Resolve-Python.ps1"
if (Test-Path $Resolve) {
    $Found = & $Resolve -RepoRoot $Root
    if ($Found) { $Py = $Found }
}
& $Py "desktop\launch_engine.py" --host-elm --host 127.0.0.1 --port 8787
Write-Host "Report: .agentforge\logs\host_elm.txt"
