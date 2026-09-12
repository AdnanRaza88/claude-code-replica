# Run on a Windows box with Python + NSIS (makensis) on PATH.
param(
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\..")
}

Set-Location $RepoRoot
$dest = Join-Path $RepoRoot "dist\AgentForge-portable"
Write-Host "Packing portable folder → $dest"
& python desktop\pack_portable.py --dest $dest
if ($LASTEXITCODE -ne 0) { throw "pack_portable failed" }

$makensis = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $makensis) {
    Write-Host "makensis not found. Portable folder is ready at $dest"
    Write-Host "Install NSIS, then: makensis /DPORTABLE_DIR=$dest desktop\windows\agentforge.nsi"
    exit 0
}

& makensis "/DPORTABLE_DIR=$dest" "desktop\windows\agentforge.nsi"
if ($LASTEXITCODE -ne 0) { throw "makensis failed" }
Write-Host "Installer written under dist\"
exit 0
